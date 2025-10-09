# MCP Integration Tests

This directory contains integration tests for the Docsray MCP server using `mcp-use`.

## Setup

1. Install development dependencies including mcp-use:
   ```bash
   pip install -e ".[dev]"
   ```

2. Ensure the docsray server is installed and available:
   ```bash
   docsray --version
   ```

## Running Tests

### Automated Tests

Run the MCP integration tests:

```bash
# Run all MCP tests
pytest tests/mcp/ -v

# Run specific test categories
pytest tests/mcp/test_mcp_tools.py -v          # Tool functionality tests
pytest tests/mcp/test_mcp_performance.py -v   # Performance tests
```

### Manual Testing

1. **Run the demo client** to test MCP server interactively:
   ```bash
   python tests/mcp/demo_client.py
   ```

2. **Start test server manually** for debugging:
   ```bash
   python tests/mcp/run_test_server.py
   ```
   Then in another terminal, use mcp-use or other MCP clients to connect.

## Test Structure

- `conftest.py` - Test configuration and fixtures
- `test_mcp_tools.py` - Tests for MCP tool functionality  
- `test_mcp_performance.py` - Performance and load tests
- `demo_client.py` - Interactive demo showing MCP usage
- `run_test_server.py` - Standalone server for manual testing

## Test Documents

The tests use documents from `tests/files/` directory. If test documents don't exist, they will be created automatically with sample content.

## Configuration

Tests use the following MCP server configuration:

- Transport: stdio (default)
- Log level: DEBUG
- Cache: enabled
- PyMuPDF provider: enabled
- Python path: points to local src/ directory

## Troubleshooting

### mcp-use not available

If `mcp-use` is not available, tests will be skipped automatically. Install it with:

```bash
pip install mcp-use
```

### Server startup issues

Check that:
1. `docsray` command is in PATH
2. Python path includes the local `src/` directory
3. Required dependencies are installed

### Test timeouts

Increase timeout values in `conftest.py` if tests are timing out on slower systems.

## Adding New Tests

1. Create test functions in the appropriate test file
2. Use the `mcp_client` fixture for MCP client setup
3. Add `@pytest.mark.skipif(not MCP_USE_AVAILABLE, reason="mcp-use not available")` decorator
4. Test both success and error cases
5. Use appropriate timeouts and error handling