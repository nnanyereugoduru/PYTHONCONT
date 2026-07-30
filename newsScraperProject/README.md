# bias_tracker

Tracks a news topic across ~25 outlets spanning the political spectrum,
clusters coverage of the same real-world story, and flags stories that
are only being covered by one ideological side ("blind spots").

## Install

```bash
pip install feedparser
```

## Usage

```bash
# Basic console output
python3 bias_tracker.py "budget bill"

# See all known sources and their bias label
python3 bias_tracker.py --list-sources

# Export a shareable HTML report
python3 bias_tracker.py "election" --format html -o report.html

# Only left/right sources, only stories with 3+ outlets, last 3 days
python3 bias_tracker.py "shutdown" --bias left right --min-outlets 3 --max-age-days 3

# JSON/CSV for piping into other tools
python3 bias_tracker.py "tariffs" --format json -o out.json
python3 bias_tracker.py "tariffs" --format csv -o out.csv
```

Run `python3 bias_tracker.py --help` for the full flag list (caching,
concurrency, similarity threshold, etc).

## Customizing sources

The first run writes a `sources.json` next to the script. Edit it to add
feeds or override bias labels — no code changes needed:

```json
{
  "source_bias": { "example.com": "left" },
  "rss_feeds": ["https://example.com/rss.xml"]
}
```

## Known limitations (read before you trust the output)

- **Bias labels are a simplified heuristic**, not an audited rating.
  Edit `sources.json` to match your own judgment.
- **Reuters and AP no longer publish official RSS feeds.** This script
  routes around that via Google News' per-publisher RSS search, which is
  unofficial and could stop working if Google changes that endpoint. If
  it breaks, remove those two entries from `RSS_FEEDS`.
- **Clustering is title-similarity based** (fast, dependency-free) rather
  than semantic — it will occasionally miss stories with very different
  headlines about the same event, or merge unrelated stories with
  coincidentally similar wording. Tune with `--threshold`.
- Some listed feed URLs may drift or go stale over time, same as any RSS
  aggregator — that's why fetch failures are logged and skipped rather
  than crashing the run.
