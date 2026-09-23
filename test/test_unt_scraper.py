import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import unt_scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unt_scraper

class TestUntScraper(unittest.TestCase):
    
    def test_clean_vmp_name_for_search(self):
        """Test that common beer styles and special characters are removed for broader searching."""
        self.assertEqual(unt_scraper.clean_vmp_name_for_search("Lervig Hazy IPA"), "lervig")
        self.assertEqual(unt_scraper.clean_vmp_name_for_search("Nøgne Ø Imperial Stout"), "nøgne ø")
        self.assertEqual(unt_scraper.clean_vmp_name_for_search("Kinn Vestkyst IPA"), "kinn vestkyst")
        # Ensure special characters are handled, "a" gets removed by style list logic
        self.assertEqual(unt_scraper.clean_vmp_name_for_search("Amundsen Dessert in a Can (Bourbon BA)"), "amundsen dessert in can")

    @patch('unt_scraper.requests.post')
    @patch('time.sleep') # Mock sleep so tests run fast
    def test_search_untappd_success(self, mock_sleep, mock_post):
        """Test that search_untappd returns hits and filters out homebrews."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{
                "hits": [
                    {"beer_name": "Good Beer", "homebrew": 0},
                    {"beer_name": "Bob's Homebrew", "homebrew": 1}
                ]
            }]
        }
        mock_post.return_value = mock_response

        # Call the function
        hits = unt_scraper.search_untappd("Test Query")
        
        # Verify the results
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["beer_name"], "Good Beer")
        mock_post.assert_called_once()
        
    @patch('unt_scraper.requests.post')
    @patch('time.sleep')
    def test_search_untappd_rate_limit(self, mock_sleep, mock_post):
        """Test that search_untappd raises an exception on rate limits (429)."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            unt_scraper.search_untappd("Test")
            
        self.assertTrue("blokkerte" in str(context.exception) or "429" in str(context.exception))

if __name__ == '__main__':
    unittest.main()
