---
sidebar_position: 4
---

# Extract Tool

Extract document content in multiple formats with precise control over output structure and formatting.

## Overview

The `docsray_extract` tool provides flexible content extraction:
- **Multi-format output** (markdown, text, JSON, HTML)
- **Selective extraction** (text, tables, images, metadata)
- **Page-specific processing** for large documents
- **Structured data output** with preserved formatting
- **Batch processing** capabilities

## Basic Usage

### Simple Text Extraction

```python
# Extract complete document as text
result = docsray.extract("document.pdf")
text = result['extraction']['text']
markdown = result['extraction']['markdown']
```

### Selective Content Extraction

```python
# Extract specific content types
result = docsray.extract(
    "document.pdf",
    extraction_targets=["text", "tables"]
)

# Access extracted content
text_content = result['extraction']['text']
tables = result['extraction']['tables']
```

## Parameters

### document_url (required)
Path or URL to document for extraction.

```python
docsray.extract("./reports/quarterly.pdf")
docsray.extract("https://example.com/whitepaper.pdf")
```

### extraction_targets (optional)
Types of content to extract. Default: `["text"]`

Available targets:
- **`"text"`** - Plain text content
- **`"tables"`** - Structured table data
- **`"images"`** - Image extraction and descriptions
- **`"metadata"`** - Document properties
- **`"structure"`** - Document hierarchy

```python
# Text only (fastest)
docsray.extract("doc.pdf", extraction_targets=["text"])

# Text and tables
docsray.extract("doc.pdf", extraction_targets=["text", "tables"])

# Everything
docsray.extract("doc.pdf", extraction_targets=["text", "tables", "images", "metadata"])
```

### output_format (optional)
Format for extracted content. Default: `"markdown"`

- **`"markdown"`** - Formatted markdown with structure
- **`"text"`** - Plain text without formatting
- **`"json"`** - Structured JSON output
- **`"html"`** - HTML with preserved formatting

```python
# Markdown output (default)
docsray.extract("doc.pdf", output_format="markdown")

# Plain text
docsray.extract("doc.pdf", output_format="text")

# Structured JSON
docsray.extract("doc.pdf", output_format="json")
```

### pages (optional)
Specific pages to extract. Default: all pages

```python
# Extract specific pages
docsray.extract("doc.pdf", pages=[1, 2, 3])

# Extract page ranges
docsray.extract("doc.pdf", pages=list(range(1, 11)))  # Pages 1-10
```

### provider (optional)
Provider for extraction. Default: `"auto"`

```python
# Fast extraction
docsray.extract("doc.pdf", provider="pymupdf4llm")

# Comprehensive extraction
docsray.extract("doc.pdf", provider="llama-parse")
```

## Response Structure

### Text Extraction Response

```json
{
  "extraction": {
    "text": "Complete document text...",
    "markdown": "# Formatted markdown...",
    "word_count": 5000,
    "character_count": 25000,
    "page_count": 10
  },
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "creation_date": "2023-01-01",
    "file_size": 1024000
  },
  "provider": "pymupdf4llm",
  "processing_time": 0.85
}
```

### Comprehensive Extraction Response

```json
{
  "extraction": {
    "text": "Document text content...",
    "markdown": "# Formatted content...",
    "tables": [
      {
        "page": 3,
        "html": "<table><tr><th>Header</th></tr></table>",
        "data": {
          "headers": ["Quarter", "Revenue"],
          "rows": [["Q1", "$100M"], ["Q2", "$115M"]]
        }
      }
    ],
    "images": [
      {
        "page": 5,
        "description": "Bar chart showing sales growth",
        "metadata": {"width": 800, "height": 600}
      }
    ],
    "structure": {
      "sections": [
        {"title": "Introduction", "page": 1, "level": 1},
        {"title": "Methods", "page": 3, "level": 1}
      ]
    }
  },
  "provider": "llama-parse"
}
```

## Use Cases

### Content Management Systems

