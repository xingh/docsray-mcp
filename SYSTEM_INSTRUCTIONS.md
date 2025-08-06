# Docsray MCP Server - System Instructions

## Overview
Docsray is an advanced document processing MCP server that provides AI-powered document analysis, extraction, and navigation capabilities. It supports multiple document formats and can process both local files (relative/absolute paths) and internet URLs. The server features dynamic provider discovery, intelligent caching, and comprehensive error handling with 52 passing tests.

## Core Capabilities

### 🔍 Document Analysis Tools

1. **docsray_peek** - Quick document overview and metadata
   - Get page count, format, file size
   - Discover available extraction formats
   - Check provider capabilities and status
   - Preview document structure

2. **docsray_map** - Comprehensive document structure mapping
   - Generate complete document hierarchy
   - Identify sections, subsections, and cross-references
   - Locate tables, images, and special elements
   - Cache results for faster subsequent access

3. **docsray_xray** - Deep AI-powered analysis
   - Extract named entities (people, organizations, dates, amounts)
   - Identify key points and main ideas
   - Analyze relationships between entities
   - Custom instruction support for specific analysis

4. **docsray_extract** - Content extraction in multiple formats
   - Markdown, text, JSON output formats
   - Page-specific extraction
   - Table and image extraction
   - Preserve formatting and structure

5. **docsray_seek** - Navigate to specific document locations
   - Jump to specific pages
   - Find sections by name
   - Search for content
   - Extract content from target location

## Provider Capabilities

### LlamaParse (AI-Powered) 🧠
- **Best for**: Deep understanding, entity extraction, custom analysis, AI-powered insights, comprehensive data extraction
- **Features**: 
  - AI-powered entity recognition
  - Custom instruction support for targeted extraction
  - Relationship mapping between entities
  - Advanced table extraction with structure preservation
  - Image extraction with descriptions and metadata
  - Complete document layout preservation
  - Mathematical equation extraction
  - Form field extraction
  - Hyperlink and cross-reference extraction
  - Font and styling information
  - Result caching in .docsray directories
- **Maximum Extraction**: The `xray` operation returns ALL cached LlamaParse data including:
  - Complete text with exact formatting
  - All tables in structured format
  - All images with metadata
  - Full document hierarchy
  - All extracted entities and relationships
  - Page-by-page layout information
- **Status**: Active when LLAMAPARSE_API_KEY is configured
- **Use when**: You need intelligent document understanding, detailed analysis, or comprehensive data extraction
- **Performance**: 5-30 seconds (API-based, cached results return instantly)

### PyMuPDF4LLM (Fast Extraction) ⚡
- **Best for**: Quick extraction, basic markdown conversion, rapid text retrieval
- **Features**: 
  - Lightning-fast local processing
  - Markdown output with formatting
  - Multi-page support
  - Basic table detection
  - No external dependencies
- **Status**: Always active (built-in)
- **Use when**: You need speed over deep analysis
- **Performance**: < 1 second (local processing)

### Auto Selection 🤖
- Intelligently chooses the best provider based on your request
- Optimizes for speed vs. quality automatically
- Considers document type, analysis complexity, and available providers
- Falls back to PyMuPDF4LLM if LlamaParse is unavailable

## Input Formats

### Local Files
- **Relative paths**: `./document.pdf`, `../folder/file.pdf`
- **Absolute paths**: `/home/user/document.pdf`, `/Users/name/file.pdf`
- **Current directory**: `document.pdf`, `file.docx`

### Internet URLs
- **Direct PDF links**: `https://example.com/document.pdf`
- **Public documents**: Any publicly accessible PDF URL
- **Common sources**: arXiv, SEC, government sites, academic papers

### Supported Formats
- **PDF** (primary format, best support)
- **Office Documents**: DOCX, PPTX, XLSX
- **Text Formats**: MD, TXT, CSV, TSV, JSON, XML
- **Web Formats**: HTML
- **Email**: EML, MSG
- **E-books**: EPUB
- **Other**: RTF, RST, ORG, ODT, ODS, ODP
- **Images**: PNG, JPG (with OCR providers - planned)

