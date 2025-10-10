"""Helper to invoke the official `mcp-use` CLI from pytest.

This module requires the official `mcp-use` CLI to be installed and available
on PATH (invoked as `mcp-use`). No non-standard fallbacks (like `npx`) are used.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict


CONFIG_PATH = Path(__file__).parent / "mcp-use.config.json"
def has_mcp_use_cli() -> bool:
    return shutil.which("mcp-use") is not None


def run_mcp_use(server: str, tool: str, args: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
    """Run the official `mcp-use` CLI for a given tool and return parsed JSON result.

    Requires the `mcp-use` binary to be available on PATH.
    """
    cfg = str(CONFIG_PATH)

    if not has_mcp_use_cli():
        raise RuntimeError("`mcp-use` CLI not found on PATH. Please install the official CLI: npm i -g mcp-use")

    cmd: list[str] = [
        "mcp-use",
        "--config", cfg,
        "--server", server,
        "--tool", tool,
        "--args", json.dumps(args),
    ]

    env = os.environ.copy()
    # Ensure local source importable
    env.setdefault("PYTHONPATH", str(Path(__file__).resolve().parents[2] / "src"))

    def _run(cmd_list: list[str]) -> str:
        p = subprocess.run(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=str(Path(__file__).resolve().parents[2]),
            timeout=timeout,
            text=True,
        )
        if p.returncode != 0:
            raise RuntimeError(p.stderr.strip() or "mcp-use command failed")
        return p.stdout.strip()

    out = _run(cmd)

    # CLI prints JSON on stdout
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        start = out.rfind("{")
        if start != -1:
            try:
                return json.loads(out[start:])
            except Exception:
                pass
        raise
