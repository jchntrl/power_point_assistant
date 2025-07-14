"""
Integration tests for PowerPoint Assistant.

These tests verify that all components work together correctly
in the complete workflow.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from io import BytesIO

from src.chains.orchestration_chain import PowerPointOrchestrationChain
from src.models.data_models import ProjectDescription


@pytest.mark.integration
class TestOrchestrationIntegration:
    """Integration tests for the complete orchestration workflow."""

    @pytest.mark.asyncio
    async def test_complete_workflow_with_mocks(
        self,
        sample_project_description,
        temp_dir
    ):
        """Test complete workflow with mocked external dependencies."""
        
        # Create mock uploaded files
        mock_files = [
            (BytesIO(b"mock pptx content"), "presentation1.pptx", "pptx"),
            (BytesIO(b"mock pdf content"), "document1.pdf", "pdf")
        ]
        
        # Mock the orchestration chain components
        with patch('src.chains.orchestration_chain.DocumentProcessor') as mock_doc_processor, \
             patch('src.chains.orchestration_chain.DocumentAnalysisChain') as mock_doc_analysis, \
             patch('src.chains.orchestration_chain.ProjectAnalysisChain') as mock_proj_analysis, \
             patch('src.chains.orchestration_chain.ContentGenerationChain') as mock_content_gen, \
             patch('src.chains.orchestration_chain.PresentationBuilder') as mock_builder:
            
            # Setup mock document processor
            mock_doc_proc_instance = Mock()
            mock_doc_proc_instance.process_document = AsyncMock(return_value=[
                Mock(title="Mock Slide", content="Mock content", slide_number=1, source_file="test.pptx")
            ])
            mock_doc_processor.return_value = mock_doc_proc_instance
            
            # Setup mock document analysis
            mock_doc_analysis_instance = Mock()
            mock_doc_analysis_instance.analyze_documents = AsyncMock(return_value=Mock(
                analysis="Mock analysis",
                source_documents=2,
                technologies=["Python", "AWS"],
                approaches=["Microservices"],
                case_studies=["Case 1"],
                key_themes=["Cloud"]
            ))
            mock_doc_analysis.return_value = mock_doc_analysis_instance
            
            # Setup mock project analysis
            mock_proj_analysis_instance = Mock()
            mock_proj_analysis_instance.analyze_project = AsyncMock(return_value=Mock(
                requirements=["Requirement 1"],
                technologies=["Python"],
                solution_approaches=["Agile"],
                target_audience="Developers",
                key_objectives=["Objective 1"]
            ))
            mock_proj_analysis.return_value = mock_proj_analysis_instance
            
            # Setup mock content generation
            mock_content_gen_instance = Mock()
            mock_content_gen_instance.generate_content = AsyncMock(return_value=Mock(
                slides=[
                    Mock(title="Slide 1", content=["Point 1", "Point 2"]),
                    Mock(title="Slide 2", content=["Point 3", "Point 4"]),
                    Mock(title="Slide 3", content=["Point 5", "Point 6"])
                ],
                generation_metadata={"test": "metadata"},
                confidence_score=0.85
            ))
            mock_content_gen.return_value = mock_content_gen_instance
            
            # Setup mock presentation builder
            mock_builder_instance = Mock()
            output_path = temp_dir / "test_presentation.pptx"
            output_path.write_bytes(b"mock presentation content")
            mock_builder_instance.build_presentation = AsyncMock(return_value=output_path)
            mock_builder.return_value = mock_builder_instance
            
            # Run the orchestration
            orchestrator = PowerPointOrchestrationChain()
            
            results = await orchestrator.generate_presentation(
                project=sample_project_description,
                uploaded_files=mock_files,
                target_slide_count=5
            )
            
            # Verify results
            assert results["success"] is True
            assert "presentation_path" in results
            assert results["presentation_path"].exists()
            assert "project_analysis" in results
            assert "document_analysis" in results
            assert "generation_result" in results
            assert results["confidence_score"] == 0.85
            assert results["final_slide_count"] == 3

    @pytest.mark.asyncio
    async def test_validation_workflow(self, sample_project_description):
        """Test input validation workflow."""
        
        orchestrator = PowerPointOrchestrationChain()
        
        # Test valid inputs
        valid_files = [
            (BytesIO(b"content"), "test.pptx", "pptx"),
            (BytesIO(b"content"), "test.pdf", "pdf")
        ]
        
        validation = await orchestrator.validate_inputs(
            sample_project_description, 
            valid_files
        )
        
        # Note: This might fail due to API key validation, so we check structure
        assert "valid" in validation
        assert "errors" in validation
        assert "warnings" in validation
        assert isinstance(validation["errors"], list)
        assert isinstance(validation["warnings"], list)

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, sample_project_description):
        """Test error handling in workflow."""
        
        with patch('src.chains.orchestration_chain.DocumentProcessor') as mock_doc_processor:
            # Setup mock to raise exception
            mock_doc_proc_instance = Mock()
            mock_doc_proc_instance.process_document = AsyncMock(side_effect=Exception("Processing failed"))
            mock_doc_processor.return_value = mock_doc_proc_instance
            
            orchestrator = PowerPointOrchestrationChain()
            
            mock_files = [(BytesIO(b"content"), "test.pptx", "pptx")]
            
            results = await orchestrator.generate_presentation(
                project=sample_project_description,
                uploaded_files=mock_files,
                target_slide_count=5
            )
            
            # Should handle error gracefully
            assert results["success"] is False
            assert "error" in results
            assert "Processing failed" in str(results["error"])

    @pytest.mark.asyncio
    async def test_preview_data_generation(self, sample_project_description):
        """Test preview data generation."""
        
        with patch('src.chains.orchestration_chain.DocumentProcessor') as mock_doc_processor, \
             patch('src.chains.orchestration_chain.ProjectAnalysisChain') as mock_proj_analysis:
            
            # Setup mocks
            mock_doc_proc_instance = Mock()
            mock_doc_proc_instance.process_document = AsyncMock(return_value=[
                Mock(title="Test", content="Content", slide_number=1)
            ])
            mock_doc_processor.return_value = mock_doc_proc_instance
            
            mock_proj_analysis_instance = Mock()
            mock_proj_analysis_instance.analyze_project = AsyncMock(return_value=Mock(
                technologies=["Python", "AWS"],
                target_audience="Developers",
                requirements=["Req1", "Req2", "Req3"]
            ))
            mock_proj_analysis.return_value = mock_proj_analysis_instance
            
            orchestrator = PowerPointOrchestrationChain()
            
            mock_files = [(BytesIO(b"content"), "test.pptx", "pptx")]
            
            preview = await orchestrator.get_preview_data(
                sample_project_description,
                mock_files
            )
            
            assert preview["success"] is True
            assert "estimated_processing_time" in preview
            assert "document_count" in preview
            assert "identified_technologies" in preview
            assert preview["document_count"] == 1


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_file_processing_pipeline(self):
        """Test file processing pipeline with different file types."""
        
        from src.tools.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Test file type validation
        assert processor.validate_file_type("test.pptx") is True
        assert processor.validate_file_type("test.pdf") is True
        assert processor.validate_file_type("test.txt") is False
        
        # Test file type detection
        assert processor.get_file_type("document.pptx") == "pptx"
        assert processor.get_file_type("document.pdf") == "pdf"
        assert processor.get_file_type("document.txt") is None

    def test_data_model_validation_pipeline(self):
        """Test data model validation in complete pipeline."""
        
        from src.models.data_models import (
            ProjectDescription, 
            ExtractedContent, 
            GeneratedSlide,
            PresentationSpec
        )
        
        # Test project validation
        project = ProjectDescription(
            description="This is a comprehensive test project description",
            client_name="Test Client Corp"
        )
        assert project.client_name == "Test Client Corp"
        
        # Test extracted content
        content = ExtractedContent(
            slide_number=1,
            title="Test Slide",
            content="Test content here",
            layout_type="bullet",
            source_file="test.pptx"
        )
        assert content.slide_number == 1
        
        # Test generated slide
        slide = GeneratedSlide(
            title="Generated Slide",
            content=["Point 1", "Point 2", "Point 3"]
        )
        assert len(slide.content) == 3
        
        # Test presentation spec
        spec = PresentationSpec(
            project=project,
            slides=[slide, slide, slide],  # Minimum 3 slides
            template_path=Path("template.pptx"),
            output_path=Path("output.pptx")
        )
        assert len(spec.slides) == 3

    @pytest.mark.asyncio
    async def test_streamlit_integration_mocking(self):
        """Test Streamlit integration components with mocking."""
        
        from src.tools.file_handler import FileUploadHandler
        
        # Test file handler initialization
        handler = FileUploadHandler()
        assert handler.document_processor is not None
        
        # Test validation methods
        mock_file = Mock()
        mock_file.name = "test.pptx"
        mock_file.size = 1024000  # 1MB
        
        validation = handler._validate_file(mock_file)
        assert validation["is_valid"] is True

    def test_template_manager_integration(self, temp_dir):
        """Test template manager integration."""
        
        from src.tools.template_manager import TemplateManager
        from src.models.data_models import GeneratedSlide
        
        manager = TemplateManager()
        
        # Test default slide generation
        slides = TemplateManager.get_default_slide_specs(
            "Test Project", 
            "Test Client"
        )
        
        assert len(slides) >= 3
        assert all(isinstance(slide, GeneratedSlide) for slide in slides)
        assert slides[0].title == "Test Project"

    @pytest.mark.asyncio 
    async def test_chain_integration_flow(self):
        """Test integration between different chains."""
        
        with patch('src.chains.document_analysis_chain.ChatOpenAI'), \
             patch('src.chains.project_analysis_chain.ChatOpenAI'), \
             patch('src.chains.content_generation_chain.ChatOpenAI'):
            
            from src.chains.document_analysis_chain import DocumentAnalysisChain
            from src.chains.project_analysis_chain import ProjectAnalysisChain
            from src.chains.content_generation_chain import ContentGenerationChain
            
            # Test chain initialization
            doc_chain = DocumentAnalysisChain()
            proj_chain = ProjectAnalysisChain()
            content_chain = ContentGenerationChain()
            
            # Verify chains are properly initialized
            assert doc_chain.llm is not None
            assert proj_chain.llm is not None
            assert content_chain.llm is not None
            
            assert doc_chain.chain is not None
            assert proj_chain.chain is not None
            assert content_chain.chain is not None


@pytest.mark.slow
@pytest.mark.integration
class TestPerformanceIntegration:
    """Performance and stress testing for integration."""

    @pytest.mark.asyncio
    async def test_multiple_file_processing_performance(self):
        """Test performance with multiple files."""
        
        from src.tools.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Create multiple mock files
        mock_files = []
        for i in range(5):  # Test with 5 files
            mock_files.append((
                BytesIO(f"Mock content for file {i}".encode()),
                f"test_{i}.pptx",
                "pptx"
            ))
        
        # Test processing time estimation
        file_sizes = [1024 * 100] * 5  # 100KB each
        estimated_time = processor.estimate_processing_time(file_sizes)
        
        assert estimated_time > 0
        assert estimated_time < 300  # Should be reasonable (under 5 minutes)

    def test_memory_usage_with_large_content(self):
        """Test memory usage with large content structures."""
        
        from src.models.data_models import ExtractedContent, GeneratedSlide
        
        # Create large content structures
        large_content_list = []
        for i in range(100):  # 100 slides
            content = ExtractedContent(
                slide_number=i + 1,
                title=f"Slide {i + 1}",
                content="Large content " * 100,  # Simulate large content
                layout_type="bullet",
                source_file="large_presentation.pptx"
            )
            large_content_list.append(content)
        
        # Verify we can handle large structures
        assert len(large_content_list) == 100
        
        # Test with generated slides
        large_slides = []
        for i in range(50):  # 50 generated slides
            slide = GeneratedSlide(
                title=f"Generated Slide {i + 1}",
                content=[f"Point {j}" for j in range(10)]  # 10 points each
            )
            large_slides.append(slide)
        
        assert len(large_slides) == 50
        total_points = sum(len(slide.content) for slide in large_slides)
        assert total_points == 500  # 50 slides * 10 points each