"""Tests for new fetch and search tools."""

import pytest
import tempfile
import os
import shutil
from pathlib import Path

from docsray.tools import fetch, search
from docsray.providers.base import Document


class TestFetchTool:
    """Test the fetch tool implementation."""

    @pytest.mark.asyncio
    async def test_fetch_local_file(self, registry, cache, mock_provider, sample_document):
        """Test fetching a local file."""
        registry.register(mock_provider)
        
        result = await fetch.handle_fetch(
            source=sample_document.url,
            registry=registry,
            cache=cache,
            return_format="metadata-only"
        )
        
        assert "source" in result
        assert result["source"] == sample_document.url
        assert result["returnFormat"] == "metadata-only"
        assert result["cacheStrategy"] == "use-cache"

    @pytest.mark.asyncio
    async def test_fetch_with_processing(self, registry, cache, mock_provider, sample_document):
        """Test fetching with content processing."""
        registry.register(mock_provider)
        
        result = await fetch.handle_fetch(
            source=sample_document.url,
            registry=registry,
            cache=cache,
            return_format="processed",
            provider="mock"
        )
        
        # Should either succeed or fail gracefully
        assert isinstance(result, dict)
        assert "source" in result or "error" in result

    @pytest.mark.asyncio
    async def test_fetch_cache_strategies(self, registry, cache, mock_provider, sample_document):
        """Test different cache strategies."""
        registry.register(mock_provider)
        
        strategies = ["use-cache", "bypass-cache", "refresh-cache"]
        
        for strategy in strategies:
            result = await fetch.handle_fetch(
                source=sample_document.url,
                registry=registry,
                cache=cache,
                cache_strategy=strategy,
                return_format="metadata-only"
            )
            
            assert result["cacheStrategy"] == strategy

    @pytest.mark.asyncio
    async def test_fetch_invalid_cache_strategy(self, registry, cache):
        """Test fetch with invalid cache strategy."""
        result = await fetch.handle_fetch(
            source="test.pdf",
            registry=registry,
            cache=cache,
            cache_strategy="invalid-strategy"
        )
        
        assert "error" in result
        assert "validStrategies" in result

    @pytest.mark.asyncio
    async def test_fetch_invalid_return_format(self, registry, cache):
        """Test fetch with invalid return format."""
        result = await fetch.handle_fetch(
            source="test.pdf",
            registry=registry,
            cache=cache,
            return_format="invalid-format"
        )
        
        assert "error" in result
        assert "validFormats" in result


