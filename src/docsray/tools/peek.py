"""Peek tool implementation."""

import logging
from typing import Any, Dict

from ..providers.base import Document
from ..providers.registry import ProviderRegistry
from ..utils.cache import DocumentCache
from ..utils.documents import get_document_format

logger = logging.getLogger(__name__)


async def handle_peek(
    document_url: str,
    depth: str,
    provider: str,
    registry: ProviderRegistry,
    cache: DocumentCache
) -> Dict[str, Any]:
    """Handle peek operation.
    
    Args:
        document_url: URL or path to document
        depth: Level of detail (metadata, structure, preview)
        provider: Provider name or "auto"
        registry: Provider registry
        cache: Document cache
        
    Returns:
        Peek result dictionary
    """
    try:
        # Validate depth
        valid_depths = ["metadata", "structure", "preview"]
        if depth not in valid_depths:
            return {
                "error": f"Invalid depth: {depth}",
                "validDepths": valid_depths
            }

        # Check cache
        cache_key = cache.generate_key(document_url, "peek", {
            "depth": depth,
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
            document, "peek", provider
        )
        if not selected_provider:
            return {
                "error": f"No provider available for {document.format} documents",
                "suggestion": "Try installing additional providers or use a different format"
            }

        # Perform peek operation
        logger.info(f"Peeking at document with {selected_provider.get_name()} provider")
        result = await selected_provider.peek(document, {"depth": depth})

        # Format response
        response = {
            "metadata": result.metadata,
            "provider": selected_provider.get_name()
        }

        if result.structure and depth in ["structure", "preview"]:
            response["structure"] = result.structure

        if result.preview and depth == "preview":
            response["preview"] = result.preview

        # Cache result
        await cache.set(cache_key, response, {
            "provider": selected_provider.get_name(),
            "operation": "peek"
        })

        return response

    except Exception as e:
        logger.error(f"Error in peek operation: {e}")
        return {
            "error": str(e),
            "type": type(e).__name__
        }
