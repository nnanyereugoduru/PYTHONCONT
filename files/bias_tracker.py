#!/usr/bin/env python3
"""
bias_tracker.py — Cross-outlet news story tracker with source-bias tagging.

Pulls the same real-world story from many outlets across the political
spectrum, clusters near-duplicate headlines, and flags stories that are
only being covered by one side ("blind spots").

NOTE ON BIAS LABELS: SOURCE_BIAS is a hand-maintained, simplified
left / right / undetermined heuristic for personal use. It is not a
rigorous or externally-audited media-bias rating — treat it as a rough
signal, not a verified classification, and edit it to match your own
judgment via sources.json (see --list-sources).

NOTE ON REUTERS / AP: Both discontinued their public RSS feeds years ago.
This script reaches their content through Google News' per-publisher RSS
search as a widely-used workaround, and reads the true publisher from the
feed's <source> tag (not the google.com redirect link) so bias tagging
stays accurate. This is unofficial and could break if Google changes that
endpoint — if it does, remove the two GOOGLE_NEWS_PROXY entries below.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from calendar import timegm
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse, quote_plus

import feedparser

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("bias_tracker")

# --------------------------------------------------------------------------
# Config: default sources. Extend/override by dropping a sources.json next
# to this script (see build_default_config() for the expected shape).
# --------------------------------------------------------------------------

SOURCE_BIAS: dict[str, str] = {
    # Right-leaning
    "foxnews.com": "right",
    "breitbart.com": "right",
    "nypost.com": "right",
    "washingtonexaminer.com": "right",
    "nationalreview.com": "right",
    "dailywire.com": "right",
    "newsmax.com": "right",
    # Left-leaning
    "nytimes.com": "left",
    "cnn.com": "left",
    "msnbc.com": "left",
    "huffpost.com": "left",
    "theguardian.com": "left",
    "vox.com": "left",
    "theatlantic.com": "left",
    # Undetermined / wire / public broadcasters / mixed-rated
    "apnews.com": "undetermined",
    "reuters.com": "undetermined",
    "npr.org": "undetermined",
    "bbc.co.uk": "undetermined",
    "pbs.org": "undetermined",
    "aljazeera.com": "undetermined",
    "axios.com": "undetermined",
    "thehill.com": "undetermined",
    "politico.com": "undetermined",
    "usatoday.com": "undetermined",
    "abcnews.go.com": "undetermined",
    "cbsnews.com": "undetermined",
    "reason.com": "undetermined",
}

GOOGLE_NEWS_PROXY = {
    # publisher_domain -> Google News RSS search URL scoped to that site.
    # See module docstring: official RSS for these two was discontinued.
    "reuters.com": "https://news.google.com/rss/search?q=when:24h+allinurl:reuters.com&hl=en-US&gl=US&ceid=US:en",
    "apnews.com": "https://news.google.com/rss/search?q=when:24h+allinurl:apnews.com&hl=en-US&gl=US&ceid=US:en",
}

RSS_FEEDS: list[str] = [
    # Right-leaning
    "https://feeds.foxnews.com/foxnews/latest",
    "https://moxie.foxnews.com/google-publisher/politics.xml",
    "https://nypost.com/politics/feed/",
    "https://feeds.washingtonexaminer.com/wex/politics",
    "https://www.nationalreview.com/feed/",
    "https://www.dailywire.com/feeds/rss.xml",
    "https://www.newsmax.com/rss/Politics/1/",
    # Left-leaning
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "http://rss.cnn.com/rss/cnn_allpolitics.rss",
    "https://www.theguardian.com/us-news/us-politics/rss",
    "https://www.theguardian.com/world/rss",
    "https://www.vox.com/rss/index.xml",
    "https://www.theatlantic.com/feed/all/",
    # Undetermined / wire / public broadcasters / mixed
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/politics/rss.xml",
    "https://www.pbs.org/newshour/feeds/rss/headlines",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.axios.com/feed",
    "https://thehill.com/homenews/feed/",
    "https://rss.politico.com/politics-news.xml",
    "https://rssfeeds.usatoday.com/usatoday-NewsTopStories",
    "https://feeds.abcnews.com/abcnews/topstories",
    "https://www.cbsnews.com/latest/rss/main",
    "https://www.reason.com/feed/",
    GOOGLE_NEWS_PROXY["reuters.com"],
    GOOGLE_NEWS_PROXY["apnews.com"],
]

CONFIG_PATH = Path(__file__).with_name("sources.json")
CACHE_PATH = Path(__file__).with_name(".bias_tracker_cache.json")
FEED_TIMEOUT_SECONDS = 10
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 1.5


def load_config() -> tuple[dict[str, str], list[str]]:
    """Merge in sources.json overrides/additions if present."""
    bias, feeds = dict(SOURCE_BIAS), list(RSS_FEEDS)
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
            bias.update(data.get("source_bias", {}))
            feeds.extend(f for f in data.get("rss_feeds", []) if f not in feeds)
            log.info("Loaded %d extra sources from %s", len(data.get("rss_feeds", [])), CONFIG_PATH.name)
        except Exception as e:
            log.warning("Could not parse %s: %s", CONFIG_PATH, e)
    return bias, feeds


def write_default_config_if_missing() -> None:
    if CONFIG_PATH.exists():
        return
    sample = {
        "_comment": "Add or override sources here. Entries here are merged with, "
                    "and take priority over, the built-in defaults in bias_tracker.py.",
        "source_bias": {"example.com": "left"},
        "rss_feeds": ["https://example.com/rss.xml"],
    }
    CONFIG_PATH.write_text(json.dumps(sample, indent=2))
    log.info("Wrote starter config to %s", CONFIG_PATH)


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Article:
    title: str
    url: str
    bias: str
    source: str
    summary: str = ""
    published: str | None = None  # ISO 8601, best-effort

    def to_json(self) -> dict:
        return asdict(self)


@dataclass
class StoryCluster:
    articles: list[Article]

    @property
    def outlet_count(self) -> int:
        return len({a.source for a in self.articles})

    @property
    def bias_counts(self) -> dict[str, int]:
        counts = {"left": 0, "right": 0, "undetermined": 0}
        for a in self.articles:
            counts[a.bias] += 1
        return counts

    @property
    def is_blind_spot(self) -> bool:
        """True if a story is covered by only one ideological side (left XOR
        right present, not both) — regardless of any undetermined coverage."""
        counts = self.bias_counts
        return (counts["left"] > 0) != (counts["right"] > 0)


# --------------------------------------------------------------------------
# Bias resolution
# --------------------------------------------------------------------------

def _host(url: str) -> str:
    return urlparse(url).netloc.lower()


def bias_for_domain(domain: str, bias_table: dict[str, str]) -> str:
    for known_domain, bias in bias_table.items():
        if domain == known_domain or domain.endswith("." + known_domain):
            return bias
    return "undetermined"


def resolve_source_and_bias(entry, feed_url: str, bias_table: dict[str, str]) -> tuple[str, str]:
    """Determine the true publisher + bias for an entry.

    For normal feeds this is just the article link's hostname. For the
    Google News proxy feeds, the link points at news.google.com, so we
    instead read the real publisher from the feed's <source> tag.
    """
    if feed_url in GOOGLE_NEWS_PROXY.values():
        source_info = entry.get("source", {})
        href = source_info.get("href", "") if isinstance(source_info, dict) else ""
        domain = _host(href) if href else ""
        if not domain:
            # Fall back to matching the known proxied domain by feed identity.
            domain = next(d for d, u in GOOGLE_NEWS_PROXY.items() if u == feed_url)
        return domain, bias_for_domain(domain, bias_table)

    domain = _host(entry.get("link", ""))
    return domain, bias_for_domain(domain, bias_table)


# --------------------------------------------------------------------------
# Fetching (with disk cache + retries + concurrency)
# --------------------------------------------------------------------------

def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text())
    except Exception:
        return {}


def _save_cache(cache: dict) -> None:
    try:
        CACHE_PATH.write_text(json.dumps(cache))
    except Exception as e:
        log.warning("Could not write cache: %s", e)


def _parse_published(entry) -> str | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    try:
        return datetime.fromtimestamp(timegm(parsed), tz=timezone.utc).isoformat()
    except Exception:
        return None


def _fetch_one_feed(feed_url: str, bias_table: dict[str, str], cache: dict, cache_ttl_s: int,
                     use_cache: bool) -> list[dict]:
    """Returns a list of lightweight, JSON-serializable entry dicts."""
    now = time.time()
    if use_cache:
        cached = cache.get(feed_url)
        if cached and now - cached["fetched_at"] < cache_ttl_s:
            return cached["entries"]

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            feed = feedparser.parse(feed_url, request_headers={"User-Agent": "bias-tracker/2.0"})
            if getattr(feed, "bozo", False) and not feed.entries:
                raise ValueError(str(feed.get("bozo_exception", "malformed feed, no entries")))
            break
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
            else:
                log.warning("Skipped %s after %d attempts: %s", feed_url, MAX_RETRIES + 1, last_error)
                return cache.get(feed_url, {}).get("entries", [])  # stale cache beats nothing

    entries = []
    for entry in feed.entries:
        domain, bias = resolve_source_and_bias(entry, feed_url, bias_table)
        entries.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "summary": entry.get("summary", ""),
            "source": domain,
            "bias": bias,
            "published": _parse_published(entry),
        })

    cache[feed_url] = {"fetched_at": now, "entries": entries}
    return entries


def fetch_articles(keyword: str, feeds: list[str], bias_table: dict[str, str], *,
                    max_age_days: int | None, workers: int, use_cache: bool,
                    cache_ttl_minutes: int) -> list[Article]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    cache = _load_cache() if use_cache else {}
    cache_ttl_s = cache_ttl_minutes * 60
    keyword_lower = keyword.lower()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=max_age_days)) if max_age_days else None

    articles: dict[str, Article] = {}
    with ThreadPoolExecutor(max_workers=min(workers, max(1, len(feeds)))) as pool:
        futures = {
            pool.submit(_fetch_one_feed, url, bias_table, cache, cache_ttl_s, use_cache): url
            for url in feeds
        }
        for future in as_completed(futures):
            for e in future.result():
                title, summary = e["title"], e["summary"]
                if keyword_lower not in title.lower() and keyword_lower not in summary.lower():
                    continue
                if cutoff and e["published"]:
                    try:
                        if datetime.fromisoformat(e["published"]) < cutoff:
                            continue
                    except ValueError:
                        pass
                if e["url"] and e["url"] not in articles:
                    articles[e["url"]] = Article(**e)

    if use_cache:
        _save_cache(cache)
    return list(articles.values())


# --------------------------------------------------------------------------
# Clustering
# --------------------------------------------------------------------------

def title_similarity(a: str, b: str) -> float:
    matcher = SequenceMatcher(None, a.lower(), b.lower())
    if matcher.quick_ratio() < 0.45:  # cheap upper-bound pre-filter
        return 0.0
    return matcher.ratio()


def group_similar(articles: list[Article], threshold: float) -> list[StoryCluster]:
    used = [False] * len(articles)
    clusters = []
    for i, art in enumerate(articles):
        if used[i]:
            continue
        group = [art]
        used[i] = True
        for j in range(i + 1, len(articles)):
            if not used[j] and title_similarity(art.title, articles[j].title) >= threshold:
                group.append(articles[j])
                used[j] = True
        clusters.append(StoryCluster(articles=group))
    return clusters


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def print_console(clusters: list[StoryCluster]) -> None:
    for c in clusters:
        counts = c.bias_counts
        tag = " [BLIND SPOT — one-sided coverage]" if c.is_blind_spot else ""
        print(f"\n=== Story cluster ({c.outlet_count} outlet{'s' if c.outlet_count != 1 else ''}) "
              f"L:{counts['left']} R:{counts['right']} U:{counts['undetermined']}{tag} ===")
        for art in c.articles:
            when = f" ({art.published[:10]})" if art.published else ""
            print(f"  [{art.bias.upper():13}] {art.title}{when}")
            print(f"                {art.url}")

    total = sum(c.outlet_count for c in clusters)
    blind_spots = sum(1 for c in clusters if c.is_blind_spot)
    print(f"\n--- {len(clusters)} clusters, {total} outlet-mentions total, "
          f"{blind_spots} one-sided (blind spot) clusters ---")


def write_json(clusters: list[StoryCluster], path: Path) -> None:
    payload = [
        {"outlet_count": c.outlet_count, "bias_counts": c.bias_counts,
         "is_blind_spot": c.is_blind_spot, "articles": [a.to_json() for a in c.articles]}
        for c in clusters
    ]
    path.write_text(json.dumps(payload, indent=2))


def write_csv(clusters: list[StoryCluster], path: Path) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["cluster_id", "outlet_count", "is_blind_spot", "bias", "source", "title", "url", "published"])
        for cid, c in enumerate(clusters, 1):
            for a in c.articles:
                writer.writerow([cid, c.outlet_count, c.is_blind_spot, a.bias, a.source, a.title, a.url, a.published or ""])


def render_html(clusters: list[StoryCluster], keyword: str, *, embedded: bool = False) -> str:
    """Render clusters as an HTML fragment (embedded=True) or full page.

    Shared by write_html() (file export) and webapp.py (live server) so the
    static report and the live site are always visually identical and never
    drift out of sync with each other.
    """
    import html as _html

    def esc(s: str) -> str:
        return _html.escape(s, quote=True)

    total = sum(c.outlet_count for c in clusters)
    blind_spots = sum(1 for c in clusters if c.is_blind_spot)

    rows = []
    for c in clusters:
        counts = c.bias_counts
        badge = '<span class="blind">ONE-SIDED</span>' if c.is_blind_spot else ""
        items = "".join(
            f'<li><span class="bias {a.bias}">{esc(a.bias.upper())}</span> '
            f'<a href="{esc(a.url)}" target="_blank" rel="noopener">{esc(a.title)}</a> '
            f'<small>{esc(a.source)}{f" &middot; {a.published[:10]}" if a.published else ""}</small></li>'
            for a in c.articles
        )
        rows.append(
            f'<section><h3>{c.outlet_count} outlet{"s" if c.outlet_count != 1 else ""} '
            f'<span class="counts">L:{counts["left"]} R:{counts["right"]} U:{counts["undetermined"]}</span> '
            f'{badge}</h3><ul>{items}</ul></section>'
        )

    summary = (f'<p class="summary">{len(clusters)} clusters &middot; {total} outlet-mentions &middot; '
               f'{blind_spots} one-sided (blind spot) cluster{"s" if blind_spots != 1 else ""}</p>')
    body = f'<h1>Coverage report: "{esc(keyword)}"</h1>{summary}{"".join(rows)}'

    if embedded:
        return body

    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Coverage report: {esc(keyword)}</title>
<style>{HTML_STYLE}</style></head><body>
{body}
<footer><p>Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} by <code>bias_tracker.py</code></p></footer>
</body></html>"""