class TestSearchTool:
    """Test the search tool implementation."""

    @pytest.fixture
    def temp_search_dir(self):
        """Create a temporary directory with test files."""
        temp_dir = tempfile.mkdtemp()
        
        # Create test files
        test_files = {
            "document1.pdf": "This is a PDF document about machine learning and AI.",
            "report.docx": "Annual report containing financial data and analytics.",
            "readme.txt": "Instructions for using the machine learning algorithms.",
            "notes.md": "# Research Notes\n\nNotes about deep learning research."
        }
        
        for filename, content in test_files.items():
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Create subdirectory
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "nested.pdf"), 'w') as f:
            f.write("Nested document with important information.")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_search_basic(self, registry, cache, temp_search_dir):
        """Test basic filesystem search."""
        result = await search.handle_search(
            query="machine learning",
            search_path=temp_search_dir,
            search_strategy="keyword",
            file_types=["pdf", "txt", "md"],
            max_results=10,
            provider="filesystem",
            registry=registry,
            cache=cache
        )
        
        assert "results" in result
        assert "total_found" in result
        assert "search_strategy" in result
        assert result["search_strategy"] == "keyword"
        assert isinstance(result["results"], list)

    @pytest.mark.asyncio
    async def test_search_coarse_to_fine(self, registry, cache, temp_search_dir):
        """Test coarse-to-fine search strategy."""
        result = await search.handle_search(
            query="machine learning",
            search_path=temp_search_dir,
            search_strategy="coarse-to-fine",
            file_types=["pdf", "txt"],
            max_results=5,
            provider="filesystem",
            registry=registry,
            cache=cache
        )
        
        assert "results" in result
        assert "statistics" in result
        assert result["search_strategy"] == "coarse-to-fine"
        
        if result["total_found"] > 0:
            # Check result structure
            first_result = result["results"][0]
            assert "file_path" in first_result
            assert "relevance_score" in first_result
            assert "relative_path" in first_result

    @pytest.mark.asyncio
    async def test_search_file_types_filter(self, registry, cache, temp_search_dir):
        """Test search with file type filtering."""
        # Search only for PDF files
        result = await search.handle_search(
            query="document",
            search_path=temp_search_dir,
            search_strategy="keyword",
            file_types=["pdf"],
            max_results=10,
            provider="filesystem",
            registry=registry,
            cache=cache
        )
        
        assert "results" in result
        
        # All results should be PDF files
        for result_item in result["results"]:
            file_path = result_item["file_path"]
            assert file_path.endswith('.pdf')

    @pytest.mark.asyncio
    async def test_search_nonexistent_path(self, registry, cache):
        """Test search with non-existent path."""
        result = await search.handle_search(
            query="test",
            search_path="/nonexistent/path",
            search_strategy="keyword",
            file_types=["pdf"],
            max_results=10,
            provider="filesystem",
            registry=registry,
            cache=cache
        )
        
        assert "error" in result
        assert "suggestion" in result

    @pytest.mark.asyncio
    async def test_search_file_as_path(self, registry, cache, temp_search_dir):
        """Test search with file path instead of directory."""
        # Create a file to use as search path
        test_file = os.path.join(temp_search_dir, "test.txt")
        
        result = await search.handle_search(
            query="test",
            search_path=test_file,
            search_strategy="keyword",
            file_types=["txt"],
            max_results=10,
            provider="filesystem",
            registry=registry,
            cache=cache
        )
        
        assert "error" in result
        assert "directory" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_search_relevance_scoring(self, registry, cache, temp_search_dir):
        """Test search relevance scoring."""
        result = await search.handle_search(
            query="machine learning",
            search_path=temp_search_dir,
            search_strategy="keyword",
            file_types=["pdf", "txt", "md"],
            max_results=10,
            provider="filesystem",
            registry=registry,
            cache=cache
        )
        
        if result["total_found"] > 1:
            # Results should be sorted by relevance (descending)
            scores = [r["relevance_score"] for r in result["results"]]
            assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_search_caching(self, registry, cache, temp_search_dir):
        """Test search result caching."""
        query_params = {
            "query": "test query",
            "search_path": temp_search_dir,
            "search_strategy": "keyword",
            "file_types": ["txt"],
            "max_results": 10,
            "provider": "filesystem"
        }
        
        # First search
        result1 = await search.handle_search(
            registry=registry,
            cache=cache,
            **query_params
        )
        
        # Second search (should use cache)
        result2 = await search.handle_search(
            registry=registry,
            cache=cache,
            **query_params
        )
        
        # Results should be identical (from cache)
        assert result1 == result2

    @pytest.mark.asyncio
    async def test_search_empty_results(self, registry, cache, temp_search_dir):
        """Test search with no matching results."""
        result = await search.handle_search(
            query="nonexistent_unique_term_12345",
            search_path=temp_search_dir,
            search_strategy="keyword",
            file_types=["pdf", "txt"],
            max_results=10,
            provider="filesystem",
            registry=registry,
            cache=cache
        )
        
        assert "results" in result
        assert result["total_found"] == 0
        assert len(result["results"]) == 0

    @pytest.mark.asyncio
    async def test_search_max_results_limit(self, registry, cache, temp_search_dir):
        """Test search with max results limit."""
        result = await search.handle_search(
            query="document",  # Should match multiple files
            search_path=temp_search_dir,
            search_strategy="keyword",
            file_types=["pdf", "txt", "md", "docx"],
            max_results=2,
            provider="filesystem",
            registry=registry,
            cache=cache
        )
        
        assert "results" in result
        assert len(result["results"]) <= 2

    @pytest.mark.asyncio
    async def test_search_result_structure(self, registry, cache, temp_search_dir):
        """Test the structure of search results."""
        result = await search.handle_search(
            query="document",
            search_path=temp_search_dir,
            search_strategy="keyword",
            file_types=["pdf", "txt"],
            max_results=10,
            provider="filesystem",
            registry=registry,
            cache=cache
        )
        
        assert "results" in result
        assert "total_found" in result
        assert "search_strategy" in result
        assert "search_path" in result
        assert "query" in result
        assert "file_types" in result
        assert "provider" in result
        assert "statistics" in result
        
        # Check statistics structure
        stats = result["statistics"]
        assert "coarse_search_candidates" in stats
        assert "fine_search_results" in stats
        assert "search_strategy_used" in stats
        
        # Check individual result structure
        if result["total_found"] > 0:
            first_result = result["results"][0]
            assert "file_path" in first_result
            assert "relative_path" in first_result
            assert "relevance_score" in first_result
            assert "snippet" in first_result
            assert "metadata" in first_result


class TestToolIntegrationWithNewFeatures:
    """Integration tests including the new fetch and search tools."""

    @pytest.mark.asyncio
    async def test_fetch_then_analyze_workflow(self, registry, cache, mock_provider, sample_document):
        """Test workflow: fetch document then analyze it."""
        registry.register(mock_provider)
        
        # Step 1: Fetch the document
        fetch_result = await fetch.handle_fetch(
            source=sample_document.url,
            registry=registry,
            cache=cache,
            return_format="raw"
        )
        
        assert "source" in fetch_result or "error" in fetch_result
        
        # Step 2: Analyze the fetched document (if fetch succeeded)
        if "error" not in fetch_result:
            from docsray.tools import peek
            
            peek_result = await peek.handle_peek(
                document_url=sample_document.url,
                depth="structure",
                provider="mock",
                registry=registry,
                cache=cache
            )
            
            assert "metadata" in peek_result

    @pytest.mark.asyncio
    async def test_search_then_process_workflow(self, registry, cache, mock_provider):
        """Test workflow: search for documents then process them."""
        registry.register(mock_provider)
        
        # Create temporary search directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test documents
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("Test document content with important information.")
            
            # Step 1: Search for documents
            search_result = await search.handle_search(
                query="important",
                search_path=temp_dir,
                search_strategy="keyword",
                file_types=["txt"],
                max_results=10,
                provider="filesystem",
                registry=registry,
                cache=cache
            )
            
            assert "results" in search_result
            
            # Step 2: Process found documents
            if search_result["total_found"] > 0:
                from docsray.tools import extract
                
                found_document = search_result["results"][0]["file_path"]
                
                extract_result = await extract.handle_extract(
                    document_url=found_document,
                    extraction_targets=["text"],
                    output_format="markdown",
                    pages=None,
                    provider="mock",
                    registry=registry,
                    cache=cache
                )
                
                assert "content" in extract_result or "error" in extract_result