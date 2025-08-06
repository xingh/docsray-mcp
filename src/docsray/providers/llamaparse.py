"""LlamaParse provider implementation for advanced document parsing."""

import asyncio
import hashlib
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from llama_parse import LlamaParse

from ..config import LlamaParseConfig
from ..utils.documents import download_document, get_document_format, get_local_document, is_url
from ..utils.llamaparse_cache import LlamaParseCache
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


class LlamaParseProvider(DocumentProvider):
    """Document provider using LlamaParse for advanced AI-powered parsing."""

    def __init__(self):
        self.config: Optional[LlamaParseConfig] = None
        self._initialized = False
        self.parser: Optional[LlamaParse] = None
        self.cache = LlamaParseCache()  # Initialize cache manager

    def get_name(self) -> str:
        return "llama-parse"

    def get_supported_formats(self) -> List[str]:
        return [
            "pdf", "docx", "pptx", "xlsx", "html", "xml", "json", "csv", "tsv",
            "md", "rst", "rtf", "txt", "epub", "eml", "msg", "org", "odt", "ods", "odp"
        ]

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            formats=self.get_supported_formats(),
            features={
                "ocr": True,
                "tables": True,
                "images": True,
                "forms": True,
                "multiLanguage": True,
                "streaming": False,
                "customInstructions": True,
                "imageExtraction": True,  # Can extract images
                "layoutPreservation": True,  # Preserves document layout
                "structuredData": True,  # Returns structured JSON
                "htmlTables": True,  # Can output tables as HTML
                "pageScreenshots": True,  # Can capture page screenshots
            },
            performance={
                "maxFileSize": 100 * 1024 * 1024,  # 100MB
                "averageSpeed": 5,  # pages per second (slower due to AI processing)
            }
        )

    async def can_process(self, document: Document) -> bool:
        """Check if provider can process the document."""
        # Initialize if needed
        if not self._initialized and self.config:
            await self.initialize(self.config)
        
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
        """Get document overview showing LlamaParse capabilities and available formats."""
        doc_path = await self._ensure_local_document(document)
        depth = options.get("depth", "structure")

        try:
            # Dynamically check what's actually enabled and available
            available_features = []
            available_formats = {}
            provider_status = "inactive"
            
            # Check if LlamaParse is properly configured
            if hasattr(self, 'config') and self.config:
                if self.config.api_key:
                    provider_status = "active"
                    # LlamaParse is configured, check what it can do
                    
                    # Check if we have cached data first
                    if self.cache:
                        cached_data = await self.cache.get_cached_extraction(doc_path)
                        if cached_data:
                            result = cached_data
                            logger.info(f"Using cached LlamaParse data for peek")
                        else:
                            # Parse document with minimal extraction for peek
                            result = await self._parse_document(doc_path, parsing_instruction="Extract document metadata and structure only")
                    else:
                        result = await self._parse_document(doc_path, parsing_instruction="Extract document metadata and structure only")
                    
                    # Dynamically determine available formats based on actual result
                    if isinstance(result, dict):
                        # Check what's actually in the result
                        if result.get("documents") or result.get("pages"):
                            available_formats["text"] = True
                            available_formats["markdown"] = True
                            available_features.append("text_extraction")
                            available_features.append("markdown_extraction")
                        
                        if result.get("documents") or result.get("pages"):
                            available_formats["json"] = True
                            available_features.append("structured_output")
                        
                        if result.get("images"):
                            available_formats["images"] = True
                            available_features.append("image_extraction")
                        
                        if result.get("tables"):
                            available_formats["tables"] = True
                            available_features.append("table_extraction")
                        
                        # Check for layout information
                        if any(p.get("layout") for p in result.get("pages", [])):
                            available_formats["layout"] = True
                            available_features.append("layout_preservation")
                    
                    # Add AI-powered features if API is working
                    available_features.extend([
                        "ai_analysis",
                        "entity_recognition",
                        "relationship_mapping",
                        "custom_instructions"
                    ])
                else:
                    # No API key configured
                    provider_status = "not_configured"
                    result = {}
            else:
                # Not properly initialized
                provider_status = "not_initialized"
                result = {}
            
            # Extract metadata from parsed result
            metadata = {
                "format": document.format or get_document_format(document.url),
                "fileSize": document.size,
                "pageCount": len(result.get("pages", [])) if isinstance(result, dict) and result else 0,
                "availableFormats": available_formats,
                "providerCapabilities": {
                    "provider": "llama-parse",
                    "features": available_features,
                    "status": provider_status,
                    "limitations": [] if provider_status == "active" else ["API key required", "No AI analysis available"]
                }
            }

            structure = {}
            preview = {}

            if depth in ["structure", "preview"]:
                structure = {
                    "hasImages": len(result.get("images", [])) > 0 if isinstance(result, dict) else False,
                    "hasTables": len(result.get("tables", [])) > 0 if isinstance(result, dict) else False,
                    "sections": self._extract_sections(result),
                    "totalDocuments": len(result.get("documents", [])) if isinstance(result, dict) else 0,
                    "extractionTypes": list(result.keys()) if isinstance(result, dict) else []
                }

            if depth == "preview":
                # Show a preview of different available formats
                preview = {
                    "firstPageText": result.get("pages", [{}])[0].get("text", "")[:500] if isinstance(result, dict) else "",
                    "firstPageMarkdown": result.get("pages", [{}])[0].get("markdown", "")[:500] if isinstance(result, dict) else "",
                    "tableOfContents": self._extract_toc(result),
                    "sampleEntities": self._extract_entities(result)[:5] if isinstance(result, dict) else [],
                    "availableData": {
                        "documents": len(result.get("documents", [])) if isinstance(result, dict) else 0,
                        "pages": len(result.get("pages", [])) if isinstance(result, dict) else 0,
                        "images": len(result.get("images", [])) if isinstance(result, dict) else 0,
                        "tables": len(result.get("tables", [])) if isinstance(result, dict) else 0
                    }
                }

        except Exception as e:
            logger.error(f"Error peeking document with LlamaParse: {e}")
            raise

        return PeekResult(
            metadata=metadata,
            structure=structure if depth in ["structure", "preview"] else None,
            preview=preview if depth == "preview" else None
        )

    async def map(self, document: Document, options: Dict[str, Any]) -> MapResult:
        """Generate document structure map using LlamaParse with enhanced extraction."""
        doc_path = await self._ensure_local_document(document)
        include_content = options.get("include_content", False)
        analysis_depth = options.get("analysis_depth", "deep")

        try:
            # Parse with custom instructions for structure mapping
            instruction = "Extract complete document structure including sections, subsections, tables, figures, and cross-references"
            if analysis_depth == "comprehensive":
                instruction += ". Include entity relationships, detailed metadata, and preserve all layout information."
            
            # Extract images for comprehensive analysis
            extract_images = analysis_depth in ["deep", "comprehensive"]
            
            result = await self._parse_document(
                doc_path, 
                parsing_instruction=instruction,
                extract_images=extract_images
            )

            # Build enhanced document map
            document_map = {
                "hierarchy": self._build_hierarchy_enhanced(result, include_content),
                "resources": {
                    "images": result.get("images", []),
                    "tables": result.get("tables", []),
                    "equations": [],  # Could be extracted from content
                },
                "crossReferences": self._extract_references(result),
                "pageStructure": []
            }
            
            # Add page structure information
            for page in result.get("pages", []):
                page_info = {
                    "pageNumber": page.get("page_num", 1),
                    "hasText": bool(page.get("text")),
                    "hasImages": any(img.get("page") == page.get("page_num") for img in result.get("images", [])),
                    "hasTables": any(tbl.get("page") == page.get("page_num") for tbl in result.get("tables", [])),
                }
                if page.get("layout"):
                    page_info["layout"] = page["layout"]
                document_map["pageStructure"].append(page_info)

            statistics = {
                "totalPages": len(result.get("pages", [])),
                "totalImages": len(result.get("images", [])),
                "totalTables": len(result.get("tables", [])),
                "totalSections": len(self._extract_sections(result)),
                "analysisDepth": analysis_depth,
            }

        except Exception as e:
            logger.error(f"Error mapping document with LlamaParse: {e}")
            raise

        return MapResult(
            document_map=document_map,
            statistics=statistics
        )

    async def seek(self, document: Document, target: Dict[str, Any]) -> SeekResult:
        """Navigate to specific location in document using LlamaParse."""
        doc_path = await self._ensure_local_document(document)

        try:
            # Parse document
            result = await self._parse_document(doc_path)

            # Find target location
            location = {}
            content = ""
            context = {}

            if "page" in target:
                page_num = target["page"]
                if isinstance(result, dict) and "pages" in result:
                    if 0 < page_num <= len(result["pages"]):
                        content = result["pages"][page_num - 1].get("text", "")
                        location = {"page": page_num, "type": "page"}
                        context = {
                            "totalPages": len(result["pages"]),
                            "hasNext": page_num < len(result["pages"]),
                            "hasPrevious": page_num > 1
                        }

            elif "section" in target:
                # Search for section
                section_content = self._find_section(result, target["section"])
                if section_content:
                    content = section_content
                    location = {"section": target["section"], "type": "section"}

            elif "query" in target:
                # Search for text
                search_result = self._search_text(result, target["query"])
                if search_result:
                    content = search_result["content"]
                    location = search_result["location"]

        except Exception as e:
            logger.error(f"Error seeking in document with LlamaParse: {e}")
            raise

        return SeekResult(
            location=location,
            content=content,
            context=context
        )

    async def xray(self, document: Document, options: Dict[str, Any]) -> XrayResult:
        """Return ALL cached LlamaParse extraction data for comprehensive analysis."""
        doc_path = await self._ensure_local_document(document)
        custom_instructions = options.get("custom_instructions")

        try:
            # Build comprehensive parsing instruction
            parsing_instruction = custom_instructions or "Extract all possible information from this document"
            
            # Parse document - this will either use cache or fetch new data
            result = await self._parse_document(doc_path, parsing_instruction=parsing_instruction)

            # Return EVERYTHING from the extraction
            analysis = {
                "full_extraction": result,  # All the raw extraction data
                "summary": {
                    "total_documents": len(result.get("documents", [])) if isinstance(result, dict) else 0,
                    "total_pages": len(result.get("pages", [])) if isinstance(result, dict) else 0,
                    "has_images": len(result.get("images", [])) > 0 if isinstance(result, dict) else False,
                    "has_tables": len(result.get("tables", [])) > 0 if isinstance(result, dict) else False,
                    "metadata": result.get("metadata", {}) if isinstance(result, dict) else {}
                }
            }
            
            # Also extract specific insights if available
            if isinstance(result, dict):
                # Extract entities from the text content
                all_text = " ".join([doc.get("text", "") for doc in result.get("documents", [])])
                
                # Basic entity extraction from the AI-processed text
                if all_text:
                    analysis["extracted_content"] = {
                        "entities": self._extract_entities(result),
                        "key_points": self._extract_key_points(result),
                        "structure": self._analyze_structure(result)
                    }

            confidence = 0.95  # High confidence since we have all the data

        except Exception as e:
            logger.error(f"Error performing xray analysis with LlamaParse: {e}")
            raise

        return XrayResult(
            analysis=analysis,
            confidence=confidence,
            provider_info={
                "name": self.get_name(),
                "model": "llama-parse-latest",
                "supports_xray": True,
                "capabilities": ["full_extraction", "images", "tables", "markdown", "json", "text"]
            }
        )

    async def extract(self, document: Document, options: Dict[str, Any]) -> ExtractResult:
        """Extract content from document using LlamaParse with enhanced capabilities."""
        doc_path = await self._ensure_local_document(document)
        extraction_targets = options.get("extraction_targets", ["text"])
        output_format = options.get("output_format", "markdown")
        pages = options.get("pages")

        try:
            # Build parsing instruction based on extraction targets
            instructions = []
            extract_images = False
            
            if "text" in extraction_targets:
                instructions.append("Extract all text content preserving structure")
            if "tables" in extraction_targets:
                instructions.append("Extract and format all tables with proper structure")
            if "images" in extraction_targets:
                instructions.append("Extract images with descriptions, captions, and metadata")
                extract_images = True
            if "forms" in extraction_targets:
                instructions.append("Extract form fields and values")
            if "metadata" in extraction_targets:
                instructions.append("Extract comprehensive document metadata")
            if "equations" in extraction_targets:
                instructions.append("Extract mathematical equations preserving notation")
            if "layout" in extraction_targets:
                instructions.append("Preserve document layout and formatting")

            parsing_instruction = ". ".join(instructions) if instructions else None
            
            # Determine result type based on output format
            result_type = "markdown" if output_format == "markdown" else None
            
            # Parse document with enhanced extraction
            result = await self._parse_document(
                doc_path, 
                parsing_instruction=parsing_instruction,
                result_type=result_type,
                extract_images=extract_images
            )

            # Format output based on requested format
            if output_format == "markdown":
                content = self._format_as_markdown_enhanced(result, extraction_targets)
            elif output_format == "json":
                content = self._format_as_json_enhanced(result, extraction_targets)
            else:  # structured - return full rich data
                content = {
                    "pages": result.get("pages", []),
                    "images": result.get("images", []) if "images" in extraction_targets else [],
                    "tables": result.get("tables", []) if "tables" in extraction_targets else [],
                    "metadata": result.get("metadata", {}),
                    "extraction_targets": extraction_targets
                }

            # Calculate enhanced statistics
            statistics = {
                "pagesExtracted": len(result.get("pages", [])),
                "charactersExtracted": sum(len(p.get("text", "")) for p in result.get("pages", [])),
                "imagesFound": len(result.get("images", [])),
                "tablesFound": len(result.get("tables", [])),
            }

            # Get pages processed
            if pages:
                pages_processed = pages
            else:
                pages_processed = [p.get("page_num", i+1) for i, p in enumerate(result.get("pages", []))]

        except Exception as e:
            logger.error(f"Error extracting from document with LlamaParse: {e}")
            raise

        return ExtractResult(
            content=content,
            format=output_format,
            pages_processed=pages_processed,
            statistics=statistics
        )

    async def initialize(self, config: LlamaParseConfig) -> None:
        """Initialize provider with configuration."""
        self.config = config
        
        # Initialize LlamaParse client
        try:
            if not config.api_key:
                raise ValueError("LlamaParse API key is required but not provided")
            
            logger.info(f"Initializing LlamaParse with mode: {config.mode}, API key: {'****' + config.api_key[-4:] if config.api_key else 'None'}")
            
            self.parser = LlamaParse(
                api_key=config.api_key,
                result_type="markdown",  # Default to markdown for rich content
                parsing_instruction=None,  # Will be set per request
                skip_diagonal_text=True,
                invalidate_cache=False,
                do_not_cache=False,
                fast_mode=config.mode == "fast",
                premium_mode=config.mode == "premium",
                # Note: Additional options removed as they may not be valid for constructor
                # and could cause hanging issues
            )
            self._initialized = True
            logger.info(f"LlamaParse provider initialized successfully in {config.mode} mode")
        except Exception as e:
            logger.error(f"Failed to initialize LlamaParse provider: {e}")
            self._initialized = False
            raise

    async def dispose(self) -> None:
        """Cleanup provider resources."""
        self._initialized = False
        self.parser = None
        logger.info("LlamaParse provider disposed")

    async def _ensure_local_document(self, document: Document) -> Path:
        """Ensure document is available locally."""
        if document.path and document.path.exists():
            return document.path

        # Check if it's a local file path
        local_path = await get_local_document(document.url)
        if local_path:
            document.path = local_path
            if not document.hash:
                with open(local_path, "rb") as f:
                    document.hash = hashlib.sha256(f.read()).hexdigest()
            return local_path

        # It's a URL, download it
        if is_url(document.url):
            local_path = await download_document(document.url)
            document.path = local_path
            if not document.hash:
                with open(local_path, "rb") as f:
                    document.hash = hashlib.sha256(f.read()).hexdigest()
            return local_path
        
        raise ValueError(f"Unable to process document: {document.url}")

    async def _parse_document(self, doc_path: Path, parsing_instruction: Optional[str] = None, 
                            result_type: Optional[str] = None, extract_images: bool = False) -> Any:
        """Parse document using LlamaParse with enhanced extraction and caching.
        
        Args:
            doc_path: Path to document
            parsing_instruction: Custom parsing instructions
            result_type: Override result type ("markdown", "text", "json")
            extract_images: Whether to extract images
        """
        # Initialize if needed
        if not self._initialized and self.config:
            await self.initialize(self.config)
        
        if not self.parser:
            raise RuntimeError("LlamaParse provider not initialized")

        # Check cache first
        cached_result = await self.cache.retrieve_extraction(doc_path, parsing_instruction)
        if cached_result:
            logger.info(f"Using cached LlamaParse extraction for {doc_path.name}")
            return cached_result
        
        # Update parsing settings
        if parsing_instruction:
            self.parser.parsing_instruction = parsing_instruction
            logger.info(f"Parsing document with instruction: {parsing_instruction[:100]}...")
        
        if result_type:
            self.parser.result_type = result_type

        logger.info(f"Making LlamaParse API call for document: {doc_path.name}")
        
        # Ensure file has proper extension for LlamaParse
        file_path_str = str(doc_path)
        if not doc_path.suffix:
            # Try to detect file type and add extension
            import mimetypes
            import shutil
            mime_type, _ = mimetypes.guess_type(str(doc_path))
            if not mime_type:
                # Use file command to detect type
                try:
                    import subprocess
                    result = subprocess.run(['file', '--mime-type', str(doc_path)], 
                                         capture_output=True, text=True)
                    if result.returncode == 0:
                        mime_type = result.stdout.split(':')[-1].strip()
                except:
                    pass
            
            # Map mime type to extension
            ext_map = {
                'application/pdf': '.pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                'application/msword': '.doc',
                'text/plain': '.txt',
                'text/html': '.html',
            }
            
            if mime_type in ext_map:
                # Create a temporary file with the proper extension
                temp_path = doc_path.with_suffix(ext_map[mime_type])
                if not temp_path.exists():
                    shutil.copy2(doc_path, temp_path)
                file_path_str = str(temp_path)
                logger.info(f"Added extension {ext_map[mime_type]} to file for LlamaParse")
        
        # Parse the document with timeout to prevent hanging
        try:
            # Set a reasonable timeout (60 seconds for API call)
            documents = await asyncio.wait_for(
                self.parser.aload_data(file_path_str),
                timeout=60.0
            )
            logger.info(f"LlamaParse API call completed. Received {len(documents) if documents else 0} document(s)")
        except asyncio.TimeoutError:
            logger.error(f"LlamaParse API call timed out after 60 seconds for {doc_path.name}")
            raise TimeoutError("LlamaParse API call timed out. Please try again or use a simpler document.")
        except Exception as e:
            logger.error(f"LlamaParse API call failed: {e}")
            raise
        
        # Build enhanced structured format
        result = {
            "documents": [],
            "pages": [],
            "images": [],
            "tables": [],
            "metadata": {}
        }
        
        if documents:
            for i, doc in enumerate(documents):
                # Store document data - handle both Document objects and dicts
                doc_text = ""
                doc_metadata = {}
                
                # Handle LlamaParse Document object
                if hasattr(doc, 'text'):
                    doc_text = doc.text
                    doc_metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                elif hasattr(doc, 'get_content'):
                    doc_text = doc.get_content()
                    doc_metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                elif isinstance(doc, dict):
                    doc_text = doc.get('text', '')
                    doc_metadata = doc.get('metadata', {})
                else:
                    # Try to convert to string
                    doc_text = str(doc)
                
                result["documents"].append({
                    "text": doc_text,
                    "metadata": doc_metadata
                })
                
                # Extract page-level data if available
                if hasattr(doc, 'pages') and doc.pages:
                    for page in doc.pages:
                        page_data = {
                            "page_num": page.get('page_num', i + 1) if isinstance(page, dict) else getattr(page, 'page_num', i + 1),
                            "text": page.get('text', '') if isinstance(page, dict) else getattr(page, 'text', ''),
                            "markdown": page.get('md', '') if isinstance(page, dict) else getattr(page, 'markdown', ''),
                        }
                        
                        # Extract images if requested
                        page_images = page.get('images', []) if isinstance(page, dict) else getattr(page, 'images', [])
                        if extract_images and page_images:
                            for img in page_images:
                                result["images"].append({
                                    "page": page_data["page_num"],
                                    "data": img.get('data') if isinstance(img, dict) else getattr(img, 'data', None),
                                    "type": img.get('type') if isinstance(img, dict) else getattr(img, 'type', None),
                                    "metadata": img.get('metadata', {}) if isinstance(img, dict) else getattr(img, 'metadata', {})
                                })
                        
                        # Extract tables
                        page_tables = page.get('tables', []) if isinstance(page, dict) else getattr(page, 'tables', [])
                        if page_tables:
                            for table in page_tables:
                                result["tables"].append({
                                    "page": page_data["page_num"],
                                    "html": table.get('html') if isinstance(table, dict) else getattr(table, 'html', None),
                                    "data": table.get('data') if isinstance(table, dict) else getattr(table, 'data', None),
                                    "metadata": table.get('metadata', {}) if isinstance(table, dict) else getattr(table, 'metadata', {})
                                })
                        
                        # Store layout if available
                        page_layout = page.get('layout') if isinstance(page, dict) else getattr(page, 'layout', None)
                        if page_layout:
                            page_data["layout"] = page_layout
                        
                        result["pages"].append(page_data)
                
                # If no page-level data, create from document
                if not result["pages"] and doc_text:
                    result["pages"].append({
                        "page_num": 1,
                        "text": doc_text,
                        "markdown": doc_text,
                        "metadata": doc_metadata
                    })
            
            # Store global metadata
            if documents and documents[0]:
                if hasattr(documents[0], 'metadata'):
                    result["metadata"] = documents[0].metadata
                elif isinstance(documents[0], dict):
                    result["metadata"] = documents[0].get('metadata', {})
                else:
                    result["metadata"] = {}
        
        # Store in cache for future use
        await self.cache.store_extraction(doc_path, result, parsing_instruction)
        logger.info(f"Cached LlamaParse extraction for {doc_path.name}")
        
        return result

    def _extract_sections(self, result: Any) -> List[Dict[str, Any]]:
        """Extract sections from parsed result."""
        sections = []
        # Implementation depends on LlamaParse output structure
        # This is a simplified version
        text = str(result)
        lines = text.split('\n')
        
        for line in lines:
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                sections.append({
                    "level": level,
                    "title": title
                })
        
        return sections

    def _extract_toc(self, result: Any) -> List[Dict[str, Any]]:
        """Extract table of contents."""
        return self._extract_sections(result)

    def _build_hierarchy(self, result: Any, include_content: bool) -> Dict[str, Any]:
        """Build document hierarchy (legacy method)."""
        hierarchy = {
            "root": {
                "type": "document",
                "title": "Document",
                "children": []
            }
        }
        
        sections = self._extract_sections(result)
        for section in sections:
            node = {
                "type": "section",
                "title": section["title"],
                "level": section["level"],
                "children": []
            }
            if include_content:
                node["content"] = ""  # Would extract actual content
            hierarchy["root"]["children"].append(node)
        
        return hierarchy
    
    def _build_hierarchy_enhanced(self, result: Dict[str, Any], include_content: bool) -> Dict[str, Any]:
        """Build enhanced document hierarchy with rich structure."""
        hierarchy = {
            "root": {
                "type": "document",
                "title": result.get("metadata", {}).get("title", "Document"),
                "metadata": result.get("metadata", {}),
                "children": []
            }
        }
        
        # Build hierarchy from pages
        for page in result.get("pages", []):
            page_node = {
                "type": "page",
                "pageNumber": page.get("page_num", 1),
                "children": []
            }
            
            # Extract sections from page content
            page_sections = self._extract_sections_from_page(page)
            for section in page_sections:
                section_node = {
                    "type": "section",
                    "title": section["title"],
                    "level": section["level"],
                    "children": []
                }
                
                if include_content:
                    # Include snippet of content
                    section_node["content"] = section.get("content", "")[:500]
                
                page_node["children"].append(section_node)
            
            # Add table nodes
            page_tables = [t for t in result.get("tables", []) if t.get("page") == page.get("page_num")]
            for i, table in enumerate(page_tables, 1):
                table_node = {
                    "type": "table",
                    "title": f"Table {i}",
                    "metadata": table.get("metadata", {})
                }
                if include_content and table.get("html"):
                    table_node["htmlContent"] = table["html"]
                page_node["children"].append(table_node)
            
            # Add image nodes
            page_images = [img for img in result.get("images", []) if img.get("page") == page.get("page_num")]
            for i, img in enumerate(page_images, 1):
                image_node = {
                    "type": "image",
                    "title": f"Image {i}",
                    "imageType": img.get("type", "unknown"),
                    "metadata": img.get("metadata", {})
                }
                page_node["children"].append(image_node)
            
            hierarchy["root"]["children"].append(page_node)
        
        return hierarchy
    
    def _extract_sections_from_page(self, page: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sections from a single page."""
        sections = []
        content = page.get("markdown", page.get("text", ""))
        lines = content.split('\n')
        
        current_content = []
        for line in lines:
            if line.startswith('#'):
                # Save previous section if exists
                if current_content and sections:
                    sections[-1]["content"] = "\n".join(current_content).strip()
                current_content = []
                
                # Extract new section
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                sections.append({
                    "level": level,
                    "title": title,
                    "content": ""
                })
            else:
                current_content.append(line)
        
        # Save last section content
        if current_content and sections:
            sections[-1]["content"] = "\n".join(current_content).strip()
        
        return sections

    def _extract_resources(self, result: Any) -> Dict[str, List[Any]]:
        """Extract document resources (images, tables, etc.)."""
        resources = {
            "images": [],
            "tables": [],
            "equations": []
        }
        
        # Parse result for resources
        # This is simplified - actual implementation would parse LlamaParse output
        text = str(result)
        
        # Look for table indicators
        if "table" in text.lower():
            resources["tables"].append({
                "id": "table-1",
                "description": "Detected table"
            })
        
        # Look for image indicators
        if "image" in text.lower() or "figure" in text.lower():
            resources["images"].append({
                "id": "img-1",
                "description": "Detected image"
            })
        
        return resources

    def _extract_references(self, result: Any) -> List[Dict[str, Any]]:
        """Extract cross-references."""
        references = []
        # Implementation would parse references from LlamaParse output
        return references

    def _find_section(self, result: Any, section_name: str) -> Optional[str]:
        """Find a specific section in the document."""
        sections = self._extract_sections(result)
        for section in sections:
            if section_name.lower() in section["title"].lower():
                # Would extract actual section content
                return f"Content of section: {section['title']}"
        return None

    def _search_text(self, result: Any, query: str) -> Optional[Dict[str, Any]]:
        """Search for text in the document."""
        text = str(result)
        query_lower = query.lower()
        text_lower = text.lower()
        
        pos = text_lower.find(query_lower)
        if pos != -1:
            # Extract context around the match
            start = max(0, pos - 100)
            end = min(len(text), pos + len(query) + 100)
            return {
                "content": text[start:end],
                "location": {"position": pos, "type": "text"}
            }
        return None

    def _extract_entities(self, result: Any) -> List[Dict[str, Any]]:
        """Extract named entities from the parsed result."""
        entities = []
        seen = set()
        
        # When LlamaParse is given entity extraction instructions, results are in documents
        if isinstance(result, dict) and "documents" in result:
            for doc in result.get("documents", []):
                text = doc.get("text", "")
                # Parse lines that look like entity listings
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and line.startswith('-'):
                        entity_text = line.lstrip('-').strip()
                        if entity_text and entity_text not in seen:
                            # Determine entity type based on content
                            entity_type = "ORGANIZATION"  # Default
                            if "Service" in entity_text or "Department" in entity_text or "Commission" in entity_text:
                                entity_type = "ORGANIZATION"
                            elif "Act" in entity_text or "FATCA" in entity_text:
                                entity_type = "LEGISLATION"
                            
                            entities.append({
                                "text": entity_text,
                                "type": entity_type,
                                "confidence": 0.8
                            })
                            seen.add(entity_text)
        
        # If no entities found, try pattern matching
        if not entities:
            import re
            all_text = ""
            if isinstance(result, dict):
                if "documents" in result:
                    all_text = " ".join(doc.get("text", "") for doc in result["documents"])
                elif "pages" in result:
                    all_text = " ".join(page.get("text", "") for page in result["pages"])
            else:
                all_text = str(result)
            
            # Find capitalized words and acronyms
            patterns = [
                r'\b[A-Z]{2,}\b',  # Acronyms like IRS, SSA
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Proper names
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, all_text)
                for word in matches:
                    if word not in seen and len(word) > 2 and word not in ["The", "This", "That"]:
                        entities.append({
                            "text": word,
                            "type": "UNKNOWN",
                            "confidence": 0.6
                        })
                        seen.add(word)
        
        return entities[:50]  # Limit to top 50

    def _extract_relationships(self, result: Any) -> List[Dict[str, Any]]:
        """Extract entity relationships."""
        relationships = []
        # Would analyze entities and their relationships
        return relationships

    def _extract_key_points(self, result: Any) -> List[str]:
        """Extract key points from the document."""
        key_points = []
        
        # When LlamaParse is given analysis instructions, it returns results in documents
        if isinstance(result, dict) and "documents" in result:
            # Extract from all document texts
            for doc in result.get("documents", []):
                text = doc.get("text", "")
                # Look for bullet points, lists, or key statements
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (
                        line.startswith(('•', '-', '*', '1.', '2.', '3.')) or
                        len(line) > 10  # Include substantial lines as potential key points
                    ):
                        cleaned = line.lstrip('•-*123456789. ').strip()
                        if cleaned and cleaned not in key_points:
                            key_points.append(cleaned)
        
        # Also check pages for content
        if isinstance(result, dict) and "pages" in result:
            for page in result.get("pages", []):
                text = page.get("text", "") or page.get("markdown", "")
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 10 and line not in key_points:
                        key_points.append(line)
        
        # If we have no key points but have text, extract first few meaningful lines
        if not key_points:
            all_text = ""
            if isinstance(result, dict):
                if "documents" in result:
                    all_text = " ".join(doc.get("text", "") for doc in result["documents"])
                elif "pages" in result:
                    all_text = " ".join(page.get("text", "") for page in result["pages"])
            else:
                all_text = str(result)
            
            # Split into sentences and take the first few
            sentences = [s.strip() for s in all_text.split('.') if s.strip()]
            key_points = sentences[:5]
        
        return key_points[:10]  # Limit to top 10

    def _analyze_sentiment(self, result: Any) -> Dict[str, Any]:
        """Analyze document sentiment."""
        # Would use AI analysis from LlamaParse
        return {
            "overall": "neutral",
            "confidence": 0.75,
            "aspects": []
        }

    def _analyze_structure(self, result: Any) -> Dict[str, Any]:
        """Analyze document structure."""
        sections = self._extract_sections(result)
        return {
            "type": "structured",
            "sections": len(sections),
            "depth": max([s["level"] for s in sections]) if sections else 0,
            "organization": "hierarchical"
        }

    def _format_as_markdown(self, result: Any, extraction_targets: List[str]) -> str:
        """Format result as markdown (legacy method for compatibility)."""
        if isinstance(result, dict):
            if "documents" in result and result["documents"]:
                return result["documents"][0].get("text", "")
            elif "pages" in result:
                return "\n\n---\n\n".join([page.get("markdown", page.get("text", "")) for page in result["pages"]])
        return str(result)
    
    def _format_as_markdown_enhanced(self, result: Dict[str, Any], extraction_targets: List[str]) -> str:
        """Format result as enhanced markdown with all requested content."""
        markdown_parts = []
        
        # Add document metadata if requested
        if "metadata" in extraction_targets and result.get("metadata"):
            markdown_parts.append("# Document Metadata\n")
            for key, value in result["metadata"].items():
                markdown_parts.append(f"- **{key}**: {value}")
            markdown_parts.append("\n")
        
        # Add page content
        for page in result.get("pages", []):
            page_num = page.get("page_num", 1)
            markdown_parts.append(f"## Page {page_num}\n")
            
            # Use markdown content if available, otherwise fall back to text
            content = page.get("markdown", page.get("text", ""))
            if content:
                markdown_parts.append(content)
            
            # Add tables if extracted
            if "tables" in extraction_targets:
                page_tables = [t for t in result.get("tables", []) if t.get("page") == page_num]
                for table in page_tables:
                    markdown_parts.append("\n### Table\n")
                    if table.get("html"):
                        markdown_parts.append(f"```html\n{table['html']}\n```\n")
                    elif table.get("data"):
                        markdown_parts.append(f"```\n{table['data']}\n```\n")
            
            # Add image references if extracted
            if "images" in extraction_targets:
                page_images = [img for img in result.get("images", []) if img.get("page") == page_num]
                if page_images:
                    markdown_parts.append("\n### Images\n")
                    for i, img in enumerate(page_images, 1):
                        img_type = img.get("type", "image")
                        metadata = img.get("metadata", {})
                        markdown_parts.append(f"- Image {i} ({img_type})")
                        if metadata:
                            for key, value in metadata.items():
                                markdown_parts.append(f"  - {key}: {value}")
            
            markdown_parts.append("\n---\n")
        
        return "\n".join(markdown_parts)

    def _format_as_json(self, result: Any, extraction_targets: List[str]) -> Dict[str, Any]:
        """Format result as JSON (legacy method for compatibility)."""
        output = {}
        
        if "text" in extraction_targets:
            output["text"] = self._format_as_markdown(result, ["text"])
        
        if "metadata" in extraction_targets:
            if isinstance(result, dict) and "metadata" in result:
                output["metadata"] = result["metadata"]
        
        if "tables" in extraction_targets:
            output["tables"] = self._extract_resources(result).get("tables", [])
        
        if "images" in extraction_targets:
            output["images"] = self._extract_resources(result).get("images", [])
        
        return output
    
    def _format_as_json_enhanced(self, result: Dict[str, Any], extraction_targets: List[str]) -> Dict[str, Any]:
        """Format result as enhanced JSON with structured data."""
        output = {}
        
        # Add text content
        if "text" in extraction_targets:
            output["text"] = []
            for page in result.get("pages", []):
                output["text"].append({
                    "page": page.get("page_num", 1),
                    "content": page.get("text", ""),
                    "markdown": page.get("markdown", "")
                })
        
        # Add metadata
        if "metadata" in extraction_targets:
            output["metadata"] = result.get("metadata", {})
        
        # Add tables with full structure
        if "tables" in extraction_targets and result.get("tables"):
            output["tables"] = result["tables"]
        
        # Add images with metadata
        if "images" in extraction_targets and result.get("images"):
            output["images"] = result["images"]
        
        # Add layout information if available
        if "layout" in extraction_targets:
            output["layout"] = []
            for page in result.get("pages", []):
                if page.get("layout"):
                    output["layout"].append({
                        "page": page.get("page_num", 1),
                        "layout": page["layout"]
                    })
        
        # Add summary statistics
        output["statistics"] = {
            "totalPages": len(result.get("pages", [])),
            "totalTables": len(result.get("tables", [])),
            "totalImages": len(result.get("images", [])),
            "extractionTargets": extraction_targets
        }
        
        return output