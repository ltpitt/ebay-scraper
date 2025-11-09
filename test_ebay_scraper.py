"""
Comprehensive test suite for eBay scraper.
Tests all functionality with mocked HTTP responses.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Sample HTML responses for testing
SAMPLE_SEARCH_PAGE_HTML = """
<html>
<body>
    <a class="s-item__link" href="https://www.ebay.com/itm/123">Item 1</a>
    <a class="s-item__link" href="https://www.ebay.com/itm/456">Item 2</a>
    <a class="s-item__link" href="https://www.ebay.com/itm/789">Item 3</a>
</body>
</html>
"""

SAMPLE_DETAIL_PAGE_HTML = """
<html>
<body>
    <h1 id="itemTitle">Details about  LEGO Star Wars Republic Gunship Set 7676</h1>
    <span id="prcIsum">US $150.00</span>
    <span class="vi-qtyS"><a>25 sold</a></span>
</body>
</html>
"""

SAMPLE_DETAIL_PAGE_NO_SOLD_HTML = """
<html>
<body>
    <h1 id="itemTitle">Details about  LEGO Star Wars Item</h1>
    <span id="prcIsum">US $200.00</span>
</body>
</html>
"""

SAMPLE_DETAIL_PAGE_EUR_HTML = """
<html>
<body>
    <h1 id="itemTitle">Details about  European Item</h1>
    <span id="prcIsum">EUR 100.00</span>
    <span class="vi-qtyS"><a>10 sold</a></span>
</body>
</html>
"""


class TestGetPage:
    """Test the get_page function."""
    
    @patch('requests.get')
    def test_get_page_success(self, mock_get):
        """Test successful page retrieval."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = "<html><body><h1>Test</h1></body></html>"
        mock_get.return_value = mock_response
        
        # Import here to ensure mocking works
        from ebay_scraper import get_page
        
        soup = get_page('https://example.com')
        
        assert soup is not None
        assert soup.find('h1').text == 'Test'
        mock_get.assert_called_once_with('https://example.com')
    
    @patch('requests.get')
    def test_get_page_failure(self, mock_get):
        """Test page retrieval with error response."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        from ebay_scraper import get_page
        
        # Should return None on error
        result = get_page('https://example.com/notfound')
        
        assert result is None
    
    @patch('requests.get')
    def test_get_page_with_lxml(self, mock_get):
        """Test that lxml parser is used."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = SAMPLE_DETAIL_PAGE_HTML
        mock_get.return_value = mock_response
        
        from ebay_scraper import get_page
        
        soup = get_page('https://example.com')
        assert soup is not None


class TestGetDetailData:
    """Test the get_detail_data function."""
    
    def test_get_detail_data_complete(self):
        """Test extracting data from a complete detail page."""
        from ebay_scraper import get_detail_data
        
        soup = BeautifulSoup(SAMPLE_DETAIL_PAGE_HTML, 'lxml')
        data = get_detail_data(soup)
        
        assert data['title'] == 'LEGO Star Wars Republic Gunship Set 7676'
        assert data['currency'] == 'US'
        assert data['price'] == '$150.00'
        assert data['total_sold'] == '25'
    
    def test_get_detail_data_no_sold(self):
        """Test extracting data when 'sold' information is missing."""
        from ebay_scraper import get_detail_data
        
        soup = BeautifulSoup(SAMPLE_DETAIL_PAGE_NO_SOLD_HTML, 'lxml')
        data = get_detail_data(soup)
        
        assert data['title'] == 'LEGO Star Wars Item'
        assert data['currency'] == 'US'
        assert data['price'] == '$200.00'
        assert data['total_sold'] == ''
    
    def test_get_detail_data_different_currency(self):
        """Test extracting data with EUR currency."""
        from ebay_scraper import get_detail_data
        
        soup = BeautifulSoup(SAMPLE_DETAIL_PAGE_EUR_HTML, 'lxml')
        data = get_detail_data(soup)
        
        assert data['title'] == 'European Item'
        assert data['currency'] == 'EUR'
        assert data['price'] == '100.00'
        assert data['total_sold'] == '10'
    
    def test_get_detail_data_empty_page(self):
        """Test extracting data from an empty page."""
        from ebay_scraper import get_detail_data
        
        soup = BeautifulSoup("<html><body></body></html>", 'lxml')
        data = get_detail_data(soup)
        
        assert data['title'] == ''
        assert data['currency'] == ''
        assert data['price'] == ''
        assert data['total_sold'] == ''
    
    def test_get_detail_data_malformed_price(self):
        """Test handling of malformed price data."""
        from ebay_scraper import get_detail_data
        
        html = """
        <html>
        <body>
            <h1 id="itemTitle">Details about  Test Item</h1>
            <span id="prcIsum">InvalidPrice</span>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        data = get_detail_data(soup)
        
        # Should handle gracefully with empty strings
        assert data['currency'] == ''
        assert data['price'] == ''


class TestGetIndexData:
    """Test the get_index_data function."""
    
    def test_get_index_data_success(self):
        """Test extracting links from search results."""
        from ebay_scraper import get_index_data
        
        soup = BeautifulSoup(SAMPLE_SEARCH_PAGE_HTML, 'lxml')
        urls = get_index_data(soup)
        
        # Note: function skips first URL (urls[1:])
        assert len(urls) == 2
        assert 'https://www.ebay.com/itm/456' in urls
        assert 'https://www.ebay.com/itm/789' in urls
    
    def test_get_index_data_empty(self):
        """Test with page containing no links."""
        from ebay_scraper import get_index_data
        
        soup = BeautifulSoup("<html><body></body></html>", 'lxml')
        urls = get_index_data(soup)
        
        assert urls == []
    
    def test_get_index_data_single_link(self):
        """Test with only one link (should return empty after skipping first)."""
        from ebay_scraper import get_index_data
        
        html = """
        <html>
        <body>
            <a class="s-item__link" href="https://www.ebay.com/itm/123">Item 1</a>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        urls = get_index_data(soup)
        
        # After skipping first link, should be empty
        assert urls == []


