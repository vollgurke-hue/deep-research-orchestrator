"""
TextCleaner - Clean and normalize text data

Removes HTML tags, fixes encoding, normalizes whitespace, deduplicates.
"""

import re
import logging
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)


class TextCleaner:
    """Text cleaning processor."""

    def __init__(self):
        """Initialize TextCleaner."""
        logger.debug("TextCleaner initialized")

    def process(self, data: Union[Dict[str, Any], str]) -> Union[Dict[str, Any], str]:
        """
        Clean text data.

        Args:
            data: Input data (dict or string)

        Returns:
            Cleaned data
        """
        logger.info("Cleaning text data...")

        # Handle dict input
        if isinstance(data, dict):
            if "data" in data and "full_text" in data["data"]:
                text = data["data"]["full_text"]
                cleaned_text = self._clean_text(text)
                data["data"]["full_text"] = cleaned_text
                return data
            else:
                # Try to clean all string values recursively
                return self._clean_dict(data)

        # Handle string input
        elif isinstance(data, str):
            return self._clean_text(data)

        else:
            logger.warning(f"Unexpected data type: {type(data)}")
            return data

    def _clean_text(self, text: str) -> str:
        """
        Clean individual text string.

        Args:
            text: Input text

        Returns:
            Cleaned text
        """
        # Remove HTML tags
        text = self._remove_html_tags(text)

        # Normalize whitespace
        text = self._normalize_whitespace(text)

        # Remove excessive newlines
        text = self._normalize_newlines(text)

        # Fix common encoding issues
        text = self._fix_encoding_issues(text)

        return text.strip()

    def _clean_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively clean all strings in dict.

        Args:
            data: Input dict

        Returns:
            Cleaned dict
        """
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = self._clean_text(value)
            elif isinstance(value, dict):
                cleaned[key] = self._clean_dict(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    self._clean_text(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                cleaned[key] = value

        return cleaned

    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from text."""
        # Remove script and style content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML comments
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

        # Remove all HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Decode HTML entities
        try:
            import html
            text = html.unescape(text)
        except ImportError:
            pass

        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace (spaces, tabs)."""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)

        # Replace tabs with single space
        text = re.sub(r'\t+', ' ', text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text

    def _normalize_newlines(self, text: str) -> str:
        """Normalize newlines."""
        # Replace multiple newlines with max 2 newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text

    def _fix_encoding_issues(self, text: str) -> str:
        """Fix common encoding issues."""
        # Replace common problematic characters
        replacements = {
            '\u00a0': ' ',  # Non-breaking space
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2026': '...',# Ellipsis
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text


# Test function
def _test_text_cleaner():
    """Test TextCleaner."""
    print("\n=== TextCleaner Test ===\n")

    cleaner = TextCleaner()
    print("✅ TextCleaner initialized")

    # Test HTML removal
    test_html = """
    <html>
        <head><title>Test</title></head>
        <body>
            <h1>Hello   World</h1>
            <p>This is a    test.</p>
            <script>alert('remove me');</script>
        </body>
    </html>
    """

    cleaned = cleaner.process(test_html)
    print(f"✅ Cleaned HTML:")
    print(f"   {cleaned[:100]}...")

    # Test dict cleaning
    test_dict = {
        "data": {
            "full_text": "<p>Hello   World</p>\n\n\n\n<p>Test</p>"
        }
    }

    cleaned_dict = cleaner.process(test_dict)
    print(f"\n✅ Cleaned dict:")
    print(f"   {cleaned_dict['data']['full_text']}")

    print("\n✅ TextCleaner tests completed!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _test_text_cleaner()
