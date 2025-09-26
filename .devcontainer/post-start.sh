#!/bin/bash

# Post-start script for Docsray MCP Server devcontainer
# Runs every time the container starts

set -e

echo "🔄 Starting Docsray MCP Server development environment..."

# Ensure we're in the right directory
cd /app

# Start virtual display for GUI applications (Claude Desktop)
echo "🖥️  Starting virtual display..."
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# Start PulseAudio for audio support
echo "🔊 Starting PulseAudio..."
pulseaudio --start --exit-idle-time=-1 &

# Ensure cache and log directories exist and have proper permissions
echo "📁 Ensuring directories exist..."
mkdir -p cache logs data
chmod 755 cache logs data

# Check if environment variables are set
echo "🔍 Checking environment configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file found"
    # Source the .env file to load environment variables
    set -a
    source .env
    set +a
else
    echo "⚠️  No .env file found. Using default configuration."
fi

# Display current configuration
echo ""
echo "📊 Current Docsray MCP Server configuration:"
echo "  • Log Level: ${DOCSRAY_LOG_LEVEL:-INFO}"
echo "  • Transport: ${DOCSRAY_TRANSPORT:-stdio}"
echo "  • Cache Enabled: ${DOCSRAY_CACHE_ENABLED:-true}"
echo "  • PyMuPDF Enabled: ${DOCSRAY_PYMUPDF_ENABLED:-true}"
echo "  • Tesseract Enabled: ${DOCSRAY_PYTESSERACT_ENABLED:-false}"

# Check if API keys are configured
echo ""
echo "🔑 API Keys status:"
if [ -n "${DOCSRAY_LLAMAPARSE_API_KEY:-}" ]; then
    echo "  • LlamaParse: ✅ Configured"
else
    echo "  • LlamaParse: ❌ Not configured"
fi

if [ -n "${DOCSRAY_MISTRAL_API_KEY:-}" ]; then
    echo "  • Mistral: ✅ Configured"
else
    echo "  • Mistral: ❌ Not configured"
fi

# Test the installation
echo ""
echo "🧪 Testing Docsray MCP Server installation..."
if command -v docsray &> /dev/null; then
    echo "✅ docsray command is available"
    docsray --version
else
    echo "❌ docsray command not found"
fi

# Check if Claude Desktop is available
echo ""
echo "🤖 Checking Claude Desktop availability..."
if command -v claude-desktop &> /dev/null; then
    echo "✅ Claude Desktop is installed"
    echo "  • Start with: claude-desktop"
    echo "  • Configuration: ~/.config/Claude/claude_desktop_config.json"
else
    echo "❌ Claude Desktop not found"
fi

echo ""
echo "🎯 Development environment ready!"
echo ""
echo "💡 Quick commands:"
echo "  • Test MCP server: docsray start --verbose"
echo "  • Run in HTTP mode: docsray start --transport http --port 3000 --verbose"
echo "  • Open Claude Desktop: claude-desktop &"
echo ""