---
sidebar_position: 3
---

# Troubleshooting

Resolve common issues and optimize Docsray MCP performance with comprehensive troubleshooting guides.

## Common Issues

### LlamaParse API Issues

#### Problem: "API key not configured" or "Invalid API key"

**Solution:**
```bash
# Check if API key is set
echo $LLAMAPARSE_API_KEY

# Set API key (get from https://cloud.llamaindex.ai)
export LLAMAPARSE_API_KEY="llx-your-key-here"

# Or add to .env file
echo "LLAMAPARSE_API_KEY=llx-your-key-here" >> .env

# Verify key format (should start with 'llx-')
if [[ $LLAMAPARSE_API_KEY == llx-* ]]; then
    echo "API key format is correct"
else
    echo "API key should start with 'llx-'"
fi
```

#### Problem: "Insufficient credits" or "Rate limit exceeded"

**Solutions:**
1. **Check your usage**: Visit [LlamaIndex Cloud Dashboard](https://cloud.llamaindex.ai)
2. **Use caching**: Enable caching to avoid repeated API calls
3. **Fallback to PyMuPDF4LLM**: Use free provider when possible

```python
# Robust extraction with fallback
def extract_with_fallback(doc_path):
    try:
        return docsray.xray(doc_path, provider="llama-parse")
    except Exception as e:
        if "credit" in str(e).lower() or "rate limit" in str(e).lower():
            print("LlamaParse limit reached, using PyMuPDF4LLM")
            return docsray.extract(doc_path, provider="pymupdf4llm")
        raise e
```

### Document Processing Issues

#### Problem: "No content extracted" or empty results

**Diagnostic Steps:**
```python
def diagnose_extraction_issue(doc_path):
    """Diagnose why document extraction is failing."""
    
    import os
    from pathlib import Path
    
    issues = []
    
    # Check if file exists
    if not os.path.exists(doc_path):
        issues.append(f"File not found: {doc_path}")
        return issues
    
    # Check file size
    file_size = os.path.getsize(doc_path)
    if file_size == 0:
        issues.append("File is empty (0 bytes)")
    elif file_size > 100 * 1024 * 1024:  # 100MB
        issues.append(f"File is very large ({file_size / (1024*1024):.1f}MB)")
    
    # Check file extension
    if not doc_path.lower().endswith(('.pdf', '.docx', '.pptx', '.html')):
        issues.append(f"Unsupported file format: {Path(doc_path).suffix}")
    
    # Try basic peek
    try:
        peek_result = docsray.peek(doc_path, depth="metadata")
        if "error" in peek_result:
            issues.append(f"Peek failed: {peek_result['error']}")
        else:
            metadata = peek_result['metadata']
            if metadata['page_count'] == 0:
                issues.append("Document has 0 pages")
            if metadata.get('is_encrypted', False):
                issues.append("Document is password protected")
    except Exception as e:
        issues.append(f"Cannot read document: {str(e)}")
    
    return issues

# Usage
issues = diagnose_extraction_issue("problematic.pdf")
for issue in issues:
    print(f"❌ {issue}")
```

**Common Solutions:**
- **Password-protected PDFs**: Remove password or use different document
- **Scanned PDFs**: Use LlamaParse for OCR capabilities
- **Corrupted files**: Re-download or get a fresh copy
- **Large files**: Process specific pages instead of entire document

#### Problem: Processing timeouts

**Solutions:**
```bash
# Increase timeout settings
export LLAMAPARSE_MAX_TIMEOUT=180  # 3 minutes
export DOCSRAY_TIMEOUT_SECONDS=60   # General timeout

# Process in smaller chunks
export DOCSRAY_MAX_FILE_SIZE_MB=50  # Limit file size
```

```python
# Process large documents in chunks
def process_large_document(doc_path, chunk_size=20):
    overview = docsray.peek(doc_path, depth="metadata")
    total_pages = overview['metadata']['page_count']
    
    if total_pages <= chunk_size:
        return docsray.extract(doc_path)
    
    # Process in chunks
    results = []
    for start in range(1, total_pages + 1, chunk_size):
        end = min(start + chunk_size - 1, total_pages)
        pages = list(range(start, end + 1))
        
        chunk_result = docsray.extract(doc_path, pages=pages)
        results.append(chunk_result['extraction']['text'])
    
    # Combine results
    return {"extraction": {"text": "\n\n".join(results)}}
```

### Cache Issues

#### Problem: Cache not working or "Permission denied" errors

**Diagnostic Steps:**
```python
def diagnose_cache_issues():
    import os
    from pathlib import Path
    
    cache_dir = Path(os.getenv('DOCSRAY_CACHE_DIR', '.docsray'))
    
    print(f"Cache directory: {cache_dir}")
    print(f"Cache enabled: {os.getenv('DOCSRAY_CACHE_ENABLED', 'true')}")
    
    if cache_dir.exists():
        print(f"Directory exists: ✓")
        
        # Check permissions
        if os.access(cache_dir, os.R_OK):
            print(f"Read permission: ✓")
        else:
            print(f"Read permission: ❌")
        
        if os.access(cache_dir, os.W_OK):
            print(f"Write permission: ✓")
        else:
            print(f"Write permission: ❌")
        
        # Check disk space
        import shutil
        total, used, free = shutil.disk_usage(cache_dir)
        free_gb = free / (1024**3)
        print(f"Free disk space: {free_gb:.1f}GB")
        
    else:
        print(f"Directory exists: ❌")
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created cache directory: ✓")
        except PermissionError:
            print(f"Cannot create cache directory: ❌")

diagnose_cache_issues()
```

**Solutions:**
```bash
# Fix permissions
chmod 755 .docsray
chown -R $USER:$USER .docsray

# Use different cache location
export DOCSRAY_CACHE_DIR="$HOME/.docsray"

# Clear corrupted cache
rm -rf .docsray

# Disable cache temporarily
export DOCSRAY_CACHE_ENABLED=false
```

### Performance Issues

#### Problem: Slow processing times

**Diagnostic Steps:**
```python
def benchmark_performance(doc_path):
    import time
    
    print("Performance Benchmark:")
    
    # Test peek operation
    start = time.time()
    peek_result = docsray.peek(doc_path, depth="metadata")
    peek_time = time.time() - start
    print(f"Peek: {peek_time:.2f}s")
    
    # Test PyMuPDF4LLM extraction
    start = time.time()
    pymupdf_result = docsray.extract(doc_path, provider="pymupdf4llm")
    pymupdf_time = time.time() - start
    print(f"PyMuPDF4LLM extract: {pymupdf_time:.2f}s")
    
    # Test LlamaParse (if available)
    try:
        start = time.time()
        llama_result = docsray.extract(doc_path, provider="llama-parse")
        llama_time = time.time() - start
        print(f"LlamaParse extract: {llama_time:.2f}s")
        print(f"LlamaParse speedup: {llama_time/pymupdf_time:.1f}x slower")
    except Exception as e:
        print(f"LlamaParse not available: {e}")

benchmark_performance("test.pdf")
```

**Solutions:**
- **Use PyMuPDF4LLM**: For speed-critical operations
- **Enable caching**: Avoid repeated processing
- **Process specific pages**: Instead of entire large documents
- **Parallel processing**: For multiple documents

## MCP Client Integration Issues

### Claude Desktop Issues

#### Problem: Docsray not showing up in Claude Desktop

**Diagnostic Steps:**
1. Check configuration file location:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Verify configuration syntax:
```json
{
  "mcpServers": {
    "docsray": {
      "command": "uvx",
      "args": ["docsray-mcp"],
      "env": {
        "LLAMAPARSE_API_KEY": "llx-your-key-here"
      }
    }
  }
}
```

3. Test command manually:
```bash
# Test if uvx can run docsray-mcp
uvx docsray-mcp --help

# Or test with python
python -m docsray.server
```

**Common Solutions:**
- **Install docsray-mcp**: `uvx docsray-mcp` or `pip install docsray-mcp`
- **Fix JSON syntax**: Use a JSON validator
- **Restart Claude Desktop**: After configuration changes
- **Check logs**: Look for error messages in Claude Desktop

### Cursor Integration Issues

#### Problem: MCP server not connecting in Cursor

**Solution:**
```json
// In Cursor settings
{
  "mcpServers": {
    "docsray": {
      "command": "python",
      "args": ["-m", "docsray.server"],
      "env": {
        "LLAMAPARSE_API_KEY": "llx-your-key-here",
        "DOCSRAY_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Error Message Reference

### LlamaParse Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `API key not found` | Missing LLAMAPARSE_API_KEY | Set API key environment variable |
| `Invalid API key` | Wrong key format | Ensure key starts with 'llx-' |
| `Insufficient credits` | No API credits | Add credits or use PyMuPDF4LLM |
| `Rate limit exceeded` | Too many requests | Wait or use caching |
| `Document too large` | File size limit | Process in chunks |
| `Processing timeout` | Document complexity | Increase timeout or chunk processing |

### File Processing Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `File not found` | Invalid path | Check file path and existence |
| `Permission denied` | File permissions | Fix file/directory permissions |
| `Unsupported format` | Wrong file type | Use PDF, DOCX, PPTX, or HTML |
| `Document encrypted` | Password protected | Remove password or use different file |
| `No content extracted` | Empty/corrupted file | Verify file integrity |
| `Memory error` | Large file | Process in smaller chunks |

### Cache Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `Cache write failed` | Permission/disk space | Fix permissions or free space |
| `Cache corrupted` | Interrupted write | Clear cache directory |
| `Cache key error` | Hash collision | Clear specific document cache |

## Debugging Tools

### Enable Debug Logging

```bash
# Enable detailed logging
export DOCSRAY_LOG_LEVEL=DEBUG
export DOCSRAY_LOG_FORMAT=json

# Log to file
export DOCSRAY_LOG_FILE=docsray.log
```

### Test Document Processing

```python
def test_document_processing(doc_path):
    """Comprehensive test of document processing."""
    
    print(f"Testing document: {doc_path}")
    
    tests = [
        ("File existence", lambda: os.path.exists(doc_path)),
        ("Basic peek", lambda: docsray.peek(doc_path, depth="metadata")),
        ("PyMuPDF extraction", lambda: docsray.extract(doc_path, provider="pymupdf4llm")),
        ("Structure analysis", lambda: docsray.map(doc_path, analysis_depth="basic")),
    ]
    
    # Add LlamaParse test if API key available
    if os.getenv('LLAMAPARSE_API_KEY'):
        tests.append(("LlamaParse extraction", lambda: docsray.extract(doc_path, provider="llama-parse")))
    
    results = []
    
    for test_name, test_func in tests:
        try:
            start_time = time.time()
            result = test_func()
            elapsed = time.time() - start_time
            
            if isinstance(result, dict) and "error" in result:
                results.append((test_name, "FAILED", result["error"], elapsed))
            else:
                results.append((test_name, "PASSED", None, elapsed))
        except Exception as e:
            elapsed = time.time() - start_time
            results.append((test_name, "ERROR", str(e), elapsed))
    
    # Print results
    print("\nTest Results:")
    for test_name, status, error, elapsed in results:
        status_symbol = "✓" if status == "PASSED" else "❌"
        print(f"  {status_symbol} {test_name}: {status} ({elapsed:.2f}s)")
        if error:
            print(f"    Error: {error}")
    
    return results

# Usage
test_results = test_document_processing("test-document.pdf")
```

### System Information

```python
def get_system_info():
    """Get comprehensive system information for debugging."""
    
    import sys
    import platform
    import psutil
    
    info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": f"{psutil.virtual_memory().total / (1024**3):.1f}GB",
        "disk_free": f"{psutil.disk_usage('.').free / (1024**3):.1f}GB",
        "environment_vars": {
            k: v for k, v in os.environ.items() 
            if k.startswith('DOCSRAY_') or k.startswith('LLAMAPARSE_')
        }
    }
    
    return info

