# IMPLEMENTATION02: Planned Improvements and Refactoring

## Overview
This document outlines planned improvements to make the eBay scraper more robust, maintainable, and suitable for porting to other languages using TDD.

## Priority 1: Critical Improvements

### 1.1 Update HTML Selectors for Current eBay Structure
**Problem**: eBay's HTML structure has likely changed since the code was written.

**Plan**:
- Research current eBay HTML structure
- Update selectors to match current eBay pages
- Add multiple fallback selectors for resilience
- Document selector update date

**Implementation Strategy**:
```python
# Instead of single selector
title = soup.find('h1', id='itemTitle')

# Use multiple fallbacks
TITLE_SELECTORS = [
    ('h1', {'id': 'itemTitle'}),
    ('h1', {'class': 'x-item-title__mainTitle'}),
    ('h1', {'class': 'it-ttl'}),
]

def get_element_with_fallbacks(soup, selectors):
    for tag, attrs in selectors:
        element = soup.find(tag, attrs)
        if element:
            return element
    return None
```

**Test Requirements**:
- Test each selector independently
- Test fallback behavior
- Test with real eBay HTML samples

### 1.2 Add Proper Error Handling and Logging
**Problem**: Currently uses print() and has limited error context.

**Plan**:
- Replace print() with proper logging
- Add structured error handling
- Include request/response context in errors
- Log to file for debugging

**Implementation Strategy**:
```python
import logging

logger = logging.getLogger(__name__)

def get_page(url, timeout=30):
    try:
        logger.info(f"Fetching URL: {url}")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'lxml')
    except requests.Timeout:
        logger.error(f"Timeout fetching {url}")
        return None
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None
```

**Test Requirements**:
- Test timeout scenarios
- Test various exception types
- Verify logging output

### 1.3 Add Configuration Management
**Problem**: URLs and settings hardcoded in main().

**Plan**:
- Create configuration class/file
- Support command-line arguments
- Support environment variables
- Support config file (YAML/JSON)

**Implementation Strategy**:
```python
import argparse
from dataclasses import dataclass

@dataclass
class ScraperConfig:
    search_url: str
    max_items: int = 15
    currency_filter: str = "US"
    timeout: int = 30
    user_agent: str = "Mozilla/5.0..."
    
def parse_args():
    parser = argparse.ArgumentParser(description='eBay Price Scraper')
    parser.add_argument('--url', required=True, help='eBay search URL')
    parser.add_argument('--max-items', type=int, default=15)
    parser.add_argument('--currency', default='US')
    return parser.parse_args()
```

**Test Requirements**:
- Test argument parsing
- Test default values
- Test invalid inputs

## Priority 2: Feature Enhancements

### 2.1 Implement CSV Export
**Problem**: TODO mentions CSV but not implemented.

**Plan**:
- Add CSV writing functionality
- Support multiple output formats (CSV, JSON)
- Include timestamp and search URL in output
- Handle file I/O errors gracefully

**Implementation Strategy**:
```python
import csv
from datetime import datetime

def save_to_csv(data_list, filename=None):
    if filename is None:
        filename = f"ebay_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'price', 'currency', 'total_sold'])
        writer.writeheader()
        writer.writerows(data_list)
    
    return filename
```

**Test Requirements**:
- Test CSV generation
- Test file creation
- Test with various data inputs
- Test error handling

### 2.2 Add Rate Limiting and Respectful Scraping
**Problem**: No delays between requests.

**Plan**:
- Add configurable delay between requests
- Check robots.txt before scraping
- Add User-Agent header
- Implement exponential backoff on errors

**Implementation Strategy**:
```python
import time
from urllib.robotparser import RobotFileParser

class RateLimiter:
    def __init__(self, min_delay=1.0):
        self.min_delay = min_delay
        self.last_request = 0
    
    def wait(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_request = time.time()

def check_robots_txt(url):
    rp = RobotFileParser()
    rp.set_url(f"{url.scheme}://{url.netloc}/robots.txt")
    rp.read()
    return rp.can_fetch("*", url.geturl())
```

**Test Requirements**:
- Test rate limiting timing
- Test robots.txt parsing
- Mock time.sleep for testing

### 2.3 Add Data Validation and Cleaning
**Problem**: Data returned as-is without validation.

**Plan**:
- Validate price format and convert to float
- Normalize currency codes
- Clean and validate sold counts
- Add data quality score

