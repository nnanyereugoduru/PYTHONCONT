# main.py

from scraper import fetch_articles
from sources import get_source_bias

def run(keyword):
    articles = fetch_articles(keyword)
    for a in articles:
        bias = get_source_bias(a["url"])
        print(f"[{bias.upper()}] {a['title']}")
        print(f"   {a['url']}\n")

if __name__ == "__main__":
    topic = input("Enter a topic/prompt to search for: ")
    run(topic)