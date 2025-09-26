"""Fetch tool implementation for unified document retrieval."""

import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import aiofiles
import httpx

from ..providers.base import Document
from ..providers.registry import ProviderRegistry
from ..utils.cache import DocumentCache
from ..utils.documents import (
    calculate_file_hash,
    get_document_format,
    is_url,
    resolve_path
)

logger = logging.getLogger(__name__)

# Default cache directory
DEFAULT_CACHE_DIR = Path.home() / ".docsray"


async def handle_fetch(
    source: str,
    registry: ProviderRegistry,
    cache: DocumentCache,
    fetch_options: Optional[Dict[str, Any]] = None,
    cache_strategy: str = "use-cache",
    return_format: str = "raw",
    provider: str = "auto"
) -> Dict[str, Any]:
    """Handle fetch operation for unified document retrieval.

    Args:
        source: URL (https://) or filesystem path to fetch
        fetch_options: Optional HTTP headers, timeout, followRedirects settings
        cache_strategy: Caching strategy (use-cache, bypass-cache, refresh-cache)
        return_format: Format of returned document (raw, processed, metadata-only)
        provider: Provider selection
        registry: Provider registry
        cache: Document cache

    Returns:
        Fetch result dictionary
    """
    try:
        # Validate cache strategy
        valid_strategies = ["use-cache", "bypass-cache", "refresh-cache"]
        if cache_strategy not in valid_strategies:
            return {
                "error": f"Invalid cache strategy: {cache_strategy}",
                "validStrategies": valid_strategies
            }

        # Validate return format
        valid_formats = ["raw", "processed", "metadata-only"]
        if return_format not in valid_formats:
            return {
                "error": f"Invalid return format: {return_format}",
                "validFormats": valid_formats
            }

        # Parse fetch options
        fetch_options = fetch_options or {}
        headers = fetch_options.get("headers", {})
        timeout = fetch_options.get("timeout", 30000)  # milliseconds
        follow_redirects = fetch_options.get("followRedirects", True)

        # Convert timeout to seconds
        timeout_seconds = timeout / 1000 if timeout else 30

        # Check cache unless bypassing or refreshing
        cache_key = cache.generate_key(source, "fetch", {
            "cache_strategy": cache_strategy,
            "return_format": return_format,
            "provider": provider,
            "fetch_options": fetch_options
        })

        if cache_strategy == "use-cache":
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached result for: {source}")
                cached_result["fromCache"] = True
                return cached_result

        # Determine source type and get document
        if is_url(source):
            result = await _fetch_from_url(
                source, headers, timeout_seconds, follow_redirects, return_format, provider, registry
            )
        else:
            result = await _fetch_from_filesystem(
                source, return_format, provider, registry
            )

        # Add metadata
        result["source"] = source
        result["cacheStrategy"] = cache_strategy
        result["returnFormat"] = return_format
        result["fromCache"] = False

        # Cache result unless bypassing cache
        if cache_strategy != "bypass-cache":
            await cache.set(cache_key, result, {
                "provider": result.get("provider"),
                "operation": "fetch",
                "source_type": "url" if is_url(source) else "filesystem"
            })

        return result

    except Exception as e:
        logger.error(f"Error in fetch operation: {e}")
        return {
            "error": str(e),
            "type": type(e).__name__,
            "source": source
        }


