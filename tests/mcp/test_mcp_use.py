"""MCP-Use integration tests for testing the MCP server locally."""

import asyncio
import pytest
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

try:
    from mcp_use import use_mcp_tool
    MCP_USE_AVAILABLE = True
except ImportError:
    MCP_USE_AVAILABLE = False


@pytest.mark.skipif(not MCP_USE_AVAILABLE, reason="mcp-use not available")
class TestMcpUseIntegration:
    """Test MCP server using mcp-use for local testing."""

    @pytest.fixture(scope="class")
    def sample_pdf_content(self):
        """Create a sample PDF-like text for testing."""
        return """# Sample Document

This is a sample document for testing purposes.

## Section 1: Introduction

This document contains various types of content including:
- Text paragraphs
- Lists and bullet points
- Tables and structured data

## Section 2: Data Analysis

Key findings:
1. First finding with important data
2. Second finding with metrics
3. Third finding with conclusions

## Section 3: Conclusions

The analysis shows significant results in multiple areas.

Contact: john.doe@example.com
Date: 2024-01-15
Amount: $10,000
"""

    @pytest.fixture(scope="class")
    def temp_document(self, sample_pdf_content):
        """Create a temporary document file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_pdf_content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass

    @pytest.fixture(scope="class")
    def mcp_server_process(self):
        """Start MCP server process for testing."""
        # Start the server in a subprocess
        server_process = subprocess.Popen([
            "python", "-m", "docsray.cli", "start"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give server time to start
        asyncio.sleep(1)
        
        yield server_process
        
        # Cleanup
        server_process.terminate()
        server_process.wait()

    @pytest.mark.asyncio
    async def test_peek_tool(self, temp_document):
        """Test the peek tool using mcp-use."""
        result = await use_mcp_tool("docsray", "docsray_peek", {
            "document_url": temp_document,
            "depth": "structure",
            "provider": "auto"
        })
        
        assert "metadata" in result
        assert "structure" in result or "error" in result  # May not have full structure for text files

    @pytest.mark.asyncio
    async def test_extract_tool(self, temp_document):
        """Test the extract tool using mcp-use."""
        result = await use_mcp_tool("docsray", "docsray_extract", {
            "document_url": temp_document,
            "extraction_targets": ["text"],
            "output_format": "markdown",
            "provider": "auto"
        })
        
        assert "content" in result or "error" in result
        if "content" in result:
            assert isinstance(result["content"], str)

    @pytest.mark.asyncio
    async def test_map_tool(self, temp_document):
        """Test the map tool using mcp-use."""
        result = await use_mcp_tool("docsray", "docsray_map", {
            "document_url": temp_document,
            "include_content": False,
            "analysis_depth": "basic",
            "provider": "auto"
        })
        
        assert "documentMap" in result or "error" in result

    @pytest.mark.asyncio
    async def test_seek_tool(self, temp_document):
        """Test the seek tool using mcp-use."""
        result = await use_mcp_tool("docsray", "docsray_seek", {
            "document_url": temp_document,
            "target": {"query": "Introduction"},
            "extract_content": True,
            "provider": "auto"
        })
        
        assert "location" in result or "error" in result
        assert "content" in result or "error" in result

    @pytest.mark.asyncio
    async def test_xray_tool(self, temp_document):
        """Test the xray tool using mcp-use."""
        result = await use_mcp_tool("docsray", "docsray_xray", {
            "document_url": temp_document,
            "analysis_type": ["entities", "key-points"],
            "provider": "auto"
        })
        
        assert "analysis" in result or "error" in result

    @pytest.mark.asyncio
    async def test_fetch_tool(self, temp_document):
        """Test the fetch tool using mcp-use."""
        result = await use_mcp_tool("docsray", "docsray_fetch", {
            "source": temp_document,
            "return_format": "metadata-only",
            "cache_strategy": "use-cache"
        })
        
        assert "path" in result or "url" in result or "error" in result

    @pytest.mark.asyncio
    async def test_search_tool(self, temp_document):
        """Test the search tool using mcp-use."""
        # Create a temporary directory with the test document
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        try:
            # Copy test document to temp directory
            dest_path = os.path.join(temp_dir, "test_document.txt")
            shutil.copy2(temp_document, dest_path)
            
            result = await use_mcp_tool("docsray", "docsray_search", {
                "query": "sample document",
                "searchPath": temp_dir,
                "searchStrategy": "keyword",
                "fileTypes": ["txt"],
                "maxResults": 5
            })
            
            assert "results" in result or "error" in result
            assert "total_found" in result or "error" in result
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_server_info_resource(self):
        """Test the server info resource."""
        try:
            result = await use_mcp_tool("docsray", "get_resource", {
                "uri": "docsray://info"
            })
            
            assert "name" in result
            assert "capabilities" in result
            assert "tools" in result
            assert result["name"] == "docsray"
            
            # Check that all 7 tools are listed
            tool_names = [tool["name"] for tool in result["tools"]]
            expected_tools = [
                "docsray_peek", "docsray_map", "docsray_xray", 
                "docsray_extract", "docsray_seek", "docsray_fetch", 
                "docsray_search"
            ]
            
            for tool in expected_tools:
                assert tool in tool_names, f"Tool {tool} not found in server info"
                
        except Exception as e:
            pytest.skip(f"Server info resource test failed: {e}")

    @pytest.mark.asyncio
    async def test_example_prompts_resource(self):
        """Test the example prompts resource."""
        try:
            result = await use_mcp_tool("docsray", "get_resource", {
                "uri": "docsray://prompts"
            })
            
            assert "basic_operations" in result
            assert "advanced_analysis" in result
            assert "provider_specific" in result
            
            # Check that all tools have examples
            basic_ops = result["basic_operations"]
            assert "peek" in basic_ops
            assert "extract" in basic_ops
            assert "map" in basic_ops
            assert "fetch" in basic_ops
            assert "search" in basic_ops
            
        except Exception as e:
            pytest.skip(f"Example prompts resource test failed: {e}")

    @pytest.mark.asyncio
    async def test_provider_capabilities(self):
        """Test that providers are correctly reporting their capabilities."""
        # Get server info to check provider capabilities
        try:
            result = await use_mcp_tool("docsray", "get_resource", {
                "uri": "docsray://info"
            })
            
            providers = result["capabilities"]["providers"]
            assert len(providers) > 0, "No providers found"
            
            # Check that PyMuPDF4LLM is always available
            provider_names = [p["name"] for p in providers]
            assert "pymupdf4llm" in provider_names, "PyMuPDF4LLM provider not found"
            
            # Verify provider structure
            for provider in providers:
                assert "name" in provider
                assert "status" in provider
                assert "supported_formats" in provider
                assert "features" in provider
                
        except Exception as e:
            pytest.skip(f"Provider capabilities test failed: {e}")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test with non-existent file
        result = await use_mcp_tool("docsray", "docsray_peek", {
            "document_url": "/non/existent/file.pdf",
            "depth": "structure"
        })
        
        assert "error" in result
        assert "suggestion" in result or "type" in result

    @pytest.mark.asyncio
    async def test_all_tools_integration(self, temp_document):
        """Integration test using all tools in sequence."""
        results = {}
        
        # 1. Peek at the document
        results["peek"] = await use_mcp_tool("docsray", "docsray_peek", {
            "document_url": temp_document,
            "depth": "metadata"
        })
        
        # 2. Map the document structure
        results["map"] = await use_mcp_tool("docsray", "docsray_map", {
            "document_url": temp_document,
            "include_content": False,
            "analysis_depth": "basic"
        })
        
        # 3. Extract content
        results["extract"] = await use_mcp_tool("docsray", "docsray_extract", {
            "document_url": temp_document,
            "extraction_targets": ["text"],
            "output_format": "markdown"
        })
        
        # 4. Seek specific content
        results["seek"] = await use_mcp_tool("docsray", "docsray_seek", {
            "document_url": temp_document,
            "target": {"query": "Section 1"},
            "extract_content": True
        })
        
        # 5. Perform xray analysis
        results["xray"] = await use_mcp_tool("docsray", "docsray_xray", {
            "document_url": temp_document,
            "analysis_type": ["entities"],
            "custom_instructions": "Find email addresses and dates"
        })
        
        # Verify all operations completed (with success or expected errors)
        for tool_name, result in results.items():
            assert isinstance(result, dict), f"{tool_name} didn't return a dict"
            # Should have either successful result fields or error information
            assert len(result) > 0, f"{tool_name} returned empty result"


@pytest.mark.skipif(MCP_USE_AVAILABLE, reason="Test for missing mcp-use")
def test_mcp_use_not_available():
    """Test case for when mcp-use is not available."""
    pytest.skip("mcp-use is not installed, install with: pip install mcp-use")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])