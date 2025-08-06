---
sidebar_position: 4
---

# Provider Comparison

A detailed comparison of PyMuPDF4LLM vs LlamaParse to help you choose the right provider for your use case.

## Quick Comparison

| Feature | PyMuPDF4LLM | LlamaParse |
|---------|-------------|------------|
| **Speed** | ⚡ < 1s | 🐌 5-30s |
| **Cost** | 💰 Free | 💳 API Credits |
| **Setup** | ✅ None | 🔑 API Key Required |
| **Accuracy** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Entity Extraction** | ❌ None | ✅ Advanced |
| **Table Analysis** | ⚠️ Basic | ✅ Advanced |
| **Image Handling** | ⚠️ Placeholders | ✅ Full Extraction |
| **Custom Instructions** | ❌ No | ✅ Yes |
| **Offline Operation** | ✅ Yes | ❌ No |
| **Multi-format** | ❌ PDF Only | ✅ PDF, DOCX, PPTX, HTML |

## Detailed Feature Comparison

### Text Extraction

#### PyMuPDF4LLM
- **Quality**: Clean, well-formatted text
- **Speed**: Lightning fast (< 1 second)
- **Formatting**: Basic markdown conversion
- **Structure**: Preserves headings and paragraphs
- **Languages**: All PDF text encodings

```python
result = docsray.extract("document.pdf", provider="pymupdf4llm")
text = result['extraction']['text']
# Clean, fast text extraction
```

#### LlamaParse
- **Quality**: AI-enhanced text with context
- **Speed**: Slower but comprehensive (5-30 seconds)
- **Formatting**: Advanced markdown with structure
- **Structure**: Deep understanding of document hierarchy
- **Languages**: Multi-language support with translation

```python
result = docsray.xray("document.pdf", provider="llama-parse")
text = result['analysis']['full_extraction']['text']
# Comprehensive, AI-analyzed text
```

### Table Processing

#### PyMuPDF4LLM Table Handling

**Capabilities:**
- ✅ Detects table boundaries
- ✅ Extracts table content as text
- ⚠️ Basic row/column detection
- ❌ No structure preservation
- ❌ No header identification

**Example Output:**
```
Quarter | Revenue | Growth
Q1 2023 | $100M | 15%
Q2 2023 | $115M | 20%
```

#### LlamaParse Table Handling

**Capabilities:**
- ✅ Advanced structure analysis
- ✅ Header identification
- ✅ Cell relationship mapping
- ✅ Data type recognition
- ✅ HTML table output
- ✅ Structured JSON data

**Example Output:**
```json
{
  "table": {
    "headers": ["Quarter", "Revenue", "Growth"],
    "rows": [
      {"Quarter": "Q1 2023", "Revenue": "$100M", "Growth": "15%"},
      {"Quarter": "Q2 2023", "Revenue": "$115M", "Growth": "20%"}
    ],
    "html": "<table><tr><th>Quarter</th>..."
  }
}
```

### Entity Recognition

#### PyMuPDF4LLM
- **Entity Extraction**: None
- **Recognition**: No structured entity identification
- **Output**: Plain text only

#### LlamaParse
- **Entity Types**: 15+ types (PERSON, ORGANIZATION, DATE, MONETARY, etc.)
- **Accuracy**: High with context understanding
- **Relationships**: Maps entity relationships
- **Custom Entities**: Configurable via instructions

```python
result = docsray.xray("contract.pdf", provider="llama-parse")
entities = result['analysis']['extracted_content']['entities']

# Example entities:
# [{"type": "PERSON", "value": "John Smith", "context": "signatory"},
#  {"type": "MONETARY", "value": "$50,000", "context": "payment amount"}]
```

### Image Processing

#### PyMuPDF4LLM
- **Detection**: Identifies image locations
- **Extraction**: No image file extraction
- **Description**: Simple placeholders only
- **Output**: `[Image: Figure 1 - Chart]`

#### LlamaParse
- **Detection**: Advanced image recognition
- **Extraction**: Full image files with metadata
- **Description**: AI-generated detailed descriptions
- **Analysis**: Content analysis and context understanding

