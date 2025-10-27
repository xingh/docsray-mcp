# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Docsray MCP** is a Model Context Protocol (MCP) server that provides AI assistants with advanced document perception capabilities. It extracts text, navigates pages, analyzes structure, and understands documents through a multi-provider architecture.

Built with FastMCP framework, it offers 5 core tools (`peek`, `map`, `xray`, `extract`, `seek`) and supports multiple document providers (PyMuPDF4LLM, LlamaParse, IBM Docling, MIMIC DocsRay) with intelligent provider selection based on document characteristics and operation requirements.

## Common Commands

### Development

```bash
# Install for development
pip install -e ".[dev]"

# Install all optional dependencies (AI, OCR, dev, docker)
pip install -e ".[all]"

# Start the MCP server (default: stdio transport)
docsray start
# Or: python -m docsray.cli start

# Start with HTTP transport for testing
docsray start --transport http --port 3000

# Start with verbose logging
docsray start --verbose
```

### Testing

```bash
# Run all tests
pytest

# Run only unit tests (fast, no API calls)
pytest tests/unit/

# Run integration tests (requires API keys)
pytest tests/integration/

# Run with coverage
pytest --cov=src/docsray --cov-report=html

# Run specific test file
pytest tests/unit/test_providers.py -v

# Run specific test
pytest tests/unit/test_providers.py::test_provider_registry -v
```

### Code Quality

```bash
# Lint code
ruff check src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/

# Format code
black src/ tests/

# Type checking
mypy src/

# Run all pre-commit checks
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

### Docker

```bash
# Build Docker image
make docker-build
# Or: docker build -t docsray-mcp .

# Run in Docker
make docker-run
# Or: docker run -it --rm docsray-mcp

# Run with Docker Compose
docker-compose up docsray-mcp
```

### Manual Testing

```bash
# Test a specific provider
docsray test --provider pymupdf4llm --document ./tests/files/sample_lease.pdf

# List available providers
docsray list-providers
```

## Architecture

### Provider System

**Multi-provider architecture** with intelligent selection based on document type and operation:

- **Base Provider** (`src/docsray/providers/base.py`): Abstract interface defining `peek()`, `map()`, `xray()`, `extract()`, `seek()` methods
- **Provider Registry** (`src/docsray/providers/registry.py`): Manages provider registration and selection with scoring algorithm
- **Scoring Logic**: Providers scored based on:
  - Format compatibility (+10 points)
  - Operation-specific capabilities (e.g., `xray` prefers providers with semantic search/VLM)
  - Performance for large files
  - OCR capabilities for scanned content

**Available Providers:**
- `pymupdf4llm`: Fast PDF extraction (always enabled)
- `llama-parse`: AI-powered analysis with LlamaParse API
- `ibm-docling`: Advanced layout understanding with VLM
- `mimic-docsray`: Semantic search with RAG and embeddings

### Tool Architecture

**MCP Tools** (`src/docsray/tools/`):
- `peek.py`: Quick document overview and metadata
- `map.py`: Structure mapping and hierarchy extraction
- `xray.py`: AI-powered deep analysis (entities, relationships)
- `extract.py`: Content extraction in multiple formats
- `seek.py`: Navigation and search within documents
- `fetch.py`: Document fetching and URL handling
- `search.py`: Advanced semantic search capabilities

### Configuration System

**Environment-based configuration** (`src/docsray/config.py`):
- Provider configs: Enable/disable providers via `DOCSRAY_<PROVIDER>_ENABLED`
- Transport config: `DOCSRAY_TRANSPORT_TYPE` (stdio/http)
- Performance: Caching, timeouts, concurrent requests
- API keys: `DOCSRAY_LLAMAPARSE_API_KEY` (or `LLAMAPARSE_API_KEY` as fallback), `DOCSRAY_MISTRAL_API_KEY`, etc.

### Server Implementation

**FastMCP Server** (`src/docsray/server.py`):
- Initializes provider registry and caches
- Registers MCP tools and resources
- Provides `docsray://info` resource for capability discovery
- Handles transport layer (stdio for MCP clients, http for development)

