---
sidebar_position: 1
---

# Tools API Reference

Complete API reference for all Docsray MCP tools with parameters, responses, and examples.

## docsray_peek

Get quick document overview and metadata.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `document_url` | string | Yes | - | Path or URL to document |
| `depth` | string | No | "structure" | Analysis depth: "metadata", "structure", "preview" |
| `provider` | string | No | "auto" | Provider: "auto", "pymupdf4llm", "llama-parse" |

### Response Schema

```json
{
  "metadata": {
    "title": "string",
    "author": "string", 
    "subject": "string",
    "creator": "string",
    "creation_date": "string (ISO 8601)",
    "modification_date": "string (ISO 8601)",
    "page_count": "integer",
    "format": "string",
    "file_size": "integer (bytes)",
    "has_images": "boolean",
    "has_tables": "boolean",
    "is_encrypted": "boolean",
    "language": "string"
  },
  "structure": {  // Only if depth >= "structure"
    "outline": [
      {
        "title": "string",
        "page": "integer",
        "level": "integer"
      }
    ],
    "sections": [
      {
        "type": "string",
        "content": "string", 
        "page": "integer"
      }
    ],
    "page_info": [
      {
        "page": "integer",
        "type": "string",
        "elements": "integer"
      }
    ]
  },
  "preview": {  // Only if depth = "preview"
    "first_page": "string",
    "sample_content": "string",
    "key_sections": ["string"],
    "preview_length": "integer",
    "total_length": "integer"
  },
  "provider": "string"
}
```

### Examples

```python
# Basic metadata
result = docsray.peek("document.pdf", depth="metadata")

# Structure analysis
result = docsray.peek("document.pdf", depth="structure")

# Full preview with specific provider
result = docsray.peek("document.pdf", depth="preview", provider="llama-parse")
```

## docsray_map

Generate comprehensive document structure map.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `document_url` | string | Yes | - | Path or URL to document |
| `include_content` | boolean | No | false | Include content snippets |
| `analysis_depth` | string | No | "deep" | Depth: "basic", "deep", "comprehensive" |
| `provider` | string | No | "auto" | Provider selection |

### Response Schema

```json
{
  "structure": {
    "outline": [
      {
        "title": "string",
        "level": "integer",
        "page": "integer",
        "section_id": "string",
        "children": ["object"] // Nested outline items
      }
    ],
    "page_map": [
      {
        "page": "integer",
        "sections": ["string"], // Section IDs
        "content_types": ["string"],
        "element_count": "integer"
      }
    ],
    "sections": [  // Only if include_content = true
      {
        "id": "string",
        "title": "string", 
        "page_start": "integer",
        "page_end": "integer",
        "content_preview": "string",
        "content_length": "integer",
        "subsections": ["string"]
      }
    ],
    "navigation": {
      "total_sections": "integer",
      "max_depth": "integer",
      "cross_references": [
        {
          "from": "string",
          "to": "string",
          "type": "string"
        }
      ]
    },
    "content_distribution": {  // Only if analysis_depth >= "comprehensive"
      "text_pages": "integer",
      "table_pages": "integer", 
      "image_pages": "integer",
      "mixed_pages": "integer"
    }
  },
  "metadata": {
    "total_pages": "integer",
    "processing_time": "number",
    "analysis_depth": "string"
  },
  "provider": "string"
}
```

### Examples

```python
# Basic structure map
result = docsray.map("document.pdf")

# Comprehensive analysis with content
result = docsray.map("document.pdf", 
                    include_content=True,
                    analysis_depth="comprehensive")
```

## docsray_xray

AI-powered comprehensive document analysis.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `document_url` | string | Yes | - | Path or URL to document |
| `analysis_type` | array | No | ["entities", "key-points"] | Analysis types to perform |
| `custom_instructions` | string | No | null | Detailed analysis instructions |
| `provider` | string | No | "llama-parse" | Provider (LlamaParse recommended) |

