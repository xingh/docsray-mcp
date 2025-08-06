# Docsray MCP Server - Quick Start Guide

## Installation

### From PyPI (Recommended)

```bash
# Install with pip
pip install docsray-mcp

# Or run directly with uvx
uvx docsray-mcp

# Or install globally with uv
uv tool install docsray-mcp
```

### From Source

```bash
git clone https://github.com/docsray/docsray-mcp
cd docsray-mcp
pip install -e .
```

### Optional Dependencies

For OCR and AI features:

```bash
# OCR support
pip install "docsray-mcp[ocr]"

# AI providers
pip install "docsray-mcp[ai]"

# All features
pip install "docsray-mcp[all]"
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:

```bash
# LlamaParse API key for AI features (optional)
LLAMAPARSE_API_KEY=llx-your-key-here

# Transport mode
DOCSRAY_TRANSPORT=stdio  # or http

# Enable providers
DOCSRAY_PYMUPDF_ENABLED=true
DOCSRAY_PYTESSERACT_ENABLED=false
DOCSRAY_MISTRAL_ENABLED=false
DOCSRAY_LLAMAPARSE_ENABLED=false

# API keys (if using AI providers)
DOCSRAY_MISTRAL_API_KEY=your-key
DOCSRAY_LLAMAPARSE_API_KEY=your-key
```

## Running the Server

### Stdio Mode (for Claude Desktop)

```bash
docsray start
```

### HTTP Mode

```bash
docsray start --transport http --port 3000
```

## MCP Client Integration

### Cursor (Confirmed Working ✅)

Add to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "python",
      "args": ["-m", "docsray.cli", "start"],
      "env": {
        "DOCSRAY_PYMUPDF_ENABLED": "true"
      }
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "docsray",
      "args": ["start"],
      "env": {
        "DOCSRAY_PYMUPDF_ENABLED": "true"
      }
    }
  }
}
```

## Basic Usage Examples

### Extract Text from PDF

```typescript
// Supports both local files and URLs
const result = await use_mcp_tool("docsray", "docsray_extract", {
  document_url: "./documents/report.pdf",  // or "https://example.com/doc.pdf"
  extraction_targets: ["text"],
  output_format: "markdown"
});
```

### Navigate to Page

```typescript
const result = await use_mcp_tool("docsray", "docsray_seek", {
  document_url: "/path/to/document.pdf",
  target: { page: 5 },
  extract_content: true
});
```

### Get Document Overview

```typescript
const result = await use_mcp_tool("docsray", "docsray_peek", {
  document_url: "/path/to/document.pdf",
  depth: "structure"
});
```

## Testing Your Setup

```bash
# List available providers
docsray list-providers

# Test a provider
docsray test --provider pymupdf4llm --document sample.pdf

# Run with debug logging
docsray start --verbose
```

## Next Steps

- Check the [API Reference](api-reference.md) for all available tools
- Learn about [Provider Configuration](providers.md)
- See [Advanced Usage](advanced.md) for complex scenarios