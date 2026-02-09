---
name: search-cluster
description: Unified search tool for Google, Wikipedia, Reddit, and RSS feeds with Redis caching. Use when user asks "search for X", "who is Y", "latest news on Z".
---

# Search Cluster

## Setup
1.  Copy `.env.example` to `.env`.
2.  Set `GOOGLE_CSE_KEY` (or `GOOGLE_API_KEY`) and `GOOGLE_CSE_ID`.
3.  Ensure Redis is accessible (host/port or Docker container).

## Usage
- **Role**: Information Scout.
- **Trigger**: "Search for...", "Find info about...", "Check Reddit for...".
- **Output**: JSON list of results (Title, Link, Snippet, Source).

### Commands
```bash
# Search Google
python3 scripts/search-cluster google "query"

# Search All Sources (Parallel)
python3 scripts/search-cluster all "query"

# Fetch RSS Feed
python3 scripts/search-cluster rss "https://rss-url.com/feed"
```

## Capabilities
1.  **Multi-Engine Clustering**: Query Google, Wiki, and Reddit in parallel (`all` mode).
2.  **Robust Caching**: Save results to Redis (TTL 24h) to save API quota.
3.  **Resilient Parsing**: Validates XML for RSS and handles API errors gracefully.

## Reference Materials
- [Search APIs & Caching](references/search-apis.md)
