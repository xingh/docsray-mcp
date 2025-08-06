---
sidebar_position: 5
---

# Seek Tool

Navigate to specific locations within documents and extract targeted content with precision.

## Overview

The `docsray_seek` tool provides precise document navigation:
- **Page-specific navigation** with exact page targeting
- **Section-based seeking** using headings and structure
- **Content search** with query-based location finding
- **Context extraction** around target locations
- **Smart positioning** with automatic content relevance

## Basic Usage

### Navigate to Specific Page

```python
# Go to page 5 and extract content
result = docsray.seek(
    "document.pdf",
    target={"page": 5},
    extract_content=True
)

content = result['content']
page_info = result['location']
```

### Find Specific Section

```python
# Navigate to "Introduction" section
result = docsray.seek(
    "document.pdf",
    target={"section": "Introduction"},
    extract_content=True
)

# Navigate to subsection
result = docsray.seek(
    "document.pdf",
    target={"section": "2.1 Methodology"},
    extract_content=True
)
```

### Search-Based Navigation

```python
# Find and navigate to content matching query
result = docsray.seek(
    "document.pdf",
    target={"query": "financial performance"},
    extract_content=True
)

# Multiple matches are returned with relevance scores
locations = result['matches']
```

## Parameters

### document_url (required)
Path or URL to the document to navigate.

```python
docsray.seek("./reports/annual-report.pdf", target={"page": 10})
docsray.seek("https://example.com/manual.pdf", target={"section": "Setup"})
```

### target (required)
Specifies the navigation target. Must contain one of:

- **`{"page": number}`** - Navigate to specific page
- **`{"section": "title"}`** - Navigate to section by title
- **`{"query": "search terms"}`** - Find content by search
- **`{"position": {"page": 3, "offset": 500}}`** - Exact position

```python
# Page navigation
docsray.seek("doc.pdf", target={"page": 1})

# Section navigation
docsray.seek("doc.pdf", target={"section": "Conclusions"})

# Search navigation
docsray.seek("doc.pdf", target={"query": "risk factors"})
```

### extract_content (optional)
Whether to extract content at the target location. Default: `true`

```python
# Just find location (faster)
docsray.seek("doc.pdf", target={"page": 5}, extract_content=False)

# Find and extract content
docsray.seek("doc.pdf", target={"page": 5}, extract_content=True)
```

### provider (optional)
Provider for document processing. Default: `"auto"`

## Response Structure

### Page Navigation Response

```json
{
  "location": {
    "type": "page",
    "page": 5,
    "total_pages": 25,
    "position": {"page": 5, "offset": 0}
  },
  "content": {
    "text": "Content from page 5...",
    "markdown": "# Formatted content from page 5...",
    "word_count": 250,
    "character_count": 1500
  },
  "navigation": {
    "previous_page": 4,
    "next_page": 6,
    "section_title": "Financial Analysis",
    "section_level": 1
  },
  "provider": "pymupdf4llm"
}
```

### Section Navigation Response

```json
{
  "location": {
    "type": "section",
    "section_title": "Introduction",
    "section_level": 1,
    "page_start": 1,
    "page_end": 3,
    "position": {"page": 1, "offset": 250}
  },
  "content": {
    "text": "Introduction section content...",
    "markdown": "# Introduction\n\nContent...",
    "subsections": [
      {"title": "Background", "page": 2},
      {"title": "Objectives", "page": 3}
    ]
  },
  "navigation": {
    "parent_section": null,
    "next_section": "Methodology",
    "previous_section": null
  }
}
```

### Search Navigation Response

```json
{
  "location": {
    "type": "query",
    "query": "financial performance",
    "total_matches": 5
  },
  "matches": [
    {
      "page": 8,
      "position": {"page": 8, "offset": 150},
      "relevance_score": 0.95,
      "context": "...strong financial performance exceeded expectations...",
      "section": "Q3 Results"
    },
    {
      "page": 12,
      "position": {"page": 12, "offset": 300},
      "relevance_score": 0.87,
      "context": "...financial performance indicators show growth...",
      "section": "Key Metrics"
    }
  ],
  "content": {
    "text": "Content from best match...",
    "markdown": "Content with highlighted matches..."
  }
}
```

