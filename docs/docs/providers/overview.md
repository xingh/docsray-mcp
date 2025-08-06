---
sidebar_position: 1
---

# Providers Overview

Docsray MCP uses a multi-provider architecture to give you the best document processing capabilities. Each provider has unique strengths and use cases.

## Available Providers

### PyMuPDF4LLM (Always Available)

**Fast, reliable PDF processing for immediate results**

- **Speed**: Lightning fast (< 1 second for most documents)
- **Reliability**: Always available, no external dependencies
- **Cost**: Completely free
- **Best for**: Quick text extraction, basic document analysis, development/testing

**Capabilities:**
- ✅ Fast text extraction
- ✅ Markdown formatting
- ✅ Basic table detection
- ✅ Multi-page support
- ✅ Image placeholder detection
- ❌ No AI-powered analysis
- ❌ No OCR capabilities
- ❌ Limited entity recognition

### LlamaParse (AI-Powered)

**Advanced document understanding with LLM capabilities**

- **Speed**: Slower (5-30 seconds depending on document complexity)
- **Intelligence**: AI-powered analysis and extraction
- **Cost**: Requires API key and credits
- **Best for**: Comprehensive analysis, entity extraction, complex documents

**Capabilities:**
- ✅ AI-powered analysis
- ✅ Entity extraction (people, organizations, dates, amounts)
- ✅ Custom analysis instructions
- ✅ Table extraction with structure preservation
- ✅ Image extraction and descriptions
- ✅ Layout and formatting preservation
- ✅ Relationship mapping
- ✅ Smart caching in `.docsray` directories
- ✅ Multi-format support (PDF, DOCX, PPTX, HTML)

## Provider Selection

Docsray automatically selects the best provider for each operation, but you can also specify explicitly:

### Automatic Selection (Recommended)

```python
# Docsray chooses the best provider based on:
# - Operation type (peek uses PyMuPDF, xray uses LlamaParse)
# - Provider availability (API keys, network)
# - Document characteristics
result = docsray.peek("document.pdf")  # Auto-selects PyMuPDF4LLM
result = docsray.xray("document.pdf")  # Auto-selects LlamaParse
```

### Manual Selection

```python
# Force specific provider
result = docsray.peek("document.pdf", provider="pymupdf4llm")
result = docsray.xray("document.pdf", provider="llama-parse")
```

## When to Use Each Provider

### Use PyMuPDF4LLM When:

- **Speed is critical** - Need results in under 1 second
- **Simple text extraction** - Just need the document text
- **Development/testing** - Rapid iteration without API costs
- **Fallback scenario** - LlamaParse unavailable or rate limited
- **Basic document preview** - Quick overview of content

**Example use cases:**
- Quick document preview in file browsers
- Text search across document collections
- Simple content extraction for indexing
- Development and testing workflows

### Use LlamaParse When:

- **Comprehensive analysis** - Need deep document understanding
- **Entity extraction** - Extract people, organizations, dates, amounts
- **Complex documents** - Multi-column layouts, forms, tables
- **Custom analysis** - Specific extraction requirements
- **Production analysis** - High-quality results for business use

**Example use cases:**
- Legal contract analysis
- Financial document processing
- Academic paper analysis
- Form data extraction
- Business intelligence workflows

## Provider Capabilities Matrix

| Feature | PyMuPDF4LLM | LlamaParse |
|---------|-------------|------------|
| **Speed** | < 1s | 5-30s |
| **Cost** | Free | API credits required |
| **Text Extraction** | ✅ Basic | ✅ Advanced |
| **Table Detection** | ✅ Basic | ✅ Structured |
| **Image Handling** | ⚠️ Placeholders | ✅ Full extraction |
| **Entity Recognition** | ❌ | ✅ Advanced |
| **Custom Instructions** | ❌ | ✅ |
| **Layout Preservation** | ⚠️ Basic | ✅ Advanced |
| **Multi-format Support** | ⚠️ PDF only | ✅ PDF, DOCX, PPTX, HTML |
| **OCR** | ❌ | ✅ |
| **Caching** | ✅ Basic | ✅ Comprehensive |
| **Offline Operation** | ✅ | ❌ |

