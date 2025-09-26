# Publishing Guide

**✅ Package Status: Successfully published to both PyPI and TestPyPI**

- **PyPI**: [https://pypi.org/project/docsray-mcp/](https://pypi.org/project/docsray-mcp/)
- **TestPyPI**: [https://test.pypi.org/project/docsray-mcp/](https://test.pypi.org/project/docsray-mcp/)
- **Current Version**: 0.3.4

This document covers how to publish the `docsray-mcp` package to PyPI and TestPyPI, and how to install it using various package managers.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Building the Package](#building-the-package)
- [Publishing to TestPyPI](#publishing-to-testpypi)
- [Publishing to PyPI](#publishing-to-pypi)
- [Installing from PyPI](#installing-from-pypi)
- [Installing from TestPyPI](#installing-from-testpypi)
- [Using with uv](#using-with-uv)
- [Troubleshooting](#troubleshooting)
- [Version Management](#version-management)

## Prerequisites

### Required Tools

Install the necessary publishing tools:

```bash
pip install --upgrade build twine
```

### PyPI Accounts

You'll need accounts on both repositories:

1. **PyPI (Production)**: [https://pypi.org](https://pypi.org)
2. **TestPyPI (Testing)**: [https://test.pypi.org](https://test.pypi.org)

### API Tokens

For each repository, create API tokens:

1. Log into your account
2. Go to Account Settings → API tokens
3. Create a new token with "Entire account" scope
4. Save the tokens securely (they start with `pypi-` or `testpypi-`)

## Building the Package

### Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info/
```

### Build Distribution Files

```bash
python -m build
```

This creates:
- `dist/docsray_mcp-X.Y.Z-py3-none-any.whl` (wheel format)
- `dist/docsray_mcp-X.Y.Z.tar.gz` (source distribution)

### Validate the Build

```bash
twine check dist/*
```

Should show `PASSED` for all files.

## Publishing to TestPyPI

### Method 1: Interactive Upload

```bash
twine upload --repository testpypi dist/*
```

When prompted:
- Username: `__token__`
- Password: Your TestPyPI API token

### Method 2: Environment Variables

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=testpypi-your-token-here
twine upload --repository testpypi dist/*
```

### Method 3: Command Line Arguments

```bash
twine upload --repository testpypi --username __token__ --password testpypi-your-token-here dist/*
```

### Verify TestPyPI Upload

Your package will be available at:
```
https://test.pypi.org/project/docsray-mcp/
```

## Publishing to PyPI

⚠️ **Warning**: Publishing to PyPI is permanent. You cannot delete or re-upload the same version.

### Method 1: Interactive Upload

```bash
twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: Your PyPI API token

### Method 2: Environment Variables

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here
twine upload dist/*
```

### Verify PyPI Upload

Your package will be available at:
```
https://pypi.org/project/docsray-mcp/
```

## Installing from PyPI

### Using pip

```bash
pip install docsray-mcp
```

### Using uv

```bash
uv add docsray-mcp
```

Or for global installation:
```bash
uv tool install docsray-mcp
```

**Note**: Since version 0.2.1, we provide both `docsray-mcp` and `docsray` executables:
```bash
# Run directly without installation (recommended)
uvx docsray-mcp start

# Legacy command (still works)
uvx --from docsray-mcp docsray

# After global installation
docsray-mcp  # or docsray
```

## Installing from TestPyPI

### Using pip

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ docsray-mcp
```

The `--extra-index-url` is needed because TestPyPI doesn't contain all dependencies.

### Using uv

#### Method 1: Direct Installation

```bash
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ docsray-mcp
```

#### Method 2: Add to Project with Custom Index

Create or modify `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
explicit = true

[project]
dependencies = [
    "docsray-mcp",
]

[tool.uv.sources]
docsray-mcp = { index = "testpypi" }
```

Then install:
```bash
uv sync
```

#### Method 3: Using uv with Environment Variables

```bash
export UV_INDEX_URL="https://test.pypi.org/simple/"
export UV_EXTRA_INDEX_URL="https://pypi.org/simple/"
uv add docsray-mcp
```

#### Method 4: Command Line Flags

```bash
uv add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ docsray-mcp
```

## Using with uv

### Creating a New Project

```bash
# Create new project
uv init my-docsray-project
cd my-docsray-project

# Add docsray-mcp as dependency
uv add docsray-mcp

# Install and sync
uv sync
```

### Adding to Existing Project

```bash
# In your existing project directory
uv add docsray-mcp
```

### Development Installation

For development with local changes:

```bash
# Install in editable mode from local source
uv add --editable /path/to/docsray-mcp

# Or from the current directory if you're in the repo
uv add --editable .
```

### Running the CLI

Since version 0.2.1, we provide both `docsray-mcp` and `docsray` executables:

```bash
# Run directly with uvx (recommended)
uvx docsray-mcp start

# Legacy command (still works)
uvx --from docsray-mcp docsray

# If installed globally with uv tool
docsray-mcp  # or docsray

# If installed in project
uv run docsray-mcp  # or docsray

# Or activate the environment first
source .venv/bin/activate  # or `uv shell`
docsray-mcp  # or docsray
```

## Troubleshooting

### Common Issues

#### Network Connectivity Errors

If you see DNS resolution errors:
```
socket.gaierror: [Errno -2] Name or service not known
```

Try:
1. Check your internet connection
2. Use explicit credentials instead of auto-detection
3. Skip TestPyPI and publish directly to PyPI

#### Authentication Errors

If authentication fails:
1. Verify your API token is correct
2. Ensure you're using `__token__` as username
3. Check that the token has the right permissions

#### Build Errors

If `python -m build` fails:
1. Check `pyproject.toml` syntax
2. Ensure all dependencies are available
3. Verify Python version compatibility

#### uv Installation Issues

If uv can't find the package:
1. Verify the package name and version
2. Check that the index URL is correct
3. Ensure both primary and extra index URLs are set

### Version Conflicts

If you get version conflicts:
```bash
# Clear uv cache
uv cache clean

# Force reinstall
uv sync --reinstall
```

## Version Management

### Updating Version

1. Update version in `pyproject.toml`:
```toml
[project]
version = "0.3.0"  # Increment as needed
```

2. Clean and rebuild:
```bash
rm -rf dist/ build/ *.egg-info/
python -m build
```

3. Publish new version:
```bash
twine upload dist/*
```

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- Major: Breaking changes
- Minor: New features, backwards compatible
- Patch: Bug fixes, backwards compatible

### Pre-release Versions

For testing:
- `1.0.0a1` (alpha)
- `1.0.0b1` (beta)
- `1.0.0rc1` (release candidate)

## Best Practices

### Before Publishing

1. ✅ Test locally with `docsray start`
2. ✅ Run `twine check dist/*`
3. ✅ Test on TestPyPI first
4. ✅ Update version number
5. ✅ Update CHANGELOG.md
6. ✅ Commit and tag the release

### Security

- 🔐 Never commit API tokens to version control
- 🔐 Use environment variables or secure credential storage
- 🔐 Regularly rotate API tokens
- 🔐 Use scoped tokens when possible

### Testing

```bash
# Test installation in clean environment
python -m venv test-env
source test-env/bin/activate
pip install docsray-mcp
docsray --help
deactivate
rm -rf test-env
```

## Repository URLs

- **PyPI**: `https://pypi.org/project/docsray-mcp/` ✅ Published
- **TestPyPI**: `https://test.pypi.org/project/docsray-mcp/` ✅ Published
- **Source**: `https://github.com/docsray/docsray-mcp`

## Useful Commands Reference

```bash
# Build
python -m build

# Check
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Install from PyPI
pip install docsray-mcp
uv add docsray-mcp
uvx docsray-mcp start  # Run directly (recommended)
uvx --from docsray-mcp docsray  # Legacy command

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ docsray-mcp
uv add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ docsray-mcp

# Clean build artifacts
rm -rf dist/ build/ *.egg-info/
```