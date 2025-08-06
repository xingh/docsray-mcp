---
sidebar_position: 1
---

# Caching System

Understand and optimize Docsray's intelligent caching system for maximum performance and cost efficiency.

## Overview

Docsray uses a sophisticated multi-layer caching system:
- **In-memory caching** for recent operations
- **Persistent file caching** in `.docsray` directories
- **Provider-specific caching** with intelligent invalidation
- **Content-aware hashing** for cache key generation
- **Automatic cache management** with configurable settings

## How Caching Works

### Cache Key Generation

```python
# Docsray automatically generates cache keys based on:
# 1. Document content hash (not filename)
# 2. Operation type (peek, map, xray, extract, seek)
# 3. Operation parameters (provider, instructions, etc.)

# Example cache key generation:
# document_hash: sha256 of document content
# operation: "xray"
# parameters: {"provider": "llama-parse", "custom_instructions": "..."}
# final_key: "xray_a1b2c3d4_provider-llama-parse_instructions-hash"
```

### Cache Structure

```
.docsray/
├── document_hash.abcd1234.docsray/          # Document-specific cache
│   ├── metadata.json                       # Document metadata
│   ├── peek_results/                       # Cached peek operations
│   │   ├── metadata_depth.json
│   │   ├── structure_depth.json
│   │   └── preview_depth.json
│   ├── extraction_results/                 # Cached extractions
│   │   ├── provider_pymupdf4llm.json
│   │   └── provider_llama-parse.json
│   ├── xray_results/                       # Cached xray analyses
│   │   ├── entities_basic.json
│   │   └── entities_custom_instructions.json
│   ├── map_results/                        # Cached structure maps
│   │   └── analysis_depth_deep.json
│   └── original.pdf                        # Copy of original document
```

## Cache Configuration

### Environment Variables

```bash
# Core cache settings
DOCSRAY_CACHE_ENABLED=true                  # Enable/disable caching
DOCSRAY_CACHE_DIR=.docsray                  # Cache directory location
DOCSRAY_CACHE_TTL=3600                      # Time-to-live in seconds
DOCSRAY_CACHE_MAX_SIZE_MB=1000              # Maximum cache size

# Advanced cache settings
DOCSRAY_CACHE_COMPRESSION=true              # Compress cached data
DOCSRAY_CACHE_CLEANUP_INTERVAL=3600         # Cleanup interval in seconds
DOCSRAY_CACHE_VALIDATION_ENABLED=true       # Validate cache integrity
DOCSRAY_CACHE_BACKUP_ENABLED=false          # Backup cache to cloud storage

# Provider-specific cache settings
LLAMAPARSE_DO_NOT_CACHE=false               # Disable LlamaParse caching
LLAMAPARSE_INVALIDATE_CACHE=false           # Force cache refresh
DOCSRAY_PYMUPDF_CACHE_TTL=1800              # PyMuPDF cache TTL
```

### Programmatic Configuration

```python
from docsray.config import CacheConfig

# Configure cache programmatically
cache_config = CacheConfig(
    enabled=True,
    cache_dir=".custom_cache",
    ttl_seconds=7200,  # 2 hours
    max_size_mb=2000,
    compression_enabled=True,
    auto_cleanup=True
)

# Apply configuration
docsray.configure_cache(cache_config)
```

## Cache Management

### Cache Status and Statistics

