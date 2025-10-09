"""Example usage of MCP server with mcp-use client."""

import asyncio
import json
import sys
from pathlib import Path

# Import mcp-use
try:
    from mcp_use import MCPClient
except ImportError:
    print("mcp-use not installed. Install with: pip install mcp-use")
    sys.exit(1)


async def demo_mcp_client():
    """Demonstrate MCP client usage with docsray server."""
    
    # Configuration for local docsray server
    config = {
        "command": "python",
        "args": [
            str(Path(__file__).parent / "run_test_server.py")
        ],
        "env": {
            "DOCSRAY_LOG_LEVEL": "DEBUG",
            "DOCSRAY_CACHE_ENABLED": "true",
            "DOCSRAY_PYMUPDF_ENABLED": "true",
            "PYTHONPATH": str(Path(__file__).parent.parent.parent / "src"),
        },
        "timeout": 30
    }
    
    print("Starting MCP client demo...")
    
    # Create and start client
    client = MCPClient(
        command=config["command"],
        args=config["args"],
        env=config["env"],
        timeout=config["timeout"]
    )
    
    try:
        await client.start()
        print("✓ MCP client connected to docsray server")
        
        # List available tools
        print("\n--- Available Tools ---")
        tools = await client.list_tools()
        for tool in tools:
            print(f"• {tool['name']}: {tool.get('description', 'No description')}")
        
        # List available resources
        print("\n--- Available Resources ---")
        resources = await client.list_resources()
        for resource in resources:
            print(f"• {resource['uri']}: {resource.get('name', 'No name')}")
        
        # List available prompts
        print("\n--- Available Prompts ---")
        prompts = await client.list_prompts()
        for prompt in prompts:
            print(f"• {prompt['name']}: {prompt.get('description', 'No description')}")
        
        # Demo: Create a test document and analyze it
        test_files_dir = Path(__file__).parent.parent / "files"
        test_files_dir.mkdir(exist_ok=True)
        
        # Create a simple test document if it doesn't exist
        test_doc = test_files_dir / "test_document.txt"
        if not test_doc.exists():
            test_doc.write_text("""
This is a test document for demonstrating the Docsray MCP server.

It contains multiple paragraphs with various content types:

1. Lists with numbered items
2. Technical information
3. Sample data for testing

The document also includes some metadata and structure that can be analyzed
using the various tools provided by the MCP server.

Key features to test:
- Content extraction
- Metadata analysis  
- Search functionality
- Document mapping
- Structure analysis
            """.strip())
            print(f"✓ Created test document: {test_doc}")
        
        # Test the peek tool
        print(f"\n--- Testing docsray_peek with {test_doc.name} ---")
        try:
            result = await client.call_tool(
                "docsray_peek",
                {
                    "url": str(test_doc),
                    "options": {"depth": "metadata"}
                }
            )
            print("✓ Peek tool result:")
            print(json.dumps(result, indent=2)[:500] + "..." if len(str(result)) > 500 else json.dumps(result, indent=2))
        except Exception as e:
            print(f"✗ Peek tool failed: {e}")
        
        # Test the extract tool
        print(f"\n--- Testing docsray_extract with {test_doc.name} ---")
        try:
            result = await client.call_tool(
                "docsray_extract",
                {
                    "url": str(test_doc),
                    "format": "markdown"
                }
            )
            print("✓ Extract tool result:")
            content = result.get("content", [])
            if content and isinstance(content, list):
                text_content = content[0].get("text", "")[:200]
                print(f"Extracted content preview: {text_content}...")
            else:
                print(json.dumps(result, indent=2)[:300] + "...")
        except Exception as e:
            print(f"✗ Extract tool failed: {e}")
        
        # Test the seek tool
        print(f"\n--- Testing docsray_seek with {test_doc.name} ---")
        try:
            result = await client.call_tool(
                "docsray_seek",
                {
                    "url": str(test_doc),
                    "query": "test",
                    "options": {"max_results": 3}
                }
            )
            print("✓ Seek tool result:")
            print(json.dumps(result, indent=2)[:400] + "..." if len(str(result)) > 400 else json.dumps(result, indent=2))
        except Exception as e:
            print(f"✗ Seek tool failed: {e}")
        
        print("\n--- Demo completed successfully! ---")
        
    except Exception as e:
        print(f"✗ Demo failed: {e}")
        raise
    finally:
        try:
            await client.stop()
            print("✓ MCP client disconnected")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(demo_mcp_client())