## Usage Patterns

### Quick Overview
```
"Peek at [document] to see its structure"
"Show me what's in [document]"
"Get metadata for [document]"
```

### Entity Extraction
```
"Extract all parties and dates from [contract]"
"Find all people and organizations in [document]"
"Identify monetary amounts in [invoice]"
```

### Structure Analysis
```
"Map the complete structure of [manual]"
"Show all sections and subsections in [document]"
"Find the hierarchy of [specification]"
```

### Content Extraction
```
"Extract pages 5-10 from [document] as markdown"
"Convert [document] to plain text"
"Get all tables from [report] as JSON"
```

### Custom Analysis
```
"Analyze [contract] and extract all obligations and deadlines"
"Review [report] for risk factors and mitigations"
"Find all technical requirements in [specification]"
```

### Maximum Data Extraction (LlamaParse)
```
# Complete comprehensive extraction - returns ALL available data
"Xray [document] with provider llama-parse and custom instructions: 'Extract ALL possible information from this document including: 1) Complete text content preserving exact formatting, whitespace, line breaks, and indentation. 2) All tables with complete data, headers, and cell values in structured format. 3) All images with detailed descriptions, captions, alt text, and positioning. 4) Complete document metadata including author, creation date, modification date, title, subject, keywords. 5) Full document structure with all sections, subsections, headings at every level. 6) All form fields and their values. 7) All hyperlinks and cross-references. 8) All footnotes, endnotes, and annotations. 9) All mathematical equations and formulas. 10) Page-by-page layout information including margins, columns, text blocks. 11) All font information, text styling, and formatting. 12) Any embedded files or attachments. 13) Complete table of contents if present. 14) All lists, both numbered and bulleted. 15) Any watermarks or background elements. Extract entities including all person names, organization names, dates, times, monetary amounts, percentages, locations, addresses, phone numbers, email addresses, URLs, legal references, product names, and technical terms. Preserve the complete document hierarchy and relationships between all elements. Include comprehensive analysis of document purpose, key findings, and relationships between entities.'"

# Simplified maximum extraction
"Xray [document] with provider llama-parse"
```

## Smart Prompting Guide

### For Legal Documents
- Request: Parties, dates, obligations, terms, conditions
- Example: "Extract all parties, payment terms, and termination clauses from lease.pdf"

### For Technical Documentation
- Request: Requirements, specifications, code examples, APIs
- Example: "Map all functions and parameters in api_documentation.pdf"

### For Financial Reports
- Request: Metrics, revenue, risks, projections
- Example: "Xray 10-K.pdf for financial metrics and forward-looking statements"

### For Academic Papers
- Request: Authors, methodology, findings, citations
- Example: "Extract methodology and conclusions from research_paper.pdf"

## Performance Optimization

### Fast Operations (< 1 second)
- Peek with pymupdf4llm
- Basic text extraction
- Page count and metadata

### Moderate Operations (1-5 seconds)
- Document mapping
- Markdown conversion
- Multi-page extraction

### Intensive Operations (5-30 seconds)
- AI-powered xray analysis
- Custom instruction processing
- Large document analysis

## Error Handling

### Common Issues and Solutions
1. **"Provider not configured"**: Add required API keys to environment
2. **"Document not accessible"**: Check file path or URL accessibility
3. **"Unsupported format"**: Convert to PDF or use appropriate provider
4. **"Timeout"**: Document too large, try specific page ranges

## Advanced Features

### Intelligent Caching System
- **Automatic caching**: All results cached in .docsray directories
- **Multi-level caching**: Document-level and operation-specific caching
- **Instant retrieval**: Subsequent requests return instantly from cache
- **Smart invalidation**: Cache automatically invalidates when documents change
- **LlamaParse integration**: Special caching for API-based operations
- **Storage efficiency**: Compressed storage with metadata tracking

