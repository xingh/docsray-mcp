# Docsray MCP Lightweight Remote-Only Capabilities System Refactor Plan

**Status:** Planning  
**Date:** 2025-10-27  
**Issue:** #16  
**Objective:** Transform Docsray into a lightweight, containerized system with clear capability classification, enabling deployment anywhere with minimal local resources while maintaining the option for GPU-enhanced perception.

---

## Executive Summary

This refactor plan addresses the following core goals:
1. **Performant** - Lightweight base image with optional heavy dependencies
2. **Stable** - Proper dependency isolation and graceful degradation
3. **Reliable** - Docker builds succeed locally and in CI/CD
4. **Accurate** - Clear provider classification and capability reporting
5. **Economic** - Efficient use of tokens, GPU resources, and API calls when needed

The refactor introduces a clear capability classification system separating **storage** and **perception** capabilities, with perception further divided into **local** and **remote** variants. This enables deployment in resource-constrained environments (CPU + memory only) while preserving advanced GPU-accelerated capabilities when available.

---

## Current State Analysis

### Architecture Overview

**Core Components:**
- **6,005 lines of Python code** across providers, tools, and utilities
- **7 MCP tools:** peek, map, xray, extract, seek, fetch, search
- **4 document providers:** PyMuPDF4LLM, LlamaParse, IBM.Docling, MIMIC.DocsRay
- **FastMCP framework** for MCP protocol implementation
- **Provider registry** with intelligent scoring-based selection

### Current Dependency Structure

**Base Dependencies (always installed):**
```
fastmcp>=2.11.1
pymupdf4llm>=0.0.17
httpx>=0.27.0
pydantic>=2.0.0
python-dotenv>=1.0.0
typing-extensions>=4.0.0
aiofiles>=24.0.0
click>=8.0.0
nest-asyncio>=1.5.0
```

**Optional Dependencies:**

1. **`ocr` extra:**
   - pytesseract>=0.3.10
   - ocrmypdf>=16.0.0
   - pillow>=10.0.0

2. **`ai` extra:**
   - mistralai>=1.0.0
   - llama-parse>=0.6.0
   - **docling>=2.58.0** ← Heavy dependency (VLM models, layout models)
   - sentence-transformers>=3.0.0
   - faiss-cpu>=1.7.0

3. **`dev` extra:** Testing and development tools
4. **`docker` extra:** Docker testing dependencies
5. **`all` extra:** Combines ocr, ai, dev, docker

### Current Problems Identified

#### 1. Docker Build Failures
- **SSL certificate verification errors** in build environment
- Base Dockerfile attempts to `pip install -e .` which pulls all base dependencies
- No network isolation or retry logic for PyPI access
- Development stage tries to install `[dev,ocr,ai]` which includes heavy dependencies

#### 2. Dependency Misclassification
- **Docling is in `ai` extra** but requires:
  - Heavy VLM models (layout understanding, table detection)
  - GPU for optimal performance
  - Significant disk space and memory
  - Local model downloads
- **Docling should be classified as `local-ai`** not remote AI
- **MIMIC.DocsRay in `ai` extra** includes:
  - sentence-transformers (local embeddings)
  - faiss-cpu (local vector store)
  - These are local-ai dependencies, not remote

#### 3. Missing Remote AI Providers
- **Gemini** (Google Cloud API) - mentioned in issue but not implemented
- **OpenRouter** - mentioned in issue but not implemented
- **Mistral AI** - config exists but provider not fully implemented

#### 4. Storage Capability Classification Missing
- No abstraction for S3 or remote filesystem access
- All document fetching assumes local filesystem or HTTP download
- No shared storage between agents via S3

#### 5. Unclear Capability Reporting
- Providers report features generically
- No distinction between local vs remote capabilities
- No resource requirement reporting (CPU, GPU, memory, API keys)

#### 6. Documentation Gaps
- Missing setup guides for:
  - LlamaParse API key acquisition
  - OpenRouter configuration
  - Google Cloud API setup
- Coolify deployment not documented
- Environment variable documentation incomplete

---

## Proposed Capability Classification

### Storage Capabilities

#### Local Filesystem (`storage.local-filesystem`)
- **Current Implementation:** ✅ Implemented
- **Dependencies:** None (Python stdlib)
- **Resources:** CPU, memory
- **Providers:** Built-in file operations
- **Use Cases:** 
  - Local development
  - Single-agent deployments
  - Fast access to local documents

#### Remote Filesystem (`storage.remote-filesystem`)
- **Current Implementation:** ❌ Not implemented
- **Dependencies:** boto3 (AWS SDK), azure-storage-blob, google-cloud-storage
- **Resources:** Network, API keys
- **Providers:** S3, Azure Blob, Google Cloud Storage
- **Use Cases:**
  - Multi-agent shared storage
  - Distributed deployments
  - Scalable document repositories

**Recommendation:** Implement S3 abstraction as separate optional dependency `storage` extra:
```toml
storage = [
    "boto3>=1.28.0",
    "s3fs>=2023.0.0"
]
```

### Perception Capabilities

#### Local PDF (`perception.local-pdf`)
- **Current Implementation:** ✅ PyMuPDF4LLM (always enabled)
- **Dependencies:** pymupdf4llm>=0.0.17
- **Resources:** CPU, memory
- **Providers:** PyMuPDF4LLM
- **Features:**
  - Fast text extraction
  - Basic table detection
  - Page navigation
  - Multi-format support (PDF, XPS, EPUB)
- **Use Cases:** 
  - Text-based PDFs
  - Quick previews
  - Minimal resource environments

#### Local OCR (`perception.local-ocr`)
- **Current Implementation:** ⚠️ Partially implemented
- **Dependencies:** 
  - pytesseract>=0.3.10
  - ocrmypdf>=16.0.0
  - pillow>=10.0.0
  - tesseract-ocr (system package)
- **Resources:** CPU, memory
- **Providers:** PyTesseract, OCRmyPDF, Pillow
- **Features:**
  - Traditional OCR
  - Image preprocessing
  - Multi-language support