```python
def import_document_to_cms(doc_path, doc_id):
    # Extract content with metadata
    result = docsray.extract(
        doc_path,
        extraction_targets=["text", "metadata", "structure"],
        output_format="markdown"
    )
    
    # Store in CMS
    document_data = {
        "id": doc_id,
        "title": result['metadata'].get('title', 'Untitled'),
        "content": result['extraction']['markdown'],
        "author": result['metadata'].get('author'),
        "created_at": result['metadata'].get('creation_date'),
        "sections": result['extraction']['structure']['sections']
    }
    
    return document_data
```

### Search Index Generation

```python
def create_search_index(document_paths):
    search_index = []
    
    for doc_path in document_paths:
        result = docsray.extract(
            doc_path,
            extraction_targets=["text", "metadata"],
            output_format="text"
        )
        
        # Create search document
        search_doc = {
            "path": doc_path,
            "title": result['metadata'].get('title', ''),
            "content": result['extraction']['text'],
            "author": result['metadata'].get('author', ''),
            "page_count": result['extraction']['page_count'],
            "word_count": result['extraction']['word_count']
        }
        
        search_index.append(search_doc)
    
    return search_index
```

### Data Processing Pipeline

```python
def extract_financial_data(report_path):
    # Extract tables and text for financial analysis
    result = docsray.extract(
        report_path,
        extraction_targets=["text", "tables"],
        output_format="json"
    )
    
    financial_data = {
        "tables": [],
        "metrics": []
    }
    
    # Process extracted tables
    for table in result['extraction']['tables']:
        if any(keyword in str(table['data']).lower() 
               for keyword in ['revenue', 'profit', 'income']):
            financial_data['tables'].append({
                "page": table['page'],
                "type": "financial",
                "data": table['data']
            })
    
    # Extract financial metrics from text using regex
    import re
    text = result['extraction']['text']
    
    # Find monetary amounts
    amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?[MmBb]?', text)
    percentages = re.findall(r'\d+(?:\.\d+)?%', text)
    
    financial_data['metrics'] = {
        "monetary_amounts": amounts,
        "percentages": percentages
    }
    
    return financial_data
```

## Advanced Usage

### Page-Range Processing

```python
def process_large_document_in_chunks(doc_path, chunk_size=10):
    # First, get total page count
    peek_result = docsray.peek(doc_path, depth="metadata")
    total_pages = peek_result['metadata']['page_count']
    
    results = []
    
    # Process in chunks
    for start_page in range(1, total_pages + 1, chunk_size):
        end_page = min(start_page + chunk_size - 1, total_pages)
        page_range = list(range(start_page, end_page + 1))
        
        chunk_result = docsray.extract(
            doc_path,
            pages=page_range,
            extraction_targets=["text", "tables"]
        )
        
        results.append({
            "pages": f"{start_page}-{end_page}",
            "content": chunk_result['extraction']
        })
    
    return results
```

### Multi-Format Export

```python
def export_document_multiple_formats(doc_path, output_dir):
    import os
    
    formats = {
        "markdown": "md",
        "text": "txt",
        "json": "json",
        "html": "html"
    }
    
    results = {}
    
    for format_name, extension in formats.items():
        result = docsray.extract(
            doc_path,
            extraction_targets=["text", "tables", "metadata"],
            output_format=format_name
        )
        
        # Save to file
        base_name = os.path.splitext(os.path.basename(doc_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.{extension}")
        
        if format_name == "json":
            import json
            with open(output_path, 'w') as f:
                json.dump(result['extraction'], f, indent=2)
        else:
            content = result['extraction'].get(format_name, result['extraction']['text'])
            with open(output_path, 'w') as f:
                f.write(content)
        
        results[format_name] = output_path
    
    return results
```

### Comparative Extraction

```python
def compare_extraction_methods(doc_path):
    providers = ["pymupdf4llm", "llama-parse"]
    comparison = {}
    
    for provider in providers:
        try:
            result = docsray.extract(
                doc_path,
                provider=provider,
                extraction_targets=["text", "tables"]
            )
            
            comparison[provider] = {
                "success": True,
                "word_count": result['extraction']['word_count'],
                "table_count": len(result['extraction'].get('tables', [])),
                "processing_time": result.get('processing_time', 0),
                "text_sample": result['extraction']['text'][:200]
            }
            
        except Exception as e:
            comparison[provider] = {
                "success": False,
                "error": str(e)
            }
    
    return comparison
```

