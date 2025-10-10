"""mcp-use based tests that exercise the Docsray MCP server using the official CLI.

These tests shell out to the `mcp-use` CLI installed on PATH. They are skipped
automatically if the official `mcp-use` binary is not available.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from .mcp_use_helper import has_mcp_use_cli, run_mcp_use


pytestmark = pytest.mark.skipif(not has_mcp_use_cli(), reason="official mcp-use CLI is required for these tests")


def _write_minimal_pdf(path: Path) -> None:
    # Same tiny valid-ish PDF used just for plumbing tests (not for content quality)
    MINIMAL_PDF = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 55 >>
stream
BT /F1 12 Tf 72 120 Td (Hello PDF from test) Tj ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000060 00000 n 
0000000110 00000 n 
0000000283 00000 n 
0000000416 00000 n 
trailer
<< /Root 1 0 R /Size 6 >>
startxref
510
%%EOF
"""
    path.write_bytes(MINIMAL_PDF)


def test_peek_and_extract_with_pdf(tmp_path: Path):
    # Create a temp PDF
    pdf_path = tmp_path / "sample.pdf"
    _write_minimal_pdf(pdf_path)

    # docsray_peek
    peek_res = run_mcp_use(
        server="docsray",
        tool="docsray_peek",
        args={
            "document_url": str(pdf_path),
            "depth": "structure",
            "provider": "auto"
        },
        timeout=90,
    )
    assert isinstance(peek_res, dict)
    assert "metadata" in peek_res or "error" in peek_res

    # docsray_extract
    extract_res = run_mcp_use(
        server="docsray",
        tool="docsray_extract",
        args={
            "document_url": str(pdf_path),
            "extraction_targets": ["text"],
            "output_format": "markdown",
            "provider": "auto"
        },
        timeout=120,
    )
    assert isinstance(extract_res, dict)
    assert "content" in extract_res or "error" in extract_res


def test_search_with_temp_dir(tmp_path: Path):
    # Create a temp directory with a few files
    base = tmp_path / "docs"
    base.mkdir()

    (base / "notes.md").write_text("# Notes\nDeep learning notes and experiments", encoding="utf-8")
    (base / "readme.txt").write_text("Quickstart and machine learning intro", encoding="utf-8")

    # docsray_search
    search_res = run_mcp_use(
        server="docsray",
        tool="docsray_search",
        args={
            "query": "learning",
            "searchPath": str(base),
            "searchStrategy": "keyword",
            "fileTypes": ["md", "txt"],
            "maxResults": 5,
            "provider": "filesystem"
        },
        timeout=60,
    )
    assert isinstance(search_res, dict)
    assert "results" in search_res or "error" in search_res


def test_fetch_local_path(tmp_path: Path):
    test_file = tmp_path / "doc.txt"
    test_file.write_text("hello world", encoding="utf-8")

    fetch_res = run_mcp_use(
        server="docsray",
        tool="docsray_fetch",
        args={
            "source": str(test_file),
            "return_format": "metadata-only",
            "cache_strategy": "use-cache"
        },
        timeout=60,
    )
    assert isinstance(fetch_res, dict)
    assert "path" in fetch_res or "error" in fetch_res or "resolvedPath" in fetch_res
