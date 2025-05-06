from flask import Blueprint, request, make_response, jsonify
import feedparser
import ssl
from datetime import datetime, timedelta
import time

ssl._create_default_https_context = ssl._create_unverified_context

rss_bp = Blueprint("rss_bp", __name__)

rss_urls = [
    'https://www.infosecurity-magazine.com/rss/news/',
    'https://www.bleepingcomputer.com/feed/',
    'https://feeds.feedburner.com/eset/blog',
    'https://feeds.feedburner.com/TheHackersNews?format=xml',
    'https://news.sophos.com/en-us/category/threat-research/feed/'
]

keywords = ['vulnerability', 'flaw']

def key_word(entry, keywords):
    title = entry.title.lower()
    description = entry.get('description', '').lower()
    for keyword in keywords:
        if keyword.lower() in title or keyword.lower() in description:
            return True
    return False

def publish_timeline(published_parsed):
    if not published_parsed:
        return False

    published_datetime = datetime.fromtimestamp(time.mktime(published_parsed))
    timeline = datetime.now() - timedelta(days=7)
    return published_datetime >= timeline

@rss_bp.route("/api/v1.0/rss", methods=["GET"])
def find_filtered_rss():
    filtered_entries = []

    for url in rss_urls:
        feed = feedparser.parse(url)

        if feed.bozo:
            continue

        for entry in feed.entries:
            if key_word(entry, keywords) and publish_timeline(entry.get('published_parsed')):
                filtered_entries.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', 'No publish date'),
                    'description': entry.get('description', 'No description available'),
                    'source': url
                })

    return jsonify(filtered_entries)
