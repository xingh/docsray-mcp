---
sidebar_position: 2
---

# Map Tool

Generate comprehensive document structure maps with detailed navigation information.

## Overview

The `docsray_map` tool creates detailed structural maps of documents:
- **Complete document outline** with hierarchical navigation
- **Page-by-page breakdown** of content types
- **Section relationships** and cross-references
- **Content distribution analysis** across pages
- **Navigation metadata** for efficient document traversal

## Basic Usage

### Generate Document Map

```python
# Basic document structure map
result = docsray.map("document.pdf")

# Access the structural information
outline = result['structure']['outline']
sections = result['structure']['sections']
page_map = result['structure']['page_map']
```

### Control Analysis Depth

```python
# Basic structure only
result = docsray.map("document.pdf", analysis_depth="basic")

# Deep structural analysis
result = docsray.map("document.pdf", analysis_depth="deep")

# Comprehensive analysis with content
result = docsray.map("document.pdf", analysis_depth="comprehensive")
```

## Parameters

### document_url (required)
Path or URL to the document to map.

```python
docsray.map("./reports/annual-report.pdf")
docsray.map("https://example.com/whitepaper.pdf")
```

### include_content (optional)
Whether to include content snippets in the map. Default: `false`

```python
# Structure only (faster)
docsray.map("doc.pdf", include_content=False)

# Structure with content samples
docsray.map("doc.pdf", include_content=True)
```

### analysis_depth (optional)
Level of structural analysis. Default: `"deep"`

- **`"basic"`** - Page structure and major headings
- **`"deep"`** - Detailed hierarchy and section analysis  
- **`"comprehensive"`** - Full structure with relationships

### provider (optional)
Provider for document processing. Default: `"auto"`

## Response Structure

### Basic Map Response

```json
{
  "structure": {
    "outline": [
      {
        "title": "Executive Summary",
        "level": 1,
        "page": 1,
        "section_id": "exec_summary",
        "children": [
          {
            "title": "Key Highlights",
            "level": 2,
            "page": 1,
            "section_id": "highlights"
          }
        ]
      }
    ],
    "page_map": [
      {
        "page": 1,
        "sections": ["exec_summary", "highlights"],
        "content_types": ["text", "list"],
        "element_count": 12
      }
    ],
    "navigation": {
      "total_sections": 8,
      "max_depth": 3,
      "cross_references": [
        {"from": "page_1", "to": "page_5", "type": "see_also"}
      ]
    }
  },
  "metadata": {
    "total_pages": 25,
    "processing_time": 2.3,
    "analysis_depth": "deep"
  },
  "provider": "llama-parse"
}
```

### Comprehensive Map with Content

```json
{
  "structure": {
    "outline": [ /* ... outline structure ... */ ],
    "page_map": [ /* ... page mapping ... */ ],
    "sections": [
      {
        "id": "exec_summary",
        "title": "Executive Summary",
        "page_start": 1,
        "page_end": 2,
        "content_preview": "This quarter showed strong performance...",
        "content_length": 1250,
        "subsections": ["highlights", "challenges"]
      }
    ],
    "content_distribution": {
      "text_pages": 20,
      "table_pages": 8,
      "image_pages": 5,
      "mixed_pages": 12
    }
  }
}
```

## Use Cases

### Document Navigation

Create interactive navigation for large documents:

```python
def create_navigation(document_path):
    result = docsray.map(document_path, analysis_depth="comprehensive")
    
    navigation = []
    for item in result['structure']['outline']:
        navigation.append({
            "title": item['title'],
            "page": item['page'], 
            "level": item['level'],
            "children": item.get('children', [])
        })
    
    return navigation

# Generate table of contents
toc = create_navigation("manual.pdf")
for item in toc:
    indent = "  " * (item['level'] - 1)
    print(f"{indent}- {item['title']} (p. {item['page']})")
```

### Content Analysis

Analyze document structure and content distribution:

```python
def analyze_document_structure(document_path):
    result = docsray.map(document_path, include_content=True)
    structure = result['structure']
    
    # Analyze content distribution
    distribution = structure['content_distribution']
    total_pages = result['metadata']['total_pages']
    
    analysis = {
        "text_ratio": distribution['text_pages'] / total_pages,
        "table_ratio": distribution['table_pages'] / total_pages,
        "image_ratio": distribution['image_pages'] / total_pages,
        "section_count": len(structure['sections']),
        "avg_section_length": total_pages / len(structure['sections'])
    }
    
    return analysis
```

### Quality Assessment

Assess document organization and structure quality:

