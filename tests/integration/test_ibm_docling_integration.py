"""Integration tests for IBM Docling provider with real docling library."""

import os
import tempfile
from pathlib import Path

import pytest

from docsray.config import IBMDoclingConfig
from docsray.providers.base import Document
from docsray.providers.ibm_docling import IBMDoclingProvider

# Skip if docling is not installed
try:
    import docling
    from docling.document_converter import DocumentConverter

    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not DOCLING_AVAILABLE, reason="docling not installed"
)


@pytest.fixture
def provider():
    """Create IBM Docling provider instance."""
    return IBMDoclingProvider()


@pytest.fixture
def config():
    """Create IBM Docling configuration."""
    return IBMDoclingConfig(
        enabled=True,
        use_vlm=False,  # Disable VLM for faster testing
        use_asr=False,
        output_format="markdown",
        ocr_enabled=True,
        table_detection=True,
        figure_detection=True,
    )


@pytest.fixture
def sample_pdf():
    """Create a simple test PDF file."""
    # Create a simple PDF with reportlab if available, otherwise use a dummy file
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".pdf") as f:
            pdf_path = f.name
            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.drawString(100, 750, "Test Document")
            c.drawString(100, 730, "This is a test PDF for IBM Docling integration tests.")
            c.drawString(100, 710, "It contains some text content.")
            c.save()

        yield Path(pdf_path)

        # Cleanup
        os.unlink(pdf_path)

    except ImportError:
        # If reportlab is not available, skip PDF creation tests
        pytest.skip("reportlab not available for PDF creation")


class TestIBMDoclingIntegration:
    """Integration tests for IBM Docling provider."""

    @pytest.mark.asyncio
    async def test_provider_initialization(self, provider, config):
        """Test that provider initializes correctly with real docling library."""
        await provider.initialize(config)

        assert provider._initialized is True
        assert provider.converter is not None
        assert isinstance(provider.converter, DocumentConverter)

    @pytest.mark.asyncio
    async def test_conversion_result_unwrapping(self, provider, config, sample_pdf):
        """Test that ConversionResult is properly unwrapped in all methods."""
        await provider.initialize(config)

        document = Document(url=str(sample_pdf), format="pdf")

        # Test peek() unwraps correctly
        peek_result = await provider.peek(document, {"depth": "metadata"})
        assert peek_result.metadata is not None
        assert "pageCount" in peek_result.metadata

    @pytest.mark.asyncio
    async def test_extract_with_default_options(self, provider, config, sample_pdf):
        """Test extract with default options works correctly."""
        await provider.initialize(config)

        document = Document(url=str(sample_pdf), format="pdf")

        extract_result = await provider.extract(
            document, {"extraction_targets": ["text"], "output_format": "markdown"}
        )

        assert extract_result.content is not None
        assert extract_result.format == "markdown"
        assert len(extract_result.pages_processed) > 0

    @pytest.mark.asyncio
    async def test_extract_with_pipeline_options(self, provider, config, sample_pdf):
        """Test extract with custom pipeline options for tables and images."""
        await provider.initialize(config)

        document = Document(url=str(sample_pdf), format="pdf")

        # Test with tables extraction
        extract_result = await provider.extract(
            document,
            {
                "extraction_targets": ["text", "tables", "images"],
                "output_format": "json",
            },
        )

        assert extract_result.content is not None
        assert extract_result.format == "json"
        assert isinstance(extract_result.content, dict)
        assert "content" in extract_result.content
        assert "metadata" in extract_result.content

    @pytest.mark.asyncio
    async def test_map_document_structure(self, provider, config, sample_pdf):
        """Test map generates proper document structure."""
        await provider.initialize(config)

        document = Document(url=str(sample_pdf), format="pdf")

        map_result = await provider.map(
            document, {"include_content": False, "analysis_depth": "deep"}
        )

        assert map_result.document_map is not None
        assert "hierarchy" in map_result.document_map
        assert "resources" in map_result.document_map
        assert map_result.statistics is not None

    @pytest.mark.asyncio
    async def test_seek_by_page(self, provider, config, sample_pdf):
        """Test seek can navigate to specific page."""
        await provider.initialize(config)

        document = Document(url=str(sample_pdf), format="pdf")

        seek_result = await provider.seek(document, {"page": 1})

        assert seek_result.location is not None
        assert seek_result.content is not None

    @pytest.mark.asyncio
    async def test_xray_analysis(self, provider, config, sample_pdf):
        """Test xray performs analysis correctly."""
        await provider.initialize(config)

        document = Document(url=str(sample_pdf), format="pdf")

        xray_result = await provider.xray(
            document, {"analysis_type": ["entities", "structure"]}
        )

        assert xray_result.analysis is not None
        assert "document_classification" in xray_result.analysis
        assert "structural_analysis" in xray_result.analysis
        assert xray_result.confidence > 0

    @pytest.mark.asyncio
    async def test_api_compatibility_with_docling_2_58(self, provider, config):
        """Test that the API works correctly with docling 2.58.0."""
        # This test verifies the fix for the API compatibility issues
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption

        # Create pipeline options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_table_structure = True
        pipeline_options.do_picture_classification = True  # Correct field name
        pipeline_options.generate_picture_images = True

        # Create format-specific options
        pdf_format_option = PdfFormatOption(pipeline_options=pipeline_options)

        # Create converter with format options
        converter = DocumentConverter(
            format_options={InputFormat.PDF: pdf_format_option}
        )

        # Verify converter was created successfully
        assert converter is not None

    @pytest.mark.asyncio
    async def test_field_names_correct(self, provider, config):
        """Test that correct field names are used (do_picture_classification not do_picture)."""
        from docling.datamodel.pipeline_options import PdfPipelineOptions

        pipeline_options = PdfPipelineOptions()

        # These should work (correct field names)
        assert hasattr(pipeline_options, "do_picture_classification")
        assert hasattr(pipeline_options, "generate_picture_images")
        assert hasattr(pipeline_options, "do_table_structure")

        # This should not exist (wrong field name)
        assert not hasattr(pipeline_options, "do_picture")

    @pytest.mark.asyncio
    async def test_dispose(self, provider, config):
        """Test provider cleanup works correctly."""
        await provider.initialize(config)
        assert provider._initialized is True

        await provider.dispose()
        assert provider._initialized is False
        assert provider.converter is None
