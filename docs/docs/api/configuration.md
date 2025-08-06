---
sidebar_position: 3
---

# Configuration API Reference

Complete reference for all configuration options, environment variables, and programmatic configuration.

## Environment Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCSRAY_CACHE_ENABLED` | boolean | `true` | Enable result caching |
| `DOCSRAY_CACHE_DIR` | string | `.docsray` | Cache directory path |
| `DOCSRAY_CACHE_TTL` | integer | `3600` | Cache TTL in seconds |
| `DOCSRAY_LOG_LEVEL` | string | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `DOCSRAY_LOG_FORMAT` | string | `text` | Log format (text, json) |
| `DOCSRAY_LOG_FILE` | string | `null` | Log file path (optional) |

### Performance Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCSRAY_MAX_CONCURRENT_REQUESTS` | integer | `5` | Max concurrent operations |
| `DOCSRAY_TIMEOUT_SECONDS` | integer | `30` | Default operation timeout |
| `DOCSRAY_MAX_FILE_SIZE_MB` | integer | `100` | Maximum file size limit |
| `DOCSRAY_AUTO_PROVIDER_SELECTION` | boolean | `true` | Enable auto provider selection |
| `DOCSRAY_FALLBACK_TO_PYMUPDF` | boolean | `true` | Fallback to PyMuPDF on errors |

### Network Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCSRAY_HTTP_TIMEOUT` | integer | `30` | HTTP request timeout |
| `DOCSRAY_MAX_RETRIES` | integer | `2` | Max retry attempts |
| `DOCSRAY_RETRY_DELAY` | integer | `1` | Delay between retries (seconds) |
| `DOCSRAY_USER_AGENT` | string | `DocsRay-MCP/0.2.0` | HTTP User-Agent header |
| `DOCSRAY_VERIFY_SSL` | boolean | `true` | Verify SSL certificates |

## Provider-Specific Configuration

### PyMuPDF4LLM Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCSRAY_PYMUPDF4LLM_ENABLED` | boolean | `true` | Enable PyMuPDF4LLM provider |
| `PYMUPDF4LLM_EXTRACT_IMAGES` | boolean | `false` | Extract images to files |
| `PYMUPDF4LLM_EXTRACT_TABLES` | boolean | `true` | Enable table detection |
| `PYMUPDF4LLM_PAGE_SEPARATORS` | boolean | `true` | Include page separators |
| `PYMUPDF4LLM_WRITE_IMAGES` | boolean | `false` | Save images to disk |
| `PYMUPDF4LLM_TO_MARKDOWN` | boolean | `true` | Convert to markdown |
| `PYMUPDF4LLM_SHOW_PROGRESS` | boolean | `false` | Show progress output |
| `PYMUPDF4LLM_DPI` | integer | `72` | Image DPI setting |
| `PYMUPDF4LLM_MAX_IMAGE_SIZE_MB` | integer | `10` | Max image size limit |
| `PYMUPDF4LLM_MAX_PAGE_SIZE_MB` | integer | `50` | Max page size limit |
| `PYMUPDF4LLM_IGNORE_ERRORS` | boolean | `true` | Continue on page errors |
| `PYMUPDF4LLM_INCLUDE_METADATA` | boolean | `true` | Extract document metadata |

### LlamaParse Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCSRAY_LLAMAPARSE_ENABLED` | boolean | `true` | Enable LlamaParse provider |
| `LLAMAPARSE_API_KEY` | string | `null` | **Required** API key (llx-*) |
| `LLAMAPARSE_BASE_URL` | string | `https://api.cloud.llamaindex.ai` | API base URL |
| `LLAMAPARSE_MODE` | string | `fast` | Processing mode (fast, accurate, premium) |
| `LLAMAPARSE_MAX_TIMEOUT` | integer | `120` | Max processing timeout (seconds) |
| `LLAMAPARSE_CHECK_INTERVAL` | integer | `1` | Status check interval (seconds) |
| `LLAMAPARSE_LANGUAGE` | string | `auto` | Document language (auto-detect) |
| `LLAMAPARSE_PARSING_INSTRUCTION` | string | `""` | Global parsing instructions |
| `LLAMAPARSE_INVALIDATE_CACHE` | boolean | `false` | Force cache refresh |
| `LLAMAPARSE_DO_NOT_CACHE` | boolean | `false` | Disable caching entirely |

