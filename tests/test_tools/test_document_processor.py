"""
Tests for document processor functionality.
"""

import pytest
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

from src.tools.document_processor import DocumentProcessor
from src.models.data_models import ExtractedContent


@pytest.fixture
def document_processor():
    """Create a DocumentProcessor instance for testing."""
    return DocumentProcessor()


@pytest.fixture
def mock_pptx_presentation():
    """Mock PowerPoint presentation for testing."""
    mock_presentation = Mock()
    
    # Mock slide 1
    mock_slide1 = Mock()
    mock_slide1.shapes.title.text = "Test Slide 1"
    mock_slide1.slide_layout.name = "Title Slide"
    
    # Mock text shapes
    mock_shape1 = Mock()
    mock_shape1.text = "First bullet point"
    mock_shape2 = Mock()
    mock_shape2.text = "Second bullet point"
    
    mock_slide1.shapes = [mock_shape1, mock_shape2]
    mock_slide1.shapes.title = mock_shape1
    
    # Mock slide 2
    mock_slide2 = Mock()
    mock_slide2.shapes.title.text = "Test Slide 2"
    mock_slide2.slide_layout.name = "Content Slide"
    
    mock_shape3 = Mock()
    mock_shape3.text = "Content for slide 2"
    mock_slide2.shapes = [mock_shape3]
    mock_slide2.shapes.title = mock_shape3
    
    mock_presentation.slides = [mock_slide1, mock_slide2]
    return mock_presentation


class TestDocumentProcessor:
    """Test cases for DocumentProcessor."""

    def test_init(self, document_processor):
        """Test DocumentProcessor initialization."""
        assert document_processor.supported_extensions == {".pptx", ".pdf"}

    def test_validate_file_type_valid(self, document_processor):
        """Test validation of valid file types."""
        assert document_processor.validate_file_type("test.pptx") is True
        assert document_processor.validate_file_type("test.pdf") is True
        assert document_processor.validate_file_type("TEST.PPTX") is True

    def test_validate_file_type_invalid(self, document_processor):
        """Test validation of invalid file types."""
        assert document_processor.validate_file_type("test.txt") is False
        assert document_processor.validate_file_type("test.docx") is False
        assert document_processor.validate_file_type("test") is False

    def test_get_file_type(self, document_processor):
        """Test file type detection."""
        assert document_processor.get_file_type("test.pptx") == "pptx"
        assert document_processor.get_file_type("test.pdf") == "pdf"
        assert document_processor.get_file_type("TEST.PPTX") == "pptx"
        assert document_processor.get_file_type("test.txt") is None

    @pytest.mark.asyncio
    async def test_process_document_invalid_type(self, document_processor):
        """Test processing document with invalid type."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            await document_processor.process_document(
                BytesIO(b"test"), "test.txt", "txt"
            )

    @pytest.mark.asyncio
    @patch('src.tools.document_processor.Presentation')
    async def test_extract_from_powerpoint(self, mock_presentation_class, document_processor, mock_pptx_presentation):
        """Test PowerPoint content extraction."""
        mock_presentation_class.return_value = mock_pptx_presentation
        
        result = await document_processor._extract_from_powerpoint(
            BytesIO(b"test"), "test.pptx"
        )
        
        assert len(result) == 2
        assert all(isinstance(item, ExtractedContent) for item in result)
        assert result[0].title == "Test Slide 1"
        assert result[0].slide_number == 1
        assert result[0].file_type == "pptx"
        assert result[0].source_file == "test.pptx"

    @pytest.mark.asyncio
    @patch('src.tools.document_processor.pypdf.PdfReader')
    async def test_extract_from_pdf(self, mock_pdf_reader, document_processor):
        """Test PDF content extraction."""
        # Mock PDF reader
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Title 1\nContent of page 1"
        
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Title 2\nContent of page 2"
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader
        
        result = await document_processor._extract_from_pdf(
            BytesIO(b"test"), "test.pdf"
        )
        
        assert len(result) == 2
        assert all(isinstance(item, ExtractedContent) for item in result)
        assert result[0].title == "Title 1"
        assert result[0].slide_number == 1
        assert result[0].file_type == "pdf"
        assert result[0].source_file == "test.pdf"

    @pytest.mark.asyncio
    async def test_process_multiple_documents(self, document_processor):
        """Test processing multiple documents."""
        with patch.object(document_processor, 'process_document') as mock_process:
            mock_process.side_effect = [
                [Mock(spec=ExtractedContent)],
                [Mock(spec=ExtractedContent), Mock(spec=ExtractedContent)]
            ]
            
            documents = [
                (BytesIO(b"test1"), "test1.pptx", "pptx"),
                (BytesIO(b"test2"), "test2.pdf", "pdf")
            ]
            
            result = await document_processor.process_multiple_documents(documents)
            
            assert len(result) == 3
            assert mock_process.call_count == 2

    def test_estimate_processing_time(self, document_processor):
        """Test processing time estimation."""
        # Test with small files
        small_files = [1024, 2048]  # 1KB, 2KB
        time_small = document_processor.estimate_processing_time(small_files)
        assert time_small >= 5.0  # Minimum time
        
        # Test with larger files
        large_files = [1024*1024*5, 1024*1024*10]  # 5MB, 10MB
        time_large = document_processor.estimate_processing_time(large_files)
        assert time_large > time_small


@pytest.mark.integration
class TestDocumentProcessorIntegration:
    """Integration tests for DocumentProcessor with real files."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(not Path("Keyrus Commercial - Template.pptx").exists(), 
                       reason="Template file not available")
    async def test_extract_from_real_template(self):
        """Test extraction from real Keyrus template."""
        processor = DocumentProcessor()
        template_path = Path("Keyrus Commercial - Template.pptx")
        
        result = await processor._extract_from_powerpoint(template_path, template_path.name)
        
        assert len(result) > 0
        assert all(isinstance(item, ExtractedContent) for item in result)
        assert all(item.source_file == template_path.name for item in result)
        assert all(item.file_type == "pptx" for item in result)

    @pytest.mark.asyncio
    async def test_error_handling_corrupted_file(self):
        """Test error handling with corrupted files."""
        processor = DocumentProcessor()
        
        # Test with invalid PowerPoint content
        with pytest.raises(Exception):
            await processor._extract_from_powerpoint(
                BytesIO(b"invalid pptx content"), "corrupted.pptx"
            )
        
        # Test with invalid PDF content
        with pytest.raises(Exception):
            await processor._extract_from_pdf(
                BytesIO(b"invalid pdf content"), "corrupted.pdf"
            )