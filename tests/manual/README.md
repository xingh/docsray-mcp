# Manual Test Scripts

This directory contains manual test scripts for testing various Docsray MCP features.

## Test Scripts

### test_providers.py
Tests basic provider functionality (PyMuPDF4LLM).
```bash
python tests/manual/test_providers.py
```

### test_xray.py
Tests the xray functionality with LlamaParse provider.
```bash
python tests/manual/test_xray.py
```

### test_with_env.py
Tests LlamaParse functionality using .env file configuration.
```bash
python tests/manual/test_with_env.py
```

### test_enhanced_llamaparse.py
Tests enhanced LlamaParse features including image extraction, tables, and layout.
```bash
python tests/manual/test_enhanced_llamaparse.py
```

### test_cache_system.py
Tests the LlamaParse caching system.
```bash
python tests/manual/test_cache_system.py
```

## Prerequisites

1. Ensure you have a `.env` file in the project root with required API keys:
   ```
   DOCSRAY_LLAMAPARSE_API_KEY=your_api_key_here
   DOCSRAY_MISTRAL_API_KEY=your_api_key_here
   ```

2. Install all dependencies:
   ```bash
   pip install -e ".[dev,llama-parse,mistral-ocr]"
   ```

## Cache Management

The LlamaParse cache is stored in `tests/tmp/`. To manage the cache:

```bash
# List cached documents
python src/docsray/cli/cache_manager.py list

# Inspect cache for a specific document
python src/docsray/cli/cache_manager.py inspect /path/to/document.pdf

# Clear cache for a specific document
python src/docsray/cli/cache_manager.py clear /path/to/document.pdf

# Clear all cache
python src/docsray/cli/cache_manager.py clear -f
```

## Sample Documents

Test documents are available in `tests/files/`:
- `sample_lease.pdf` - Lease agreement document
- `financial_report.pdf` - Financial report with tables
- `financial_statement.pdf` - Financial statement
- `sample_lease_agreement.pdf` - Another lease agreement