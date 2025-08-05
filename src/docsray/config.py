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


class ProvidersConfig(BaseModel):
    default: ProviderType = Field(default=ProviderType.AUTO)
    pymupdf4llm: PyMuPDFConfig = Field(default_factory=PyMuPDFConfig)
    pytesseract: PyTesseractConfig = Field(default_factory=PyTesseractConfig)
    ocrmypdf: OCRmyPDFConfig = Field(default_factory=OCRmyPDFConfig)
    mistral_ocr: MistralOCRConfig = Field(default_factory=MistralOCRConfig)
    llama_parse: LlamaParseConfig = Field(default_factory=LlamaParseConfig)


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
