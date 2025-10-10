"""Configuration for official mcp-use CLI integration tests."""

import os
from pathlib import Path
from typing import Dict

import pytest


@pytest.fixture
def test_documents_dir() -> Path:
    """Directory containing test documents."""
    return Path(__file__).parent.parent / "files"


@pytest.fixture
def sample_pdf_path(test_documents_dir: Path) -> Path:
    """Path to sample PDF for testing."""
    pdf_path = test_documents_dir / "sample.pdf"
    if not pdf_path.exists():
        # Create a minimal test PDF if it doesn't exist
        test_documents_dir.mkdir(exist_ok=True)
        # This would normally be a real PDF file for testing
        pdf_path.write_text("Sample PDF content placeholder")
    return pdf_path


@pytest.fixture
def mcp_server_env() -> Dict[str, str]:
    """Environment variables for the MCP server."""
    env = os.environ.copy()
    env.update({
        "DOCSRAY_LOG_LEVEL": "DEBUG",
        "DOCSRAY_CACHE_ENABLED": "true",
        "DOCSRAY_PYMUPDF_ENABLED": "true",
        "PYTHONPATH": str(Path(__file__).parent.parent.parent / "src"),
    })
    return env