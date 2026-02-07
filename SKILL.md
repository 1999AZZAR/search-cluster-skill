# SKILL: search-cluster

## Description
Unified search tool for Google, Wikipedia, Reddit, and RSS feeds with Redis caching. Use when user asks "search for X", "who is Y", "latest news on Z".

## Setup
1.  Copy `.env.example` to `.env`.
2.  Set `GOOGLE_CSE_KEY` and `GOOGLE_CSE_ID`.
3.  Ensure Redis is running (`redis-server`).

## Usage
- **Role**: Information Scout.
- **Trigger**: "Search for...", "Find info about...", "Check Reddit for...".
- **Output**: Summarized search results (Title, URL, Snippet).

## Capabilities
1.  **Multi-Engine**: Query multiple sources (Google, Wiki, Reddit) in parallel.
2.  **Caching**: Save results to Redis for 24h to save API quota.
3.  **Parsing**: Extract main content from HTML (fallback).

## Reference Materials
- [Search APIs & Caching](references/search-apis.md)
