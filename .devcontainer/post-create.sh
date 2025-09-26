#!/bin/bash

# Post-create script for Docsray MCP Server devcontainer
# Runs once after the container is created

set -e

echo "🚀 Setting up Docsray MCP Server development environment..."

# Ensure we're in the right directory
cd /app

# Install the project in development mode with all optional dependencies
echo "📦 Installing Docsray MCP Server in development mode..."
pip install -e ".[dev,ocr,ai]"

# Set up pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
pre-commit install || echo "⚠️  Pre-commit hooks setup failed (this is optional)"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p cache logs data
mkdir -p ~/.local/share/Claude
mkdir -p ~/.config/Claude

# Set up Claude Desktop configuration directory
echo "🤖 Setting up Claude Desktop configuration..."
CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
mkdir -p "$CLAUDE_CONFIG_DIR"

# Create a sample Claude Desktop configuration for MCP
cat > "$CLAUDE_CONFIG_DIR/claude_desktop_config.json" << 'EOF'
{
  "mcpServers": {
    "docsray": {
      "command": "docsray",
      "args": ["start"],
      "env": {
        "DOCSRAY_PYMUPDF_ENABLED": "true",
        "DOCSRAY_LOG_LEVEL": "DEBUG",
        "DOCSRAY_CACHE_ENABLED": "true"
      }
    }
  }
}
EOF

echo "✅ Claude Desktop MCP configuration created at: $CLAUDE_CONFIG_DIR/claude_desktop_config.json"

# Set up environment file from example
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please update it with your API keys if needed."
fi

# Install additional development tools
echo "🛠️  Installing additional development tools..."
npm install -g @anthropic-ai/mcp-cli || echo "⚠️  MCP CLI installation failed (optional)"

# Run tests to ensure everything is working
echo "🧪 Running initial tests..."
python -m pytest tests/ --tb=short -v || echo "⚠️  Some tests failed, but this is expected in development"

# Display useful information
echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Quick start commands:"
echo "  • Start MCP server (stdio): docsray start"
echo "  • Start MCP server (HTTP):  docsray start --transport http --port 3000"
echo "  • Run tests:                pytest"
echo "  • Format code:              black src/ tests/"
echo "  • Lint code:                ruff check src/ tests/"
echo "  • Type check:               mypy src/"
echo ""
echo "🤖 Claude Desktop:"
echo "  • Configuration: ~/.config/Claude/claude_desktop_config.json"
echo "  • Start Claude Desktop with: claude-desktop"
echo "  • The MCP server is pre-configured in Claude Desktop"
echo ""
echo "🔧 Development tips:"
echo "  • Use 'docsray start --verbose' for detailed logging"
echo "  • Check logs in ./logs/ directory"
echo "  • Cache is stored in ./cache/ directory"
echo "  • Test documents can be placed in ./data/ directory"
echo ""