### Dynamic Provider Discovery
- **Runtime detection**: Providers auto-discovered based on available dependencies
- **Capability reporting**: Tools report actual capabilities based on enabled providers
- **Graceful fallbacks**: Automatic fallback to available providers
- **Status monitoring**: Real-time provider health and availability checking

### Batch Processing
- Process multiple documents sequentially
- Compare results across providers
- Extract from multiple sources
- Maintain session context across operations

### Custom Instructions (LlamaParse)
- Provide specific analysis criteria
- Focus on particular aspects (entities, relationships, specific data)
- Use domain-specific terminology
- Support for complex, multi-step analysis instructions
- **Maximum Extraction Technique**: Use comprehensive instructions in xray operation to extract ALL data
- **Full Data Access**: The xray operation returns the complete `full_extraction` data structure
- **Cached Results**: All LlamaParse extractions are cached and returned in full during xray

## Best Practices

1. **Start with Peek**: Always peek first to understand document structure
2. **Use Appropriate Provider**: LlamaParse for analysis, PyMuPDF4LLM for speed
3. **Be Specific**: Provide clear extraction instructions
4. **Leverage Caching**: Repeated operations on same document are free
5. **Handle Pages**: Extract specific pages for large documents

## Examples by Use Case

### Contract Analysis
```
1. Peek at contract.pdf to see structure
2. Xray contract.pdf to extract all parties and terms
3. Extract specific sections as needed
```

### Research Paper Review
```
1. Map the structure of paper.pdf
2. Extract methodology section
3. Find all citations and references
```

### Financial Report Processing
```
1. Xray report.pdf for key metrics
2. Extract all tables as JSON
3. Find specific sections by name
```

### Documentation Navigation
```
1. Map complete structure of manual.pdf
2. Seek to specific sections
3. Extract relevant pages
```

## Response Format

All tools return structured JSON with:
- **Success**: Extracted content, metadata, provider info
- **Error**: Clear error message, suggestions for resolution
- **Metadata**: Processing time, provider used, cache status, operation details
- **Provider Info**: Which provider was used, why it was selected
- **Cache Status**: Whether result was cached, cache hit/miss information
- **Document Info**: Format, page count, file size, accessibility status

## Rate Limits and Quotas

- **PyMuPDF4LLM**: Unlimited (local processing, no external dependencies)
- **LlamaParse**: Based on API plan (typically 1000 pages/day free tier)
- **Caching**: Unlimited local storage, dramatically reduces API usage
- **Concurrent Operations**: Configurable via DOCSRAY_MAX_CONCURRENT_REQUESTS (default: 5)
- **Timeout Handling**: Configurable via DOCSRAY_TIMEOUT_SECONDS (default: 30)

## Security and Privacy

- **Local Processing**: PyMuPDF4LLM processes files entirely locally
- **Secure Downloads**: URLs fetched securely via HTTPS with certificate verification
- **API Key Security**: Keys never exposed in responses or logs
- **Cache Control**: Local .docsray cache directories, user-controlled
- **Data Isolation**: Each document gets isolated cache directory
- **No Permanent Storage**: Only cached with user consent via cache system
- **Privacy**: LlamaParse API usage subject to LlamaIndex privacy policy

## Getting Started

1. **Simple Test**:
   ```
   Peek at ./tests/files/sample_lease.pdf
   ```

2. **URL Test**:
   ```
   Peek at https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
   ```

3. **Analysis Test**:
   ```
   Xray ./tests/files/sample_lease.pdf and extract all entities
   ```

## Support and Feedback

- Check provider status with peek to diagnose issues
- Use specific provider parameter to force provider selection
- Enable debug logging for detailed operation traces

---

*This MCP server is designed to make document processing intelligent, efficient, and accessible. Use natural language to describe what you need, and the system will choose the optimal approach.*