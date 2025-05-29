import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import sqlite3
import time
from datetime import datetime
import warnings
from bs4 import MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

FEEDS = [
    {"source": "BBC News",           "country": "UK",           "url": "http://feeds.bbci.co.uk/news/rss.xml"},
    {"source": "CNN",                "country": "USA",          "url": "http://rss.cnn.com/rss/edition.rss"},
    {"source": "Al Jazeera",         "country": "Qatar",        "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"source": "NHK",                "country": "Japan",        "url": "https://www3.nhk.or.jp/rss/news/cat0.xml"},
    {"source": "NDTV",               "country": "India",        "url": "https://feeds.feedburner.com/ndtvnews-top-stories"},
    {"source": "Korea Herald",       "country": "South Korea",   "url": "http://www.koreaherald.com/rss/rss_welcome.php"},
    {"source": "Le Monde",           "country": "France",        "url": "https://www.lemonde.fr/rss/une.xml"},
    {"source": "Der Spiegel",        "country": "Germany",       "url": "https://www.spiegel.de/international/index.rss"},
    {"source": "El Pais",            "country": "Spain",         "url": "https://elpais.com/rss/feed.html?feedId=1022"},
    {"source": "Folha de S.Paulo",   "country": "Brazil",        "url": "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml"},
    {"source": "RT",                 "country": "Russia",        "url": "https://www.rt.com/rss/news"},
    {"source": "The Australian",     "country": "Australia",     "url": "https://www.theaustralian.com.au/rss"},
    {"source": "The Guardian",       "country": "UK",            "url": "https://www.theguardian.com/uk/rss"},
    {"source": "Times of India",     "country": "India",         "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"},
    {"source": "CNA", "country": "Singapore", "url": "https://www.channelnewsasia.com/news/rss"},
    {"source": "Xinhua", "country": "China", "url": "http://www.xinhuanet.com/english/rss/worldrss.xml"},
    {"source": "Excélsior", "country": "Mexico", "url": "https://www.excelsior.com.mx/rss.xml"},
    {"source": "Detik News", "country": "Indonesia", "url": "https://rss.detik.com/index.php/detikcom"},
    {"source": "Clarín", "country": "Argentina", "url": "https://www.clarin.com/rss/lo-ultimo/"},
    {"source": "Global News", "country": "Canada", "url": "https://globalnews.ca/feed/"},

    #more feeds can be added if required
]


def fetch_feed(url):
    """Download and parse an RSS feed from a URL."""
    try:
        response = requests.get(url, timeout=10)  # 10-second timeout
        response.raise_for_status()
        return feedparser.parse(response.content)
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return feedparser.parse('')  # return empty


def parse_entries(feed, source, country):
    """Extract structured article data from feed entries."""
    articles = []
    for entry in feed.entries:
        # Parse basic fields
        title = entry.get('title', '').strip()
        link = entry.get('link', '').strip()
        published = entry.get('published', entry.get('updated', '')).strip()
        # Convert published to ISO format
        try:
            published_dt = datetime(*entry.published_parsed[:6])
            published = published_dt.isoformat()
        except:
            pass
        summary = BeautifulSoup(entry.get('summary', ''), 'html.parser').get_text().strip()

        articles.append({
            'source': source,
            'country': country,
            'title': title,
            'link': link,
            'published': published,
            'summary': summary
        })
    return articles

def save_to_csv(data, filename='news_data.csv'):
    df = pd.DataFrame(data)
    df.drop_duplicates(subset='link', inplace=True)
    df.to_csv(filename, index=False, encoding='utf-8')


def save_to_json(data, filename='news_data.json'):
    # Deduplicate by link
    unique = {item['link']: item for item in data}
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(list(unique.values()), f, ensure_ascii=False, indent=2)


def save_to_sqlite(data, db_name='news.db'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    # Create table if not exists
    c.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        link TEXT PRIMARY KEY,
        source TEXT,
        country TEXT,
        title TEXT,
        published TEXT,
        summary TEXT
    )
    ''')
    # Insert or ignore duplicates
    for item in data:
        c.execute('''INSERT OR IGNORE INTO articles
                     (link, source, country, title, published, summary)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (item['link'], item['source'], item['country'],
                   item['title'], item['published'], item['summary']))
    conn.commit()
    conn.close()

def main():
    all_articles = []

    for feed_meta in FEEDS:
        print(f"Fetching {feed_meta['source']} ({feed_meta['country']}) -> {feed_meta['url']} ...")
        feed = fetch_feed(feed_meta['url'])
        entries = parse_entries(feed, feed_meta['source'], feed_meta['country'])
        all_articles.extend(entries)
        time.sleep(1)  # Be kind to servers

    # Save outputs
    save_to_csv(all_articles, 'news_data.csv')
    save_to_json(all_articles, 'news_data.json')
    save_to_sqlite(all_articles, 'news.db')

    print("Completed! Data saved to CSV, JSON, and SQLite.")


if __name__ == '__main__':
    main()