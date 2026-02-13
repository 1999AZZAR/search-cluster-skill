---
name: search-cluster
description: Unified search tool for Google, Wikipedia, Reddit, and RSS feeds with Redis caching. Use when user asks "search for X", "who is Y", "latest news on Z".
---

# Search Cluster

## Overview
A unified search aggregator that queries multiple sources (Google, Wikipedia, Reddit, RSS) in parallel. It caches results in Redis to optimize performance and reduce API usage.

## Setup
1.  Copy `.env.example` to `.env`.
2.  Set `GOOGLE_CSE_KEY` (or `GOOGLE_API_KEY`) and `GOOGLE_CSE_ID`.
3.  Ensure Redis is accessible (host/port or Docker container).

## Configuration
This skill requires the following environment variables in `.env`:

| Variable | Description | Required? |
| :--- | :--- | :--- |
| `GOOGLE_CSE_KEY` | Google Custom Search JSON API Key | Yes (for Google) |
| `GOOGLE_CSE_ID` | Google Custom Search Engine ID (cx) | Yes (for Google) |
| `REDIS_HOST` | Redis hostname (default: localhost) | No |
| `REDIS_PORT` | Redis port (default: 6379) | No |
| `REDDIT_USER_AGENT`| Custom User-Agent for Reddit API | No |

## Usage
- **Role**: Information Scout.
- **Trigger**: "Search for...", "Find info about...", "Check Reddit for...".
- **Output**: JSON list of results (Title, Link, Snippet, Source).

### Commands
#### `scripts/search-cluster.py`
The main aggregator script.

**Syntax:**
```bash
python3 scripts/search-cluster.py <SOURCE> <QUERY>
```

**Sources:** `google`, `wiki`, `reddit`, `rss`, `all`.

**Examples:**
```bash
# Search Google
python3 scripts/search-cluster.py google "query"

# Search All Sources (Parallel)
python3 scripts/search-cluster.py all "query"

# Fetch RSS Feed
python3 scripts/search-cluster.py rss "https://rss-url.com/feed"
```

## Capabilities
1.  **Multi-Engine Clustering**: Query Google, Wiki, and Reddit in parallel (`all` mode).
2.  **Robust Caching**: Save results to Redis (TTL 24h) to save API quota.
3.  **Resilient Parsing**: Validates XML for RSS and handles API errors gracefully.

## Privacy & Data Flow
- **Redis**: Used solely for caching search results (TTL: 24h) to reduce API calls and latency. Can connect to a local instance or a container. No data is sent to external Redis servers.
- **API Calls**:
  - Google: Sent directly to `googleapis.com`.
  - Reddit: Sent to `reddit.com`.
  - Wikipedia: Sent to `wikipedia.org`.
  - RSS: Fetched directly from the source URL.
- **Logs**: No external logging or tracking.

## Reference Materials
- [Search APIs & Caching](references/search-apis.md)