- **Use Cases:**
  - Scanned documents
  - Image-based PDFs
  - No API key required

#### Local AI (`perception.local-ai`)
- **Current Implementation:** ⚠️ Partially implemented (misclassified)
- **Dependencies:**
  - docling>=2.58.0 (VLM, layout models)
  - sentence-transformers>=3.0.0
  - faiss-cpu>=1.7.0 or faiss-gpu
  - torch, transformers (implicit)
- **Resources:** CPU (acceptable), GPU (optimal), memory (high), disk space (high)
- **Providers:** IBM.Docling, MIMIC.DocsRay (RAG components)
- **Features:**
  - Visual Language Model understanding
  - Advanced layout analysis
  - Local embeddings
  - Semantic search (RAG)
  - Entity extraction
  - Table/figure detection
- **Use Cases:**
  - GPU-enabled environments
  - High-accuracy requirements
  - Complex document analysis
  - Offline deployments

#### Remote AI (`perception.remote-ai`)
- **Current Implementation:** ⚠️ Partially implemented
- **Dependencies:**
  - llama-parse>=0.6.0
  - mistralai>=1.0.0
  - google-generativeai (Gemini) ← Not yet added
  - openai (for OpenRouter) ← Not yet added
- **Resources:** Network, API keys, minimal CPU/memory
- **Providers:** LlamaParse, Mistral AI, Gemini, OpenRouter
- **Features:**
  - Cloud-based document understanding
  - Custom analysis instructions
  - Entity extraction
  - Multi-modal analysis (text + images)
  - No local GPU required
- **Use Cases:**
  - Lightweight deployments
  - Containers with minimal resources
  - Pay-per-use models
  - Latest AI capabilities

---

## Refactoring Strategy

### Phase 1: Dependency Reorganization (Critical Path)

**Objective:** Fix Docker builds and properly classify dependencies.

#### 1.1 Restructure `pyproject.toml` Optional Dependencies

**Current:**
```toml
[project.optional-dependencies]
ocr = [...]
ai = [
    "mistralai>=1.0.0",
    "llama-parse>=0.6.0",
    "docling>=2.58.0",  # ← PROBLEM: Heavy local-ai
    "sentence-transformers>=3.0.0",  # ← PROBLEM: Local-ai
    "faiss-cpu>=1.7.0",  # ← PROBLEM: Local-ai
]
```

**Proposed:**
```toml
[project.optional-dependencies]
# Lightweight OCR (CPU only, no AI)
ocr = [
    "pytesseract>=0.3.10",
    "ocrmypdf>=16.0.0",
    "pillow>=10.0.0",
]

# Remote AI providers (minimal local resources)
remote-ai = [
    "llama-parse>=0.6.0",
    "mistralai>=1.0.0",
    "google-generativeai>=0.3.0",  # Gemini
    "openai>=1.0.0",  # For OpenRouter
]

# Local AI (requires GPU or high CPU/memory)
local-ai = [
    "docling>=2.58.0",
    "sentence-transformers>=3.0.0",
    "faiss-cpu>=1.7.0",
    "torch>=2.0.0",
    "transformers>=4.30.0",
]

# Local AI with GPU acceleration
local-ai-gpu = [
    "docling>=2.58.0",
    "sentence-transformers>=3.0.0",
    "faiss-gpu>=1.7.0",
    "torch>=2.0.0",
    "transformers>=4.30.0",
]

# Remote storage providers
storage = [
    "boto3>=1.28.0",
    "s3fs>=2023.0.0",
]

# Development tools
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=5.0.0",
    "pytest-mock>=3.14.0",
    "black>=24.0.0",
    "ruff>=0.5.0",
    "mypy>=1.0.0",
    "types-aiofiles",
]

# Docker testing
docker = [
    "testcontainers>=4.0.0",
    "requests>=2.28.0",
    "docker>=6.0.0",
    "pytest-docker>=2.0.0",
]

# Convenience bundles
lightweight = ["docsray-mcp[ocr,remote-ai]"]
full-local = ["docsray-mcp[ocr,local-ai,remote-ai,storage]"]
full-gpu = ["docsray-mcp[ocr,local-ai-gpu,remote-ai,storage]"]
all = ["docsray-mcp[ocr,local-ai,remote-ai,storage,dev,docker]"]
```

**Benefits:**
- Clear separation of local vs remote capabilities
- Users can install only what they need
- Docker images can be lightweight by default
- Explicit GPU vs CPU choices

#### 1.2 Update Dockerfile for Lightweight Base Image

**Current Issues:**
- Attempts to install all base dependencies in builder stage
- SSL certificate errors during PyPI access
- Development stage pulls heavy dependencies

**Proposed Dockerfile Strategy:**

```dockerfile
# ============================================================================
# Lightweight Runtime (Default)
# ============================================================================
FROM python:3.11-slim as runtime-base

# Install only system dependencies for base + ocr
RUN apt-get update && apt-get install -y \
    libgcc-s1 libstdc++6 \
    ca-certificates curl \
    tesseract-ocr tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r docsray && useradd -r -g docsray -d /app docsray

WORKDIR /app
COPY --chown=docsray:docsray . .

# Install base package only (minimal dependencies)
RUN pip install --no-cache-dir -e .

USER docsray
ENV PYTHONUNBUFFERED=1 \
    DOCSRAY_TRANSPORT="stdio"

CMD ["docsray", "start"]

# ============================================================================
# Lightweight + Remote AI (Recommended for most deployments)
# ============================================================================
FROM runtime-base as runtime-remote-ai

USER root
RUN pip install --no-cache-dir -e ".[remote-ai,ocr]"
USER docsray

# ============================================================================
# Full Local AI (GPU optional)
# ============================================================================
FROM runtime-base as runtime-local-ai

USER root
RUN pip install --no-cache-dir -e ".[local-ai,remote-ai,ocr]"
USER docsray

# ============================================================================
# Development
# ============================================================================
FROM runtime-base as development

USER root
RUN apt-get update && apt-get install -y git vim && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -e ".[dev,remote-ai,ocr]"
USER docsray

ENV DOCSRAY_LOG_LEVEL="DEBUG"
CMD ["docsray", "start", "--verbose"]
```

