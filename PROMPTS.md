# Docsray MCP Prompts Showcase

This document contains example prompts that demonstrate docsray's capabilities with both local files and internet URLs. Each prompt can be executed directly.

## 🚀 Quick Start - Basic Capabilities

### 1. Document Overview (PEEK)
Get a quick overview of any document's structure and available formats.

**Local File Examples:**
```
Peek at ./tests/files/sample_lease.pdf to see its structure and metadata
Show me what's in ../documents/report.pdf
Get an overview of ./README.md
```

**Internet URL Examples:**
```
Peek at https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
Show me the structure of https://arxiv.org/pdf/2301.00234.pdf
What's in this PDF: https://www.adobe.com/support/products/enterprise/knowledgecenter/media/c4611_sample_explain.pdf
```

## 📊 Document Analysis (XRAY)

### 2. Entity Extraction
Extract named entities, organizations, dates, and key information.

**Local File Examples:**
```
Xray ./contracts/agreement.pdf and extract all parties, dates, and monetary amounts
Analyze ../legal/lease.pdf to find all entities and obligations
Extract all company names and people from ./business/proposal.pdf
```

**Internet URL Examples:**
```
Xray https://www.sec.gov/files/form10-k.pdf and extract all financial metrics
Analyze this research paper https://arxiv.org/pdf/2301.00234.pdf for authors and methodologies
Extract entities from https://www.un.org/sites/un2.un.org/files/2021/03/udhr.pdf
```

### 3. Key Points and Summaries
Get the main ideas and critical information.

**Local File Examples:**
```
Extract key points from ./research/study.pdf
What are the main findings in ../reports/analysis.pdf?
Summarize the important points in ./documents/whitepaper.pdf
```

**Internet URL Examples:**
```
Extract key points from https://bitcoin.org/bitcoin.pdf
What are the main ideas in https://arxiv.org/pdf/1706.03762.pdf (Attention is All You Need)
Summarize https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_SPM.pdf
```

## 🗺️ Document Mapping (MAP)

### 4. Structure Analysis
Map out the complete document hierarchy and organization.

**Local File Examples:**
```
Map the structure of ./manual/user_guide.pdf including all sections
Show me the complete hierarchy of ../books/textbook.pdf
Create a detailed map of ./specs/technical_specification.pdf
```

**Internet URL Examples:**
```
Map out the structure of https://www.postgresql.org/files/documentation/pdf/16/postgresql-16-US.pdf
Show the document hierarchy of https://docs.python.org/3/archives/python-3.12.0-docs-pdf-letter.zip
Map this AWS whitepaper: https://docs.aws.amazon.com/pdfs/wellarchitected/latest/framework/wellarchitected-framework.pdf
```

## 📝 Content Extraction (EXTRACT)

### 5. Text and Markdown Extraction
Convert documents to various formats.

**Local File Examples:**
```
Extract text from ./documents/report.pdf as markdown
Convert ../presentations/slides.pdf to markdown format
Get the content of ./articles/paper.pdf in plain text
```

**Internet URL Examples:**
```
Extract markdown from https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
Convert https://www.adobe.com/support/products/enterprise/knowledgecenter/media/c4611_sample_explain.pdf to text
Get markdown content from https://arxiv.org/pdf/2301.00234.pdf
```

### 6. Page-Specific Extraction
Extract specific pages or ranges.

**Local File Examples:**
```
Extract pages 5-10 from ./reports/annual_report.pdf
Get only the first page of ../documents/contract.pdf
Extract pages 1, 3, 5, 7 from ./manual/guide.pdf
```

**Internet URL Examples:**
```
Extract pages 1-5 from https://www.un.org/sites/un2.un.org/files/2021/03/udhr.pdf
Get page 10 from https://bitcoin.org/bitcoin.pdf
Extract the executive summary (pages 1-3) from https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_SPM.pdf
```

## 🔍 Advanced Analysis

### 7. Custom Instructions
Provide specific analysis instructions for AI-powered providers.

**Local File Examples:**
```
Analyze ./contracts/service_agreement.pdf and extract all SLA metrics, penalties, and performance criteria
Xray ../medical/patient_record.pdf to identify all diagnoses, medications, and treatment plans
Review ./financial/statement.pdf and list all assets, liabilities, and cash flows
```