**Implementation Strategy**:
```python
from decimal import Decimal
import re

def clean_price(price_str):
    """Extract numeric price from string like '$150.00'"""
    match = re.search(r'\d+\.?\d*', price_str.replace(',', ''))
    return Decimal(match.group()) if match else None

def clean_sold_count(sold_str):
    """Extract numeric sold count from string like '1,234 sold'"""
    clean = sold_str.replace(',', '').replace('\xa0', '')
    match = re.search(r'\d+', clean)
    return int(match.group()) if match else None

def validate_item_data(data):
    """Return data quality score and cleaned data"""
    score = 0
    cleaned = data.copy()
    
    if data['title']:
        score += 25
    if data['price'] and (cleaned['price'] := clean_price(data['price'])):
        score += 40
    if data['currency']:
        score += 20
    if data['total_sold'] and (cleaned['total_sold'] := clean_sold_count(data['total_sold'])):
        score += 15
    
    cleaned['quality_score'] = score
    return cleaned
```

**Test Requirements**:
- Test various price formats
- Test sold count formats
- Test quality scoring

## Priority 3: Architecture Improvements

### 3.1 Refactor to Object-Oriented Design
**Problem**: All functions are standalone, no state management.

**Plan**:
- Create ScraperSession class
- Create ItemData dataclass
- Create ResultSet class for aggregations
- Separate concerns into modules

**Implementation Strategy**:
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ItemData:
    url: str
    title: str
    price: Optional[float]
    currency: str
    total_sold: Optional[int]
    quality_score: int
    
    @classmethod
    def from_soup(cls, soup, url):
        """Factory method to create ItemData from BeautifulSoup"""
        # Extract and clean data
        pass

class ScraperSession:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.rate_limiter = RateLimiter(config.min_delay)
        self.results: List[ItemData] = []
    
    def scrape_search_page(self, url):
        """Scrape a search results page"""
        pass
    
    def scrape_item_page(self, url):
        """Scrape an individual item page"""
        pass
    
    def calculate_statistics(self):
        """Calculate price statistics from results"""
        pass

class ResultSet:
    def __init__(self, items: List[ItemData]):
        self.items = items
    
    def filter_by_currency(self, currency):
        return [item for item in self.items if item.currency == currency]
    
    def average_price(self):
        prices = [item.price for item in self.items if item.price]
        return sum(prices) / len(prices) if prices else 0
    
    def to_csv(self, filename):
        """Export to CSV"""
        pass
    
    def to_json(self, filename):
        """Export to JSON"""
        pass
```

**Test Requirements**:
- Test class initialization
- Test method interactions
- Test state management

### 3.2 Separate Concerns into Modules
**Problem**: Single file contains all functionality.

**Plan**:
- `scraper/` package structure
- `scraper/http.py` - HTTP requests and caching
- `scraper/parser.py` - HTML parsing logic
- `scraper/models.py` - Data models
- `scraper/export.py` - Export functionality
- `scraper/config.py` - Configuration
- `scraper/cli.py` - Command-line interface

**Directory Structure**:
```
ebay-scraper/
├── scraper/
│   ├── __init__.py
│   ├── http.py
│   ├── parser.py
│   ├── models.py
│   ├── export.py
│   ├── config.py
│   └── cli.py
├── tests/
│   ├── __init__.py
│   ├── test_http.py
│   ├── test_parser.py
│   ├── test_models.py
│   └── test_export.py
├── ebay_scraper.py  # Legacy compatibility
├── setup.py
├── requirements.txt
└── README.md
```

**Test Requirements**:
- Test each module independently
- Test module interactions
- Test import structure

### 3.3 Add Caching Layer
**Problem**: Re-fetches same pages on multiple runs.

**Plan**:
- Add optional HTTP response caching
- Cache parsed results
- Configurable cache duration
- Cache invalidation strategy

**Implementation Strategy**:
```python
import hashlib
import pickle
from pathlib import Path

class ResponseCache:
    def __init__(self, cache_dir='.cache', ttl=3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl
    
    def _get_cache_key(self, url):
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url):
        cache_file = self.cache_dir / self._get_cache_key(url)
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < self.ttl:
                return pickle.load(cache_file.open('rb'))
        return None
    
    def set(self, url, data):
        cache_file = self.cache_dir / self._get_cache_key(url)
        pickle.dump(data, cache_file.open('wb'))
