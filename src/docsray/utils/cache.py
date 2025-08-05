"""Document caching utilities."""

import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CacheEntry:
    """Single cache entry."""

    def __init__(self, key: str, value: Any, metadata: Dict[str, Any]):
        self.key = key
        self.value = value
        self.metadata = metadata
        self.timestamp = time.time()
        self.access_count = 0

    def is_expired(self, ttl: int) -> bool:
        """Check if entry is expired."""
        return time.time() - self.timestamp > ttl

    def access(self) -> Any:
        """Access the entry and update stats."""
        self.access_count += 1
        return self.value


class DocumentCache:
    """Simple in-memory document cache."""

    def __init__(self, enabled: bool = True, ttl: int = 3600, max_size: int = 100):
        self.enabled = enabled
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    def generate_key(self, document_url: str, operation: str, options: Dict[str, Any]) -> str:
        """Generate cache key for a request."""
        normalized = {
            "url": document_url,
            "operation": operation,
            "options": self._normalize_options(options)
        }

        key_str = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None

        async with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired(self.ttl):
                logger.debug(f"Cache hit for key: {key[:8]}...")
                return entry.access()
            elif entry:
                # Remove expired entry
                del self._cache[key]

        return None

    async def set(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Set value in cache."""
        if not self.enabled:
            return

        async with self._lock:
            # Evict oldest entries if at capacity
            if len(self._cache) >= self.max_size:
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k].timestamp
                )
                del self._cache[oldest_key]

            self._cache[key] = CacheEntry(key, value, metadata or {})
            logger.debug(f"Cache set for key: {key[:8]}...")

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")

    def _normalize_options(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize options for consistent key generation."""
        # Remove non-deterministic values
        normalized = options.copy()
        for key in ["timestamp", "request_id", "session_id"]:
            normalized.pop(key, None)

        # Sort lists for consistency
        for key, value in normalized.items():
            if isinstance(value, list):
                normalized[key] = sorted(value)

        return normalized