```python
def get_cache_statistics():
    """Get detailed cache usage statistics."""
    
    import os
    import json
    from pathlib import Path
    
    cache_dir = Path(os.getenv('DOCSRAY_CACHE_DIR', '.docsray'))
    
    if not cache_dir.exists():
        return {"status": "No cache directory found"}
    
    stats = {
        "cache_directory": str(cache_dir),
        "total_cached_documents": 0,
        "total_cache_size_mb": 0,
        "cached_operations": {},
        "oldest_cache_entry": None,
        "newest_cache_entry": None
    }
    
    # Analyze cache directory
    cache_times = []
    
    for doc_cache_dir in cache_dir.glob("*.docsray"):
        if doc_cache_dir.is_dir():
            stats["total_cached_documents"] += 1
            
            # Calculate directory size
            total_size = sum(f.stat().st_size for f in doc_cache_dir.rglob('*') if f.is_file())
            stats["total_cache_size_mb"] += total_size / (1024 * 1024)
            
            # Check operation types
            for result_dir in doc_cache_dir.iterdir():
                if result_dir.is_dir():
                    operation_type = result_dir.name.replace('_results', '')
                    stats["cached_operations"][operation_type] = stats["cached_operations"].get(operation_type, 0) + 1
            
            # Get cache timestamps
            metadata_file = doc_cache_dir / "metadata.json"
            if metadata_file.exists():
                cache_times.append(metadata_file.stat().st_mtime)
    
    if cache_times:
        stats["oldest_cache_entry"] = min(cache_times)
        stats["newest_cache_entry"] = max(cache_times)
        stats["total_cache_size_mb"] = round(stats["total_cache_size_mb"], 2)
    
    return stats

# Usage
cache_stats = get_cache_statistics()
print(f"Cached documents: {cache_stats['total_cached_documents']}")
print(f"Cache size: {cache_stats['total_cache_size_mb']} MB")
print(f"Operations cached: {cache_stats['cached_operations']}")
```

### Cache Cleanup and Maintenance

```python
def cleanup_cache(max_age_days=30, max_size_mb=1000):
    """Clean up old or excessive cache entries."""
    
    import os
    import shutil
    import time
    from pathlib import Path
    
    cache_dir = Path(os.getenv('DOCSRAY_CACHE_DIR', '.docsray'))
    
    if not cache_dir.exists():
        return {"status": "No cache to clean"}
    
    cleanup_stats = {
        "directories_removed": 0,
        "space_freed_mb": 0,
        "errors": []
    }
    
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 3600
    
    # Get all cache directories with their sizes and ages
    cache_dirs = []
    for doc_cache_dir in cache_dir.glob("*.docsray"):
        if doc_cache_dir.is_dir():
            metadata_file = doc_cache_dir / "metadata.json"
            if metadata_file.exists():
                age = current_time - metadata_file.stat().st_mtime
                size = sum(f.stat().st_size for f in doc_cache_dir.rglob('*') if f.is_file()) / (1024 * 1024)
                cache_dirs.append((doc_cache_dir, age, size))
    
    # Sort by age (oldest first) for cleanup
    cache_dirs.sort(key=lambda x: x[1], reverse=True)
    
    total_size = sum(entry[2] for entry in cache_dirs)
    
    for doc_cache_dir, age, size in cache_dirs:
        should_remove = False
        reason = ""
        
        # Remove if too old
        if age > max_age_seconds:
            should_remove = True
            reason = f"older than {max_age_days} days"
        
        # Remove if total cache size exceeds limit
        elif total_size > max_size_mb:
            should_remove = True
            reason = "cache size limit exceeded"
            total_size -= size
        
        if should_remove:
            try:
                shutil.rmtree(doc_cache_dir)
                cleanup_stats["directories_removed"] += 1
                cleanup_stats["space_freed_mb"] += size
                print(f"Removed cache for {doc_cache_dir.name}: {reason}")
            except Exception as e:
                cleanup_stats["errors"].append(f"Failed to remove {doc_cache_dir.name}: {str(e)}")
    
    cleanup_stats["space_freed_mb"] = round(cleanup_stats["space_freed_mb"], 2)
    return cleanup_stats

# Usage
cleanup_result = cleanup_cache(max_age_days=14, max_size_mb=500)
print(f"Cleanup complete: {cleanup_result}")
```

### Selective Cache Invalidation

