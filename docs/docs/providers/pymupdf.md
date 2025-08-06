---
sidebar_position: 3
---

# PyMuPDF4LLM Provider

PyMuPDF4LLM is Docsray's fast, reliable PDF processing provider that delivers immediate results without external dependencies.

## Overview

PyMuPDF4LLM provides:
- **Lightning-fast processing** (< 1 second for most documents)
- **Zero external dependencies** - works offline
- **Reliable text extraction** with consistent formatting
- **Basic table detection** and structure preservation
- **Always available fallback** when other providers fail

## Key Strengths

### Speed and Performance
- **Sub-second processing** for most documents
- **Minimal memory usage** - efficient resource utilization
- **No network dependencies** - works completely offline
- **Instant startup** - no API initialization delays

### Reliability
- **Always available** - no API keys or external services required
- **Consistent results** - deterministic processing
- **Stable output** - same input produces same output
- **Error resilient** - handles corrupted or unusual PDFs gracefully

### Cost Effectiveness
- **Completely free** - no API charges or usage limits
- **No rate limiting** - process unlimited documents
- **Local processing** - no data leaves your system

## Capabilities

### Text Extraction

PyMuPDF4LLM excels at clean, formatted text extraction:

```python
# Fast text extraction
result = docsray.extract("document.pdf", provider="pymupdf4llm")

# Access extracted content
text = result['extraction']['text']          # Clean plain text
markdown = result['extraction']['markdown']  # Formatted markdown
```

**Text extraction features:**
- ✅ Preserves paragraph structure
- ✅ Maintains line breaks and spacing
- ✅ Handles multiple columns
- ✅ Extracts headers and footers
- ✅ Processes multi-page documents
- ✅ Handles various PDF encodings

### Basic Table Detection

Detects and extracts simple table structures:

```python
result = docsray.extract("report.pdf", provider="pymupdf4llm")
tables = result.get('tables', [])

for table in tables:
    page = table['page']
    content = table['content']    # Table as text
    structure = table['rows']     # Basic row detection
```

**Table capabilities:**
- ✅ Detects table boundaries
- ✅ Extracts table content as text
- ✅ Basic row and column detection
- ⚠️ Limited complex table handling
- ❌ No advanced table structure analysis

### Image Handling

Provides basic image detection and placeholder insertion:

```python
result = docsray.extract("document.pdf", provider="pymupdf4llm")

# Images are represented as placeholders in text
# "[Image: Figure 1 - Chart showing sales data]"
```

**Image features:**
- ✅ Detects image locations
- ✅ Inserts descriptive placeholders
- ✅ Preserves document flow around images
- ❌ No image extraction or analysis
- ❌ No image descriptions beyond placeholders

### Metadata Extraction

Extracts comprehensive document metadata:

```python
result = docsray.peek("document.pdf", provider="pymupdf4llm")
metadata = result['metadata']

# Available metadata fields:
# - title, author, subject, creator
# - creation_date, modification_date
# - page_count, format, file_size
# - security settings, permissions
```

## Configuration Options

### Basic Configuration

PyMuPDF4LLM works out of the box with no configuration required:

```bash
# No setup needed - always enabled
# No API keys or external dependencies
```

### Optional Configuration

Fine-tune PyMuPDF4LLM behavior with environment variables:

```bash
# Image handling
PYMUPDF4LLM_EXTRACT_IMAGES=false     # Extract embedded images to files
PYMUPDF4LLM_EXTRACT_TABLES=true      # Enable table detection  
PYMUPDF4LLM_PAGE_SEPARATORS=true     # Include page break markers
PYMUPDF4LLM_WRITE_IMAGES=false       # Save images to disk

# Text formatting
PYMUPDF4LLM_TO_MARKDOWN=true         # Output as markdown
PYMUPDF4LLM_SHOW_PROGRESS=false      # Show processing progress
PYMUPDF4LLM_DPI=72                   # Image DPI for extraction
```

### Performance Tuning

