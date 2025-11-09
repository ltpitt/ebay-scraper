# eBay Scraper

A Python-based web scraper for extracting product information and calculating average prices from eBay search results.

## ⚠️ Current Status

**Version**: 1.0 (Fixed and Tested)
**Test Coverage**: 94% (17 tests passing)
**Status**: ✅ All bugs fixed, comprehensive test suite added

### Recent Changes
- ✅ Fixed critical bug in `get_page()` function (UnboundLocalError)
- ✅ Renamed module to `ebay_scraper.py` for proper Python imports
- ✅ Added comprehensive test suite with 17 tests
- ✅ Added dependencies management (requirements.txt)
- ✅ Added .gitignore for Python artifacts

## 📋 Features

- Scrapes eBay search result pages
- Extracts product details from individual item pages:
  - Product title
  - Price and currency
  - Number of items sold
- Filters results by currency (US dollars by default)
- Calculates average price across multiple listings
- Graceful error handling for missing data

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install requests beautifulsoup4 lxml pytest pytest-mock pytest-cov
```

## 📖 Usage

### Running the Scraper

1. Edit the `main()` function in `ebay_scraper.py` to set your search URL:
```python
url = 'YOUR_EBAY_SEARCH_URL_HERE'
numberOfHits = 15  # Number of items to scrape
```

2. Run the scraper:
```bash
python3 ebay_scraper.py
```

### Example Output
```
{'title': 'LEGO Star Wars Republic Gunship Set 7676', 'price': '$150.00', 'currency': 'US', 'total_sold': '25'}
{'title': 'LEGO Star Wars Item', 'price': '$200.00', 'currency': 'US', 'total_sold': ''}

The average price of this item on Ebay is: $175.00
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest test_ebay_scraper.py -v
```

### Run Tests with Coverage
```bash
pytest test_ebay_scraper.py --cov=ebay_scraper --cov-report=term-missing
```

### Run Specific Test Class
```bash
pytest test_ebay_scraper.py::TestGetDetailData -v
```

## 📁 Project Structure

```
ebay-scraper/
├── ebay_scraper.py          # Main scraper module
├── test_ebay_scraper.py     # Comprehensive test suite
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
├── IMPLEMENTATION01.md      # Current architecture documentation
├── IMPLEMENTATION02.md      # Future improvements and plans
├── LICENSE                  # Project license
└── README.md               # This file
```

## 🔧 API Reference

### `get_page(url: str) -> BeautifulSoup | None`
Fetches and parses an HTML page from the given URL.

**Parameters**:
- `url` (str): The URL to fetch

**Returns**:
- `BeautifulSoup` object if successful
- `None` if request fails

**Example**:
```python
soup = get_page('https://www.ebay.com/...')
if soup:
    # Process the page
```

### `get_detail_data(soup: BeautifulSoup) -> dict`
Extracts product information from an eBay item detail page.

**Parameters**:
- `soup` (BeautifulSoup): Parsed HTML of an eBay item page

**Returns**:
- Dictionary with keys: `title`, `price`, `currency`, `total_sold`
- Empty strings for missing data

**Example**:
```python
data = get_detail_data(soup)
print(f"{data['title']}: {data['currency']} {data['price']}")
```

### `get_index_data(soup: BeautifulSoup) -> list[str]`
Extracts product URLs from an eBay search results page.

**Parameters**:
- `soup` (BeautifulSoup): Parsed HTML of an eBay search page

**Returns**:
- List of product URLs (skips first link)

**Example**:
```python
urls = get_index_data(soup)
for url in urls[:10]:  # First 10 items
    # Process each URL
