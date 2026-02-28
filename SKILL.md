---
name: search-cluster
description: Aggregated search aggregator using Google CSE, GNews RSS, Wikipedia, Reddit, and Scrapling.
---

# Search Cluster (Complete Edition v2.9)

A multi-provider search aggregator designed for high-availability and security.

## Installation
The scrapling provider requires a dedicated virtual environment.
1. Create a venv: python3 -m venv venv/scrapling
2. Install scrapling: venv/scrapling/bin/pip install scrapling
3. Provide the path to the venv binary in SCRAPLING_PYTHON_PATH.

## Security Posture
- Subprocess Isolation: Query inputs are passed as arguments to stealth_fetch.py.
- Strict TLS: Mandatory SSL verification on all providers.
- Sanitization: Integrated native internal scrubber (Path Neutral).

## Requirements and Environment
Declare these variables in your environment or vault:

| Variable | Description |
|---|---|
| GOOGLE_API_KEY | API Key for Google Custom Search. |
| GOOGLE_CSE_ID | Search Engine ID for Google CSE. |
| SCRAPLING_PYTHON_PATH | Path to the scrapling venv python binary. |
| REDIS_HOST | Optional: For result caching. |

## Providers
- google: Official Google Custom Search.
- wiki: Wikipedia OpenSearch API.
- reddit: Reddit JSON search API.
- gnews: Google News RSS aggregator.
- scrapling: Headless stealth scraping (via DuckDuckGo).

## Workflow
1. Execute: scripts/search-cluster.py all "<query>"
2. Output is structured JSON with source, title, link, and sanitized snippet.
