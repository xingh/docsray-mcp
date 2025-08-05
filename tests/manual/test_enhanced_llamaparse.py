#!/usr/bin/env python3
"""Test enhanced LlamaParse functionality."""

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

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_enhanced_extraction():
    """Test enhanced extraction capabilities."""
    try:
        # Load configuration
        config = DocsrayConfig.from_env()
        logger.info("Initializing Docsray server...")
        server = DocsrayServer(config)
        
        # Test document
        test_doc = Path("/workspace/docsray-mcp/tests/files/sample_lease.pdf")
        
        # Test 1: Extract with multiple targets including images and tables
        logger.info("\n=== TEST 1: Enhanced Extraction with Multiple Targets ===")
        from src.docsray.tools import extract
        
        result = await extract.handle_extract(
            document_url=str(test_doc),
            extraction_targets=["text", "tables", "images", "metadata", "layout"],
            output_format="structured",  # Get full structured data
            pages=None,  # All pages
            provider="llama-parse",
            registry=server.registry,
            cache=server.cache
        )
        
        if "error" in result:
            logger.error(f"Extract Error: {result['error']}")
        else:
            logger.info(f"Extract Success!")
            if "statistics" in result:
                stats = result["statistics"]
                logger.info(f"Statistics: {json.dumps(stats, indent=2)}")
            
            if "content" in result:
                content = result["content"]
                logger.info(f"Content keys: {list(content.keys())}")
                
                # Check pages
                if "pages" in content:
                    logger.info(f"Pages extracted: {len(content['pages'])}")
                    if content['pages']:
                        first_page = content['pages'][0]
                        logger.info(f"First page keys: {list(first_page.keys())}")
                        if "markdown" in first_page:
                            logger.info(f"First page has markdown content: {len(first_page['markdown'])} chars")
                
                # Check images
                if "images" in content:
                    logger.info(f"Images found: {len(content['images'])}")
                    for img in content['images'][:2]:
                        logger.info(f"  - Image on page {img.get('page')}: {img.get('type', 'unknown')}")
                
                # Check tables
                if "tables" in content:
                    logger.info(f"Tables found: {len(content['tables'])}")
                    for table in content['tables'][:2]:
                        logger.info(f"  - Table on page {table.get('page')}")
                        if table.get('html'):
                            logger.info(f"    Has HTML content: {len(table['html'])} chars")
        
        # Test 2: Map with comprehensive analysis
        logger.info("\n=== TEST 2: Comprehensive Document Mapping ===")
        from src.docsray.tools import map as map_tool
        
        map_result = await map_tool.handle_map(
            document_url=str(test_doc),
            include_content=True,
            analysis_depth="comprehensive",
            provider="llama-parse",
            registry=server.registry,
            cache=server.cache
        )
        
        if "error" in map_result:
            logger.error(f"Map Error: {map_result['error']}")
        else:
            logger.info(f"Map Success!")
            if "statistics" in map_result:
                logger.info(f"Map Statistics: {json.dumps(map_result['statistics'], indent=2)}")
            
            if "document_map" in map_result:
                doc_map = map_result["document_map"]
                
                # Check hierarchy
                if "hierarchy" in doc_map:
                    hierarchy = doc_map["hierarchy"]
                    logger.info(f"Document hierarchy root: {hierarchy.get('root', {}).get('type')}")
                    if "children" in hierarchy.get("root", {}):
                        logger.info(f"Root children: {len(hierarchy['root']['children'])}")
                
                # Check resources
                if "resources" in doc_map:
                    resources = doc_map["resources"]
                    logger.info(f"Resources found:")
                    logger.info(f"  - Images: {len(resources.get('images', []))}")
                    logger.info(f"  - Tables: {len(resources.get('tables', []))}")
                
                # Check page structure
                if "pageStructure" in doc_map:
                    page_struct = doc_map["pageStructure"]
                    logger.info(f"Page structure entries: {len(page_struct)}")
                    for page in page_struct[:2]:
                        logger.info(f"  - Page {page.get('pageNumber')}: "
                                  f"hasText={page.get('hasText')}, "
                                  f"hasImages={page.get('hasImages')}, "
                                  f"hasTables={page.get('hasTables')}")
        
        # Test 3: Extract as JSON with enhanced format
        logger.info("\n=== TEST 3: JSON Format with Enhanced Structure ===")
        
        json_result = await extract.handle_extract(
            document_url=str(test_doc),
            extraction_targets=["text", "tables", "images", "metadata"],
            output_format="json",
            pages=[1, 2],  # First two pages only
            provider="llama-parse",
            registry=server.registry,
            cache=server.cache
        )
        
        if "error" in json_result:
            logger.error(f"JSON Extract Error: {json_result['error']}")
        else:
            logger.info(f"JSON Extract Success!")
            if "content" in json_result:
                content = json_result["content"]
                logger.info(f"JSON content keys: {list(content.keys())}")
                
                if "statistics" in content:
                    logger.info(f"Extraction statistics: {json.dumps(content['statistics'], indent=2)}")
                
                if "text" in content:
                    logger.info(f"Text entries: {len(content['text'])}")
                    for text_entry in content['text'][:2]:
                        logger.info(f"  - Page {text_entry.get('page')}: "
                                  f"{len(text_entry.get('content', ''))} chars, "
                                  f"markdown: {len(text_entry.get('markdown', ''))} chars")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(test_enhanced_extraction())