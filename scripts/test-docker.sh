#!/bin/bash
# Docker Test Runner for Docsray MCP Server
# Comprehensive testing of Docker configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="docsray-mcp-test"
DEV_IMAGE_NAME="docsray-mcp-dev-test"

echo -e "${BLUE}🐳 Docsray MCP Server Docker Test Suite${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_warning "Docker Compose not found (some tests will be skipped)"
    fi
    
    print_success "Prerequisites check passed"
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build main image
    print_status "Building main Docker image..."
    if docker build -t "$IMAGE_NAME" .; then
        print_success "Main image built successfully"
    else
        print_error "Failed to build main image"
        exit 1
    fi
    
    # Build dev image
    if [ -f ".devcontainer/Dockerfile" ]; then
        print_status "Building development Docker image..."
        if docker build -f .devcontainer/Dockerfile -t "$DEV_IMAGE_NAME" .; then
            print_success "Development image built successfully"
        else
            print_warning "Failed to build development image"
        fi
    fi
}

# Test basic Docker functionality
test_basic_docker() {
    print_status "Testing basic Docker functionality..."
    
    # Test image exists
    if docker images -q "$IMAGE_NAME" | grep -q .; then
        print_success "Docker image exists"
    else
        print_error "Docker image not found"
        return 1
    fi
    
    # Test container starts
    print_status "Testing container startup..."
    if docker run --rm "$IMAGE_NAME" docsray --version; then
        print_success "Container starts and runs docsray command"
    else
        print_error "Container failed to start or run docsray"
        return 1
    fi
    
    # Test Python import
    print_status "Testing Python imports in container..."
    if docker run --rm "$IMAGE_NAME" python -c "from docsray.server import DocsrayServer; print('Import successful')"; then
        print_success "Python imports work correctly"
    else
        print_error "Python imports failed"
        return 1
    fi
}

# Test Docker Compose configurations
test_docker_compose() {
    print_status "Testing Docker Compose configurations..."
    
    cd "$PROJECT_ROOT"
    
    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        print_warning "docker-compose.yml not found, skipping Compose tests"
        return 0
    fi
    
    # Test basic compose file syntax
    if docker-compose config > /dev/null 2>&1 || docker compose config > /dev/null 2>&1; then
        print_success "Docker Compose configuration is valid"
    else
        print_error "Docker Compose configuration is invalid"
        return 1
    fi
    
    # Test development compose file if it exists
    if [ -f "docker-compose.dev.yml" ]; then
        if docker-compose -f docker-compose.dev.yml config > /dev/null 2>&1; then
            print_success "Development Docker Compose configuration is valid"
        else
            print_warning "Development Docker Compose configuration is invalid"
        fi
    fi
}

# Test environment variable handling
test_environment_variables() {
    print_status "Testing environment variable handling..."
    
    # Test with custom environment variables
    ENV_TEST_OUTPUT=$(docker run --rm \
        -e DOCSRAY_LOG_LEVEL=DEBUG \
        -e DOCSRAY_PYMUPDF_ENABLED=true \
        -e DOCSRAY_CACHE_ENABLED=false \
        "$IMAGE_NAME" \
        python -c "import os; print(f'LOG_LEVEL={os.environ.get(\"DOCSRAY_LOG_LEVEL\", \"NOT_SET\")}'); print(f'PYMUPDF={os.environ.get(\"DOCSRAY_PYMUPDF_ENABLED\", \"NOT_SET\")}'); print(f'CACHE={os.environ.get(\"DOCSRAY_CACHE_ENABLED\", \"NOT_SET\")}')")
    
    if echo "$ENV_TEST_OUTPUT" | grep -q "LOG_LEVEL=DEBUG" && \
       echo "$ENV_TEST_OUTPUT" | grep -q "PYMUPDF=true" && \
       echo "$ENV_TEST_OUTPUT" | grep -q "CACHE=false"; then
        print_success "Environment variables are handled correctly"
    else
        print_error "Environment variables not handled correctly"
        print_error "Output: $ENV_TEST_OUTPUT"
        return 1
    fi
}

# Test volume mounts
test_volume_mounts() {
    print_status "Testing volume mounts..."
    
    # Create temporary directory for testing
    TEMP_DIR=$(mktemp -d)
    TEST_FILE="$TEMP_DIR/test.txt"
    echo "Docker volume test" > "$TEST_FILE"
    
    # Test volume mount
    if docker run --rm -v "$TEMP_DIR:/app/test-data" "$IMAGE_NAME" \
        python -c "
import os
if os.path.exists('/app/test-data/test.txt'):
    with open('/app/test-data/test.txt', 'r') as f:
        content = f.read().strip()
    if content == 'Docker volume test':
        print('Volume mount successful')
    else:
        print('Volume content incorrect')
        exit(1)
else:
    print('Volume file not found')
    exit(1)
"; then
        print_success "Volume mounts work correctly"
    else
        print_error "Volume mounts failed"
        rm -rf "$TEMP_DIR"
        return 1
    fi
    
    # Clean up
    rm -rf "$TEMP_DIR"
}

