#!/usr/bin/env python3
"""Test script to verify provider functionality."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Set up environment variables first
os.environ["DOCSRAY_PYMUPDF4LLM_ENABLED"] = "true"
os.environ["DOCSRAY_LLAMAPARSE_ENABLED"] = "false"  # Disable for now

from src.docsray.config import DocsrayConfig
from src.docsray.server import DocsrayServer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_providers():
    """Test provider functionality."""
    try:
        # Load configuration
        config = DocsrayConfig.from_env()
        
        logger.info(f"PyMuPDF4LLM enabled: {config.providers.pymupdf4llm.enabled}")
        logger.info(f"LlamaParse enabled: {config.providers.llama_parse.enabled}")
        
        # Initialize server
        server = DocsrayServer(config)
        
        # Check available providers
        providers = server.registry.list_providers()
        logger.info(f"Available providers: {providers}")
        
        # Test document path
        test_doc = Path("/workspace/docsray-mcp/tests/files/sample_lease.pdf")
        if not test_doc.exists():
            logger.error(f"Test document not found: {test_doc}")
            return
        
        logger.info(f"Testing with document: {test_doc}")
        
        # Test peek with PyMuPDF4LLM (should work)
        logger.info("\n=== Testing PEEK with PyMuPDF4LLM ===")
        from src.docsray.tools import peek
        
        peek_result = await peek.handle_peek(
            document_url=str(test_doc),
            depth="structure",
            provider="pymupdf4llm",
            registry=server.registry,
            cache=server.cache
        )
        
        if "error" in peek_result:
            logger.error(f"Peek Error: {peek_result['error']}")
        else:
            logger.info(f"Peek Success! Provider: {peek_result.get('provider', 'pymupdf4llm')}")
            logger.info(f"Metadata: {peek_result.get('metadata', {})}")
        
        # Test xray with PyMuPDF4LLM (should fail gracefully)
        logger.info("\n=== Testing XRAY with PyMuPDF4LLM (should fail gracefully) ===")
        from src.docsray.tools import xray
        
        xray_result = await xray.handle_xray(
            document_url=str(test_doc),
            analysis_type=["entities", "key-points"],
            custom_instructions="Extract key information",
            provider="pymupdf4llm",
            registry=server.registry,
            cache=server.cache
        )
        
        if "error" in xray_result:
            logger.info(f"Expected error received: {xray_result['error']}")
            if "suggestion" in xray_result:
                logger.info(f"Suggestion: {xray_result['suggestion']}")
        else:
            logger.warning("Xray should have failed with PyMuPDF4LLM!")
        
        # Test extract with PyMuPDF4LLM (should work)
        logger.info("\n=== Testing EXTRACT with PyMuPDF4LLM ===")
        from src.docsray.tools import extract
        
        extract_result = await extract.handle_extract(
            document_url=str(test_doc),
            extraction_targets=["text"],
            output_format="markdown",
            pages=[1],
            provider="pymupdf4llm",
            registry=server.registry,
            cache=server.cache
        )
        
        if "error" in extract_result:
            logger.error(f"Extract Error: {extract_result['error']}")
        else:
            logger.info(f"Extract Success! Provider: {extract_result.get('provider', 'pymupdf4llm')}")
            if 'content' in extract_result:
                content_preview = str(extract_result['content'])[:200]
                logger.info(f"Content preview: {content_preview}...")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(test_providers())