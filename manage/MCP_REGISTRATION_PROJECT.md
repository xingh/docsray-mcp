# MCP Registration Project Plan

**Status: Ready for Registration** ✅  
**Package Version**: 0.2.0  
**Last Updated**: 2025-08-06

## Quick Reference

- **Package Name**: docsray-mcp
- **Executable**: `docsray` (not docsray-mcp)
- **PyPI**: https://pypi.org/project/docsray-mcp/ ✅
- **TestPyPI**: https://test.pypi.org/project/docsray-mcp/ ✅
- **GitHub**: https://github.com/docsray/docsray-mcp
- **Documentation**: https://docs.docsray.dev

## Installation Command

```bash
# Recommended for MCP clients
uvx --from docsray-mcp docsray

# Alternative methods
pip install docsray-mcp
uv tool install docsray-mcp
```

## Phase 1: Package Publication ✅ COMPLETE

### Status
- [x] Published to PyPI (2025-08-06)
- [x] Published to TestPyPI
- [x] Installation verified with pip, uv, and uvx
- [x] Documentation updated with correct commands
- [x] CHANGELOG updated with release notes

### Known Issue & Solution
**Issue**: Package name is `docsray-mcp` but executable is `docsray`  
**Solution**: All documentation updated to use `uvx --from docsray-mcp docsray`

## Phase 2: MCP Registry Submission 🚀 READY

### Registry Entry

Submit to: https://github.com/anthropics/mcp-servers

```yaml
- name: docsray-mcp
  description: AI-powered document perception and analysis MCP server with intelligent provider selection
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
  features:
    - Multi-provider architecture (PyMuPDF4LLM, LlamaParse)
    - AI-powered entity extraction
    - Comprehensive caching system
    - Universal format support (PDF, URLs, local files)
```

### MCP Client Configurations

#### Claude Desktop
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

#### Cursor
Add to Cursor settings:

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

### Submission Checklist

- [x] Package published and working on PyPI
- [x] README.md with clear installation instructions
- [x] All 5 tools functioning and documented
- [x] Configuration examples tested
- [x] Error handling and logging implemented
- [ ] Fork MCP registry repository
- [ ] Add entry to appropriate category
- [ ] Submit PR with detailed description

## Phase 3: Community Announcement 📣

### Announcement Content

**Title**: Introducing Docsray MCP Server - AI-Powered Document Analysis for Claude

**Key Points**:
1. 5 powerful tools for document analysis
2. Multi-provider architecture with intelligent selection
3. AI-powered deep analysis with LlamaParse
4. Smart caching for optimal performance
5. Universal format support

**Platforms**:
- [ ] GitHub Discussions announcement
- [ ] Twitter/X thread
- [ ] Dev.to article
- [ ] Reddit (r/LocalLLaMA, r/artificial)
- [ ] LinkedIn post
- [ ] Discord/Slack communities

### Social Media Template

```
🚀 Introducing Docsray MCP Server!

Give Claude advanced document perception:
📄 Extract text, tables, entities from any PDF
🔍 5 tools: peek, map, xray, extract, seek
🤖 AI-powered analysis with LlamaParse
⚡ Smart caching & multi-provider support

Install: uvx --from docsray-mcp docsray

GitHub: https://github.com/docsray/docsray-mcp
#MCP #Claude #AI #DocumentProcessing
```

## Phase 4: Documentation & Support 📚

### Current Documentation
- **README.md**: Main documentation ✅
- **PUBLISHING.md**: Publishing guide ✅
- **CONTRIBUTING.md**: Contribution guidelines ✅
- **PROMPTS.md**: Example use cases ✅
- **docs/**: Additional documentation ✅

### Support Channels
- **Issues**: https://github.com/docsray/docsray-mcp/issues
- **Discussions**: https://github.com/docsray/docsray-mcp/discussions
- **Email**: team@docsray.dev

## Implementation Timeline

### Immediate (This Week)
1. [ ] Submit PR to MCP registry
2. [ ] Create GitHub release v0.2.0
3. [ ] Enable GitHub Discussions
4. [ ] Post initial announcement

### Week 2
1. [ ] Write technical blog post
2. [ ] Create video demo
3. [ ] Reach out to communities
4. [ ] Monitor feedback

### Month 1
1. [ ] Gather user feedback
2. [ ] Address initial issues
3. [ ] Plan v0.3.0 features
4. [ ] Expand documentation

## Success Metrics

### Short Term (1 Month)
- [ ] Listed in official MCP registry
- [ ] 100+ GitHub stars
- [ ] 500+ PyPI downloads
- [ ] 5+ user issues/discussions

### Medium Term (3 Months)
- [ ] 500+ GitHub stars
- [ ] 2000+ monthly PyPI downloads
- [ ] 10+ community contributors
- [ ] Integration tutorials created

### Long Term (6 Months)
- [ ] 1000+ GitHub stars
- [ ] 5000+ monthly downloads
- [ ] Multiple provider implementations
- [ ] Active community ecosystem

## Technical Details

### Package Structure
See: [pyproject.toml](../pyproject.toml)

### Provider Capabilities
- **PyMuPDF4LLM**: Fast PDF processing (always enabled)
- **LlamaParse**: AI-powered analysis (requires API key)
- **Future**: PyTesseract, Mistral OCR

### Tool Descriptions
1. **docsray_peek**: Quick document overview
2. **docsray_map**: Document structure mapping
3. **docsray_xray**: AI-powered deep analysis
4. **docsray_extract**: Content extraction
5. **docsray_seek**: Document navigation

## Next Actions

1. **Immediate**: Submit to MCP registry
2. **Today**: Create GitHub release
3. **This Week**: Post announcements
4. **Ongoing**: Monitor and respond to feedback

## Related Files

- [README.md](../README.md) - Main documentation
- [PUBLISHING.md](PUBLISHING.md) - Publishing details
- [CHANGELOG.md](../CHANGELOG.md) - Release history
- [pyproject.toml](../pyproject.toml) - Package configuration

---

**Note**: This is the consolidated project plan. The separate MCP_REGISTRATION.md and MCP_REGISTRATION_PLAN.md files can be archived or removed.