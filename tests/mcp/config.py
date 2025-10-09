"""Configuration for MCP-Use local testing."""

import os
from pathlib import Path

# MCP Server configuration for local testing
MCP_SERVER_CONFIG = {
    "docsray": {
        "command": "python",
        "args": ["-m", "docsray.cli", "start"],
        "env": {
            "DOCSRAY_PYMUPDF_ENABLED": "true",
            "DOCSRAY_LOG_LEVEL": "DEBUG",
            "DOCSRAY_CACHE_ENABLED": "true",
            # Add any API keys from environment
            "LLAMAPARSE_API_KEY": os.getenv("LLAMAPARSE_API_KEY", ""),
            "DOCSRAY_LLAMAPARSE_API_KEY": os.getenv("DOCSRAY_LLAMAPARSE_API_KEY", ""),
            "DOCSRAY_IBM_DOCLING_ENABLED": os.getenv("DOCSRAY_IBM_DOCLING_ENABLED", "false"),
            "DOCSRAY_MIMIC_ENABLED": os.getenv("DOCSRAY_MIMIC_ENABLED", "false"),
        },
        "working_directory": str(Path(__file__).parent.parent.parent)
    }
}

# Test configuration
TEST_CONFIG = {
    "timeout": 30,  # seconds
    "retry_attempts": 3,
    "sample_documents": {
        "text": "sample.txt",
        "pdf": "sample.pdf",
        "markdown": "sample.md"
    }
}

# Expected server capabilities
EXPECTED_CAPABILITIES = {
    "tools": [
        "docsray_peek",
        "docsray_map", 
        "docsray_xray",
        "docsray_extract",
        "docsray_seek",
        "docsray_fetch",
        "docsray_search"
    ],
    "providers": [
        "pymupdf4llm"  # Always available
    ],
    "formats": [
        "pdf", "txt", "md", "docx", "html"
    ],
    "features": [
        "caching", "url_support", "local_files", 
        "semantic_search", "entity_extraction"
    ]
}