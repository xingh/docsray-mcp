---
sidebar_position: 2
---

# Performance Optimization

Optimize Docsray for speed, throughput, and resource efficiency across different use cases and environments.

## Performance Overview

Docsray's performance depends on several factors:
- **Document characteristics** - Size, complexity, format
- **Provider selection** - PyMuPDF4LLM vs LlamaParse
- **Operation type** - peek vs extract vs xray
- **System resources** - CPU, memory, network
- **Cache utilization** - Hit rates and storage efficiency

## Quick Performance Wins

### 1. Enable Caching

```bash
# Ensure caching is enabled (default)
export DOCSRAY_CACHE_ENABLED=true
export DOCSRAY_CACHE_TTL=3600
```

### 2. Choose Right Provider

```python
# Fast operations (< 1 second)
result = docsray.peek("doc.pdf", provider="pymupdf4llm")
result = docsray.extract("doc.pdf", provider="pymupdf4llm")

# Quality operations (5-30 seconds)
result = docsray.xray("doc.pdf", provider="llama-parse")
```

### 3. Use Appropriate Depths

```python
# Fastest - metadata only
docsray.peek("doc.pdf", depth="metadata")

# Balanced - structure included  
docsray.peek("doc.pdf", depth="structure")

# Comprehensive - full preview
docsray.peek("doc.pdf", depth="preview")
```

## Provider Performance Comparison

### Speed Benchmarks

| Operation | PyMuPDF4LLM | LlamaParse | Speedup |
|-----------|-------------|------------|---------|
| **Peek (metadata)** | 0.1s | 0.3s | 3x faster |
| **Peek (structure)** | 0.3s | 2.1s | 7x faster |
| **Extract (text)** | 0.5s | 12.5s | 25x faster |
| **Extract (tables)** | 0.8s | 18.2s | 23x faster |
| **Map (basic)** | 1.2s | 8.4s | 7x faster |
| **Xray (entities)** | N/A | 15.8s | LlamaParse only |

### Quality vs Speed Tradeoffs

```python
def choose_provider_strategy(document_path, priority="balanced"):
    """Choose provider based on performance requirements."""
    
    # Get document characteristics
    overview = docsray.peek(document_path, depth="metadata")
    page_count = overview['metadata']['page_count']
    file_size_mb = overview['metadata']['file_size'] / (1024 * 1024)
    
    if priority == "speed":
        # Prioritize speed over quality
        return "pymupdf4llm"
    
    elif priority == "quality":
        # Prioritize quality over speed
        return "llama-parse"
    
    elif priority == "balanced":
        # Balance speed and quality based on document
        if page_count > 50 or file_size_mb > 10:
            return "pymupdf4llm"  # Large docs - use fast provider
        elif overview['metadata'].get('has_tables', False):
            return "llama-parse"  # Tables - use quality provider
        else:
            return "pymupdf4llm"  # Default to fast
    
    elif priority == "cost":
        # Minimize API costs
        return "pymupdf4llm"
    
    return "pymupdf4llm"  # Default fallback

# Usage
strategy = choose_provider_strategy("report.pdf", priority="balanced")
result = docsray.extract("report.pdf", provider=strategy)
```

## Concurrent Processing

### Parallel Document Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def process_document_parallel(document_paths, max_workers=3):
    """Process multiple documents in parallel."""
    
    def process_single(doc_path):
        start_time = time.time()
        try:
            # Choose fast operations for parallel processing
            result = docsray.extract(doc_path, provider="pymupdf4llm")
            processing_time = time.time() - start_time
            
            return {
                "document": doc_path,
                "success": True,
                "processing_time": processing_time,
                "word_count": result['extraction']['word_count'],
                "error": None
            }
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "document": doc_path,
                "success": False,
                "processing_time": processing_time,
                "word_count": 0,
                "error": str(e)
            }
    
    # Process documents in parallel
    results = []
    total_start = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_doc = {executor.submit(process_single, doc): doc 
                        for doc in document_paths}
        
        for future in as_completed(future_to_doc):
            result = future.result()
            results.append(result)
            
            status = "✓" if result["success"] else "✗"
            print(f"{status} {result['document']}: {result['processing_time']:.1f}s")
    
    total_time = time.time() - total_start
    successful = [r for r in results if r["success"]]
    
    print(f"\nParallel processing complete:")
    print(f"  Total time: {total_time:.1f}s")
    print(f"  Successful: {len(successful)}/{len(document_paths)}")
    print(f"  Total words: {sum(r['word_count'] for r in successful):,}")
    print(f"  Throughput: {len(successful)/total_time:.1f} docs/second")
    
    return results

