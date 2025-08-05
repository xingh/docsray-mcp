#!/usr/bin/env python3
"""CLI tool for managing LlamaParse cache."""

import argparse
import json
import sys
from pathlib import Path

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.docsray.utils.llamaparse_cache import LlamaParseCache


def list_cached_documents(args):
    """List all cached documents."""
    cache = LlamaParseCache(Path(args.cache_root) if args.cache_root else None)
    cached_docs = cache.list_cached_documents()
    
    if not cached_docs:
        print("No cached documents found.")
        return
    
    print(f"\nCached Documents ({len(cached_docs)} total):")
    print("-" * 80)
    
    total_size = 0
    for doc in cached_docs:
        print(f"\nDocument: {Path(doc['original_document']).name}")
        print(f"  Original path: {doc['original_document']}")
        print(f"  Cached at: {doc['extraction_timestamp']}")
        print(f"  Cache size: {doc['cache_size_mb']} MB")
        print(f"  Location: {doc['cache_dir']}")
        total_size += doc['cache_size_bytes']
    
    print("-" * 80)
    print(f"Total cache size: {round(total_size / (1024 * 1024), 2)} MB")


def info_cached_document(args):
    """Show detailed information about a cached document."""
    cache = LlamaParseCache(Path(args.cache_root) if args.cache_root else None)
    doc_path = Path(args.document)
    
    info = cache.get_cache_info(doc_path)
    
    if not info:
        print(f"No cache found for: {doc_path}")
        return
    
    print(f"\nCache Information for: {doc_path.name}")
    print("=" * 80)
    
    print("\nMetadata:")
    for key, value in info['metadata'].items():
        print(f"  {key}: {value}")
    
    print("\nStatistics:")
    stats = info['statistics']
    print(f"  Pages: {stats['pages']}")
    print(f"  Images: {stats['images']}")
    print(f"  Tables: {stats['tables']}")
    print(f"  Cache size: {stats['cache_size_mb']} MB")
    
    print(f"\nCache directory: {info['cache_directory']}")


def clear_cache(args):
    """Clear cache for specific document or all."""
    cache = LlamaParseCache(Path(args.cache_root) if args.cache_root else None)
    
    if args.document:
        doc_path = Path(args.document)
        count = cache.clear_cache(doc_path)
        if count:
            print(f"Cleared cache for: {doc_path}")
        else:
            print(f"No cache found for: {doc_path}")
    else:
        # Confirm before clearing all
        if not args.force:
            response = input("Clear ALL cached documents? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        
        count = cache.clear_cache()
        print(f"Cleared {count} cached documents.")


def inspect_cache(args):
    """Inspect cache contents for a document."""
    cache = LlamaParseCache(Path(args.cache_root) if args.cache_root else None)
    doc_path = Path(args.document)
    
    cache_dir = cache.get_cache_dir(doc_path)
    
    if not cache_dir.exists():
        print(f"No cache found for: {doc_path}")
        return
    
    print(f"\nCache Contents for: {doc_path.name}")
    print(f"Location: {cache_dir}")
    print("=" * 80)
    
    # Show directory structure
    print("\nDirectory Structure:")
    for item in sorted(cache_dir.rglob("*")):
        if item.is_file():
            indent = "  " * (len(item.relative_to(cache_dir).parts) - 1)
            size = item.stat().st_size
            size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
            print(f"{indent}- {item.name} ({size_str})")
    
    # Show sample content if requested
    if args.show_content:
        print("\n" + "=" * 80)
        
        # Show first page text
        first_page = cache_dir / "pages" / "page_001.txt"
        if first_page.exists():
            print("\nFirst Page Text (first 500 chars):")
            with open(first_page) as f:
                content = f.read()[:500]
                print(content)
                if len(content) == 500:
                    print("...")
        
        # Show tables if any
        tables_index = cache_dir / "tables" / "tables_index.json"
        if tables_index.exists():
            with open(tables_index) as f:
                tables = json.load(f)
                if tables:
                    print(f"\nTables Found: {len(tables)}")
                    for i, table in enumerate(tables[:2]):
                        print(f"  Table {i+1} on page {table.get('page', 'unknown')}")
        
        # Show images if any
        images_index = cache_dir / "images" / "images_index.json"
        if images_index.exists():
            with open(images_index) as f:
                images = json.load(f)
                if images:
                    print(f"\nImages Found: {len(images)}")
                    for i, img in enumerate(images[:3]):
                        print(f"  Image {i+1}: {img.get('type', 'unknown')} on page {img.get('page', 'unknown')}")


def main():
    """Main entry point for cache manager CLI."""
    parser = argparse.ArgumentParser(description="Manage LlamaParse document cache")
    parser.add_argument("--cache-root", help="Cache root directory (default: tests/tmp)")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all cached documents")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show info about cached document")
    info_parser.add_argument("document", help="Path to document")
    
    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear cache")
    clear_parser.add_argument("document", nargs="?", help="Document to clear (omit to clear all)")
    clear_parser.add_argument("-f", "--force", action="store_true", help="Don't ask for confirmation")
    
    # Inspect command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect cache contents")
    inspect_parser.add_argument("document", help="Path to document")
    inspect_parser.add_argument("-c", "--show-content", action="store_true", 
                               help="Show sample content from cache")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == "list":
        list_cached_documents(args)
    elif args.command == "info":
        info_cached_document(args)
    elif args.command == "clear":
        clear_cache(args)
    elif args.command == "inspect":
        inspect_cache(args)


if __name__ == "__main__":
    main()