# 🔍 Docsray MCP Server

[![PyPI](https://img.shields.io/pypi/v/docsray-mcp)](https://pypi.org/project/docsray-mcp/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://github.com/anthropics/mcp)
[![Status](https://img.shields.io/badge/Status-Working-brightgreen.svg)](https://github.com/docsray/docsray-mcp)

**Docsray** is a powerful Model Context Protocol (MCP) server that gives AI assistants like Claude advanced document perception capabilities. Extract text, navigate pages, analyze structure, and understand any document with ease.

**✅ Status: Phase 1 Complete - Working in Cursor and other MCP clients**

## ✨ Features

### 🎯 Five Powerful Tools

1. **`docsray_extract`** - Extract content in multiple formats (text, tables, images)
2. **`docsray_seek`** - Navigate to specific pages or sections
3. **`docsray_peek`** - Get document overview and metadata without full extraction
4. **`docsray_map`** - Generate comprehensive document structure maps
5. **`docsray_xray`** - AI-powered deep document analysis (with compatible providers)

### 🔌 Multi-Provider Architecture

- **PyMuPDF4LLM** - Lightning-fast PDF processing (included by default)
- **PyTesseract** - OCR for scanned documents
- **OCRmyPDF** - Advanced OCR with PDF optimization
- **Mistral OCR** - AI-powered OCR and analysis
- **LlamaParse** - Deep document understanding with LLMs

### 🚀 Key Benefits

- **Universal Format Support** - PDFs, images, Office docs, and more
- **Intelligent Provider Selection** - Automatically chooses the best tool for each document
- **High Performance** - Built-in caching and parallel processing
- **Production Ready** - Comprehensive error handling and logging
- **Easy Integration** - Works seamlessly with Claude Desktop and other MCP clients

## 📦 Installation

### Quick Start with uvx (Recommended)

```bash
# Run directly without installation
uvx docsray-mcp

# Or install globally
uv tool install docsray-mcp
```

### Using pip

```bash
pip install docsray-mcp

# With OCR support
pip install "docsray-mcp[ocr]"

# With AI providers
pip install "docsray-mcp[ai]"

# Everything
pip install "docsray-mcp[all]"
```

## 🚀 Integration

### Cursor Integration (Confirmed Working ✅)

Add to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "python",
      "args": ["-m", "docsray.server"],
      "env": {
        "DOCSRAY_PYMUPDF_ENABLED": "true"
      }
    }
  }
}
```

### Claude Desktop Integration

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "docsray": {
      "command": "uvx",
      "args": ["docsray-mcp"],
      "env": {
        "DOCSRAY_PYMUPDF_ENABLED": "true"
      }
    }
  }
}
```

### With API Keys (for AI providers)

```json
{
  "mcpServers": {
    "docsray": {
      "command": "uvx",
      "args": ["docsray-mcp"],
      "env": {
        "DOCSRAY_MISTRAL_ENABLED": "true",
        "DOCSRAY_MISTRAL_API_KEY": "your-mistral-api-key",
        "DOCSRAY_LLAMAPARSE_ENABLED": "true",
        "DOCSRAY_LLAMAPARSE_API_KEY": "your-llamaparse-api-key"
      }
    }
  }
}
```

## 💡 Usage Examples

### Supported Input Formats

Docsray supports multiple ways to reference documents:

- **URLs**: `https://example.com/document.pdf`
- **Absolute paths**: `/home/user/documents/report.pdf`
- **Relative paths**: `./documents/report.pdf` or `../shared/report.pdf`
- **Home directory paths**: `~/Documents/report.pdf`

### Extract Text from a PDF

```python
# In Claude - using local file
result = await use_mcp_tool("docsray", "docsray_extract", {
  "document_url": "./documents/report.pdf",
  "extraction_targets": ["text", "tables"],
  "output_format": "markdown"
})

# Or using a URL
result = await use_mcp_tool("docsray", "docsray_extract", {
  "document_url": "https://example.com/document.pdf",
  "extraction_targets": ["text", "tables"],
  "output_format": "markdown"
})
```

### Navigate to a Specific Page

```python
result = await use_mcp_tool("docsray", "docsray_seek", {
  "document_url": "~/Documents/manual.pdf",
  "target": {"page": 5},
  "extract_content": true
})
```

### Get Document Overview

```python
result = await use_mcp_tool("docsray", "docsray_peek", {
  "document_url": "../shared/contract.pdf",
  "depth": "structure"
})
```

### Generate Document Map

```python
result = await use_mcp_tool("docsray", "docsray_map", {
  "document_url": "/path/to/document.pdf",
  "include_content": false,
  "analysis_depth": "deep"
})
```

### AI-Powered Analysis

```python
result = await use_mcp_tool("docsray", "docsray_xray", {
  "document_url": "https://example.com/research-paper.pdf",
  "analysis_type": ["entities", "key-points", "sentiment"],
  "provider": "mistral-ocr"
})
```

## 🎯 Real-World Use Cases

### 📊 Financial Analysis
Extract tables from financial reports, analyze trends, and identify key metrics across multiple documents.

### 📚 Research Assistant
Navigate academic papers, extract citations, and summarize findings from large document collections.

### 📋 Contract Review
Analyze legal documents, extract key terms, and identify important clauses with AI assistance.

### 🏢 Invoice Processing
Extract data from invoices and receipts, with OCR support for scanned documents.

### 📖 Content Migration
Convert legacy documents to modern formats while preserving structure and formatting.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Provider Selection
DOCSRAY_DEFAULT_PROVIDER=auto  # auto, pymupdf4llm, mistral-ocr, etc.

# PyMuPDF4LLM (enabled by default)
DOCSRAY_PYMUPDF_ENABLED=true

# OCR Providers
DOCSRAY_PYTESSERACT_ENABLED=true
DOCSRAY_TESSERACT_LANGUAGES=eng,fra,deu
DOCSRAY_OCRMYPDF_ENABLED=true

# AI Providers
DOCSRAY_MISTRAL_ENABLED=true
DOCSRAY_MISTRAL_API_KEY=your-api-key
DOCSRAY_LLAMAPARSE_ENABLED=true
DOCSRAY_LLAMAPARSE_API_KEY=your-api-key

# Performance
DOCSRAY_CACHE_ENABLED=true
DOCSRAY_CACHE_TTL=3600
DOCSRAY_MAX_CONCURRENT_REQUESTS=10
```

## 🛠️ CLI Commands

```bash
# Start the server
docsray start

# List available providers
docsray list-providers

# Test a provider
docsray test --provider pymupdf4llm --document sample.pdf

# Start with specific transport
docsray start --transport http --port 8080
```

## 📊 Provider Comparison

| Provider | Formats | OCR | AI Analysis | Speed | Best For |
|----------|---------|-----|-------------|-------|----------|
| PyMuPDF4LLM | PDF, XPS, EPUB | ❌ | ❌ | ⚡⚡⚡ | Fast text extraction |
| PyTesseract | Images, PDF | ✅ | ❌ | ⚡ | Scanned documents |
| OCRmyPDF | PDF | ✅ | ❌ | ⚡⚡ | PDF optimization |
| Mistral OCR | PDF, Images, DOCX | ✅ | ✅ | ⚡⚡ | Complex layouts |
| LlamaParse | PDF, DOCX, PPTX | ✅ | ✅ | ⚡ | Deep understanding |

## 🔧 Advanced Features

### Caching
Documents are automatically cached to improve performance for repeated operations.

### Provider Fallback
If one provider fails, Docsray automatically tries alternative providers.

### Parallel Processing
Multiple documents can be processed concurrently for better throughput.

### Custom Provider Selection
Force specific providers for specialized tasks:

```python
result = await use_mcp_tool("docsray", "docsray_extract", {
  "document_url": "scanned.pdf",
  "provider": "ocrmypdf"  # Force OCR provider
})
```

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Clone the repository
git clone https://github.com/docsray/docsray-mcp
cd docsray-mcp

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/
```

## 📚 Documentation

- [Quick Start Guide](docs/quickstart.md)
- [API Reference](docs/api-reference.md)
- [Provider Documentation](docs/providers.md)
- [Examples](examples/)

## 🛣️ Roadmap

- [x] Phase 1: Core MCP server with PyMuPDF4LLM
- [ ] Phase 2: OCR providers (PyTesseract, OCRmyPDF)
- [ ] Phase 3: AI providers (Mistral, LlamaParse)
- [ ] Phase 4: Advanced features (streaming, batch processing)
- [ ] Phase 5: Plugin SDK for custom providers

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- [FastMCP](https://github.com/anthropics/fastmcp) - Rapid MCP server development
- [PyMuPDF4LLM](https://github.com/pymupdf/pymupdf4llm) - PDF processing
- [Model Context Protocol](https://github.com/anthropics/mcp) - AI integration standard

## 📞 Support

- 📧 Email: support@docsray.dev
- 💬 Discord: [Join our community](https://discord.gg/docsray)
- 🐛 Issues: [GitHub Issues](https://github.com/docsray/docsray-mcp/issues)
- 📖 Docs: [docs.docsray.dev](https://docs.docsray.dev)

---

<p align="center">
  Made with ❤️ by the Docsray Team
</p>

<p align="center">
  <a href="https://github.com/docsray/docsray-mcp/stargazers">⭐ Star us on GitHub!</a>
</p>