**Multi-stage Build Tags:**
- `docsray-mcp:latest` → runtime-base (minimal)
- `docsray-mcp:remote-ai` → runtime-remote-ai (recommended)
- `docsray-mcp:local-ai` → runtime-local-ai (GPU optional)
- `docsray-mcp:dev` → development

**Docker Compose for Coolify:**
```yaml
services:
  docsray-remote-ai:
    build:
      context: .
      target: runtime-remote-ai
    environment:
      - DOCSRAY_LLAMAPARSE_API_KEY=${DOCSRAY_LLAMAPARSE_API_KEY}
      - DOCSRAY_MISTRAL_API_KEY=${DOCSRAY_MISTRAL_API_KEY}
      - DOCSRAY_GOOGLE_API_KEY=${DOCSRAY_GOOGLE_API_KEY}
      - DOCSRAY_OPENROUTER_API_KEY=${DOCSRAY_OPENROUTER_API_KEY}
    restart: unless-stopped
```

#### 1.3 Fix Docker Build SSL Issues

**Solutions:**
1. **Add retry logic to pip install**
2. **Use pip trusted host flag for problematic builds**
3. **Add ARG for pip index URL** (allow custom PyPI mirrors)
4. **Pre-download wheel files** for critical dependencies (optional)

**Implementation:**
```dockerfile
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_TRUSTED_HOST=""

RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    --index-url ${PIP_INDEX_URL} \
    --retries 5 \
    --timeout 60
```

### Phase 2: Provider Classification and Capability Reporting

**Objective:** Enable dynamic capability discovery and proper provider classification.

#### 2.1 Enhance Provider Capability Reporting

**Add to `ProviderCapabilities` model:**
```python
class ResourceRequirements(BaseModel):
    """Resource requirements for a provider."""
    cpu: str = "low"  # low, medium, high
    memory: str = "low"  # low, medium, high  
    gpu: bool = False
    disk_space: str = "low"  # low, medium, high
    network: bool = False
    api_key_required: bool = False

class ProviderCapabilities(BaseModel):
    """Provider capability definition."""
    formats: List[str]
    features: Dict[str, bool]
    performance: Dict[str, Union[int, float]]
    
    # NEW FIELDS
    classification: str  # "local-pdf", "local-ocr", "local-ai", "remote-ai"
    resource_requirements: ResourceRequirements
    provider_type: str  # "local" or "remote"
```

#### 2.2 Classify Existing Providers

**Provider Classification Matrix:**

| Provider | Classification | Type | CPU | Memory | GPU | API Key | Network |
|----------|---------------|------|-----|--------|-----|---------|---------|
| PyMuPDF4LLM | `local-pdf` | local | low | low | No | No | No |
| PyTesseract | `local-ocr` | local | medium | low | No | No | No |
| OCRmyPDF | `local-ocr` | local | medium | medium | No | No | No |
| IBM.Docling | `local-ai` | local | high | high | Optional | No | No |
| MIMIC.DocsRay (RAG) | `local-ai` | local | high | high | Optional | No | No |
| LlamaParse | `remote-ai` | remote | low | low | No | Yes | Yes |
| Mistral AI | `remote-ai` | remote | low | low | No | Yes | Yes |
| Gemini | `remote-ai` | remote | low | low | No | Yes | Yes |
| OpenRouter | `remote-ai` | remote | low | low | No | Yes | Yes |

#### 2.3 Update Provider Registry Scoring

**Add classification-aware scoring:**
```python
def _score_provider(self, provider: DocumentProvider, document: Document, 
                    operation: str, preferred_type: Optional[str] = None) -> float:
    """Score provider with classification awareness."""
    score = 0.0
    caps = provider.get_capabilities()
    
    # Prefer remote providers in lightweight deployments
    if preferred_type == "remote" and caps.provider_type == "remote":
        score += 15.0
    elif preferred_type == "local" and caps.provider_type == "local":
        score += 15.0
    
    # Existing format and operation scoring...
    # ...
    
    return score
```

**Add configuration for preferred provider type:**
```python
class PerformanceConfig(BaseModel):
    cache_enabled: bool = Field(default=True)
    cache_ttl: int = Field(default=3600, ge=0)
    max_concurrent_requests: int = Field(default=10, ge=1)
    timeout_seconds: int = Field(default=120, ge=1)
    
    # NEW
    preferred_provider_type: Optional[str] = Field(
        default=None,
        description="Prefer 'local' or 'remote' providers when available"
    )
```

### Phase 3: Implement Missing Remote AI Providers

**Objective:** Add Gemini and OpenRouter providers for complete remote AI coverage.

#### 3.1 Implement Gemini Provider

**File:** `src/docsray/providers/gemini.py`

**Features:**
- Native PDF upload to Gemini API
- Multi-modal understanding (text + images)
- Custom instruction support
- Streaming responses
- Long context window (up to 1M tokens for Gemini 1.5 Pro)

**Configuration:**
```python
class GeminiConfig(BaseModel):
    enabled: bool = Field(default=False)
    api_key: Optional[str] = Field(default=None)
    model: str = Field(default="gemini-1.5-pro")
    max_output_tokens: int = Field(default=8192)
    temperature: float = Field(default=0.2)
```

**Environment Variables:**
```bash
DOCSRAY_GEMINI_ENABLED=true
DOCSRAY_GEMINI_API_KEY=your-api-key
DOCSRAY_GEMINI_MODEL=gemini-1.5-pro
```

**Implementation Checklist:**
- [ ] Add `google-generativeai>=0.3.0` to `remote-ai` extra
- [ ] Implement `GeminiProvider` class
- [ ] Add configuration to `config.py`
- [ ] Register in `server.py`
- [ ] Add tests for Gemini provider
- [ ] Update documentation

#### 3.2 Implement OpenRouter Provider