async def _fetch_from_url(
    url: str,
    headers: Dict[str, str],
    timeout_seconds: float,
    follow_redirects: bool,
    return_format: str,
    provider: str,
    registry: ProviderRegistry
) -> Dict[str, Any]:
    """Fetch document from web URL.

    Args:
        url: Document URL
        headers: HTTP headers
        timeout_seconds: Request timeout in seconds
        follow_redirects: Whether to follow redirects
        return_format: Return format
        provider: Provider selection
        registry: Provider registry

    Returns:
        Fetch result dictionary
    """
    logger.info(f"Fetching document from URL: {url}")

    # Ensure cache directory exists
    cache_dir = DEFAULT_CACHE_DIR / "downloads"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Determine file extension
    doc_format = get_document_format(url)
    suffix = f".{doc_format}" if doc_format else ""

    # Create cache file path based on URL hash
    url_hash = calculate_file_hash_from_string(url)
    cached_file = cache_dir / f"{url_hash}{suffix}"

    file_size = 0
    content_type = None
    local_path = None

    try:
        # Configure HTTP client
        client_kwargs = {
            "timeout": timeout_seconds,
            "follow_redirects": follow_redirects
        }

        if headers:
            client_kwargs["headers"] = headers

        async with httpx.AsyncClient(**client_kwargs) as client:
            # First make a HEAD request to get metadata
            try:
                head_response = await client.head(url)
                head_response.raise_for_status()
                file_size = int(head_response.headers.get("content-length", 0))
                content_type = head_response.headers.get("content-type", "")
                logger.info(f"Document metadata - Size: {file_size} bytes, Type: {content_type}")
            except Exception as head_error:
                logger.warning(f"Failed to get HEAD response, proceeding with GET: {head_error}")

            # Download the file with progress tracking
            async with client.stream("GET", url) as response:
                response.raise_for_status()

                # Update metadata from response if HEAD failed
                if not file_size:
                    file_size = int(response.headers.get("content-length", 0))
                if not content_type:
                    content_type = response.headers.get("content-type", "")

                # Write to cache file with progress reporting
                bytes_downloaded = 0
                async with aiofiles.open(cached_file, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        await f.write(chunk)
                        bytes_downloaded += len(chunk)

                        # Log progress for large files (> 1MB)
                        if file_size > 1024 * 1024 and bytes_downloaded % (1024 * 1024) == 0:
                            progress_pct = (bytes_downloaded / file_size * 100) if file_size else 0
                            logger.info(f"Download progress: {progress_pct:.1f}% ({bytes_downloaded} bytes)")

                local_path = cached_file
                logger.info(f"Downloaded document to: {cached_file}")

    except httpx.HTTPError as e:
        logger.error(f"HTTP error downloading {url}: {e}")
        return {
            "error": f"Failed to download document: {str(e)}",
            "type": "HTTPError",
            "url": url,
            "suggestion": "Check URL validity and network connection"
        }
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return {
            "error": f"Download failed: {str(e)}",
            "type": type(e).__name__,
            "url": url
        }

    # Build result based on return format
    result = {
        "url": url,
        "localPath": str(local_path),
        "fileSize": file_size,
        "contentType": content_type,
        "format": doc_format,
        "downloadComplete": True
    }

    if return_format == "metadata-only":
        return result

    # For raw format, include file hash
    if return_format == "raw":
        if local_path and local_path.exists():
            result["fileHash"] = calculate_file_hash(local_path)
        return result

    # For processed format, use provider to process the document
    if return_format == "processed" and local_path:
        try:
            document = Document(
                url=str(local_path),
                format=doc_format or "pdf"
            )

            # Select provider for processing
            selected_provider = await registry.select_provider(
                document, "extract", provider
            )

            if selected_provider:
                extract_result = await selected_provider.extract(document, {
                    "extraction_targets": ["text"],
                    "output_format": "markdown"
                })

                result["processedContent"] = extract_result.content
                result["provider"] = selected_provider.get_name()
            else:
                result["warning"] = "No provider available for processing"

        except Exception as e:
            logger.warning(f"Failed to process document: {e}")
            result["warning"] = f"Processing failed: {str(e)}"

    return result


async def _fetch_from_filesystem(
    path: str,
    return_format: str,
    provider: str,
    registry: ProviderRegistry
) -> Dict[str, Any]:
    """Fetch document from filesystem path.

    Args:
        path: Filesystem path
        return_format: Return format
        provider: Provider selection
        registry: Provider registry

    Returns:
        Fetch result dictionary
    """
    logger.info(f"Fetching document from filesystem: {path}")

    try:
        # Resolve the path
        resolved_path = resolve_path(path)
        doc_format = get_document_format(str(resolved_path))
        file_size = resolved_path.stat().st_size

        # Build result
        result = {
            "path": path,
            "resolvedPath": str(resolved_path),
            "fileSize": file_size,
            "format": doc_format,
            "exists": True
        }

        if return_format == "metadata-only":
            return result

        # For raw format, include file hash
        if return_format == "raw":
            result["fileHash"] = calculate_file_hash(resolved_path)
            return result

        # For processed format, use provider to process the document
        if return_format == "processed":
            try:
                document = Document(
                    url=str(resolved_path),
                    format=doc_format or "pdf"
                )

                # Select provider for processing
                selected_provider = await registry.select_provider(
                    document, "extract", provider
                )

                if selected_provider:
                    extract_result = await selected_provider.extract(document, {
                        "extraction_targets": ["text"],
                        "output_format": "markdown"
                    })

                    result["processedContent"] = extract_result.content
                    result["provider"] = selected_provider.get_name()
                else:
                    result["warning"] = "No provider available for processing"

            except Exception as e:
                logger.warning(f"Failed to process document: {e}")
                result["warning"] = f"Processing failed: {str(e)}"

        return result

    except FileNotFoundError:
        return {
            "error": f"File not found: {path}",
            "type": "FileNotFoundError",
            "path": path,
            "suggestion": "Check that the file path exists and is accessible"
        }
    except PermissionError:
        return {
            "error": f"Permission denied accessing: {path}",
            "type": "PermissionError",
            "path": path,
            "suggestion": "Check file permissions"
        }
    except Exception as e:
        return {
            "error": f"Failed to access file: {str(e)}",
            "type": type(e).__name__,
            "path": path
        }


def calculate_file_hash_from_string(content: str, algorithm: str = "sha256") -> str:
    """Calculate hash of a string.

    Args:
        content: String content to hash
        algorithm: Hash algorithm to use

    Returns:
        Hex digest of string hash
    """
    import hashlib
    hasher = hashlib.new(algorithm)
    hasher.update(content.encode('utf-8'))
    return hasher.hexdigest()