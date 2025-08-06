---
sidebar_position: 1
---

# Introduction

Welcome to **Docsray MCP** - the most comprehensive document perception server for Claude and the MCP ecosystem.

## What is Docsray?

Docsray is an advanced document processing MCP server that enables Claude to extract **everything** from any document. With support for multiple providers and intelligent caching, it's the ultimate tool for document analysis, extraction, and understanding.

## Key Features

### 🎯 **Comprehensive Extraction**
Extract ALL data from documents with a single command:
- Complete text with exact formatting
- Tables with full structure
- Images with descriptions
- Entities (people, organizations, dates, amounts)
- Document hierarchy and layout
- Metadata and properties

### 🔄 **Multi-Provider Architecture**
- **LlamaParse**: AI-powered deep analysis (5-30s)
- **PyMuPDF**: Lightning-fast extraction (&lt;1s)
- **Auto-selection**: Intelligent provider choice

### ⚡ **Intelligent Caching**
- Process once, access forever
- Instant retrieval of cached results
- Smart invalidation on document changes

## Quick Example

```text
# In Claude Desktop or Cursor, ask:
"Xray document.pdf with provider llama-parse"

# Claude will use Docsray to extract:
- All entities (people, organizations, dates, amounts)
- All tables with complete structure
- All images with descriptions
- Complete document hierarchy
```

## Five Powerful Tools

1. **Peek** 🔍 - Quick overview and metadata
2. **Map** 🗺️ - Complete document structure
3. **Xray** 🩻 - Comprehensive AI analysis
4. **Extract** 📝 - Content in any format
5. **Seek** 🎯 - Navigate to specific locations

## Why Docsray?

- **Production Ready**: 52+ tests, comprehensive error handling
- **Universal Support**: PDF, DOCX, PPTX, HTML, and more
- **Local & Remote**: Works with files and URLs
- **Natural Language**: Designed for Claude's conversational interface

## Getting Started

Ready to extract everything from your documents? Head to our [Quickstart Guide](./getting-started/quickstart) to begin!

## Community

- [GitHub](https://github.com/docsray/docsray-mcp)
- [Discord](https://discord.gg/docsray)
- [Twitter](https://twitter.com/docsray)

## License

Docsray is open source and available under the Apache 2.0 license.