**File:** `src/docsray/providers/openrouter.py`

**Features:**
- Access to multiple AI models through single API
- Cost optimization (choose cheapest model for task)
- Fallback between models
- OpenAI-compatible API

**Configuration:**
```python
class OpenRouterConfig(BaseModel):
    enabled: bool = Field(default=False)
    api_key: Optional[str] = Field(default=None)
    base_url: str = Field(default="https://openrouter.ai/api/v1")
    model: str = Field(default="anthropic/claude-3-haiku")
    max_tokens: int = Field(default=4096)
    temperature: float = Field(default=0.2)
```

**Environment Variables:**
```bash
DOCSRAY_OPENROUTER_ENABLED=true
DOCSRAY_OPENROUTER_API_KEY=your-api-key
DOCSRAY_OPENROUTER_MODEL=anthropic/claude-3-haiku
```

**Implementation Checklist:**
- [ ] Add `openai>=1.0.0` to `remote-ai` extra
- [ ] Implement `OpenRouterProvider` class
- [ ] Add configuration to `config.py`
- [ ] Register in `server.py`
- [ ] Add tests for OpenRouter provider
- [ ] Update documentation

#### 3.3 Complete Mistral AI Provider Implementation

**Current Status:** Configuration exists but provider not fully implemented

**Tasks:**
- [ ] Verify Mistral OCR API integration
- [ ] Implement all required provider methods
- [ ] Add comprehensive tests
- [ ] Document Mistral-specific capabilities

### Phase 4: Storage Abstraction

**Objective:** Enable S3 and remote filesystem access for multi-agent deployments.

#### 4.1 Abstract Storage Layer

**File:** `src/docsray/storage/__init__.py`

**Storage Interface:**
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, BinaryIO