```

## ⚠️ Known Limitations

1. **HTML Selectors May Be Outdated**: eBay frequently changes their HTML structure
2. **Hardcoded Configuration**: Search URL must be edited in source code
3. **No CSV Export**: Despite TODO comment, CSV export is not implemented
4. **No Rate Limiting**: Makes rapid sequential requests
5. **Currency Filtering**: Only filters by US currency in main()
6. **No Error Recovery**: If parsing fails, returns empty strings

See [IMPLEMENTATION01.md](IMPLEMENTATION01.md) for detailed analysis.

## 🔮 Future Improvements

See [IMPLEMENTATION02.md](IMPLEMENTATION02.md) for comprehensive improvement plans including:

- **Priority 1**: Update HTML selectors, add proper logging, configuration management
- **Priority 2**: CSV export, rate limiting, data validation
- **Priority 3**: OOP refactoring, modular architecture, caching
- **Priority 4**: Integration tests, performance tests, CI/CD
- **Priority 5**: Documentation improvements

## 🧪 Test Suite

The project includes a comprehensive test suite with 94% code coverage:

**Test Categories**:
- ✅ HTTP request handling (success/failure)
- ✅ Data extraction (complete/partial/empty data)
- ✅ URL collection from search results
- ✅ Integration tests (full workflow)
- ✅ Edge cases (special characters, malformed data)
- ✅ Data validation and type checking

**17 Tests**:
```
test_ebay_scraper.py::TestGetPage::test_get_page_success
test_ebay_scraper.py::TestGetPage::test_get_page_failure
test_ebay_scraper.py::TestGetPage::test_get_page_with_lxml
test_ebay_scraper.py::TestGetDetailData::test_get_detail_data_complete
test_ebay_scraper.py::TestGetDetailData::test_get_detail_data_no_sold
test_ebay_scraper.py::TestGetDetailData::test_get_detail_data_different_currency
test_ebay_scraper.py::TestGetDetailData::test_get_detail_data_empty_page
test_ebay_scraper.py::TestGetDetailData::test_get_detail_data_malformed_price
test_ebay_scraper.py::TestGetIndexData::test_get_index_data_success
test_ebay_scraper.py::TestGetIndexData::test_get_index_data_empty
test_ebay_scraper.py::TestGetIndexData::test_get_index_data_single_link
test_ebay_scraper.py::TestMainFunction::test_main_basic_flow
test_ebay_scraper.py::TestMainFunction::test_main_with_multiple_currencies
test_ebay_scraper.py::TestEdgeCases::test_title_with_special_characters
test_ebay_scraper.py::TestEdgeCases::test_sold_with_special_formatting
test_ebay_scraper.py::TestDataValidation::test_get_detail_data_returns_dict
test_ebay_scraper.py::TestDataValidation::test_get_index_data_returns_list
```

## 🤝 Contributing

This project is being prepared for a language port using TDD (Test-Driven Development). The goal is to:

1. ✅ Fix all bugs in the current Python implementation
2. ✅ Create comprehensive test suite
3. 🔄 Achieve 100% test coverage
4. 🔄 Document all behaviors and edge cases
5. ⏳ Port to another language using the test suite as specification

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `pytest test_ebay_scraper.py -v`
4. Make changes
5. Ensure all tests pass
6. Add tests for new functionality

## ⚖️ Legal and Ethical Considerations

**Important**: Web scraping may be subject to legal and ethical restrictions:

- Check eBay's Terms of Service before using this tool
- Respect robots.txt directives
- Implement rate limiting to avoid overloading servers
- Only use for personal, educational, or research purposes
- Do not use for commercial purposes without permission
- Consider using eBay's official API for production use

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🐛 Bug Reports

If you find a bug:
1. Check if it's already documented in IMPLEMENTATION01.md
2. Verify it's reproducible with the test suite
3. Open an issue with:
   - Python version
   - Dependencies versions
   - Steps to reproduce
   - Expected vs actual behavior

## 📚 Documentation

- **IMPLEMENTATION01.md**: Current architecture and design
- **IMPLEMENTATION02.md**: Planned improvements and roadmap
- **test_ebay_scraper.py**: Living documentation of expected behaviors

## 🎯 Project Goals

1. ✅ **Understand the code**: Thoroughly analyzed and documented
2. ✅ **Fix bugs**: Critical UnboundLocalError fixed
3. ✅ **Create test suite**: 17 tests with 94% coverage
4. 🔄 **Prepare for port**: Documentation and test infrastructure ready
5. ⏳ **Port to another language**: Next phase using TDD

---

**Status**: Ready for TDD-based language port 🚀
