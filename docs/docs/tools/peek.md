---
sidebar_position: 1
---

# Peek Tool

Get a quick overview and metadata of any document with lightning-fast performance.

## Overview

The `docsray_peek` tool provides instant document insights without full processing:
- **Document metadata** (title, author, page count, file size)
- **Format detection** and compatibility check
- **Quick preview** of document content
- **Provider capabilities** for the document type
- **Processing estimates** for different operations

## Basic Usage

### Quick Document Check

```python
# Get basic metadata
result = docsray.peek("document.pdf")

print(f"Title: {result['metadata']['title']}")
print(f"Pages: {result['metadata']['page_count']}")  
print(f"Size: {result['metadata']['file_size']} bytes")
```

### With Depth Control

```python
# Metadata only (fastest)
result = docsray.peek("document.pdf", depth="metadata")

# Include document structure
result = docsray.peek("document.pdf", depth="structure") 

# Include content preview
result = docsray.peek("document.pdf", depth="preview")
```

## Parameters

### document_url (required)
Path or URL to the document to analyze.

```python
# Local files
docsray.peek("./reports/quarterly.pdf")
docsray.peek("/home/user/documents/contract.pdf")

# URLs
docsray.peek("https://example.com/document.pdf")
```

### depth (optional)
Level of analysis detail. Default: `"structure"`

- **`"metadata"`** - Basic file information only
- **`"structure"`** - Metadata + document structure
- **`"preview"`** - Metadata + structure + content preview

```python
# Fastest - metadata only
docsray.peek("doc.pdf", depth="metadata")

# Balanced - includes structure
docsray.peek("doc.pdf", depth="structure")

# Most comprehensive - includes preview
docsray.peek("doc.pdf", depth="preview")
```

### provider (optional)
Provider to use for analysis. Default: `"auto"`

```python
# Let Docsray choose the best provider
docsray.peek("document.pdf")  # Uses auto-selection

# Force specific provider
docsray.peek("document.pdf", provider="pymupdf4llm")  # Fast
docsray.peek("document.pdf", provider="llama-parse")  # Comprehensive
```

## Response Structure

The peek tool returns a structured response with different levels of detail:

### Metadata Response (`depth="metadata"`)

```json
{
  "metadata": {
    "title": "Quarterly Financial Report",
    "author": "Finance Department", 
    "subject": "Q3 2023 Results",
    "creator": "Microsoft Word",
    "creation_date": "2023-10-15T10:30:00Z",
    "modification_date": "2023-10-16T14:20:00Z",
    "page_count": 25,
    "format": "pdf",
    "file_size": 2048576,
    "has_images": true,
    "has_tables": true,
    "is_encrypted": false,
    "language": "en"
  },
  "provider": "pymupdf4llm"
}
```

### Structure Response (`depth="structure"`)

```json
{
  "metadata": { /* ... metadata fields ... */ },
  "structure": {
    "outline": [
      {"title": "Executive Summary", "page": 1, "level": 1},
      {"title": "Financial Highlights", "page": 3, "level": 1},
      {"title": "Revenue Analysis", "page": 5, "level": 2},
      {"title": "Cost Structure", "page": 8, "level": 2}
    ],
    "sections": [
      {"type": "header", "content": "Executive Summary", "page": 1},
      {"type": "paragraph", "content": "This quarter...", "page": 1},
      {"type": "table", "content": "Financial Data", "page": 3}
    ],
    "page_info": [
      {"page": 1, "type": "content", "elements": 5},
      {"page": 2, "type": "content", "elements": 8}
    ]
  },
  "provider": "pymupdf4llm"
}
```

### Preview Response (`depth="preview"`)

```json
{
  "metadata": { /* ... metadata fields ... */ },
  "structure": { /* ... structure fields ... */ },
  "preview": {
    "first_page": "Executive Summary\n\nThis quarterly report presents...",
    "sample_content": "Key highlights from the document...",
    "key_sections": [
      "Executive Summary",
      "Financial Performance", 
      "Market Analysis"
    ],
    "preview_length": 500,
    "total_length": 45000
  },
  "provider": "pymupdf4llm"
}
```

## Use Cases

### Document Validation

Check if a document is readable and get basic information:

```python
def validate_document(path):
    result = docsray.peek(path, depth="metadata")
    
    if "error" in result:
        return False, result["error"]
    
    metadata = result["metadata"]
    if metadata["page_count"] == 0:
        return False, "Document has no pages"
    
    if metadata["is_encrypted"]:
        return False, "Document is password protected"
    
    return True, f"Valid PDF with {metadata['page_count']} pages"
```

### File Browser Integration

Show document previews in file managers:

```python
def get_document_info(file_path):
    result = docsray.peek(file_path, depth="structure")
    
    return {
        "title": result["metadata"].get("title", "Untitled"),
        "pages": result["metadata"]["page_count"],
        "size": format_file_size(result["metadata"]["file_size"]),
        "sections": len(result["structure"]["outline"]),
        "preview": result.get("preview", {}).get("first_page", "")[:200]
    }
```

### Batch Document Processing

Quickly analyze multiple documents:

```python
import os

def analyze_document_folder(folder_path):
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    results = []
    
    for pdf_file in pdf_files:
        file_path = os.path.join(folder_path, pdf_file)
        result = docsray.peek(file_path, depth="metadata")
        
        if "error" not in result:
            results.append({
                "filename": pdf_file,
                "title": result["metadata"].get("title", pdf_file),
                "pages": result["metadata"]["page_count"],
                "size": result["metadata"]["file_size"]
            })
    
    return results
```

