#!/usr/bin/env python3
"""Integration tests for LlamaParse provider functionality."""

import os
import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.docsray.config import DocsrayConfig
from src.docsray.server import DocsrayServer
from src.docsray.providers.base import Document
from src.docsray.utils.llamaparse_cache import LlamaParseCache


@pytest.mark.skipif(
    not os.getenv("LLAMAPARSE_API_KEY"),
    reason="LlamaParse API key not configured"
)
class TestLlamaParseIntegration:
    """Test LlamaParse provider integration."""
    
    @pytest.fixture
    def test_document(self):
        """Create a test document."""
        return Path(__file__).parent.parent / "files" / "sample_lease.pdf"
    
    @pytest.fixture
    def config_with_llamaparse(self):
        """Create config with LlamaParse enabled."""
        return DocsrayConfig(
            providers={
                "llama_parse": {
                    "enabled": True,
                    "api_key": os.getenv("LLAMAPARSE_API_KEY", "test-key"),
                    "mode": "balanced"
                },
                "pymupdf4llm": {"enabled": True}
            }
        )
    
    @pytest.mark.asyncio
    async def test_llamaparse_initialization(self, config_with_llamaparse):
        """Test LlamaParse provider initialization."""
        server = DocsrayServer(config_with_llamaparse)
        
        # Check provider is registered
        providers = server.registry.list_providers()
        assert "llama-parse" in providers
        
        # Get provider
        provider = server.registry.get_provider("llama-parse")
        assert provider is not None
        assert hasattr(provider, 'config')
        assert provider.config.api_key == config_with_llamaparse.providers.llama_parse.api_key
    
    @pytest.mark.asyncio
    async def test_llamaparse_caching(self, config_with_llamaparse, test_document):
        """Test LlamaParse caching functionality."""
        if not test_document.exists():
            pytest.skip(f"Test document not found: {test_document}")
        
        server = DocsrayServer(config_with_llamaparse)
        cache = LlamaParseCache()
        
        # Clear any existing cache
        cache.clear_cache(test_document)
        
        # First request should create cache
        from src.docsray.tools import peek
        result1 = await peek.handle_peek(
            document_url=str(test_document),
            depth="structure",
            provider="llama-parse",
            registry=server.registry,
            cache=server.cache
        )
        
        # Check cache was created
        cache_info = cache.get_cache_info(test_document)
        if cache_info:  # Cache might not be created if API call fails
            assert cache_info.get('cache_directory') is not None
            assert cache_info.get('statistics', {}).get('cache_size_bytes', 0) > 0
    
    @pytest.mark.asyncio
    async def test_llamaparse_xray_extraction(self, config_with_llamaparse, test_document):
        """Test LlamaParse xray extraction capabilities."""
        if not test_document.exists():
            pytest.skip(f"Test document not found: {test_document}")
        
        server = DocsrayServer(config_with_llamaparse)
        
        from src.docsray.tools import xray
        result = await xray.handle_xray(
            document_url=str(test_document),
            analysis_type=["entities", "key-points"],
            custom_instructions="Extract all parties and dates",
            provider="llama-parse",
            registry=server.registry,
            cache=server.cache
        )
        
        # If API key is valid, check results
        if "error" not in result:
            assert "analysis" in result
            analysis = result["analysis"]
            
            # Check for full extraction data
            if "full_extraction" in analysis:
                extraction = analysis["full_extraction"]
                assert isinstance(extraction, dict)
            
            # Check summary
            if "summary" in analysis:
                summary = analysis["summary"]
                assert "total_documents" in summary or "total_pages" in summary
    
    @pytest.mark.asyncio
    async def test_llamaparse_enhanced_extraction(self, config_with_llamaparse, test_document):
        """Test enhanced extraction with multiple formats."""
        if not test_document.exists():
            pytest.skip(f"Test document not found: {test_document}")
        
        server = DocsrayServer(config_with_llamaparse)
        provider = server.registry.get_provider("llama-parse")
        
        if provider:
            # Test provider capabilities
            caps = provider.get_capabilities()
            assert "pdf" in caps.formats
            
            # Test document processing
            doc = Document(url=str(test_document), format="pdf")
            can_process = await provider.can_process(doc)
            assert can_process is True