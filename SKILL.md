---
name: search-cluster
description: Unified search aggregator for Google, Wikipedia, Reddit, NewsAPI, and RSS feeds with optional Redis caching. Supports parallel querying and structured JSON output.
metadata: {"openclaw":{"requires":{"bins":["python3"],"env":["GOOGLE_CSE_KEY","GOOGLE_CSE_ID","NEWSAPI_KEY"]},"install":[{"id":"pip-deps","kind":"exec","command":"pip install redis"}]}}
---

# Search Cluster

Unified search system for multi-source information gathering.

## Prerequisites
- **Binary**: `python3` must be installed.
- **Google Search**: Requires `GOOGLE_CSE_KEY` and `GOOGLE_CSE_ID`.
- **NewsAPI**: Requires `NEWSAPI_KEY`.
- **Cache (Optional)**: Active Redis instance (defaults to localhost:6379).

## Setup
1. Define API keys in your environment or a local `.env` file.
2. Install optional Redis client: `pip install redis`.

## Core Workflows

### 1. Single Source Search
Query a specific engine for targeted results.
- **Usage**: `python3 $WORKSPACE/skills/search-cluster/scripts/search-cluster.py <source> "<query>"`
- **Sources**: `google`, `wiki`, `reddit`, `newsapi`.

### 2. Aggregated Search
Query all supported engines in parallel and aggregate results.
- **Usage**: `python3 $WORKSPACE/skills/search-cluster/scripts/search-cluster.py all "<query>"`

### 3. RSS/Feed Fetching
Retrieve and parse standard RSS or Atom feeds.
- **Usage**: `python3 $WORKSPACE/skills/search-cluster/scripts/search-cluster.py rss "<url>"`

## Reliability & Security
- **Secure Networking**: Enforces strict SSL/TLS verification for all API and feed requests. No unverified fallback is permitted.
- **Namespace Isolation**: Cache keys are prefixed with `search:` to avoid collisions.
- **Local Preference**: Redis connectivity defaults to `localhost`. Users must explicitly set `REDIS_HOST` for remote instances.
- **User Agent**: Uses a standardized `SearchClusterBot` agent to comply with site policies.

## Reference
- **API Setup**: See [references/search-apis.md](references/search-apis.md).
