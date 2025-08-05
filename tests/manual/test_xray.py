#!/usr/bin/env python3
"""Test script to verify xray functionality with LlamaParse provider."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Set up environment variables first
os.environ["DOCSRAY_LLAMAPARSE_ENABLED"] = "true"
os.environ["DOCSRAY_LLAMAPARSE_API_KEY"] = os.getenv("LLAMAPARSE_API_KEY", "")
os.environ["DOCSRAY_LLAMAPARSE_MODE"] = "fast"

from src.docsray.config import DocsrayConfig
from src.docsray.server import DocsrayServer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_xray():
    """Test xray functionality."""
    try:
        # Load configuration
        config = DocsrayConfig.from_env()
        
        # Check if API key is set
        if not config.providers.llama_parse.api_key:
            logger.error("LLAMAPARSE_API_KEY environment variable is not set!")
            logger.info("Please set LLAMAPARSE_API_KEY environment variable and try again.")
            return
        
        logger.info(f"Configuration loaded. LlamaParse enabled: {config.providers.llama_parse.enabled}")
        logger.info(f"API Key present: {'Yes' if config.providers.llama_parse.api_key else 'No'}")
        
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
        
        # Test xray with LlamaParse
        from src.docsray.providers.base import Document
        from src.docsray.tools import xray
        
        result = await xray.handle_xray(
            document_url=str(test_doc),
            analysis_type=["entities", "key-points"],
            custom_instructions="Extract the main parties and key terms from this lease agreement",
            provider="llama-parse",
            registry=server.registry,
            cache=server.cache
        )
        
        logger.info("Xray result:")
        if "error" in result:
            logger.error(f"Error: {result['error']}")
            if "suggestion" in result:
                logger.info(f"Suggestion: {result['suggestion']}")
        else:
            logger.info(f"Provider used: {result.get('provider')}")
            logger.info(f"Analysis keys: {list(result.get('analysis', {}).keys())}")
            
            # Show some results
            if 'analysis' in result:
                analysis = result['analysis']
                if 'entities' in analysis:
                    logger.info(f"Found {len(analysis['entities'])} entities")
                    for entity in analysis['entities'][:3]:
                        logger.info(f"  - {entity}")
                
                if 'key_points' in analysis:
                    logger.info(f"Found {len(analysis['key_points'])} key points")
                    for point in analysis['key_points'][:3]:
                        logger.info(f"  - {point}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(test_xray())