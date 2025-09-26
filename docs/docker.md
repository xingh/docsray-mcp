# Docker Guide for Docsray MCP Server

This guide covers how to run Docsray MCP Server using Docker and Docker Compose, including development container setup.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/xingh/docsray-mcp
cd docsray-mcp

# Start the MCP server in stdio mode
docker-compose up docsray-mcp

# Or start in HTTP mode
docker-compose up docsray-http
```

### Using Docker directly

```bash
# Build the image
docker build -t docsray-mcp .

# Run in stdio mode (for Claude Desktop)
docker run -it --rm docsray-mcp

# Run in HTTP mode
docker run -it --rm -p 3000:3000 -e DOCSRAY_TRANSPORT=http docsray-mcp
```

## Configuration

### Environment Variables

The Docker container supports all standard Docsray environment variables:

```bash
# Core configuration
DOCSRAY_TRANSPORT=stdio|http
DOCSRAY_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
DOCSRAY_CACHE_ENABLED=true|false

# Provider configuration
DOCSRAY_PYMUPDF_ENABLED=true|false
DOCSRAY_PYTESSERACT_ENABLED=true|false
DOCSRAY_LLAMAPARSE_ENABLED=true|false
DOCSRAY_MISTRAL_ENABLED=true|false

# API keys (if using AI providers)
DOCSRAY_LLAMAPARSE_API_KEY=your-key
DOCSRAY_MISTRAL_API_KEY=your-key

# HTTP configuration
DOCSRAY_HTTP_HOST=0.0.0.0
DOCSRAY_HTTP_PORT=3000
```

### Using Environment Files

Create a `.env` file in your project directory:

```bash
# Copy the example
cp .env.example .env

# Edit with your configuration
nano .env
```

Then use it with Docker Compose:

```bash
docker-compose --env-file .env up
```

## Production Deployment

### Docker Compose Production Setup

```yaml
version: '3.8'
services:
  docsray-mcp:
    image: docsray-mcp:latest
    restart: unless-stopped
    environment:
      - DOCSRAY_TRANSPORT=stdio
      - DOCSRAY_LOG_LEVEL=INFO
      - DOCSRAY_PYMUPDF_ENABLED=true
    volumes:
      - docsray-cache:/app/cache
      - docsray-logs:/app/logs
    stdin_open: true
    tty: true

volumes:
  docsray-cache:
  docsray-logs:
```

### Health Checks

The Docker image includes health checks for HTTP mode:

```bash
# Check health status
docker ps  # Look for "healthy" status

# View health check logs
docker inspect --format='{{json .State.Health}}' container_name
```

## Development with Docker

### Development Container

The project includes a full development container setup:

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up docsray-dev

# With Jupyter notebook
docker-compose -f docker-compose.dev.yml --profile jupyter up

# With Redis caching
docker-compose -f docker-compose.dev.yml --profile redis up

# Run tests
docker-compose -f docker-compose.dev.yml --profile test up test-docs
```

### VS Code DevContainer

The project includes a complete VS Code devcontainer setup:

1. Install the "Dev Containers" extension in VS Code
2. Open the project folder
3. Click "Reopen in Container" when prompted
4. VS Code will build and start the development container

The devcontainer includes:
- Full Python development environment
- Claude Desktop pre-installed and configured
- All development tools (pytest, black, ruff, mypy)
- Pre-configured VS Code extensions
- Automatic MCP server configuration for Claude Desktop

### Development Features

- **Hot Reload**: Source code changes are automatically reflected
- **Debug Support**: Debug port 5678 is exposed for remote debugging
- **Jupyter Integration**: Optional Jupyter notebook server
- **Redis Caching**: Optional Redis for advanced caching scenarios
- **Test Runner**: Automated test execution in container

## Container Architecture

### Multi-stage Build

The Dockerfile uses a multi-stage build for optimization:

1. **Builder Stage**: Installs build dependencies and compiles packages
2. **Runtime Stage**: Minimal runtime environment for production
3. **Development Stage**: Extended environment with development tools

### Security Features

- **Non-root User**: Runs as dedicated `docsray` user
- **Minimal Base**: Uses Python slim image
- **Layer Optimization**: Efficient layer caching
- **Security Scanning**: Compatible with container security tools

### Volumes and Persistence

The container uses several volumes for persistence:

- `/app/cache`: Document processing cache
- `/app/logs`: Application logs
- `/app/data`: Document storage (if needed)

## Integration with MCP Clients

### Claude Desktop

The development container automatically configures Claude Desktop:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "docsray",
      "args": ["start"],
      "env": {
        "DOCSRAY_PYMUPDF_ENABLED": "true",
        "DOCSRAY_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Cursor

For Cursor integration with Docker:

```json
{
  "mcpServers": {
    "docsray": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "docsray-mcp"],
      "env": {
        "DOCSRAY_PYMUPDF_ENABLED": "true"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

2. **Port Conflicts**
   ```bash
   # Use different ports
   docker-compose up -e DOCSRAY_HTTP_PORT=3001
   ```

3. **Memory Issues**
   ```bash
   # Increase Docker memory limit
   docker run --memory=2g docsray-mcp
   ```

### Debugging

```bash
# View logs
docker-compose logs docsray-mcp

# Interactive shell
docker-compose exec docsray-mcp bash

# Debug mode
docker-compose up -e DOCSRAY_LOG_LEVEL=DEBUG
```

### Performance Tuning

```bash
# Optimize for production
docker run --memory=1g --cpus=2 docsray-mcp

# Enable caching
docker run -e DOCSRAY_CACHE_ENABLED=true -v cache:/app/cache docsray-mcp
```

## Building Custom Images

### Custom Dockerfile

```dockerfile
FROM docsray-mcp:latest

# Add custom dependencies
RUN pip install custom-package

# Custom configuration
COPY custom-config.json /app/config.json
ENV DOCSRAY_CONFIG_PATH=/app/config.json
```

### Build Arguments

```bash
# Build with specific Python version
docker build --build-arg PYTHON_VERSION=3.11 .

# Build development image
docker build --target development -t docsray-mcp:dev .
```

## Best Practices

1. **Use Multi-stage Builds**: Minimize final image size
2. **Non-root User**: Always run as non-root for security
3. **Health Checks**: Include health checks for HTTP mode
4. **Volume Management**: Use named volumes for persistence
5. **Environment Variables**: Use environment variables for configuration
6. **Resource Limits**: Set appropriate memory and CPU limits
7. **Security Scanning**: Regularly scan images for vulnerabilities

## Examples

See the `examples/docker/` directory for complete examples of:
- Production deployment
- Development setup
- CI/CD integration
- Kubernetes deployment
- Docker Swarm configuration