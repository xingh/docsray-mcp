"""Configuration management for Docsray MCP server."""

import os
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class TransportType(str, Enum):
    STDIO = "stdio"
    HTTP = "http"


class ProviderType(str, Enum):
    AUTO = "auto"
    PYMUPDF4LLM = "pymupdf4llm"
    PYTESSERACT = "pytesseract"
    OCRMYPDF = "ocrmypdf"
    MISTRAL_OCR = "mistral-ocr"
    LLAMA_PARSE = "llama-parse"
    MIMIC_DOCSRAY = "mimic-docsray"
    IBM_DOCLING = "ibm-docling"


class TransportConfig(BaseModel):
    type: TransportType = Field(default=TransportType.STDIO)
    http_port: int = Field(default=3000, ge=1, le=65535)
    http_host: str = Field(default="127.0.0.1")


class PyMuPDFConfig(BaseModel):
    enabled: bool = Field(default=True)
    page_chunks: bool = Field(default=True)
    write_images: bool = Field(default=True)
    extract_words: bool = Field(default=True)


class PyTesseractConfig(BaseModel):
    enabled: bool = Field(default=False)
    tesseract_path: Optional[str] = Field(default=None)
    languages: list[str] = Field(default_factory=lambda: ["eng"])


class OCRmyPDFConfig(BaseModel):
    enabled: bool = Field(default=False)
    optimize: int = Field(default=1, ge=0, le=3)
    skip_text: bool = Field(default=True)
    force_ocr: bool = Field(default=False)


class MistralOCRConfig(BaseModel):
    enabled: bool = Field(default=False)
    api_key: Optional[str] = Field(default=None)
    base_url: str = Field(default="https://api.mistral.ai")
    model: str = Field(default="mistral-ocr-latest")


class LlamaParseConfig(BaseModel):
    enabled: bool = Field(default=False)
    api_key: Optional[str] = Field(default=None)
    mode: str = Field(default="balanced")

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        if v not in ["fast", "balanced", "premium"]:
            raise ValueError("mode must be 'fast', 'balanced', or 'premium'")
        return v