HTML_STYLE = """
body { font-family: system-ui, sans-serif; max-width: 820px; margin: 2rem auto; line-height: 1.5; padding: 0 1rem; color: #1a1a1a; }
h1 { margin-bottom: 0.25rem; }
.summary { color: #555; margin-top: 0; }
section { border: 1px solid #ddd; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
section h3 { margin-top: 0; display: flex; align-items: center; gap: 0.5rem; font-size: 1rem; }
.counts { font-weight: normal; color: #777; font-size: 0.8rem; }
ul { margin: 0.5rem 0 0; padding-left: 1.2rem; }
li { margin-bottom: 0.4rem; }
.bias { font-size: 0.7rem; font-weight: bold; padding: 2px 6px; border-radius: 4px; color: white; }
.bias.left { background: #3b6fd6; } .bias.right { background: #d63b3b; } .bias.undetermined { background: #888; }
.blind { background: #f2a900; color: #222; font-size: 0.7rem; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
small { color: #777; }
a { color: #0b5fa5; }
footer { margin-top: 2rem; color: #999; font-size: 0.8rem; }
form.search { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
form.search input[type=text] { flex: 1; min-width: 200px; padding: 0.5rem; font-size: 1rem; border: 1px solid #ccc; border-radius: 6px; }
form.search button { padding: 0.5rem 1.2rem; font-size: 1rem; border: none; border-radius: 6px; background: #0b5fa5; color: white; cursor: pointer; }
form.search button:hover { background: #084a82; }
nav a { text-decoration: none; color: #0b5fa5; font-size: 0.9rem; }
.loading { color: #777; font-style: italic; }
"""


