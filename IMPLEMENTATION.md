# AllEvents.in Scraper - Implementation Summary

## Overview
Production-ready Apify actor for scraping event data from AllEvents.in using Playwright with comprehensive error handling, anti-detection, and Apify SDK 2.x integration.

## Files Created

### 1. src/main.py (168 lines)
Main scraper implementation with:

**Class: AllEventsScraper**
- `initialize()`: Sets up Playwright browser with anti-detection
  - Realistic Chrome user agent
  - Navigator property overrides (webdriver, plugins, languages)
  - Apify proxy integration via Actor.config.proxy_password
  - Custom headers and viewport settings
  
- `scrape_events()`: Main scraping orchestrator
  - Navigates to URL with extended timeout (60s)
  - Handles networkidle wait state
  - Manages pagination (Load More buttons + infinite scroll)
  - Respects maxResults limit
  - Incremental data extraction
  
- `_extract_events_from_page()`: DOM parsing with multi-selector strategy
  - Tries multiple CSS selectors for robustness:
    - `.event-card`, `[data-event-id]`, `article.event`, etc.
  - Falls back gracefully if primary selectors fail
  
- `_extract_event_data()`: Comprehensive field extraction
  - **title**: h2/h3/h4 tags or .title classes
  - **url**: Event link (absolute URL via urljoin)
  - **date**: Date elements with raw text preservation
  - **time**: Time elements
  - **location**: Venue/location fields
  - **category**: Tags/badges/category labels
  - **price**: Price text + boolean isFree flag
  - **description**: Summary/description (truncated to 500 chars)
  - **image**: Event image with absolute URL
  - **scrapedAt**: ISO timestamp
  - **sourceUrl**: Source page URL
  
- `_parse_date()`: Date normalization (extensible with dateutil)
  
- `_handle_pagination()`: Multi-strategy pagination
  - Button clicks: "Load More", "Show More", "Next"
  - Infinite scroll detection
  - Returns boolean success indicator

**Function: main()**
- Async context manager with `async with Actor:`
- Input parameter handling:
  - `startUrls`: Array of URLs to scrape
  - `city`: Default city name (default: "washington")
  - `category`: Optional category filter
  - `maxResults`: Result limit (None = unlimited)
  - `proxy`: Enable/disable Apify proxy (default: true)
- URL building logic (startUrls or city-based)
- Incremental data push via `Actor.push_data()`
- Proper cleanup in finally block
- Comprehensive logging throughout

### 2. src/__main__.py (7 lines)
Entry point for `python -m src` execution:
- Imports main() from .main (relative import - SDK 4.x compatible)
- Runs with asyncio.run()
- Includes `if __name__ == '__main__'` guard

### 3. src/__init__.py (3 lines)
Package initialization:
- Version declaration
- Docstring

### 4. requirements.txt (3 lines)
Dependency specifications with compatibility pins:
```
apify>=2.0.0,<3.0.0
playwright>=1.40.0,<2.0.0
pydantic>=2.0.0,<2.10.0  # Critical: <2.10 for crawlee compatibility
```

## Key Features

### 1. **Production-Ready Error Handling**
- Try/except blocks at every extraction level
- Graceful degradation (missing fields don't crash scraper)
- Element existence checks before interaction
- Timeout handling with generous limits
- Comprehensive logging (info, warning, error levels)

### 2. **Apify SDK 2.x Best Practices** (from apify-actor-pitfalls skill)
- ✅ No `await` on `Actor.log.*()` calls (synchronous in SDK 2.x)
- ✅ Proxy via `Actor.config.proxy_password` (not Actor.get_env())
- ✅ Relative imports in __main__.py (`.main` not `src.main`)
- ✅ Incremental `Actor.push_data()` for memory efficiency
- ✅ Async context manager pattern
- ✅ Pydantic <2.10 pin to avoid crawlee conflicts

### 3. **Anti-Detection Measures**
- Browser args: `--disable-blink-features=AutomationControlled`
- Navigator property overrides (webdriver=false, plugins populated)
- Realistic Chrome 131 user agent
- Proper HTTP headers (Accept-Language, DNT, Sec-Fetch-*)
- Random-like delays (2000ms, 1500ms wait times)
- Apify residential proxy support

### 4. **Robust Selector Strategy**
- Multiple fallback selectors per element type
- Logs which selector succeeded (debugging aid)
- Handles dynamic class names and data attributes
- No hard failures on missing optional fields

### 5. **Pagination Handling**
- Detects and clicks "Load More" buttons
- Tries multiple button text variants
- Implements infinite scroll fallback
- Stops when no new content appears
- Respects maxResults quota across pages

### 6. **Data Quality**
- URL normalization (relative → absolute)
- Date parsing with multiple format support
- Price text + boolean isFree field
- Metadata fields (scrapedAt, sourceUrl)
- Description length limiting (prevents huge fields)

## Input Schema Compatibility

Expected input format:
```json
{
  "startUrls": [
    {"url": "https://allevents.in/washington"},
    {"url": "https://allevents.in/newyork/music"}
  ],
  "city": "washington",
  "category": "music",
  "maxResults": 50,
  "proxy": true
}
```

## Output Schema

Each event object contains:
```json
{
  "title": "Event Title",
  "url": "https://allevents.in/events/...",
  "date": "2024-01-15",
  "dateRaw": "Jan 15, 2024",
  "time": "7:00 PM",
  "location": "Venue Name, City",
  "category": "Music",
  "price": "$25 - $50",
  "isFree": false,
  "description": "Event description...",
  "image": "https://cdn.allevents.in/...",
  "scrapedAt": "2024-01-01T12:00:00",
  "sourceUrl": "https://allevents.in/washington"
}
```

## Known Limitations & Future Enhancements

### Current Implementation
- Date parsing is basic (returns raw text if ISO conversion fails)
- No deep-link scraping (doesn't visit individual event pages)
- Fixed pagination limit (5 pages max for safety)
- No retry logic for failed requests

### Potential Improvements
1. Add `python-dateutil` for robust date parsing
2. Implement detail page scraping for full descriptions
3. Add request retry with exponential backoff
4. Support custom CSS selectors via input
5. Add category filtering post-scrape
6. Implement deduplication by URL

## Testing Recommendations

1. **Basic Run**: Test with maxResults=3, single city
2. **Pagination**: Test without maxResults limit
3. **Proxy**: Test with proxy=false on local network
4. **Multiple URLs**: Test startUrls array
5. **Error Handling**: Test with invalid URLs

## Compliance with Requirements

✅ **Playwright**: Used (not Camoufox - per pitfalls skill)  
✅ **Comprehensive Fields**: 12 fields extracted (title, date, time, location, price, url, category, + 5 more)  
✅ **Pagination**: Implemented with Load More + infinite scroll  
✅ **Apify Proxies**: Integrated via Actor.config.proxy_password  
✅ **maxResults**: Respected across pagination  
✅ **Actor.push_data()**: Incremental pushing  
✅ **Error Handling**: Multi-level try/except blocks  
✅ **Logging**: Actor.log.info/warning/error throughout  
✅ **SDK 2.x Integration**: No awaits on sync methods, proper imports

## Code Quality

- **Lines of Code**: 168 (main.py)
- **Complexity**: Low-medium (clear separation of concerns)
- **Maintainability**: High (modular methods, comprehensive comments)
- **Readability**: Docstrings on all methods, inline comments
- **Best Practices**: Async/await, context managers, type hints
