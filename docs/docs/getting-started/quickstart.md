---
sidebar_position: 2
---

# Quickstart

Get started with Docsray in 5 minutes! This guide will walk you through basic usage and show you how to extract everything from documents.

## Your First Document Analysis

### 1. Quick Overview (Peek)

Start by getting a quick overview of any document:

```python
# Local file
"Peek at ./invoice.pdf"

# URL
"Peek at https://example.com/document.pdf"
```

Response shows:
- Page count and file size
- Available extraction formats
- Provider capabilities
- Document metadata

### 2. Extract Everything (Xray)

Use the power of AI to extract ALL data:

```python
"Xray invoice.pdf with provider llama-parse"
```

This returns:
- All text content
- All tables structured
- All images with descriptions
- All entities recognized
- Complete document hierarchy

### 3. Get Specific Content (Extract)

Extract content in your preferred format:

```python
# As markdown
"Extract pages 1-5 from report.pdf as markdown"

# As JSON with tables
"Extract all tables from financial.pdf as JSON"

# Specific pages
"Extract page 3 from contract.pdf"
```

## Maximum Extraction Example

Here's how to get EVERYTHING from a document:

```python
"""
Xray document.pdf with provider llama-parse and custom instructions: 
'Extract ALL possible information including: 
1) Complete text content preserving exact formatting
2) All tables with complete data
3) All images with descriptions
4) Complete document metadata
5) Full document structure
6) All entities (people, orgs, dates, amounts)
7) Page-by-page layout information'
"""
```

## Common Use Cases

### Legal Document Analysis

```python
# Extract all parties and terms
"Xray contract.pdf and extract all parties, dates, and obligations"

# Find specific clauses
"Seek to 'termination clause' in agreement.pdf"
```

### Financial Reports

```python
# Extract financial metrics
"Xray 10-k.pdf for revenue, growth rates, and risk factors"

# Get all tables
"Extract all tables from earnings.pdf as JSON"
```

### Academic Papers

```python
# Map document structure
"Map the structure of research-paper.pdf"

# Extract methodology
"Extract the methodology section from paper.pdf"
```

### Invoice Processing

```python
# Extract key data
"Xray invoice.pdf and extract vendor, amount, date, and line items"

# Get as structured data
"Extract invoice.pdf as JSON with tables"
```

## Working with Providers

### Auto-Selection (Default)
Let Docsray choose the best provider:

```python
"Analyze document.pdf"  # Automatically selects provider
```

### LlamaParse (Comprehensive)
For deep analysis and AI-powered extraction:

```python
"Xray document.pdf with provider llama-parse"
```

Features:
- Entity recognition
- Custom instructions
- Table structure preservation
- Image extraction
- 5-30 second processing

### PyMuPDF (Fast)
For quick text extraction:

```python
"Extract document.pdf with provider pymupdf4llm"
```

Features:
- Sub-second processing
- Basic markdown
- Text extraction
- No API required

## Navigation and Search

### Navigate to Pages

```python
"Seek to page 10 in manual.pdf"
```

### Find Sections

```python
"Seek to 'Introduction' section in thesis.pdf"
```

### Search Content

```python
"Search for 'payment terms' in contract.pdf"
```

## Tips for Best Results

### 1. Start with Peek
Always peek first to understand the document:
```python
"Peek at document.pdf"
```

### 2. Use Specific Instructions
Be specific about what you want:
```python
"Extract all email addresses and phone numbers from contact.pdf"
```

### 3. Leverage Caching
Results are cached - subsequent requests are instant:
```python
"Xray report.pdf"  # First time: 10 seconds
"Xray report.pdf"  # Second time: instant
```

### 4. Handle Large Documents
Process specific pages for large documents:
```python
"Extract pages 1-10 from large-manual.pdf"
```

## Interactive Example

Try this complete workflow:

```python
# 1. Check what's in the document
"Peek at sample.pdf"

# 2. Map the structure
"Map the structure of sample.pdf"

# 3. Extract everything with AI
"Xray sample.pdf with provider llama-parse"

# 4. Get specific content
"Extract tables from sample.pdf as JSON"

# 5. Navigate to specific sections
"Seek to page 5 in sample.pdf"
```

## Next Steps

- Learn about [Providers](../providers/overview) in detail
- See [API Reference](../api/tools) for all options

Ready to extract everything from your documents? Start using Docsray with Claude now!