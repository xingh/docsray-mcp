"""Base provider interface for document processing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


@dataclass
class Document:
    """Document representation."""

    url: str
    path: Optional[Path] = None
    format: Optional[str] = None
    size: Optional[int] = None
    hash: Optional[str] = None
    has_scanned_content: bool = False
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ProviderCapabilities(BaseModel):
    """Provider capability definition."""

    formats: List[str]
    features: Dict[str, bool]
    performance: Dict[str, Union[int, float]]


class PeekResult(BaseModel):
    """Result from peek operation."""

    metadata: Dict[str, Any]
    structure: Optional[Dict[str, Any]] = None
    preview: Optional[Dict[str, Any]] = None


class SeekResult(BaseModel):
    """Result from seek operation."""

    location: Dict[str, Any]
    content: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class MapResult(BaseModel):
    """Result from map operation."""

    document_map: Dict[str, Any]
    statistics: Optional[Dict[str, Any]] = None


class XrayResult(BaseModel):
    """Result from xray operation."""

    analysis: Dict[str, Any]
    confidence: Optional[float] = None
    provider_info: Optional[Dict[str, Any]] = None


class ExtractResult(BaseModel):
    """Result from extract operation."""

    content: Union[str, Dict[str, Any], List[Any]]
    format: str
    pages_processed: Optional[List[int]] = None
    statistics: Optional[Dict[str, Any]] = None


class DocumentProvider(ABC):
    """Abstract base class for document providers."""

    @abstractmethod
    def get_name(self) -> str:
        """Get provider name."""
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats."""
        pass

    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Get provider capabilities."""
        pass

    @abstractmethod
    async def can_process(self, document: Document) -> bool:
        """Check if provider can process the document."""
        pass

    @abstractmethod
    async def peek(self, document: Document, options: Dict[str, Any]) -> PeekResult:
        """Get document overview without full extraction."""
        pass

    @abstractmethod
    async def map(self, document: Document, options: Dict[str, Any]) -> MapResult:
        """Generate document structure map."""
        pass

    @abstractmethod
    async def seek(self, document: Document, target: Dict[str, Any]) -> SeekResult:
        """Navigate to specific location in document."""
        pass

    @abstractmethod
    async def xray(self, document: Document, options: Dict[str, Any]) -> XrayResult:
        """Perform deep document analysis."""
        pass

    @abstractmethod
    async def extract(self, document: Document, options: Dict[str, Any]) -> ExtractResult:
        """Extract content from document."""
        pass

    @abstractmethod
    async def initialize(self, config: Any) -> None:
        """Initialize provider with configuration."""
        pass

    @abstractmethod
    async def dispose(self) -> None:
        """Cleanup provider resources."""
        pass