#### Analysis Types

- `"entities"` - Extract people, organizations, dates, amounts, etc.
- `"relationships"` - Map connections between entities
- `"key-points"` - Identify main ideas and findings
- `"sentiment"` - Analyze document tone
- `"structure"` - Deep structural analysis

### Response Schema

```json
{
  "analysis": {
    "extracted_content": {
      "entities": [
        {
          "type": "string", // PERSON, ORGANIZATION, DATE, MONETARY, etc.
          "value": "string",
          "context": "string",
          "page": "integer",
          "confidence": "number (0-1)"
        }
      ],
      "key_points": [
        {
          "point": "string",
          "importance": "string", // high, medium, low
          "page": "integer", 
          "supporting_evidence": ["string"]
        }
      ],
      "relationships": [  // Only if "relationships" in analysis_type
        {
          "entity1": "string",
          "entity2": "string", 
          "relationship": "string",
          "confidence": "number (0-1)"
        }
      ],
      "sentiment": {  // Only if "sentiment" in analysis_type
        "overall_tone": "string", // positive, negative, neutral
        "confidence_level": "string", // high, medium, low
        "key_indicators": ["string"]
      }
    },
    "full_extraction": {
      "documents": ["object"], // Complete document data
      "pages": ["object"],     // Page-by-page content
      "images": ["object"],    // Image extractions with descriptions
      "tables": ["object"]     // Structured table data
    },
    "summary": {
      "total_entities": "integer",
      "entity_types": ["string"],
      "key_points_count": "integer", 
      "confidence_score": "number (0-1)",
      "processing_time": "number"
    }
  },
  "provider": "string"
}
```

### Examples

```python
# Basic entity extraction
result = docsray.xray("document.pdf", analysis_type=["entities"])

# Comprehensive analysis with custom instructions
result = docsray.xray("contract.pdf",
                     analysis_type=["entities", "relationships", "key-points"],
                     custom_instructions="Extract all parties, dates, and obligations")

# Full analysis
result = docsray.xray("document.pdf",
                     analysis_type=["entities", "relationships", "key-points", "sentiment"])
```

## docsray_extract

Extract document content in multiple formats.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `document_url` | string | Yes | - | Path or URL to document |
| `extraction_targets` | array | No | ["text"] | Content types to extract |
| `output_format` | string | No | "markdown" | Output format |
| `pages` | array | No | null | Specific pages to extract |
| `provider` | string | No | "auto" | Provider selection |

#### Extraction Targets

- `"text"` - Plain text content
- `"tables"` - Structured table data
- `"images"` - Image extraction and descriptions  
- `"metadata"` - Document properties
- `"structure"` - Document hierarchy

#### Output Formats

- `"markdown"` - Formatted markdown with structure
- `"text"` - Plain text without formatting
- `"json"` - Structured JSON output
- `"html"` - HTML with preserved formatting

### Response Schema

```json
{
  "extraction": {
    "text": "string",           // Plain text content
    "markdown": "string",       // Formatted markdown
    "html": "string",          // HTML format (if requested)
    "word_count": "integer",
    "character_count": "integer",
    "page_count": "integer",
    "tables": [  // Only if "tables" in extraction_targets
      {
        "page": "integer",
        "html": "string",
        "data": {
          "headers": ["string"],
          "rows": [["string"]]
        }
      }
    ],
    "images": [  // Only if "images" in extraction_targets
      {
        "page": "integer", 
        "description": "string",
        "metadata": {
          "width": "integer",
          "height": "integer",
          "format": "string"
        }
      }
    ],
    "structure": {  // Only if "structure" in extraction_targets
      "sections": [
        {
          "title": "string",
          "page": "integer",
          "level": "integer"
        }
      ]
    }
  },
  "metadata": {  // Only if "metadata" in extraction_targets
    "title": "string",
    "author": "string",
    "creation_date": "string",
    "file_size": "integer"
  },
  "provider": "string",
  "processing_time": "number"
}
```

