---
sidebar_position: 3
---

# How Docsray Works

Understanding the MCP architecture and how Docsray integrates with Claude.

## What is an MCP Server?

Docsray is a **Model Context Protocol (MCP) server**, not a standalone CLI tool. This means:

1. **It runs as a server** that provides tools to AI assistants
2. **Claude connects to it** via the MCP protocol
3. **You interact through Claude**, not directly with the server

## Architecture Overview

```
┌─────────────┐     MCP Protocol     ┌──────────────┐
│   Claude    │ ◄──────────────────► │   Docsray    │
│  Desktop    │                       │  MCP Server  │
└─────────────┘                       └──────────────┘
       ▲                                     │
       │                                     ▼
       │                              ┌──────────────┐
   You type:                          │  Document    │
   "Xray invoice.pdf"                 │  Processing  │
                                      └──────────────┘
```

## Installation vs Usage

### Installation (One-time setup)

```bash
# Install the package
pip install docsray-mcp

# Or run directly with uvx
uvx docsray-mcp
```

### Configuration (One-time setup)

Configure Claude Desktop to connect to Docsray:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "uvx",
      "args": ["docsray-mcp"],
      "env": {
        "LLAMAPARSE_API_KEY": "your-key-here"
      }
    }
  }
}
```

### Usage (Daily interaction)

**You don't run commands directly!** Instead, you ask Claude:

```text
You: Analyze the invoice.pdf file on my desktop
Claude: I'll analyze that invoice for you using Docsray...
        [Uses docsray_xray tool]
        
        Here's what I found in the invoice:
        - Vendor: Acme Corp
        - Total Amount: $1,234.56
        - Due Date: March 15, 2024
        ...
```

## The Five Tools

When you ask Claude to work with documents, it uses these Docsray tools:

### 1. docsray_peek
**You say:** "What's in this PDF?"  
**Claude uses:** `docsray_peek` tool  
**You get:** Document overview and metadata

### 2. docsray_map
**You say:** "Show me the structure of this document"  
**Claude uses:** `docsray_map` tool  
**You get:** Complete document hierarchy

### 3. docsray_xray
**You say:** "Extract everything from this invoice"  
**Claude uses:** `docsray_xray` tool  
**You get:** All entities, tables, text, and images

### 4. docsray_extract
**You say:** "Get the tables from page 5"  
**Claude uses:** `docsray_extract` tool  
**You get:** Specific content in your preferred format

### 5. docsray_seek
**You say:** "Find the payment terms section"  
**Claude uses:** `docsray_seek` tool  
**You get:** Navigation to specific content

## Common Misunderstandings

### ❌ Wrong: Direct CLI Usage
```bash
# This doesn't exist:
docsray xray document.pdf --provider llama-parse

# Or this:
mcp docsray xray document.pdf
```

### ✅ Right: Through Claude
```text
You: Xray document.pdf with provider llama-parse
Claude: [Uses docsray_xray tool with those parameters]
```

### ❌ Wrong: Python Import
```python
# You can't import it in your code:
import docsray
result = docsray.xray("document.pdf")
```

### ✅ Right: MCP Server Connection
```text
Claude Desktop → MCP Protocol → Docsray Server → Document Processing
```

## Behind the Scenes

When you ask Claude to "Xray invoice.pdf", here's what happens:

1. **Claude interprets** your request
2. **Claude calls** the `docsray_xray` tool via MCP
3. **Docsray server** receives the tool call
4. **Provider selected** (LlamaParse or PyMuPDF)
5. **Document processed** using the provider
6. **Results cached** for future use
7. **Data returned** to Claude via MCP
8. **Claude presents** the results to you

## Advanced Usage

### Specifying Providers

```text
# Let Docsray choose
Analyze report.pdf

# Force LlamaParse (comprehensive)
Xray report.pdf with provider llama-parse

# Force PyMuPDF (fast)
Extract text from report.pdf with provider pymupdf4llm
```

### Custom Instructions

```text
Xray contract.pdf with custom instructions:
"Focus on payment terms, penalties, and termination clauses"
```

### Working with URLs

```text
Analyze https://example.com/document.pdf
```

## Troubleshooting

### Server Not Starting?

1. Check your Claude Desktop config file
2. Verify the command path is correct
3. Ensure Python/uvx is installed

### Tools Not Available?

1. Restart Claude Desktop
2. Check server logs for errors
3. Verify installation with `pip list | grep docsray`

### Provider Issues?

1. For LlamaParse: Check API key is set
2. For PyMuPDF: Always available as fallback
3. Try specifying provider explicitly

## Next Steps

Now that you understand how Docsray works:

1. [Configure your installation](./installation)
2. [Try the quickstart examples](./quickstart)
3. [Learn about providers](../providers/overview)

Remember: Docsray is a server that gives Claude document superpowers - you interact through Claude, not directly with Docsray!