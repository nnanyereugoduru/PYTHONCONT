
"""
webapp.py — A tiny local website for bias_tracker.py.

This does NOT reimplement any tracking/clustering logic. It imports the
functions directly from bias_tracker.py and renders their output with
bias_tracker.render_html(), so the website can never drift out of sync
with the underlying code — if you change how clustering or bias-tagging
works in bias_tracker.py, the site picks it up automatically.

Run:
    python3 webapp.py            # serves on http://localhost:8000
    python3 webapp.py --port 9000

Stdlib only (beyond the feedparser dependency bias_tracker.py already needs).
"""

from __future__ import annotations

import argparse
import html
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import bias_tracker as bt

PAGE_HEADER = """<!doctype html><html><head><meta charset="utf-8">
<title>Bias Tracker</title>
<style>{style}</style></head><body>
<nav><a href="/">&larr; New search</a></nav>
<h1>Bias Tracker</h1>
<p class="summary">Cross-outlet coverage lookup, powered by bias_tracker.py</p>
<form class="search" method="get" action="/search">
  <input type="text" name="q" placeholder="Topic, e.g. 'budget bill'" value="{q}" required>
  <label><input type="checkbox" name="left" {left_checked}> Left</label>
  <label><input type="checkbox" name="right" {right_checked}> Right</label>
  <label><input type="checkbox" name="undetermined" {und_checked}> Undetermined</label>
  <button type="submit">Search</button>
</form>
"""


def render_page(body: str, q: str = "", bias_filter: list[str] | None = None) -> str:
    bias_filter = bias_filter or []
    header = PAGE_HEADER.format(
        style=bt.HTML_STYLE,
        q=html.escape(q, quote=True),
        left_checked="checked" if not bias_filter or "left" in bias_filter else "",
        right_checked="checked" if not bias_filter or "right" in bias_filter else "",
        und_checked="checked" if not bias_filter or "undetermined" in bias_filter else "",
    )
    return f"{header}{body}</body></html>"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep console quiet; errors still surface via 500 responses

    def _send_html(self, content: str, status: int = 200):
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/":
            self._send_html(render_page("<p>Enter a topic above to see how outlets across the "
                                         "spectrum are covering it.</p>"))
            return

        if parsed.path == "/search":
            keyword = (params.get("q", [""])[0]).strip()
            bias_filter = [b for b in ("left", "right", "undetermined") if params.get(b)]
            if not keyword:
                self._send_html(render_page("<p>Please enter a topic.</p>"), status=400)
                return

            try:
                bias_table, feeds = bt.load_config()
                started = time.time()
                articles = bt.fetch_articles(
                    keyword, feeds, bias_table,
                    max_age_days=14, workers=10, use_cache=True, cache_ttl_minutes=15,
                )
                if bias_filter:
                    articles = [a for a in articles if a.bias in bias_filter]

                if not articles:
                    self._send_html(render_page(
                        f"<p>No matching articles found for &ldquo;{html.escape(keyword)}&rdquo;.</p>",
                        q=keyword, bias_filter=bias_filter))
                    return

                clusters = bt.group_similar(articles, threshold=0.45)
                clusters.sort(key=lambda c: c.outlet_count, reverse=True)
                elapsed = time.time() - started

                body = bt.render_html(clusters, keyword, embedded=True)
                body += f'<p class="summary">Fetched in {elapsed:.1f}s from {len(feeds)} feeds.</p>'
                self._send_html(render_page(body, q=keyword, bias_filter=bias_filter))
            except Exception as e:
                self._send_html(render_page(f"<p>Something went wrong: {html.escape(str(e))}</p>",
                                             q=keyword, bias_filter=bias_filter), status=500)
            return

        self._send_html(render_page("<p>Not found.</p>"), status=404)


def main():
    parser = argparse.ArgumentParser(description="Serve the bias_tracker website locally.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="localhost")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Serving at http://{args.host}:{args.port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
        server.shutdown()


if __name__ == "__main__":
    main()