# Usage
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf", "doc4.pdf"]
results = process_document_parallel(documents, max_workers=4)
```

### Batch Processing Optimization

```python
def optimized_batch_processing(document_paths, batch_size=5):
    """Process documents in optimized batches."""
    
    # Group documents by characteristics for optimal processing
    document_groups = {
        "small_fast": [],    # < 10 pages, use fast provider
        "medium_balanced": [], # 10-50 pages, balanced approach  
        "large_chunked": []    # > 50 pages, process in chunks
    }
    
    # Categorize documents
    for doc_path in document_paths:
        try:
            overview = docsray.peek(doc_path, depth="metadata")
            page_count = overview['metadata']['page_count']
            
            if page_count < 10:
                document_groups["small_fast"].append(doc_path)
            elif page_count <= 50:
                document_groups["medium_balanced"].append(doc_path)
            else:
                document_groups["large_chunked"].append(doc_path)
                
        except Exception as e:
            print(f"Warning: Could not categorize {doc_path}: {e}")
            document_groups["medium_balanced"].append(doc_path)  # Default
    
    batch_results = []
    
    # Process small documents quickly in parallel
    if document_groups["small_fast"]:
        print(f"Processing {len(document_groups['small_fast'])} small documents...")
        small_results = process_document_parallel(
            document_groups["small_fast"], 
            max_workers=6  # More workers for fast operations
        )
        batch_results.extend(small_results)
    
    # Process medium documents with balanced approach
    if document_groups["medium_balanced"]:
        print(f"Processing {len(document_groups['medium_balanced'])} medium documents...")
        medium_results = process_document_parallel(
            document_groups["medium_balanced"],
            max_workers=3  # Fewer workers for balanced processing
        )
        batch_results.extend(medium_results)
    
    # Process large documents individually with chunking
    if document_groups["large_chunked"]:
        print(f"Processing {len(document_groups['large_chunked'])} large documents...")
        for doc_path in document_groups["large_chunked"]:
            try:
                # Process first 20 pages only for large documents
                result = docsray.extract(
                    doc_path, 
                    pages=list(range(1, 21)),
                    provider="pymupdf4llm"
                )
                batch_results.append({
                    "document": doc_path,
                    "success": True,
                    "word_count": result['extraction']['word_count'],
                    "note": "First 20 pages only"
                })
            except Exception as e:
                batch_results.append({
                    "document": doc_path,
                    "success": False,
                    "error": str(e)
                })
    
    return batch_results

