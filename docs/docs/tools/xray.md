---
sidebar_position: 3
---

# Xray Tool

Perform comprehensive AI-powered document analysis with entity extraction, relationship mapping, and deep insights.

## Overview

The `docsray_xray` tool provides the most comprehensive document analysis available:
- **AI-powered entity extraction** (people, organizations, dates, amounts)
- **Relationship mapping** between entities and concepts
- **Key point identification** and summarization
- **Sentiment analysis** and document tone assessment
- **Custom analysis instructions** for specific use cases
- **Complete document understanding** with context preservation

## Basic Usage

### Comprehensive Analysis

```python
# Full AI analysis with all features
result = docsray.xray("document.pdf")

# Access the rich analysis data
entities = result['analysis']['extracted_content']['entities']
key_points = result['analysis']['extracted_content']['key_points']
relationships = result['analysis']['extracted_content']['relationships']
```

### Custom Analysis Instructions

```python
# Tailored analysis for specific needs
result = docsray.xray(
    "contract.pdf",
    custom_instructions="""
    Extract all parties, dates, monetary amounts, and obligations.
    Identify termination conditions and governing law.
    Map relationships between parties and their responsibilities.
    """
)
```

## Parameters

### document_url (required)
Path or URL to the document for analysis.

```python
docsray.xray("./legal/contract.pdf")
docsray.xray("https://example.com/research-paper.pdf")
```

### analysis_type (optional)
Types of analysis to perform. Default: `["entities", "key-points"]`

Available analysis types:
- **`"entities"`** - Extract people, organizations, dates, amounts, etc.
- **`"relationships"`** - Map connections between entities
- **`"key-points"`** - Identify main ideas and findings
- **`"sentiment"`** - Analyze document tone and sentiment
- **`"structure"`** - Deep structural analysis

```python
# Specific analysis types
docsray.xray("doc.pdf", analysis_type=["entities", "relationships"])

# Comprehensive analysis
docsray.xray("doc.pdf", analysis_type=["entities", "relationships", "key-points", "sentiment"])
```

### custom_instructions (optional)
Detailed instructions for AI analysis. Highly recommended for best results.

```python
# Domain-specific instructions
financial_instructions = """
Extract all financial metrics, revenue figures, growth rates,
profit margins, and forward-looking statements. Identify
risk factors and competitive advantages mentioned.
"""

result = docsray.xray("10k-report.pdf", custom_instructions=financial_instructions)
```

### provider (optional)
Provider for analysis. Default: `"llama-parse"` (recommended)

```python
# Use AI provider for best results
docsray.xray("document.pdf", provider="llama-parse")
```

## Response Structure

### Complete Xray Response

```json
{
  "analysis": {
    "extracted_content": {
      "entities": [
        {
          "type": "PERSON",
          "value": "John Smith",
          "context": "Chief Executive Officer",
          "page": 1,
          "confidence": 0.95
        },
        {
          "type": "MONETARY",
          "value": "$2.5 million",
          "context": "annual revenue",
          "page": 3,
          "confidence": 0.98
        }
      ],
      "key_points": [
        {
          "point": "Company achieved 25% revenue growth in Q3",
          "importance": "high",
          "page": 2,
          "supporting_evidence": ["Table 1: Revenue Growth", "Figure 2: Performance Chart"]
        }
      ],
      "relationships": [
        {
          "entity1": "John Smith",
          "entity2": "Acme Corp",
          "relationship": "CEO of",
          "confidence": 0.92
        }
      ],
      "sentiment": {
        "overall_tone": "positive",
        "confidence_level": "high",
        "key_indicators": ["strong performance", "exceeded expectations"]
      }
    },
    "full_extraction": {
      "documents": [/* complete document data */],
      "pages": [/* page-by-page content */],
      "images": [/* extracted images with descriptions */],
      "tables": [/* structured table data */]
    },
    "summary": {
      "total_entities": 45,
      "entity_types": ["PERSON", "ORGANIZATION", "DATE", "MONETARY"],
      "key_points_count": 12,
      "confidence_score": 0.89,
      "processing_time": 23.5
    }
  },
  "provider": "llama-parse"
}
```

## Entity Types

Xray automatically identifies these entity types:

### People and Organizations
- **PERSON** - Individual names
- **ORGANIZATION** - Company names, institutions
- **ROLE** - Job titles and positions

### Dates and Times
- **DATE** - Specific dates (2023-10-15)
- **TIME_PERIOD** - Quarters, years, ranges
- **DEADLINE** - Due dates and deadlines

### Financial Information
- **MONETARY** - Amounts with currency
- **PERCENTAGE** - Growth rates, margins
- **FINANCIAL_METRIC** - Revenue, profit, ratios

### Location Information
- **LOCATION** - Cities, countries, regions
- **ADDRESS** - Physical addresses
- **FACILITY** - Buildings, offices

