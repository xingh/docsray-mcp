# Contributing to Docsray MCP

Thank you for your interest in contributing to Docsray MCP! This document provides guidelines and information for contributors.

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Git
- A virtual environment manager (venv, conda, or similar)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/docsray-mcp.git
   cd docsray-mcp
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set Up Environment Variables**
   ```bash
   cp .env.example .env  # If .env.example exists
   # Add your API keys for testing (use either env var):
   echo "DOCSRAY_LLAMAPARSE_API_KEY=llx-your-key-here" >> .env
   # Or: echo "LLAMAPARSE_API_KEY=llx-your-key-here" >> .env
   ```

5. **Verify Installation**
   ```bash
   python -m docsray --help
   pytest tests/unit/ -v
   ```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/              # Fast isolated tests (no API calls)
├── integration/       # Component interaction tests
├── manual/           # Manual testing scripts and debugging
└── files/            # Test documents (PDFs, etc.)
```

### Running Tests

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

### Test Requirements

- **Unit tests**: Must run without external dependencies or API calls
- **Integration tests**: Can use API keys but should be marked with appropriate decorators
- **All tests**: Should be deterministic and not depend on external state
- **Coverage**: Aim for >90% coverage on new code

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch
from docsray.providers.base import DocumentProvider

def test_provider_initialization():
    """Test provider initialization with proper setup."""
    provider = DocumentProvider()
    assert provider.get_name() == "base"
    assert len(provider.get_supported_formats()) >= 0

@pytest.mark.integration
async def test_llamaparse_integration():
    """Integration test requiring API key."""
    # Test implementation
    pass
```

## 🎨 Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Imports**: Use isort for import organization
- **Type hints**: Required for all public functions and methods
- **Docstrings**: Required for all public functions, classes, and modules

### Tools and Configuration

```bash
# Format code
black src/ tests/

# Check and fix imports
ruff check src/ tests/ --fix

# Type checking
mypy src/

# Run all linting
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

### Pre-commit Hooks (Recommended)

```bash
pip install pre-commit
pre-commit install
```

## 📝 Documentation

### Docstring Format

Use Google-style docstrings:

```python
async def extract_content(
    document_url: str,
    extraction_targets: List[str],
    provider: str = "auto"
) -> ExtractResult:
    """Extract content from document.
    
    Args:
        document_url: URL or path to document
        extraction_targets: List of targets to extract (text, tables, images)
        provider: Provider name or "auto" for automatic selection
        
    Returns:
        ExtractResult containing extracted content and metadata
        
    Raises:
        DocumentNotFoundError: If document cannot be accessed
        ProviderError: If extraction fails
    """
```

### API Documentation

- Update docstrings when changing function signatures
- Add examples to docstrings for complex functions
- Update README.md if adding new features
- Update SYSTEM_INSTRUCTIONS.md for new capabilities

## 🏗️ Architecture Guidelines

### Provider Development

When adding new providers:

1. **Inherit from DocumentProvider**
   ```python
   from docsray.providers.base import DocumentProvider
   
   class NewProvider(DocumentProvider):
       def get_name(self) -> str:
           return "new-provider"
   ```

2. **Implement required methods**
   - `get_supported_formats()`
   - `get_capabilities()`
   - `peek()`, `map()`, `xray()`, `extract()`, `seek()`

3. **Add to registry**
   ```python
   # In providers/__init__.py
   from .new_provider import NewProvider
   ```

4. **Add configuration**
   ```python
   # In config.py
   class NewProviderConfig:
       api_key: Optional[str] = None
   ```

### Tool Development

When adding new tools:

1. **Create tool module**: `src/docsray/tools/new_tool.py`
2. **Implement async function**: `async def handle_new_tool(...)`
3. **Register in server**: Add to `src/docsray/server.py`
4. **Add tests**: Both unit and integration tests
5. **Update documentation**: Add examples to PROMPTS.md

### Error Handling

```python
from docsray.exceptions import DocsrayError, DocumentNotFoundError

async def your_function():
    try:
        # Your code
        pass
    except FileNotFoundError as e:
        raise DocumentNotFoundError(f"Document not found: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise DocsrayError(f"Operation failed: {e}")
```

## 🐛 Issue Reporting

### Bug Reports

Please include:

1. **Environment details**:
   - Python version
   - OS and version
   - Docsray version
   - MCP client (Cursor, Claude Desktop, etc.)

2. **Reproduction steps**:
   - Exact commands or prompts used
   - Input documents (if shareable)
   - Expected vs actual behavior

3. **Logs and errors**:
   - Complete error messages
   - Relevant log output
   - Stack traces

### Feature Requests

Please include:

1. **Use case**: Describe the problem you're trying to solve
2. **Proposed solution**: How you envision the feature working
3. **Alternatives**: Other approaches you've considered
4. **Impact**: Who would benefit from this feature

## 🔄 Pull Request Process

### Before Creating a PR

1. **Create an issue** (for non-trivial changes)
2. **Fork the repository**
3. **Create a feature branch**: `git checkout -b feature/your-feature`
4. **Write tests** for new functionality
5. **Update documentation** as needed
6. **Run the full test suite**
7. **Check code style** with linting tools

### PR Requirements

- [ ] Tests pass (`pytest`)
- [ ] Code style checks pass (`black`, `ruff`, `mypy`)
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (for significant changes)
- [ ] Commit messages are clear and descriptive

### PR Description Template

```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Documentation
- [ ] README updated
- [ ] API documentation updated
- [ ] Examples added/updated

## Notes
Any additional context or considerations
```

### Review Process

1. **Automated checks**: All CI checks must pass
2. **Code review**: At least one maintainer review required
3. **Testing**: Verify functionality in multiple environments
4. **Documentation**: Ensure documentation is clear and complete

## 📦 Release Process

### Version Management

We use semantic versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release branch
4. Run full test suite
5. Create GitHub release with notes
6. Deploy to PyPI (maintainers only)

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Acknowledge contributions

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code reviews and technical discussion

### Recognition

Contributors are recognized in:
- `CHANGELOG.md` for significant contributions
- GitHub contributors list
- Release notes for major features

## 🆘 Getting Help

### Development Questions

1. **Check existing issues** and documentation
2. **Search discussions** for similar questions
3. **Create a discussion** for general questions
4. **Create an issue** for bugs or specific problems

### Setup Issues

Common solutions:

```bash
# Clean reinstall
pip uninstall docsray-mcp
pip install -e ".[dev]"

# Reset environment
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Clear caches
rm -rf .pytest_cache/ __pycache__/
find . -name "*.pyc" -delete
```

## 📋 Checklist for New Contributors

- [ ] Read this contributing guide
- [ ] Set up development environment
- [ ] Run tests successfully
- [ ] Make a small test change and verify it works
- [ ] Look at existing issues for "good first issue" labels
- [ ] Join GitHub discussions for community updates

---

Thank you for contributing to Docsray MCP! Your efforts help make document processing more accessible and powerful for everyone.