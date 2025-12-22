"""
Registered Tools using @tool decorator.

This module provides tool wrappers for the tool registry.
Import this module to auto-register all tools.
"""
from typing import Dict, Any, List
from pathlib import Path

from src.core.tool_decorator import tool
from src.tools.data_collection.web_scraper import WebScraper
from src.tools.data_collection.pdf_extractor import PDFExtractor
from src.tools.data_collection.text_cleaner import TextCleaner


# Initialize tool instances (lazy loaded)
_web_scraper = None
_pdf_extractor = None
_text_cleaner = None


def _get_web_scraper():
    global _web_scraper
    if _web_scraper is None:
        _web_scraper = WebScraper()
    return _web_scraper


def _get_pdf_extractor():
    global _pdf_extractor
    if _pdf_extractor is None:
        _pdf_extractor = PDFExtractor()
    return _pdf_extractor


def _get_text_cleaner():
    global _text_cleaner
    if _text_cleaner is None:
        _text_cleaner = TextCleaner()
    return _text_cleaner


@tool(
    name="web_scraper",
    description="Scrape data from web pages. Supports CSS selectors for targeted extraction. Implements rate limiting and respects robots.txt.",
    examples=[
        "web_scraper(url='https://example.com', selectors={'title': 'h1', 'content': 'p'})",
        "web_scraper(url='https://news.site.com/article', selectors={})"
    ]
)
def web_scraper(
    url: str,
    selectors: Dict[str, str] = None,
    rate_limit_seconds: float = 1.0,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Scrape data from a web page.

    Args:
        url: Target URL to scrape
        selectors: CSS selectors for data extraction (field_name -> selector)
        rate_limit_seconds: Minimum seconds between requests to same domain
        timeout: Request timeout in seconds

    Returns:
        Dict with scraped data, status code, and metadata
    """
    scraper = _get_web_scraper()

    config = {
        "config": {
            "selectors": selectors or {},
            "rate_limit_seconds": rate_limit_seconds,
            "timeout": timeout
        }
    }

    return scraper.collect(url, config)


@tool(
    name="pdf_extractor",
    description="Extract text content from PDF files. Supports both local files and URLs.",
    examples=[
        "pdf_extractor(file_path='/path/to/document.pdf')",
        "pdf_extractor(file_path='research_paper.pdf', max_pages=10)"
    ]
)
def pdf_extractor(
    file_path: str,
    max_pages: int = None
) -> Dict[str, Any]:
    """
    Extract text from a PDF file.

    Args:
        file_path: Path to PDF file or URL
        max_pages: Maximum number of pages to extract (None = all)

    Returns:
        Dict with extracted text, page count, and metadata
    """
    extractor = _get_pdf_extractor()

    config = {
        "config": {
            "max_pages": max_pages
        }
    }

    return extractor.extract(file_path, config)


@tool(
    name="text_cleaner",
    description="Clean and normalize text data. Removes extra whitespace, special characters, and optionally applies stemming/lemmatization.",
    examples=[
        "text_cleaner(text='  Raw    text with   spaces  ', remove_special_chars=True)",
        "text_cleaner(text='Text to clean', lowercase=True, remove_urls=True)"
    ]
)
def text_cleaner(
    text: str,
    lowercase: bool = False,
    remove_urls: bool = False,
    remove_special_chars: bool = False,
    remove_extra_whitespace: bool = True
) -> str:
    """
    Clean and normalize text.

    Args:
        text: Text to clean
        lowercase: Convert to lowercase
        remove_urls: Remove URLs
        remove_special_chars: Remove special characters
        remove_extra_whitespace: Normalize whitespace

    Returns:
        Cleaned text string
    """
    cleaner = _get_text_cleaner()

    config = {
        "lowercase": lowercase,
        "remove_urls": remove_urls,
        "remove_special_chars": remove_special_chars,
        "remove_extra_whitespace": remove_extra_whitespace
    }

    return cleaner.clean(text, config)


# Research-specific tools

@tool(
    name="search_local_docs",
    description="Search through local documentation and research files using keyword matching.",
    examples=[
        "search_local_docs(query='machine learning', path='/docs')",
        "search_local_docs(query='API documentation', path='/project/docs', max_results=5)"
    ]
)
def search_local_docs(
    query: str,
    path: str = "./docs",
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Search local documentation files.

    Args:
        query: Search query
        path: Path to search in
        max_results: Maximum number of results

    Returns:
        List of matching documents with excerpts
    """
    # TODO: Implement local document search
    # For now, return placeholder
    return [{
        "file": "example.md",
        "excerpt": f"Placeholder result for query: {query}",
        "relevance": 0.5
    }]


@tool(
    name="calculate_statistics",
    description="Calculate basic statistics (mean, median, std dev) from numerical data.",
    examples=[
        "calculate_statistics(numbers=[1, 2, 3, 4, 5])",
        "calculate_statistics(numbers=[10, 20, 30, 40])"
    ]
)
def calculate_statistics(numbers: List[float]) -> Dict[str, float]:
    """
    Calculate statistics from numbers.

    Args:
        numbers: List of numbers

    Returns:
        Dict with mean, median, std_dev, min, max
    """
    import statistics

    if not numbers:
        return {"error": "Empty input"}

    return {
        "mean": statistics.mean(numbers),
        "median": statistics.median(numbers),
        "std_dev": statistics.stdev(numbers) if len(numbers) > 1 else 0,
        "min": min(numbers),
        "max": max(numbers),
        "count": len(numbers)
    }


# Auto-import triggers registration
__all__ = [
    "web_scraper",
    "pdf_extractor",
    "text_cleaner",
    "search_local_docs",
    "calculate_statistics"
]
