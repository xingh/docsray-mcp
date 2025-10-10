# MCP Integration Tests (official mcp-use CLI)

This directory contains integration tests for the Docsray MCP server that invoke tools via the official `mcp-use` command-line client.

## Requirements

- Node.js 18+ and npm
- Official `mcp-use` CLI installed globally:
  ```bash
  npm i -g mcp-use
  ```
- Python dev deps for this repo:
  ```bash
  pip install -e ".[dev]"
  ```

The tests use a local server process with PYTHONPATH pointed at `src/` so they always exercise the current branch.

## Run the tests

```bash
pytest tests/mcp/ -v
```

If the `mcp-use` binary is not on PATH, these tests will be skipped with a clear message.

## How it works

- Config: `tests/mcp/mcp-use.config.json` launches the server with `python -m docsray.cli start` and environment vars (e.g., `PYTHONPATH=src`).
- Helper: `tests/mcp/mcp_use_helper.py` shells out to the `mcp-use` CLI and returns parsed JSON.
- Tests: `tests/mcp/test_mcp_use_cli.py` covers peek, extract, search, and fetch against temp files/dirs.

## Troubleshooting

- mcp-use missing: Install it globally (`npm i -g mcp-use`) and ensure your shell PATH includes npm globals.
- Timeouts: Increase the per-call `timeout` values inside tests if your machine is slow.
- Provider toggles: Adjust env in `mcp-use.config.json` to enable/disable providers during local runs.

## Adding more cases

Follow the pattern in `test_mcp_use_cli.py`: prepare a small input, call `run_mcp_use(tool=..., args=...)`, assert on a few key fields, and keep timeouts reasonable.