# Print system information
sys_info = get_system_info()
print("System Information:")
for key, value in sys_info.items():
    if key == "environment_vars":
        print(f"  {key}:")
        for env_key, env_value in value.items():
            # Mask API keys
            if "api_key" in env_key.lower():
                env_value = f"{env_value[:8]}...{env_value[-4:]}" if len(env_value) > 12 else "***"
            print(f"    {env_key}={env_value}")
    else:
        print(f"  {key}: {value}")
```

## Getting Help

### Community Resources

1. **GitHub Issues**: [github.com/docsray/docsray-mcp/issues](https://github.com/docsray/docsray-mcp/issues)
2. **Discussions**: [github.com/docsray/docsray-mcp/discussions](https://github.com/docsray/docsray-mcp/discussions)
3. **Documentation**: [docs.docsray.dev](https://docs.docsray.dev)

### Reporting Bugs

When reporting issues, include:

1. **System information** (use `get_system_info()` above)
2. **Error messages** with full stack trace
3. **Steps to reproduce** the issue
4. **Sample document** (if possible)
5. **Expected vs actual behavior**
6. **Configuration** (with sensitive info masked)

### Performance Issues

For performance problems, include:

1. **Benchmark results** (use `benchmark_performance()` above)
2. **Document characteristics** (size, pages, complexity)
3. **Resource usage** during processing
4. **Cache statistics**
5. **Network conditions** (if using LlamaParse)

## Prevention Best Practices

1. **Test with small documents first**
2. **Use appropriate providers for your use case**
3. **Monitor resource usage and cache health**
4. **Keep API keys secure and up to date**
5. **Regularly update to latest version**
6. **Use error handling in production code**
7. **Have fallback strategies for critical operations**

## Next Steps

- Review [Performance Optimization](./performance) for speed improvements
- Check [Caching Guide](./caching) for cache-related issues
- See [Configuration Documentation](../getting-started/configuration) for setup options