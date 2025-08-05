"""Tests for utility modules."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from docsray.utils.cache import DocumentCache
from docsray.utils.documents import (
    calculate_file_hash,
    get_document_format,
    is_url,
)
from docsray.utils.logging import setup_logging


class TestDocumentCache:
    """Test DocumentCache functionality."""
    
    @pytest.fixture
    def cache(self):
        return DocumentCache(enabled=True, ttl=60, max_size=10)
    
    def test_generate_key(self, cache):
        key1 = cache.generate_key("doc.pdf", "extract", {"format": "markdown"})
        key2 = cache.generate_key("doc.pdf", "extract", {"format": "markdown"})
        key3 = cache.generate_key("doc.pdf", "extract", {"format": "json"})
        
        assert key1 == key2  # Same inputs
        assert key1 != key3  # Different options
    
    @pytest.mark.asyncio
    async def test_cache_hit_miss(self, cache):
        key = "test_key"
        value = {"result": "data"}
        
        # Miss
        result = await cache.get(key)
        assert result is None
        
        # Set
        await cache.set(key, value)
        
        # Hit
        result = await cache.get(key)
        assert result == value
    
    @pytest.mark.asyncio
    async def test_cache_disabled(self):
        cache = DocumentCache(enabled=False)
        key = "test_key"
        value = {"result": "data"}
        
        await cache.set(key, value)
        result = await cache.get(key)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self):
        cache = DocumentCache(enabled=True, ttl=0)  # Instant expiration
        key = "test_key"
        value = {"result": "data"}
        
        await cache.set(key, value)
        await asyncio.sleep(0.1)
        
        result = await cache.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_eviction(self):
        cache = DocumentCache(enabled=True, ttl=60, max_size=2)
        
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")  # Should evict key1
        
        assert await cache.get("key1") is None
        assert await cache.get("key2") == "value2"
        assert await cache.get("key3") == "value3"
    
    @pytest.mark.asyncio
    async def test_cache_clear(self, cache):
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        
        await cache.clear()
        
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None


class TestDocumentUtils:
    """Test document utility functions."""
    
    def test_get_document_format_by_extension(self):
        assert get_document_format("test.pdf") == "pdf"
        assert get_document_format("document.docx") == "docx"
        assert get_document_format("/path/to/file.epub") == "epub"
        assert get_document_format("http://example.com/file.png") == "png"
    
    def test_get_document_format_unknown(self):
        assert get_document_format("test.unknown") is None
        assert get_document_format("noextension") is None
    
    def test_is_url(self):
        assert is_url("http://example.com/file.pdf") is True
        assert is_url("https://example.com/file.pdf") is True
        assert is_url("ftp://example.com/file.pdf") is True
        
        assert is_url("/path/to/file.pdf") is False
        assert is_url("file.pdf") is False
        assert is_url("C:\\path\\to\\file.pdf") is False
    
    def test_calculate_file_hash(self):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = Path(tmp.name)
        
        try:
            hash1 = calculate_file_hash(tmp_path)
            hash2 = calculate_file_hash(tmp_path)
            
            assert hash1 == hash2  # Same file, same hash
            assert len(hash1) == 64  # SHA-256 hex digest length
        finally:
            tmp_path.unlink()


class TestLogging:
    """Test logging setup."""
    
    def test_setup_logging_default(self):
        setup_logging()
        # Should not raise any exceptions
    
    def test_setup_logging_custom(self):
        setup_logging(level="DEBUG", format="%(message)s")
        # Should not raise any exceptions