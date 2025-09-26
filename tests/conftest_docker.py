"""Docker-specific pytest configuration and fixtures."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Generator

import pytest


def pytest_configure(config):
    """Configure pytest for Docker tests."""
    config.addinivalue_line(
        "markers", "docker: mark test as requiring Docker"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Add docker marker to Docker tests automatically."""
    for item in items:
        if "test_docker" in str(item.fspath):
            item.add_marker(pytest.mark.docker)


@pytest.fixture(scope="session")
def docker_available() -> bool:
    """Check if Docker is available on the system."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


@pytest.fixture(scope="session")
def docker_compose_available() -> bool:
    """Check if Docker Compose is available on the system."""
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True
        
        # Try docker compose (new syntax)
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_image_name() -> str:
    """Standard test image name."""
    return "docsray-mcp-test"


@pytest.fixture(scope="session")
def built_docker_image(docker_available: bool, project_root: Path, test_image_name: str) -> Generator[str, None, None]:
    """Build Docker image for testing and clean up after."""
    if not docker_available:
        pytest.skip("Docker is not available")
    
    # Build the image
    result = subprocess.run(
        ["docker", "build", "-t", test_image_name, "."],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        pytest.skip(f"Failed to build Docker image: {result.stderr}")
    
    yield test_image_name
    
    # Clean up the image after tests
    subprocess.run(
        ["docker", "rmi", test_image_name],
        capture_output=True,
    )


@pytest.fixture
def temp_env_file() -> Generator[Path, None, None]:
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("""
DOCSRAY_LOG_LEVEL=DEBUG
DOCSRAY_PYMUPDF_ENABLED=true
DOCSRAY_CACHE_ENABLED=true
DOCSRAY_TRANSPORT=stdio
""".strip())
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Clean up
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_test_document() -> Generator[Path, None, None]:
    """Create a temporary test document."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document for Docker integration testing.\n")
        f.write("It contains multiple lines of text.\n")
        f.write("Perfect for testing document processing capabilities.")
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Clean up
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def docker_cleanup():
    """Fixture to ensure Docker resources are cleaned up."""
    containers_to_cleanup = []
    volumes_to_cleanup = []
    
    yield {
        'containers': containers_to_cleanup,
        'volumes': volumes_to_cleanup
    }
    
    # Clean up containers
    for container in containers_to_cleanup:
        subprocess.run(
            ["docker", "rm", "-f", container],
            capture_output=True,
        )
    
    # Clean up volumes
    for volume in volumes_to_cleanup:
        subprocess.run(
            ["docker", "volume", "rm", "-f", volume],
            capture_output=True,
        )


def pytest_runtest_setup(item):
    """Setup for individual test items."""
    if item.get_closest_marker("docker"):
        # Check if Docker is available before running Docker tests
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                pytest.skip("Docker is not available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker is not available")


# Custom markers for test organization
pytestmark = [
    pytest.mark.integration,
    pytest.mark.docker,
]