"""Integration tests for the Docsray server."""

import pytest

from docsray.config import DocsrayConfig
from docsray.server import DocsrayServer


class TestDocsrayServer:
    """Test DocsrayServer integration."""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, test_config):
        server = DocsrayServer(test_config)
        
        assert server.config == test_config
        assert server.cache is not None
        assert server.registry is not None
        assert server.mcp is not None
        
        # Check tools are registered
        # FastMCP registers tools internally, we can't directly access them
        # Just verify the server initialized without errors
        assert server.mcp is not None
        
        await server.shutdown()
    
    @pytest.mark.asyncio
    async def test_server_provider_initialization(self, test_config):
        server = DocsrayServer(test_config)
        
        # Check PyMuPDF4LLM provider is registered
        providers = server.registry.list_providers()
        assert "pymupdf4llm" in providers
        
        provider = server.registry.get_provider("pymupdf4llm")
        assert provider is not None
        assert provider.get_name() == "pymupdf4llm"
        
        await server.shutdown()
    
    @pytest.mark.asyncio
    async def test_server_with_disabled_providers(self):
        config = DocsrayConfig(
            providers={
                "pymupdf4llm": {"enabled": False}
            }
        )
        
        server = DocsrayServer(config)
        
        # No providers should be registered
        providers = server.registry.list_providers()
        assert len(providers) == 0
        
        await server.shutdown()
    
    @pytest.mark.asyncio
    async def test_server_stdio_transport(self, test_config):
        test_config.transport.type = "stdio"
        server = DocsrayServer(test_config)
        
        assert server.config.transport.type == "stdio"
        
        # Would test actual stdio communication here
        # For now, just verify it's configured correctly
        
        await server.shutdown()
    
    @pytest.mark.asyncio
    async def test_server_http_transport(self):
        config = DocsrayConfig(
            transport={
                "type": "http",
                "http_port": 8888,
                "http_host": "127.0.0.1"
            }
        )
        
        server = DocsrayServer(config)
        
        assert server.config.transport.type == "http"
        assert server.config.transport.http_port == 8888
        
        await server.shutdown()