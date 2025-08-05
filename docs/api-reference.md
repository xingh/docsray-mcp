# Docsray MCP API Reference

## Tools

### docsray_seek

Navigate to specific pages or sections within documents.

**Parameters:**
- `document_url` (string, required): URL or file path (absolute, relative, or ~) to the document
- `target` (object, required): Navigation target
  - `page` (integer): Page number (1-based)
  - `section` (string): Section title
  - `query` (string): Text to search for
- `extract_content` (boolean, default: true): Whether to extract content
- `provider` (string, default: "auto"): Provider selection

**Response:**
```json
{
  "location": {
    "page": 1,
    "type": "page"
  },
  "content": "Page content...",
  "context": {
    "totalPages": 10,
    "hasNext": true,
    "hasPrevious": false
  },
  "provider": "pymupdf4llm"
}
```

### docsray_peek

Get document structure, metadata, and overview without full extraction.

**Parameters:**
- `document_url` (string, required): URL or file path (absolute, relative, or ~) to the document
- `depth` (string, default: "structure"): Level of detail
  - `metadata`: Basic document info only
  - `structure`: Include document structure
  - `preview`: Include content preview
- `provider` (string, default: "auto"): Provider selection

**Response:**
```json
{
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "pageCount": 42,
    "format": "PDF",
    "fileSize": 1048576,
    "createdDate": "2024-01-01T00:00:00Z"
  },
  "structure": {
    "hasImages": true,
    "hasTables": true,
    "sections": []
  },
  "preview": {
    "firstPageText": "Preview text...",
    "tableOfContents": []
  },
  "provider": "pymupdf4llm"
}
```

### docsray_map

Generate comprehensive document structure map.

**Parameters:**
- `document_url` (string, required): URL or file path (absolute, relative, or ~) to the document
- `include_content` (boolean, default: false): Include content snippets
- `analysis_depth` (string, default: "deep"): Analysis depth level
  - `shallow`: Basic structure only
  - `deep`: Detailed structure with resources
  - `comprehensive`: Full analysis with relationships
- `provider` (string, default: "auto"): Provider selection

**Response:**
```json
{
  "documentMap": {
    "hierarchy": {
      "root": {
        "type": "document",
        "title": "Document Title",
        "children": []
      }
    },
    "resources": {
      "images": [],
      "tables": []
    },
    "crossReferences": []
  },
  "statistics": {
    "totalPages": 10,
    "totalImages": 5,
    "totalTables": 2
  },
  "provider": "pymupdf4llm"
}
```

### docsray_xray

Perform deep AI-powered document analysis (Note: Currently returns placeholder - full AI analysis coming with AI provider implementation).

**Parameters:**
- `document_url` (string, required): URL or file path (absolute, relative, or ~) to the document
- `analysis_type` (array, default: ["entities", "key-points"]): Types of analysis
  - `entities`: Extract named entities
  - `relationships`: Find entity relationships
  - `key-points`: Extract key points
  - `sentiment`: Analyze sentiment
  - `structure`: Analyze document structure
- `custom_instructions` (string, optional): Custom analysis instructions
- `provider` (string, default: "llama-parse"): Provider selection

**Response:**
```json
{
  "analysis": {
    "entities": [...],
    "key_points": [...],
    "relationships": [...]
  },
  "confidence": 0.95,
  "providerInfo": {
    "name": "llama-parse",
    "model": "latest"
  },
  "provider": "llama-parse"
}
```

### docsray_extract

Extract specific content or data from documents.

**Parameters:**
- `document_url` (string, required): URL or file path (absolute, relative, or ~) to the document
- `extraction_targets` (array, default: ["text"]): Content to extract
  - `text`: Document text
  - `tables`: Table data
  - `images`: Image information
  - `forms`: Form fields
  - `metadata`: Document metadata
  - `equations`: Mathematical equations
- `output_format` (string, default: "markdown"): Output format
  - `markdown`: Formatted markdown
  - `json`: Structured JSON
  - `structured`: Raw provider format
- `pages` (array, optional): Specific pages to extract (1-based)
- `provider` (string, default: "auto"): Provider selection

**Response:**
```json
{
  "content": "# Document Title\n\nExtracted content...",
  "format": "markdown",
  "pagesProcessed": [1, 2, 3],
  "statistics": {
    "pagesExtracted": 3,
    "charactersExtracted": 1500
  },
  "provider": "pymupdf4llm"
}
```

## Provider Capabilities

### pymupdf4llm (✅ Implemented)
- **Formats**: pdf, xps, epub, cbz, svg
- **Features**: tables, images, forms, multi-language
- **Best for**: Fast extraction, structured PDFs

### pytesseract (🔄 Planned)
- **Formats**: png, jpg, pdf
- **Features**: OCR, multi-language
- **Best for**: Scanned documents

### ocrmypdf (🔄 Planned)
- **Formats**: pdf
- **Features**: Advanced OCR, PDF/A conversion
- **Best for**: OCR with PDF optimization

### mistral-ocr (🔄 Planned)
- **Formats**: pdf, png, jpg, docx, pptx
- **Features**: AI-powered OCR, custom instructions
- **Best for**: Complex layouts, handwriting

### llama-parse (🔄 Planned)
- **Formats**: pdf, docx, pptx, html
- **Features**: AI analysis, entity extraction
- **Best for**: Deep document understanding

## Error Codes

- `-30001`: Provider not available
- `-30002`: Provider initialization failed
- `-30003`: No suitable provider found
- `-31001`: Unsupported document format
- `-31002`: Document too large
- `-31003`: Document corrupted
- `-31004`: Document encrypted
- `-32001`: Operation timeout
- `-32002`: Operation failed
- `-32003`: Invalid target

## Rate Limits

- Default: 10 concurrent requests
- Configurable via `DOCSRAY_MAX_CONCURRENT_REQUESTS`
- Cache TTL: 3600 seconds (1 hour)