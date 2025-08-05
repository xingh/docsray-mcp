"""Seek tool implementation."""

import logging
from typing import Any, Dict

from ..providers.base import Document
from ..providers.registry import ProviderRegistry
from ..utils.cache import DocumentCache
from ..utils.documents import get_document_format

logger = logging.getLogger(__name__)


async def handle_seek(
    document_url: str,
    target: Dict[str, Any],
    extract_content: bool,
    provider: str,
    registry: ProviderRegistry,
    cache: DocumentCache
) -> Dict[str, Any]:
    """Handle seek operation.
    
    Args:
        document_url: URL or path to document
        target: Navigation target (page, section, or query)
        extract_content: Whether to extract content
        provider: Provider name or "auto"
        registry: Provider registry
        cache: Document cache
        
    Returns:
        Seek result dictionary
    """
    try:
        # Check cache
        cache_key = cache.generate_key(document_url, "seek", {
            "target": target,
            "extract_content": extract_content,
            "provider": provider
        })
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result

        # Create document object
        document = Document(
            url=document_url,
            format=get_document_format(document_url)
        )

        # Select provider
        selected_provider = await registry.select_provider(
            document, "seek", provider
        )
        if not selected_provider:
            return {
                "error": f"No provider available for {document.format} documents",
                "suggestion": "Try installing additional providers or use a different format"
            }

        # Perform seek operation
        logger.info(f"Seeking in document with {selected_provider.get_name()} provider")
        result = await selected_provider.seek(document, target)

        # Format response
        response = {
            "location": result.location,
            "provider": selected_provider.get_name()
        }

        if extract_content and result.content:
            response["content"] = result.content

        if result.context:
            response["context"] = result.context

        # Cache result
        await cache.set(cache_key, response, {
            "provider": selected_provider.get_name(),
            "operation": "seek"
        })

        return response

    except Exception as e:
        logger.error(f"Error in seek operation: {e}")
        return {
            "error": str(e),
            "type": type(e).__name__
        }
