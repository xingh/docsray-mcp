# Manual Test Scripts

This directory contains manual test scripts for debugging and development purposes. These tests are NOT run automatically in CI.

## Available Tests

### test_cache_system.py
Tests the LlamaParse caching system with real API calls.
```bash
python tests/manual/test_cache_system.py
```

### test_with_env.py
Tests LlamaParse functionality with environment variables.
```bash
export LLAMAPARSE_API_KEY="your-key"
python tests/manual/test_with_env.py
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

## Running the Full Test Suite

To run the complete automated test suite:

```bash
# Run all tests (unit + integration)
pytest tests/

# Run only unit tests (fast, no API calls)
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run with coverage report
pytest tests/ --cov=src/docsray --cov-report=html

# Run specific test file
pytest tests/integration/test_tools.py

# Run with verbose output
pytest tests/ -v
```

## Test Organization

- **Unit Tests** (`tests/unit/`): Fast, isolated tests for individual components
- **Integration Tests** (`tests/integration/`): Tests that verify component interactions
- **Manual Tests** (`tests/manual/`): Scripts for debugging with real API calls

## Sample Documents

Test documents are available in `tests/files/`:
- `sample_lease.pdf` - Lease agreement document
- `financial_report.pdf` - Financial report with tables
- `financial_statement.pdf` - Financial statement
- `sample_lease_agreement.pdf` - Another lease agreement