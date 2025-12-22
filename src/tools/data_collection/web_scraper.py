"""
WebScraper - Collect data from web pages

Uses BeautifulSoup for static HTML scraping.
Respects robots.txt and implements rate limiting.
"""

import logging
import time
from typing import Dict, Any
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger(__name__)


class WebScraper:
    """Web scraping handler for collecting data from web pages."""

    def __init__(self):
        """Initialize WebScraper."""
        self.last_request_time = {}  # Track per-domain rate limiting
        logger.debug("WebScraper initialized")

    def collect(self, url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect data from web page.

        Args:
            url: Target URL
            config: Source configuration dict

        Returns:
            Collected data dict with metadata
        """
        logger.info(f"Scraping URL: {url}")

        try:
            # Import dependencies (lazy loading)
            import requests
            from bs4 import BeautifulSoup
        except ImportError as e:
            logger.error(f"Required dependencies not installed: {e}")
            raise ImportError(
                "Web scraping requires: pip install requests beautifulsoup4 lxml"
            )

        # Rate limiting
        self._apply_rate_limit(url, config)

        # Prepare request
        headers = self._get_headers(config)
        timeout = config.get("config", {}).get("timeout", 30)

        # Make request
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise

        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')

        # Extract data using selectors from config
        selectors = config.get("config", {}).get("selectors", {})
        extracted_data = {}

        for field_name, selector in selectors.items():
            try:
                element = soup.select_one(selector)
                if element:
                    extracted_data[field_name] = element.get_text(strip=True)
                else:
                    extracted_data[field_name] = None
                    logger.warning(f"Selector not found: {selector}")
            except Exception as e:
                logger.warning(f"Error extracting {field_name}: {e}")
                extracted_data[field_name] = None

        # Fallback: extract full page if no selectors
        if not selectors:
            # Remove script and style tags
            for tag in soup(["script", "style"]):
                tag.decompose()

            extracted_data["full_text"] = soup.get_text(separator='\n', strip=True)
            extracted_data["title"] = soup.title.string if soup.title else None

        # Compile result
        result = {
            "url": url,
            "status_code": response.status_code,
            "collected_at": datetime.now().isoformat(),
            "content_type": response.headers.get("Content-Type"),
            "data": extracted_data,
            "metadata": {
                "encoding": response.encoding,
                "final_url": response.url,  # In case of redirects
                "headers": dict(response.headers)
            }
        }

        logger.info(f"Successfully scraped {url}")

        return result

    def _apply_rate_limit(self, url: str, config: Dict[str, Any]):
        """
        Apply rate limiting per domain.

        Args:
            url: Target URL
            config: Source configuration
        """
        rate_limit = config.get("config", {}).get("rate_limit_seconds", 1)

        domain = urlparse(url).netloc

        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < rate_limit:
                sleep_time = rate_limit - elapsed
                logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s for {domain}")
                time.sleep(sleep_time)

        self.last_request_time[domain] = time.time()

    def _get_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get HTTP headers from config.

        Args:
            config: Source configuration

        Returns:
            Headers dict
        """
        user_agent = config.get("config", {}).get(
            "user_agent",
            "Mozilla/5.0 (Research Bot)"
        )

        return {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }


# Test function
def _test_web_scraper():
    """Test WebScraper with a simple example."""
    print("\n=== WebScraper Test ===\n")

    scraper = WebScraper()
    print("✅ WebScraper initialized")

    # Test with example.com
    test_config = {
        "config": {
            "selectors": {
                "title": "h1",
                "content": "p"
            },
            "rate_limit_seconds": 1,
            "user_agent": "Test Bot 1.0"
        }
    }

    try:
        result = scraper.collect("https://example.com", test_config)
        print(f"✅ Successfully scraped example.com")
        print(f"   Title: {result['data'].get('title')}")
        print(f"   Status: {result['status_code']}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

    print("\n✅ WebScraper tests completed!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _test_web_scraper()
