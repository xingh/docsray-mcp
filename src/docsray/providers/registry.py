"""Provider registry for managing document providers."""

import logging
from typing import Dict, List, Optional

from .base import Document, DocumentProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Registry for managing document providers."""

    def __init__(self):
        self._providers: Dict[str, DocumentProvider] = {}
        self._default_provider: Optional[str] = None

    def register(self, provider: DocumentProvider) -> None:
        """Register a provider.
        
        Args:
            provider: Provider instance to register
        """
        name = provider.get_name()
        if name in self._providers:
            logger.warning(f"Provider {name} already registered, overwriting")

        self._providers[name] = provider
        logger.info(f"Registered provider: {name}")

        # Set as default if first provider
        if not self._default_provider:
            self._default_provider = name

    def unregister(self, name: str) -> None:
        """Unregister a provider.
        
        Args:
            name: Provider name to unregister
        """
        if name in self._providers:
            del self._providers[name]
            logger.info(f"Unregistered provider: {name}")

            # Update default if needed
            if self._default_provider == name:
                self._default_provider = next(iter(self._providers), None)

    def get_provider(self, name: str) -> Optional[DocumentProvider]:
        """Get a provider by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance or None if not found
        """
        return self._providers.get(name)

    def list_providers(self) -> List[str]:
        """Get list of registered provider names.
        
        Returns:
            List of provider names
        """
        return list(self._providers.keys())

    def get_default_provider(self) -> Optional[DocumentProvider]:
        """Get the default provider.
        
        Returns:
            Default provider instance or None
        """
        if self._default_provider:
            return self._providers.get(self._default_provider)
        return None

    def set_default_provider(self, name: str) -> None:
        """Set the default provider.
        
        Args:
            name: Provider name to set as default
            
        Raises:
            ValueError: If provider not found
        """
        if name not in self._providers:
            raise ValueError(f"Provider {name} not found in registry")
        self._default_provider = name

    async def select_provider(
        self,
        document: Document,
        operation: str,
        user_preference: Optional[str] = None
    ) -> Optional[DocumentProvider]:
        """Select the best provider for a document and operation.
        
        Args:
            document: Document to process
            operation: Operation to perform
            user_preference: User's preferred provider
            
        Returns:
            Selected provider or None
        """
        # User preference takes precedence
        if user_preference and user_preference != "auto":
            provider = self.get_provider(user_preference)
            if provider and await provider.can_process(document):
                return provider
            logger.warning(
                f"Requested provider {user_preference} cannot process document, "
                "falling back to auto selection"
            )

        # Score providers
        candidates = []
        for name, provider in self._providers.items():
            if await provider.can_process(document):
                score = self._score_provider(provider, document, operation)
                candidates.append((score, provider))

        if not candidates:
            logger.error(f"No provider available for {document.format} documents")
            return None

        # Sort by score (highest first) and return best
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    def _score_provider(
        self,
        provider: DocumentProvider,
        document: Document,
        operation: str
    ) -> float:
        """Score a provider for a given document and operation.
        
        Args:
            provider: Provider to score
            document: Document to process
            operation: Operation to perform
            
        Returns:
            Score value
        """
        score = 0.0
        caps = provider.get_capabilities()

        # Format compatibility
        if document.format and document.format.lower() in caps.formats:
            score += 10.0

        # Operation-specific scoring
        if operation == "xray":
            if caps.features.get("customInstructions", False):
                score += 5.0
        elif operation == "extract":
            if document.has_scanned_content and caps.features.get("ocr", False):
                score += 8.0
            if caps.features.get("tables", False):
                score += 2.0
        elif operation == "map":
            if caps.features.get("streaming", False):
                score += 3.0

        # Performance scoring for large files
        if document.size and document.size > 10 * 1024 * 1024:  # 10MB
            avg_speed = caps.performance.get("averageSpeed", 0)
            score += min(avg_speed / 100, 5.0)  # Cap at 5 points

        return score