```python
def invalidate_cache_for_document(document_path):
    """Invalidate cache for a specific document."""
    
    import hashlib
    import shutil
    from pathlib import Path
    
    # Generate document hash to find cache directory
    with open(document_path, 'rb') as f:
        content = f.read()
        doc_hash = hashlib.sha256(content).hexdigest()[:8]
    
    cache_dir = Path(os.getenv('DOCSRAY_CACHE_DIR', '.docsray'))
    
    # Find matching cache directory
    for cache_subdir in cache_dir.glob(f"*.{doc_hash}.docsray"):
        if cache_subdir.is_dir():
            try:
                shutil.rmtree(cache_subdir)
                print(f"Invalidated cache for {document_path}")
                return True
            except Exception as e:
                print(f"Failed to invalidate cache: {str(e)}")
                return False
    
    print(f"No cache found for {document_path}")
    return False

def invalidate_operation_cache(document_path, operation_type):
    """Invalidate cache for specific operation on a document."""
    
    import hashlib
    import shutil
    from pathlib import Path
    
    # Generate document hash
    with open(document_path, 'rb') as f:
        content = f.read()
        doc_hash = hashlib.sha256(content).hexdigest()[:8]
    
    cache_dir = Path(os.getenv('DOCSRAY_CACHE_DIR', '.docsray'))
    
    # Find and remove specific operation cache
    for cache_subdir in cache_dir.glob(f"*.{doc_hash}.docsray"):
        if cache_subdir.is_dir():
            operation_cache = cache_subdir / f"{operation_type}_results"
            if operation_cache.exists():
                try:
                    shutil.rmtree(operation_cache)
                    print(f"Invalidated {operation_type} cache for {document_path}")
                    return True
                except Exception as e:
                    print(f"Failed to invalidate {operation_type} cache: {str(e)}")
                    return False
    
    print(f"No {operation_type} cache found for {document_path}")
    return False

# Usage examples
invalidate_cache_for_document("updated-document.pdf")
invalidate_operation_cache("document.pdf", "xray")
```

## Performance Optimization

### Cache Hit Rate Analysis

```python
def analyze_cache_performance():
    """Analyze cache hit rates and performance."""
    
    # This would typically be implemented with cache metrics
    # For demonstration, showing the concept
    
    performance_metrics = {
        "cache_hit_rate": 0.85,  # 85% of operations use cache
        "avg_cache_lookup_time": 0.05,  # 50ms average lookup
        "avg_cold_operation_time": 15.2,  # 15.2s for uncached operations
        "cache_size_efficiency": 0.92,  # 92% of cache space is useful
        "most_cached_operations": {
            "peek": 1250,
            "extract": 890,
            "xray": 340,
            "map": 120
        }
    }
    
    # Calculate performance benefits
    operations_cached = performance_metrics["cache_hit_rate"]
    time_saved_per_operation = performance_metrics["avg_cold_operation_time"] - performance_metrics["avg_cache_lookup_time"]
    
    performance_metrics["estimated_time_savings"] = {
        "per_cached_operation": f"{time_saved_per_operation:.1f}s",
        "total_operations": sum(performance_metrics["most_cached_operations"].values()),
        "total_time_saved": f"{sum(performance_metrics['most_cached_operations'].values()) * operations_cached * time_saved_per_operation / 3600:.1f} hours"
    }
    
    return performance_metrics

# Usage
perf_metrics = analyze_cache_performance()
print(f"Cache hit rate: {perf_metrics['cache_hit_rate']:.1%}")
print(f"Time saved per cached operation: {perf_metrics['estimated_time_savings']['per_cached_operation']}")
print(f"Total estimated time savings: {perf_metrics['estimated_time_savings']['total_time_saved']}")
```

### Cache Warming Strategies