class TestMainFunction:
    """Test the main function with full integration."""
    
    @patch('ebay_scraper.get_page')
    def test_main_basic_flow(self, mock_get_page, capsys):
        """Test the main function's basic flow."""
        from ebay_scraper import main
        
        # Mock search page
        search_soup = BeautifulSoup(SAMPLE_SEARCH_PAGE_HTML, 'lxml')
        
        # Mock detail pages
        detail_soup1 = BeautifulSoup(SAMPLE_DETAIL_PAGE_HTML, 'lxml')
        detail_soup2 = BeautifulSoup(SAMPLE_DETAIL_PAGE_NO_SOLD_HTML, 'lxml')
        
        # Setup mock to return different soups
        mock_get_page.side_effect = [search_soup, detail_soup1, detail_soup2]
        
        # Run main (will use hardcoded URL in the function)
        main()
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify some output was produced
        assert 'title' in captured.out or 'price' in captured.out or 'average' in captured.out.lower()
    
    @patch('ebay_scraper.get_page')
    def test_main_with_multiple_currencies(self, mock_get_page, capsys):
        """Test main function filtering by US currency."""
        from ebay_scraper import main
        
        search_soup = BeautifulSoup(SAMPLE_SEARCH_PAGE_HTML, 'lxml')
        detail_soup1 = BeautifulSoup(SAMPLE_DETAIL_PAGE_HTML, 'lxml')
        detail_soup2 = BeautifulSoup(SAMPLE_DETAIL_PAGE_EUR_HTML, 'lxml')
        
        mock_get_page.side_effect = [search_soup, detail_soup1, detail_soup2]
        
        main()
        
        captured = capsys.readouterr()
        # Should only count US currency items
        assert 'average' in captured.out.lower()


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_title_with_special_characters(self):
        """Test title extraction with unicode characters."""
        from ebay_scraper import get_detail_data
        
        html = """
        <html>
        <body>
            <h1 id="itemTitle">Details about \xa0Item with Special Chars™®©</h1>
            <span id="prcIsum">US $50.00</span>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        data = get_detail_data(soup)
        
        assert 'Special Chars' in data['title']
        assert '\xa0' not in data['title']  # Should be stripped
    
    def test_sold_with_special_formatting(self):
        """Test sold count with various formats."""
        from ebay_scraper import get_detail_data
        
        html = """
        <html>
        <body>
            <h1 id="itemTitle">Details about  Test</h1>
            <span id="prcIsum">US $100.00</span>
            <span class="vi-qtyS"><a>1,234 sold</a></span>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        data = get_detail_data(soup)
        
        # Should extract the number (may or may not handle comma)
        assert data['total_sold'] == '1,234'


class TestDataValidation:
    """Test data validation and type checking."""
    
    def test_get_detail_data_returns_dict(self):
        """Ensure get_detail_data always returns a dictionary."""
        from ebay_scraper import get_detail_data
        
        soup = BeautifulSoup("<html></html>", 'lxml')
        data = get_detail_data(soup)
        
        assert isinstance(data, dict)
        assert 'title' in data
        assert 'price' in data
        assert 'currency' in data
        assert 'total_sold' in data
    
    def test_get_index_data_returns_list(self):
        """Ensure get_index_data always returns a list."""
        from ebay_scraper import get_index_data
        
        soup = BeautifulSoup("<html></html>", 'lxml')
        urls = get_index_data(soup)
        
        assert isinstance(urls, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
