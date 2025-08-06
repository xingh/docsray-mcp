---
sidebar_position: 1
---

# Installation

Get Docsray MCP up and running in minutes.

## Requirements

- Python 3.9 or higher
- pip package manager
- Claude Desktop or compatible MCP client

## Install via pip

```bash
pip install docsray-mcp
```

## Install from source

```bash
git clone https://github.com/docsray/docsray-mcp.git
cd docsray-mcp
pip install -e .
```

## Provider Setup

### PyMuPDF (Default - No Setup Required)

PyMuPDF4LLM is included and works out of the box:

```bash
# Already included, no action needed!
```

### LlamaParse (AI-Powered Analysis)

For comprehensive extraction with AI analysis:

1. Get your API key from [LlamaIndex Cloud](https://cloud.llamaindex.ai)
2. Set the environment variable:

```bash
export LLAMAPARSE_API_KEY="your-api-key-here"
```

Or add to your `.env` file:

```env
LLAMAPARSE_API_KEY=your-api-key-here
```

## Configure Claude Desktop

Add Docsray to your Claude Desktop configuration:

### macOS
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "python",
      "args": ["-m", "docsray.server"],
      "env": {
        "LLAMAPARSE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Windows
Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "python",
      "args": ["-m", "docsray.server"],
      "env": {
        "LLAMAPARSE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Verify Installation

Test with Claude:

```
You: Peek at https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf

Claude: [Uses Docsray to analyze the PDF and show its structure]
```

## Optional Configuration

### Environment Variables

```bash
# LlamaParse configuration
LLAMAPARSE_API_KEY=your-api-key
LLAMAPARSE_MODE=fast  # or 'accurate', 'premium'

# Performance tuning
DOCSRAY_MAX_CONCURRENT_REQUESTS=5
DOCSRAY_TIMEOUT_SECONDS=30

# Caching
DOCSRAY_CACHE_DIR=.docsray  # Custom cache directory
```

### Provider Selection

```python
# Force specific provider
docsray.xray("document.pdf", provider="llama-parse")
docsray.peek("document.pdf", provider="pymupdf4llm")

# Let Docsray choose (default)
docsray.xray("document.pdf")  # Auto-selects best provider
```

## Troubleshooting

### LlamaParse not working?
- Check your API key is set correctly
- Verify you have API credits available
- Try the fast mode: `LLAMAPARSE_MODE=fast`

### PyMuPDF issues?
- Ensure Python 3.9+ is installed
- Try reinstalling: `pip install --upgrade pymupdf4llm`

### Cache issues?
- Clear cache: `rm -rf .docsray/`
- Check disk space availability

## Next Steps

Now that you have Docsray installed, check out the [Quickstart Guide](./quickstart) to start extracting data from documents!