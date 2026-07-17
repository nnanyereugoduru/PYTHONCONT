import feedparser
from difflib import SequenceMatcher

# ---- Your bias lookup table ----
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

def get_bias(url):
    for domain, bias in SOURCE_BIAS.items():
        if domain in url:
            return bias
    return "undetermined"

# ---- RSS feeds to pull from ----
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

def fetch_articles(keyword):
    matches = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"Skipped {feed_url}: {e}")
            continue

        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "")
            if keyword.lower() in title.lower() or keyword.lower() in summary.lower():
                matches.append({
                    "title": title,
                    "url": link,
                    "bias": get_bias(link),
                })
    return matches

# ---- Group similar titles together (same story, different outlets) ----
def title_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def group_similar(articles, threshold=0.45):
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
            if title_similarity(art["title"], articles[j]["title"]) >= threshold:
                group.append(articles[j])
                used[j] = True
        groups.append(group)

    return groups

def run(keyword):
    articles = fetch_articles(keyword)
    if not articles:
        print("No matching articles found.")
        return

    groups = group_similar(articles)
    # show biggest groups first (most cross-outlet coverage)
    groups.sort(key=len, reverse=True)

    for group in groups:
        print(f"\n=== Story cluster ({len(group)} outlet{'s' if len(group) > 1 else ''}) ===")
        for art in group:
            print(f"  [{art['bias'].upper():13}] {art['title']}")
            print(f"                {art['url']}")

if __name__ == "__main__":
    topic = input("Enter a topic/prompt to search for: ")
    run(topic)