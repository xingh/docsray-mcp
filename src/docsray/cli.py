"""CLI entry point for Docsray MCP server."""

import asyncio
import logging
import sys
from pathlib import Path

import click
import nest_asyncio
from dotenv import load_dotenv

from . import __version__
from .config import DocsrayConfig
from .server import DocsrayServer

# Apply nest_asyncio patch immediately to allow nested event loops
nest_asyncio.apply()

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__, prog_name="docsray")
def cli():
    """Docsray MCP Server - Advanced document perception and understanding."""
    pass


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path"
)
@click.option(
    "--transport",
    "-t",
    type=click.Choice(["stdio", "http"]),
    help="Transport type (default: stdio)"
)
@click.option(
    "--port",
    "-p",
    type=int,
    help="HTTP port (default: 3000)"
)
@click.option(
    "--host",
    "-h",
    type=str,
    help="HTTP host (default: 127.0.0.1)"
)
@click.option(
    "--provider",
    type=str,
    help="Default provider selection"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging"
)
def start(config, transport, port, host, provider, verbose):
    """Start the MCP server."""
    # Load environment variables
    load_dotenv()

    # Create configuration
    if config:
        # Load from file (future feature)
        click.echo(f"Loading config from: {config}")

    server_config = DocsrayConfig.from_env()

    # Override with CLI options
    if transport:
        server_config.transport.type = transport
    if port:
        server_config.transport.http_port = port
    if host:
        server_config.transport.http_host = host
    if provider:
        server_config.providers.default = provider
    if verbose:
        server_config.log_level = "DEBUG"

    # Create and run server
    server = DocsrayServer(server_config)

    async def run_server():
        """Run the server with proper shutdown handling."""
        try:
            await server.run()
        except KeyboardInterrupt:
            click.echo("\nShutting down...")
            await server.shutdown()
        except Exception as e:
            logger.error(f"Server error: {e}")
            await server.shutdown()
            raise

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        click.echo("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--provider",
    "-p",
    type=str,
    required=True,
    help="Provider to test"
)
@click.option(
    "--document",
    "-d",
    type=str,
    help="Document to test with"
)
def test(provider, document):
    """Test provider connectivity."""
    # Load environment variables
    load_dotenv()

    async def run_test():
        config = DocsrayConfig.from_env()
        server = DocsrayServer(config)

        # Get provider
        provider_instance = server.registry.get_provider(provider)
        if not provider_instance:
            click.echo(f"Provider '{provider}' not found")
            return

        click.echo(f"Testing provider: {provider}")
        click.echo(f"Supported formats: {', '.join(provider_instance.get_supported_formats())}")

        caps = provider_instance.get_capabilities()
        click.echo(f"Features: {caps.features}")

        if document:
            from .providers.base import Document
            from .utils.documents import get_document_format

            doc = Document(
                url=document,
                format=get_document_format(document)
            )

            can_process = await provider_instance.can_process(doc)
            click.echo(f"Can process {document}: {can_process}")

            if can_process:
                try:
                    result = await provider_instance.peek(doc, {"depth": "metadata"})
                    click.echo(f"Document metadata: {result.metadata}")
                except Exception as e:
                    click.echo(f"Error: {e}")

    # Run test
    try:
        asyncio.run(run_test())
    except Exception as e:
        click.echo(f"Test error: {e}")
        sys.exit(1)


@cli.command()
def list_providers():
    """List available providers."""
    # Load environment variables
    load_dotenv()

    config = DocsrayConfig.from_env()

    click.echo("Available providers:")
    click.echo()

    # Check each provider
    providers = [
        ("pymupdf4llm", config.providers.pymupdf4llm.enabled, "PDF, XPS, EPUB processing"),
        ("pytesseract", config.providers.pytesseract.enabled, "OCR for scanned documents"),
        ("ocrmypdf", config.providers.ocrmypdf.enabled, "Advanced OCR processing"),
        ("mistral-ocr", config.providers.mistral_ocr.enabled, "AI-powered OCR and analysis"),
        ("llama-parse", config.providers.llama_parse.enabled, "Advanced document parsing"),
    ]

    for name, enabled, description in providers:
        status = "✓ Enabled" if enabled else "✗ Disabled"
        click.echo(f"  {name:<15} {status:<12} - {description}")

    click.echo()
    click.echo(f"Default provider: {config.providers.default}")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
