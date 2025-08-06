# Changelog

All notable changes to Docsray MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-08-06

### 🚀 Published to PyPI

- **PyPI Release**: Package now available at [https://pypi.org/project/docsray-mcp/](https://pypi.org/project/docsray-mcp/)
- **TestPyPI Release**: Testing version at [https://test.pypi.org/project/docsray-mcp/](https://test.pypi.org/project/docsray-mcp/)
- **Installation**: `pip install docsray-mcp` or `uvx --from docsray-mcp docsray`
- **Executable**: Package provides `docsray` command (not `docsray-mcp`)

## [0.2.0] - 2025-08-05

### 🎉 Major Features Added

#### LlamaParse Integration
- **New Provider**: Integrated LlamaParse for AI-powered document analysis
- **AI Capabilities**: Advanced entity extraction, relationship mapping, and custom analysis
- **Custom Instructions**: Support for specific analysis criteria and domain-specific requests
- **Advanced Parsing**: Superior handling of complex documents, tables, and layouts

#### Enhanced Caching System
- **Smart Caching**: Comprehensive caching system with .docsray directories
- **Multi-level Cache**: Document-level and operation-specific caching
- **LlamaParse Cache**: Specialized caching for API-based operations to minimize costs
- **Cache Management**: Automatic invalidation and efficient storage

#### Dynamic Provider Discovery
- **Runtime Detection**: Providers auto-discovered based on available dependencies
- **Capability Reporting**: Tools report actual capabilities based on enabled providers
- **Graceful Fallbacks**: Automatic fallback to available providers
- **Status Monitoring**: Real-time provider health and availability checking

### 🛠️ Tools and Functionality

#### Five Core Tools
- **docsray_peek**: Quick document overview with format detection and provider capabilities
- **docsray_map**: Comprehensive document structure mapping with caching
- **docsray_xray**: AI-powered deep analysis extracting entities, relationships, and insights
- **docsray_extract**: Content extraction in multiple formats (markdown, text, JSON, tables)
- **docsray_seek**: Navigation to specific pages, sections, or content search

#### Multi-Provider Architecture
- **PyMuPDF4LLM**: Lightning-fast PDF processing (always enabled as fallback)
  - Fast markdown extraction
  - Basic table detection
  - Multi-page support
  - Local processing (no API required)
- **LlamaParse**: Deep document understanding with LLMs
  - AI-powered entity extraction
  - Custom analysis instructions
  - Rich format preservation
  - Comprehensive caching

### 🚀 Performance and Reliability

#### Testing Infrastructure
- **Comprehensive Test Suite**: 52 tests with >90% coverage
- **Test Categories**: Unit tests (no API calls), integration tests, manual testing scripts
- **Continuous Integration**: Automated testing with pytest, coverage reporting
- **Mock Testing**: Extensive mocking for reliable unit tests

#### Error Handling and Logging
- **Robust Error Handling**: Comprehensive error catching with helpful messages
- **Structured Logging**: Configurable logging levels with detailed operation traces
- **Timeout Management**: Configurable timeouts for all operations
- **Provider Failover**: Automatic provider switching on failures

### 🔧 Configuration and Environment

#### Environment Variables
- **Provider Configuration**: Control provider enablement and behavior
- **Performance Tuning**: Configurable cache TTL, concurrent requests, timeouts
- **Logging Control**: Adjustable log levels and output formatting
- **API Key Management**: Secure API key handling for external providers

#### Installation Methods
- **uvx Support**: Direct execution without installation via `uvx docsray-mcp`
- **Global Installation**: System-wide installation with `uv tool install`
- **Pip Installation**: Traditional pip install with optional dependencies
- **Development Mode**: Editable installation for contributors

### 🌐 Input and Output Support

#### Universal Input Support
- **Local Files**: Relative paths (./path, ../path) and absolute paths (/absolute)
- **Internet URLs**: Direct HTTPS URLs to publicly accessible documents
- **Format Detection**: Automatic format detection and validation
- **Security**: Secure HTTPS downloads with certificate verification

#### Multiple Output Formats
- **Markdown**: Rich markdown with preserved formatting
- **Plain Text**: Clean text extraction without formatting
- **JSON**: Structured data output for programmatic use
- **Tables**: Specialized table extraction and formatting

### 🏗️ Architecture Improvements

#### Modular Design
- **Provider Interface**: Clean provider abstraction for easy extension
- **Tool Separation**: Each tool implemented as separate module
- **Configuration Management**: Centralized configuration with validation
- **Cache Utilities**: Reusable caching components

#### MCP Integration
- **FastMCP Framework**: Built on FastMCP for robust MCP protocol support
- **Resource Discovery**: Built-in resources for MCP client discovery
- **Tool Registration**: Dynamic tool registration based on provider availability
- **Protocol Compliance**: Full MCP specification compliance

### 📚 Documentation

#### Comprehensive Documentation
- **README.md**: Complete setup and usage guide
- **PROMPTS.md**: Extensive prompt examples for all tools
- **SYSTEM_INSTRUCTIONS.md**: Detailed system capabilities and usage patterns
- **CONTRIBUTING.md**: Developer guidelines and contribution process
- **API Reference**: Detailed tool parameter documentation

#### Examples and Use Cases
- **Legal Documents**: Contract analysis, entity extraction, obligation mapping
- **Technical Documentation**: API documentation processing, requirement extraction
- **Financial Reports**: Metric extraction, table processing, risk analysis
- **Academic Papers**: Methodology extraction, citation finding, research analysis

### 🔒 Security and Privacy

#### Data Protection
- **Local Processing**: PyMuPDF4LLM processes files entirely locally
- **API Key Security**: Keys never exposed in responses or logs
- **Cache Control**: User-controlled local .docsray cache directories
- **Data Isolation**: Each document gets isolated cache directory

#### Network Security
- **HTTPS Enforcement**: All URL downloads use secure HTTPS
- **Certificate Verification**: Proper SSL/TLS certificate validation
- **No Permanent Storage**: Only cached with explicit user consent

### 🐛 Bug Fixes

- Fixed provider detection and initialization edge cases
- Improved error messages for better user experience
- Resolved caching conflicts between different providers
- Fixed timeout handling for large document processing
- Corrected provider capability reporting accuracy

### 🔄 Breaking Changes

- **Provider Names**: Standardized provider naming (pymupdf4llm, llama-parse)
- **Configuration**: New environment variable naming convention
- **Cache Structure**: Updated cache directory structure (.docsray format)
- **Tool Parameters**: Refined parameter validation and naming

### 📦 Dependencies

#### Core Dependencies
- `fastmcp>=2.11.1` - MCP server framework
- `pymupdf4llm>=0.0.17` - Fast PDF processing
- `httpx>=0.27.0` - HTTP client for URL downloads
- `pydantic>=2.0.0` - Data validation and settings
- `python-dotenv>=1.0.0` - Environment variable loading

#### Optional Dependencies
- `llama-parse>=0.6.0` - AI-powered document parsing (ai extra)
- `pytesseract>=0.3.10` - OCR capabilities (ocr extra)
- `pytest>=8.0.0` - Testing framework (dev extra)
- `black>=24.0.0` - Code formatting (dev extra)

### 🚀 Performance Improvements

- **Caching**: Up to 100x faster repeated operations with intelligent caching
- **Concurrent Processing**: Configurable concurrent request handling
- **Memory Optimization**: Efficient memory usage for large documents
- **Provider Selection**: Intelligent provider selection for optimal performance

### 🎯 Future Roadmap

#### Planned Features (Version 0.3.0)
- **PyTesseract Provider**: OCR support for scanned documents
- **Mistral OCR Provider**: AI-powered OCR and analysis
- **Batch Processing**: Multi-document batch operations
- **Advanced Analytics**: Document comparison and analysis tools

#### Long-term Goals
- **Image Processing**: Enhanced image extraction and analysis
- **Multi-modal Analysis**: Combined text, image, and table analysis
- **Plugin System**: Third-party provider plugin architecture
- **Cloud Integration**: Support for cloud storage providers

---

## [0.1.0] - 2025-08-04

### 🎉 Initial Release

#### Core Framework
- **MCP Server**: Basic Model Context Protocol server implementation
- **FastMCP Integration**: Built on FastMCP framework for robust protocol support
- **Provider Architecture**: Extensible provider system for document processing

#### Basic Features
- **PyMuPDF4LLM Provider**: Fast PDF processing and text extraction
- **Basic Tools**: Initial implementation of document processing tools
- **Configuration System**: Environment-based configuration management
- **Error Handling**: Basic error handling and logging

#### Documentation
- **README**: Basic setup and usage instructions
- **License**: Apache 2.0 license for open source usage

---

## Contributing

For details on contributing to this project, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.