```python
def warm_cache_for_documents(document_paths, operations=None):
    """Pre-populate cache for frequently accessed documents."""
    
    if operations is None:
        operations = ["peek", "extract"]  # Most common operations
    
    warming_results = {
        "documents_processed": 0,
        "operations_cached": 0,
        "total_time": 0,
        "errors": []
    }
    
    import time
    start_time = time.time()
    
    for doc_path in document_paths:
        try:
            print(f"Warming cache for {doc_path}...")
            
            for operation in operations:
                op_start = time.time()
                
                if operation == "peek":
                    docsray.peek(doc_path, depth="structure")
                elif operation == "extract":
                    docsray.extract(doc_path, provider="pymupdf4llm")  # Fast extraction
                elif operation == "map":
                    docsray.map(doc_path, analysis_depth="basic")
                elif operation == "xray":
                    docsray.xray(doc_path, analysis_type=["entities"])
                
                op_time = time.time() - op_start
                print(f"  {operation}: {op_time:.1f}s")
                
                warming_results["operations_cached"] += 1
            
            warming_results["documents_processed"] += 1
            
        except Exception as e:
            error_msg = f"Failed to warm cache for {doc_path}: {str(e)}"
            warming_results["errors"].append(error_msg)
            print(f"  Error: {error_msg}")
    
    warming_results["total_time"] = time.time() - start_time
    
    return warming_results

# Usage - warm cache for frequently accessed documents
frequently_accessed = [
    "quarterly-report.pdf",
    "annual-report.pdf", 
    "board-presentation.pdf"
]

warming_result = warm_cache_for_documents(
    frequently_accessed,
    operations=["peek", "extract", "xray"]
)

print(f"Cache warming complete: {warming_result['documents_processed']} documents")
print(f"Total operations cached: {warming_result['operations_cached']}")
print(f"Total time: {warming_result['total_time']:.1f}s")
```

## Advanced Cache Features

### Cache Compression

```python
def configure_cache_compression():
    """Configure cache compression for space efficiency."""
    
    # Cache compression is automatically enabled for:
    # - JSON results larger than 1MB
    # - Full text extractions
    # - Large image extractions
    
    compression_settings = {
        "enabled": True,
        "algorithm": "gzip",  # or "lz4" for faster compression
        "compression_level": 6,  # Balance of speed vs. compression
        "min_size_bytes": 1024 * 1024,  # Only compress files > 1MB
        "exclude_formats": [".jpg", ".png", ".pdf"]  # Already compressed
    }
    
    return compression_settings

# Set compression via environment
import os
os.environ['DOCSRAY_CACHE_COMPRESSION'] = 'true'
os.environ['DOCSRAY_CACHE_COMPRESSION_LEVEL'] = '6'
```

### Cache Synchronization

```python
def setup_distributed_cache():
    """Set up distributed cache for multiple instances."""
    
    # Configuration for shared cache storage
    distributed_config = {
        "type": "shared_filesystem",  # or "redis", "s3"
        "location": "/shared/docsray-cache",
        "sync_interval_seconds": 300,
        "conflict_resolution": "timestamp",  # newest wins
        "backup_enabled": True,
        "backup_location": "s3://bucket/docsray-backup"
    }
    
    # Environment setup for distributed caching
    cache_env_vars = {
        "DOCSRAY_CACHE_TYPE": "distributed",
        "DOCSRAY_CACHE_SHARED_PATH": "/shared/docsray-cache",
        "DOCSRAY_CACHE_SYNC_ENABLED": "true",
        "DOCSRAY_CACHE_BACKUP_S3_BUCKET": "bucket/docsray-backup"
    }
    
    return distributed_config, cache_env_vars

# Example distributed cache setup
config, env_vars = setup_distributed_cache()
print("Distributed cache configuration:")
for key, value in env_vars.items():
    print(f"  {key}={value}")
```

## Cache Monitoring and Alerts

