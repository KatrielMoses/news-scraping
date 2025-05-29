# Web Scraping News RSS Feeds

This project scrapes news headlines and summaries from multiple international RSS feeds and stores them in CSV, JSON, and SQLite database formats.

## Installation 
terminal: 
pip install -r req.txt

## Execute
terminal:
python main.py

## Problems faced
-several feeds used previously were either outdated, broken or restricts the usage. <br/>
-had to implement the use of warnings due to the warning caused by BeautifulSoup misinterpreting a filename-like string.<br/>
-due to some restrictions on the urls, had to implement a 10 second timeout to figure out the websites which are restricting access.<br/>
-Max retries exceeded with url: /reuters/canada (Caused by NameResolutionError("<urllib3.connection.HTTPConnection object at 0x000001F403141060>: Failed to resolve 'feeds.reuters.com' ([Errno 11001] getaddrinfo failed)")), which was due to feeds.routers.com probably being blocked by my network or the ISP.<br/>