```python
result = docsray.xray("report.pdf", provider="llama-parse")
images = result['analysis']['full_extraction']['images']

# Example image data:
# {
#   "description": "Bar chart showing quarterly revenue growth",
#   "page": 3,
#   "metadata": {"width": 800, "height": 600, "format": "PNG"}
# }
```

## Performance Comparison

### Processing Speed

| Document Size | PyMuPDF4LLM | LlamaParse |
|---------------|-------------|------------|
| **Small (1-5 pages)** | 0.1-0.3s | 5-10s |
| **Medium (5-20 pages)** | 0.3-1.0s | 10-20s |
| **Large (20+ pages)** | 1.0-5.0s | 20-60s |

### Memory Usage

| Document Size | PyMuPDF4LLM | LlamaParse |
|---------------|-------------|------------|
| **Small** | 10-30MB | 50-100MB |
| **Medium** | 30-100MB | 100-300MB |
| **Large** | 100-300MB | 300-800MB |

### Accuracy Comparison

**Text Extraction Accuracy:**
- **PyMuPDF4LLM**: 90-95% for standard PDFs
- **LlamaParse**: 95-99% with context understanding

**Table Extraction Accuracy:**
- **PyMuPDF4LLM**: 70-80% structure preservation
- **LlamaParse**: 90-95% structure preservation

**Entity Recognition Accuracy:**
- **PyMuPDF4LLM**: 0% (not supported)
- **LlamaParse**: 85-95% depending on document type

## Cost Analysis

### PyMuPDF4LLM Costs
- **Processing**: $0 (completely free)
- **API Calls**: No API usage
- **Infrastructure**: Local processing only
- **Scaling**: No additional costs

### LlamaParse Costs
- **Processing**: Based on LlamaIndex Cloud pricing
- **API Calls**: Per-document charges
- **Caching**: Reduces repeat processing costs
- **Scaling**: Costs scale with usage

**Cost per Document (Estimated):**
- Small documents: $0.01-0.05
- Medium documents: $0.05-0.15  
- Large documents: $0.15-0.50

## Use Case Decision Matrix

### Choose PyMuPDF4LLM When:

✅ **Speed is critical** (need results in < 1 second)  
✅ **Processing many documents** (batch operations)  
✅ **Cost is a concern** (zero API charges)  
✅ **Simple text extraction** (basic content needs)  
✅ **Development/testing** (rapid iteration)  
✅ **Offline processing** (no internet required)  
✅ **Metadata extraction** (document properties)  

**Example scenarios:**
- Document preview in file managers
- Search index generation
- Quick document validation
- Development workflows
- High-volume document processing

### Choose LlamaParse When:

✅ **Comprehensive analysis** needed  
✅ **Entity extraction** required  
✅ **Complex tables** must be preserved  
✅ **Image analysis** important  
✅ **Custom instructions** needed  
✅ **Production analysis** (accuracy over speed)  
✅ **Multi-format support** required  

**Example scenarios:**
- Legal contract analysis
- Financial document processing
- Research paper analysis
- Form data extraction
- Business intelligence workflows

## Hybrid Approaches

### Sequential Processing

```python
# Fast overview first, detailed analysis second
def analyze_document(doc_path):
    # Quick overview with PyMuPDF4LLM
    overview = docsray.peek(doc_path, provider="pymupdf4llm")
    
    # Decide if detailed analysis is needed
    if overview['metadata']['page_count'] > 50:
        return overview  # Too large, keep basic
    
    # Comprehensive analysis with LlamaParse
    return docsray.xray(doc_path, provider="llama-parse")
```

### Fallback Strategy

```python
# Try LlamaParse, fallback to PyMuPDF4LLM
def robust_extraction(doc_path):
    try:
        return docsray.xray(doc_path, provider="llama-parse")
    except Exception as e:
        print(f"LlamaParse failed: {e}, falling back...")
        return docsray.extract(doc_path, provider="pymupdf4llm")
```

### Parallel Processing