### Legal and Regulatory
- **LEGAL_REFERENCE** - Laws, regulations, cases
- **CONTRACT_TERM** - Specific contract clauses
- **COMPLIANCE** - Regulatory requirements

### Technical Information
- **PRODUCT** - Product names and models
- **TECHNOLOGY** - Technical specifications
- **PROCESS** - Procedures and methods

## Use Cases

### Legal Document Analysis

```python
def analyze_legal_contract(contract_path):
    instructions = """
    Extract all parties and their roles, key dates (effective date, 
    termination date, deadlines), monetary terms (payments, penalties),
    governing law, dispute resolution procedures, and termination conditions.
    Identify any unusual or high-risk clauses.
    """
    
    result = docsray.xray(contract_path, 
                         analysis_type=["entities", "relationships", "key-points"],
                         custom_instructions=instructions)
    
    # Extract structured contract data
    contract_data = {
        "parties": [e for e in result['analysis']['extracted_content']['entities'] 
                   if e['type'] in ['PERSON', 'ORGANIZATION']],
        "key_dates": [e for e in result['analysis']['extracted_content']['entities'] 
                     if e['type'] == 'DATE'],
        "financial_terms": [e for e in result['analysis']['extracted_content']['entities'] 
                          if e['type'] == 'MONETARY'],
        "key_points": result['analysis']['extracted_content']['key_points']
    }
    
    return contract_data
```

### Financial Document Analysis

```python
def analyze_financial_report(report_path):
    instructions = """
    Extract all financial metrics including revenue, profit margins,
    growth rates, and key performance indicators. Identify forward-looking
    statements, risk factors, and competitive advantages. Analyze
    year-over-year comparisons and trends.
    """
    
    result = docsray.xray(report_path,
                         analysis_type=["entities", "key-points", "sentiment"],
                         custom_instructions=instructions)
    
    financial_analysis = {
        "metrics": [e for e in result['analysis']['extracted_content']['entities'] 
                   if e['type'] in ['MONETARY', 'PERCENTAGE', 'FINANCIAL_METRIC']],
        "trends": result['analysis']['extracted_content']['key_points'],
        "sentiment": result['analysis']['extracted_content']['sentiment'],
        "risk_factors": [kp for kp in result['analysis']['extracted_content']['key_points']
                        if 'risk' in kp['point'].lower()]
    }
    
    return financial_analysis
```

### Research Paper Analysis

```python
def analyze_research_paper(paper_path):
    instructions = """
    Extract authors and affiliations, research methodology, key findings,
    statistical significance, limitations, and future research directions.
    Identify all citations and references. Summarize the main contribution
    and novelty of the research.
    """
    
    result = docsray.xray(paper_path,
                         analysis_type=["entities", "key-points", "relationships"],
                         custom_instructions=instructions)
    
    research_analysis = {
        "authors": [e for e in result['analysis']['extracted_content']['entities'] 
                   if e['type'] == 'PERSON'],
        "methodology": [kp for kp in result['analysis']['extracted_content']['key_points']
                       if 'method' in kp['point'].lower()],
        "findings": [kp for kp in result['analysis']['extracted_content']['key_points']
                    if kp['importance'] == 'high'],
        "citations": [e for e in result['analysis']['extracted_content']['entities'] 
                     if e['type'] == 'CITATION']
    }
    
    return research_analysis
```

## Advanced Analysis Patterns

### Multi-Document Analysis

```python
def analyze_document_series(document_paths, theme):
    results = {}
    
    instructions = f"""
    Focus on information related to {theme}. Extract all relevant
    entities, key developments, and relationships. Note any changes
    or trends over time.
    """
    
    for doc_path in document_paths:
        result = docsray.xray(doc_path, custom_instructions=instructions)
        results[doc_path] = result['analysis']['extracted_content']
    
    # Aggregate findings across documents
    all_entities = []
    for doc_result in results.values():
        all_entities.extend(doc_result['entities'])
    
    # Find common entities and trends
    entity_counts = {}
    for entity in all_entities:
        key = f"{entity['type']}:{entity['value']}"
        entity_counts[key] = entity_counts.get(key, 0) + 1
    
    return {
        "individual_results": results,
        "common_entities": entity_counts,
        "total_documents": len(document_paths)
    }
```

### Comparative Analysis

```python
def compare_documents(doc1_path, doc2_path, comparison_focus):
    instructions = f"""
    Focus on {comparison_focus}. Extract all relevant information
    that can be used for comparison between documents. Note
    similarities and differences.
    """
    
    result1 = docsray.xray(doc1_path, custom_instructions=instructions)
    result2 = docsray.xray(doc2_path, custom_instructions=instructions)
    
    # Extract entities for comparison
    entities1 = {f"{e['type']}:{e['value']}" for e in result1['analysis']['extracted_content']['entities']}
    entities2 = {f"{e['type']}:{e['value']}" for e in result2['analysis']['extracted_content']['entities']}
    
    comparison = {
        "common_entities": entities1.intersection(entities2),
        "unique_to_doc1": entities1 - entities2,
        "unique_to_doc2": entities2 - entities1,
        "doc1_key_points": result1['analysis']['extracted_content']['key_points'],
        "doc2_key_points": result2['analysis']['extracted_content']['key_points']
    }
    
    return comparison
```

