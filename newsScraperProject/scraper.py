import feedparser

RSS_FEEDS = {
    "https://feeds.foxnews.com/foxnews/latest",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.bbci.co.uk/news/rss.xml",
}

def fetch_articles(keyword):
    matches = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "")
            if keyword.lower() in title.lower() or keyword.lower() in summary.lower():
                matches.append({
                    "title": title,
                    "url": link,
                    "summary": summary,
                    "source_feed": feed_url,
                })
    return matches