def write_html(clusters: list[StoryCluster], path: Path, keyword: str) -> None:
    path.write_text(render_html(clusters, keyword))


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Track a news topic across outlets with bias tagging.")
    parser.add_argument("keyword", nargs="?", help="Topic/keyword to search for")
    parser.add_argument("--format", choices=["console", "json", "csv", "html"], default="console")
    parser.add_argument("-o", "--output", help="Output file path (required for json/csv/html)")
    parser.add_argument("--max-age-days", type=int, default=14, help="Ignore articles older than N days (0 = no limit)")
    parser.add_argument("--min-outlets", type=int, default=1, help="Only show clusters with at least N outlets")
    parser.add_argument("--threshold", type=float, default=0.45, help="Title-similarity threshold for clustering (0-1)")
    parser.add_argument("--bias", nargs="*", choices=["left", "right", "undetermined"],
                         help="Only include articles from these bias categories")
    parser.add_argument("--workers", type=int, default=10, help="Concurrent feed fetch workers")
    parser.add_argument("--no-cache", action="store_true", help="Disable the disk cache entirely")
    parser.add_argument("--refresh-cache", action="store_true", help="Ignore cached entries and refetch everything")
    parser.add_argument("--cache-ttl", type=int, default=15, help="Cache lifetime in minutes")
    parser.add_argument("--list-sources", action="store_true", help="Print known sources and their bias, then exit")
    args = parser.parse_args()

    write_default_config_if_missing()
    bias_table, feeds = load_config()

    if args.list_sources:
        for domain, bias in sorted(bias_table.items(), key=lambda kv: (kv[1], kv[0])):
            print(f"  {bias:13} {domain}")
        return

    keyword = args.keyword or input("Enter a topic/prompt to search for: ")

    use_cache = not args.no_cache
    if args.refresh_cache and CACHE_PATH.exists():
        CACHE_PATH.unlink()

    articles = fetch_articles(
        keyword, feeds, bias_table,
        max_age_days=args.max_age_days or None,
        workers=args.workers,
        use_cache=use_cache,
        cache_ttl_minutes=args.cache_ttl,
    )

    if args.bias:
        articles = [a for a in articles if a.bias in args.bias]

    if not articles:
        print("No matching articles found.")
        return

    clusters = group_similar(articles, threshold=args.threshold)
    clusters = [c for c in clusters if c.outlet_count >= args.min_outlets]
    clusters.sort(key=lambda c: c.outlet_count, reverse=True)

    if not clusters:
        print("Articles were found, but none met --min-outlets. Try lowering it.")
        return

    if args.format == "console":
        print_console(clusters)
        return

    if not args.output:
        parser.error(f"--format {args.format} requires -o/--output")
    out_path = Path(args.output)

    if args.format == "json":
        write_json(clusters, out_path)
    elif args.format == "csv":
        write_csv(clusters, out_path)
    else:  # html
        write_html(clusters, out_path, keyword)

    print(f"Wrote {len(clusters)} clusters to {out_path}")


if __name__ == "__main__":
    main()
