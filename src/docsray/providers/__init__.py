"""Document providers for Docsray."""

from .base import DocumentProvider, ProviderCapabilities
from .registry import ProviderRegistry

__all__ = ["DocumentProvider", "ProviderCapabilities", "ProviderRegistry"]