## Provider Configuration

### PyMuPDF4LLM Setup

No setup required - always available:

```bash
# Already included with Docsray installation
# No API keys or configuration needed
```

### LlamaParse Setup

Requires API key from LlamaIndex Cloud:

```bash
# Get API key from https://cloud.llamaindex.ai
export LLAMAPARSE_API_KEY="llx-your-key-here"

# Optional configuration
export LLAMAPARSE_MODE="fast"  # or "accurate", "premium"
export LLAMAPARSE_MAX_TIMEOUT="120"
```

## Performance Characteristics

### PyMuPDF4LLM Performance

```
Document Size    | Processing Time | Memory Usage
Small (1-10 pages)   | 0.1-0.5s     | 10-50MB
Medium (10-50 pages) | 0.5-2s       | 50-200MB  
Large (50+ pages)    | 2-10s        | 200MB+
```

### LlamaParse Performance

```
Document Size    | Processing Time | Memory Usage
Small (1-10 pages)   | 5-15s        | 20-100MB
Medium (10-50 pages) | 15-30s       | 100-500MB
Large (50+ pages)    | 30-120s      | 500MB+
```

## Caching Behavior

### PyMuPDF4LLM Caching

- Basic in-memory caching
- Results cached for current session
- No persistent cache across restarts

### LlamaParse Caching

- Comprehensive persistent caching in `.docsray` directories
- Results cached permanently until document changes
- Instant retrieval of cached results
- Smart cache invalidation on document modification

## Error Handling and Fallbacks

Docsray includes intelligent error handling:

### Automatic Fallbacks

```python
# If LlamaParse fails, automatically falls back to PyMuPDF4LLM
result = docsray.extract("document.pdf")
# 1. Tries LlamaParse first
# 2. Falls back to PyMuPDF4LLM on error
# 3. Returns best available result
```

### Error Scenarios

1. **LlamaParse API Error** → Falls back to PyMuPDF4LLM
2. **Network timeout** → Falls back to PyMuPDF4LLM  
3. **Invalid API key** → Falls back to PyMuPDF4LLM
4. **Rate limit exceeded** → Falls back to PyMuPDF4LLM
5. **Unsupported format** → Tries alternative provider

## Future Providers

Coming in future releases:

### PyTesseract (OCR)
- Optical Character Recognition for scanned documents
- Support for image-based PDFs
- Multi-language OCR capabilities

### Mistral OCR (AI-Powered)
- AI-enhanced OCR with context understanding
- Better accuracy on complex layouts
- Integrated with Mistral's language models

## Provider Selection Algorithm

Docsray's intelligent provider selection considers:

1. **Operation Type**
   - `peek` → PyMuPDF4LLM (speed priority)
   - `xray` → LlamaParse (analysis priority)
   - `extract` → Based on requirements

2. **Provider Availability**
   - API key presence
   - Network connectivity
   - Service status

3. **Document Characteristics**
   - File size and complexity
   - Format type
   - Processing requirements

4. **User Preferences**
   - Explicit provider selection
   - Configuration settings
   - Performance vs accuracy trade-offs

## Best Practices

### Development
- Use PyMuPDF4LLM for rapid development and testing
- Switch to LlamaParse for production analysis
- Always handle both providers in your error handling

### Production
- Configure LlamaParse with proper API key
- Enable comprehensive caching
- Monitor API usage and costs
- Set appropriate timeouts

### Cost Optimization
- Use PyMuPDF4LLM for simple operations
- Cache LlamaParse results aggressively
- Process documents once, access results many times
- Use batch processing for multiple documents

## Getting Help

- Check [LlamaParse Documentation](./llamaparse) for detailed LlamaParse configuration
- See [PyMuPDF Guide](./pymupdf) for PyMuPDF4LLM optimization
- Review [Provider Comparison](./comparison) for detailed feature comparison
- Visit [Troubleshooting](../advanced/troubleshooting) for common issues

## Next Steps

- Learn about [LlamaParse Configuration](./llamaparse)
- Explore [PyMuPDF4LLM Features](./pymupdf)  
- Compare [Provider Capabilities](./comparison)
- See [Performance Optimization](../advanced/performance)