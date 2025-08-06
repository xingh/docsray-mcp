"""Main Docsray MCP server implementation using FastMCP."""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .config import DocsrayConfig
from .providers.registry import ProviderRegistry
from .tools import extract, map, peek, seek, xray
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
                    providers.append({
                        "name": name,
                        "status": "active" if provider._initialized else "registered",
                        "capabilities": provider.get_capabilities().__dict__ if hasattr(provider, 'get_capabilities') else {}
                    })
            
            return {
                "name": "docsray",
                "version": "1.0.0",
                "description": "AI-powered document processing MCP server",
                "capabilities": {
                    "document_formats": ["pdf", "docx", "doc", "txt", "md"],
                    "input_sources": ["local_files", "urls"],
                    "extraction_formats": ["markdown", "text", "json"],
                    "analysis_types": ["entities", "key_points", "structure", "relationships"],
                    "providers": providers
                },
                "usage_examples": {
                    "quick_overview": "Peek at document.pdf to see its structure",
                    "entity_extraction": "Xray contract.pdf and extract all parties and dates",
                    "structure_mapping": "Map the complete hierarchy of manual.pdf",
                    "content_extraction": "Extract pages 5-10 from report.pdf as markdown",
                    "url_processing": "Analyze https://example.com/document.pdf"
                },
                "best_practices": [
                    "Start with peek to understand document structure",
                    "Use xray for AI-powered analysis",
                    "Use extract for fast content retrieval",
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
                    ]
                },
                "by_document_type": {
                    "legal": "Xray contract.pdf to extract parties, terms, obligations, and deadlines",
                    "financial": "Analyze report.pdf for revenue, expenses, and projections",
                    "technical": "Map api_docs.pdf and extract all endpoints and parameters",
                    "academic": "Extract authors, methodology, and findings from paper.pdf"
                },
                "provider_specific": {
                    "fast_extraction": "Extract text from document.pdf with provider pymupdf4llm",
                    "ai_analysis": "Xray document.pdf with provider llama-parse",
                    "auto_selection": "Analyze document.pdf (system chooses best provider)"
                }
            }
        
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
            except Exception as e:
                logger.error(f"Failed to register LlamaParse provider: {e}")

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
