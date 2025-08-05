"""Tests for provider modules."""

import pytest

from docsray.providers.base import Document
from docsray.providers.registry import ProviderRegistry


class TestProviderRegistry:
    """Test ProviderRegistry functionality."""
    
    @pytest.fixture
    def registry_with_providers(self, registry, mock_provider):
        """Registry with mock providers."""
        registry.register(mock_provider)
        return registry
    
    def test_register_provider(self, registry, mock_provider):
        assert len(registry.list_providers()) == 0
        
        registry.register(mock_provider)
        
        assert len(registry.list_providers()) == 1
        assert "mock" in registry.list_providers()
    
    def test_register_duplicate(self, registry, mock_provider):
        registry.register(mock_provider)
        registry.register(mock_provider)  # Should overwrite
        
        assert len(registry.list_providers()) == 1
    
    def test_unregister_provider(self, registry_with_providers):
        registry_with_providers.unregister("mock")
        
        assert len(registry_with_providers.list_providers()) == 0
        assert registry_with_providers.get_provider("mock") is None
    
    def test_get_provider(self, registry_with_providers, mock_provider):
        provider = registry_with_providers.get_provider("mock")
        
        assert provider is mock_provider
        assert provider.get_name() == "mock"
    
    def test_get_nonexistent_provider(self, registry):
        provider = registry.get_provider("nonexistent")
        assert provider is None
    
    def test_default_provider(self, registry, mock_provider):
        # First registered becomes default
        registry.register(mock_provider)
        
        default = registry.get_default_provider()
        assert default is mock_provider
    
    def test_set_default_provider(self, registry_with_providers, mock_provider):
        # Create another provider
        mock_provider2 = mock_provider
        mock_provider2.name = "mock2"
        registry_with_providers.register(mock_provider2)
        
        registry_with_providers.set_default_provider("mock2")
        
        default = registry_with_providers.get_default_provider()
        assert default.get_name() == "mock2"
    
    def test_set_invalid_default(self, registry):
        with pytest.raises(ValueError):
            registry.set_default_provider("nonexistent")
    
    @pytest.mark.asyncio
    async def test_select_provider_user_preference(
        self, registry_with_providers, sample_document
    ):
        provider = await registry_with_providers.select_provider(
            sample_document, "extract", "mock"
        )
        
        assert provider is not None
        assert provider.get_name() == "mock"
    
    @pytest.mark.asyncio
    async def test_select_provider_auto(
        self, registry_with_providers, sample_document
    ):
        provider = await registry_with_providers.select_provider(
            sample_document, "extract", "auto"
        )
        
        assert provider is not None
        assert provider.get_name() == "mock"
    
    @pytest.mark.asyncio
    async def test_select_provider_no_match(self, registry_with_providers):
        # Document with unsupported format
        doc = Document(url="test.xyz", format="xyz")
        
        provider = await registry_with_providers.select_provider(
            doc, "extract", "auto"
        )
        
        assert provider is None
    
    def test_score_provider(self, registry_with_providers, mock_provider):
        doc = Document(url="test.pdf", format="pdf", size=50 * 1024 * 1024)
        
        score = registry_with_providers._score_provider(
            mock_provider, doc, "extract"
        )
        
        # Format match (10) + tables (2) + performance bonus (0.5)
        assert score == 12.5


class TestDocument:
    """Test Document class."""
    
    def test_document_creation(self):
        doc = Document(
            url="http://example.com/test.pdf",
            format="pdf",
            size=1024
        )
        
        assert doc.url == "http://example.com/test.pdf"
        assert doc.format == "pdf"
        assert doc.size == 1024
        assert doc.metadata == {}
    
    def test_document_defaults(self):
        doc = Document(url="test.pdf")
        
        assert doc.path is None
        assert doc.format is None
        assert doc.size is None
        assert doc.hash is None
        assert doc.has_scanned_content is False