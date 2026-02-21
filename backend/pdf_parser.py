"""
PDF Parser Module
Extracts text content from uploaded PDF resume files using pypdf.
"""

from pypdf import PdfReader
import io
import re


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file_bytes: Raw bytes of the PDF file.
        
    Returns:
        Extracted text content as a string.
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    raw_text = "\n".join(text_parts)
    # Clean up excessive whitespace while preserving paragraph structure
    cleaned = re.sub(r'\n{3,}', '\n\n', raw_text)
    cleaned = re.sub(r' {2,}', ' ', cleaned)
    return cleaned.strip()


def get_pdf_metadata(file_bytes: bytes) -> dict:
    """
    Extract metadata from a PDF file (page count, file size, etc.)
    
    Args:
        file_bytes: Raw bytes of the PDF file.
        
    Returns:
        Dictionary of metadata.
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    metadata = reader.metadata or {}

    return {
        "page_count": len(reader.pages),
        "file_size_kb": round(len(file_bytes) / 1024, 1),
        "author": str(metadata.get("/Author", "Unknown")),
        "creator": str(metadata.get("/Creator", "Unknown")),
    }