## Use Cases

### Interactive Document Viewer

```python
class DocumentViewer:
    def __init__(self, document_path):
        self.document_path = document_path
        self.current_page = 1
        self.history = []
    
    def go_to_page(self, page_number):
        result = docsray.seek(
            self.document_path,
            target={"page": page_number},
            extract_content=True
        )
        
        self.history.append(self.current_page)
        self.current_page = page_number
        
        return result['content']
    
    def go_to_section(self, section_name):
        result = docsray.seek(
            self.document_path,
            target={"section": section_name},
            extract_content=True
        )
        
        location = result['location']
        self.history.append(self.current_page)
        self.current_page = location['page_start']
        
        return result['content']
    
    def search_content(self, query):
        result = docsray.seek(
            self.document_path,
            target={"query": query},
            extract_content=True
        )
        
        return result['matches']
    
    def go_back(self):
        if self.history:
            previous_page = self.history.pop()
            return self.go_to_page(previous_page)
        return None

# Usage
viewer = DocumentViewer("manual.pdf")
content = viewer.go_to_section("Installation")
matches = viewer.search_content("configuration")
```

### Document Citation System

```python
def create_citation_links(document_path, citations):
    citation_data = []
    
    for citation in citations:
        # Find citation in document
        result = docsray.seek(
            document_path,
            target={"query": citation['text']},
            extract_content=True
        )
        
        if result['matches']:
            best_match = result['matches'][0]
            citation_data.append({
                "citation": citation['text'],
                "page": best_match['page'],
                "context": best_match['context'],
                "relevance": best_match['relevance_score']
            })
    
    return citation_data

# Usage
citations = [
    {"text": "According to the annual report"},
    {"text": "The study found that"},
    {"text": "As stated in the methodology"}
]

links = create_citation_links("research.pdf", citations)
```

### Content Validation

```python
def validate_document_structure(document_path, expected_sections):
    validation_results = []
    
    for section in expected_sections:
        result = docsray.seek(
            document_path,
            target={"section": section},
            extract_content=False
        )
        
        if "error" in result:
            validation_results.append({
                "section": section,
                "found": False,
                "error": result["error"]
            })
        else:
            validation_results.append({
                "section": section,
                "found": True,
                "page": result['location']['page_start'],
                "level": result['location']['section_level']
            })
    
    return validation_results

# Usage
required_sections = [
    "Executive Summary",
    "Introduction", 
    "Methodology",
    "Results",
    "Conclusions"
]

validation = validate_document_structure("report.pdf", required_sections)
```

## Advanced Usage

### Multi-Target Navigation

```python
def navigate_multiple_targets(document_path, targets):
    navigation_results = []
    
    for target in targets:
        result = docsray.seek(
            document_path,
            target=target,
            extract_content=True
        )
        
        navigation_results.append({
            "target": target,
            "result": result
        })
    
    return navigation_results

# Usage
targets = [
    {"page": 1},
    {"section": "Abstract"},
    {"query": "machine learning"},
    {"page": 10}
]

results = navigate_multiple_targets("paper.pdf", targets)
```

### Smart Content Extraction

```python
def extract_around_keywords(document_path, keywords):
    extracted_content = []
    
    for keyword in keywords:
        result = docsray.seek(
            document_path,
            target={"query": keyword},
            extract_content=True
        )
        
        for match in result.get('matches', []):
            extracted_content.append({
                "keyword": keyword,
                "page": match['page'],
                "context": match['context'],
                "relevance": match['relevance_score']
            })
    
    # Sort by relevance
    extracted_content.sort(key=lambda x: x['relevance'], reverse=True)
    
    return extracted_content

# Usage
keywords = ["revenue growth", "market share", "competitive advantage"]
content = extract_around_keywords("business-plan.pdf", keywords)
```

