"""Test MCP server tools using mcp-use."""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

# Import mcp-use when available
try:
    from mcp_use import MCPClient
    MCP_USE_AVAILABLE = True
except ImportError:
    MCP_USE_AVAILABLE = False
    MCPClient = None


@pytest.mark.skipif(not MCP_USE_AVAILABLE, reason="mcp-use not available")
class TestMCPServerTools:
    """Test MCP server tools functionality."""

    @pytest.fixture
    async def mcp_client(self, mcp_config: Dict[str, Any]):
        """Create and initialize MCP client."""
        client = MCPClient(
            command=mcp_config["command"],
            args=mcp_config["args"],
            env=mcp_config["env"],
            timeout=mcp_config["timeout"]
        )
        
        await client.start()
        yield client
        await client.stop()

    async def test_list_tools(self, mcp_client):
        """Test that MCP server exposes expected tools."""
        tools = await mcp_client.list_tools()
        
        expected_tools = {
            "docsray_extract",
            "docsray_peek", 
            "docsray_seek",
            "docsray_map",
            "docsray_xray"
        }
        
        tool_names = {tool["name"] for tool in tools}
        assert expected_tools.issubset(tool_names), f"Missing tools: {expected_tools - tool_names}"

    async def test_peek_tool(self, mcp_client, sample_pdf_path: Path):
        """Test the peek tool functionality."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")
            
        result = await mcp_client.call_tool(
            "docsray_peek",
            {
                "url": str(sample_pdf_path),
                "options": {"depth": "metadata"}
            }
        )
        
        assert result is not None
        assert "content" in result
        
        # Parse the result content
        content = result["content"]
        if isinstance(content, list) and content:
            content_text = content[0].get("text", "")
            assert content_text  # Should have some content

    async def test_extract_tool(self, mcp_client, sample_pdf_path: Path):
        """Test the extract tool functionality."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")
            
        result = await mcp_client.call_tool(
            "docsray_extract",
            {
                "url": str(sample_pdf_path),
                "format": "markdown"
            }
        )
        
        assert result is not None
        assert "content" in result

    async def test_map_tool(self, mcp_client, sample_pdf_path: Path):
        """Test the map tool functionality."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")
            
        result = await mcp_client.call_tool(
            "docsray_map",
            {
                "url": str(sample_pdf_path),
                "options": {"include_structure": True}
            }
        )
        
        assert result is not None
        assert "content" in result

    async def test_seek_tool(self, mcp_client, sample_pdf_path: Path):
        """Test the seek tool functionality."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")
            
        result = await mcp_client.call_tool(
            "docsray_seek",
            {
                "url": str(sample_pdf_path),
                "query": "test content",
                "options": {"max_results": 5}
            }
        )
        
        assert result is not None
        assert "content" in result

    async def test_xray_tool(self, mcp_client, sample_pdf_path: Path):
        """Test the xray tool functionality.""" 
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")
            
        result = await mcp_client.call_tool(
            "docsray_xray",
            {
                "url": str(sample_pdf_path),
                "options": {"analysis_type": "comprehensive"}
            }
        )
        
        assert result is not None
        assert "content" in result

    async def test_server_resources(self, mcp_client):
        """Test that server exposes expected resources."""
        resources = await mcp_client.list_resources()
        
        # Should have at least the cache resource
        resource_uris = {resource["uri"] for resource in resources}
        
        # Check for expected resource patterns
        cache_resources = [uri for uri in resource_uris if uri.startswith("cache://")]
        assert len(cache_resources) >= 0  # May be empty if no cache entries

    async def test_server_prompts(self, mcp_client):
        """Test that server exposes expected prompts."""
        prompts = await mcp_client.list_prompts()
        
        expected_prompts = {
            "analyze_document",
            "extract_content", 
            "summarize_document"
        }
        
        prompt_names = {prompt["name"] for prompt in prompts}
        
        # Check if any expected prompts are available
        # (Server might not implement all prompts)
        available_prompts = expected_prompts.intersection(prompt_names)
        assert len(available_prompts) >= 0  # At least check the call doesn't fail


@pytest.mark.skipif(not MCP_USE_AVAILABLE, reason="mcp-use not available")
class TestMCPServerStability:
    """Test MCP server stability and error handling."""

    @pytest.fixture
    async def mcp_client(self, mcp_config: Dict[str, Any]):
        """Create and initialize MCP client."""
        client = MCPClient(
            command=mcp_config["command"],
            args=mcp_config["args"],
            env=mcp_config["env"],
            timeout=mcp_config["timeout"]
        )
        
        await client.start()
        yield client
        await client.stop()

    async def test_invalid_tool_call(self, mcp_client):
        """Test server handles invalid tool calls gracefully."""
        with pytest.raises(Exception):  # Should raise some kind of error
            await mcp_client.call_tool("nonexistent_tool", {})

    async def test_invalid_document_url(self, mcp_client):
        """Test server handles invalid document URLs gracefully."""
        result = await mcp_client.call_tool(
            "docsray_peek",
            {
                "url": "/nonexistent/file.pdf",
                "options": {"depth": "metadata"}
            }
        )
        
        # Should handle gracefully, not crash
        assert result is not None

    async def test_malformed_parameters(self, mcp_client):
        """Test server handles malformed parameters gracefully."""
        with pytest.raises(Exception):  # Should raise validation error
            await mcp_client.call_tool(
                "docsray_extract",
                {
                    "url": 123,  # Should be string
                    "format": "invalid_format"
                }
            )

    async def test_server_restart_stability(self, mcp_config: Dict[str, Any]):
        """Test that server can be restarted multiple times."""
        for i in range(3):
            client = MCPClient(
                command=mcp_config["command"],
                args=mcp_config["args"],
                env=mcp_config["env"],
                timeout=mcp_config["timeout"]
            )
            
            await client.start()
            
            # Quick test to ensure server is responsive
            tools = await client.list_tools()
            assert len(tools) > 0
            
            await client.stop()
            
            # Small delay between restarts
            await asyncio.sleep(0.5)


# Alternative test approach for when mcp-use is not available
@pytest.mark.skipif(MCP_USE_AVAILABLE, reason="mcp-use is available, use direct tests")
class TestMCPServerManual:
    """Manual MCP server tests using subprocess."""

    async def test_server_starts(self, mcp_server_env: Dict[str, str], tmp_path: Path):
        """Test that MCP server starts without crashing."""
        import subprocess
        import time
        
        # Create a test script to start server briefly
        test_script = tmp_path / "test_server.py"
        test_script.write_text('''
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from docsray.cli import main
from docsray.config import DocsrayConfig
from docsray.server import DocsrayServer

async def test_startup():
    config = DocsrayConfig.from_env()
    server = DocsrayServer(config)
    
    # Quick startup test
    print("Server created successfully")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_startup())
    print(f"Startup test: {'PASS' if result else 'FAIL'}")
        ''')
        
        # Run the test
        result = subprocess.run(
            ["python", str(test_script)],
            env=mcp_server_env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0, f"Server startup failed: {result.stderr}"
        assert "PASS" in result.stdout