# Test HTTP mode
test_http_mode() {
    print_status "Testing HTTP mode..."
    
    # Start container in HTTP mode in background
    CONTAINER_ID=$(docker run -d --rm -p 3001:3000 \
        -e DOCSRAY_TRANSPORT=http \
        -e DOCSRAY_HTTP_HOST=0.0.0.0 \
        -e DOCSRAY_HTTP_PORT=3000 \
        "$IMAGE_NAME" \
        docsray start --transport http --port 3000 --verbose)
    
    if [ -z "$CONTAINER_ID" ]; then
        print_error "Failed to start container in HTTP mode"
        return 1
    fi
    
    # Wait for container to start
    sleep 10
    
    # Test if container is running
    if docker ps -q -f id="$CONTAINER_ID" | grep -q .; then
        print_success "HTTP mode container is running"
        
        # Try to connect (this might fail if no health endpoint exists, which is OK)
        if curl -f http://localhost:3001/health > /dev/null 2>&1; then
            print_success "HTTP endpoint is responding"
        else
            print_warning "HTTP endpoint not responding (this might be expected)"
        fi
    else
        print_error "HTTP mode container failed to start"
        docker logs "$CONTAINER_ID" 2>/dev/null || true
        return 1
    fi
    
    # Clean up
    docker stop "$CONTAINER_ID" > /dev/null 2>&1 || true
}

# Test resource limits
test_resource_limits() {
    print_status "Testing resource limits..."
    
    # Test with memory limit
    if docker run --rm --memory=256m "$IMAGE_NAME" docsray --version > /dev/null 2>&1; then
        print_success "Container works with 256MB memory limit"
    else
        print_warning "Container failed with 256MB memory limit"
    fi
    
    # Test with CPU limit
    if docker run --rm --cpus=0.5 "$IMAGE_NAME" docsray --version > /dev/null 2>&1; then
        print_success "Container works with 0.5 CPU limit"
    else
        print_warning "Container failed with 0.5 CPU limit"
    fi
}

# Run pytest Docker tests if available
run_pytest_tests() {
    print_status "Running pytest Docker tests..."
    
    if [ -f "tests/integration/test_docker.py" ]; then
        # Check if docker dependencies are installed
        if python -c "import testcontainers" > /dev/null 2>&1; then
            if python -m pytest tests/integration/test_docker.py -v -m docker --tb=short; then
                print_success "Pytest Docker tests passed"
            else
                print_error "Pytest Docker tests failed"
                return 1
            fi
        else
            print_warning "Docker test dependencies not installed, skipping pytest tests"
            print_warning "Run 'pip install -e .[docker]' to install Docker test dependencies"
        fi
    else
        print_warning "No pytest Docker tests found"
    fi
}

# Clean up function
cleanup() {
    print_status "Cleaning up test artifacts..."
    
    # Remove test images
    docker rmi "$IMAGE_NAME" > /dev/null 2>&1 || true
    docker rmi "$DEV_IMAGE_NAME" > /dev/null 2>&1 || true
    
    # Clean up any remaining test containers
    docker ps -aq --filter "ancestor=$IMAGE_NAME" | xargs -r docker rm -f > /dev/null 2>&1 || true
    docker ps -aq --filter "ancestor=$DEV_IMAGE_NAME" | xargs -r docker rm -f > /dev/null 2>&1 || true
    
    print_success "Cleanup completed"
}

# Main test execution
main() {
    local exit_code=0
    
    # Parse arguments
    SKIP_CLEANUP=false
    VERBOSE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-cleanup)
                SKIP_CLEANUP=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --skip-cleanup    Don't clean up images after tests"
                echo "  --verbose, -v     Verbose output"
                echo "  --help, -h        Show this help"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Set up trap for cleanup
    if [ "$SKIP_CLEANUP" = false ]; then
        trap cleanup EXIT
    fi
    
    # Run tests
    check_prerequisites || exit_code=1
    
    if [ $exit_code -eq 0 ]; then
        build_images || exit_code=1
    fi
    
    if [ $exit_code -eq 0 ]; then
        test_basic_docker || exit_code=1
    fi
    
    if [ $exit_code -eq 0 ]; then
        test_docker_compose || exit_code=1
    fi
    
    if [ $exit_code -eq 0 ]; then
        test_environment_variables || exit_code=1
    fi
    
    if [ $exit_code -eq 0 ]; then
        test_volume_mounts || exit_code=1
    fi
    
    if [ $exit_code -eq 0 ]; then
        test_http_mode || exit_code=1
    fi
    
    if [ $exit_code -eq 0 ]; then
        test_resource_limits || exit_code=1
    fi
    
    if [ $exit_code -eq 0 ]; then
        run_pytest_tests || exit_code=1
    fi
    
    # Summary
    echo ""
    echo -e "${BLUE}======================================${NC}"
    if [ $exit_code -eq 0 ]; then
        print_success "All Docker tests passed! 🎉"
    else
        print_error "Some Docker tests failed! ❌"
    fi
    echo -e "${BLUE}======================================${NC}"
    
    exit $exit_code
}

# Create scripts directory if it doesn't exist
mkdir -p "$(dirname "$0")"

# Run main function
main "$@"