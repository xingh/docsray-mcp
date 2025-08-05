#!/usr/bin/env python3
"""Test the LlamaParse caching system."""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(Path(__file__).parent.parent.parent / '.env')

from src.docsray.config import DocsrayConfig
from src.docsray.server import DocsrayServer
from src.docsray.utils.llamaparse_cache import LlamaParseCache

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_cache_system():
    """Test the caching system with LlamaParse."""
    try:
        # Initialize server
        config = DocsrayConfig.from_env()
        server = DocsrayServer(config)
        
        # Test document
        test_doc = Path("/workspace/docsray-mcp/tests/files/sample_lease.pdf")
        
        # Initialize cache manager
        cache = LlamaParseCache()
        
        # Clear any existing cache for this document
        cache.clear_cache(test_doc)
        logger.info("Cleared any existing cache")
        
        # Test 1: First extraction (should make API call and cache)
        logger.info("\n=== TEST 1: First Extraction (API Call + Cache) ===")
        from src.docsray.tools import extract
        
        result1 = await extract.handle_extract(
            document_url=str(test_doc),
            extraction_targets=["text", "tables", "images", "metadata"],
            output_format="structured",
            pages=None,  # All pages
            provider="llama-parse",
            registry=server.registry,
            cache=server.cache
        )
        
        if "error" in result1:
            logger.error(f"Error: {result1['error']}")
            return
        
        logger.info("First extraction completed successfully")
        
        # Check if cache was created
        cache_info = cache.get_cache_info(test_doc)
        if cache_info:
            logger.info(f"Cache created successfully:")
            logger.info(f"  Pages: {cache_info['statistics']['pages']}")
            logger.info(f"  Images: {cache_info['statistics']['images']}")
            logger.info(f"  Tables: {cache_info['statistics']['tables']}")
            logger.info(f"  Size: {cache_info['statistics']['cache_size_mb']} MB")
        else:
            logger.error("Cache was not created!")
            return
        
        # Test 2: Second extraction (should use cache)
        logger.info("\n=== TEST 2: Second Extraction (From Cache) ===")
        
        result2 = await extract.handle_extract(
            document_url=str(test_doc),
            extraction_targets=["text", "tables", "images", "metadata"],
            output_format="structured",
            pages=None,  # All pages
            provider="llama-parse",
            registry=server.registry,
            cache=server.cache
        )
        
        if "error" in result2:
            logger.error(f"Error: {result2['error']}")
            return
        
        logger.info("Second extraction completed successfully (should have used cache)")
        
        # Verify results are the same
        if result1.get("content") and result2.get("content"):
            # Compare page counts
            pages1 = len(result1["content"].get("pages", []))
            pages2 = len(result2["content"].get("pages", []))
            
            if pages1 == pages2:
                logger.info(f"✓ Both extractions have same page count: {pages1}")
            else:
                logger.error(f"✗ Page count mismatch: {pages1} vs {pages2}")
        
        # Test 3: List cached documents
        logger.info("\n=== TEST 3: List Cached Documents ===")
        cached_docs = cache.list_cached_documents()
        logger.info(f"Found {len(cached_docs)} cached document(s)")
        for doc in cached_docs:
            logger.info(f"  - {Path(doc['original_document']).name}: {doc['cache_size_mb']} MB")
        
        # Test 4: Inspect cache contents
        logger.info("\n=== TEST 4: Inspect Cache Directory ===")
        cache_dir = cache.get_cache_dir(test_doc)
        logger.info(f"Cache directory: {cache_dir}")
        
        if cache_dir.exists():
            # List cache structure
            logger.info("Cache structure:")
            for item in sorted(cache_dir.iterdir()):
                if item.is_dir():
                    logger.info(f"  📁 {item.name}/")
                    for subitem in sorted(item.iterdir())[:3]:  # Show first 3 items
                        logger.info(f"    - {subitem.name}")
                    if len(list(item.iterdir())) > 3:
                        logger.info(f"    ... and {len(list(item.iterdir())) - 3} more")
                else:
                    logger.info(f"  📄 {item.name}")
            
            # Check if original document was cached
            original_file = cache_dir / f"original.pdf"
            if original_file.exists():
                logger.info(f"✓ Original document cached: {original_file.stat().st_size / 1024:.1f} KB")
            
            # Check metadata
            metadata_file = cache_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    logger.info(f"✓ Metadata stored:")
                    logger.info(f"    Document hash: {metadata.get('document_hash', '')[:16]}...")
                    logger.info(f"    Timestamp: {metadata.get('extraction_timestamp', '')}")
        
        # Test 5: Different parsing instruction (should not use cache)
        logger.info("\n=== TEST 5: Different Parsing Instruction ===")
        
        # Clear provider's parser to ensure different instruction
        from src.docsray.tools import xray
        
        result3 = await xray.handle_xray(
            document_url=str(test_doc),
            analysis_type=["entities"],
            custom_instructions="Extract only company names",  # Different instruction
            provider="llama-parse",
            registry=server.registry,
            cache=server.cache
        )
        
        logger.info("Extraction with different instruction completed")
        logger.info("(Should have made a new API call due to different parsing instruction)")
        
        logger.info("\n=== Cache System Test Completed Successfully ===")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(test_cache_system())