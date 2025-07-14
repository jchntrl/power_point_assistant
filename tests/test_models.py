"""
Tests for data models and validation.
"""

import pytest
from datetime import datetime
from pathlib import Path
from typing import List

from pydantic import ValidationError

from src.models.data_models import (
    ProjectDescription,
    PowerPointSource,
    ExtractedContent,
    GeneratedSlide,
    PresentationSpec,
    DocumentAnalysisResult,
    ProjectAnalysisResult,
    ContentGenerationResult,
    ProcessingStatus,
    FileUploadInfo
)


class TestProjectDescription:
    """Test cases for ProjectDescription model."""

    def test_valid_project_description(self):
        """Test creation of valid ProjectDescription."""
        project = ProjectDescription(
            description="This is a test project description with enough content",
            client_name="Test Client",
            industry="Technology",
            timeline="6 months",
            budget_range="$100K-500K",
            key_technologies=["Python", "AWS", "React"]
        )
        
        assert project.description == "This is a test project description with enough content"
        assert project.client_name == "Test Client"
        assert project.industry == "Technology"
        assert len(project.key_technologies) == 3

    def test_minimum_description_length(self):
        """Test minimum description length validation."""
        with pytest.raises(ValidationError):
            ProjectDescription(
                description="Too short",  # Less than 10 characters
                client_name="Test Client"
            )

    def test_minimum_client_name_length(self):
        """Test minimum client name length validation."""
        with pytest.raises(ValidationError):
            ProjectDescription(
                description="This is a valid project description",
                client_name=""  # Empty client name
            )

    def test_optional_fields(self):
        """Test that optional fields can be None."""
        project = ProjectDescription(
            description="This is a valid project description",
            client_name="Test Client"
        )
        
        assert project.industry is None
        assert project.timeline is None
        assert project.budget_range is None
        assert project.key_technologies == []


class TestExtractedContent:
    """Test cases for ExtractedContent model."""

    def test_valid_extracted_content(self):
        """Test creation of valid ExtractedContent."""
        content = ExtractedContent(
            slide_number=1,
            title="Test Slide",
            content="This is test content",
            layout_type="bullet",
            source_file="test.pptx",
            file_type="pptx"
        )
        
        assert content.slide_number == 1
        assert content.title == "Test Slide"
        assert content.file_type == "pptx"

    def test_slide_number_validation(self):
        """Test slide number must be >= 1."""
        with pytest.raises(ValidationError):
            ExtractedContent(
                slide_number=0,  # Invalid slide number
                title="Test Slide",
                content="Test content",
                layout_type="bullet",
                source_file="test.pptx"
            )

    def test_default_file_type(self):
        """Test default file type is pptx."""
        content = ExtractedContent(
            slide_number=1,
            title="Test Slide",
            content="Test content",
            layout_type="bullet",
            source_file="test.pptx"
        )
        
        assert content.file_type == "pptx"


class TestGeneratedSlide:
    """Test cases for GeneratedSlide model."""

    def test_valid_generated_slide(self):
        """Test creation of valid GeneratedSlide."""
        slide = GeneratedSlide(
            title="Test Slide",
            content=["Point 1", "Point 2", "Point 3"],
            layout_type="bullet",
            notes="These are speaker notes"
        )
        
        assert slide.title == "Test Slide"
        assert len(slide.content) == 3
        assert slide.layout_type == "bullet"
        assert slide.notes == "These are speaker notes"

    def test_minimum_title_length(self):
        """Test minimum title length validation."""
        with pytest.raises(ValidationError):
            GeneratedSlide(
                title="",  # Empty title
                content=["Point 1"]
            )

    def test_minimum_content_items(self):
        """Test minimum content items validation."""
        with pytest.raises(ValidationError):
            GeneratedSlide(
                title="Test Slide",
                content=[]  # Empty content list
            )

    def test_default_layout_type(self):
        """Test default layout type is bullet."""
        slide = GeneratedSlide(
            title="Test Slide",
            content=["Point 1"]
        )
        
        assert slide.layout_type == "bullet"


class TestPresentationSpec:
    """Test cases for PresentationSpec model."""

    def test_valid_presentation_spec(self):
        """Test creation of valid PresentationSpec."""
        project = ProjectDescription(
            description="Test project description",
            client_name="Test Client"
        )
        
        slides = [
            GeneratedSlide(title="Slide 1", content=["Point 1"]),
            GeneratedSlide(title="Slide 2", content=["Point 2"]),
            GeneratedSlide(title="Slide 3", content=["Point 3"])
        ]
        
        spec = PresentationSpec(
            project=project,
            slides=slides,
            template_path=Path("template.pptx"),
            output_path=Path("output.pptx")
        )
        
        assert len(spec.slides) == 3
        assert spec.project.client_name == "Test Client"

    def test_slide_count_validation(self):
        """Test slide count validation."""
        project = ProjectDescription(
            description="Test project description",
            client_name="Test Client"
        )
        
        # Too few slides
        with pytest.raises(ValidationError):
            PresentationSpec(
                project=project,
                slides=[GeneratedSlide(title="Slide 1", content=["Point 1"])],  # Only 1 slide
                template_path=Path("template.pptx"),
                output_path=Path("output.pptx")
            )
        
        # Too many slides
        too_many_slides = [
            GeneratedSlide(title=f"Slide {i}", content=[f"Point {i}"])
            for i in range(20)  # 20 slides (max is 15)
        ]
        
        with pytest.raises(ValidationError):
            PresentationSpec(
                project=project,
                slides=too_many_slides,
                template_path=Path("template.pptx"),
                output_path=Path("output.pptx")
            )


