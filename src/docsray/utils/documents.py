"""Document handling utilities."""

import hashlib
import logging
import mimetypes
import os
import tempfile
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

import aiofiles
import httpx

logger = logging.getLogger(__name__)

# Document format mappings
FORMAT_EXTENSIONS = {
    ".pdf": "pdf",
    ".xps": "xps",
    ".epub": "epub",
    ".cbz": "cbz",
    ".svg": "svg",
    ".png": "png",
    ".jpg": "jpg",
    ".jpeg": "jpg",
    ".docx": "docx",
    ".pptx": "pptx",
    ".txt": "txt",
}

MIME_TO_FORMAT = {
    "application/pdf": "pdf",
    "application/vnd.ms-xpsdocument": "xps",
    "application/epub+zip": "epub",
    "application/x-cbz": "cbz",
    "image/svg+xml": "svg",
    "image/png": "png",
    "image/jpeg": "jpg",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "text/plain": "txt",
}


def get_document_format(url_or_path: str) -> Optional[str]:
    """Determine document format from URL or path.
    
    Args:
        url_or_path: Document URL or file path
        
    Returns:
        Document format string or None
    """
    # Try extension first
    path = Path(urlparse(url_or_path).path)
    ext = path.suffix.lower()
    if ext in FORMAT_EXTENSIONS:
        return FORMAT_EXTENSIONS[ext]

    # Try MIME type
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type and mime_type in MIME_TO_FORMAT:
        return MIME_TO_FORMAT[mime_type]

    return None


async def download_document(url: str, timeout: int = 30) -> Path:
    """Download document from URL to temporary file.
    
    Args:
        url: Document URL
        timeout: Download timeout in seconds
        
    Returns:
        Path to downloaded file
        
    Raises:
        httpx.HTTPError: On download failure
    """
    logger.info(f"Downloading document from: {url}")

    # Determine file extension
    doc_format = get_document_format(url)
    suffix = f".{doc_format}" if doc_format else ""

    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
        prefix="docsray_"
    )
    temp_path = Path(temp_file.name)
    temp_file.close()

    try:
        # Download with streaming
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()

                # Write to file
                async with aiofiles.open(temp_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        await f.write(chunk)

        logger.info(f"Downloaded document to: {temp_path}")
        return temp_path

    except Exception:
        # Clean up on failure
        if temp_path.exists():
            temp_path.unlink()
        raise


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """Calculate hash of a file.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm to use
        
    Returns:
        Hex digest of file hash
    """
    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()


def is_url(path_or_url: str) -> bool:
    """Check if string is a URL.
    
    Args:
        path_or_url: Path or URL string
        
    Returns:
        True if URL, False otherwise
    """
    try:
        result = urlparse(path_or_url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def resolve_path(path_or_url: str) -> Path:
    """Resolve a file path (relative or absolute) to an absolute Path object.
    
    Args:
        path_or_url: File path (relative or absolute)
        
    Returns:
        Absolute Path object
        
    Raises:
        FileNotFoundError: If the resolved path doesn't exist
    """
    # Expand user home directory if present
    expanded = os.path.expanduser(path_or_url)
    
    # Convert to Path and resolve to absolute
    path = Path(expanded).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    return path


async def get_local_document(path_or_url: str) -> Optional[Path]:
    """Get local document path from URL or file path.
    
    Args:
        path_or_url: Document URL or local file path
        
    Returns:
        Path to local document file, or None if it's a URL
    """
    if is_url(path_or_url):
        return None
    
    try:
        return resolve_path(path_or_url)
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error accessing local file: {e}")
        raise