## Performance Optimization

### Extraction Target Selection

```python
# Fastest - text only
result = docsray.extract("doc.pdf", extraction_targets=["text"])

# Balanced - text and tables
result = docsray.extract("doc.pdf", extraction_targets=["text", "tables"])

# Comprehensive - everything (slower)
result = docsray.extract("doc.pdf", 
                        extraction_targets=["text", "tables", "images", "metadata"])
```

### Provider Selection for Speed

```python
# Fast extraction (PyMuPDF4LLM)
result = docsray.extract("doc.pdf", provider="pymupdf4llm")

# Comprehensive extraction (LlamaParse)
result = docsray.extract("doc.pdf", provider="llama-parse")

# Auto-selection based on needs
result = docsray.extract("doc.pdf")  # Uses best available
```

### Memory Management

```python
def memory_efficient_extraction(doc_path):
    # Process specific pages to reduce memory usage
    peek_result = docsray.peek(doc_path, depth="metadata")
    total_pages = peek_result['metadata']['page_count']
    
    if total_pages > 100:
        # Large document - process in smaller chunks
        return process_large_document_in_chunks(doc_path, chunk_size=25)
    else:
        # Normal processing
        return docsray.extract(doc_path)
```

## Error Handling

```python
def robust_extraction(doc_path, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            result = docsray.extract(doc_path)
            
            if "error" in result:
                if attempt < max_retries:
                    continue
                return None, result["error"]
            
            # Validate extraction quality
            if result['extraction']['word_count'] == 0:
                if attempt < max_retries:
                    continue
                return None, "No content extracted"
            
            return result, None
            
        except Exception as e:
            if attempt < max_retries:
                continue
            return None, f"Extraction failed: {str(e)}"
    
    return None, "Max retries exceeded"

# Usage
result, error = robust_extraction("document.pdf")
if error:
    print(f"Extraction failed: {error}")
else:
    print(f"Extracted {result['extraction']['word_count']} words")
```

## Best Practices

1. **Choose Appropriate Targets** - Only extract what you need for better performance
2. **Use Page Ranges** - Process large documents in chunks
3. **Select Right Format** - Use JSON for structured data, markdown for formatted text
4. **Provider Selection** - PyMuPDF4LLM for speed, LlamaParse for quality
5. **Handle Errors** - Always check for extraction errors and empty results
6. **Cache Results** - Leverage automatic caching for repeated extractions

## Integration Examples

### REST API

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/extract', methods=['POST'])
def extract_document():
    data = request.json
    doc_path = data.get('document_path')
    targets = data.get('targets', ['text'])
    format_type = data.get('format', 'markdown')
    
    result = docsray.extract(
        doc_path,
        extraction_targets=targets,
        output_format=format_type
    )
    
    if "error" in result:
        return jsonify({"error": result["error"]}), 400
    
    return jsonify(result)
```

### Batch Processing Script

```python
import os
import json

def batch_extract_documents(input_dir, output_dir):
    pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
    results = []
    
    for pdf_file in pdf_files:
        input_path = os.path.join(input_dir, pdf_file)
        output_file = os.path.splitext(pdf_file)[0] + '.json'
        output_path = os.path.join(output_dir, output_file)
        
        try:
            result = docsray.extract(
                input_path,
                extraction_targets=["text", "metadata"],
                output_format="json"
            )
            
            # Save extraction result
            with open(output_path, 'w') as f:
                json.dump(result['extraction'], f, indent=2)
            
            results.append({
                "file": pdf_file,
                "status": "success",
                "output": output_path,
                "word_count": result['extraction']['word_count']
            })
            
        except Exception as e:
            results.append({
                "file": pdf_file,
                "status": "error",
                "error": str(e)
            })
    
    return results
```

## Next Steps

- Learn about [Seek Tool](./seek) for navigation to specific content
- See [Basic Extraction Examples](../examples/basic-extraction) for detailed use cases
- Check [Table Extraction Guide](../examples/table-extraction) for structured data
- Review [API Reference](../api/tools) for complete parameter documentation