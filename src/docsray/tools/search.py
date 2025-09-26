"""Search tool implementation for filesystem document search with coarse-to-fine methodology."""

import logging
import os
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
import fnmatch
import hashlib

from ..providers.base import Document
from ..providers.registry import ProviderRegistry
from ..utils.cache import DocumentCache
from ..utils.documents import get_document_format

logger = logging.getLogger(__name__)


class SearchResult:
    """Search result for a single document."""

    def __init__(
        self,
        file_path: str,
        relevance_score: float = 0.0,
        snippet: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.file_path = file_path
        self.relevance_score = relevance_score
        self.snippet = snippet or ""
        self.metadata = metadata or {}


class FilesystemSearchProvider:
    """Basic filesystem search provider implementing coarse-to-fine methodology."""

    def __init__(self):
        self.name = "filesystem"

    async def coarse_search(
        self,
        search_path: str,
        file_types: List[str],
        max_results: int
    ) -> List[str]:
        """Coarse search: Fast filesystem scanning for matching file types."""
        matching_files = []
        search_path = Path(os.path.expanduser(search_path)).resolve()

        if not search_path.exists():
            logger.warning(f"Search path does not exist: {search_path}")
            return []

        # Create file patterns for the requested types
        patterns = []
        for file_type in file_types:
            patterns.extend([f"*.{file_type}", f"*.{file_type.upper()}"])

        try:
            # Walk through directory tree
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    # Check if file matches any pattern
                    if any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                        full_path = os.path.join(root, file)
                        matching_files.append(full_path)

                        # Limit results for performance
                        if len(matching_files) >= max_results * 3:  # Get more for ranking
                            break

                if len(matching_files) >= max_results * 3:
                    break

        except Exception as e:
            logger.error(f"Error during coarse search: {e}")

        return matching_files[:max_results * 3]

    async def fine_search(
        self,
        query: str,
        file_paths: List[str],
        search_strategy: str,
        max_results: int
    ) -> List[SearchResult]:
        """Fine search: Content analysis and ranking."""
        results = []
        query_lower = query.lower()

        for file_path in file_paths:
            try:
                # Get file metadata
                stat = os.stat(file_path)
                file_size = stat.st_size

                # Skip very large files for performance
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    continue

                relevance_score = 0.0
                snippet = ""

                if search_strategy in ["keyword", "coarse-to-fine", "hybrid"]:
                    # Filename matching
                    filename = os.path.basename(file_path).lower()
                    if query_lower in filename:
                        relevance_score += 0.3

                    # Try to read file content for matching
                    try:
                        # Handle different encodings
                        encodings = ['utf-8', 'latin-1', 'cp1252']
                        content = ""

                        for encoding in encodings:
                            try:
                                with open(file_path, 'r', encoding=encoding) as f:
                                    content = f.read()[:10000]  # First 10KB for performance
                                break
                            except UnicodeDecodeError:
                                continue

                        if content:
                            content_lower = content.lower()

                            # Count query occurrences
                            query_count = content_lower.count(query_lower)
                            if query_count > 0:
                                relevance_score += min(query_count * 0.1, 0.7)  # Cap at 0.7

                                # Extract snippet around first occurrence
                                start_idx = content_lower.find(query_lower)
                                if start_idx >= 0:
                                    snippet_start = max(0, start_idx - 50)
                                    snippet_end = min(len(content), start_idx + len(query) + 50)
                                    snippet = content[snippet_start:snippet_end].strip()

                                    # Add ellipsis if truncated
                                    if snippet_start > 0:
                                        snippet = "..." + snippet
                                    if snippet_end < len(content):
                                        snippet = snippet + "..."

                    except Exception as e:
                        # For binary files or read errors, just use filename matching
                        logger.debug(f"Could not read content of {file_path}: {e}")
                        pass

                # Semantic search would go here if implemented
                if search_strategy == "semantic":
                    # Placeholder for semantic search - would need embeddings
                    relevance_score += 0.1

                # Only include results with some relevance
                if relevance_score > 0:
                    results.append(SearchResult(
                        file_path=file_path,
                        relevance_score=relevance_score,
                        snippet=snippet,
                        metadata={
                            "file_size": file_size,
                            "file_type": get_document_format(file_path),
                            "modified_time": stat.st_mtime
                        }
                    ))

            except Exception as e:
                logger.debug(f"Error processing file {file_path}: {e}")
                continue

        # Sort by relevance score (descending)
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:max_results]