### Examples

```python
# Simple text extraction
result = docsray.extract("document.pdf")

# Extract specific content types
result = docsray.extract("document.pdf", 
                        extraction_targets=["text", "tables", "images"])

# Extract specific pages as JSON
result = docsray.extract("document.pdf",
                        pages=[1, 2, 3],
                        output_format="json")
```

## docsray_seek

Navigate to specific document locations.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `document_url` | string | Yes | - | Path or URL to document |
| `target` | object | Yes | - | Navigation target specification |
| `extract_content` | boolean | No | true | Extract content at target location |
| `context_size` | string | No | "medium" | Context amount around target |
| `provider` | string | No | "auto" | Provider selection |

#### Target Object

One of these target types:

```json
// Page navigation
{"page": "integer"}

// Section navigation  
{"section": "string"}

// Search navigation
{"query": "string"}

// Exact position
{"position": {"page": "integer", "offset": "integer"}}
```

#### Context Sizes

- `"small"` - 200 characters around target
- `"medium"` - 500 characters around target
- `"large"` - 1000 characters around target  
- `"page"` - Entire page content

### Response Schema

```json
{
  "location": {
    "type": "string", // "page", "section", "query", "position"
    // For page navigation:
    "page": "integer",
    "total_pages": "integer",
    // For section navigation:
    "section_title": "string",
    "section_level": "integer", 
    "page_start": "integer",
    "page_end": "integer",
    // For query navigation:
    "query": "string",
    "total_matches": "integer",
    // Common:
    "position": {
      "page": "integer",
      "offset": "integer"
    }
  },
  "content": {  // Only if extract_content = true
    "text": "string",
    "markdown": "string",
    "word_count": "integer",
    "character_count": "integer"
  },
  "matches": [  // Only for query navigation
    {
      "page": "integer",
      "position": {"page": "integer", "offset": "integer"},
      "relevance_score": "number (0-1)",
      "context": "string",
      "section": "string"
    }
  ],
  "navigation": {
    "previous_page": "integer",
    "next_page": "integer",
    "section_title": "string",
    "parent_section": "string",
    "next_section": "string",
    "previous_section": "string"
  },
  "provider": "string"
}
```

### Examples

```python
# Navigate to specific page
result = docsray.seek("document.pdf", target={"page": 5})

# Find section
result = docsray.seek("document.pdf", target={"section": "Introduction"})

# Search for content
result = docsray.seek("document.pdf", 
                     target={"query": "financial performance"},
                     context_size="large")
```

## Error Responses

All tools return error responses in this format when operations fail:

```json
{
  "error": "string",      // Human-readable error message
  "type": "string",       // Error type (FileNotFoundError, etc.)
  "details": "object",    // Additional error details (optional)
  "suggestion": "string"  // Suggested solution (optional)
}
```

## Common Parameters

### Provider Options

- `"auto"` - Automatic provider selection (default)
- `"pymupdf4llm"` - Fast PyMuPDF4LLM provider
- `"llama-parse"` - AI-powered LlamaParse provider

### Document URL Formats

- Local files: `"./document.pdf"`, `"/absolute/path/document.pdf"`
- URLs: `"https://example.com/document.pdf"`

### Rate Limits

- **PyMuPDF4LLM**: No limits (local processing)
- **LlamaParse**: Based on your API plan
- **Auto provider**: Inherits limits from selected provider

## Response Caching

All tool responses are automatically cached based on:

1. **Document content hash** (not filename)
2. **Operation parameters** (provider, depth, instructions, etc.)
3. **Operation type** (peek, map, xray, extract, seek)

Cache keys are generated as: `{operation}_{doc_hash}_{params_hash}`

## Next Steps

- See [Provider API Reference](./providers) for provider-specific details
- Check [Configuration API](./configuration) for environment settings
- Review [Tools Documentation](../tools/peek) for usage examples