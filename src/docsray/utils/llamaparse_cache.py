"""LlamaParse extraction cache management.

This module handles caching of LlamaParse extraction results to avoid redundant API calls
and preserve all extracted information including text, images, tables, and metadata.
"""

import hashlib
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class LlamaParseCache:
    """Manages caching of LlamaParse extraction results."""
    
    def __init__(self, cache_root: Optional[Path] = None):
        """Initialize the LlamaParse cache.
        
        Args:
            cache_root: Root directory for cache storage. Defaults to tests/tmp
        """
        self.cache_root = cache_root or Path("/workspace/docsray-mcp/tests/tmp")
        self.cache_root.mkdir(parents=True, exist_ok=True)
        logger.info(f"LlamaParse cache initialized at: {self.cache_root}")
    
    def get_cache_dir(self, document_path: Path) -> Path:
        """Get the cache directory for a document.
        
        Args:
            document_path: Path to the document
            
        Returns:
            Path to the cache directory (document_name.docsray)
        """
        # Use document name and hash for unique identification
        doc_hash = self._compute_document_hash(document_path)
        cache_dir_name = f"{document_path.stem}.{doc_hash[:8]}.docsray"
        cache_dir = self.cache_root / cache_dir_name
        return cache_dir
    
    def _compute_document_hash(self, document_path: Path) -> str:
        """Compute hash of document for cache key.
        
        Args:
            document_path: Path to document
            
        Returns:
            SHA256 hash of document content
        """
        if document_path.exists():
            with open(document_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        else:
            # For URLs or non-existent paths, hash the path itself
            return hashlib.sha256(str(document_path).encode()).hexdigest()
    
    async def store_extraction(self, document_path: Path, extraction_result: Dict[str, Any], 
                              parsing_instruction: Optional[str] = None) -> Path:
        """Store LlamaParse extraction results in cache.
        
        Args:
            document_path: Path to the original document
            extraction_result: The full extraction result from LlamaParse
            parsing_instruction: The instruction used for parsing (for cache key)
            
        Returns:
            Path to the cache directory
        """
        cache_dir = self.get_cache_dir(document_path)
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Storing LlamaParse extraction cache at: {cache_dir}")
        
        # Store metadata
        metadata = {
            "original_document": str(document_path),
            "document_hash": self._compute_document_hash(document_path),
            "extraction_timestamp": datetime.now().isoformat(),
            "parsing_instruction": parsing_instruction,
            "llamaparse_version": "latest",  # Could be enhanced to track actual version
            "cache_version": "1.0"
        }
        
        with open(cache_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Store the full extraction result
        with open(cache_dir / "extraction_result.json", "w") as f:
            json.dump(extraction_result, f, indent=2)
        
        # Store pages separately for easier access
        pages_dir = cache_dir / "pages"
        pages_dir.mkdir(exist_ok=True)
        
        for page in extraction_result.get("pages", []):
            page_num = page.get("page_num", 1)
            
            # Store page text
            with open(pages_dir / f"page_{page_num:03d}.txt", "w") as f:
                f.write(page.get("text", ""))
            
            # Store page markdown
            with open(pages_dir / f"page_{page_num:03d}.md", "w") as f:
                f.write(page.get("markdown", ""))
            
            # Store page metadata
            if page.get("metadata"):
                with open(pages_dir / f"page_{page_num:03d}_metadata.json", "w") as f:
                    json.dump(page["metadata"], f, indent=2)
            
            # Store layout if available
            if page.get("layout"):
                with open(pages_dir / f"page_{page_num:03d}_layout.json", "w") as f:
                    json.dump(page["layout"], f, indent=2)
        
        # Store images
        if extraction_result.get("images"):
            images_dir = cache_dir / "images"
            images_dir.mkdir(exist_ok=True)
            
            with open(images_dir / "images_index.json", "w") as f:
                json.dump(extraction_result["images"], f, indent=2)
            
            # If image data is available, store separately
            for i, img in enumerate(extraction_result["images"]):
                if img.get("data"):
                    # Store image data (base64 or binary)
                    with open(images_dir / f"image_{i:03d}.data", "w") as f:
                        f.write(str(img["data"]))
        
        # Store tables
        if extraction_result.get("tables"):
            tables_dir = cache_dir / "tables"
            tables_dir.mkdir(exist_ok=True)
            
            with open(tables_dir / "tables_index.json", "w") as f:
                json.dump(extraction_result["tables"], f, indent=2)
            
            # Store individual tables
            for i, table in enumerate(extraction_result["tables"]):
                if table.get("html"):
                    with open(tables_dir / f"table_{i:03d}.html", "w") as f:
                        f.write(table["html"])
                
                if table.get("data"):
                    with open(tables_dir / f"table_{i:03d}.json", "w") as f:
                        json.dump(table["data"], f, indent=2)
        
        # Copy original document to cache
        if document_path.exists():
            shutil.copy2(document_path, cache_dir / f"original{document_path.suffix}")
        
        # Store the raw documents list if available
        if extraction_result.get("documents"):
            with open(cache_dir / "documents.json", "w") as f:
                json.dump(extraction_result["documents"], f, indent=2)
        
        logger.info(f"Cache stored successfully with {len(extraction_result.get('pages', []))} pages, "
                   f"{len(extraction_result.get('images', []))} images, "
                   f"{len(extraction_result.get('tables', []))} tables")
        
        return cache_dir
    
    async def retrieve_extraction(self, document_path: Path, 
                                 parsing_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve cached LlamaParse extraction if available.
        
        Args:
            document_path: Path to the document
            parsing_instruction: The parsing instruction to match (optional)
            
        Returns:
            Cached extraction result or None if not found/invalid
        """
        cache_dir = self.get_cache_dir(document_path)
        
        if not cache_dir.exists():
            logger.debug(f"No cache found for {document_path}")
            return None
        
        # Check metadata
        metadata_path = cache_dir / "metadata.json"
        if not metadata_path.exists():
            logger.warning(f"Cache directory exists but no metadata found: {cache_dir}")
            return None
        
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        # Verify document hash matches (ensure document hasn't changed)
        current_hash = self._compute_document_hash(document_path)
        if metadata.get("document_hash") != current_hash:
            logger.info(f"Document has changed, cache invalid for {document_path}")
            return None
        
        # Check if parsing instruction matches (if specified)
        if parsing_instruction and metadata.get("parsing_instruction") != parsing_instruction:
            logger.info(f"Parsing instruction mismatch, cache invalid for {document_path}")
            return None
        
        # Load extraction result
        extraction_path = cache_dir / "extraction_result.json"
        if not extraction_path.exists():
            logger.warning(f"No extraction result found in cache: {cache_dir}")
            return None
        
        with open(extraction_path) as f:
            extraction_result = json.load(f)
        
        logger.info(f"Retrieved cached extraction for {document_path} from {cache_dir}")
        logger.info(f"Cache contains {len(extraction_result.get('pages', []))} pages, "
                   f"{len(extraction_result.get('images', []))} images, "
                   f"{len(extraction_result.get('tables', []))} tables")
        
        return extraction_result
    
    async def get_cached_extraction(self, document_path: Path, parsing_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Async wrapper for retrieve_extraction for compatibility."""
        return await self.retrieve_extraction(document_path, parsing_instruction)
    
    def clear_cache(self, document_path: Optional[Path] = None) -> int:
        """Clear cache for a specific document or all cached data.
        
        Args:
            document_path: Specific document to clear cache for, or None for all
            
        Returns:
            Number of cache directories removed
        """
        count = 0
        
        if document_path:
            # Clear specific document cache
            cache_dir = self.get_cache_dir(document_path)
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                logger.info(f"Cleared cache for {document_path}")
                count = 1
        else:
            # Clear all caches
            for cache_dir in self.cache_root.glob("*.docsray"):
                shutil.rmtree(cache_dir)
                count += 1
            logger.info(f"Cleared {count} cache directories")
        
        return count
    
    def list_cached_documents(self) -> list[Dict[str, Any]]:
        """List all cached documents with their metadata.
        
        Returns:
            List of cached document information
        """
        cached_docs = []
        
        for cache_dir in self.cache_root.glob("*.docsray"):
            metadata_path = cache_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path) as f:
                    metadata = json.load(f)
                
                # Calculate cache size
                cache_size = sum(f.stat().st_size for f in cache_dir.rglob("*") if f.is_file())
                
                cached_docs.append({
                    "cache_dir": str(cache_dir),
                    "original_document": metadata.get("original_document"),
                    "extraction_timestamp": metadata.get("extraction_timestamp"),
                    "cache_size_bytes": cache_size,
                    "cache_size_mb": round(cache_size / (1024 * 1024), 2)
                })
        
        return cached_docs
    
    def get_cache_info(self, document_path: Path) -> Optional[Dict[str, Any]]:
        """Get detailed information about cached data for a document.
        
        Args:
            document_path: Path to the document
            
        Returns:
            Detailed cache information or None if not cached
        """
        cache_dir = self.get_cache_dir(document_path)
        
        if not cache_dir.exists():
            return None
        
        metadata_path = cache_dir / "metadata.json"
        if not metadata_path.exists():
            return None
        
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        # Count cached items
        pages_count = len(list((cache_dir / "pages").glob("page_*.txt"))) if (cache_dir / "pages").exists() else 0
        images_count = 0
        tables_count = 0
        
        if (cache_dir / "images" / "images_index.json").exists():
            with open(cache_dir / "images" / "images_index.json") as f:
                images_count = len(json.load(f))
        
        if (cache_dir / "tables" / "tables_index.json").exists():
            with open(cache_dir / "tables" / "tables_index.json") as f:
                tables_count = len(json.load(f))
        
        # Calculate cache size
        cache_size = sum(f.stat().st_size for f in cache_dir.rglob("*") if f.is_file())
        
        return {
            "cache_directory": str(cache_dir),
            "metadata": metadata,
            "statistics": {
                "pages": pages_count,
                "images": images_count,
                "tables": tables_count,
                "cache_size_bytes": cache_size,
                "cache_size_mb": round(cache_size / (1024 * 1024), 2)
            }
        }