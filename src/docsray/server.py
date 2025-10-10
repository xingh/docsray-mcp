"""Main Docsray MCP server implementation using FastMCP."""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .config import DocsrayConfig
from .providers.registry import ProviderRegistry
from .tools import extract, fetch, map, peek, search, seek, xray
from .utils.cache import DocumentCache
from .utils.logging import setup_logging

logger = logging.getLogger(__name__)


class ServerInfo(BaseModel):
    """Server information model."""

    name: str = "docsray"
    version: str = "0.1.0"
    description: str = "Advanced document perception and understanding MCP server"


class DocsrayServer:
    """Main Docsray MCP server."""

    def __init__(self, config: Optional[DocsrayConfig] = None):
        """Initialize the Docsray server.
        
        Args:
            config: Server configuration. If None, loads from environment.
        """
        self.config = config or DocsrayConfig.from_env()
        setup_logging(self.config.log_level)

        # Initialize FastMCP server
        self.mcp = FastMCP(
            name="docsray",
            dependencies=["httpx", "pymupdf4llm"]
        )

        # Initialize components
        self.cache = DocumentCache(
            enabled=self.config.performance.cache_enabled,
            ttl=self.config.performance.cache_ttl
        )
        self.registry = ProviderRegistry()

        # Register tools
        self._register_tools()

        # Initialize providers
        self._initialize_providers()

        logger.info(f"Docsray server initialized with transport: {self.config.transport.type}")

    def _register_tools(self) -> None:
        """Register all MCP tools."""
        
        # Server information resource
        @self.mcp.resource(
            uri="docsray://info",
            name="docsray_info",
            description="Server capabilities, providers, and usage instructions"
        )
        async def get_server_info() -> Dict[str, Any]:
            """Return comprehensive server information for discovery."""
            providers = []
            for name in self.registry.list_providers():
                provider = self.registry.get_provider(name)
                if provider:
                    caps = provider.get_capabilities() if hasattr(provider, 'get_capabilities') else None
                    providers.append({
                        "name": name,
                        "status": "active" if provider._initialized else "registered",
                        "supported_formats": caps.formats if caps else [],
                        "features": caps.features if caps else {},
                        "performance": caps.performance if caps else {}
                    })
            
            return {
                "name": "docsray",
                "version": "1.0.0",
                "description": "AI-powered document processing MCP server with advanced capabilities",
                "tools": [
                    {
                        "name": "docsray_peek",
                        "description": "Quick document overview with format detection and provider capabilities",
                        "input_types": ["local_files", "urls"]
                    },
                    {
                        "name": "docsray_map", 
                        "description": "Generate comprehensive document structure maps with caching",
                        "features": ["hierarchy_detection", "resource_extraction", "cross_references"]
                    },
                    {
                        "name": "docsray_xray",
                        "description": "AI-powered deep analysis extracting entities, relationships, and insights",
                        "analysis_types": ["entities", "key_points", "relationships", "sentiment", "topics", "custom"]
                    },
                    {
                        "name": "docsray_extract",
                        "description": "Extract content in multiple formats (markdown, text, JSON, tables)",
                        "output_formats": ["markdown", "text", "json", "structured"],
                        "extraction_targets": ["text", "tables", "images", "metadata"]
                    },
                    {
                        "name": "docsray_seek",
                        "description": "Navigate to specific pages, sections, or search for content",
                        "navigation_types": ["page", "section", "query", "semantic_search"]
                    },
                    {
                        "name": "docsray_fetch",
                        "description": "Unified document retrieval from web URLs or filesystem with caching",
                        "source_types": ["https_urls", "filesystem_paths"],
                        "return_formats": ["raw", "processed", "metadata-only"],
                        "features": ["progress_reporting", "caching", "multiple_encodings"]
                    },
                    {
                        "name": "docsray_search",
                        "description": "Intelligent filesystem search using coarse-to-fine methodology",
                        "search_strategies": ["coarse-to-fine", "semantic", "keyword", "hybrid"],
                        "features": ["semantic_ranking", "content_analysis", "relevance_scoring"]
                    }
                ],
                "capabilities": {
                    "document_formats": [
                        "pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls",
                        "txt", "md", "html", "xml", "json", "csv", "rtf",
                        "png", "jpg", "jpeg", "tiff", "bmp", "gif", "webp",
                        "odt", "ods", "odp", "epub", "mobi"
                    ],
                    "input_sources": ["local_files", "web_urls", "filesystem_search"],
                    "extraction_formats": ["markdown", "text", "json", "structured", "DoclingDocument"],
                    "analysis_types": [
                        "entities", "key_points", "structure", "relationships", 
                        "sentiment", "topics", "custom_instructions", "multimodal"
                    ],
                    "advanced_features": [
                        "semantic_search", "rag_retrieval", "hybrid_ocr", 
                        "layout_understanding", "reading_order_preservation",
                        "coarse_to_fine_search", "document_chunking",
                        "vector_embeddings", "multimodal_analysis"
                    ],
                    "providers": providers
                },
                "usage_examples": {
                    "quick_overview": "Peek at document.pdf to see its structure",
                    "entity_extraction": "Xray contract.pdf and extract all parties and dates",
                    "structure_mapping": "Map the complete hierarchy of manual.pdf",
                    "content_extraction": "Extract pages 5-10 from report.pdf as markdown",
                    "url_processing": "Analyze https://example.com/document.pdf",
                    "document_fetch": "Fetch https://example.com/doc.pdf with processed format",
                    "semantic_search": "Search for 'machine learning' in ./research/ with semantic strategy",
                    "advanced_analysis": "Xray contract.pdf with provider ibm-docling for advanced layout understanding"
                },
                "best_practices": [
                    "Start with peek to understand document structure",
                    "Use xray for AI-powered analysis with custom instructions",
                    "Use extract for fast content retrieval",
                    "Use fetch for unified document retrieval with caching",
                    "Use search for intelligent filesystem discovery",
                    "Choose providers based on your needs: pymupdf4llm (fast), llama-parse (AI), ibm-docling (layout), mimic-docsray (search)",
                    "Results are cached for fast subsequent access"
                ]
            }
        
        # Example prompts resource
        @self.mcp.resource(
            uri="docsray://prompts",
            name="docsray_prompts", 
            description="Example prompts and usage patterns for all tools"
        )
        async def get_example_prompts() -> Dict[str, Any]:
            """Return categorized example prompts for discovery."""
            return {
                "basic_operations": {
                    "peek": [
                        "Peek at ./document.pdf to see its structure",
                        "Show me what's in https://arxiv.org/pdf/2301.00234.pdf",
                        "Get an overview of ../reports/annual.pdf"
                    ],
                    "extract": [
                        "Extract text from ./report.pdf as markdown",
                        "Get pages 5-10 from document.pdf",
                        "Convert https://example.com/doc.pdf to text"
                    ],
                    "map": [
                        "Map the structure of ./manual.pdf",
                        "Show the hierarchy of specification.pdf",
                        "Create a navigation map for textbook.pdf"
                    ],
                    "fetch": [
                        "Fetch https://example.com/document.pdf with processed format",
                        "Download ./local/document.pdf with metadata-only format",
                        "Retrieve https://arxiv.org/pdf/paper.pdf with caching"
                    ],
                    "search": [
                        "Search for 'machine learning' in ./research/ using coarse-to-fine",
                        "Find documents about 'contracts' in /legal/ with semantic search",
                        "Locate files containing 'API documentation' in ./docs/ folder"
                    ]
                },
                "advanced_analysis": {
                    "entities": [
                        "Extract all parties and dates from contract.pdf",
                        "Find all people and organizations in report.pdf",
                        "Identify monetary amounts in invoice.pdf"
                    ],
                    "custom": [
                        "Analyze lease.pdf and extract rent, term, and obligations",
                        "Review 10-K.pdf for risk factors and financial metrics",
                        "Extract methodology and conclusions from research.pdf"
                    ],
                    "multimodal": [
                        "Xray presentation.pptx with provider ibm-docling for visual elements",
                        "Analyze infographic.pdf with multimodal analysis enabled",
                        "Extract text from scanned document with hybrid OCR"
                    ],
                    "semantic": [
                        "Search ./documents/ for content similar to 'deep learning algorithms'",
                        "Find related documents using semantic similarity",
                        "Perform RAG-enabled search across document collection"
                    ]
                },
                "by_document_type": {
                    "legal": "Xray contract.pdf to extract parties, terms, obligations, and deadlines",
                    "financial": "Analyze report.pdf for revenue, expenses, and projections",
                    "technical": "Map api_docs.pdf and extract all endpoints and parameters",
                    "academic": "Extract authors, methodology, and findings from paper.pdf",
                    "presentations": "Extract slides and speaker notes from presentation.pptx",
                    "spreadsheets": "Analyze financial_data.xlsx for trends and key metrics",
                    "forms": "Extract form fields and values from application.pdf"
                },
                "provider_specific": {
                    "fast_extraction": "Extract text from document.pdf with provider pymupdf4llm",
                    "ai_analysis": "Xray document.pdf with provider llama-parse",
                    "layout_understanding": "Analyze complex_layout.pdf with provider ibm-docling",
                    "semantic_search": "Search documents with provider mimic-docsray",
                    "auto_selection": "Analyze document.pdf (system chooses best provider)"
                },
                "workflow_examples": {
                    "document_discovery": [
                        "1. Search for relevant documents: Search for 'quarterly reports' in ./finance/",
                        "2. Get overview: Peek at found documents to understand structure",
                        "3. Deep analysis: Xray key documents for entities and insights"
                    ],
                    "content_processing": [
                        "1. Fetch document: Fetch https://example.com/report.pdf",
                        "2. Map structure: Map the document hierarchy and sections",
                        "3. Extract content: Extract specific pages or sections as needed"
                    ],
                    "comparative_analysis": [
                        "1. Search for similar documents across providers",
                        "2. Extract key information using different analysis strategies",
                        "3. Compare results and choose optimal approach"
                    ]
                },
                "advanced_features": {
                    "chunking_and_embedding": "Process large_document.pdf with chunking for semantic search",
                    "reading_order": "Extract content from complex_layout.pdf preserving reading order",
                    "table_extraction": "Extract structured tables from financial_report.pdf",
                    "figure_analysis": "Analyze charts and diagrams in research_paper.pdf",
                    "hybrid_ocr": "Process scanned_document.pdf with AI and traditional OCR",
                    "custom_instructions": "Analyze contract.pdf focusing on termination clauses and penalties"
                }
            }

        # Search tool
        @self.mcp.tool(
            name="docsray_search",
            description="Search for documents in the filesystem using intelligent coarse-to-fine search methodology inspired by MIMIC.DocsRay. Finds documents by content matching and filename patterns."
        )
        async def tool_search(
            query: str = Field(..., description="Search query for finding documents"),
            searchPath: str = Field("./", description="Base path to search within"),
            searchStrategy: str = Field("coarse-to-fine", description="Search strategy (coarse-to-fine, semantic, keyword, hybrid)"),
            fileTypes: List[str] = Field(["pdf", "docx", "md", "txt"], description="File types to include in search"),
            maxResults: int = Field(10, description="Maximum number of results to return"),
            provider: str = Field("auto", description="Provider selection (auto, mimic-docsray, filesystem)")
        ) -> Dict[str, Any]:
            return await search.handle_search(
                query=query,
                search_path=searchPath,
                search_strategy=searchStrategy,
                file_types=fileTypes,
                max_results=maxResults,
                provider=provider,
                registry=self.registry,
                cache=self.cache
            )

        # Seek tool
        @self.mcp.tool(
            name="docsray_seek",
            description="Navigate to specific pages or sections in a document. Jump to page numbers, find sections by name, or search for content. Supports both local files (./path/file.pdf) and URLs (https://example.com/doc.pdf)"
        )
        async def tool_seek(
            document_url: str = Field(..., description="URL or local file path (absolute or relative) to the document"),
            target: Dict[str, Any] = Field(..., description="Navigation target (page, section, or query)"),
            extract_content: bool = Field(True, description="Whether to extract content from the target location"),
            provider: str = Field("auto", description="Provider selection")
        ) -> Dict[str, Any]:
            return await seek.handle_seek(
                document_url=document_url,
                target=target,
                extract_content=extract_content,
                provider=provider,
                registry=self.registry,
                cache=self.cache
            )

        # Peek tool
        @self.mcp.tool(
            name="docsray_peek",
            description="Get quick document overview: page count, format, available extraction formats, provider capabilities. Use this first to understand what's in a document. Works with local files and URLs"
        )
        async def tool_peek(
            document_url: str = Field(..., description="URL or local file path (absolute or relative) to the document"),
            depth: str = Field("structure", description="Level of detail to retrieve"),
            provider: str = Field("auto", description="Provider selection"),
            explanation: Optional[str] = Field(None, description="Optional explanation of why this tool is being called (ignored)")
        ) -> Dict[str, Any]:
            return await peek.handle_peek(
                document_url=document_url,
                depth=depth,
                provider=provider,
                registry=self.registry,
                cache=self.cache
            )

        # Map tool
        @self.mcp.tool(
            name="docsray_map",
            description="Generate complete document structure map showing hierarchy, sections, tables, images. Returns detailed navigation structure. Caches results for fast subsequent access"
        )
        async def tool_map(
            document_url: str = Field(..., description="URL or local file path (absolute or relative) to the document"),
            include_content: bool = Field(False, description="Include content snippets in the map"),
            analysis_depth: str = Field("deep", description="Analysis depth level"),
            provider: str = Field("auto", description="Provider selection"),
            explanation: Optional[str] = Field(None, description="Optional explanation of why this tool is being called (ignored)")
        ) -> Dict[str, Any]:
            return await map.handle_map(
                document_url=document_url,
                include_content=include_content,
                analysis_depth=analysis_depth,
                provider=provider,
                registry=self.registry,
                cache=self.cache
            )

        # Xray tool
        @self.mcp.tool(
            name="docsray_xray",
            description="Deep AI analysis: extract entities (people, orgs, dates, amounts), key points, relationships. Supports custom instructions like 'extract all obligations and deadlines'. Best for contracts, reports, papers"
        )
        async def tool_xray(
            document_url: str = Field(..., description="URL or local file path (absolute or relative) to the document"),
            analysis_type: List[str] = Field(
                ["entities", "key-points"],
                description="Types of analysis to perform"
            ),
            custom_instructions: Optional[str] = Field(None, description="Custom analysis instructions"),
            provider: str = Field("llama-parse", description="Provider selection"),
            explanation: Optional[str] = Field(None, description="Optional explanation of why this tool is being called (ignored)")
        ) -> Dict[str, Any]:
            return await xray.handle_xray(
                document_url=document_url,
                analysis_type=analysis_type,
                custom_instructions=custom_instructions,
                provider=provider,
                registry=self.registry,
                cache=self.cache
            )

        # Extract tool
        @self.mcp.tool(
            name="docsray_extract",
            description="Extract content as markdown, text, or JSON. Extract specific pages, tables, or images. Preserves formatting. Fast for basic extraction, AI-powered for complex needs"
        )
        async def tool_extract(
            document_url: str = Field(..., description="URL or local file path (absolute or relative) to the document"),
            extraction_targets: List[str] = Field(
                ["text"],
                description="Types of content to extract"
            ),
            output_format: str = Field("markdown", description="Output format"),
            pages: Optional[List[int]] = Field(None, description="Specific pages to extract from"),
            provider: str = Field("auto", description="Provider selection"),
            explanation: Optional[str] = Field(None, description="Optional explanation of why this tool is being called (ignored)")
        ) -> Dict[str, Any]:
            return await extract.handle_extract(
                document_url=document_url,
                extraction_targets=extraction_targets,
                output_format=output_format,
                pages=pages,
                provider=provider,
                registry=self.registry,
                cache=self.cache
            )

        # Fetch tool
        @self.mcp.tool(
            name="docsray_fetch",
            description="Fetch documents from web URLs or filesystem paths. Unified document retrieval with caching, progress reporting, and multiple return formats"
        )
        async def tool_fetch(
            source: str = Field(..., description="URL (https://) or filesystem path to fetch"),
            fetch_options: Optional[Dict[str, Any]] = Field(None, description="HTTP headers, timeout, followRedirects settings"),
            cache_strategy: str = Field("use-cache", description="Caching strategy (use-cache, bypass-cache, refresh-cache)"),
            return_format: str = Field("raw", description="Format of returned document (raw, processed, metadata-only)"),
            provider: str = Field("auto", description="Provider selection for processed format")
        ) -> Dict[str, Any]:
            return await fetch.handle_fetch(
                source=source,
                registry=self.registry,
                cache=self.cache,
                fetch_options=fetch_options,
                cache_strategy=cache_strategy,
                return_format=return_format,
                provider=provider
            )

    def _initialize_providers(self) -> None:
        """Initialize enabled providers."""
        # PyMuPDF4LLM provider (always enabled in phase 1)
        if self.config.providers.pymupdf4llm.enabled:
            try:
                from .providers.pymupdf4llm import PyMuPDF4LLMProvider
                provider = PyMuPDF4LLMProvider()
                # Mark as initialized synchronously for now
                provider._initialized = True
                provider.config = self.config.providers.pymupdf4llm
                self.registry.register(provider)
                logger.info("PyMuPDF4LLM provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize PyMuPDF4LLM provider: {e}")

        # LlamaParse provider
        if self.config.providers.llama_parse.enabled:
            try:
                from .providers.llamaparse import LlamaParseProvider
                provider = LlamaParseProvider()
                # Store config for lazy initialization
                provider.config = self.config.providers.llama_parse
                self.registry.register(provider)
                logger.info("LlamaParse provider registered (will initialize on first use)")
            except ModuleNotFoundError as e:
                logger.error(
                    "Failed to register LlamaParse provider: %s. Install optional deps with 'pip install \"docsray-mcp[ai]\"' or 'pip install llama-parse'.",
                    e
                )
            except Exception as e:
                logger.error(f"Failed to register LlamaParse provider: {e}")

        # MIMIC.DocsRay provider
        if self.config.providers.mimic_docsray.enabled:
            try:
                from .providers.mimic_docsray import MimicDocsrayProvider
                provider = MimicDocsrayProvider()
                # Store config for lazy initialization
                provider.config = self.config.providers.mimic_docsray
                self.registry.register(provider)
                logger.info("MIMIC.DocsRay provider registered (will initialize on first use)")
            except Exception as e:
                logger.error(f"Failed to register MIMIC.DocsRay provider: {e}")

        # IBM.Docling provider
        if self.config.providers.ibm_docling.enabled:
            try:
                from .providers.ibm_docling import IBMDoclingProvider
                provider = IBMDoclingProvider()
                # Store config for lazy initialization
                provider.config = self.config.providers.ibm_docling
                self.registry.register(provider)
                logger.info("IBM.Docling provider registered (will initialize on first use)")
            except ModuleNotFoundError as e:
                logger.error(
                    "Failed to register IBM.Docling provider: %s. Install with 'pip install \"docsray-mcp[ai]\"' or 'pip install docling'.",
                    e
                )
            except Exception as e:
                logger.error(f"Failed to register IBM.Docling provider: {e}")

        # Log available providers
        providers = self.registry.list_providers()
        logger.info(f"Available providers: {', '.join(providers)}")

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting Docsray MCP server...")

        if self.config.transport.type == "stdio":
            # Run with stdio transport (default)
            await self.mcp.run_async()
        else:
            # HTTP transport
            await self.mcp.run_async(
                transport="http",
                port=self.config.transport.http_port,
                host=self.config.transport.http_host
            )

    async def shutdown(self) -> None:
        """Shutdown the server and cleanup resources."""
        logger.info("Shutting down Docsray server...")

        # Dispose all providers
        for provider_name in self.registry.list_providers():
            provider = self.registry.get_provider(provider_name)
            if provider:
                await provider.dispose()

        # Clear cache
        await self.cache.clear()

        logger.info("Docsray server shutdown complete")
