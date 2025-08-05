"""PyMuPDF4LLM provider implementation."""

import hashlib
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import pymupdf4llm

from ..config import PyMuPDFConfig
from ..utils.documents import download_document, get_document_format, get_local_document, is_url
from .base import (
    Document,
    DocumentProvider,
    ExtractResult,
    MapResult,
    PeekResult,
    ProviderCapabilities,
    SeekResult,
    XrayResult,
)

logger = logging.getLogger(__name__)


class PyMuPDF4LLMProvider(DocumentProvider):
    """Document provider using PyMuPDF4LLM."""

    def __init__(self):
        self.config: Optional[PyMuPDFConfig] = None
        self._initialized = False

    def get_name(self) -> str:
        return "pymupdf4llm"

    def get_supported_formats(self) -> List[str]:
        return ["pdf", "xps", "epub", "cbz", "svg"]

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            formats=self.get_supported_formats(),
            features={
                "ocr": False,
                "tables": True,
                "images": True,
                "forms": True,
                "multiLanguage": True,
                "streaming": True,
                "customInstructions": False,
            },
            performance={
                "maxFileSize": 500 * 1024 * 1024,  # 500MB
                "averageSpeed": 100,  # pages per second
            }
        )

    async def can_process(self, document: Document) -> bool:
        """Check if provider can process the document."""
        if not self._initialized:
            return False

        # Check format
        doc_format = document.format or get_document_format(document.url)
        if doc_format and doc_format.lower() not in self.get_supported_formats():
            return False

        # Check size limit
        if document.size:
            max_size = self.get_capabilities().performance["maxFileSize"]
            if document.size > max_size:
                return False

        return True

    async def peek(self, document: Document, options: Dict[str, Any]) -> PeekResult:
        """Get document overview."""
        doc_path = await self._ensure_local_document(document)
        depth = options.get("depth", "structure")

        # Extract basic metadata
        metadata = {}
        structure = {}
        preview = {}

        try:
            # Get document info using pymupdf4llm
            md_text = pymupdf4llm.to_markdown(
                str(doc_path),
                page_chunks=True,
                write_images=False,
                pages=[0]  # Just first page for preview
            )

            # Parse metadata from first chunk
            if md_text and isinstance(md_text, list) and len(md_text) > 0:
                first_chunk = md_text[0]
                metadata.update({
                    "pageCount": first_chunk.get("metadata", {}).get("total_pages", 0),
                    "format": document.format or "PDF",
                    "fileSize": document.size,
                })

                if depth in ["structure", "preview"]:
                    # Extract structure info
                    structure = {
                        "hasImages": first_chunk.get("metadata", {}).get("has_images", False),
                        "hasTables": first_chunk.get("metadata", {}).get("has_tables", False),
                        "sections": [],  # Would need more processing
                    }

                if depth == "preview":
                    preview = {
                        "firstPageText": first_chunk.get("text", "")[:500],
                        "tableOfContents": []  # Would need TOC extraction
                    }

        except Exception as e:
            logger.error(f"Error peeking document: {e}")
            raise

        return PeekResult(
            metadata=metadata,
            structure=structure if depth in ["structure", "preview"] else None,
            preview=preview if depth == "preview" else None
        )

    async def map(self, document: Document, options: Dict[str, Any]) -> MapResult:
        """Generate document structure map."""
        doc_path = await self._ensure_local_document(document)
        include_content = options.get("include_content", False)
        analysis_depth = options.get("analysis_depth", "deep")

        try:
            # Extract full document with chunks
            # Note: write_images saves to current directory, so we disable it for now
            # TODO: Configure image output directory or handle images differently
            chunks = pymupdf4llm.to_markdown(
                str(doc_path),
                page_chunks=True,
                write_images=False,  # Disabled to prevent cluttering root directory
                extract_words=True
            )

            # Build document map
            document_map = {
                "hierarchy": {
                    "root": {
                        "type": "document",
                        "title": Path(doc_path).stem,
                        "children": []
                    }
                },
                "resources": {
                    "images": [],
                    "tables": [],
                },
                "crossReferences": []
            }

            # Process chunks to build structure
            for i, chunk in enumerate(chunks):
                page_num = chunk.get("metadata", {}).get("page", i + 1)

                # Add page as section
                page_section = {
                    "type": "page",
                    "title": f"Page {page_num}",
                    "page": page_num,
                    "children": []
                }

                if include_content:
                    page_section["content"] = chunk.get("text", "")[:200]

                document_map["hierarchy"]["root"]["children"].append(page_section)

                # Extract resources if deep analysis
                if analysis_depth in ["deep", "comprehensive"]:
                    # Images would be in chunk metadata
                    if chunk.get("metadata", {}).get("images"):
                        for img in chunk["metadata"]["images"]:
                            document_map["resources"]["images"].append({
                                "id": f"img-{page_num}-{len(document_map['resources']['images'])}",
                                "page": page_num,
                                "caption": img.get("caption", ""),
                            })

            # Add statistics
            statistics = {
                "totalPages": len(chunks),
                "totalImages": len(document_map["resources"]["images"]),
                "totalTables": len(document_map["resources"]["tables"]),
            }

        except Exception as e:
            logger.error(f"Error mapping document: {e}")
            raise

        return MapResult(
            document_map=document_map,
            statistics=statistics
        )

    async def seek(self, document: Document, target: Dict[str, Any]) -> SeekResult:
        """Navigate to specific location in document."""
        doc_path = await self._ensure_local_document(document)

        try:
            # Determine target page
            target_page = None
            if "page" in target:
                target_page = target["page"] - 1  # Convert to 0-based
            elif "section" in target:
                # Would need section mapping
                target_page = 0
            elif "query" in target:
                # Would need text search
                target_page = 0

            # Extract target page
            if target_page is not None:
                chunks = pymupdf4llm.to_markdown(
                    str(doc_path),
                    page_chunks=True,
                    pages=[target_page]
                )

                if chunks:
                    content = chunks[0].get("text", "")
                    location = {
                        "page": target_page + 1,
                        "type": "page"
                    }
                    context = {
                        "totalPages": chunks[0].get("metadata", {}).get("total_pages", 0),
                        "hasNext": target_page + 1 < chunks[0].get("metadata", {}).get("total_pages", 0),
                        "hasPrevious": target_page > 0
                    }

                    return SeekResult(
                        location=location,
                        content=content,
                        context=context
                    )

        except Exception as e:
            logger.error(f"Error seeking in document: {e}")
            raise

        return SeekResult(
            location={"page": 1, "type": "page"},
            content="",
            context={}
        )

    async def xray(self, document: Document, options: Dict[str, Any]) -> XrayResult:
        """Perform deep document analysis."""
        # PyMuPDF4LLM doesn't support AI analysis
        # This would be handled by AI providers
        return XrayResult(
            analysis={
                "error": "PyMuPDF4LLM does not support AI-powered analysis. "
                         "Please use mistral-ocr or llama-parse providers."
            },
            confidence=0.0,
            provider_info={"name": self.get_name(), "supports_xray": False}
        )

    async def extract(self, document: Document, options: Dict[str, Any]) -> ExtractResult:
        """Extract content from document."""
        doc_path = await self._ensure_local_document(document)
        extraction_targets = options.get("extraction_targets", ["text"])
        output_format = options.get("output_format", "markdown")
        pages = options.get("pages")

        try:
            # Configure extraction
            extract_kwargs = {
                "page_chunks": True,
                "write_images": False,  # We'll handle images separately if needed
                "extract_words": True,
            }

            if pages:
                # Convert to 0-based page numbers
                extract_kwargs["pages"] = [p - 1 for p in pages]

            # If images are requested, extract in a temporary directory
            if "images" in extraction_targets:
                with tempfile.TemporaryDirectory(prefix="pymupdf_images_") as temp_dir:
                    # Save current directory
                    original_dir = os.getcwd()
                    try:
                        # Change to temp directory for image extraction
                        os.chdir(temp_dir)
                        extract_kwargs["write_images"] = True
                        chunks = pymupdf4llm.to_markdown(str(doc_path), **extract_kwargs)
                        
                        # Collect image files created
                        image_files = list(Path(temp_dir).glob("*.png"))
                        logger.info(f"Extracted {len(image_files)} images to temporary directory")
                        
                        # TODO: Process images if needed (e.g., move to cache)
                    finally:
                        # Always restore original directory
                        os.chdir(original_dir)
            else:
                # Extract without images
                chunks = pymupdf4llm.to_markdown(str(doc_path), **extract_kwargs)

            # Process based on output format
            if output_format == "markdown":
                # Combine chunks into markdown
                content = "\n\n".join([chunk.get("text", "") for chunk in chunks])
            elif output_format == "json":
                # Return structured data
                content = {
                    "pages": [
                        {
                            "page": chunk.get("metadata", {}).get("page", i + 1),
                            "text": chunk.get("text", ""),
                            "metadata": chunk.get("metadata", {})
                        }
                        for i, chunk in enumerate(chunks)
                    ]
                }
            else:  # structured
                content = chunks

            # Get pages processed
            pages_processed = []
            for chunk in chunks:
                page = chunk.get("metadata", {}).get("page")
                if page:
                    pages_processed.append(page)

            statistics = {
                "pagesExtracted": len(pages_processed),
                "charactersExtracted": sum(len(chunk.get("text", "")) for chunk in chunks),
            }

        except Exception as e:
            logger.error(f"Error extracting from document: {e}")
            raise

        return ExtractResult(
            content=content,
            format=output_format,
            pages_processed=pages_processed,
            statistics=statistics
        )

    async def initialize(self, config: PyMuPDFConfig) -> None:
        """Initialize provider with configuration."""
        self.config = config
        self._initialized = True
        logger.info("PyMuPDF4LLM provider initialized")

    async def dispose(self) -> None:
        """Cleanup provider resources."""
        self._initialized = False
        logger.info("PyMuPDF4LLM provider disposed")

    async def _ensure_local_document(self, document: Document) -> Path:
        """Ensure document is available locally.
        
        Args:
            document: Document to process
            
        Returns:
            Path to local document file
        """
        # If we already have a local path, use it
        if document.path and document.path.exists():
            return document.path

        # Check if it's a local file path
        local_path = await get_local_document(document.url)
        if local_path:
            document.path = local_path
            # Calculate hash if not present
            if not document.hash:
                with open(local_path, "rb") as f:
                    document.hash = hashlib.sha256(f.read()).hexdigest()
            return local_path

        # It's a URL, download it
        if is_url(document.url):
            local_path = await download_document(document.url)
            document.path = local_path

            # Calculate hash if not present
            if not document.hash:
                with open(local_path, "rb") as f:
                    document.hash = hashlib.sha256(f.read()).hexdigest()

            return local_path
        
        # Should not reach here, but raise error if we do
        raise ValueError(f"Unable to process document: {document.url}")
