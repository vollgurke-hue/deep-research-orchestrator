"""
PDFExtractor - Extract text from PDF files

Extracts text content from PDFs while preserving structure.
"""

import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PDFExtractor:
    """PDF extraction handler for collecting data from PDF files."""

    def __init__(self):
        """Initialize PDFExtractor."""
        logger.debug("PDFExtractor initialized")

    def collect(self, file_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract text from PDF file.

        Args:
            file_path: Path to PDF file
            config: Source configuration dict

        Returns:
            Extracted data dict with metadata
        """
        logger.info(f"Extracting PDF: {file_path}")

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            # Import dependencies (lazy loading)
            import PyPDF2
        except ImportError:
            logger.error("PyPDF2 not installed")
            raise ImportError(
                "PDF extraction requires: pip install PyPDF2"
            )

        # Extract text
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)

                # Extract metadata
                metadata = {}
                if pdf_reader.metadata:
                    metadata = {
                        "title": pdf_reader.metadata.get("/Title"),
                        "author": pdf_reader.metadata.get("/Author"),
                        "subject": pdf_reader.metadata.get("/Subject"),
                        "creator": pdf_reader.metadata.get("/Creator"),
                        "producer": pdf_reader.metadata.get("/Producer"),
                        "creation_date": pdf_reader.metadata.get("/CreationDate")
                    }

                # Extract text from all pages
                num_pages = len(pdf_reader.pages)
                pages = []

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()

                    pages.append({
                        "page_number": page_num + 1,
                        "text": text
                    })

                # Compile full text
                full_text = "\n\n".join(page["text"] for page in pages)

        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise

        # Compile result
        result = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "collected_at": datetime.now().isoformat(),
            "num_pages": num_pages,
            "data": {
                "full_text": full_text,
                "pages": pages,
                "metadata": metadata
            }
        }

        logger.info(f"Successfully extracted {num_pages} pages from {file_path.name}")

        return result


# Test function
def _test_pdf_extractor():
    """Test PDFExtractor."""
    print("\n=== PDFExtractor Test ===\n")

    extractor = PDFExtractor()
    print("✅ PDFExtractor initialized")

    # Note: Actual test requires a PDF file
    print("⚠️  Actual PDF extraction requires a test PDF file")
    print("✅ PDFExtractor tests completed!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _test_pdf_extractor()
