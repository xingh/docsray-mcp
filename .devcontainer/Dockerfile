# Development Container for Docsray MCP Server
# Includes Claude Desktop and full development environment

FROM python:3.11-slim

# Set build arguments
ARG USERNAME=docsray
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y install --no-install-recommends \
    # Essential development tools
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    curl \
    wget \
    unzip \
    # Python development
    python3-dev \
    python3-pip \
    # OCR and document processing
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libimage-exiftool-perl \
    # Image processing libraries
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    # System utilities
    htop \
    tree \
    jq \
    vim \
    nano \
    # X11 and GUI support for Claude Desktop
    xvfb \
    x11-apps \
    x11-utils \
    x11-xserver-utils \
    dbus-x11 \
    # Audio support
    pulseaudio \
    # Networking
    ca-certificates \
    gnupg \
    lsb-release \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (for some development tools)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install Claude Desktop
RUN wget -O /tmp/claude-desktop.deb "https://storage.googleapis.com/anthropic-cdn/claude-desktop/claude-desktop_1.0.0_amd64.deb" && \
    dpkg -i /tmp/claude-desktop.deb || true && \
    apt-get update && \
    apt-get -f install -y && \
    rm /tmp/claude-desktop.deb

# Set up Python virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install common development tools
RUN pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel \
    # Development and debugging tools
    ipython \
    jupyter \
    notebook \
    # Code quality tools
    black \
    ruff \
    mypy \
    pre-commit \
    # Testing tools
    pytest \
    pytest-asyncio \
    pytest-cov \
    pytest-mock \
    # Documentation tools
    sphinx \
    mkdocs \
    mkdocs-material

# Switch to the development user
USER $USERNAME

# Set working directory
WORKDIR /app

# Create directories
RUN mkdir -p /home/$USERNAME/.local/share/Claude \
    && mkdir -p /home/$USERNAME/.config \
    && mkdir -p /app/cache \
    && mkdir -p /app/logs \
    && mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    DOCSRAY_CACHE_DIR="/app/cache" \
    DOCSRAY_LOG_LEVEL="DEBUG" \
    # Display for GUI applications
    DISPLAY=:99 \
    # Claude Desktop configuration
    CLAUDE_CONFIG_PATH="/home/$USERNAME/.config/Claude"

# Copy and set up the project (this will be overridden by mount in devcontainer)
COPY --chown=$USERNAME:$USERNAME . .

# Install the project in development mode
RUN pip install --no-cache-dir -e ".[dev,ocr,ai]"

# Default command
CMD ["bash"]