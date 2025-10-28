# Multi-stage Dockerfile for Docsray MCP Server
# Best practices for containerized MCP servers

# ============================================================================
# Build stage
# ============================================================================
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILDPLATFORM
ARG TARGETPLATFORM
ARG TARGETARCH

# Install system dependencies required for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy dependency files first (for better caching)
COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE ./
COPY src/ ./src/

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e .

# ============================================================================
# Runtime stage
# ============================================================================
FROM python:3.11-slim as runtime

# Set metadata labels
LABEL org.opencontainers.image.title="Docsray MCP Server"
LABEL org.opencontainers.image.description="AI-powered document perception and analysis MCP server"
LABEL org.opencontainers.image.version="0.3.3"
LABEL org.opencontainers.image.authors="Docsray Team <team@docsray.dev>"
LABEL org.opencontainers.image.url="https://docsray.dev"
LABEL org.opencontainers.image.source="https://github.com/xingh/docsray-mcp"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    # Essential runtime libraries
    libgcc-s1 \
    libstdc++6 \
    # OCR dependencies (optional)
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    # Image processing
    libimage-exiftool-perl \
    # Networking and security
    ca-certificates \
    curl \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r docsray && useradd -r -g docsray -d /app -s /bin/bash docsray

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory and copy source code
WORKDIR /app
COPY --chown=docsray:docsray . .

# Install the package in the runtime environment
RUN pip install --no-cache-dir -e .

# Create directories for data and cache
RUN mkdir -p /app/data /app/cache /app/logs && \
    chown -R docsray:docsray /app

# Switch to non-root user
USER docsray

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    DOCSRAY_CACHE_DIR="/app/cache" \
    DOCSRAY_LOG_LEVEL="INFO" \
    DOCSRAY_TRANSPORT="stdio"

# Expose port for HTTP mode (if needed)
EXPOSE 3000

# Health check for HTTP mode
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Default command - can be overridden
CMD ["docsray", "start"]

# ============================================================================
# Development stage (optional)
# ============================================================================
FROM runtime as development

# Switch back to root to install dev dependencies
USER root

# Install development tools
RUN apt-get update && apt-get install -y \
    git \
    vim \
    nano \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir -e ".[dev,ocr,ai]"

# Switch back to docsray user
USER docsray

# Override for development
ENV DOCSRAY_LOG_LEVEL="DEBUG"
CMD ["docsray", "start", "--verbose"]
