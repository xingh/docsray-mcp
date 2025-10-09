"""Script to run MCP server for local testing and development."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from docsray.config import DocsrayConfig
from docsray.server import DocsrayServer


async def run_test_server():
    """Run MCP server for testing with mcp-use."""
    # Load configuration
    config = DocsrayConfig.from_env()
    
    # Override settings for testing
    config.log_level = "DEBUG"
    config.cache.enabled = True
    config.providers.pymupdf4llm.enabled = True
    
    # Create server
    server = DocsrayServer(config)
    
    print("Starting Docsray MCP Server for testing...")
    print(f"Transport: {config.transport.type}")
    print(f"Log level: {config.log_level}")
    print(f"Cache enabled: {config.cache.enabled}")
    print("Press Ctrl+C to stop")
    
    try:
        await server.run()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        await server.shutdown()
    except Exception as e:
        print(f"Server error: {e}")
        await server.shutdown()
        raise


if __name__ == "__main__":
    # Set environment variables for testing
    os.environ.setdefault("DOCSRAY_LOG_LEVEL", "DEBUG")
    os.environ.setdefault("DOCSRAY_CACHE_ENABLED", "true")
    os.environ.setdefault("DOCSRAY_PYMUPDF_ENABLED", "true")
    
    asyncio.run(run_test_server())