class DocumentStorage(ABC):
    """Abstract document storage interface."""
    
    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if document exists."""
        pass
    
    @abstractmethod
    async def read(self, path: str) -> bytes:
        """Read document bytes."""
        pass
    
    @abstractmethod
    async def write(self, path: str, data: bytes) -> None:
        """Write document bytes."""
        pass
    
    @abstractmethod
    async def list(self, prefix: str) -> List[str]:
        """List documents with prefix."""
        pass
    
    @abstractmethod
    async def delete(self, path: str) -> None:
        """Delete document."""
        pass
```

**Implementations:**

1. **Local Filesystem Storage** (`storage/local.py`)
   - Always available
   - No extra dependencies
   - Fast access

2. **S3 Storage** (`storage/s3.py`)
   - Requires `boto3`, `s3fs`
   - Shared storage between agents
   - Scalable

**Configuration:**
```python
class StorageConfig(BaseModel):
    type: str = Field(default="local")  # "local" or "s3"
    
    # S3 configuration
    s3_bucket: Optional[str] = None
    s3_prefix: Optional[str] = None
    s3_region: Optional[str] = None
    s3_endpoint: Optional[str] = None
    
    # Local configuration
    local_base_path: str = Field(default="./data")
```

**Environment Variables:**
```bash
DOCSRAY_STORAGE_TYPE=s3
DOCSRAY_S3_BUCKET=my-documents
DOCSRAY_S3_PREFIX=docsray/
DOCSRAY_S3_REGION=us-east-1
# AWS credentials via standard AWS env vars
```

#### 4.2 Update Document Fetching

**Modify `fetch.py` tool:**
- Use storage abstraction instead of direct filesystem
- Support `s3://bucket/key` URLs
- Maintain backward compatibility with local paths

**Example:**
```python
async def fetch_document(url: str, storage: DocumentStorage) -> Document:
    """Fetch document from URL or storage."""
    if url.startswith("s3://"):
        # Parse S3 URL and use S3 storage
        return await fetch_from_s3(url, storage)
    elif url.startswith("http://") or url.startswith("https://"):
        # Download and cache
        return await download_document(url, storage)
    else:
        # Local file or storage path
        return await storage.read(url)
```

### Phase 5: Configuration and Documentation

**Objective:** Provide clear setup documentation and environment templates.

#### 5.1 Comprehensive Environment Configuration

**Update `.env.example` with clear sections:**

```bash
# ===========================================
# CORE CONFIGURATION
# ===========================================
DOCSRAY_LOG_LEVEL=INFO
DOCSRAY_TRANSPORT_TYPE=stdio

# ===========================================
# STORAGE CONFIGURATION
# ===========================================
DOCSRAY_STORAGE_TYPE=local  # Options: local, s3
# DOCSRAY_S3_BUCKET=my-documents
# DOCSRAY_S3_PREFIX=docsray/
# DOCSRAY_S3_REGION=us-east-1

# ===========================================
# PROVIDER CONFIGURATION
# ===========================================

# PyMuPDF4LLM (Always enabled - local PDF processing)
DOCSRAY_PYMUPDF4LLM_ENABLED=true

# ===========================================
# REMOTE AI PROVIDERS (Lightweight)
# ===========================================

# LlamaParse - AI-powered document parsing
# Get API key: https://cloud.llamaindex.ai
DOCSRAY_LLAMAPARSE_ENABLED=false
DOCSRAY_LLAMAPARSE_API_KEY=llx-your-api-key-here

# Gemini - Google's multimodal AI
# Get API key: https://makersuite.google.com/app/apikey
DOCSRAY_GEMINI_ENABLED=false
DOCSRAY_GEMINI_API_KEY=your-gemini-api-key
DOCSRAY_GEMINI_MODEL=gemini-1.5-pro

# OpenRouter - Multiple models through one API
# Get API key: https://openrouter.ai/keys
DOCSRAY_OPENROUTER_ENABLED=false
DOCSRAY_OPENROUTER_API_KEY=your-openrouter-key
DOCSRAY_OPENROUTER_MODEL=anthropic/claude-3-haiku

# Mistral AI - OCR and analysis
# Get API key: https://console.mistral.ai/
DOCSRAY_MISTRAL_ENABLED=false
DOCSRAY_MISTRAL_API_KEY=your-mistral-api-key

# ===========================================
# LOCAL OCR PROVIDERS (CPU only)
# ===========================================

# PyTesseract - Traditional OCR
DOCSRAY_PYTESSERACT_ENABLED=false
DOCSRAY_PYTESSERACT_LANG=eng

# OCRmyPDF - Advanced OCR
DOCSRAY_OCRMYPDF_ENABLED=false

# ===========================================
# LOCAL AI PROVIDERS (GPU recommended)
# ===========================================

# IBM Docling - Advanced layout understanding
DOCSRAY_IBM_DOCLING_ENABLED=false
DOCSRAY_IBM_DOCLING_USE_VLM=true
DOCSRAY_IBM_DOCLING_DEVICE=cpu  # or cuda

# MIMIC DocsRay - Semantic search and RAG
DOCSRAY_MIMIC_ENABLED=false
DOCSRAY_MIMIC_RAG_ENABLED=true

# ===========================================
# PERFORMANCE TUNING
# ===========================================
DOCSRAY_CACHE_ENABLED=true
DOCSRAY_CACHE_TTL=3600
DOCSRAY_PREFERRED_PROVIDER_TYPE=remote  # Options: local, remote, auto
```

#### 5.2 API Key Setup Documentation

**Create:** `docs/setup/api-keys.md`

**Sections:**
1. **LlamaParse Setup**
   - Link to signup page
   - Free tier details
   - API key location
   - Environment variable setup

2. **Google Gemini Setup**
   - Link to Google AI Studio
   - API key creation
   - Free tier quotas
   - Model selection guide

3. **OpenRouter Setup**
   - Account creation
   - API key generation
   - Credit purchase
   - Model selection and pricing

4. **Mistral AI Setup**
   - Console access
   - API key generation
   - Pricing information

#### 5.3 Coolify Deployment Guide

**Create:** `docs/deployment/coolify.md`

**Contents:**
1. **Prerequisites**
   - Coolify installation
   - Docker access
   - Environment variables

2. **Deployment Steps**
   - Repository connection
   - Build configuration
   - Environment variable setup
   - Health check configuration

3. **Recommended Configuration**
   - Use `remote-ai` Docker image
   - Set API keys as secrets
   - Configure resource limits
   - Enable auto-restart

**Example Coolify Configuration:**
```yaml
version: '3.8'

services:
  docsray:
    build:
      context: https://github.com/xingh/docsray-mcp.git
      dockerfile: Dockerfile
      target: runtime-remote-ai
    environment:
      DOCSRAY_LLAMAPARSE_API_KEY: ${DOCSRAY_LLAMAPARSE_API_KEY}
      DOCSRAY_GEMINI_API_KEY: ${DOCSRAY_GEMINI_API_KEY}
      DOCSRAY_OPENROUTER_API_KEY: ${DOCSRAY_OPENROUTER_API_KEY}
      DOCSRAY_TRANSPORT_TYPE: stdio
      DOCSRAY_LOG_LEVEL: INFO
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

#### 5.4 Installation Guide Updates

**Update:** `README.md`, `docs/quickstart.md`

**Add sections:**
1. **Installation Options**
   - Minimal (local PDF only)
   - Lightweight (remote AI)
   - Full local (GPU)
   - Full (everything)

2. **Docker Installation Options**
   - Base image (minimal)
   - Remote AI image (recommended)
   - Local AI image (GPU)
   - Development image

**Example:**
```bash
# Minimal installation (local PDF processing only)
pip install docsray-mcp

# Lightweight with remote AI (recommended)
pip install "docsray-mcp[remote-ai,ocr]"

# Full local with GPU acceleration
pip install "docsray-mcp[local-ai-gpu,remote-ai,ocr]"

# Docker - lightweight remote AI
docker pull docsray/docsray-mcp:remote-ai
docker run -e DOCSRAY_LLAMAPARSE_API_KEY=xxx docsray/docsray-mcp:remote-ai
```

### Phase 6: Testing and Validation

**Objective:** Ensure all refactored components work correctly.

#### 6.1 Docker Build Tests

**Test Matrix:**
- [ ] Base image builds successfully
- [ ] Remote AI image builds successfully
- [ ] Local AI image builds successfully
- [ ] Development image builds successfully
- [ ] All images run without errors
- [ ] Environment variables are properly loaded
- [ ] SSL certificate issues are resolved

#### 6.2 Provider Tests

**Test Coverage:**
- [ ] PyMuPDF4LLM works in base image
- [ ] LlamaParse works with API key
- [ ] Gemini provider integration
- [ ] OpenRouter provider integration
- [ ] Mistral AI provider completion
- [ ] IBM Docling in local-ai image
- [ ] MIMIC DocsRay in local-ai image

#### 6.3 Tool Tests

**Validate all tools work with:**
- [ ] Local PDF provider
- [ ] Remote AI providers
- [ ] Local AI providers
- [ ] Mixed provider scenarios

#### 6.4 Integration Tests

**End-to-end scenarios:**
- [ ] Lightweight deployment (remote AI only)
- [ ] Full local deployment (GPU enabled)
- [ ] Hybrid deployment (local + remote)
- [ ] Coolify deployment
- [ ] S3 storage integration

### Phase 7: Migration and Deprecation

**Objective:** Handle backward compatibility and migration.

#### 7.1 Backward Compatibility

**Maintain compatibility for:**
- Existing environment variables
- Old Docker image tags
- Previous provider names

**Deprecation warnings for:**
- `ai` extra → Use `remote-ai` or `local-ai`
- Unnamed Docker tags → Use explicit tags

#### 7.2 Migration Guide

**Create:** `docs/migration/v0.6-to-v0.7.md`

**Sections:**
1. **Dependency Changes**
   - Old vs new extras
   - Migration commands

2. **Environment Variable Changes**
   - Deprecated variables
   - New variables
   - Backward compatibility period

3. **Docker Image Changes**
   - New tag structure
   - Recommended tags per use case

---

## Implementation Roadmap

### Priority 1: Critical (Blocking Issues) - Week 1

**Fixes Docker builds and enables lightweight deployment**

- [ ] **Task 1.1:** Restructure `pyproject.toml` optional dependencies
  - Split `ai` into `remote-ai` and `local-ai`
  - Add `storage` extra
  - Create convenience bundles
  - **Estimated time:** 2 hours
  - **Complexity:** Low
  - **Impact:** High

- [ ] **Task 1.2:** Fix Dockerfile SSL issues and create multi-stage builds
  - Add retry logic
  - Create `runtime-base`, `runtime-remote-ai`, `runtime-local-ai` stages
  - Test all stages build successfully
  - **Estimated time:** 4 hours
  - **Complexity:** Medium
  - **Impact:** High

- [ ] **Task 1.3:** Update `.env.example` with new structure
  - Clear section organization
  - Add API key URLs
  - Document all providers
  - **Estimated time:** 1 hour
  - **Complexity:** Low
  - **Impact:** Medium

- [ ] **Task 1.4:** Test Docker builds locally and in CI
  - Validate all stages
  - Fix any remaining SSL issues
  - **Estimated time:** 2 hours
  - **Complexity:** Medium
  - **Impact:** High

**Deliverables:**
- ✅ Docker builds succeed locally and in CI
- ✅ Lightweight base image (~200MB)
- ✅ Remote AI image (~300MB)
- ✅ Clear dependency classification

### Priority 2: Provider Enhancement - Week 2

**Adds missing remote AI providers and improves capability reporting**

- [ ] **Task 2.1:** Enhance `ProviderCapabilities` model
  - Add `classification` field
  - Add `resource_requirements` model
  - Add `provider_type` field
  - **Estimated time:** 2 hours
  - **Complexity:** Low
  - **Impact:** Medium

- [ ] **Task 2.2:** Update all existing providers with new capabilities
  - PyMuPDF4LLM → `local-pdf`
  - LlamaParse → `remote-ai`
  - IBM.Docling → `local-ai`
  - MIMIC.DocsRay → `local-ai`
  - **Estimated time:** 3 hours
  - **Complexity:** Medium
  - **Impact:** Medium

- [ ] **Task 2.3:** Implement Gemini provider
  - Create `gemini.py`
  - Add configuration
  - Implement all required methods
  - Add tests
  - **Estimated time:** 8 hours
  - **Complexity:** High
  - **Impact:** High

- [ ] **Task 2.4:** Implement OpenRouter provider
  - Create `openrouter.py`
  - Add configuration
  - Implement all required methods
  - Add tests
  - **Estimated time:** 6 hours
  - **Complexity:** Medium
  - **Impact:** High

- [ ] **Task 2.5:** Complete Mistral AI provider
  - Verify implementation
  - Add missing methods
  - Add tests
  - **Estimated time:** 4 hours
  - **Complexity:** Medium
  - **Impact:** Medium

**Deliverables:**
- ✅ 3 new remote AI providers (Gemini, OpenRouter, Mistral complete)
- ✅ Enhanced capability reporting
- ✅ Classification-aware provider selection

### Priority 3: Storage Abstraction - Week 3

**Enables S3 and shared storage for multi-agent deployments**

- [ ] **Task 3.1:** Create storage abstraction layer
  - Define `DocumentStorage` interface
  - Implement `LocalStorage`
  - **Estimated time:** 4 hours
  - **Complexity:** Medium
  - **Impact:** Medium

- [ ] **Task 3.2:** Implement S3 storage
  - Create `S3Storage` class
  - Add boto3 integration
  - Add tests
  - **Estimated time:** 6 hours
  - **Complexity:** High
  - **Impact:** Medium

- [ ] **Task 3.3:** Update fetch tool with storage abstraction
  - Support `s3://` URLs
  - Maintain backward compatibility
  - Add tests
  - **Estimated time:** 4 hours
  - **Complexity:** Medium
  - **Impact:** Medium

- [ ] **Task 3.4:** Add storage configuration
  - Environment variables
  - Configuration models
  - Documentation
  - **Estimated time:** 2 hours
  - **Complexity:** Low
  - **Impact:** Low

**Deliverables:**
- ✅ S3 storage support
- ✅ Shared storage between agents
- ✅ Backward compatible with local storage

### Priority 4: Documentation - Week 4

**Comprehensive setup and deployment guides**

- [ ] **Task 4.1:** Create API key setup guide
  - LlamaParse setup
  - Gemini setup
  - OpenRouter setup
  - Mistral AI setup
  - **Estimated time:** 3 hours
  - **Complexity:** Low
  - **Impact:** High

- [ ] **Task 4.2:** Create Coolify deployment guide
  - Prerequisites
  - Step-by-step setup
  - Example configurations
  - Troubleshooting
  - **Estimated time:** 4 hours
  - **Complexity:** Medium
  - **Impact:** High

- [ ] **Task 4.3:** Update installation documentation
  - New installation options
  - Docker image variants
  - Use case recommendations
  - **Estimated time:** 2 hours
  - **Complexity:** Low
  - **Impact:** Medium

- [ ] **Task 4.4:** Create migration guide
  - v0.6 to v0.7 changes
  - Dependency migration
  - Environment variable changes
  - **Estimated time:** 2 hours
  - **Complexity:** Low
  - **Impact:** Medium

**Deliverables:**
- ✅ Complete API key setup documentation
- ✅ Coolify deployment guide
- ✅ Updated installation guides
- ✅ Migration documentation

### Priority 5: Testing and Validation - Ongoing

**Continuous validation throughout implementation**

- [ ] **Task 5.1:** Docker build tests
  - All stages build successfully
  - Images run without errors
  - Size optimization verified
  - **Estimated time:** Ongoing
  - **Complexity:** Low
  - **Impact:** High

- [ ] **Task 5.2:** Provider integration tests
  - Each provider tested independently
  - Multi-provider scenarios
  - Fallback behavior
  - **Estimated time:** Ongoing
  - **Complexity:** Medium
  - **Impact:** High

- [ ] **Task 5.3:** End-to-end deployment tests
  - Lightweight deployment
  - Full local deployment
  - Coolify deployment
  - S3 storage integration
  - **Estimated time:** Ongoing
  - **Complexity:** High
  - **Impact:** High

**Deliverables:**
- ✅ All tests passing
- ✅ CI/CD validation
- ✅ Deployment verification

---

## Success Metrics

### Performance Metrics

1. **Docker Image Sizes:**
   - Base image: < 200MB (target: ~150MB)
   - Remote AI image: < 300MB (target: ~250MB)
   - Local AI image: < 2GB (target: ~1.5GB)

2. **Build Times:**
   - Base image: < 2 minutes
   - Remote AI image: < 3 minutes
   - Local AI image: < 10 minutes

3. **Memory Usage:**
   - Base: < 100MB idle
   - Remote AI: < 150MB idle
   - Local AI: < 500MB idle (CPU), < 2GB (GPU)

### Stability Metrics

1. **Docker Build Success Rate:**
   - Local builds: 100%
   - CI/CD builds: 100%
   - Fresh environment builds: 100%

2. **Provider Initialization:**
   - Graceful degradation when API keys missing
   - No crashes on import errors
   - Clear error messages

### Reliability Metrics

1. **API Coverage:**
   - All 7 tools work with remote AI providers
   - All 7 tools work with local providers
   - Proper fallback between providers

2. **Error Handling:**
   - Network failures handled gracefully
   - API rate limits respected
   - Timeout handling

### Accuracy Metrics

1. **Capability Reporting:**
   - 100% accurate provider classification
   - Correct resource requirement reporting
   - Proper feature flags

2. **Provider Selection:**
   - Correct provider chosen for document type
   - Preference settings respected
   - Fallback logic correct

### Economic Metrics

1. **API Cost Optimization:**
   - Proper caching reduces redundant calls
   - Cheapest suitable provider selected
   - User can control provider preference

2. **Resource Efficiency:**
   - Minimal CPU/memory in lightweight mode
   - GPU only used when enabled
   - No unnecessary downloads

---

## Risk Mitigation

### Risk 1: Breaking Changes for Existing Users

**Mitigation:**
- Maintain backward compatibility for environment variables
- Deprecation warnings instead of immediate removal
- Comprehensive migration guide
- Old package extras still work (with warnings)

### Risk 2: Docker Build Failures in New Environments

**Mitigation:**
- Multiple PyPI mirror support
- Retry logic with exponential backoff
- Pre-built wheels for critical dependencies (optional)
- Clear troubleshooting documentation

### Risk 3: Provider Implementation Complexity

**Mitigation:**
- Start with Gemini (most straightforward)
- Leverage existing LlamaParse patterns
- Comprehensive testing at each step
- Fallback to existing providers if issues

### Risk 4: S3 Storage Adoption Challenges

**Mitigation:**
- S3 completely optional
- Local storage remains default
- Clear setup documentation
- Example configurations provided

### Risk 5: Performance Regression

**Mitigation:**
- Benchmark before and after changes
- Maintain existing provider selection logic
- Caching strategies unchanged
- Comprehensive performance testing

---

## Dependencies and Blockers

### External Dependencies

1. **PyPI Package Availability:**
   - `google-generativeai` - ✅ Available
   - `openai` - ✅ Available
   - `boto3` - ✅ Available

2. **API Access:**
   - Gemini API - ✅ Available (free tier exists)
   - OpenRouter API - ✅ Available (paid, free tier minimal)
   - LlamaParse API - ✅ Available (free tier exists)

### Internal Dependencies

1. **Provider Interface:**
   - Must maintain compatibility with existing providers
   - New capability fields must be optional

2. **MCP Protocol:**
   - No changes required to MCP protocol
   - All changes internal to Docsray

### Potential Blockers

1. **Docker Build Environment:**
   - SSL certificate issues in CI/CD
   - **Mitigation:** Retry logic, trusted hosts

2. **API Rate Limits:**
   - Free tier limitations during testing
   - **Mitigation:** Use mocks for CI tests, manual integration tests

3. **GPU Testing:**
   - Local AI testing requires GPU access
   - **Mitigation:** CPU fallback, community testing

---

## Post-Refactor Maintenance

### Version Management

**Semantic Versioning:**
- v0.7.0 - Major refactor release
- v0.7.x - Bug fixes and minor improvements
- v0.8.0 - Next feature release (S3 storage)

### Deprecation Schedule

**v0.7.0 (Refactor release):**
- Mark `ai` extra as deprecated (warnings)
- Old environment variables still work

**v0.8.0 (6 months later):**
- Remove `ai` extra
- Migrate all usage to `remote-ai` / `local-ai`

**v1.0.0 (1 year later):**
- Remove old environment variable compatibility
- Clean deprecation notices

### Documentation Maintenance

**Regular Updates:**
- API key setup guides (quarterly)
- Provider comparison matrix (as providers added)
- Performance benchmarks (each release)
- Example configurations (as needed)

### Community Engagement

**Feedback Channels:**
- GitHub issues for bugs and features
- Discussions for questions and ideas
- Examples repository for community contributions

---

## Appendix

### A. Provider Comparison Matrix

| Feature | PyMuPDF | PyTess | Docling | MIMIC | LlamaParse | Gemini | OpenRouter | Mistral |
|---------|---------|---------|---------|-------|------------|--------|------------|---------|
| **Type** | Local | Local | Local | Local | Remote | Remote | Remote | Remote |
| **Classification** | local-pdf | local-ocr | local-ai | local-ai | remote-ai | remote-ai | remote-ai | remote-ai |
| **API Key** | No | No | No | No | Yes | Yes | Yes | Yes |
| **GPU** | No | No | Optional | Optional | No | No | No | No |
| **Tables** | Basic | No | Advanced | Advanced | Advanced | Advanced | Advanced | Advanced |
| **OCR** | No | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| **Entities** | No | No | Yes | Yes | Yes | Yes | Yes | Yes |
| **Custom Instructions** | No | No | No | Yes | Yes | Yes | Yes | Yes |
| **Cost** | Free | Free | Free | Free | Paid | Paid | Paid | Paid |
| **Speed** | Fast | Slow | Medium | Medium | Medium | Fast | Fast | Fast |
| **Accuracy** | Good | Medium | Excellent | Excellent | Excellent | Excellent | Excellent | Excellent |

### B. Capability Classification Examples

**Local PDF:**
```python
{
    "classification": "local-pdf",
    "provider_type": "local",
    "resource_requirements": {
        "cpu": "low",
        "memory": "low",
        "gpu": False,
        "network": False,
        "api_key_required": False
    }
}
```

**Remote AI:**
```python
{
    "classification": "remote-ai",
    "provider_type": "remote",
    "resource_requirements": {
        "cpu": "low",
        "memory": "low",
        "gpu": False,
        "network": True,
        "api_key_required": True
    }
}
```

**Local AI:**
```python
{
    "classification": "local-ai",
    "provider_type": "local",
    "resource_requirements": {
        "cpu": "high",
        "memory": "high",
        "gpu": True,  # optional but recommended
        "network": False,
        "api_key_required": False
    }
}
```

### C. Environment Variable Reference

**Complete list of all environment variables after refactor:**

```bash
# Core
DOCSRAY_LOG_LEVEL=INFO
DOCSRAY_TRANSPORT_TYPE=stdio
DOCSRAY_HTTP_PORT=3000

# Storage
DOCSRAY_STORAGE_TYPE=local
DOCSRAY_S3_BUCKET=
DOCSRAY_S3_PREFIX=
DOCSRAY_S3_REGION=

# Performance
DOCSRAY_CACHE_ENABLED=true
DOCSRAY_CACHE_TTL=3600
DOCSRAY_PREFERRED_PROVIDER_TYPE=auto

# PyMuPDF4LLM (local-pdf)
DOCSRAY_PYMUPDF4LLM_ENABLED=true

# PyTesseract (local-ocr)
DOCSRAY_PYTESSERACT_ENABLED=false
DOCSRAY_PYTESSERACT_LANG=eng

# OCRmyPDF (local-ocr)
DOCSRAY_OCRMYPDF_ENABLED=false

# IBM Docling (local-ai)
DOCSRAY_IBM_DOCLING_ENABLED=false
DOCSRAY_IBM_DOCLING_USE_VLM=true
DOCSRAY_IBM_DOCLING_DEVICE=cpu

# MIMIC DocsRay (local-ai)
DOCSRAY_MIMIC_ENABLED=false
DOCSRAY_MIMIC_RAG_ENABLED=true

# LlamaParse (remote-ai)
DOCSRAY_LLAMAPARSE_ENABLED=false
DOCSRAY_LLAMAPARSE_API_KEY=

# Gemini (remote-ai)
DOCSRAY_GEMINI_ENABLED=false
DOCSRAY_GEMINI_API_KEY=
DOCSRAY_GEMINI_MODEL=gemini-1.5-pro

# OpenRouter (remote-ai)
DOCSRAY_OPENROUTER_ENABLED=false
DOCSRAY_OPENROUTER_API_KEY=
DOCSRAY_OPENROUTER_MODEL=anthropic/claude-3-haiku

# Mistral AI (remote-ai)
DOCSRAY_MISTRAL_ENABLED=false
DOCSRAY_MISTRAL_API_KEY=
```

### D. Docker Compose Examples

**Lightweight (Remote AI):**
```yaml
version: '3.8'
services:
  docsray:
    image: docsray-mcp:remote-ai
    environment:
      - DOCSRAY_LLAMAPARSE_API_KEY=${LLAMAPARSE_KEY}
      - DOCSRAY_GEMINI_API_KEY=${GEMINI_KEY}
    volumes:
      - ./documents:/app/data
    restart: unless-stopped
```

**Full Stack (Local + Remote AI):**
```yaml
version: '3.8'
services:
  docsray:
    image: docsray-mcp:local-ai
    environment:
      - DOCSRAY_IBM_DOCLING_ENABLED=true
      - DOCSRAY_IBM_DOCLING_DEVICE=cuda
      - DOCSRAY_LLAMAPARSE_API_KEY=${LLAMAPARSE_KEY}
    volumes:
      - ./documents:/app/data
      - ./models:/app/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### E. API Cost Estimates (as of 2025-10-27)

| Provider | Free Tier | Pricing | Best For |
|----------|-----------|---------|----------|
| LlamaParse | 1,000 pages/day | $0.003/page | Complex layouts |
| Gemini | 15 RPM free | $0.00025/1k chars | Large documents |
| OpenRouter | Minimal | Varies by model | Model flexibility |
| Mistral | No free tier | $0.25/1M tokens | OCR tasks |

**Cost Optimization Tips:**
1. Use PyMuPDF4LLM for simple PDFs (free)
2. Cache aggressively to avoid redundant calls
3. Use cheapest suitable model via OpenRouter
4. Consider local-ai for high-volume processing

---

## Conclusion

This refactoring plan transforms Docsray into a flexible, lightweight system that can be deployed anywhere from resource-constrained containers to GPU-accelerated servers. The clear separation of **local** and **remote** capabilities, combined with proper Docker image stratification, enables users to choose the right balance of cost, performance, and resource usage for their specific needs.

**Key Benefits:**
- ✅ Docker builds succeed reliably
- ✅ Lightweight deployment option (< 300MB)
- ✅ Clear capability classification
- ✅ Multiple remote AI provider options
- ✅ Optional GPU acceleration
- ✅ S3 storage for multi-agent deployments
- ✅ Comprehensive documentation

**Implementation Timeline:** 4 weeks  
**Estimated Effort:** ~80 hours  
**Risk Level:** Low (backward compatible)  
**Impact:** High (enables all deployment scenarios)

---

**Prepared by:** GitHub Copilot  
**Review Status:** Pending  
**Approval Status:** Pending  
**Implementation Start:** TBD
