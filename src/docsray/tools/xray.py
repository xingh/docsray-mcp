"""Xray tool implementation."""

import logging
from typing import Any, Dict, List, Optional

from ..providers.base import Document
from ..providers.registry import ProviderRegistry
from ..utils.cache import DocumentCache
from ..utils.documents import get_document_format

logger = logging.getLogger(__name__)


async def handle_xray(
    document_url: str,
    analysis_type: List[str],
    custom_instructions: Optional[str],
    provider: str,
    registry: ProviderRegistry,
    cache: DocumentCache
) -> Dict[str, Any]:
    """Handle xray operation.
    
    Args:
        document_url: URL or path to document
        analysis_type: Types of analysis to perform
        custom_instructions: Custom analysis instructions
        provider: Provider name
        registry: Provider registry
        cache: Document cache
        
    Returns:
        Xray result dictionary
    """
    try:
        # Validate analysis types
        valid_types = ["entities", "relationships", "key-points", "sentiment", "structure"]
        invalid_types = [t for t in analysis_type if t not in valid_types]
        if invalid_types:
            return {
                "error": f"Invalid analysis types: {invalid_types}",
                "validTypes": valid_types
            }

        # Check cache
        cache_key = cache.generate_key(document_url, "xray", {
            "analysis_type": sorted(analysis_type),
            "custom_instructions": custom_instructions,
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

        # Select provider - xray requires AI-capable providers
        if provider == "auto":
            # Default to llama-parse for xray
            provider = "llama-parse"

        selected_provider = await registry.select_provider(
            document, "xray", provider
        )
        if not selected_provider:
            return {
                "error": "No AI-capable provider available for xray analysis",
                "suggestion": "Enable mistral-ocr or llama-parse providers with API keys"
            }

        # Check if provider supports xray
        capabilities = selected_provider.get_capabilities()
        if not capabilities.features.get("customInstructions", False):
            return {
                "error": f"Provider {selected_provider.get_name()} does not support AI analysis",
                "suggestion": "Use mistral-ocr or llama-parse providers for xray functionality"
            }

        # Perform xray operation
        logger.info(f"Analyzing document with {selected_provider.get_name()} provider")
        result = await selected_provider.xray(document, {
            "analysis_type": analysis_type,
            "custom_instructions": custom_instructions
        })

        # Format response
        response = {
            "analysis": result.analysis,
            "provider": selected_provider.get_name()
        }

        if result.confidence is not None:
            response["confidence"] = result.confidence

        if result.provider_info:
            response["providerInfo"] = result.provider_info

        # Cache result
        await cache.set(cache_key, response, {
            "provider": selected_provider.get_name(),
            "operation": "xray"
        })

        return response

    except Exception as e:
        logger.error(f"Error in xray operation: {e}")
        return {
            "error": str(e),
            "type": type(e).__name__
        }