**Internet URL Examples:**
```
Analyze https://www.sec.gov/files/form10-k.pdf with focus on risk factors and competitive threats
Xray https://arxiv.org/pdf/2301.00234.pdf and extract all mathematical equations and algorithms
Review https://www.federalreserve.gov/monetarypolicy/files/fomcprojtabl20240918.pdf for economic projections
```

### 8. Navigation and Seeking (SEEK)
Navigate to specific pages, sections, or search for content within documents.

**Local File Examples:**
```
Seek to page 15 in ./manual/user_guide.pdf and extract the content
Find the "Conclusion" section in ../reports/analysis.pdf
Search for "payment terms" in ./contracts/agreement.pdf and show the relevant section
Go to page 5 of ./presentation/slides.pdf
```

**Internet URL Examples:**
```
Seek to page 10 in https://bitcoin.org/bitcoin.pdf
Find the "Abstract" section in https://arxiv.org/pdf/2301.00234.pdf
Search for "methodology" in https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_SPM.pdf
Navigate to page 3 of https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
```

### 9. Comparison Analysis
Compare extraction quality between providers.

**Local File Examples:**
```
Compare how pymupdf4llm vs llama-parse extract content from ./sample.pdf
Show me the difference in entity extraction between providers for ../contract.pdf
Which provider best handles tables in ./data/spreadsheet.pdf?
Extract with provider pymupdf4llm from ./document.pdf (fast extraction)
Extract with provider llama-parse from ./document.pdf (AI analysis)
```

**Provider-Specific Examples:**
```
# Fast extraction with PyMuPDF4LLM
Extract text from ./report.pdf using provider pymupdf4llm
Peek at ./document.pdf with provider pymupdf4llm for quick overview

# AI-powered analysis with LlamaParse
Xray ./contract.pdf with provider llama-parse for deep entity extraction
Analyze ./research.pdf using provider llama-parse with custom instructions: "Focus on methodology and statistical significance"
```

## 🚀 Maximum Data Extraction (Comprehensive Analysis)

### 10. Complete Document Extraction with LlamaParse
Extract ALL available data from a document using LlamaParse's full capabilities.

**Maximum Extraction Prompt:**
```
Xray ./document.pdf with provider llama-parse and custom instructions: "Extract ALL possible information from this document including: 1) Complete text content preserving exact formatting, whitespace, line breaks, and indentation. 2) All tables with complete data, headers, and cell values in structured format. 3) All images with detailed descriptions, captions, alt text, and positioning. 4) Complete document metadata including author, creation date, modification date, title, subject, keywords. 5) Full document structure with all sections, subsections, headings at every level. 6) All form fields and their values. 7) All hyperlinks and cross-references. 8) All footnotes, endnotes, and annotations. 9) All mathematical equations and formulas. 10) Page-by-page layout information including margins, columns, text blocks. 11) All font information, text styling, and formatting. 12) Any embedded files or attachments. 13) Complete table of contents if present. 14) All lists, both numbered and bulleted. 15) Any watermarks or background elements. Extract entities including all person names, organization names, dates, times, monetary amounts, percentages, locations, addresses, phone numbers, email addresses, URLs, legal references, product names, and technical terms. Preserve the complete document hierarchy and relationships between all elements. Include comprehensive analysis of document purpose, key findings, and relationships between entities."
```

**Why This Works:**
- The `xray` operation returns the complete `full_extraction` data from LlamaParse
- Custom instructions trigger comprehensive AI analysis
- All cached extraction data is returned in a single response
- Includes both raw data and AI-analyzed insights

**Simplified Versions for Specific Needs:**

```
# For complete raw data extraction
Xray ./document.pdf with provider llama-parse

# For entity-focused extraction
Xray ./document.pdf with provider llama-parse and custom instructions: "Extract all entities including people, organizations, dates, locations, monetary amounts, legal references, and their relationships"

# For structural analysis
Xray ./document.pdf with provider llama-parse and custom instructions: "Extract complete document structure including all sections, subsections, tables, images, cross-references, and preserve all layout information"

# For content and formatting
Xray ./document.pdf with provider llama-parse and custom instructions: "Extract all text content preserving exact formatting, indentation, lists, equations, and styling information"
```