### Advanced Cache Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCSRAY_CACHE_MAX_SIZE_MB` | integer | `1000` | Maximum cache size |
| `DOCSRAY_CACHE_COMPRESSION` | boolean | `true` | Enable cache compression |
| `DOCSRAY_CACHE_CLEANUP_INTERVAL` | integer | `3600` | Cleanup interval (seconds) |
| `DOCSRAY_CACHE_VALIDATION_ENABLED` | boolean | `true` | Validate cache integrity |
| `DOCSRAY_CACHE_BACKUP_ENABLED` | boolean | `false` | Enable cache backups |
| `DOCSRAY_CACHE_BACKUP_LOCATION` | string | `null` | Backup storage location |

## Configuration Files

### YAML Configuration

Create a `docsray.yaml` file for complex configuration:

```yaml
# docsray.yaml
providers:
  pymupdf4llm:
    enabled: true
    extract_images: false
    extract_tables: true
    page_separators: true
    to_markdown: true
    dpi: 72
    max_image_size_mb: 10
    
  llamaparse:
    enabled: true
    api_key: ${LLAMAPARSE_API_KEY}
    base_url: "https://api.cloud.llamaindex.ai"
    mode: fast
    max_timeout: 120
    language: auto
    check_interval: 1
    
cache:
  enabled: true
  directory: .docsray
  ttl: 3600
  max_size_mb: 1000
  compression: true
  cleanup_interval: 3600
  validation_enabled: true
  
performance:
  max_concurrent_requests: 5
  timeout_seconds: 30
  max_file_size_mb: 100
  auto_provider_selection: true
  fallback_to_pymupdf: true
  
network:
  http_timeout: 30
  max_retries: 2
  retry_delay: 1
  verify_ssl: true
  user_agent: "DocsRay-MCP/0.2.0"
  
logging:
  level: INFO
  format: text
  file: null
```

### JSON Configuration

Alternative JSON format:

```json
{
  "providers": {
    "pymupdf4llm": {
      "enabled": true,
      "extract_images": false,
      "extract_tables": true
    },
    "llamaparse": {
      "enabled": true,
      "api_key": "${LLAMAPARSE_API_KEY}",
      "mode": "fast",
      "max_timeout": 120
    }
  },
  "cache": {
    "enabled": true,
    "directory": ".docsray",
    "ttl": 3600
  },
  "logging": {
    "level": "INFO",
    "format": "text"
  }
}
```

## Programmatic Configuration

### Configuration Classes

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CacheConfig:
    """Cache configuration settings."""
    enabled: bool = True
    directory: str = ".docsray"
    ttl: int = 3600
    max_size_mb: int = 1000
    compression: bool = True
    cleanup_interval: int = 3600
    validation_enabled: bool = True

@dataclass
class PerformanceConfig:
    """Performance-related settings."""
    max_concurrent_requests: int = 5
    timeout_seconds: int = 30
    max_file_size_mb: int = 100
    auto_provider_selection: bool = True
    fallback_to_pymupdf: bool = True

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "text"
    file: Optional[str] = None

@dataclass
class DocsrayConfig:
    """Main Docsray configuration."""
    cache: CacheConfig = CacheConfig()
    performance: PerformanceConfig = PerformanceConfig()
    logging: LoggingConfig = LoggingConfig()
