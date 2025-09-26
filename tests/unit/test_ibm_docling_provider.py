"""Tests for IBM.Docling provider."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from docsray.config import IBMDoclingConfig
from docsray.providers.base import Document
from docsray.providers.ibm_docling import IBMDoclingProvider


class TestIBMDoclingProvider:
    """Test IBM.Docling provider functionality."""

    @pytest.fixture
    def provider(self):
        """Create IBM.Docling provider instance."""
        return IBMDoclingProvider()

    @pytest.fixture
    def config(self):
        """Create IBM.Docling configuration."""
        return IBMDoclingConfig(
            enabled=True,
            use_vlm=True,
            use_asr=False,
            output_format="DoclingDocument",
            ocr_enabled=True,
            table_detection=True,
            figure_detection=True,
        )

    @pytest.fixture
    def sample_document(self):
        """Create sample document for testing."""
        return Document(
            url="test.pdf",
            format="pdf",
            size=1024 * 1024,
            has_scanned_content=False
        )

    def test_get_name(self, provider):
        assert provider.get_name() == "ibm-docling"

    def test_get_supported_formats(self, provider):
        formats = provider.get_supported_formats()

        # Check key formats are supported
        assert "pdf" in formats
        assert "docx" in formats
        assert "pptx" in formats
        assert "xlsx" in formats
        assert "html" in formats
        assert "audio" in formats  # ASR support
        assert "image" in formats
        assert "png" in formats
        assert "jpg" in formats

    def test_get_capabilities(self, provider):
        capabilities = provider.get_capabilities()

        # Check key features
        assert capabilities.features["ocr"] is True
        assert capabilities.features["tables"] is True
        assert capabilities.features["images"] is True
        assert capabilities.features["vlm"] is True  # Visual Language Model
        assert capabilities.features["asr"] is True  # Automatic Speech Recognition
        assert capabilities.features["layoutUnderstanding"] is True
        assert capabilities.features["readingOrder"] is True
        assert capabilities.features["structuredExtraction"] is True
        assert capabilities.features["documentClassification"] is True
        assert capabilities.features["entityExtraction"] is True
        assert capabilities.features["semanticAnalysis"] is True

        # Check performance characteristics
        assert capabilities.performance["maxFileSize"] == 100 * 1024 * 1024  # 100MB
        assert capabilities.performance["gpuAccelerated"] == True

    @pytest.mark.asyncio
    async def test_can_process_valid_document(self, provider, config, sample_document):
        await provider.initialize(config)

        result = await provider.can_process(sample_document)
        assert result is True

    @pytest.mark.asyncio
    async def test_can_process_unsupported_format(self, provider, config):
        await provider.initialize(config)

        doc = Document(url="test.xyz", format="xyz")
        result = await provider.can_process(doc)
        assert result is False

    @pytest.mark.asyncio
    async def test_can_process_oversized_document(self, provider, config):
        await provider.initialize(config)

        doc = Document(
            url="test.pdf",
            format="pdf",
            size=200 * 1024 * 1024  # 200MB - over limit
        )
        result = await provider.can_process(doc)
        assert result is False

    @pytest.mark.asyncio
    async def test_can_process_uninitialized(self, provider, sample_document):
        result = await provider.can_process(sample_document)
        assert result is False

    @pytest.mark.asyncio
    async def test_initialize(self, provider, config):
        with patch('docsray.providers.ibm_docling.DocumentConverter') as mock_converter:
            mock_converter.return_value = MagicMock()

            await provider.initialize(config)

            assert provider._initialized is True
            assert provider.config == config
            assert provider.converter is not None

    @pytest.mark.asyncio
    async def test_dispose(self, provider, config):
        with patch('docsray.providers.ibm_docling.DocumentConverter'):
            await provider.initialize(config)
            await provider.dispose()

            assert provider._initialized is False
            assert provider.converter is None

    @pytest.mark.asyncio
    async def test_peek_basic_metadata(self, provider, config, sample_document):
        """Test basic peek functionality with metadata extraction."""
        with patch('docsray.providers.ibm_docling.DocumentConverter') as mock_converter_cls:
            # Setup mock converter and document
            mock_converter = MagicMock()
            mock_converter_cls.return_value = mock_converter

            mock_docling_doc = MagicMock()
            mock_docling_doc.pages = [MagicMock(), MagicMock()]  # 2 pages
            mock_docling_doc.title = "Test Document"
            mock_docling_doc.language = "en"
            mock_converter.convert.return_value = mock_docling_doc

            # Mock file operations
            with patch('docsray.providers.ibm_docling.IBMDoclingProvider._ensure_local_document') as mock_ensure:
                mock_path = MagicMock()
                mock_path.stat.return_value.st_size = 2048
                mock_path.exists.return_value = True
                mock_path.stem = "test"
                mock_ensure.return_value = mock_path

                await provider.initialize(config)
                result = await provider.peek(sample_document, {"depth": "metadata"})

                assert result.metadata is not None
                assert result.metadata["pageCount"] == 2
                assert result.metadata["title"] == "Test Document"
                assert result.metadata["language"] == "en"
                assert result.metadata["fileSize"] == 2048
                assert result.metadata["providerCapabilities"]["provider"] == "ibm-docling"
                assert "advanced_layout_understanding" in result.metadata["providerCapabilities"]["features"]

    @pytest.mark.asyncio
    async def test_extract_docling_document_format(self, provider, config, sample_document):
        """Test extraction in native DoclingDocument format."""
        with patch('docsray.providers.ibm_docling.DocumentConverter') as mock_converter_cls:
            # Setup mock converter
            mock_converter = MagicMock()
            mock_converter_cls.return_value = mock_converter

            mock_docling_doc = MagicMock()
            mock_docling_doc.pages = [MagicMock(), MagicMock()]
            mock_docling_doc.model_dump.return_value = {"test": "document"}
            mock_converter.convert.return_value = mock_docling_doc

            with patch('docsray.providers.ibm_docling.IBMDoclingProvider._ensure_local_document'):
                await provider.initialize(config)

                result = await provider.extract(
                    sample_document,
                    {
                        "extraction_targets": ["text"],
                        "output_format": "DoclingDocument"
                    }
                )

                assert result.format == "DoclingDocument"
                assert result.content is not None
                assert result.content["document"] == {"test": "document"}
                assert result.content["pages"] == 2
                assert result.content["structure_preserved"] is True
                assert result.pages_processed == [1, 2]
                assert result.statistics["structurePreserved"] is True

    @pytest.mark.asyncio
    async def test_extract_markdown_format(self, provider, config, sample_document):
        """Test extraction in markdown format."""
        with patch('docsray.providers.ibm_docling.DocumentConverter') as mock_converter_cls:
            mock_converter = MagicMock()
            mock_converter_cls.return_value = mock_converter

            mock_docling_doc = MagicMock()
            mock_docling_doc.pages = [MagicMock()]
            mock_docling_doc.export_to_markdown.return_value = "# Test Document\n\nContent here"
            mock_converter.convert.return_value = mock_docling_doc

            with patch('docsray.providers.ibm_docling.IBMDoclingProvider._ensure_local_document'):
                await provider.initialize(config)

                result = await provider.extract(
                    sample_document,
                    {
                        "extraction_targets": ["text"],
                        "output_format": "markdown"
                    }
                )

                assert result.format == "markdown"
                assert result.content == "# Test Document\n\nContent here"
                assert result.pages_processed == [1]

    @pytest.mark.asyncio
    async def test_xray_analysis(self, provider, config, sample_document):
        """Test AI-powered document analysis."""
        with patch('docsray.providers.ibm_docling.DocumentConverter') as mock_converter_cls:
            mock_converter = MagicMock()
            mock_converter_cls.return_value = mock_converter

            mock_docling_doc = MagicMock()
            mock_converter.convert.return_value = mock_docling_doc

            with patch('docsray.providers.ibm_docling.IBMDoclingProvider._ensure_local_document'):
                await provider.initialize(config)

                result = await provider.xray(
                    sample_document,
                    {
                        "analysis_type": ["entities", "key-points", "sentiment"],
                        "custom_instructions": "Extract contract terms"
                    }
                )

                assert result.analysis is not None
                assert "entities" in result.analysis
                assert "key_points" in result.analysis
                assert "sentiment" in result.analysis
                assert "custom_analysis" in result.analysis
                assert result.confidence == 0.9
                assert result.provider_info["name"] == "ibm-docling"
                assert result.provider_info["supports_xray"] is True
                assert "VLM" in result.provider_info["capabilities"]

    @pytest.mark.asyncio
    async def test_map_comprehensive_structure(self, provider, config, sample_document):
        """Test comprehensive document structure mapping."""
        with patch('docsray.providers.ibm_docling.DocumentConverter') as mock_converter_cls:
            mock_converter = MagicMock()
            mock_converter_cls.return_value = mock_converter

            # Create mock document with structure
            mock_docling_doc = MagicMock()
            mock_docling_doc.pages = [MagicMock(), MagicMock()]
            mock_docling_doc.title = "Test Document"

            # Mock text elements with headings
            mock_text1 = MagicMock()
            mock_text1.label = "title"
            mock_text1.text = "Introduction"
            mock_text2 = MagicMock()
            mock_text2.label = "heading-1"
            mock_text2.text = "Chapter 1"
            mock_docling_doc.texts = [mock_text1, mock_text2]

            # Mock tables
            mock_table = MagicMock()
            mock_table.caption = "Data Table"
            mock_table.num_rows = 5
            mock_table.num_cols = 3
            mock_docling_doc.tables = [mock_table]

            # Mock pictures
            mock_picture = MagicMock()
            mock_picture.caption = "Figure 1"
            mock_picture.bbox = {"x": 100, "y": 200, "width": 300, "height": 400}
            mock_docling_doc.pictures = [mock_picture]

            mock_converter.convert.return_value = mock_docling_doc

            with patch('docsray.providers.ibm_docling.IBMDoclingProvider._ensure_local_document'):
                await provider.initialize(config)

                result = await provider.map(
                    sample_document,
                    {
                        "include_content": True,
                        "analysis_depth": "comprehensive"
                    }
                )

                assert result.document_map is not None
                assert result.document_map["hierarchy"]["root"]["title"] == "Test Document"
                assert len(result.document_map["hierarchy"]["root"]["children"]) == 2
                assert len(result.document_map["resources"]["tables"]) == 1
                assert len(result.document_map["resources"]["figures"]) == 1
                assert len(result.document_map["layout"]["readingOrder"]) == 2

                # Check table information
                table_info = result.document_map["resources"]["tables"][0]
                assert table_info["caption"] == "Data Table"
                assert table_info["structure"]["rows"] == 5
                assert table_info["structure"]["columns"] == 3

                # Check figure information
                figure_info = result.document_map["resources"]["figures"][0]
                assert figure_info["caption"] == "Figure 1"

                # Check statistics
                assert result.statistics["totalPages"] == 2
                assert result.statistics["totalSections"] == 2
                assert result.statistics["totalTables"] == 1
                assert result.statistics["totalFigures"] == 1
                assert result.statistics["layoutPreserved"] is True
                assert result.statistics["readingOrderDetected"] is True

    def test_config_validation(self):
        """Test IBM.Docling configuration validation."""
        # Valid config
        config = IBMDoclingConfig(
            enabled=True,
            output_format="DoclingDocument"
        )
        assert config.output_format == "DoclingDocument"

        # Invalid output format should raise validation error
        with pytest.raises(ValueError):
            IBMDoclingConfig(
                enabled=True,
                output_format="invalid_format"
            )

    @pytest.mark.asyncio
    async def test_audio_processing_capability(self, provider, config):
        """Test that provider can handle audio files when ASR is enabled."""
        config.use_asr = True

        audio_doc = Document(url="test.wav", format="audio")

        with patch('docsray.providers.ibm_docling.DocumentConverter'):
            await provider.initialize(config)

            result = await provider.can_process(audio_doc)
            assert result is True

            # Check that audio format is in supported formats
            formats = provider.get_supported_formats()
            assert "audio" in formats

    def test_feature_scoring_in_registry(self):
        """Test that IBM.Docling features are properly scored in registry."""
        provider = IBMDoclingProvider()
        caps = provider.get_capabilities()

        # IBM.Docling should have high scores for these capabilities
        assert caps.features["vlm"] is True  # Should get +8 for xray operations
        assert caps.features["layoutUnderstanding"] is True  # Should get +7 for xray, +8 for map
        assert caps.features["structuredExtraction"] is True  # Should get +7 for extract
        assert caps.features["readingOrder"] is True  # Should get +5 for extract
        assert caps.features["documentClassification"] is True  # Should get +6 for map
        assert caps.features["entityExtraction"] is True  # Should get +6 for xray