from flask import Blueprint, request, make_response, jsonify 
from bson import ObjectId
import globals 
import string
import feedparser
import ssl
ssl._create_default_https_context=ssl._create_unverified_context

rss3_bp = Blueprint("rss3_bp", __name__)


rss_url = 'https://www.ncsc.gov.uk/api/1/services/v1/report-rss-feed.xml'
            
keywords = ['']

def key_word(entry, keywords):
    title = entry.title.lower()
    description = entry.get('description', '').lower()
    for keyword in keywords:
        if keyword.lower() in title or keyword.lower() in description:
            return True
    return False

@rss3_bp.route("/api/v1.0/rss3", methods=["GET"])
def find_filtered_rss():
    feed = feedparser.parse(rss_url)

    if feed.bozo:
        return jsonify({"error": "Failed to parse RSS feed"}), 400

    filtered_entries = []

    for entry in feed.entries:
        if key_word(entry, keywords):
            filtered_entries.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                'description': entry.get('description', 'No description available')

            })

    return jsonify(filtered_entries)