## Performance and Caching

### Processing Performance

| Document Size | Typical Time | Memory Usage |
|---------------|-------------|--------------|
| Small (1-10 pages) | 5-15s | 50-150MB |
| Medium (10-50 pages) | 15-60s | 150-500MB |
| Large (50+ pages) | 60-180s | 500MB-1GB |

### Caching Benefits

Xray results are automatically cached with LlamaParse:

```python
# First analysis - full processing
result1 = docsray.xray("document.pdf")  # 30 seconds

# Subsequent analysis - instant from cache
result2 = docsray.xray("document.pdf")  # 0.1 seconds

# Different instructions - new processing
result3 = docsray.xray("document.pdf", 
                      custom_instructions="Extract only financial data")  # 30 seconds
```

## Error Handling

```python
def robust_xray_analysis(document_path, instructions=None):
    try:
        result = docsray.xray(document_path, 
                             custom_instructions=instructions)
        
        if "error" in result:
            return None, result["error"]
        
        # Validate result quality
        analysis = result['analysis']['extracted_content']
        if len(analysis['entities']) == 0:
            return None, "No entities extracted - document may be empty or unreadable"
        
        return result, None
        
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower():
            return None, "LlamaParse API key not configured"
        elif "timeout" in error_msg.lower():
            return None, "Analysis timeout - document may be too large"
        else:
            return None, f"Analysis failed: {error_msg}"

# Usage with error handling
analysis, error = robust_xray_analysis("document.pdf")
if error:
    print(f"Analysis failed: {error}")
else:
    entities = analysis['analysis']['extracted_content']['entities']
    print(f"Extracted {len(entities)} entities")
```

## Custom Instructions Guide

### Effective Instruction Writing

```python
# Good: Specific and detailed
good_instructions = """
Extract all contract parties with their roles and contact information.
Identify key dates including effective date, termination date, and any deadlines.
Find all monetary amounts including payments, penalties, and deposits.
Note any termination conditions, renewal clauses, and governing law.
"""

# Poor: Vague and general
poor_instructions = "Extract important information from this contract."

# Use the good instructions
result = docsray.xray("contract.pdf", custom_instructions=good_instructions)
```

### Domain-Specific Templates

#### Legal Documents
```python
legal_template = """
Extract all parties and their legal roles. Identify key dates (execution,
effective, termination). Find all monetary terms (amounts, payment schedules,
penalties). Note governing law, jurisdiction, dispute resolution procedures,
termination conditions, and any unusual or high-risk clauses.
"""
```

#### Financial Reports
```python
financial_template = """
Extract all financial metrics (revenue, profit, margins, ratios).
Identify growth rates and year-over-year comparisons. Find forward-looking
statements and guidance. Note risk factors, competitive advantages,
and market conditions discussed.
"""
```

#### Academic Papers
```python
academic_template = """
Extract authors, affiliations, and contact information. Identify research
methodology, sample sizes, and statistical methods. Find key findings,
statistical significance, and confidence intervals. Note limitations,
future research directions, and novel contributions.
"""
```

## Best Practices

1. **Provide Detailed Instructions** - More specific instructions yield better results
2. **Use Appropriate Analysis Types** - Select only needed analysis types for faster processing
3. **Leverage Caching** - Identical documents and instructions use cached results
4. **Handle Large Documents** - Consider processing in sections for very large documents
5. **Validate Results** - Always check entity counts and confidence scores
6. **Provider Selection** - Always use LlamaParse for xray operations

## Integration Examples

### Document Processing Pipeline

```python
class DocumentProcessor:
    def __init__(self):
        self.processed_docs = {}
    
    def process_document(self, doc_path, doc_type):
        # Get appropriate instructions for document type
        instructions = self.get_instructions_for_type(doc_type)
        
        # Perform xray analysis
        result = docsray.xray(doc_path, custom_instructions=instructions)
        
        # Store processed results
        self.processed_docs[doc_path] = {
            "analysis": result['analysis']['extracted_content'],
            "processed_at": datetime.now(),
            "document_type": doc_type
        }
        
        return result
    
    def get_instructions_for_type(self, doc_type):
        instructions = {
            "contract": "Extract parties, dates, amounts, terms, and conditions...",
            "financial": "Extract financial metrics, growth rates, and projections...",
            "research": "Extract methodology, findings, and conclusions..."
        }
        return instructions.get(doc_type, "Extract key information and entities.")
```

## Next Steps

- Learn about [Extract Tool](./extract) for content extraction based on xray findings
- See [Seek Tool](./seek) for navigation to specific entities or sections
- Review [API Reference](../api/tools) for complete parameter documentation