## Key Design Patterns

### Provider Selection Flow

1. User preference (if specified) takes precedence
2. Otherwise, registry scores all providers that can handle the document
3. Provider scoring considers:
   - Format support
   - Operation type (xray vs extract vs search)
   - Special capabilities (OCR, semantic search, VLM)
   - Performance characteristics
4. Highest-scored provider is selected

### Caching Strategy

- **LlamaParse Cache**: Results stored in `.docsray/` directories (per-document persistent cache)
- **Document Cache**: In-memory LRU cache for frequently accessed documents
- **Cache Control**: Configurable via `DOCSRAY_CACHE_ENABLED`, `DOCSRAY_CACHE_TTL`

### Error Handling

- Custom exceptions in `src/docsray/exceptions.py` (implied from usage patterns)
- Provider failures trigger fallback to next-best provider
- Comprehensive logging at INFO level (DEBUG available with `--verbose`)

## Development Workflow

### Adding a New Provider

1. Create provider class in `src/docsray/providers/your_provider.py` inheriting from `DocumentProvider`
2. Implement required methods: `get_name()`, `get_supported_formats()`, `get_capabilities()`, `can_process()`, and tool methods
3. Add provider config to `src/docsray/config.py` (e.g., `YourProviderConfig`)
4. Register in `src/docsray/server.py` in `_initialize_providers()` method
5. Add tests in `tests/unit/test_providers.py` and `tests/integration/`
6. Update `.env.example` with provider-specific environment variables

### Adding a New Tool

1. Create tool module in `src/docsray/tools/your_tool.py`
2. Implement async handler function following existing tool patterns
3. Register tool in `src/docsray/server.py` in `_register_tools()` method
4. Add parameter models using Pydantic if needed
5. Add tests in `tests/unit/test_tools.py` and `tests/integration/`
6. Add example prompts to `PROMPTS.md`

### Testing Strategy

- **Unit tests** (`tests/unit/`): Fast, isolated, no API calls, use mocks
- **Integration tests** (`tests/integration/`): Test provider interactions, require API keys, marked with `@pytest.mark.integration`
- **Manual tests** (`tests/manual/`): Debugging scripts and one-off testing
- Target: >90% coverage for new code

## Important Configuration Details

### Environment Variables Priority

1. CLI arguments (highest priority)
2. Environment variables
3. `.env` file
4. Default values in config classes

### Provider Capabilities

Each provider reports capabilities via `get_capabilities()` returning:
- `formats`: Supported document formats
- `features`: Dict of feature flags (ocr, tables, semanticSearch, vlm, etc.)
- `performance`: Speed metrics and characteristics

### MCP Transport Modes

- **stdio** (default): For MCP clients like Cursor, Claude Desktop
- **http**: For development/debugging (access on http://localhost:3000)

## Common Pitfalls

1. **Missing API Keys**: LlamaParse and other AI providers require valid API keys in environment
2. **Provider Not Initialized**: Check provider enabled flag and initialization in server logs
3. **Cache Staleness**: Clear `.docsray/` directories or set `DOCSRAY_LLAMAPARSE_INVALIDATE_CACHE=true`
4. **Async Context**: All tool methods are async; use `await` and proper event loop handling
5. **Test Isolation**: Unit tests must not make real API calls; use mocks and fixtures in `tests/conftest.py`

## Important Files

- `pyproject.toml`: Dependencies, optional extras, tool configuration
- `Makefile`: Convenient commands for all common operations
- `CONTRIBUTING.md`: Detailed development guidelines and PR process
- `PROMPTS.md`: Example prompts demonstrating all capabilities
- `.env.example`: Complete list of configuration options
- `tests/conftest.py`: Pytest fixtures and test configuration

## CLI Entry Points

- `docsray`: Main CLI command (defined in `src/docsray/cli.py`)
- `docsray-mcp`: Alias for `docsray`
- Both installed via `[project.scripts]` in `pyproject.toml`
