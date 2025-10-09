"""Integration tests for tool endpoints."""

import pytest

from docsray.providers.base import Document
from docsray.tools import extract, fetch, map, peek, search, seek, xray


class TestToolIntegration:
    """Test tool endpoint integration."""
    
    @pytest.mark.asyncio
    async def test_seek_tool(self, registry, cache, mock_provider, sample_document):
        # Register provider
        registry.register(mock_provider)
        
        result = await seek.handle_seek(
            document_url=sample_document.url,
            target={"page": 1},
            extract_content=True,
            provider="mock",
            registry=registry,
            cache=cache
        )
        
        assert "location" in result
        assert result["location"]["page"] == 1
        assert "content" in result
        assert result["provider"] == "mock"
    
    @pytest.mark.asyncio
    async def test_peek_tool(self, registry, cache, mock_provider, sample_document):
        registry.register(mock_provider)
        
        result = await peek.handle_peek(
            document_url=sample_document.url,
            depth="structure",
            provider="mock",
            registry=registry,
            cache=cache
        )
        
        assert "metadata" in result
        assert "structure" in result
        assert result["provider"] == "mock"
    
    @pytest.mark.asyncio
    async def test_map_tool(self, registry, cache, mock_provider, sample_document):
        registry.register(mock_provider)
        
        result = await map.handle_map(
            document_url=sample_document.url,
            include_content=False,
            analysis_depth="deep",
            provider="mock",
            registry=registry,
            cache=cache
        )
        
        assert "documentMap" in result
        assert "statistics" in result
        assert result["provider"] == "mock"
    
    @pytest.mark.asyncio
    async def test_extract_tool(self, registry, cache, mock_provider, sample_document):
        registry.register(mock_provider)
        
        result = await extract.handle_extract(
            document_url=sample_document.url,
            extraction_targets=["text"],
            output_format="markdown",
            pages=None,
            provider="mock",
            registry=registry,
            cache=cache
        )
        
        assert "content" in result
        assert result["format"] == "markdown"
        assert result["provider"] == "mock"
    
    @pytest.mark.asyncio
    async def test_xray_tool(self, registry, cache, mock_provider, sample_document):
        registry.register(mock_provider)

        result = await xray.handle_xray(
            document_url=sample_document.url,
            analysis_type=["entities", "key-points"],
            custom_instructions=None,
            provider="mock",
            registry=registry,
            cache=cache
        )

        assert "analysis" in result
        assert result["provider"] == "mock"

    @pytest.mark.asyncio
    async def test_fetch_tool(self, registry, cache, mock_provider, sample_document):
        registry.register(mock_provider)

        result = await fetch.handle_fetch(
            source=sample_document.url,
            registry=registry,
            cache=cache,
            return_format="metadata-only"
        )

        # For file paths, expect path-related fields
        if not sample_document.url.startswith("http"):
            assert "path" in result or "error" in result
        # Test parameter validation
        assert result["cacheStrategy"] == "use-cache"
        assert result["returnFormat"] == "metadata-only"

    @pytest.mark.asyncio
    async def test_search_tool(self, registry, cache, mock_provider, sample_document):
        registry.register(mock_provider)
        import tempfile
        import shutil
        import os

        # Create temporary directory with test document
        temp_dir = tempfile.mkdtemp()
        try:
            # Copy test document to temp directory
            dest_path = os.path.join(temp_dir, "test_document.txt")
            if os.path.exists(sample_document.url):
                shutil.copy2(sample_document.url, dest_path)
            else:
                # Create a simple test file
                with open(dest_path, 'w') as f:
                    f.write("Sample document content for testing search functionality.")
            
            result = await search.handle_search(
                query="sample document",
                search_path=temp_dir,
                search_strategy="keyword",
                file_types=["txt"],
                max_results=5,
                provider="filesystem",
                registry=registry,
                cache=cache
            )
            
            assert "results" in result
            assert "total_found" in result
            assert "search_strategy" in result
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_tool_caching(self, registry, cache, mock_provider, sample_document):
        registry.register(mock_provider)
        
        # First call
        result1 = await peek.handle_peek(
            document_url=sample_document.url,
            depth="metadata",
            provider="mock",
            registry=registry,
            cache=cache
        )
        
        # Second call (should hit cache)
        result2 = await peek.handle_peek(
            document_url=sample_document.url,
            depth="metadata",
            provider="mock",
            registry=registry,
            cache=cache
        )
        
        assert result1 == result2
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self, registry, cache):
        # No providers registered
        result = await seek.handle_seek(
            document_url="test.pdf",
            target={"page": 1},
            extract_content=True,
            provider="auto",
            registry=registry,
            cache=cache
        )
        
        assert "error" in result
        assert "suggestion" in result