class TestDocumentAnalysisResult:
    """Test cases for DocumentAnalysisResult model."""

    def test_valid_document_analysis_result(self):
        """Test creation of valid DocumentAnalysisResult."""
        result = DocumentAnalysisResult(
            analysis="Test analysis",
            source_documents=5,
            technologies=["Python", "AWS"],
            approaches=["Agile", "DevOps"],
            case_studies=["Case 1", "Case 2"],
            key_themes=["Cloud", "AI"]
        )
        
        assert result.analysis == "Test analysis"
        assert result.source_documents == 5
        assert len(result.technologies) == 2

    def test_source_documents_validation(self):
        """Test source documents count validation."""
        with pytest.raises(ValidationError):
            DocumentAnalysisResult(
                analysis="Test analysis",
                source_documents=-1  # Invalid negative count
            )

    def test_default_lists(self):
        """Test default empty lists for optional fields."""
        result = DocumentAnalysisResult(
            analysis="Test analysis",
            source_documents=0
        )
        
        assert result.technologies == []
        assert result.approaches == []
        assert result.case_studies == []
        assert result.key_themes == []


class TestProcessingStatus:
    """Test cases for ProcessingStatus model."""

    def test_valid_processing_status(self):
        """Test creation of valid ProcessingStatus."""
        status = ProcessingStatus(
            status="processing",
            progress=0.5,
            message="Processing documents...",
            current_step="Document analysis",
            total_steps=5,
            completed_steps=2
        )
        
        assert status.status == "processing"
        assert status.progress == 0.5
        assert status.completed_steps == 2

    def test_progress_validation(self):
        """Test progress value validation."""
        # Test invalid progress values
        with pytest.raises(ValidationError):
            ProcessingStatus(
                status="processing",
                progress=1.5  # > 1.0
            )
        
        with pytest.raises(ValidationError):
            ProcessingStatus(
                status="processing",
                progress=-0.1  # < 0.0
            )

    def test_default_values(self):
        """Test default values for optional fields."""
        status = ProcessingStatus(status="processing")
        
        assert status.progress == 0.0
        assert status.message == ""
        assert status.error is None
        assert status.total_steps == 5
        assert status.completed_steps == 0


class TestFileUploadInfo:
    """Test cases for FileUploadInfo model."""

    def test_valid_file_upload_info(self):
        """Test creation of valid FileUploadInfo."""
        info = FileUploadInfo(
            filename="test.pptx",
            file_type="pptx",
            file_size=1024000,
            processing_status="completed",
            extracted_content_count=5
        )
        
        assert info.filename == "test.pptx"
        assert info.file_type == "pptx"
        assert info.file_size == 1024000
        assert info.extracted_content_count == 5

    def test_file_size_validation(self):
        """Test file size validation."""
        with pytest.raises(ValidationError):
            FileUploadInfo(
                filename="test.pptx",
                file_type="pptx",
                file_size=-100  # Invalid negative size
            )

    def test_default_timestamp(self):
        """Test default upload timestamp."""
        info = FileUploadInfo(
            filename="test.pptx",
            file_type="pptx",
            file_size=1024
        )
        
        assert isinstance(info.upload_timestamp, datetime)
        assert info.processing_status == "pending"
        assert info.extracted_content_count == 0


@pytest.mark.integration
class TestModelIntegration:
    """Integration tests for model interactions."""

    def test_complete_presentation_workflow_models(self):
        """Test complete workflow using all models."""
        # Create project
        project = ProjectDescription(
            description="Complete test project for model integration",
            client_name="Integration Test Client",
            key_technologies=["Python", "LangChain"]
        )
        
        # Create extracted content
        extracted_content = [
            ExtractedContent(
                slide_number=1,
                title="Source Slide 1",
                content="Source content 1",
                layout_type="bullet",
                source_file="source.pptx"
            ),
            ExtractedContent(
                slide_number=2,
                title="Source Slide 2",
                content="Source content 2",
                layout_type="bullet",
                source_file="source.pptx"
            )
        ]
        
        # Create analysis results
        doc_analysis = DocumentAnalysisResult(
            analysis="Analysis of source documents",
            source_documents=1,
            technologies=["Python", "AI"],
            approaches=["RAG", "Chain-of-thought"]
        )
        
        project_analysis = ProjectAnalysisResult(
            requirements=["Req 1", "Req 2"],
            technologies=["Python", "LangChain"],
            solution_approaches=["RAG", "LLM"],
            target_audience="Technical team",
            key_objectives=["Obj 1", "Obj 2"]
        )
        
        # Create generated slides
        slides = [
            GeneratedSlide(title="Generated Slide 1", content=["Point 1", "Point 2"]),
            GeneratedSlide(title="Generated Slide 2", content=["Point 3", "Point 4"]),
            GeneratedSlide(title="Generated Slide 3", content=["Point 5", "Point 6"])
        ]
        
        # Create presentation spec
        spec = PresentationSpec(
            project=project,
            slides=slides,
            template_path=Path("template.pptx"),
            output_path=Path("output.pptx")
        )
        
        # Verify everything is properly connected
        assert spec.project.client_name == "Integration Test Client"
        assert len(spec.slides) == 3
        assert len(extracted_content) == 2
        assert doc_analysis.source_documents == 1
        assert len(project_analysis.requirements) == 2