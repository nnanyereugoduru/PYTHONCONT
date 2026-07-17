import requests
from bs4 import BeautifulSoup
import re


def check_product(url):
    headers = {"User-Agent": "Mozilla/5.0 (learning project)"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.encoding = "utf-8"
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.select_one("h1").get_text(strip=True)
    price_text = soup.select_one("p.price_color").get_text(strip=True)
    price = float(re.sub(r"[^\d.]", "", price_text))
    stock_text = soup.select_one("p.availability").get_text(strip=True)
    in_stock = "In stock" in stock_text

    return {"title": title, "price": price, "in_stock": in_stock}

if __name__ == "__main__":
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    result = check_product(url)
    print(result)