### Document Triage

Decide which documents need detailed processing:

```python
def triage_documents(document_list):
    for doc_path in document_list:
        result = docsray.peek(doc_path, depth="structure")
        
        metadata = result["metadata"]
        structure = result["structure"]
        
        # Prioritize based on characteristics
        priority = "low"
        
        if metadata["page_count"] > 50:
            priority = "high"  # Large documents
        elif len(structure["outline"]) > 10:
            priority = "medium"  # Complex structure
        elif metadata.get("has_tables", False):
            priority = "medium"  # Contains data tables
            
        print(f"{doc_path}: {priority} priority ({metadata['page_count']} pages)")
```

## Performance Characteristics

### Processing Speed by Depth

| Depth | Typical Time | Use Case |
|-------|-------------|----------|
| `metadata` | 0.1-0.5s | Quick file validation |
| `structure` | 0.3-1.0s | File browser previews |
| `preview` | 0.5-2.0s | Content previews |

### Provider Performance

| Provider | Speed | Best For |
|----------|-------|----------|
| **PyMuPDF4LLM** | Very Fast | Quick metadata and structure |
| **LlamaParse** | Slower | Detailed analysis when needed |
| **Auto** | Balanced | General use (defaults to PyMuPDF4LLM) |

## Error Handling

The peek tool includes comprehensive error handling:

### Common Errors

```python
result = docsray.peek("nonexistent.pdf")
if "error" in result:
    error_type = result.get("type", "Unknown")
    if error_type == "FileNotFoundError":
        print("File does not exist")
    elif error_type == "PermissionError":
        print("Cannot access file - check permissions")
    elif "encrypted" in result["error"]:
        print("Document is password protected")
```

### Graceful Error Handling

```python
def safe_peek(document_path):
    try:
        result = docsray.peek(document_path)
        
        if "error" in result:
            return None, result["error"]
        
        return result, None
        
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

# Usage
document, error = safe_peek("document.pdf")
if error:
    print(f"Cannot analyze document: {error}")
else:
    print(f"Document has {document['metadata']['page_count']} pages")
```

## Advanced Usage

### Custom Provider Selection

```python
# Always use fast provider for peek operations
result = docsray.peek("document.pdf", provider="pymupdf4llm")

# Use AI provider for enhanced metadata extraction
result = docsray.peek("document.pdf", provider="llama-parse", depth="preview")
```

### Conditional Processing

```python
def smart_document_processing(doc_path):
    # Quick peek first
    peek_result = docsray.peek(doc_path, depth="metadata")
    
    if "error" in peek_result:
        return peek_result
    
    metadata = peek_result["metadata"]
    
    # Decide on further processing based on peek results
    if metadata["page_count"] > 100:
        # Large document - use fast provider
        return docsray.extract(doc_path, provider="pymupdf4llm")
    elif metadata.get("has_tables", False):
        # Has tables - use AI provider for better table extraction
        return docsray.xray(doc_path, provider="llama-parse")
    else:
        # Standard document - use default processing
        return docsray.extract(doc_path)
```

### Caching Strategy

Peek results are automatically cached for better performance:

```python
# First call - processes document
result1 = docsray.peek("document.pdf", depth="structure")  # ~0.5s

# Second call - returns cached result
result2 = docsray.peek("document.pdf", depth="structure")  # ~0.01s

# Different depth - may require new processing
result3 = docsray.peek("document.pdf", depth="preview")   # ~1.0s
```

## Best Practices

1. **Start with Peek** - Always use peek before expensive operations
2. **Choose Appropriate Depth** - Use metadata for validation, structure for overview, preview for content sampling
3. **Handle Errors Gracefully** - Always check for error responses
4. **Cache Results** - Leverage automatic caching for repeated access
5. **Provider Selection** - Use PyMuPDF4LLM for speed, LlamaParse for comprehensive analysis

## Integration Examples

### Web Application

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/document/info/<path:document_path>')
def get_document_info(document_path):
    result = docsray.peek(document_path, depth="structure")
    
    if "error" in result:
        return jsonify({"error": result["error"]}), 400
    
    return jsonify({
        "title": result["metadata"].get("title", "Untitled"),
        "pages": result["metadata"]["page_count"],
        "sections": result["structure"]["outline"],
        "provider": result["provider"]
    })
```

### Command Line Tool

```python
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description='Peek at document')
    parser.add_argument('document', help='Path to document')
    parser.add_argument('--depth', choices=['metadata', 'structure', 'preview'], 
                       default='structure', help='Analysis depth')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    result = docsray.peek(args.document, depth=args.depth)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
            return 1
        
        metadata = result["metadata"]
        print(f"Title: {metadata.get('title', 'Untitled')}")
        print(f"Pages: {metadata['page_count']}")
        print(f"Size: {metadata['file_size']} bytes")
        print(f"Provider: {result['provider']}")

if __name__ == "__main__":
    main()
```

## Next Steps

- Learn about [Map Tool](./map) for detailed document structure analysis
- See [Extract Tool](./extract) for content extraction
- Check [Xray Tool](./xray) for comprehensive AI analysis
- Review [API Reference](../api/tools) for all parameters