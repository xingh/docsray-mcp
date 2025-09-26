#!/usr/bin/env python3
"""Test script for new Phase 7-9 features."""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from docsray.tools.search import handle_search
from docsray.tools.fetch import handle_fetch
from docsray.providers.registry import ProviderRegistry
from docsray.providers.ibm_docling import IBMDoclingProvider
from docsray.providers.mimic_docsray import MimicDocsrayProvider
from docsray.config import DocsrayConfig

def test_search_endpoint():
    """Test the new search endpoint."""
    print("\n=== Testing Search Endpoint ===")

    # Create test directory with sample files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_files = {
            "document1.md": "This is a markdown document about python programming",
            "report.txt": "Annual report containing financial data and python scripts",
            "readme.pdf": "PDF content would go here",
            "data.json": '{"key": "value", "type": "json"}',
        }

        for filename, content in test_files.items():
            filepath = Path(tmpdir) / filename
            filepath.write_text(content)

        # Test search
        try:
            result = handle_search(
                query="python",
                searchPath=str(tmpdir),
                searchStrategy="coarse-to-fine",
                fileTypes=["md", "txt", "pdf", "json"],
                maxResults=5
            )

            print(f"✅ Search found {len(result.get('results', []))} results")
            for r in result.get('results', []):
                print(f"  - {r['filename']} (score: {r['score']:.2f})")

            return True
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False

def test_fetch_endpoint():
    """Test the new fetch endpoint."""
    print("\n=== Testing Fetch Endpoint ===")

    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content for fetch endpoint")
        test_file = f.name

    try:
        # Test filesystem fetch
        result = handle_fetch(
            source=test_file,
            cacheStrategy="bypass-cache",
            returnFormat="raw"
        )

        if result.get('content'):
            print(f"✅ Fetch successful - retrieved {len(result.get('content', ''))} bytes")
            print(f"  - Hash: {result.get('hash', 'N/A')}")
            print(f"  - From cache: {result.get('fromCache', False)}")
            return True
        else:
            print(f"❌ Fetch failed: No content retrieved")
            return False
    except Exception as e:
        print(f"❌ Fetch failed: {e}")
        return False
    finally:
        os.unlink(test_file)

def test_ibm_docling_provider():
    """Test IBM.Docling provider."""
    print("\n=== Testing IBM.Docling Provider ===")

    try:
        provider = IBMDoclingProvider()

        # Test capabilities
        capabilities = provider.get_capabilities()
        print(f"✅ IBM.Docling provider initialized")
        print(f"  - Formats: {len(provider.get_supported_formats())} supported")
        print(f"  - Features: VLM={capabilities.features.get('vlm', False)}, "
              f"ASR={capabilities.features.get('asr', False)}, "
              f"Layout={capabilities.features.get('layoutUnderstanding', False)}")

        # Test provider name
        assert provider.get_name() == "ibm-docling"
        print(f"  - Provider name: {provider.get_name()}")

        return True
    except Exception as e:
        print(f"❌ IBM.Docling provider test failed: {e}")
        return False

def test_mimic_docsray_provider():
    """Test MIMIC.DocsRay provider."""
    print("\n=== Testing MIMIC.DocsRay Provider ===")

    try:
        provider = MimicDocsrayProvider()

        # Test capabilities
        capabilities = provider.get_capabilities()
        print(f"✅ MIMIC.DocsRay provider initialized")
        print(f"  - Formats: {len(provider.get_supported_formats())} supported")
        print(f"  - Features: Semantic={capabilities.features.get('semanticSearch', False)}, "
              f"RAG={capabilities.features.get('ragSupport', False)}, "
              f"Hybrid OCR={capabilities.features.get('hybridOCR', False)}")

        # Test provider name
        assert provider.get_name() == "mimic-docsray"
        print(f"  - Provider name: {provider.get_name()}")

        return True
    except Exception as e:
        print(f"❌ MIMIC.DocsRay provider test failed: {e}")
        return False

def test_provider_registry():
    """Test provider registry with new providers."""
    print("\n=== Testing Provider Registry ===")

    try:
        config = DocsrayConfig()
        registry = ProviderRegistry()

        # Register new providers
        ibm_provider = IBMDoclingProvider()
        mimic_provider = MimicDocsrayProvider()

        registry.register(ibm_provider)
        registry.register(mimic_provider)

        # Test retrieval
        assert registry.get_provider("ibm-docling") == ibm_provider
        assert registry.get_provider("mimic-docsray") == mimic_provider

        print(f"✅ Provider registry working")
        print(f"  - Registered providers: {list(registry.providers.keys())}")

        return True
    except Exception as e:
        print(f"❌ Provider registry test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Formuli.Docsray.MCP Phase 7-9 Features")
    print("=" * 60)

    results = {
        "Search Endpoint": test_search_endpoint(),
        "Fetch Endpoint": test_fetch_endpoint(),
        "IBM.Docling Provider": test_ibm_docling_provider(),
        "MIMIC.DocsRay Provider": test_mimic_docsray_provider(),
        "Provider Registry": test_provider_registry(),
    }

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed.")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())