### Document Comparison Navigation

```python
def compare_document_sections(doc1_path, doc2_path, section_name):
    results = {}
    
    for doc_path in [doc1_path, doc2_path]:
        result = docsray.seek(
            doc_path,
            target={"section": section_name},
            extract_content=True
        )
        
        if "error" not in result:
            results[doc_path] = {
                "found": True,
                "content": result['content']['text'],
                "page": result['location']['page_start'],
                "word_count": result['content']['word_count']
            }
        else:
            results[doc_path] = {
                "found": False,
                "error": result["error"]
            }
    
    return results

# Usage
comparison = compare_document_sections(
    "report-2022.pdf",
    "report-2023.pdf",
    "Financial Performance"
)
```

## Performance Characteristics

### Navigation Speed by Target Type

| Target Type | Typical Time | Use Case |
|-------------|-------------|----------|
| Page | 0.1-0.5s | Fast page jumping |
| Section | 0.5-2.0s | Structure-based navigation |
| Query | 1.0-5.0s | Content search and discovery |

## Error Handling

```python
def safe_seek_operation(document_path, target):
    try:
        result = docsray.seek(
            document_path,
            target=target,
            extract_content=True
        )
        
        if "error" in result:
            return None, result["error"]
        
        return result, None
        
    except Exception as e:
        error_msg = str(e)
        
        if "not found" in error_msg.lower():
            return None, f"Target not found: {target}"
        elif "page" in error_msg.lower() and "out of range" in error_msg.lower():
            return None, f"Page number out of range: {target.get('page', 'unknown')}"
        else:
            return None, f"Seek operation failed: {error_msg}"

# Usage with error handling
result, error = safe_seek_operation("doc.pdf", {"section": "Nonexistent"})
if error:
    print(f"Navigation failed: {error}")
else:
    print(f"Found content at page {result['location']['page_start']}")
```

## Integration Examples

### Web API Endpoint

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/documents/<path:doc_path>/seek', methods=['POST'])
def seek_in_document(doc_path):
    data = request.json
    target = data.get('target')
    extract_content = data.get('extract_content', True)
    
    if not target:
        return jsonify({"error": "Target is required"}), 400
    
    result = docsray.seek(
        doc_path,
        target=target,
        extract_content=extract_content
    )
    
    if "error" in result:
        return jsonify({"error": result["error"]}), 404
    
    return jsonify(result)

# Example requests:
# POST /api/documents/report.pdf/seek
# {"target": {"page": 5}, "extract_content": true}
```

### Command Line Tool

```python
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description='Seek within document')
    parser.add_argument('document', help='Path to document')
    parser.add_argument('--page', type=int, help='Navigate to page number')
    parser.add_argument('--section', help='Navigate to section')
    parser.add_argument('--query', help='Search for content')
    parser.add_argument('--no-content', action='store_true', help='Skip content extraction')
    
    args = parser.parse_args()
    
    # Build target
    target = {}
    if args.page:
        target['page'] = args.page
    elif args.section:
        target['section'] = args.section
    elif args.query:
        target['query'] = args.query
    else:
        print("Error: Must specify --page, --section, or --query")
        return 1
    
    # Perform seek operation
    result = docsray.seek(
        args.document,
        target=target,
        extract_content=not args.no_content
    )
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1
    
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    exit(main())
```

## Best Practices

1. **Handle Missing Targets** - Always check for errors when seeking sections
2. **Use Caching** - Repeated seeks to same locations use cached results
3. **Combine with Other Tools** - Use peek/map to understand structure before seeking
4. **Validate Targets** - Ensure page numbers are within document range
5. **Provider Selection** - Auto-selection works well for most seek operations

## Next Steps

- Learn about [Basic Extraction Examples](../examples/basic-extraction) for content processing
- See [Map Tool](./map) for understanding document structure before navigation
- Check [Peek Tool](./peek) for quick document overview
- Review [API Reference](../api/tools) for complete parameter documentation