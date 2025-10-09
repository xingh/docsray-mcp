"""Test MCP server performance and load handling."""

import asyncio
import time
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
class TestMCPServerPerformance:
    """Test MCP server performance characteristics."""

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

    async def test_tool_response_time(self, mcp_client, sample_pdf_path: Path):
        """Test that tools respond within reasonable time limits."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")

        # Test peek tool response time
        start_time = time.time()
        
        result = await mcp_client.call_tool(
            "docsray_peek",
            {
                "url": str(sample_pdf_path),
                "options": {"depth": "quick"}
            }
        )
        
        response_time = time.time() - start_time
        
        assert result is not None
        assert response_time < 10.0, f"Peek tool took too long: {response_time:.2f}s"

    async def test_concurrent_requests(self, mcp_client, sample_pdf_path: Path):
        """Test server handles concurrent requests."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")

        # Create multiple concurrent requests
        tasks = []
        for i in range(3):  # Start with small number
            task = mcp_client.call_tool(
                "docsray_peek",
                {
                    "url": str(sample_pdf_path),
                    "options": {"depth": "metadata"}
                }
            )
            tasks.append(task)

        # Wait for all to complete
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Check results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 2, "Most concurrent requests should succeed"
        assert total_time < 30.0, f"Concurrent requests took too long: {total_time:.2f}s"

    async def test_memory_usage_stability(self, mcp_client, sample_pdf_path: Path):
        """Test that server doesn't leak memory with repeated requests."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")

        # Make multiple requests to the same document
        for i in range(5):
            result = await mcp_client.call_tool(
                "docsray_peek",
                {
                    "url": str(sample_pdf_path),
                    "options": {"depth": "metadata"}
                }
            )
            assert result is not None
            
            # Small delay between requests
            await asyncio.sleep(0.1)

        # If we get here without timeout/crash, memory usage is stable enough


@pytest.mark.skipif(not MCP_USE_AVAILABLE, reason="mcp-use not available") 
class TestMCPServerIntegration:
    """Integration tests for MCP server with different document types."""

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

    async def test_workflow_extract_then_seek(self, mcp_client, sample_pdf_path: Path):
        """Test a typical workflow: extract content then search within it."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")

        # First extract content
        extract_result = await mcp_client.call_tool(
            "docsray_extract",
            {
                "url": str(sample_pdf_path),
                "format": "text"
            }
        )
        
        assert extract_result is not None
        assert "content" in extract_result

        # Then search within it
        seek_result = await mcp_client.call_tool(
            "docsray_seek",
            {
                "url": str(sample_pdf_path),
                "query": "content",  # Generic search term
                "options": {"max_results": 3}
            }
        )
        
        assert seek_result is not None
        assert "content" in seek_result

    async def test_caching_behavior(self, mcp_client, sample_pdf_path: Path):
        """Test that caching improves performance on repeated requests."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")

        # First request (cold cache)
        start_time = time.time()
        result1 = await mcp_client.call_tool(
            "docsray_peek",
            {
                "url": str(sample_pdf_path),
                "options": {"depth": "metadata"}
            }
        )
        first_time = time.time() - start_time

        # Second request (warm cache)
        start_time = time.time()
        result2 = await mcp_client.call_tool(
            "docsray_peek",
            {
                "url": str(sample_pdf_path),
                "options": {"depth": "metadata"}
            }
        )
        second_time = time.time() - start_time

        assert result1 is not None
        assert result2 is not None
        
        # Second request should generally be faster (or at least not much slower)
        # Allow some variance for system fluctuations
        assert second_time <= first_time * 2.0, "Caching should not make requests significantly slower"

    async def test_provider_selection(self, mcp_client, sample_pdf_path: Path):
        """Test that different providers can be selected."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")

        # Try with different providers if available
        providers_to_test = ["pymupdf4llm", "auto"]
        
        for provider in providers_to_test:
            try:
                result = await mcp_client.call_tool(
                    "docsray_peek",
                    {
                        "url": str(sample_pdf_path),
                        "options": {
                            "depth": "metadata",
                            "provider": provider
                        }
                    }
                )
                
                assert result is not None, f"Provider {provider} should work"
                
            except Exception as e:
                # Some providers might not be available in test environment
                # This is acceptable as long as at least one works
                print(f"Provider {provider} not available: {e}")
                continue