class MimicDocsrayConfig(BaseModel):
    enabled: bool = Field(default=False)
    api_key: Optional[str] = Field(default=None)
    base_url: str = Field(default="https://api.docsray.com")
    model: str = Field(default="docsray-v1")
    chunk_size: int = Field(default=1000, ge=100, le=10000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    max_chunks: int = Field(default=100, ge=10, le=1000)
    search_depth: str = Field(default="deep")
    semantic_ranking: bool = Field(default=True)
    multimodal_analysis: bool = Field(default=True)
    hybrid_ocr: bool = Field(default=True)
    tesseract_path: Optional[str] = Field(default=None)
    coarse_to_fine: bool = Field(default=True)
    rag_enabled: bool = Field(default=True)
    vector_store_type: str = Field(default="faiss")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")

    @field_validator("search_depth")
    @classmethod
    def validate_search_depth(cls, v: str) -> str:
        if v not in ["basic", "deep", "comprehensive"]:
            raise ValueError("search_depth must be 'basic', 'deep', or 'comprehensive'")
        return v

    @field_validator("vector_store_type")
    @classmethod
    def validate_vector_store_type(cls, v: str) -> str:
        if v not in ["faiss", "chroma", "pinecone", "memory"]:
            raise ValueError("vector_store_type must be 'faiss', 'chroma', 'pinecone', or 'memory'")
        return v


class IBMDoclingConfig(BaseModel):
    """IBM.Docling provider configuration."""
    enabled: bool = Field(default=False)
    use_vlm: bool = Field(default=True, description="Use Visual Language Model for document understanding")
    use_asr: bool = Field(default=False, description="Use Automatic Speech Recognition for audio files")
    output_format: str = Field(default="DoclingDocument", description="Output format: DoclingDocument, markdown, json")
    ocr_enabled: bool = Field(default=True, description="Enable OCR for scanned documents")
    table_detection: bool = Field(default=True, description="Enable advanced table detection")
    figure_detection: bool = Field(default=True, description="Enable figure and image classification")

    # Advanced layout understanding options
    layout_model: Optional[str] = Field(default=None, description="Custom layout analysis model")
    reading_order: bool = Field(default=True, description="Preserve reading order in output")

    # Performance settings
    batch_size: int = Field(default=1, ge=1, le=10, description="Batch size for processing multiple documents")
    max_pages: Optional[int] = Field(default=None, ge=1, description="Maximum pages to process per document")

    # Model settings
    device: Optional[str] = Field(default=None, description="Device for model execution (cpu, cuda, etc.)")
    model_path: Optional[str] = Field(default=None, description="Custom model path")

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        if v not in ["DoclingDocument", "markdown", "json"]:
            raise ValueError("output_format must be 'DoclingDocument', 'markdown', or 'json'")
        return v


class ProvidersConfig(BaseModel):
    default: ProviderType = Field(default=ProviderType.AUTO)
    pymupdf4llm: PyMuPDFConfig = Field(default_factory=PyMuPDFConfig)
    pytesseract: PyTesseractConfig = Field(default_factory=PyTesseractConfig)
    ocrmypdf: OCRmyPDFConfig = Field(default_factory=OCRmyPDFConfig)
    mistral_ocr: MistralOCRConfig = Field(default_factory=MistralOCRConfig)
    llama_parse: LlamaParseConfig = Field(default_factory=LlamaParseConfig)
    mimic_docsray: MimicDocsrayConfig = Field(default_factory=MimicDocsrayConfig)
    ibm_docling: IBMDoclingConfig = Field(default_factory=IBMDoclingConfig)


class PerformanceConfig(BaseModel):
    cache_enabled: bool = Field(default=True)
    cache_ttl: int = Field(default=3600, ge=0)
    max_concurrent_requests: int = Field(default=10, ge=1)
    timeout_seconds: int = Field(default=120, ge=1)


class DocsrayConfig(BaseModel):
    """Main configuration for Docsray MCP server."""

    transport: TransportConfig = Field(default_factory=TransportConfig)
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    log_level: str = Field(default="INFO")

    @classmethod
    def from_env(cls) -> "DocsrayConfig":
        """Create configuration from environment variables."""
        config_dict: Dict[str, Any] = {
            "transport": {
                "type": os.getenv("DOCSRAY_TRANSPORT", "stdio"),
                "http_port": int(os.getenv("DOCSRAY_HTTP_PORT", "3000")),
                "http_host": os.getenv("DOCSRAY_HTTP_HOST", "127.0.0.1"),
            },
            "providers": {
                "default": os.getenv("DOCSRAY_DEFAULT_PROVIDER", "auto"),
                "pymupdf4llm": {
                    "enabled": os.getenv("DOCSRAY_PYMUPDF_ENABLED", "true").lower() == "true",
                },
                "pytesseract": {
                    "enabled": os.getenv("DOCSRAY_PYTESSERACT_ENABLED", "false").lower() == "true",
                    "tesseract_path": os.getenv("DOCSRAY_TESSERACT_PATH"),
                    "languages": os.getenv("DOCSRAY_TESSERACT_LANGUAGES", "eng").split(","),
                },
                "ocrmypdf": {
                    "enabled": os.getenv("DOCSRAY_OCRMYPDF_ENABLED", "false").lower() == "true",
                },
                "mistral_ocr": {
                    "enabled": os.getenv("DOCSRAY_MISTRAL_ENABLED", "false").lower() == "true",
                    "api_key": os.getenv("DOCSRAY_MISTRAL_API_KEY"),
                    "base_url": os.getenv("DOCSRAY_MISTRAL_BASE_URL", "https://api.mistral.ai"),
                },
                "llama_parse": {
                    "enabled": os.getenv("DOCSRAY_LLAMAPARSE_ENABLED", "false").lower() == "true",
                    "api_key": os.getenv("DOCSRAY_LLAMAPARSE_API_KEY"),
                    "mode": os.getenv("DOCSRAY_LLAMAPARSE_MODE", "balanced"),
                },
                "mimic_docsray": {
                    "enabled": os.getenv("DOCSRAY_MIMIC_ENABLED", "false").lower() == "true",
                    "api_key": os.getenv("DOCSRAY_MIMIC_API_KEY"),
                    "base_url": os.getenv("DOCSRAY_MIMIC_BASE_URL", "https://api.docsray.com"),
                    "model": os.getenv("DOCSRAY_MIMIC_MODEL", "docsray-v1"),
                    "chunk_size": int(os.getenv("DOCSRAY_MIMIC_CHUNK_SIZE", "1000")),
                    "chunk_overlap": int(os.getenv("DOCSRAY_MIMIC_CHUNK_OVERLAP", "200")),
                    "max_chunks": int(os.getenv("DOCSRAY_MIMIC_MAX_CHUNKS", "100")),
                    "search_depth": os.getenv("DOCSRAY_MIMIC_SEARCH_DEPTH", "deep"),
                    "semantic_ranking": os.getenv("DOCSRAY_MIMIC_SEMANTIC_RANKING", "true").lower() == "true",
                    "multimodal_analysis": os.getenv("DOCSRAY_MIMIC_MULTIMODAL", "true").lower() == "true",
                    "hybrid_ocr": os.getenv("DOCSRAY_MIMIC_HYBRID_OCR", "true").lower() == "true",
                    "tesseract_path": os.getenv("DOCSRAY_MIMIC_TESSERACT_PATH"),
                    "coarse_to_fine": os.getenv("DOCSRAY_MIMIC_COARSE_TO_FINE", "true").lower() == "true",
                    "rag_enabled": os.getenv("DOCSRAY_MIMIC_RAG_ENABLED", "true").lower() == "true",
                    "vector_store_type": os.getenv("DOCSRAY_MIMIC_VECTOR_STORE", "faiss"),
                    "embedding_model": os.getenv("DOCSRAY_MIMIC_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
                },
                "ibm_docling": {
                    "enabled": os.getenv("DOCSRAY_IBM_DOCLING_ENABLED", "false").lower() == "true",
                    "use_vlm": os.getenv("DOCSRAY_IBM_DOCLING_USE_VLM", "true").lower() == "true",
                    "use_asr": os.getenv("DOCSRAY_IBM_DOCLING_USE_ASR", "false").lower() == "true",
                    "output_format": os.getenv("DOCSRAY_IBM_DOCLING_OUTPUT_FORMAT", "DoclingDocument"),
                    "ocr_enabled": os.getenv("DOCSRAY_IBM_DOCLING_OCR_ENABLED", "true").lower() == "true",
                    "table_detection": os.getenv("DOCSRAY_IBM_DOCLING_TABLE_DETECTION", "true").lower() == "true",
                    "figure_detection": os.getenv("DOCSRAY_IBM_DOCLING_FIGURE_DETECTION", "true").lower() == "true",
                    "layout_model": os.getenv("DOCSRAY_IBM_DOCLING_LAYOUT_MODEL"),
                    "reading_order": os.getenv("DOCSRAY_IBM_DOCLING_READING_ORDER", "true").lower() == "true",
                    "batch_size": int(os.getenv("DOCSRAY_IBM_DOCLING_BATCH_SIZE", "1")),
                    "max_pages": int(os.getenv("DOCSRAY_IBM_DOCLING_MAX_PAGES")) if os.getenv("DOCSRAY_IBM_DOCLING_MAX_PAGES") else None,
                    "device": os.getenv("DOCSRAY_IBM_DOCLING_DEVICE"),
                    "model_path": os.getenv("DOCSRAY_IBM_DOCLING_MODEL_PATH"),
                },
            },
            "performance": {
                "cache_enabled": os.getenv("DOCSRAY_CACHE_ENABLED", "true").lower() == "true",
                "cache_ttl": int(os.getenv("DOCSRAY_CACHE_TTL", "3600")),
                "max_concurrent_requests": int(os.getenv("DOCSRAY_MAX_CONCURRENT_REQUESTS", "10")),
                "timeout_seconds": int(os.getenv("DOCSRAY_TIMEOUT_SECONDS", "120")),
            },
            "log_level": os.getenv("DOCSRAY_LOG_LEVEL", "INFO"),
        }

        return cls(**config_dict)