```python
def monitor_cache_health():
    """Monitor cache health and set up alerts."""
    
    health_metrics = {
        "cache_hit_rate": 0.0,
        "cache_size_mb": 0.0,
        "cache_age_distribution": {},
        "error_rate": 0.0,
        "disk_usage_percent": 0.0
    }
    
    # Get cache statistics
    stats = get_cache_statistics()
    
    # Calculate health scores
    health_score = 100
    alerts = []
    
    # Check cache hit rate
    if stats.get("cache_hit_rate", 0) < 0.5:
        health_score -= 20
        alerts.append("Low cache hit rate - consider cache warming")
    
    # Check cache size
    cache_size = stats.get("total_cache_size_mb", 0)
    if cache_size > 2000:  # 2GB
        health_score -= 15
        alerts.append("Large cache size - consider cleanup")
    
    # Check disk space
    import shutil
    disk_usage = shutil.disk_usage(".")
    disk_free_percent = (disk_usage.free / disk_usage.total) * 100
    
    if disk_free_percent < 10:
        health_score -= 30
        alerts.append("Low disk space - cache may fail")
    
    health_metrics.update({
        "health_score": health_score,
        "alerts": alerts,
        "cache_size_mb": cache_size,
        "disk_free_percent": disk_free_percent
    })
    
    return health_metrics

def setup_cache_alerts(email_notify=False):
    """Set up automated cache monitoring and alerts."""
    
    alert_config = {
        "monitoring_interval": 3600,  # Check every hour
        "alert_thresholds": {
            "cache_size_mb": 2000,
            "disk_free_percent": 10,
            "cache_hit_rate": 0.5,
            "error_rate": 0.05
        },
        "notification_methods": ["log", "email"] if email_notify else ["log"],
        "alert_cooldown": 3600  # Don't spam alerts
    }
    
    return alert_config

# Usage
health = monitor_cache_health()
print(f"Cache health score: {health['health_score']}/100")
if health['alerts']:
    print("Alerts:")
    for alert in health['alerts']:
        print(f"  ⚠️ {alert}")
```

## Best Practices

1. **Enable Caching** - Always keep caching enabled unless debugging
2. **Monitor Cache Size** - Set appropriate size limits and cleanup schedules
3. **Cache Warming** - Pre-populate cache for frequently accessed documents
4. **Selective Invalidation** - Only invalidate cache when documents change
5. **Compression** - Enable compression for large documents
6. **Regular Cleanup** - Set up automated cache maintenance
7. **Performance Monitoring** - Track cache hit rates and benefits

## Troubleshooting

### Common Cache Issues

```python
def diagnose_cache_issues():
    """Diagnose common cache problems."""
    
    import os
    from pathlib import Path
    
    issues = []
    
    # Check if caching is enabled
    if os.getenv('DOCSRAY_CACHE_ENABLED', 'true').lower() == 'false':
        issues.append("Caching is disabled - set DOCSRAY_CACHE_ENABLED=true")
    
    # Check cache directory permissions
    cache_dir = Path(os.getenv('DOCSRAY_CACHE_DIR', '.docsray'))
    if cache_dir.exists():
        if not os.access(cache_dir, os.W_OK):
            issues.append(f"Cache directory not writable: {cache_dir}")
    else:
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            issues.append(f"Cannot create cache directory: {cache_dir}")
    
    # Check disk space
    import shutil
    try:
        disk_usage = shutil.disk_usage(cache_dir.parent)
        free_gb = disk_usage.free / (1024**3)
        if free_gb < 1:
            issues.append(f"Low disk space: {free_gb:.1f}GB free")
    except:
        issues.append("Cannot check disk space")
    
    # Check for corrupted cache
    if cache_dir.exists():
        for cache_subdir in cache_dir.glob("*.docsray"):
            metadata_file = cache_subdir / "metadata.json"
            if not metadata_file.exists():
                issues.append(f"Corrupted cache directory: {cache_subdir.name}")
    
    return issues

# Usage
cache_issues = diagnose_cache_issues()
if cache_issues:
    print("Cache Issues Found:")
    for issue in cache_issues:
        print(f"  ❌ {issue}")
else:
    print("✅ No cache issues detected")
```

## Next Steps

- Learn about [Performance Optimization](./performance) for overall system tuning
- See [Troubleshooting Guide](./troubleshooting) for resolving issues
- Check [Configuration Guide](../getting-started/configuration) for setup options