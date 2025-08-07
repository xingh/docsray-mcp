# 🔍 Docsray MCP Server

[![PyPI](https://img.shields.io/pypi/v/docsray-mcp)](https://pypi.org/project/docsray-mcp/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://github.com/anthropics/mcp)
[![Status](https://img.shields.io/badge/Status-Working-brightgreen.svg)](https://github.com/docsray/docsray-mcp)
[![Netlify Status](https://api.netlify.com/api/v1/badges/6065d1ba-7e6c-49fa-a97e-9cada2cbc00a/deploy-status)](https://app.netlify.com/projects/docsray/deploys)

**Docsray** is a powerful Model Context Protocol (MCP) server that gives AI assistants like Claude advanced document perception capabilities. Extract text, navigate pages, analyze structure, and understand any document with ease.

**✅ Status: Published to PyPI and TestPyPI - Working in Cursor, Claude Desktop, and other MCP clients**

## ✨ Features

### 🎯 Five Powerful Tools

1. **`docsray_peek`** - Quick document overview with format detection and provider capabilities
2. **`docsray_map`** - Generate comprehensive document structure maps with caching
3. **`docsray_xray`** - AI-powered deep analysis extracting entities, relationships, and insights
4. **`docsray_extract`** - Extract content in multiple formats (markdown, text, JSON, tables)
5. **`docsray_seek`** - Navigate to specific pages, sections, or search for content

### 🔌 Multi-Provider Architecture

- **PyMuPDF4LLM** - Lightning-fast PDF processing (✅ Implemented)
  - Fast markdown extraction
  - Basic table detection
  - Multi-page support
  - Always enabled as fallback

- **LlamaParse** - Deep document understanding with LLMs (✅ Implemented)
  - AI-powered entity extraction
  - Custom analysis instructions
  - Comprehensive caching in .docsray directories
  - Rich format preservation (markdown, images, tables)

- **PyTesseract** - OCR for scanned documents (🔄 Planned)
- **Mistral OCR** - AI-powered OCR and analysis (🔄 Planned)

### 🚀 Key Benefits

- **Universal Input Support** - Local files (./path, ../path, /absolute) and URLs (https://)
- **Intelligent Provider Selection** - Automatically chooses the best tool for each task
- **Smart Caching** - LlamaParse results cached in .docsray directories for instant access
- **Dynamic Discovery** - Tools report actual capabilities based on what's enabled
- **Production Ready** - Comprehensive error handling, logging, and 56 tests
- **Self-Documenting** - Built-in resources for discovery by MCP clients

## 📦 Installation

### Quick Start with uvx (Recommended)

```bash
# Run directly without installation
uvx docsray-mcp start

# Or install globally
uv tool install docsray-mcp
# Then run with:
docsray start
# or
docsray-mcp start
```

### Alternative: Install with pip

```bash
# Basic installation (PyMuPDF4LLM only)
pip install docsray-mcp

# With LlamaParse for AI analysis
pip install "docsray-mcp[ai]"

# Development installation
pip install -e ".[dev]"
```

## 🚀 Quick Start

### 1. Set up API Keys (Optional but Recommended)

Create a `.env` file in your project:

```bash
# For AI-powered analysis with LlamaParse
LLAMAPARSE_API_KEY=llx-your-key-here

# Or use environment variables
export LLAMAPARSE_API_KEY=llx-your-key-here
```

Get your free LlamaParse API key at [cloud.llamaindex.ai](https://cloud.llamaindex.ai)

### 2. Configure with Your MCP Client

#### For Cursor

Add to your Cursor settings:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "uvx",
      "args": ["docsray-mcp"],
      "env": {
        "LLAMAPARSE_API_KEY": "llx-your-key-here"
      }
    }
  }
}
```

#### For Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "uvx",
      "args": ["docsray-mcp"],
      "env": {
        "LLAMAPARSE_API_KEY": "llx-your-key-here"
      }
    }
  }
}
```

## 📚 Usage Examples

### Basic Document Overview

```
Peek at ./document.pdf to see its structure and available formats
```

### Extract Entities from Contracts

```
Xray ./contract.pdf and extract all parties, dates, payment terms, and obligations
```

### Navigate Documents

```
Map the complete structure of ./manual.pdf including all sections and subsections
```

### Extract Specific Content

```
Extract pages 10-20 from ./report.pdf as markdown
```

### Analyze Web Documents

```
Analyze https://arxiv.org/pdf/2301.00234.pdf for methodology and key findings
```

### Compare Providers

```
Extract text from document.pdf with provider pymupdf4llm (fast)
Xray document.pdf with provider llama-parse (AI analysis)
```

## 🛠️ Advanced Configuration

### Environment Variables

```bash
# Provider Configuration
DOCSRAY_PYMUPDF4LLM_ENABLED=true  # Always true by default
DOCSRAY_LLAMAPARSE_ENABLED=true
LLAMAPARSE_API_KEY=llx-your-key

# Performance Tuning
DOCSRAY_CACHE_ENABLED=true
DOCSRAY_CACHE_TTL=3600
DOCSRAY_MAX_CONCURRENT_REQUESTS=5
DOCSRAY_TIMEOUT_SECONDS=30

# Logging
DOCSRAY_LOG_LEVEL=INFO
```

### Provider Capabilities

#### PyMuPDF4LLM (Always Available)
- ✅ Fast text extraction
- ✅ Markdown formatting
- ✅ Basic table detection
- ✅ Multi-page support
- ❌ No AI analysis
- ❌ No OCR

#### LlamaParse (When API Key Configured)
- ✅ AI-powered analysis
- ✅ Entity extraction
- ✅ Custom instructions
- ✅ Table extraction
- ✅ Image extraction
- ✅ Layout preservation
- ✅ Relationship mapping
- ✅ Result caching

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run only unit tests (no API calls)
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest tests/ --cov=src/docsray --cov-report=html
```

Current test coverage: **52 tests passing** with comprehensive coverage across all components

## 📖 API Reference

### Tool: docsray_peek

Get quick document overview and metadata.

```python
{
  "document_url": "path/to/document.pdf",
  "depth": "structure",  # metadata | structure | preview
  "provider": "auto"     # auto | pymupdf4llm | llama-parse
}
```

### Tool: docsray_map

Generate comprehensive document structure map.

```python
{
  "document_url": "path/to/document.pdf",
  "include_content": false,
  "analysis_depth": "deep",  # basic | deep | comprehensive
  "provider": "auto"
}
```

### Tool: docsray_xray

Deep AI-powered document analysis.

```python
{
  "document_url": "path/to/document.pdf",
  "analysis_type": ["entities", "key-points"],
  "custom_instructions": "Extract all dates and amounts",
  "provider": "llama-parse"
}
```

### Tool: docsray_extract

Extract content in various formats.

```python
{
  "document_url": "path/to/document.pdf",
  "extraction_targets": ["text", "tables"],
  "output_format": "markdown",  # markdown | text | json
  "pages": [1, 2, 3],  # Optional: specific pages
  "provider": "auto"
}
```

### Tool: docsray_seek

Navigate to specific document locations.

```python
{
  "document_url": "path/to/document.pdf",
  "target": {"page": 5},  # or {"section": "Introduction"} or {"query": "search text"}
  "extract_content": true,
  "provider": "auto"
}
```

## 🏗️ Architecture

```
docsray-mcp/
├── src/docsray/
│   ├── server.py           # FastMCP server with discovery resources
│   ├── providers/          # Provider implementations
│   │   ├── base.py        # Provider interface
│   │   ├── pymupdf4llm.py # Fast PDF extraction
│   │   └── llamaparse.py  # AI-powered analysis
│   ├── tools/             # MCP tool implementations
│   │   ├── peek.py        # Document overview
│   │   ├── map.py         # Structure mapping
│   │   ├── xray.py        # Deep analysis
│   │   ├── extract.py     # Content extraction
│   │   └── seek.py        # Navigation
│   └── utils/             # Utilities
│       ├── cache.py       # Document caching
│       └── llamaparse_cache.py  # LlamaParse .docsray cache
├── tests/
│   ├── unit/              # Fast isolated tests
│   ├── integration/       # Component interaction tests
│   └── manual/            # Debugging scripts
└── PROMPTS.md            # Example prompts for all use cases
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/docsray/docsray-mcp.git
cd docsray-mcp

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
ruff check src/
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on [FastMCP](https://github.com/jlowin/fastmcp) framework
- Document processing powered by [PyMuPDF4LLM](https://github.com/pymupdf/PyMuPDF4LLM)
- AI analysis powered by [LlamaParse](https://github.com/run-llama/llama_parse)
- Inspired by the [Model Context Protocol](https://github.com/anthropics/mcp) specification

## 📬 Support

- 📖 [Documentation](https://docs.docsray.dev)
- 🐛 [Issue Tracker](https://github.com/docsray/docsray-mcp/issues)
- 💬 [Discussions](https://github.com/docsray/docsray-mcp/discussions)

---

**Made with ❤️ for the MCP ecosystem**