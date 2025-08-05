"""Pytest configuration and fixtures."""

import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio

from docsray.config import DocsrayConfig
from docsray.providers.base import Document
from docsray.providers.registry import ProviderRegistry
from docsray.server import DocsrayServer
from docsray.utils.cache import DocumentCache


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config() -> DocsrayConfig:
    """Create test configuration."""
    return DocsrayConfig(
        transport={"type": "stdio"},
        providers={
            "default": "pymupdf4llm",
            "pymupdf4llm": {"enabled": True}
        },
        performance={
            "cache_enabled": True,
            "cache_ttl": 60,
            "max_concurrent_requests": 5,
            "timeout_seconds": 30
        },
        log_level="DEBUG"
    )


@pytest_asyncio.fixture
async def server(test_config: DocsrayConfig) -> AsyncGenerator[DocsrayServer, None]:
    """Create test server instance."""
    server = DocsrayServer(test_config)
    yield server
    await server.shutdown()


@pytest.fixture
def registry() -> ProviderRegistry:
    """Create test provider registry."""
    return ProviderRegistry()


@pytest.fixture
def cache() -> DocumentCache:
    """Create test document cache."""
    return DocumentCache(enabled=True, ttl=60)


@pytest.fixture
def sample_pdf() -> Generator[Path, None, None]:
    """Create a sample PDF file for testing."""
    import fitz  # PyMuPDF
    
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        # Create a simple PDF
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Test Document")
        page.insert_text((50, 100), "This is page 1 content.")
        
        page2 = doc.new_page()
        page2.insert_text((50, 50), "Page 2")
        page2.insert_text((50, 100), "This is page 2 content.")
        
        doc.save(tmp.name)
        doc.close()
        
        yield Path(tmp.name)
        
    # Cleanup
    Path(tmp.name).unlink(missing_ok=True)


@pytest.fixture
def sample_document(sample_pdf: Path) -> Document:
    """Create a sample document object."""
    return Document(
        url=str(sample_pdf),
        path=sample_pdf,
        format="pdf",
        size=sample_pdf.stat().st_size
    )


@pytest.fixture
def mock_provider():
    """Create a mock provider for testing."""
    from unittest.mock import AsyncMock, Mock
    
    from docsray.providers.base import (
        DocumentProvider,
        ExtractResult,
        MapResult,
        PeekResult,
        ProviderCapabilities,
        SeekResult,
        XrayResult,
    )
    
    class MockProvider(DocumentProvider):
        def __init__(self):
            self.name = "mock"
            self.initialized = False
        
        def get_name(self) -> str:
            return self.name
        
        def get_supported_formats(self) -> list[str]:
            return ["pdf", "txt", "docx"]
        
        def get_capabilities(self) -> ProviderCapabilities:
            return ProviderCapabilities(
                formats=self.get_supported_formats(),
                features={
                    "ocr": True,
                    "tables": True,
                    "images": True,
                    "forms": False,
                    "multiLanguage": True,
                    "streaming": False,
                    "customInstructions": True
                },
                performance={
                    "maxFileSize": 100 * 1024 * 1024,
                    "averageSpeed": 50
                }
            )
        
        async def can_process(self, document: Document) -> bool:
            return document.format in self.get_supported_formats()
        
        async def peek(self, document: Document, options: dict) -> PeekResult:
            return PeekResult(
                metadata={"title": "Test Document", "pageCount": 2},
                structure={"hasImages": False, "hasTables": False},
                preview={"firstPageText": "Test content"}
            )
        
        async def map(self, document: Document, options: dict) -> MapResult:
            return MapResult(
                document_map={
                    "hierarchy": {"root": {"type": "document", "children": []}}
                },
                statistics={"totalPages": 2}
            )
        
        async def seek(self, document: Document, target: dict) -> SeekResult:
            return SeekResult(
                location={"page": 1, "type": "page"},
                content="Test content",
                context={"totalPages": 2}
            )
        
        async def xray(self, document: Document, options: dict) -> XrayResult:
            return XrayResult(
                analysis={"entities": [], "key_points": []},
                confidence=0.9
            )
        
        async def extract(self, document: Document, options: dict) -> ExtractResult:
            return ExtractResult(
                content="# Test Document\n\nTest content",
                format="markdown",
                pages_processed=[1, 2],
                statistics={"pagesExtracted": 2}
            )
        
        async def initialize(self, config) -> None:
            self.initialized = True
        
        async def dispose(self) -> None:
            self.initialized = False
    
    return MockProvider()