```bash
# Memory management
PYMUPDF4LLM_MAX_IMAGE_SIZE_MB=10     # Skip large images
PYMUPDF4LLM_MAX_PAGE_SIZE_MB=50      # Skip oversized pages

# Processing options
PYMUPDF4LLM_IGNORE_ERRORS=true       # Continue on page errors
PYMUPDF4LLM_INCLUDE_METADATA=true    # Extract metadata
```

## Use Cases

### Ideal Use Cases

PyMuPDF4LLM is perfect for:

#### Quick Document Preview
```python
# Get instant document overview
result = docsray.peek("document.pdf", provider="pymupdf4llm", depth="preview")
print(f"Pages: {result['page_count']}")
print(f"Preview: {result['preview'][:500]}...")
```

#### Fast Text Search
```python
# Extract text for search indexing
result = docsray.extract("document.pdf", provider="pymupdf4llm")
text = result['extraction']['text']

# Search within extracted text
if "important keyword" in text.lower():
    print("Keyword found in document")
```

#### Development and Testing
```python
# Rapid iteration during development
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
for doc in documents:
    result = docsray.extract(doc, provider="pymupdf4llm")
    print(f"{doc}: {len(result['extraction']['text'])} characters")
```

#### Batch Processing
```python
# Process many documents quickly
import os
pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]

for pdf in pdf_files:
    result = docsray.peek(pdf, provider="pymupdf4llm")
    metadata = result['metadata']
    print(f"{pdf}: {metadata.get('title', 'No title')} - {metadata['page_count']} pages")
```

### Not Ideal For

Avoid PyMuPDF4LLM when you need:
- **Advanced entity extraction** - Use LlamaParse
- **Complex table analysis** - Use LlamaParse  
- **Custom analysis instructions** - Use LlamaParse
- **Image extraction and analysis** - Use LlamaParse
- **AI-powered insights** - Use LlamaParse

## Performance Characteristics

### Processing Speed

```
Document Size        | Typical Processing Time
1-5 pages           | 0.1 - 0.3 seconds
6-20 pages          | 0.3 - 1.0 seconds  
21-50 pages         | 1.0 - 3.0 seconds
51-100 pages        | 3.0 - 8.0 seconds
100+ pages          | 8.0+ seconds
```

### Memory Usage

```
Document Size        | Memory Usage
Small (< 5MB)       | 10-30MB
Medium (5-20MB)     | 30-100MB
Large (20-50MB)     | 100-300MB
Very Large (50MB+)  | 300MB+
```

### Throughput

- **Concurrent processing**: Handles multiple documents simultaneously
- **No rate limits**: Process unlimited documents
- **Consistent performance**: Speed doesn't degrade with usage

## Output Format

### Text Output Structure

```python
{
    "extraction": {
        "text": "Full document text...",
        "markdown": "# Formatted markdown...",
        "page_count": 10,
        "word_count": 5000,
        "character_count": 25000
    },
    "metadata": {
        "title": "Document Title",
        "author": "Author Name", 
        "page_count": 10,
        "creation_date": "2023-01-01",
        "file_size": 1024000
    },
    "provider_info": {
        "name": "pymupdf4llm",
        "version": "0.0.17",
        "processing_time": 0.45
    }
}
```

### Markdown Formatting

PyMuPDF4LLM converts PDF structure to markdown:

```markdown
# Document Title

## Section 1

Regular paragraph text with **bold** and *italic* formatting.

### Subsection 1.1  

- Bullet point 1
- Bullet point 2

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |

[Image: Figure 1 - Sales Chart]

---
*Page 2*

## Section 2

More content...
```

## Error Handling

PyMuPDF4LLM includes robust error handling:

### Common Error Types

1. **File Access Errors**
   - File not found
   - Permission denied
   - Corrupted PDF

2. **Processing Errors**
   - Encrypted PDF without password
   - Unsupported PDF features
   - Memory limitations

3. **Format Errors**
   - Invalid PDF structure
   - Damaged file headers
   - Incomplete downloads

### Error Recovery

```python
try:
    result = docsray.extract("document.pdf", provider="pymupdf4llm")
except Exception as e:
    if "permission" in str(e).lower():
        print("PDF is password protected or encrypted")
    elif "memory" in str(e).lower():
        print("Document too large - try processing specific pages")
    elif "corrupt" in str(e).lower():
        print("PDF file appears to be corrupted")
    else:
        print(f"Processing error: {e}")
```

