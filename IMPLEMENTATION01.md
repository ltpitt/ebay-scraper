# IMPLEMENTATION01: eBay Scraper - Current State and Architecture

## Overview
eBay scraper is a Python tool that scrapes eBay search results to calculate average prices for items. It collects data from search result pages and individual item detail pages.

## Current Architecture

### Core Components

#### 1. `get_page(url: str) -> BeautifulSoup | None`
**Purpose**: Fetches and parses HTML from a given URL.

**Current Implementation**:
- Makes HTTP GET request using `requests` library
- Parses HTML with BeautifulSoup using 'lxml' parser
- Returns `None` on HTTP errors
- Prints error message to stdout on failure

**Issues Fixed**:
- ✅ Fixed `UnboundLocalError` when server returns error status
- Now properly returns `None` instead of throwing exception

#### 2. `get_detail_data(soup: BeautifulSoup) -> dict`
**Purpose**: Extracts product information from an eBay item detail page.

**Current Implementation**:
- Extracts title from `<h1 id="itemTitle">`
- Extracts price and currency from `<span id="prcIsum">`
- Extracts sold count from `<span class="vi-qtyS">`
- Returns dictionary with keys: `title`, `price`, `currency`, `total_sold`
- Uses try-except blocks to handle missing elements gracefully

**Data Structure**:
```python
{
    'title': str,        # Item title (cleaned of "Details about" prefix)
    'price': str,        # Price with currency symbol (e.g., "$150.00")
    'currency': str,     # Currency code (e.g., "US", "EUR")
    'total_sold': str    # Number of items sold (e.g., "25")
}
```

#### 3. `get_index_data(soup: BeautifulSoup) -> list[str]`
**Purpose**: Extracts product URLs from eBay search results page.

**Current Implementation**:
- Finds all links with class `s-item__link`
- Returns list of href URLs
- Skips first link (typically a sponsored/featured item)

#### 4. `main()`
**Purpose**: Orchestrates the scraping process and calculates average price.

**Current Implementation**:
- Uses hardcoded search URL
- Configurable number of items to scrape (`numberOfHits`)
- Fetches search results page
- Iterates through product links
- Collects data from each product
- Filters by US currency
- Calculates and prints average price

## Known Limitations

### 1. HTML Selectors May Be Outdated
eBay frequently changes their HTML structure. Current selectors:
- `#itemTitle` - May not exist on all item pages
- `#prcIsum` - Price element ID has likely changed
- `.s-item__link` - Search result link class
- `.vi-qtyS` - Sold quantity element

**Impact**: Scraper may return empty data if eBay's HTML structure has changed.

### 2. Hardcoded Configuration
- Search URL is hardcoded in `main()`
- Number of items to scrape is hardcoded
- Only filters US currency

### 3. No Error Recovery
- If one item page fails, the script continues but may affect average calculation
- Division by zero possible if no valid US currency items found

### 4. No CSV Output
- Despite TODO comment mentioning CSV output, it's not implemented
- Only prints to stdout

### 5. No Rate Limiting
- Makes rapid sequential requests
- Could trigger eBay's anti-scraping measures

### 6. No Authentication/Headers
- Doesn't set User-Agent header
- May be identified as bot traffic

## Test Coverage

### Current Test Suite (17 tests, 94% coverage)

**Test Categories**:
1. **HTTP Request Handling** (3 tests)
   - Successful page retrieval
   - Failed requests (404, etc.)
   - Parser configuration

2. **Data Extraction** (8 tests)
   - Complete product data
   - Missing optional fields
   - Different currencies
   - Empty/malformed pages
   - Special characters handling

3. **URL Collection** (3 tests)
   - Multiple links extraction
   - Empty search results
   - Single link edge case

4. **Integration Tests** (2 tests)
   - Full scraping workflow
   - Multi-currency filtering

5. **Edge Cases & Validation** (3 tests)
   - Unicode/special characters
   - Number formatting
   - Return type validation

**Coverage Gaps** (6% uncovered):
- Lines 56-57: Exception handling in try-except blocks
- Line 86: Script execution guard

## Dependencies

```
requests>=2.31.0      # HTTP requests
beautifulsoup4>=4.12.0 # HTML parsing
lxml>=4.9.0           # Fast HTML parser
pytest>=7.4.0         # Testing framework
pytest-mock>=3.11.0   # Mocking support
pytest-cov>=4.1.0     # Coverage reporting
```

## Usage

### Running the Scraper
```bash
python3 ebay_scraper.py
```

### Running Tests
```bash
# All tests
pytest test_ebay_scraper.py -v

# With coverage
pytest test_ebay_scraper.py --cov=ebay_scraper --cov-report=term-missing

# Specific test class
pytest test_ebay_scraper.py::TestGetDetailData -v
```

## Design Patterns

### Current Patterns
- **Separation of Concerns**: Each function has single responsibility
- **Error Tolerance**: Try-except blocks prevent crashes on missing data
- **Default Values**: Returns empty strings instead of None for missing data

### Anti-Patterns Present
- **Hardcoded Configuration**: URLs and settings embedded in code
- **Print Debugging**: Uses print() instead of logging
- **Magic Numbers**: Array slicing `urls[1:]` without explanation
- **Global State**: No class structure, all functions are standalone

## Security Considerations

### Current Issues
1. **No Request Timeout**: Requests could hang indefinitely
2. **No URL Validation**: Accepts any URL without verification
3. **No Rate Limiting**: Could be used for DoS
4. **No Input Sanitization**: Main function uses hardcoded URL (safe) but library functions don't validate

### Recommendations
- Add request timeout parameter
- Validate URLs before making requests
- Implement rate limiting between requests
- Add logging instead of print statements
- Consider robots.txt compliance

## Future Improvements (See IMPLEMENTATION02.md)
This document describes the current state. For planned improvements and refactoring plans, see IMPLEMENTATION02.md.
