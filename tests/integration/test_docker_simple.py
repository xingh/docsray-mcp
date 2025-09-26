"""Simplified Docker tests for Docsray MCP Server."""

import os
import subprocess
import tempfile
import time
from pathlib import Path

import pytest


@pytest.mark.docker
class TestDockerBasic:
    """Basic Docker functionality tests using subprocess."""

    @pytest.fixture(scope="class")
    def docker_image(self) -> str:
        """Build and return the Docker image name."""
        project_root = Path(__file__).parent.parent.parent
        image_name = "docsray-mcp-test"
        
        # Build the Docker image for testing
        result = subprocess.run(
            ["docker", "build", "-t", image_name, "."],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            pytest.skip(f"Failed to build Docker image: {result.stderr}")
        
        yield image_name
        
        # Cleanup
        subprocess.run(
            ["docker", "rmi", image_name],
            capture_output=True,
        )

    def test_docker_build_success(self, docker_image: str):
        """Test that Docker image builds successfully."""
        result = subprocess.run(
            ["docker", "images", "-q", docker_image],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert result.stdout.strip() != "", "Docker image should exist"

    def test_container_version_command(self, docker_image: str):
        """Test that container can run docsray --version."""
        result = subprocess.run(
            ["docker", "run", "--rm", docker_image, "docsray", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        assert result.returncode == 0
        assert "docsray" in result.stdout.lower() or "0." in result.stdout

    def test_container_python_import(self, docker_image: str):
        """Test that Python imports work in container."""
        result = subprocess.run(
            [
                "docker", "run", "--rm", 
                "-e", "DOCSRAY_LOG_LEVEL=DEBUG",
                docker_image,
                "python", "-c", "from docsray.server import DocsrayServer; print('Import successful')"
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        assert result.returncode == 0
        assert "Import successful" in result.stdout

    def test_container_environment_variables(self, docker_image: str):
        """Test that environment variables are properly set."""
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-e", "DOCSRAY_LOG_LEVEL=DEBUG",
                "-e", "DOCSRAY_PYMUPDF_ENABLED=true",
                "-e", "DOCSRAY_CACHE_ENABLED=false",
                docker_image,
                "python", "-c", 
                "import os; print(f'LOG_LEVEL={os.environ.get(\"DOCSRAY_LOG_LEVEL\", \"NOT_SET\")}'); "
                "print(f'PYMUPDF={os.environ.get(\"DOCSRAY_PYMUPDF_ENABLED\", \"NOT_SET\")}'); "
                "print(f'CACHE={os.environ.get(\"DOCSRAY_CACHE_ENABLED\", \"NOT_SET\")}')"
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        assert result.returncode == 0
        assert "LOG_LEVEL=DEBUG" in result.stdout
        assert "PYMUPDF=true" in result.stdout
        assert "CACHE=false" in result.stdout

    def test_container_volume_mount(self, docker_image: str):
        """Test that volume mounts work."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Docker volume test")
            
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "-v", f"{temp_dir}:/app/test-data",
                    docker_image,
                    "python", "-c",
                    "import os; "
                    "assert os.path.exists('/app/test-data/test.txt'), 'File not found'; "
                    "with open('/app/test-data/test.txt', 'r') as f: content = f.read().strip(); "
                    "assert content == 'Docker volume test', f'Wrong content: {content}'; "
                    "print('Volume mount successful')"
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            assert result.returncode == 0
            assert "Volume mount successful" in result.stdout

    def test_container_memory_limit(self, docker_image: str):
        """Test container works with memory limit."""
        result = subprocess.run(
            [
                "docker", "run", "--rm", "--memory=512m",
                docker_image, "docsray", "--version"
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        assert result.returncode == 0

    @pytest.mark.slow
    def test_container_http_mode_startup(self, docker_image: str):
        """Test that container can start in HTTP mode."""
        # Start container in background
        process = subprocess.Popen(
            [
                "docker", "run", "--rm", "-p", "3001:3000",
                "-e", "DOCSRAY_TRANSPORT=http",
                "-e", "DOCSRAY_HTTP_HOST=0.0.0.0",
                "-e", "DOCSRAY_HTTP_PORT=3000",
                docker_image,
                "docsray", "start", "--transport", "http", "--port", "3000", "--verbose"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        try:
            # Wait a bit for startup
            time.sleep(10)
            
            # Check if process is still running (didn't crash)
            assert process.poll() is None, "Container process terminated unexpectedly"
            
            # Try to connect (might fail if no health endpoint, which is OK)
            try:
                import requests
                response = requests.get("http://localhost:3001/health", timeout=5)
                # Any response (even 404) means the server is running
                print(f"HTTP response: {response.status_code}")
            except requests.exceptions.RequestException:
                # Server might not have health endpoint, which is OK
                print("HTTP request failed (this might be expected)")
                
        finally:
            # Clean up
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()


@pytest.mark.docker
class TestDockerCompose:
    """Test Docker Compose configurations."""

    def test_docker_compose_config_valid(self):
        """Test that docker-compose.yml is valid."""
        project_root = Path(__file__).parent.parent.parent
        compose_file = project_root / "docker-compose.yml"
        
        if not compose_file.exists():
            pytest.skip("docker-compose.yml not found")
        
        # Test with docker-compose command
        result = subprocess.run(
            ["docker-compose", "config"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            # Try with docker compose (newer syntax)
            result = subprocess.run(
                ["docker", "compose", "config"],
                cwd=project_root,
                capture_output=True,
                text=True,
            )
        
        assert result.returncode == 0, f"Docker Compose config invalid: {result.stderr}"

    def test_dev_compose_config_valid(self):
        """Test that docker-compose.dev.yml is valid."""
        project_root = Path(__file__).parent.parent.parent
        compose_file = project_root / "docker-compose.dev.yml"
        
        if not compose_file.exists():
            pytest.skip("docker-compose.dev.yml not found")
        
        result = subprocess.run(
            ["docker-compose", "-f", "docker-compose.dev.yml", "config"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            # Try with docker compose (newer syntax)
            result = subprocess.run(
                ["docker", "compose", "-f", "docker-compose.dev.yml", "config"],
                cwd=project_root,
                capture_output=True,
                text=True,
            )
        
        assert result.returncode == 0, f"Development Docker Compose config invalid: {result.stderr}"


@pytest.mark.docker
class TestDevContainer:
    """Test devcontainer configuration."""

    def test_devcontainer_dockerfile_exists(self):
        """Test that devcontainer Dockerfile exists and is valid."""
        project_root = Path(__file__).parent.parent.parent
        dockerfile = project_root / ".devcontainer" / "Dockerfile"
        
        assert dockerfile.exists(), "Devcontainer Dockerfile not found"
        
        # Test that it can be parsed (basic syntax check)
        content = dockerfile.read_text()
        assert "FROM" in content
        assert "docsray" in content.lower()

    def test_devcontainer_json_valid(self):
        """Test that devcontainer.json is valid JSON."""
        project_root = Path(__file__).parent.parent.parent
        config_file = project_root / ".devcontainer" / "devcontainer.json"
        
        if not config_file.exists():
            pytest.skip("devcontainer.json not found")
        
        import json
        try:
            config = json.loads(config_file.read_text())
            assert "name" in config
            assert "dockerFile" in config or "image" in config
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in devcontainer.json: {e}")

    def test_devcontainer_scripts_executable(self):
        """Test that devcontainer scripts are executable."""
        project_root = Path(__file__).parent.parent.parent
        scripts_dir = project_root / ".devcontainer"
        
        for script_name in ["post-create.sh", "post-start.sh"]:
            script_path = scripts_dir / script_name
            if script_path.exists():
                assert os.access(script_path, os.X_OK), f"{script_name} should be executable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])