```

**Test Requirements**:
- Test cache hit/miss
- Test TTL expiration
- Test cache invalidation

## Priority 4: Testing and Quality

### 4.1 Add Integration Tests with Real HTML Samples
**Problem**: Only unit tests with mocked HTML.

**Plan**:
- Save real eBay HTML samples (anonymized)
- Create integration tests using saved HTML
- Test against multiple eBay domains (.com, .co.uk, .de)
- Automated selector validation

**Implementation Strategy**:
```
tests/
├── fixtures/
│   ├── search_page_us.html
│   ├── search_page_uk.html
│   ├── item_page_basic.html
│   ├── item_page_no_sold.html
│   └── item_page_multiple_currencies.html
└── test_integration.py
```

**Test Requirements**:
- Test with real HTML structure
- Test cross-domain compatibility
- Validate selector updates

### 4.2 Add Performance Tests
**Problem**: No performance benchmarks.

**Plan**:
- Measure scraping speed
- Test with large result sets
- Memory usage profiling
- Identify bottlenecks

**Implementation Strategy**:
```python
import pytest
import time

@pytest.mark.performance
def test_scraping_speed():
    start = time.time()
    # Scrape 100 items
    duration = time.time() - start
    assert duration < 120  # Should complete in 2 minutes
```

### 4.3 Add Continuous Integration
**Problem**: No automated testing on commits.

**Plan**:
- GitHub Actions workflow
- Run tests on push/PR
- Check code coverage
- Lint with flake8/black
- Type checking with mypy

**Implementation Strategy**:
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=scraper
      - run: flake8 scraper/
```

## Priority 5: Documentation

### 5.1 Add Comprehensive README
**Plan**:
- Installation instructions
- Usage examples
- API documentation
- Configuration options
- Troubleshooting guide
- Legal/ethical considerations

### 5.2 Add API Documentation
**Plan**:
- Docstrings for all functions
- Type hints throughout
- Sphinx documentation generation
- Usage examples in docstrings

### 5.3 Add Contributing Guide
**Plan**:
- How to set up development environment
- How to run tests
- Code style guidelines
- How to submit PRs

## Language Port Preparation

### Requirements for TDD-Based Port

1. **Complete Test Coverage**
   - All edge cases documented
   - All behaviors tested
   - Clear input/output specifications

2. **Clear Specifications**
   - Data models documented
   - Function signatures documented
   - Error handling documented

3. **Test Data Sets**
   - Sample HTML for all scenarios
   - Expected outputs documented
   - Edge cases identified

4. **Architecture Documentation**
   - Component interactions
   - State management
   - Error propagation

### Suggested Target Languages

1. **Go**: Good for CLI tools, fast, single binary
2. **Rust**: Maximum performance, safety
3. **TypeScript/Node.js**: Good for web developers
4. **Java**: Enterprise environments

### Port Process

1. **Pre-Port**
   - Achieve 100% test coverage
   - Document all behaviors
   - Create comprehensive test fixtures
   - Freeze feature set

2. **During Port**
   - Port tests first (TDD)
   - Port one component at a time
   - Maintain API compatibility
   - Run tests continuously

3. **Post-Port**
   - Performance comparison
   - Feature parity verification
   - Cross-language integration tests

## Maintenance Guidelines

### Code Review Checklist
- [ ] All functions have docstrings
- [ ] All functions have type hints
- [ ] New features have tests
- [ ] Tests pass locally
- [ ] No hardcoded values
- [ ] Error handling present
- [ ] Logging instead of print()

### Release Process
1. Update version number
2. Update CHANGELOG
3. Run full test suite
4. Test with real eBay pages
5. Update documentation
6. Create git tag
7. Build and publish package

## Timeline Estimate

- Priority 1: 2-3 days
- Priority 2: 3-4 days
- Priority 3: 5-7 days
- Priority 4: 2-3 days
- Priority 5: 2-3 days

**Total Estimated Time**: 14-20 days for complete refactoring

## Success Metrics

- [ ] 100% test coverage
- [ ] All tests passing
- [ ] No hardcoded configuration
- [ ] Proper logging throughout
- [ ] CSV export working
- [ ] Rate limiting implemented
- [ ] OOP refactoring complete
- [ ] Documentation complete
- [ ] CI/CD pipeline working
- [ ] Ready for language port
