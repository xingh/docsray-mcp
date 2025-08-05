"""Map tool implementation."""

import logging
from typing import Any, Dict

from ..providers.base import Document
from ..providers.registry import ProviderRegistry
from ..utils.cache import DocumentCache
from ..utils.documents import get_document_format

logger = logging.getLogger(__name__)


async def handle_map(
    document_url: str,
    include_content: bool,
    analysis_depth: str,
    provider: str,
    registry: ProviderRegistry,
    cache: DocumentCache
) -> Dict[str, Any]:
    """Handle map operation.
    
    Args:
        document_url: URL or path to document
        include_content: Whether to include content snippets
        analysis_depth: Depth of analysis (shallow, deep, comprehensive)
        provider: Provider name or "auto"
        registry: Provider registry
        cache: Document cache
        
    Returns:
        Map result dictionary
    """
    try:
        # Validate analysis depth
        valid_depths = ["shallow", "deep", "comprehensive"]
        if analysis_depth not in valid_depths:
            return {
                "error": f"Invalid analysis depth: {analysis_depth}",
                "validDepths": valid_depths
            }

        # Check cache
        cache_key = cache.generate_key(document_url, "map", {
            "include_content": include_content,
            "analysis_depth": analysis_depth,
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
            document, "map", provider
        )
        if not selected_provider:
            return {
                "error": f"No provider available for {document.format} documents",
                "suggestion": "Try installing additional providers or use a different format"
            }

        # Perform map operation
        logger.info(f"Mapping document with {selected_provider.get_name()} provider")
        result = await selected_provider.map(document, {
            "include_content": include_content,
            "analysis_depth": analysis_depth
        })

        # Format response
        response = {
            "documentMap": result.document_map,
            "provider": selected_provider.get_name()
        }

        if result.statistics:
            response["statistics"] = result.statistics

        # Cache result
        await cache.set(cache_key, response, {
            "provider": selected_provider.get_name(),
            "operation": "map"
        })

        return response

    except Exception as e:
        logger.error(f"Error in map operation: {e}")
        return {
            "error": str(e),
            "type": type(e).__name__
        }
