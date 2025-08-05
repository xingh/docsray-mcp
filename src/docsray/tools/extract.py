"""Extract tool implementation."""

import logging
from typing import Any, Dict, List, Optional

from ..providers.base import Document
from ..providers.registry import ProviderRegistry
from ..utils.cache import DocumentCache
from ..utils.documents import get_document_format

logger = logging.getLogger(__name__)


async def handle_extract(
    document_url: str,
    extraction_targets: List[str],
    output_format: str,
    pages: Optional[List[int]],
    provider: str,
    registry: ProviderRegistry,
    cache: DocumentCache
) -> Dict[str, Any]:
    """Handle extract operation.
    
    Args:
        document_url: URL or path to document
        extraction_targets: Types of content to extract
        output_format: Output format (markdown, json, structured)
        pages: Specific pages to extract
        provider: Provider name or "auto"
        registry: Provider registry
        cache: Document cache
        
    Returns:
        Extract result dictionary
    """
    try:
        # Validate extraction targets
        valid_targets = ["text", "tables", "images", "forms", "metadata", "equations", "layout"]
        invalid_targets = [t for t in extraction_targets if t not in valid_targets]
        if invalid_targets:
            return {
                "error": f"Invalid extraction targets: {invalid_targets}",
                "validTargets": valid_targets
            }

        # Check cache
        cache_key = cache.generate_key(document_url, "extract", {
            "extraction_targets": sorted(extraction_targets),
            "output_format": output_format,
            "pages": sorted(pages) if pages else None,
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
            document, "extract", provider
        )
        if not selected_provider:
            return {
                "error": f"No provider available for {document.format} documents",
                "suggestion": "Try installing additional providers or use a different format"
            }

        # Check provider capabilities
        capabilities = selected_provider.get_capabilities()
        unsupported = []

        if "tables" in extraction_targets and not capabilities.features.get("tables"):
            unsupported.append("tables")
        if "images" in extraction_targets and not capabilities.features.get("images"):
            unsupported.append("images")
        if "forms" in extraction_targets and not capabilities.features.get("forms"):
            unsupported.append("forms")

        if unsupported:
            logger.warning(
                f"Provider {selected_provider.get_name()} does not support: {unsupported}"
            )

        # Perform extraction
        logger.info(f"Extracting from document with {selected_provider.get_name()} provider")
        result = await selected_provider.extract(document, {
            "extraction_targets": extraction_targets,
            "output_format": output_format,
            "pages": pages
        })

        # Format response
        response = {
            "content": result.content,
            "format": result.format,
            "provider": selected_provider.get_name()
        }

        if result.pages_processed:
            response["pagesProcessed"] = result.pages_processed

        if result.statistics:
            response["statistics"] = result.statistics

        if unsupported:
            response["warnings"] = [
                f"The following targets are not supported by {selected_provider.get_name()}: "
                f"{', '.join(unsupported)}"
            ]

        # Cache result
        await cache.set(cache_key, response, {
            "provider": selected_provider.get_name(),
            "operation": "extract"
        })

        return response

    except Exception as e:
        logger.error(f"Error in extract operation: {e}")
        return {
            "error": str(e),
            "type": type(e).__name__
        }
