#!/usr/bin/env python3
"""Test script using .env file configuration."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

# Load .env file
load_dotenv(Path(__file__).parent.parent.parent / '.env')

from src.docsray.config import DocsrayConfig
from src.docsray.server import DocsrayServer

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_with_llamaparse():
    """Test xray functionality with LlamaParse."""
    try:
        # Load configuration from environment
        config = DocsrayConfig.from_env()
        
        logger.info(f"PyMuPDF4LLM enabled: {config.providers.pymupdf4llm.enabled}")
        logger.info(f"LlamaParse enabled: {config.providers.llama_parse.enabled}")
        logger.info(f"LlamaParse API key present: {bool(config.providers.llama_parse.api_key)}")
        
        # Initialize server
        logger.info("Initializing Docsray server...")
        server = DocsrayServer(config)
        
        # Check available providers
        providers = server.registry.list_providers()
        logger.info(f"Available providers: {providers}")
        
        if "llama-parse" not in providers:
            logger.error("LlamaParse provider not available!")
            return
        
        # Test document
        test_doc = Path("/workspace/docsray-mcp/tests/files/sample_lease.pdf")
        if not test_doc.exists():
            logger.error(f"Test document not found: {test_doc}")
            return
        
        logger.info(f"Testing xray with document: {test_doc}")
        
        # Test xray with LlamaParse
        from src.docsray.tools import xray
        
        result = await xray.handle_xray(
            document_url=str(test_doc),
            analysis_type=["entities", "key-points"],
            custom_instructions="Extract the main parties and key terms from this lease agreement",
            provider="llama-parse",
            registry=server.registry,
            cache=server.cache
        )
        
        logger.info("\n=== XRAY RESULT ===")
        if "error" in result:
            logger.error(f"Error: {result['error']}")
            if "suggestion" in result:
                logger.info(f"Suggestion: {result['suggestion']}")
        else:
            logger.info(f"SUCCESS! Provider used: {result.get('provider')}")
            logger.info(f"Provider info: {result.get('providerInfo')}")
            
            # Show analysis results
            if 'analysis' in result:
                analysis = result['analysis']
                logger.info(f"Analysis keys: {list(analysis.keys())}")
                
                if 'entities' in analysis:
                    logger.info(f"\nFound {len(analysis['entities'])} entities:")
                    for entity in analysis['entities'][:5]:
                        logger.info(f"  - {entity}")
                
                if 'key_points' in analysis:
                    logger.info(f"\nFound {len(analysis['key_points'])} key points:")
                    for i, point in enumerate(analysis['key_points'][:5], 1):
                        logger.info(f"  {i}. {point}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(test_with_llamaparse())