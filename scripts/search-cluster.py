#!/usr/bin/env python3
import sys
import os
import json
import hashlib
import urllib.request
import urllib.parse
import urllib.error
import re
import ssl
import time
import argparse
import concurrent.futures
import xml.etree.ElementTree as ET
from datetime import datetime

# --- Configuration ---
# DO NOT LOAD .env implicitly from parent dirs to avoid leaking host secrets.
# Users should source .env before running or pass vars explicitly.

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_CSE_KEY") or os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Redis Config
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CACHE_TTL = 86400  # 24 hours

# User Agent
USER_AGENT = os.getenv("REDDIT_USER_AGENT", "SearchClusterBot/1.0")

# --- Redis Client ---
redis_client = None
try:
    import redis
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)
        redis_client.ping()
    except Exception:
        # Redis optional, continue without cache if unreachable
        redis_client = None
except ImportError:
    # Redis optional
    redis_client = None

def redis_set(key, value):
    if redis_client:
        try:
            redis_client.setex(key, CACHE_TTL, value)
        except:
            pass

def redis_get(key):
    if redis_client:
        try:
            return redis_client.get(key)
        except:
            pass
    return None

# --- Networking Helper ---
def fetch_url(url, headers=None, timeout=10):
    if headers is None:
        headers = {"User-Agent": USER_AGENT}
    
    req = urllib.request.Request(url, headers=headers)
    
    # SSL Context - Secure by default
    # If users need to bypass, they should configure certificates properly on the host
    # We do NOT disable SSL verification globally.
    ctx = ssl.create_default_context()
    
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        return None
    except Exception:
        return None

def fetch_json(url, headers=None):
    data = fetch_url(url, headers)
    if data:
        try:
            return json.loads(data.decode())
        except:
            return {}
    return {}

# --- Search Providers ---

def google_search(query):
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return {"error": "Missing Google API Key or CSE ID"}

    cache_key = f"search:google:{hashlib.md5(query.encode()).hexdigest()}"
    cached = redis_get(cache_key)
    if cached: return json.loads(cached)

    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={urllib.parse.quote(query)}"
    data = fetch_json(url)
    results = []
    
    if "items" in data:
        for item in data["items"]:
            results.append({
                "source": "google",
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet", "")
            })
    
    if results:
        redis_set(cache_key, json.dumps(results))
    return results

def wiki_search(query):
    cache_key = f"search:wiki:{hashlib.md5(query.encode()).hexdigest()}"
    cached = redis_get(cache_key)
    if cached: return json.loads(cached)

    url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit=5&namespace=0&format=json"
    data = fetch_json(url)
    results = []
    
    if isinstance(data, list) and len(data) > 3:
        for i in range(len(data[1])):
            results.append({
                "source": "wiki",
                "title": data[1][i],
                "link": data[3][i],
                "snippet": data[2][i]
            })
            
    if results:
        redis_set(cache_key, json.dumps(results))
    return results

def reddit_search(query):
    cache_key = f"search:reddit:{hashlib.md5(query.encode()).hexdigest()}"
    cached = redis_get(cache_key)
    if cached: return json.loads(cached)

    headers = {"User-Agent": USER_AGENT}
    url = f"https://www.reddit.com/search.json?q={urllib.parse.quote(query)}&limit=5&sort=relevance"
    
    data = fetch_json(url, headers=headers)
    results = []
    
    if "data" in data and "children" in data["data"]:
        for child in data["data"]["children"]:
            post = child["data"]
            results.append({
                "source": "reddit",
                "title": post.get("title"),
                "link": f"https://reddit.com{post.get('permalink')}",
                "snippet": f"Subreddit: r/{post.get('subreddit')} | Score: {post.get('score')} | {post.get('selftext', '')[:100]}..."
            })
            
    if results:
        redis_set(cache_key, json.dumps(results))
    return results

def rss_fetch(url):
    cache_key = f"search:rss:{hashlib.md5(url.encode()).hexdigest()}"
    cached = redis_get(cache_key)
    if cached: return json.loads(cached)

    xml_data = fetch_url(url)
    if not xml_data:
        return []

    results = []
    try:
        root = ET.fromstring(xml_data)
        # Handle RSS 2.0
        for item in root.findall(".//item")[:5]:
            title = item.find("title")
            link = item.find("link")
            desc = item.find("description")
            results.append({
                "source": "rss",
                "title": title.text if title is not None else "No Title",
                "link": link.text if link is not None else url,
                "snippet": desc.text[:200] if desc is not None and desc.text else ""
            })
        
        # Handle Atom if RSS failed or empty (basic check)
        if not results:
            for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry")[:5]:
                title = entry.find("{http://www.w3.org/2005/Atom}title")
                link = entry.find("{http://www.w3.org/2005/Atom}link")
                summary = entry.find("{http://www.w3.org/2005/Atom}summary")
                results.append({
                    "source": "rss",
                    "title": title.text if title is not None else "No Title",
                    "link": link.attrib.get("href") if link is not None else url,
                    "snippet": summary.text[:200] if summary is not None and summary.text else ""
                })

    except ET.ParseError:
        return [{"error": "Failed to parse RSS feed"}]

    if results:
        redis_set(cache_key, json.dumps(results))
    return results

def search_all(query):
    """Query all sources in parallel and aggregate results."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_google = executor.submit(google_search, query)
        future_wiki = executor.submit(wiki_search, query)
        future_reddit = executor.submit(reddit_search, query)
        
        # Collect results
        results = []
        try:
            g_res = future_google.result()
            if isinstance(g_res, list): results.extend(g_res)
        except: pass
        
        try:
            w_res = future_wiki.result()
            if isinstance(w_res, list): results.extend(w_res)
        except: pass
        
        try:
            r_res = future_reddit.result()
            if isinstance(r_res, list): results.extend(r_res)
        except: pass
        
    return results

# --- Main ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search Cluster Tool")
    parser.add_argument("source", choices=["google", "wiki", "reddit", "rss", "all"], help="Search source")
    parser.add_argument("query", help="Search query or RSS URL")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    try:
        if args.source == "google":
            print(json.dumps(google_search(args.query), indent=2))
        elif args.source == "wiki":
            print(json.dumps(wiki_search(args.query), indent=2))
        elif args.source == "reddit":
            print(json.dumps(reddit_search(args.query), indent=2))
        elif args.source == "rss":
            print(json.dumps(rss_fetch(args.query), indent=2))
        elif args.source == "all":
            print(json.dumps(search_all(args.query), indent=2))
            
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
