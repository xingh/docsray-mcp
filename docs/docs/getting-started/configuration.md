---
sidebar_position: 3
---

# Configuration

Customize Docsray MCP to fit your specific document processing needs.

## Environment Variables

Configure Docsray using environment variables or a `.env` file in your project root.

### Provider Configuration

```bash
# LlamaParse API Key (required for AI analysis)
# Use either (DOCSRAY_LLAMAPARSE_API_KEY takes precedence):
DOCSRAY_LLAMAPARSE_API_KEY=llx-your-key-here  # Preferred
# LLAMAPARSE_API_KEY=llx-your-key-here  # Alternative (standard LlamaParse env var)

# Provider enablement (PyMuPDF4LLM is always enabled)
DOCSRAY_PYMUPDF4LLM_ENABLED=true  # Default: true
DOCSRAY_LLAMAPARSE_ENABLED=true   # Default: true if API key is present

# LlamaParse specific settings
LLAMAPARSE_MODE=fast              # Options: fast, accurate, premium
LLAMAPARSE_MAX_TIMEOUT=120        # Max processing timeout in seconds
```

> **Note**: Both `DOCSRAY_LLAMAPARSE_API_KEY` and `LLAMAPARSE_API_KEY` are supported for the API key. If both are set, `DOCSRAY_LLAMAPARSE_API_KEY` takes precedence. This provides compatibility with both Docsray-specific configurations and standard LlamaParse setups.

### Performance Tuning

```bash
# Cache Configuration
DOCSRAY_CACHE_ENABLED=true        # Enable caching (default: true)
DOCSRAY_CACHE_TTL=3600            # Cache TTL in seconds (default: 3600)
DOCSRAY_CACHE_DIR=.docsray        # Cache directory (default: .docsray)

# Request Configuration
DOCSRAY_MAX_CONCURRENT_REQUESTS=5  # Max concurrent requests (default: 5)
DOCSRAY_TIMEOUT_SECONDS=30         # Default timeout (default: 30)
DOCSRAY_MAX_FILE_SIZE_MB=100       # Max file size in MB (default: 100)

# Processing Configuration
DOCSRAY_AUTO_PROVIDER_SELECTION=true  # Auto-select provider (default: true)
DOCSRAY_FALLBACK_TO_PYMUPDF=true      # Fallback if LlamaParse fails (default: true)
```

### Logging Configuration

```bash
# Logging
DOCSRAY_LOG_LEVEL=INFO            # Options: DEBUG, INFO, WARNING, ERROR
DOCSRAY_LOG_FORMAT=json           # Options: json, text (default: text)
DOCSRAY_LOG_FILE=docsray.log      # Log file path (optional)
```

## Configuration File

Create a `docsray.yaml` configuration file for more advanced settings:

```yaml
# docsray.yaml
providers:
  pymupdf4llm:
    enabled: true
    extract_images: false
    
  llamaparse:
    enabled: true
    api_key: ${LLAMAPARSE_API_KEY}
    mode: fast
    max_timeout: 120
    custom_instructions: |
      Extract text preserving formatting.
      Include all tables and images.
      
cache:
  enabled: true
  directory: .docsray
  ttl: 3600
  max_size_mb: 1000
  
performance:
  max_concurrent_requests: 5
  timeout_seconds: 30
  max_file_size_mb: 100
  
logging:
  level: INFO
  format: text
  file: docsray.log
```

## MCP Client Configuration

### Claude Desktop

Configure Docsray in Claude Desktop's settings:

#### macOS Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "uvx",
      "args": ["docsray-mcp"],
      "env": {
        "LLAMAPARSE_API_KEY": "llx-your-key-here",
        "DOCSRAY_LOG_LEVEL": "INFO",
        "DOCSRAY_CACHE_ENABLED": "true"
      }
    }
  }
}
```

#### Windows Configuration

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "uvx",
      "args": ["docsray-mcp"],
      "env": {
        "LLAMAPARSE_API_KEY": "llx-your-key-here",
        "DOCSRAY_LOG_LEVEL": "INFO",
        "DOCSRAY_CACHE_ENABLED": "true"
      }
    }
  }
}
```

### Cursor Configuration

