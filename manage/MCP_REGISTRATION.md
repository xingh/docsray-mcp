# MCP Registration Plan

**Status: Ready for Registration** ✅

## Package Information

- **Package Name**: docsray-mcp
- **PyPI URL**: https://pypi.org/project/docsray-mcp/
- **GitHub Repository**: https://github.com/docsray/docsray-mcp
- **Current Version**: 0.2.0
- **Executable Name**: `docsray` (not `docsray-mcp`)

## Installation Methods

### 1. Using uvx (Recommended)
```bash
uvx --from docsray-mcp docsray
```

### 2. Global Installation with uv
```bash
uv tool install docsray-mcp
docsray
```

### 3. Using pip
```bash
pip install docsray-mcp
docsray
```

## MCP Configuration Examples

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "docsray": {
      "command": "uvx",
      "args": ["--from", "docsray-mcp", "docsray"],
      "env": {
        "LLAMAPARSE_API_KEY": "llx-your-key-here"
      }
    }
  }
}
```

### Cursor Configuration
```json
{
  "mcpServers": {
    "docsray": {
      "command": "uvx",
      "args": ["--from", "docsray-mcp", "docsray"],
      "env": {
        "LLAMAPARSE_API_KEY": "llx-your-key-here"
      }
    }
  }
}
```

## MCP Registry Submission

### Package Details for Registry

**Name**: Docsray MCP Server

**Description**: AI-powered document perception and analysis MCP server with intelligent provider selection. Extract text, navigate pages, analyze structure, and understand any document with ease.

**Category**: Document Processing / AI Analysis

**Key Features**:
- 🔍 5 powerful tools for document analysis
- 🤖 AI-powered deep analysis with LlamaParse
- 📄 Universal format support (PDF, URLs, local files)
- ⚡ Smart caching for instant results
- 🔌 Multi-provider architecture

**Tools Provided**:
1. `docsray_peek` - Quick document overview
2. `docsray_map` - Document structure mapping
3. `docsray_xray` - AI-powered deep analysis
4. `docsray_extract` - Content extraction
5. `docsray_seek` - Document navigation

**Installation Command**:
```bash
uvx --from docsray-mcp docsray
```

**Configuration Example**:
```json
{
  "command": "uvx",
  "args": ["--from", "docsray-mcp", "docsray"],
  "env": {
    "LLAMAPARSE_API_KEY": "optional-api-key"
  }
}
```

**Requirements**:
- Python 3.9+
- Optional: LlamaParse API key for AI features

**Links**:
- PyPI: https://pypi.org/project/docsray-mcp/
- GitHub: https://github.com/docsray/docsray-mcp
- Documentation: https://docs.docsray.dev

## Submission Steps

1. **Verify Package Works** ✅
   - Package is published to PyPI
   - Installation via uvx confirmed working
   - MCP server starts successfully

2. **Prepare Registry PR**
   - Fork the MCP registry repository
   - Add entry to the appropriate category (Document Processing)
   - Include all configuration examples
   - Submit PR with detailed description

3. **Registry Entry Format**
```yaml
- name: docsray-mcp
  description: AI-powered document perception and analysis MCP server
  author: Docsray Team
  homepage: https://github.com/docsray/docsray-mcp
  pypi: docsray-mcp
  command: uvx --from docsray-mcp docsray
  categories:
    - document-processing
    - ai-analysis
  tools:
    - docsray_peek
    - docsray_map
    - docsray_xray
    - docsray_extract
    - docsray_seek
```

## Testing Checklist

- [x] Package published to PyPI
- [x] Package published to TestPyPI
- [x] Installation via pip works
- [x] Installation via uv works
- [x] Direct execution via uvx works
- [x] Claude Desktop configuration tested
- [x] Cursor configuration tested
- [x] All 5 tools functioning
- [x] Documentation updated
- [x] README includes correct installation instructions

## Known Issues & Solutions

### Issue: Command Name
The package is `docsray-mcp` but the executable is `docsray`. Users need to use:
```bash
uvx --from docsray-mcp docsray
```
Not:
```bash
uvx docsray-mcp  # This won't work
```

### Solution Documentation
All documentation has been updated to reflect the correct command usage.

## Next Steps

1. Submit to MCP Registry
2. Create announcement for community
3. Monitor for user feedback
4. Plan v0.3.0 features based on usage

## Support Information

- **Issues**: https://github.com/docsray/docsray-mcp/issues
- **Discussions**: https://github.com/docsray/docsray-mcp/discussions
- **Documentation**: https://docs.docsray.dev
- **Email**: team@docsray.dev