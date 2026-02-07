# Search API Configuration

## Redis Caching Strategy
- **Key Prefix**: `mema:search:cache:<query_hash>`
- **TTL**: 24 hours (default)
- **Serialization**: JSON

## Supported Engines
1.  **Google Custom Search (CSE)**
    - Limit: 100 queries/day (Free Tier)
    - Params: `cx`, `key`, `q`, `num`
    - Good for: General knowledge, news.

2.  **Wikipedia API**
    - Endpoint: `https://en.wikipedia.org/w/api.php`
    - Action: `query`, `prop=extracts`
    - Good for: Entities, history, definitions.

3.  **Reddit (PRAW/JSON)**
    - Endpoint: `https://www.reddit.com/search.json`
    - Good for: Opinions, troubleshooting, recent trends.

4.  **RSS/Atom Feeds**
    - Library: `feedparser`
    - Good for: Blogs, news sites.