Add to your Cursor settings:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "uvx",
      "args": ["docsray-mcp"],
      "env": {
        "LLAMAPARSE_API_KEY": "llx-your-key-here",
        "DOCSRAY_CACHE_DIR": ".docsray",
        "DOCSRAY_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Alternative Installation Methods

#### Using Python Module

```json
{
  "mcpServers": {
    "docsray": {
      "command": "python",
      "args": ["-m", "docsray.server"],
      "env": {
        "LLAMAPARSE_API_KEY": "llx-your-key-here"
      }
    }
  }
}
```

#### Using Virtual Environment

```json
{
  "mcpServers": {
    "docsray": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "docsray.server"],
      "env": {
        "LLAMAPARSE_API_KEY": "llx-your-key-here"
      }
    }
  }
}
```

## Provider-Specific Configuration

### LlamaParse Configuration

```bash
# API Configuration
LLAMAPARSE_API_KEY=llx-your-key-here
LLAMAPARSE_BASE_URL=https://api.cloud.llamaindex.ai  # Default URL

# Processing Configuration
LLAMAPARSE_MODE=fast                  # fast, accurate, premium
LLAMAPARSE_MAX_TIMEOUT=120           # Processing timeout
LLAMAPARSE_LANGUAGE=auto             # Document language (auto-detect)
LLAMAPARSE_PARSING_INSTRUCTION=""    # Custom parsing instructions

# Advanced Configuration  
LLAMAPARSE_INVALIDATE_CACHE=false    # Force cache invalidation
LLAMAPARSE_DO_NOT_CACHE=false        # Disable caching for this provider
LLAMAPARSE_CHECK_INTERVAL=1          # Status check interval in seconds
```

### PyMuPDF4LLM Configuration

```bash
# Processing Configuration
PYMUPDF4LLM_EXTRACT_IMAGES=false     # Extract embedded images
PYMUPDF4LLM_EXTRACT_TABLES=true      # Extract table content
PYMUPDF4LLM_PAGE_SEPARATORS=true     # Include page separators
PYMUPDF4LLM_WRITE_IMAGES=false       # Save images to disk
```

## Advanced Configuration Options

### Custom Cache Implementation

```python
# Custom cache configuration
DOCSRAY_CACHE_BACKEND=redis           # Options: filesystem, redis, memory
DOCSRAY_REDIS_URL=redis://localhost:6379/0
DOCSRAY_CACHE_KEY_PREFIX=docsray:
```

### Authentication Configuration

```bash
# API Authentication
DOCSRAY_API_KEY_HEADER=X-API-Key      # Custom API key header
DOCSRAY_BEARER_TOKEN=""               # Bearer token for authentication
DOCSRAY_BASIC_AUTH=""                 # Basic auth credentials
```

### Network Configuration

```bash
# HTTP Configuration
DOCSRAY_USER_AGENT="DocsRay-MCP/0.2.0"
DOCSRAY_HTTP_TIMEOUT=30
DOCSRAY_MAX_REDIRECTS=5
DOCSRAY_VERIFY_SSL=true

# Proxy Configuration
HTTP_PROXY=http://proxy:8080
HTTPS_PROXY=https://proxy:8080
NO_PROXY=localhost,127.0.0.1
```

## Validation and Testing

### Validate Configuration

Test your configuration with a simple document:

```bash
# Test with Claude/MCP client
You: Peek at https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf

# Should return document metadata and structure
```

### Debug Configuration Issues

Enable debug logging to troubleshoot:

```bash
export DOCSRAY_LOG_LEVEL=DEBUG
```

Check the logs for configuration validation messages and any errors.

### Provider Capability Testing

```python
# Test provider availability
result = docsray.peek("test.pdf", depth="metadata")
providers = result.get("available_providers", [])
print(f"Available providers: {providers}")
```

## Configuration Best Practices

1. **Use Environment Variables** - Keep sensitive API keys in environment variables
2. **Enable Caching** - Always use caching for better performance
3. **Set Appropriate Timeouts** - Balance processing time vs user experience
4. **Monitor Resource Usage** - Configure limits based on your system capacity
5. **Use Debug Logging** - Enable when troubleshooting issues
6. **Validate API Keys** - Test provider connectivity during setup

## Troubleshooting Configuration

### Common Issues

1. **LlamaParse Not Working**
   - Verify API key is correct
   - Check API key has sufficient credits
   - Ensure network connectivity to LlamaIndex Cloud

2. **Cache Issues**
   - Check cache directory permissions
   - Verify available disk space
   - Clear cache if corrupted: `rm -rf .docsray/`

3. **Performance Issues**
   - Reduce `DOCSRAY_MAX_CONCURRENT_REQUESTS`
   - Increase `DOCSRAY_TIMEOUT_SECONDS`
   - Enable caching if disabled

4. **MCP Connection Issues**
   - Verify command path in MCP configuration
   - Check environment variables are set correctly
   - Test with simple document first

### Getting Help

- Check the [Troubleshooting Guide](../advanced/troubleshooting)
- Review logs with `DOCSRAY_LOG_LEVEL=DEBUG`
- Test with minimal configuration first
- Verify all dependencies are installed correctly

## Next Steps

- Learn about [Provider Comparison](../providers/comparison)
- Explore [Performance Optimization](../advanced/performance)
- See [API Reference](../api/configuration) for all options