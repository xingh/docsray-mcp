---
sidebar_position: 2
---

# LlamaParse Provider

LlamaParse is Docsray's AI-powered document analysis provider, offering deep document understanding and comprehensive extraction capabilities.

## Overview

LlamaParse leverages advanced language models to provide:
- **AI-powered document analysis** with deep understanding
- **Entity extraction** with high accuracy
- **Custom analysis instructions** for specific use cases  
- **Comprehensive caching** for instant subsequent access
- **Multi-format support** beyond just PDF

## Setup and Configuration

### Getting an API Key

1. Visit [LlamaIndex Cloud](https://cloud.llamaindex.ai)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key (starts with `llx-`)
5. Copy your API key for configuration

### Basic Configuration

```bash
# Set your API key using either method:

# Method 1: Docsray-specific (recommended)
export DOCSRAY_LLAMAPARSE_API_KEY="llx-your-key-here"

# Method 2: Standard LlamaParse env var (also supported)
export LLAMAPARSE_API_KEY="llx-your-key-here"

# Or add to your .env file (DOCSRAY_LLAMAPARSE_API_KEY takes precedence if both are set)
echo "DOCSRAY_LLAMAPARSE_API_KEY=llx-your-key-here" >> .env
# echo "LLAMAPARSE_API_KEY=llx-your-key-here" >> .env  # Alternative
```

> **API Key Priority**: If both `DOCSRAY_LLAMAPARSE_API_KEY` and `LLAMAPARSE_API_KEY` are set, `DOCSRAY_LLAMAPARSE_API_KEY` takes precedence. This allows compatibility with both Docsray-specific and standard LlamaParse configurations.

### Advanced Configuration

```bash
# Processing Mode
LLAMAPARSE_MODE=fast              # Options: fast, accurate, premium

# Timeouts and Limits  
LLAMAPARSE_MAX_TIMEOUT=120        # Max processing time in seconds
LLAMAPARSE_CHECK_INTERVAL=1       # Status check interval

# Language and Instructions
LLAMAPARSE_LANGUAGE=auto          # Document language (auto-detect)
LLAMAPARSE_PARSING_INSTRUCTION="" # Global parsing instructions

# Cache Control
LLAMAPARSE_INVALIDATE_CACHE=false # Force cache refresh
LLAMAPARSE_DO_NOT_CACHE=false     # Disable caching entirely
```

## Processing Modes

LlamaParse offers different processing modes to balance speed vs accuracy:

### Fast Mode (Recommended)
```bash
LLAMAPARSE_MODE=fast
```
- **Processing time**: 5-15 seconds
- **Best for**: Most documents, general analysis
- **Accuracy**: High for standard documents
- **Cost**: Lower API credit usage

### Accurate Mode
```bash
LLAMAPARSE_MODE=accurate
```
- **Processing time**: 15-30 seconds  
- **Best for**: Complex layouts, forms, tables
- **Accuracy**: Higher for challenging documents
- **Cost**: Medium API credit usage

### Premium Mode
```bash
LLAMAPARSE_MODE=premium
```
- **Processing time**: 30+ seconds
- **Best for**: Critical analysis, maximum accuracy needed
- **Accuracy**: Highest available
- **Cost**: Higher API credit usage

## Core Capabilities

### Text Extraction with Formatting

LlamaParse preserves document structure and formatting:

```python
# Extract with full formatting preservation
result = docsray.extract("document.pdf", provider="llama-parse")

# Access formatted content
text = result['extraction']['text']          # Plain text
markdown = result['extraction']['markdown']  # Formatted markdown
```

### Advanced Entity Recognition

Extract structured entities automatically:

```python
result = docsray.xray("contract.pdf", provider="llama-parse")
entities = result['analysis']['extracted_content']['entities']

# Common entity types:
# - PERSON: Individual names
# - ORGANIZATION: Company names
# - DATE: All date formats
# - MONETARY: Amounts, currencies
# - LOCATION: Addresses, places
# - EMAIL: Email addresses
# - PHONE: Phone numbers
# - LEGAL_REFERENCE: Legal citations
```

### Table Extraction with Structure

Extract tables maintaining their structure:

```python
result = docsray.extract("report.pdf", provider="llama-parse")
tables = result['analysis']['full_extraction']['tables']

for table in tables:
    page = table['page']
    html = table['html']          # HTML representation
    data = table['data']          # Structured data
    headers = table['headers']    # Column headers
```

### Image Extraction and Analysis

Extract images with AI-generated descriptions:

```python
result = docsray.xray("document.pdf", provider="llama-parse") 
images = result['analysis']['full_extraction']['images']

for image in images:
    description = image['description']  # AI-generated description
    page = image['page']               # Page location
    metadata = image['metadata']       # Size, format, etc.
```

## Custom Analysis Instructions

Tailor LlamaParse's analysis to your specific needs:

### Basic Instructions

```python
result = docsray.xray(
    "document.pdf",
    provider="llama-parse",
    custom_instructions="Extract all monetary amounts and dates"
)
```

### Comprehensive Instructions

```python
custom_instructions = """
Extract all the following information:
1. All parties involved (people and organizations)
2. All dates (effective dates, deadlines, expiration dates)
3. All monetary amounts with currency
4. All obligations and responsibilities by party
5. All terms and conditions
6. Any penalties or consequences
7. Governing law and jurisdiction

Preserve the exact wording for all critical terms.
Identify relationships between entities and obligations.
Note any conditional clauses or exceptions.
"""

result = docsray.xray(
    "legal-contract.pdf",
    provider="llama-parse", 
    custom_instructions=custom_instructions
)
```

### Domain-Specific Instructions

#### Financial Documents
```python
financial_instructions = """
Extract all financial metrics including:
- Revenue figures by quarter/year
- Growth rates and percentages  
- Profit margins and ratios
- Balance sheet items
- Cash flow data
- Forward guidance and projections
- Risk factors and uncertainties
"""
```

#### Research Papers
```python
research_instructions = """
Extract research paper structure:
- Abstract and key findings
- Methodology and experimental design
- Results with statistical significance
- All citations and references
- Author affiliations and contact info
- Funding sources and acknowledgments
"""
```

#### Legal Documents
```python
legal_instructions = """
Extract legal document elements:
- All parties and their roles
- Effective dates and term lengths
- Financial obligations and payment terms
- Termination conditions and procedures
- Governing law and dispute resolution
- Warranties, representations, and disclaimers
"""
```

## Caching System

LlamaParse includes a sophisticated caching system for optimal performance:

### How Caching Works

1. **Document fingerprinting** - Unique hash based on content
2. **Instruction-aware caching** - Different instructions create separate cache entries
3. **Persistent storage** - Cache survives application restarts
4. **Automatic invalidation** - Detects document changes

### Cache Structure

```
.docsray/
├── document_hash.abcd1234.docsray/
│   ├── metadata.json          # Document metadata
│   ├── extraction_result.json # Full extraction result
│   ├── documents.json         # Processed documents
│   ├── original.pdf          # Original file copy
│   └── pages/                # Individual page content
│       ├── page_001.md
│       ├── page_002.md
│       └── ...
```

### Cache Management

```bash
# Cache location (configurable)
export DOCSRAY_CACHE_DIR=.docsray

# Cache behavior
export DOCSRAY_CACHE_ENABLED=true       # Enable caching (default)
export DOCSRAY_CACHE_TTL=3600          # Cache TTL in seconds

# Force cache refresh for a specific document
export LLAMAPARSE_INVALIDATE_CACHE=true

# Disable caching temporarily
export LLAMAPARSE_DO_NOT_CACHE=true
```

### Cache Benefits

- **Speed**: Instant retrieval (0.1s vs 10-30s processing)
- **Cost**: Avoid repeated API charges
- **Reliability**: Works offline for cached documents
- **Consistency**: Same results across multiple requests

## Error Handling

LlamaParse includes comprehensive error handling:

### Common Error Scenarios

1. **API Key Issues**
   - Invalid or missing API key
   - Insufficient credits
   - Rate limiting

2. **Document Issues**
   - Corrupted or unreadable files
   - Unsupported formats
   - Files too large

3. **Network Issues**
   - Connection timeouts
   - Service unavailability
   - Rate limits

### Automatic Fallbacks

```python
# Docsray automatically handles LlamaParse failures
result = docsray.extract("document.pdf")
# If LlamaParse fails, automatically falls back to PyMuPDF4LLM
```

### Manual Error Handling

```python
try:
    result = docsray.xray("document.pdf", provider="llama-parse")
except Exception as e:
    # Handle specific LlamaParse errors
    if "api_key" in str(e).lower():
        print("API key issue - check your LLAMAPARSE_API_KEY")
    elif "timeout" in str(e).lower():
        print("Processing timeout - try increasing LLAMAPARSE_MAX_TIMEOUT")
    else:
        print(f"LlamaParse error: {e}")
```

## Performance Optimization

### Processing Time Optimization

```bash
# Use fast mode for quicker results
LLAMAPARSE_MODE=fast

# Reduce timeout for faster failures
LLAMAPARSE_MAX_TIMEOUT=60

# More frequent status checks
LLAMAPARSE_CHECK_INTERVAL=0.5
```

### Cost Optimization

```bash
# Enable aggressive caching
DOCSRAY_CACHE_ENABLED=true
DOCSRAY_CACHE_TTL=86400  # 24 hours

# Use specific processing modes strategically
LLAMAPARSE_MODE=fast     # For most documents
LLAMAPARSE_MODE=accurate # Only when needed
```

### Memory Optimization

```bash
# Limit concurrent requests
DOCSRAY_MAX_CONCURRENT_REQUESTS=2

# Process large documents in chunks
DOCSRAY_MAX_FILE_SIZE_MB=50
```

## Supported Formats

LlamaParse supports multiple document formats:

- **PDF** - Primary format, best support
- **DOCX** - Microsoft Word documents  
- **PPTX** - PowerPoint presentations
- **HTML** - Web pages and HTML documents
- **TXT** - Plain text files
- **RTF** - Rich Text Format

## Monitoring and Debugging

### Enable Debug Logging

```bash
export DOCSRAY_LOG_LEVEL=DEBUG
```

### Monitor API Usage

Track your LlamaIndex Cloud usage:
1. Visit [LlamaIndex Cloud Dashboard](https://cloud.llamaindex.ai)
2. Check API usage and remaining credits
3. Monitor processing times and success rates

### Debug Common Issues

```python
# Test provider availability
result = docsray.peek("test.pdf", depth="metadata")
providers = result.get("available_providers", [])
print("llama-parse" in providers)  # Should be True if configured

# Test with simple document first
result = docsray.peek("https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")
```

## Best Practices

1. **API Key Security** - Never commit API keys to version control
2. **Cache Management** - Keep caching enabled for better performance  
3. **Timeout Configuration** - Set reasonable timeouts based on document complexity
4. **Instruction Specificity** - More specific instructions yield better results
5. **Mode Selection** - Use fast mode unless accuracy is critical
6. **Error Handling** - Always handle potential API failures
7. **Cost Monitoring** - Monitor API usage to avoid unexpected charges

## Troubleshooting

### API Key Not Working
```bash
# Verify API key format (should start with llx-)
echo $LLAMAPARSE_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $LLAMAPARSE_API_KEY" https://api.cloud.llamaindex.ai/api/parsing/health
```

### Processing Timeouts
```bash
# Increase timeout
export LLAMAPARSE_MAX_TIMEOUT=180

# Use faster mode
export LLAMAPARSE_MODE=fast
```

### Cache Issues
```bash
# Clear cache
rm -rf .docsray/

# Disable cache temporarily
export DOCSRAY_CACHE_ENABLED=false
```

## Next Steps

- Learn about [PyMuPDF4LLM](./pymupdf) for fast processing
- Compare [Provider Capabilities](./comparison)
- See [Performance Optimization](../advanced/performance)
- Check [API Reference](../providers/overview) for all options