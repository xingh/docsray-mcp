"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from docsray.config import (
    DocsrayConfig,
    LlamaParseConfig,
    MistralOCRConfig,
    OCRmyPDFConfig,
    PerformanceConfig,
    ProvidersConfig,
    ProviderType,
    PyMuPDFConfig,
    PyTesseractConfig,
    TransportConfig,
    TransportType,
)


class TestTransportConfig:
    """Test TransportConfig."""
    
    def test_default_values(self):
        config = TransportConfig()
        assert config.type == TransportType.STDIO
        assert config.http_port == 3000
        assert config.http_host == "127.0.0.1"
    
    def test_custom_values(self):
        config = TransportConfig(
            type=TransportType.HTTP,
            http_port=8080,
            http_host="0.0.0.0"
        )
        assert config.type == TransportType.HTTP
        assert config.http_port == 8080
        assert config.http_host == "0.0.0.0"
    
    def test_port_validation(self):
        with pytest.raises(ValueError):
            TransportConfig(http_port=0)
        
        with pytest.raises(ValueError):
            TransportConfig(http_port=70000)


class TestProviderConfigs:
    """Test provider configuration classes."""
    
    def test_pymupdf_config(self):
        config = PyMuPDFConfig()
        assert config.enabled is True
        assert config.page_chunks is True
        assert config.write_images is True
        assert config.extract_words is True
    
    def test_pytesseract_config(self):
        config = PyTesseractConfig(
            enabled=True,
            tesseract_path="/usr/bin/tesseract",
            languages=["eng", "fra"]
        )
        assert config.enabled is True
        assert config.tesseract_path == "/usr/bin/tesseract"
        assert config.languages == ["eng", "fra"]
    
    def test_mistral_ocr_config(self):
        config = MistralOCRConfig(
            enabled=True,
            api_key="test-key",
            base_url="https://api.test.com"
        )
        assert config.enabled is True
        assert config.api_key == "test-key"
        assert config.base_url == "https://api.test.com"
        assert config.model == "mistral-ocr-latest"
    
    def test_llama_parse_config(self):
        config = LlamaParseConfig(
            enabled=True,
            api_key="test-key",
            parsing_mode="premium"
        )
        assert config.enabled is True
        assert config.api_key == "test-key"
        assert config.parsing_mode == "premium"
    
    def test_llama_parse_invalid_mode(self):
        with pytest.raises(ValueError):
            LlamaParseConfig(parsing_mode="invalid")


class TestDocsrayConfig:
    """Test main DocsrayConfig."""
    
    def test_default_values(self):
        config = DocsrayConfig()
        assert config.transport.type == TransportType.STDIO
        assert config.providers.default == ProviderType.AUTO
        assert config.providers.pymupdf4llm.enabled is True
        assert config.performance.cache_enabled is True
        assert config.log_level == "INFO"
    
    def test_from_env_default(self):
        config = DocsrayConfig.from_env()
        assert config.transport.type == TransportType.STDIO
        assert config.providers.default == ProviderType.AUTO
    
    @patch.dict(os.environ, {
        "DOCSRAY_TRANSPORT": "http",
        "DOCSRAY_HTTP_PORT": "8080",
        "DOCSRAY_HTTP_HOST": "0.0.0.0",
        "DOCSRAY_DEFAULT_PROVIDER": "pymupdf4llm",
        "DOCSRAY_PYMUPDF_ENABLED": "false",
        "DOCSRAY_PYTESSERACT_ENABLED": "true",
        "DOCSRAY_TESSERACT_LANGUAGES": "eng,fra,deu",
        "DOCSRAY_CACHE_ENABLED": "false",
        "DOCSRAY_CACHE_TTL": "7200",
        "DOCSRAY_LOG_LEVEL": "DEBUG"
    })
    def test_from_env_custom(self):
        config = DocsrayConfig.from_env()
        
        # Transport
        assert config.transport.type == "http"
        assert config.transport.http_port == 8080
        assert config.transport.http_host == "0.0.0.0"
        
        # Providers
        assert config.providers.default == "pymupdf4llm"
        assert config.providers.pymupdf4llm.enabled is False
        assert config.providers.pytesseract.enabled is True
        assert config.providers.pytesseract.languages == ["eng", "fra", "deu"]
        
        # Performance
        assert config.performance.cache_enabled is False
        assert config.performance.cache_ttl == 7200
        
        # Logging
        assert config.log_level == "DEBUG"
    
    @patch.dict(os.environ, {
        "DOCSRAY_MISTRAL_ENABLED": "true",
        "DOCSRAY_MISTRAL_API_KEY": "test-api-key",
        "DOCSRAY_LLAMAPARSE_ENABLED": "true",
        "DOCSRAY_LLAMAPARSE_API_KEY": "test-llama-key",
        "DOCSRAY_LLAMAPARSE_MODE": "fast"
    })
    def test_from_env_api_providers(self):
        config = DocsrayConfig.from_env()
        
        # Mistral OCR
        assert config.providers.mistral_ocr.enabled is True
        assert config.providers.mistral_ocr.api_key == "test-api-key"
        
        # LlamaParse
        assert config.providers.llama_parse.enabled is True
        assert config.providers.llama_parse.api_key == "test-llama-key"
        assert config.providers.llama_parse.parsing_mode == "fast"