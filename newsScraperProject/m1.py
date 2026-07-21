"""
Cross-outlet story tracker with (simplified) source-bias tagging.

NOTE ON BIAS LABELS: SOURCE_BIAS is a hand-maintained, simplified
left/right/undetermined heuristic for personal use. It is not a rigorous
or authoritative media-bias classification — treat it as a rough signal,
not a verified rating.
"""

import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from difflib import SequenceMatcher
from urllib.parse import urlparse

import feedparser

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

FEED_TIMEOUT_SECONDS = 10

SOURCE_BIAS = {
    "foxnews.com": "right",
    "breitbart.com": "right",
    "nypost.com": "right",
    "washingtonexaminer.com": "right",
    "nytimes.com": "left",
    "cnn.com": "left",
    "msnbc.com": "left",
    "huffpost.com": "left",
    "apnews.com": "undetermined",
    "reuters.com": "undetermined",
    "npr.org": "undetermined",
    "bbc.co.uk": "undetermined",
}

RSS_FEEDS = [
    "https://feeds.foxnews.com/foxnews/latest",
    "https://moxie.foxnews.com/google-publisher/politics.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "http://rss.cnn.com/rss/cnn_allpolitics.rss",
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/politics/rss.xml",
    "https://nypost.com/politics/feed/",
    "https://feeds.washingtonexaminer.com/wex/politics",
]


@dataclass(frozen=True)
class Article:
    title: str
    url: str
    bias: str


def get_bias(url: str) -> str:
    """Match on the actual hostname, not a raw substring of the URL."""
    host = urlparse(url).netloc.lower()
    for domain, bias in SOURCE_BIAS.items():
        if host == domain or host.endswith("." + domain):
            return bias
    return "undetermined"


def _fetch_one_feed(feed_url: str, keyword: str) -> list[Article]:
    matches = []
    try:
        feed = feedparser.parse(feed_url, request_headers={"User-Agent": "bias-tracker/1.0"})
    except Exception as e:
        log.warning("Skipped %s: %s", feed_url, e)
        return matches

    if getattr(feed, "bozo", False):
        log.warning("Malformed feed at %s: %s", feed_url, feed.get("bozo_exception"))
        # feedparser often still recovers partial entries, so keep going
        # rather than discarding the feed outright.

    keyword_lower = keyword.lower()
    for entry in feed.entries:
        title = entry.get("title", "")
        link = entry.get("link", "")
        summary = entry.get("summary", "")
        if keyword_lower in title.lower() or keyword_lower in summary.lower():
            matches.append(Article(title=title, url=link, bias=get_bias(link)))
    return matches


def fetch_articles(keyword: str, feeds: list[str] = RSS_FEEDS) -> list[Article]:
    """Fetch matching articles from all feeds concurrently, deduped by URL."""
    articles: dict[str, Article] = {}  # url -> Article, dedups same-outlet dupes

    with ThreadPoolExecutor(max_workers=min(8, len(feeds))) as pool:
        futures = {pool.submit(_fetch_one_feed, url, keyword): url for url in feeds}
        for future in as_completed(futures):
            for art in future.result():
                if art.url and art.url not in articles:
                    articles[art.url] = art

    return list(articles.values())


def title_similarity(a: str, b: str) -> float:
    matcher = SequenceMatcher(None, a.lower(), b.lower())
    # Cheap upper-bound check first; skip the expensive ratio() if it can't
    # possibly clear the threshold.
    if matcher.quick_ratio() < 0.45:
        return 0.0
    return matcher.ratio()


def group_similar(articles: list[Article], threshold: float = 0.45) -> list[list[Article]]:
    groups = []
    used = [False] * len(articles)

    for i, art in enumerate(articles):
        if used[i]:
            continue
        group = [art]
        used[i] = True
        for j in range(i + 1, len(articles)):
            if used[j]:
                continue
            if title_similarity(art.title, articles[j].title) >= threshold:
                group.append(articles[j])
                used[j] = True
        groups.append(group)

    return groups


def run(keyword: str) -> None:
    articles = fetch_articles(keyword)
    if not articles:
        print("No matching articles found.")
        return

    groups = sorted(group_similar(articles), key=len, reverse=True)

    for group in groups:
        print(f"\n=== Story cluster ({len(group)} outlet{'s' if len(group) > 1 else ''}) ===")
        for art in group:
            print(f"  [{art.bias.upper():13}] {art.title}")
            print(f"                {art.url}")


def main():
    parser = argparse.ArgumentParser(description="Track a news topic across outlets with bias tagging.")
    parser.add_argument("keyword", nargs="?", help="Topic/keyword to search for")
    args = parser.parse_args()

    keyword = args.keyword or input("Enter a topic/prompt to search for: ")
    run(keyword)


if __name__ == "__main__":
    main()