# Usage
documents = ["small1.pdf", "medium1.pdf", "large1.pdf", "small2.pdf"]
batch_results = optimized_batch_processing(documents)
```

## Memory Optimization

### Memory-Efficient Processing

```python
def memory_efficient_extraction(document_path, max_memory_mb=500):
    """Extract content while managing memory usage."""
    
    import psutil
    import os
    
    # Check initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / (1024 * 1024)
    
    # Get document size
    overview = docsray.peek(document_path, depth="metadata")
    page_count = overview['metadata']['page_count']
    file_size_mb = overview['metadata']['file_size'] / (1024 * 1024)
    
    print(f"Document: {page_count} pages, {file_size_mb:.1f}MB")
    print(f"Initial memory: {initial_memory:.1f}MB")
    
    # Choose memory-efficient strategy
    if file_size_mb > 20 or page_count > 100:
        # Large document - process in chunks
        chunk_size = min(25, max(5, 1000 // page_count))  # Dynamic chunk size
        results = []
        
        for start_page in range(1, page_count + 1, chunk_size):
            end_page = min(start_page + chunk_size - 1, page_count)
            page_range = list(range(start_page, end_page + 1))
            
            print(f"Processing pages {start_page}-{end_page}...")
            
            try:
                chunk_result = docsray.extract(
                    document_path,
                    pages=page_range,
                    provider="pymupdf4llm"  # Memory efficient
                )
                
                results.append({
                    "pages": f"{start_page}-{end_page}",
                    "content": chunk_result['extraction']['text'],
                    "word_count": chunk_result['extraction']['word_count']
                })
                
                # Check memory usage
                current_memory = process.memory_info().rss / (1024 * 1024)
                memory_increase = current_memory - initial_memory
                
                if memory_increase > max_memory_mb:
                    print(f"Memory limit reached: {current_memory:.1f}MB")
                    break
                    
            except Exception as e:
                print(f"Error processing pages {start_page}-{end_page}: {e}")
                break
        
        # Combine results
        combined_content = "\\n\\n".join(r["content"] for r in results)
        total_words = sum(r["word_count"] for r in results)
        
        return {
            "extraction": {
                "text": combined_content,
                "word_count": total_words,
                "chunks_processed": len(results),
                "memory_efficient": True
            }
        }
    
    else:
        # Small/medium document - process normally
        return docsray.extract(document_path, provider="pymupdf4llm")

# Usage
result = memory_efficient_extraction("large-report.pdf", max_memory_mb=300)
print(f"Extracted {result['extraction']['word_count']} words in {result['extraction'].get('chunks_processed', 1)} chunks")
```

### Resource Monitoring

```python
def monitor_resource_usage():
    """Monitor CPU, memory, and disk usage during processing."""
    
    import psutil
    import time
    import threading
    
    monitoring_data = {
        "cpu_percent": [],
        "memory_mb": [],
        "disk_io": [],
        "timestamps": []
    }
    
    monitoring_active = threading.Event()
    monitoring_active.set()
    
    def monitor_loop():
        while monitoring_active.is_set():
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_mb = memory.used / (1024 * 1024)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            
            monitoring_data["cpu_percent"].append(cpu_percent)
            monitoring_data["memory_mb"].append(memory_mb)
            monitoring_data["disk_io"].append(disk_io.read_bytes + disk_io.write_bytes)
            monitoring_data["timestamps"].append(time.time())
            
            time.sleep(1)
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    
    return monitoring_data, monitoring_active

def analyze_resource_usage(monitoring_data):
    """Analyze resource usage patterns."""
    
    if not monitoring_data["cpu_percent"]:
        return {"error": "No monitoring data available"}
    
    analysis = {
        "duration_seconds": len(monitoring_data["cpu_percent"]),
        "cpu": {
            "average": sum(monitoring_data["cpu_percent"]) / len(monitoring_data["cpu_percent"]),
            "max": max(monitoring_data["cpu_percent"]),
            "min": min(monitoring_data["cpu_percent"])
        },
        "memory": {
            "average_mb": sum(monitoring_data["memory_mb"]) / len(monitoring_data["memory_mb"]),
            "max_mb": max(monitoring_data["memory_mb"]),
            "min_mb": min(monitoring_data["memory_mb"])
        },
        "disk_io": {
            "total_bytes": monitoring_data["disk_io"][-1] - monitoring_data["disk_io"][0] if len(monitoring_data["disk_io"]) > 1 else 0
        }
    }
    
    return analysis

# Usage example
monitoring_data, monitoring_active = monitor_resource_usage()

try:
    # Perform document processing
    result = docsray.extract("large-document.pdf")
    
finally:
    # Stop monitoring
    monitoring_active.clear()
    time.sleep(2)  # Wait for monitor thread to finish
    
    # Analyze usage
    analysis = analyze_resource_usage(monitoring_data)
    print(f"Resource usage analysis:")
    print(f"  Duration: {analysis['duration_seconds']}s")
    print(f"  CPU average: {analysis['cpu']['average']:.1f}%")
    print(f"  Memory average: {analysis['memory']['average_mb']:.1f}MB")
    print(f"  Disk I/O: {analysis['disk_io']['total_bytes'] / (1024*1024):.1f}MB")
```

## Network Optimization

### Connection Pooling and Timeouts

```python
def optimize_network_settings():
    """Configure optimal network settings for API calls."""
    
    network_config = {
        # LlamaParse API optimization
        "LLAMAPARSE_MAX_TIMEOUT": "60",        # Reasonable timeout
        "LLAMAPARSE_CHECK_INTERVAL": "2",      # Check status every 2s
        "DOCSRAY_MAX_CONCURRENT_REQUESTS": "3", # Limit concurrent requests
        
        # HTTP optimization
        "DOCSRAY_HTTP_TIMEOUT": "30",          # Connection timeout
        "DOCSRAY_MAX_RETRIES": "2",            # Retry failed requests
        "DOCSRAY_RETRY_DELAY": "1",            # Delay between retries
        
        # Network efficiency
        "DOCSRAY_KEEP_ALIVE": "true",          # Reuse connections
        "DOCSRAY_COMPRESSION": "true",         # Compress requests/responses
    }
    
    # Apply settings
    import os
    for key, value in network_config.items():
        os.environ[key] = value
    
    return network_config

# Apply network optimizations
network_settings = optimize_network_settings()
print("Network optimization applied:")
for key, value in network_settings.items():
    print(f"  {key}={value}")
```

### Offline Processing Strategies

```python
def maximize_offline_processing(document_paths):
    """Maximize use of offline providers to reduce network dependency."""
    
    processing_plan = {
        "offline_capable": [],
        "requires_network": [],
        "hybrid_approach": []
    }
    
    for doc_path in document_paths:
        try:
            # Analyze document requirements
            overview = docsray.peek(doc_path, depth="structure")
            
            has_complex_tables = overview['structure'].get('tables', 0) > 3
            has_many_images = overview['metadata'].get('has_images', False)
            needs_entity_extraction = "entity" in doc_path.lower() or "contract" in doc_path.lower()
            
            if needs_entity_extraction:
                processing_plan["requires_network"].append({
                    "document": doc_path,
                    "reason": "Entity extraction requires LlamaParse",
                    "provider": "llama-parse"
                })
            elif has_complex_tables:
                processing_plan["hybrid_approach"].append({
                    "document": doc_path,
                    "reason": "Complex tables - try offline first, fallback to online",
                    "primary_provider": "pymupdf4llm",
                    "fallback_provider": "llama-parse"
                })
            else:
                processing_plan["offline_capable"].append({
                    "document": doc_path,
                    "reason": "Standard document - offline processing sufficient",
                    "provider": "pymupdf4llm"
                })
                
        except Exception as e:
            print(f"Could not analyze {doc_path}: {e}")
            processing_plan["offline_capable"].append({
                "document": doc_path,
                "reason": "Default to offline processing",
                "provider": "pymupdf4llm"
            })
    
    return processing_plan

def execute_offline_first_strategy(processing_plan):
    """Execute processing with offline-first approach."""
    
    results = {
        "offline_results": [],
        "network_results": [],
        "hybrid_results": [],
        "performance_summary": {}
    }
    
    start_time = time.time()
    
    # Process offline-capable documents first (fast)
    print(f"Processing {len(processing_plan['offline_capable'])} documents offline...")
    for item in processing_plan["offline_capable"]:
        try:
            result = docsray.extract(item["document"], provider=item["provider"])
            results["offline_results"].append({
                "document": item["document"],
                "success": True,
                "word_count": result['extraction']['word_count']
            })
        except Exception as e:
            results["offline_results"].append({
                "document": item["document"],
                "success": False,
                "error": str(e)
            })
    
    offline_time = time.time() - start_time
    
    # Process hybrid documents (try offline first)
    print(f"Processing {len(processing_plan['hybrid_approach'])} documents with hybrid approach...")
    for item in processing_plan["hybrid_approach"]:
        try:
            # Try offline first
            result = docsray.extract(item["document"], provider=item["primary_provider"])
            results["hybrid_results"].append({
                "document": item["document"],
                "success": True,
                "provider_used": item["primary_provider"],
                "word_count": result['extraction']['word_count']
            })
        except Exception:
            try:
                # Fallback to network provider
                result = docsray.extract(item["document"], provider=item["fallback_provider"])
                results["hybrid_results"].append({
                    "document": item["document"],
                    "success": True,
                    "provider_used": item["fallback_provider"],
                    "word_count": result['extraction']['word_count']
                })
            except Exception as e:
                results["hybrid_results"].append({
                    "document": item["document"],
                    "success": False,
                    "error": str(e)
                })
    
    hybrid_time = time.time() - start_time - offline_time
    
    # Process network-required documents
    print(f"Processing {len(processing_plan['requires_network'])} documents requiring network...")
    for item in processing_plan["requires_network"]:
        try:
            result = docsray.xray(item["document"], provider=item["provider"])
            results["network_results"].append({
                "document": item["document"],
                "success": True,
                "entity_count": len(result['analysis']['extracted_content'].get('entities', []))
            })
        except Exception as e:
            results["network_results"].append({
                "document": item["document"],
                "success": False,
                "error": str(e)
            })
    
    network_time = time.time() - start_time - offline_time - hybrid_time
    
    results["performance_summary"] = {
        "total_time": time.time() - start_time,
        "offline_time": offline_time,
        "hybrid_time": hybrid_time, 
        "network_time": network_time,
        "offline_percentage": (offline_time / (time.time() - start_time)) * 100
    }
    
    return results

# Usage
documents = ["report1.pdf", "contract.pdf", "tables.pdf", "simple.pdf"]
plan = maximize_offline_processing(documents)
results = execute_offline_first_strategy(plan)

print(f"\\nOffline processing: {results['performance_summary']['offline_percentage']:.1f}%")
print(f"Total time: {results['performance_summary']['total_time']:.1f}s")
```

## Performance Monitoring

### Benchmarking Tools

```python
def benchmark_operations(test_documents, iterations=3):
    """Benchmark different operations and providers."""
    
    import statistics
    
    benchmarks = {
        "operations": ["peek", "extract", "xray"],
        "providers": ["pymupdf4llm", "llama-parse"],
        "results": {}
    }
    
    for doc_path in test_documents:
        doc_results = {}
        
        for operation in benchmarks["operations"]:
            for provider in benchmarks["providers"]:
                if operation == "xray" and provider == "pymupdf4llm":
                    continue  # Skip unsupported combination
                
                times = []
                success_count = 0
                
                for iteration in range(iterations):
                    try:
                        start_time = time.time()
                        
                        if operation == "peek":
                            docsray.peek(doc_path, depth="structure", provider=provider)
                        elif operation == "extract":
                            docsray.extract(doc_path, provider=provider)
                        elif operation == "xray":
                            docsray.xray(doc_path, analysis_type=["entities"], provider=provider)
                        
                        elapsed = time.time() - start_time
                        times.append(elapsed)
                        success_count += 1
                        
                    except Exception as e:
                        print(f"Failed {operation} with {provider} on {doc_path}: {e}")
                
                if times:
                    key = f"{operation}_{provider}"
                    doc_results[key] = {
                        "mean_time": statistics.mean(times),
                        "median_time": statistics.median(times),
                        "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
                        "success_rate": success_count / iterations,
                        "iterations": iterations
                    }
        
        benchmarks["results"][doc_path] = doc_results
    
    return benchmarks

def analyze_benchmarks(benchmarks):
    """Analyze benchmark results and provide recommendations."""
    
    analysis = {
        "fastest_operations": {},
        "most_reliable": {},
        "recommendations": []
    }
    
    # Find fastest operations for each document
    for doc_path, results in benchmarks["results"].items():
        fastest_op = None
        fastest_time = float('inf')
        
        for op_provider, metrics in results.items():
            if metrics["success_rate"] == 1.0 and metrics["mean_time"] < fastest_time:
                fastest_time = metrics["mean_time"]
                fastest_op = op_provider
        
        if fastest_op:
            analysis["fastest_operations"][doc_path] = {
                "operation": fastest_op,
                "time": fastest_time
            }
    
    # Generate recommendations
    pymupdf_times = []
    llama_times = []
    
    for doc_results in benchmarks["results"].values():
        for op_provider, metrics in doc_results.items():
            if "pymupdf4llm" in op_provider and metrics["success_rate"] == 1.0:
                pymupdf_times.append(metrics["mean_time"])
            elif "llama-parse" in op_provider and metrics["success_rate"] == 1.0:
                llama_times.append(metrics["mean_time"])
    
    if pymupdf_times and llama_times:
        pymupdf_avg = statistics.mean(pymupdf_times)
        llama_avg = statistics.mean(llama_times)
        speedup = llama_avg / pymupdf_avg
        
        analysis["recommendations"].append(
            f"PyMuPDF4LLM is {speedup:.1f}x faster on average ({pymupdf_avg:.1f}s vs {llama_avg:.1f}s)"
        )
    
    return analysis

# Usage
test_docs = ["small.pdf", "medium.pdf", "large.pdf"]
benchmark_results = benchmark_operations(test_docs, iterations=3)
analysis = analyze_benchmarks(benchmark_results)

print("\\nPerformance Recommendations:")
for recommendation in analysis["recommendations"]:
    print(f"  • {recommendation}")
```

## Best Practices Summary

1. **Cache Everything** - Enable caching and warm frequently accessed documents
2. **Choose Right Provider** - PyMuPDF4LLM for speed, LlamaParse for quality
3. **Process in Parallel** - Use concurrent processing for multiple documents
4. **Monitor Resources** - Track CPU, memory, and network usage
5. **Optimize for Context** - Adapt strategies based on document characteristics
6. **Measure Performance** - Benchmark operations and track improvements
7. **Plan for Scale** - Design for your expected document volume and frequency

## Next Steps

- Learn about [Caching Strategies](./caching) for optimal cache utilization
- See [Troubleshooting Guide](./troubleshooting) for resolving performance issues
- Check [Configuration Options](../getting-started/configuration) for tuning parameters