## 🎯 Specific Use Cases

### 11. Legal Documents
```
Analyze ./lease.pdf and extract: tenant names, landlord, rent amount, lease term, and all obligations
Xray ../nda.pdf to find all confidentiality clauses and exceptions
Map the structure of ./terms_of_service.pdf including all sections and subsections
```

### 11. Technical Documentation
```
Extract all code examples from ./api_documentation.pdf
Map the structure of ../software_manual.pdf with all functions and parameters
Find all system requirements in ./installation_guide.pdf
```

### 12. Financial Reports
```
Xray ./10-k.pdf and extract all revenue figures, growth rates, and forward guidance
Analyze ../quarterly_report.pdf for segment performance and geographic breakdown
Extract all financial tables from ./earnings_report.pdf as JSON
```

### 13. Academic Papers
```
Extract methodology section from ./research_paper.pdf
Find all citations and references in ../thesis.pdf
Analyze ./journal_article.pdf for hypothesis, methods, results, and conclusions
```

## 🌐 Working with Different Sources

### 14. Public Documents
```
Analyze https://www.whitehouse.gov/wp-content/uploads/2022/10/Biden-Harris-Administrations-National-Security-Strategy-10.2022.pdf
Extract key policies from https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/1234567/policy.pdf
Map the structure of https://europa.eu/documents/official_document.pdf
```

### 15. Research Papers (arXiv)
```
Xray https://arxiv.org/pdf/2103.00020.pdf (CLIP paper) for model architecture
Extract abstract and conclusion from https://arxiv.org/pdf/2005.11401.pdf (GPT-3 paper)
Find all datasets mentioned in https://arxiv.org/pdf/1810.04805.pdf (BERT paper)
```

### 16. Standards and Specifications
```
Map the structure of https://www.w3.org/TR/WCAG21/wcag21.pdf
Extract all requirements from https://www.iso.org/files/live/sites/isoorg/files/store/en/PUB100080.pdf
Find all test criteria in https://datatracker.ietf.org/doc/pdf/rfc9110.pdf
```

## 💡 Tips for Best Results

### Provider Selection
- **LlamaParse**: Use for deep analysis, entity extraction, custom instructions, AI-powered understanding
- **PyMuPDF4LLM**: Use for fast extraction, basic markdown conversion, quick text retrieval
- **Auto**: Let the system choose based on your request and document type

### Path Formats
- Relative paths: `./file.pdf`, `../folder/file.pdf`
- Absolute paths: `/home/user/documents/file.pdf`, `/Users/name/Documents/file.pdf`
- URLs: Must start with `http://` or `https://` and be publicly accessible

### Performance Tips
```
# Quick overview (fast, < 1 second)
Peek at ./document.pdf with provider pymupdf4llm

# Deep analysis (slower but comprehensive, 5-30 seconds)
Xray ./document.pdf with provider llama-parse

# Let system choose automatically
Analyze ./document.pdf

# Specific page extraction (fast)
Extract page 5 from ./document.pdf

# Navigate to specific sections
Seek to "Introduction" section in ./document.pdf
```

### Caching Benefits
- Results are automatically cached in .docsray directories
- Subsequent requests to the same document are instant
- Cache works for all providers and operations
- Cache automatically invalidates when documents change

### File Format Support
- **Primary**: PDF (best support)
- **Office**: DOCX, PPTX, XLSX
- **Text**: MD, TXT, CSV, JSON, XML
- **Web**: HTML pages
- **Email**: EML, MSG files
- **Other**: EPUB, RTF, ODT, ODS, ODP

## 🧪 Test These Prompts

You can test any of these prompts directly. For example:

1. **Test with local sample:**
   ```
   Peek at ./tests/files/sample_lease.pdf
   ```

2. **Test with public URL:**
   ```
   Peek at https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
   ```

3. **Test entity extraction:**
   ```
   Xray ./tests/files/sample_lease.pdf and extract all parties and dates
   ```

4. **Test structure mapping:**
   ```
   Map the complete structure of ./tests/files/sample_lease.pdf
   ```

---

*Note: Replace file paths with your actual documents. URLs should be publicly accessible PDFs.*