async def handle_search(
    query: str,
    search_path: str,
    search_strategy: str,
    file_types: List[str],
    max_results: int,
    provider: str,
    registry: ProviderRegistry,
    cache: DocumentCache
) -> Dict[str, Any]:
    """Handle search operation using coarse-to-fine methodology.

    Args:
        query: Search query for finding documents
        search_path: Base path to search within
        search_strategy: Search strategy (coarse-to-fine, semantic, keyword, hybrid)
        file_types: File types to include in search
        max_results: Maximum number of results to return
        provider: Provider selection (auto, mimic-docsray, filesystem)
        registry: Provider registry
        cache: Document cache

    Returns:
        Search result dictionary
    """
    try:
        # Generate cache key
        cache_key = cache.generate_key("search", "filesystem_search", {
            "query": query,
            "search_path": search_path,
            "search_strategy": search_strategy,
            "file_types": sorted(file_types),
            "max_results": max_results,
            "provider": provider
        })

        # Check cache
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached search results for query: {query}")
            return cached_result

        # Validate and normalize search path
        search_path = os.path.expanduser(search_path)
        if not os.path.exists(search_path):
            return {
                "error": f"Search path does not exist: {search_path}",
                "suggestion": "Please provide a valid directory path"
            }

        if not os.path.isdir(search_path):
            return {
                "error": f"Search path is not a directory: {search_path}",
                "suggestion": "Please provide a directory path, not a file path"
            }

        # Initialize filesystem search provider
        fs_provider = FilesystemSearchProvider()

        logger.info(f"Starting coarse-to-fine search for query: '{query}' in {search_path}")

        # Phase 1: Coarse search - Fast filesystem scanning
        logger.debug("Phase 1: Coarse search - scanning filesystem")
        candidate_files = await fs_provider.coarse_search(
            search_path=search_path,
            file_types=file_types,
            max_results=max_results
        )

        if not candidate_files:
            return {
                "results": [],
                "total_found": 0,
                "search_strategy": search_strategy,
                "search_path": search_path,
                "message": f"No {', '.join(file_types)} files found in the specified path"
            }

        logger.debug(f"Coarse search found {len(candidate_files)} candidate files")

        # Phase 2: Fine search - Content analysis and ranking
        logger.debug("Phase 2: Fine search - analyzing content and ranking")
        search_results = await fs_provider.fine_search(
            query=query,
            file_paths=candidate_files,
            search_strategy=search_strategy,
            max_results=max_results
        )

        # Format results
        formatted_results = []
        for result in search_results:
            # Make path relative to search_path for cleaner display
            try:
                relative_path = os.path.relpath(result.file_path, search_path)
            except ValueError:
                # If paths are on different drives (Windows), use absolute path
                relative_path = result.file_path

            formatted_results.append({
                "file_path": result.file_path,
                "relative_path": relative_path,
                "relevance_score": round(result.relevance_score, 3),
                "snippet": result.snippet,
                "metadata": result.metadata
            })

        response = {
            "results": formatted_results,
            "total_found": len(formatted_results),
            "search_strategy": search_strategy,
            "search_path": search_path,
            "query": query,
            "file_types": file_types,
            "provider": "filesystem"
        }

        # Add search statistics
        response["statistics"] = {
            "coarse_search_candidates": len(candidate_files),
            "fine_search_results": len(search_results),
            "search_strategy_used": search_strategy
        }

        # Cache the results
        await cache.set(cache_key, response, {
            "provider": "filesystem",
            "operation": "search"
        })

        logger.info(f"Search completed: found {len(formatted_results)} relevant documents")
        return response

    except Exception as e:
        logger.error(f"Error in search operation: {e}")
        return {
            "error": str(e),
            "type": type(e).__name__,
            "suggestion": "Please check your search parameters and try again"
        }