## Advanced Features

### Page-Specific Processing

```python
# Extract specific pages only
result = docsray.extract(
    "large-document.pdf", 
    provider="pymupdf4llm",
    pages=[1, 2, 3, 10]  # Only process these pages
)
```

### Custom Text Formatting

```python
# Control output formatting
result = docsray.extract(
    "document.pdf",
    provider="pymupdf4llm", 
    output_format="text"  # Plain text instead of markdown
)
```

### Metadata-Only Extraction

```python
# Get just metadata without full text extraction
result = docsray.peek(
    "document.pdf",
    provider="pymupdf4llm",
    depth="metadata"  # Metadata only, very fast
)
```

## Integration Patterns

### As Primary Provider

```python
# Use PyMuPDF4LLM for all basic operations
def quick_document_info(pdf_path):
    result = docsray.peek(pdf_path, provider="pymupdf4llm")
    return {
        "title": result['metadata'].get('title', 'Unknown'),
        "pages": result['metadata']['page_count'],
        "size": result['metadata']['file_size']
    }
```

### As Fallback Provider

```python  
# Use as fallback when LlamaParse unavailable
def extract_with_fallback(document_path):
    try:
        # Try LlamaParse first for comprehensive analysis
        return docsray.xray(document_path, provider="llama-parse")
    except Exception:
        # Fall back to PyMuPDF4LLM for basic extraction
        return docsray.extract(document_path, provider="pymupdf4llm")
```

### For Development

```python
# Quick development workflow
def dev_document_check(pdf_path):
    # Fast check during development
    result = docsray.peek(pdf_path, provider="pymupdf4llm", depth="structure")
    print(f"Document: {pdf_path}")
    print(f"Pages: {result['metadata']['page_count']}")
    print(f"Size: {result['metadata']['file_size'] / 1024:.1f}KB")
    print(f"Sample: {result['preview'][:200]}...")
```

## Best Practices

1. **Use for Speed-Critical Operations** - When sub-second response needed
2. **Ideal for Development** - Fast iteration and testing
3. **Perfect for Metadata** - Getting document info quickly
4. **Batch Processing** - Handle large volumes efficiently
5. **Reliable Fallback** - Always works when other providers fail
6. **Text Indexing** - Extract text for search systems
7. **Document Validation** - Quick format and readability checks

## Limitations

### What PyMuPDF4LLM Cannot Do

- **Advanced entity recognition** - No AI-powered analysis
- **Complex table structure** - Limited to basic table detection
- **Image analysis** - No image extraction or description
- **Custom instructions** - No configurable analysis behavior
- **OCR** - Cannot read scanned or image-based PDFs
- **Multi-format support** - PDF files only

### When to Use LlamaParse Instead

Switch to LlamaParse for:
- Entity extraction (people, organizations, dates, amounts)
- Complex table analysis with structure preservation
- Image extraction and AI-generated descriptions
- Custom analysis instructions for specific use cases
- Multi-format document support (DOCX, PPTX, HTML)
- Advanced document understanding and relationships

## Troubleshooting

### Common Issues

1. **Encrypted PDFs**
   ```python
   # Handle password-protected PDFs
   try:
       result = docsray.extract("encrypted.pdf", provider="pymupdf4llm")
   except Exception as e:
       if "password" in str(e).lower():
           print("PDF requires password - not supported")
   ```

2. **Large Documents**
   ```python
   # Process specific pages for large documents
   result = docsray.extract(
       "huge-document.pdf",
       provider="pymupdf4llm", 
       pages=list(range(1, 11))  # First 10 pages only
   )
   ```

3. **Memory Issues**
   ```bash
   # Reduce memory usage
   export PYMUPDF4LLM_MAX_IMAGE_SIZE_MB=5
   export PYMUPDF4LLM_MAX_PAGE_SIZE_MB=25
   ```

## Next Steps

- Compare with [LlamaParse capabilities](./llamaparse)
- See [Provider Comparison](./comparison) for detailed differences
- Learn about [Performance Optimization](../advanced/performance)
- Check [API Reference](../api/providers) for all options