```python
def assess_document_quality(document_path):
    result = docsray.map(document_path, analysis_depth="comprehensive")
    structure = result['structure']
    
    # Check structural quality
    outline = structure['outline']
    navigation = structure['navigation']
    
    quality_score = 0
    feedback = []
    
    # Check hierarchical structure
    if navigation['max_depth'] >= 2:
        quality_score += 20
        feedback.append("Good hierarchical structure")
    else:
        feedback.append("Consider adding subsections")
    
    # Check section balance
    sections = structure['sections']
    lengths = [s['content_length'] for s in sections]
    if max(lengths) / min(lengths) < 3:  # Not too imbalanced
        quality_score += 20
        feedback.append("Well-balanced section lengths")
    
    return {
        "quality_score": quality_score,
        "feedback": feedback,
        "structure_depth": navigation['max_depth'],
        "section_count": len(sections)
    }
```

## Performance Characteristics

### Analysis Depth Performance

| Depth | Typical Time | Memory Usage | Use Case |
|-------|-------------|--------------|----------|
| Basic | 1-3s | Low | Quick structure overview |
| Deep | 3-10s | Medium | Detailed navigation |
| Comprehensive | 10-30s | High | Full analysis |

### Document Size Impact

| Document Size | Basic | Deep | Comprehensive |
|---------------|-------|------|--------------|
| Small (1-10 pages) | 1-2s | 2-4s | 5-10s |
| Medium (10-50 pages) | 2-5s | 5-15s | 15-45s |
| Large (50+ pages) | 5-15s | 15-60s | 60-180s |

## Advanced Usage

### Selective Section Mapping

```python
# Map specific sections only
def map_sections(document_path, target_sections):
    full_map = docsray.map(document_path)
    outline = full_map['structure']['outline']
    
    filtered_sections = []
    for section in outline:
        if any(target in section['title'].lower() for target in target_sections):
            filtered_sections.append(section)
    
    return filtered_sections

# Find financial sections
financial_sections = map_sections("annual-report.pdf", 
                                 ["financial", "revenue", "earnings"])
```

### Cross-Document Mapping

```python
# Compare structure across multiple documents
def compare_document_structures(doc_paths):
    structures = {}
    
    for doc_path in doc_paths:
        result = docsray.map(doc_path, analysis_depth="basic")
        structures[doc_path] = {
            "sections": len(result['structure']['outline']),
            "depth": result['structure']['navigation']['max_depth'],
            "pages": result['metadata']['total_pages']
        }
    
    return structures

# Compare multiple reports
reports = ["q1-2023.pdf", "q2-2023.pdf", "q3-2023.pdf"]
comparison = compare_document_structures(reports)
for doc, stats in comparison.items():
    print(f"{doc}: {stats['sections']} sections, {stats['pages']} pages")
```

## Error Handling

```python
def safe_map_document(document_path):
    try:
        result = docsray.map(document_path)
        
        if "error" in result:
            return None, result["error"]
        
        return result, None
        
    except Exception as e:
        return None, f"Mapping failed: {str(e)}"

# Usage with error handling
map_result, error = safe_map_document("document.pdf")
if error:
    print(f"Cannot map document: {error}")
else:
    outline = map_result['structure']['outline']
    print(f"Document has {len(outline)} main sections")
```

## Integration Patterns

### Document Management System

```python
class DocumentManager:
    def __init__(self):
        self.documents = {}
    
    def add_document(self, path):
        # Map document structure
        result = docsray.map(path, include_content=False)
        
        self.documents[path] = {
            "structure": result['structure'],
            "metadata": result['metadata'],
            "indexed_at": datetime.now()
        }
    
    def find_section(self, query):
        matches = []
        for doc_path, doc_data in self.documents.items():
            for section in doc_data['structure']['sections']:
                if query.lower() in section['title'].lower():
                    matches.append({
                        "document": doc_path,
                        "section": section['title'],
                        "page": section['page_start']
                    })
        return matches
```

### Web API

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/document/<path:document_path>/map')
def get_document_map(document_path):
    depth = request.args.get('depth', 'deep')
    include_content = request.args.get('content', 'false').lower() == 'true'
    
    result = docsray.map(document_path, 
                        analysis_depth=depth,
                        include_content=include_content)
    
    if "error" in result:
        return jsonify({"error": result["error"]}), 400
    
    return jsonify(result)
```

## Best Practices

1. **Choose Appropriate Depth** - Use basic for quick overview, comprehensive for detailed analysis
2. **Cache Results** - Map results are automatically cached for repeated access
3. **Consider Document Size** - Large documents may require longer processing times
4. **Use Include Content Sparingly** - Only include content when needed for analysis
5. **Provider Selection** - LlamaParse provides richer structure analysis than PyMuPDF4LLM

## Next Steps

- Learn about [Xray Tool](./xray) for AI-powered content analysis
- See [Seek Tool](./seek) for navigation to specific sections
- Check [Extract Tool](./extract) for content extraction based on structure
- Review [API Reference](../api/tools) for complete parameter details