```

### Configuration Manager

```python
class ConfigManager:
    """Manages Docsray configuration from multiple sources."""
    
    def __init__(self):
        self.config = DocsrayConfig()
        self.load_configuration()
    
    def load_configuration(self):
        """Load configuration from environment and config files."""
        # Load from environment variables
        self.load_from_environment()
        
        # Load from config file if exists
        if os.path.exists("docsray.yaml"):
            self.load_from_yaml("docsray.yaml")
        elif os.path.exists("docsray.json"):
            self.load_from_json("docsray.json")
    
    def load_from_environment(self):
        """Load configuration from environment variables."""
        import os
        
        # Cache settings
        self.config.cache.enabled = os.getenv('DOCSRAY_CACHE_ENABLED', 'true').lower() == 'true'
        self.config.cache.directory = os.getenv('DOCSRAY_CACHE_DIR', '.docsray')
        self.config.cache.ttl = int(os.getenv('DOCSRAY_CACHE_TTL', '3600'))
        
        # Performance settings
        self.config.performance.max_concurrent_requests = int(os.getenv('DOCSRAY_MAX_CONCURRENT_REQUESTS', '5'))
        self.config.performance.timeout_seconds = int(os.getenv('DOCSRAY_TIMEOUT_SECONDS', '30'))
        
        # Logging settings
        self.config.logging.level = os.getenv('DOCSRAY_LOG_LEVEL', 'INFO')
        self.config.logging.format = os.getenv('DOCSRAY_LOG_FORMAT', 'text')
        self.config.logging.file = os.getenv('DOCSRAY_LOG_FILE')
    
    def load_from_yaml(self, file_path: str):
        """Load configuration from YAML file."""
        import yaml
        
        with open(file_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
        
        # Update configuration from YAML
        if 'cache' in yaml_config:
            cache_config = yaml_config['cache']
            self.config.cache = CacheConfig(**cache_config)
    
    def get_config(self) -> DocsrayConfig:
        """Get current configuration."""
        return self.config
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any errors."""
        errors = []
        
        # Validate cache directory
        if not os.path.exists(self.config.cache.directory):
            try:
                os.makedirs(self.config.cache.directory, exist_ok=True)
            except PermissionError:
                errors.append(f"Cannot create cache directory: {self.config.cache.directory}")
        
        # Validate timeout values
        if self.config.performance.timeout_seconds <= 0:
            errors.append("Timeout must be positive")
        
        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if self.config.logging.level not in valid_levels:
            errors.append(f"Invalid log level: {self.config.logging.level}")
        
        return errors

# Usage
config_manager = ConfigManager()
config = config_manager.get_config()
errors = config_manager.validate_config()

if errors:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
```

### Runtime Configuration

```python
def configure_docsray(**kwargs):
    """Configure Docsray at runtime."""
    
    # Apply configuration changes
    if 'cache_enabled' in kwargs:
        os.environ['DOCSRAY_CACHE_ENABLED'] = str(kwargs['cache_enabled']).lower()
    
    if 'log_level' in kwargs:
        os.environ['DOCSRAY_LOG_LEVEL'] = kwargs['log_level']
    
    if 'timeout' in kwargs:
        os.environ['DOCSRAY_TIMEOUT_SECONDS'] = str(kwargs['timeout'])
    
    # Reload configuration
    config_manager = ConfigManager()
    return config_manager.get_config()

# Usage examples
configure_docsray(cache_enabled=False, log_level="DEBUG")
configure_docsray(timeout=60, max_concurrent_requests=3)
```

## Configuration Validation

### Validation Rules

```python
class ConfigValidator:
    """Validates Docsray configuration."""
    
    @staticmethod
    def validate_cache_config(config: CacheConfig) -> List[str]:
        """Validate cache configuration."""
        errors = []
        
        if config.ttl <= 0:
            errors.append("Cache TTL must be positive")
        
        if config.max_size_mb <= 0:
            errors.append("Cache max size must be positive")
        
        if not os.path.exists(os.path.dirname(config.directory)):
            errors.append(f"Cache directory parent does not exist: {config.directory}")
        
        return errors
    
    @staticmethod
    def validate_performance_config(config: PerformanceConfig) -> List[str]:
        """Validate performance configuration."""
        errors = []
        
        if config.max_concurrent_requests <= 0:
            errors.append("Max concurrent requests must be positive")
        
        if config.timeout_seconds <= 0:
            errors.append("Timeout must be positive")
        
        if config.max_file_size_mb <= 0:
            errors.append("Max file size must be positive")
        
        return errors
    
    @staticmethod
    def validate_logging_config(config: LoggingConfig) -> List[str]:
        """Validate logging configuration."""
        errors = []
        
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if config.level not in valid_levels:
            errors.append(f"Invalid log level: {config.level}")
        
        valid_formats = ['text', 'json']
        if config.format not in valid_formats:
            errors.append(f"Invalid log format: {config.format}")
        
        if config.file and not os.path.exists(os.path.dirname(config.file)):
            errors.append(f"Log file directory does not exist: {config.file}")
        
        return errors

# Usage
validator = ConfigValidator()
config = config_manager.get_config()

all_errors = []
all_errors.extend(validator.validate_cache_config(config.cache))
all_errors.extend(validator.validate_performance_config(config.performance))
all_errors.extend(validator.validate_logging_config(config.logging))

if all_errors:
    print("Configuration validation errors:")
    for error in all_errors:
        print(f"  ❌ {error}")
else:
    print("✅ Configuration is valid")
```

## Configuration Profiles

### Environment-Based Profiles

```python
def load_profile(profile_name: str) -> DocsrayConfig:
    """Load configuration profile by name."""
    
    profiles = {
        "development": DocsrayConfig(
            cache=CacheConfig(
                enabled=True,
                directory=".docsray-dev",
                ttl=300  # 5 minutes
            ),
            logging=LoggingConfig(
                level="DEBUG",
                format="text"
            ),
            performance=PerformanceConfig(
                max_concurrent_requests=2,
                timeout_seconds=10
            )
        ),
        
        "production": DocsrayConfig(
            cache=CacheConfig(
                enabled=True,
                directory="/var/cache/docsray",
                ttl=3600,  # 1 hour
                max_size_mb=5000
            ),
            logging=LoggingConfig(
                level="WARNING",
                format="json",
                file="/var/log/docsray.log"
            ),
            performance=PerformanceConfig(
                max_concurrent_requests=10,
                timeout_seconds=60
            )
        ),
        
        "testing": DocsrayConfig(
            cache=CacheConfig(
                enabled=False  # Disable cache for tests
            ),
            logging=LoggingConfig(
                level="ERROR",
                format="text"
            ),
            performance=PerformanceConfig(
                max_concurrent_requests=1,
                timeout_seconds=5
            )
        )
    }
    
    return profiles.get(profile_name, DocsrayConfig())

# Usage
profile = os.getenv('DOCSRAY_PROFILE', 'development')
config = load_profile(profile)
```

## Configuration Monitoring

### Configuration Changes

```python
class ConfigMonitor:
    """Monitor configuration changes."""
    
    def __init__(self, config: DocsrayConfig):
        self.config = config
        self.watchers = []
    
    def add_watcher(self, callback):
        """Add configuration change callback."""
        self.watchers.append(callback)
    
    def update_config(self, new_config: DocsrayConfig):
        """Update configuration and notify watchers."""
        old_config = self.config
        self.config = new_config
        
        # Notify watchers of changes
        for watcher in self.watchers:
            watcher(old_config, new_config)
    
    def detect_changes(self, old_config: DocsrayConfig, new_config: DocsrayConfig) -> Dict[str, Any]:
        """Detect specific configuration changes."""
        changes = {}
        
        # Check cache changes
        if old_config.cache.enabled != new_config.cache.enabled:
            changes['cache_enabled'] = {
                'old': old_config.cache.enabled,
                'new': new_config.cache.enabled
            }
        
        # Check logging changes
        if old_config.logging.level != new_config.logging.level:
            changes['log_level'] = {
                'old': old_config.logging.level,
                'new': new_config.logging.level
            }
        
        return changes

# Usage
config_monitor = ConfigMonitor(config)

def on_config_change(old_config, new_config):
    changes = config_monitor.detect_changes(old_config, new_config)
    if changes:
        print(f"Configuration changed: {changes}")

config_monitor.add_watcher(on_config_change)
```

## Best Practices

### Configuration Management

1. **Environment Variables** - Use for deployment-specific settings
2. **Configuration Files** - Use for complex, structured configuration
3. **Validation** - Always validate configuration before use
4. **Profiles** - Use different profiles for different environments
5. **Monitoring** - Track configuration changes in production
6. **Security** - Never commit API keys or sensitive data
7. **Documentation** - Document all configuration options

### Security Considerations

```python
def sanitize_config_for_logging(config: DocsrayConfig) -> Dict[str, Any]:
    """Sanitize configuration for safe logging."""
    
    config_dict = {
        "cache": {
            "enabled": config.cache.enabled,
            "directory": config.cache.directory,
            "ttl": config.cache.ttl
        },
        "logging": {
            "level": config.logging.level,
            "format": config.logging.format
        },
        "performance": {
            "max_concurrent_requests": config.performance.max_concurrent_requests,
            "timeout_seconds": config.performance.timeout_seconds
        }
    }
    
    # Remove sensitive information
    # API keys, passwords, etc. are not included
    
    return config_dict
```

## Next Steps

- See [Tools API Reference](./tools) for operation parameters
- Check [Providers Overview](../providers/overview) for provider-specific settings
- Review [Configuration Guide](../getting-started/configuration) for setup examples