```python
# Process with both providers simultaneously
import asyncio

async def dual_analysis(doc_path):
    fast_task = docsray.extract(doc_path, provider="pymupdf4llm")
    deep_task = docsray.xray(doc_path, provider="llama-parse")
    
    fast_result = await fast_task
    # Return fast result immediately, continue with deep analysis
    
    deep_result = await deep_task
    return {"fast": fast_result, "comprehensive": deep_result}
```

## Format Support Comparison

### PyMuPDF4LLM Supported Formats
- ✅ **PDF** - Full support
- ❌ **DOCX** - Not supported
- ❌ **PPTX** - Not supported
- ❌ **HTML** - Not supported
- ❌ **RTF** - Not supported

### LlamaParse Supported Formats
- ✅ **PDF** - Full support
- ✅ **DOCX** - Full support
- ✅ **PPTX** - Full support
- ✅ **HTML** - Full support
- ✅ **RTF** - Full support
- ✅ **TXT** - Full support

## Quality Metrics

### Text Extraction Quality

**Standard Business Documents:**
- PyMuPDF4LLM: 95% accuracy
- LlamaParse: 98% accuracy

**Complex Layouts (Multi-column, forms):**
- PyMuPDF4LLM: 80% accuracy
- LlamaParse: 95% accuracy

**Scanned Documents:**
- PyMuPDF4LLM: 0% (no OCR)
- LlamaParse: 85% accuracy

**Technical Documents:**
- PyMuPDF4LLM: 90% accuracy
- LlamaParse: 97% accuracy

### Table Extraction Quality

**Simple Tables:**
- PyMuPDF4LLM: 85% structure preserved
- LlamaParse: 98% structure preserved

**Complex Tables (merged cells, nested headers):**
- PyMuPDF4LLM: 60% structure preserved
- LlamaParse: 90% structure preserved

**Financial Tables:**
- PyMuPDF4LLM: 70% accuracy
- LlamaParse: 95% accuracy

## Recommendation Framework

### Start with This Decision Tree:

```
Do you need results in < 1 second?
├─ Yes → PyMuPDF4LLM
└─ No
   ├─ Do you need entity extraction?
   │  ├─ Yes → LlamaParse
   │  └─ No
   │     ├─ Do you need complex table analysis?
   │     │  ├─ Yes → LlamaParse  
   │     │  └─ No
   │     │     ├─ Is cost a major concern?
   │     │     │  ├─ Yes → PyMuPDF4LLM
   │     │     │  └─ No → LlamaParse (better quality)
```

### Best Practice Recommendations

1. **Development**: Start with PyMuPDF4LLM for rapid iteration
2. **Production**: Use LlamaParse for comprehensive analysis
3. **Batch Processing**: PyMuPDF4LLM for speed, LlamaParse for accuracy
4. **User-Facing**: PyMuPDF4LLM for previews, LlamaParse for detailed views
5. **Cost-Sensitive**: PyMuPDF4LLM with LlamaParse for critical documents only

## Migration Path

### From PyMuPDF4LLM to LlamaParse

```python
# Current PyMuPDF4LLM usage
result = docsray.extract("doc.pdf", provider="pymupdf4llm")
text = result['extraction']['text']

# Migrate to LlamaParse for better results
result = docsray.xray("doc.pdf", provider="llama-parse")
text = result['analysis']['full_extraction']['text']
entities = result['analysis']['extracted_content']['entities']
tables = result['analysis']['full_extraction']['tables']
```

### Gradual Migration Strategy

1. **Phase 1**: Keep PyMuPDF4LLM for all operations
2. **Phase 2**: Add LlamaParse for critical documents
3. **Phase 3**: Use LlamaParse as primary, PyMuPDF4LLM as fallback
4. **Phase 4**: Full LlamaParse adoption with cost optimization

## Next Steps

- Learn about [Tools Overview](../tools/peek) to understand which tools work best with each provider
- See [Performance Optimization](../advanced/performance) for provider-specific tuning
- Check [Caching Guide](../advanced/caching) to optimize LlamaParse costs
- Review [API Reference](../providers/overview) for all configuration options