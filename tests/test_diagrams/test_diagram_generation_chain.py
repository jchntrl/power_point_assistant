"""
Tests for diagram generation chain functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.chains.diagram_generation_chain import DiagramGenerationChain
from src.models.data_models import (
    DiagramGenerationResult,
    DocumentAnalysisResult,
    ProjectAnalysisResult,
    ProjectDescription,
    GeneratedDiagram
)


class TestDiagramGenerationChain:
    """Test cases for DiagramGenerationChain class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.chain = DiagramGenerationChain()

    def test_initialization(self):
        """Test proper initialization of DiagramGenerationChain."""
        assert self.chain.llm is not None
        assert self.chain.diagram_prompt is not None
        assert self.chain.chain is not None
        assert self.chain.diagram_generator is not None
        assert self.chain.diagram_styler is not None

    def test_summarize_project_analysis(self):
        """Test project analysis summarization."""
        project_analysis = ProjectAnalysisResult(
            requirements=["Scalable architecture", "Real-time processing"],
            technologies=["AWS", "Python", "React"],
            solution_approaches=["Microservices", "Event-driven"],
            target_audience="Technical team",
            technical_challenges=["High throughput", "Data consistency"]
        )
        
        summary = self.chain._summarize_project_analysis(project_analysis)
        
        assert isinstance(summary, str)
        assert "Scalable architecture" in summary
        assert "AWS" in summary
        assert "Microservices" in summary
        assert "Technical team" in summary

    def test_summarize_document_analysis(self):
        """Test document analysis summarization."""
        document_analysis = DocumentAnalysisResult(
            analysis="Comprehensive analysis of technical capabilities",
            source_documents=3,
            technologies=["AWS Lambda", "DynamoDB", "API Gateway"],
            approaches=["Serverless", "Microservices"],
            case_studies=["E-commerce platform", "IoT analytics"]
        )
        
        summary = self.chain._summarize_document_analysis(document_analysis)
        
        assert isinstance(summary, str)
        assert "AWS Lambda" in summary
        assert "Serverless" in summary
        assert "E-commerce platform" in summary

    def test_parse_diagram_specifications_valid_json(self):
        """Test parsing valid diagram specifications."""
        valid_json = '''
        {
            "diagrams": [
                {
                    "diagram_type": "microservices",
                    "title": "Test Architecture",
                    "components": [
                        {
                            "name": "API Gateway",
                            "component_type": "api",
                            "icon_provider": "aws",
                            "icon_name": "APIGateway"
                        }
                    ],
                    "connections": [],
                    "layout_direction": "TB"
                }
            ],
            "analysis_metadata": {
                "architecture_pattern": "microservices",
                "technical_confidence": 0.8
            }
        }
        '''
        
        result = self.chain._parse_diagram_specifications(valid_json)
        
        assert "diagrams" in result
        assert "analysis_metadata" in result
        assert len(result["diagrams"]) == 1
        assert result["diagrams"][0]["title"] == "Test Architecture"

    def test_parse_diagram_specifications_invalid_json(self):
        """Test parsing invalid JSON."""
        invalid_json = "This is not valid JSON"
        
        result = self.chain._parse_diagram_specifications(invalid_json)
        
        assert "diagrams" in result
        assert "analysis_metadata" in result
        assert len(result["diagrams"]) == 0
        assert "error" in result["analysis_metadata"]

    def test_validate_diagram_spec_valid(self):
        """Test validation of valid diagram specification."""
        valid_spec = {
            "diagram_type": "microservices",
            "title": "Valid Architecture",
            "components": [
                {
                    "name": "Service A",
                    "component_type": "service",
                    "icon_provider": "aws"
                },
                {
                    "name": "Service B", 
                    "component_type": "service",
                    "icon_provider": "aws"
                }
            ]
        }
        
        is_valid = self.chain._validate_diagram_spec(valid_spec)
        assert is_valid is True

    def test_validate_diagram_spec_invalid(self):
        """Test validation of invalid diagram specifications."""
        # Missing required fields
        invalid_spec1 = {
            "title": "Missing Type"
        }
        assert self.chain._validate_diagram_spec(invalid_spec1) is False
        
        # Insufficient components
        invalid_spec2 = {
            "diagram_type": "microservices",
            "title": "Too Few Components",
            "components": [
                {"name": "Only One", "component_type": "service", "icon_provider": "aws"}
            ]
        }
        assert self.chain._validate_diagram_spec(invalid_spec2) is False
        
        # Invalid component structure
        invalid_spec3 = {
            "diagram_type": "microservices", 
            "title": "Invalid Components",
            "components": [
                {"name": "Missing Type"},
                {"component_type": "service"}
            ]
        }
        assert self.chain._validate_diagram_spec(invalid_spec3) is False

    def test_create_diagram_spec(self):
        """Test creation of DiagramSpec from parsed data."""
        diagram_data = {
            "diagram_type": "cloud_architecture",
            "title": "Test Cloud Architecture",
            "components": [
                {
                    "name": "Load Balancer",
                    "component_type": "loadbalancer",
                    "icon_provider": "aws",
                    "icon_name": "ELB"
                },
                {
                    "name": "Web Server",
                    "component_type": "compute",
                    "icon_provider": "aws",
                    "icon_name": "EC2"
                }
            ],
            "connections": [
                {
                    "source": "Load Balancer",
                    "target": "Web Server",
                    "connection_type": "arrow"
                }
            ],
            "layout_direction": "TB",
            "clustering": {
                "Frontend": ["Load Balancer", "Web Server"]
            }
        }
        
        spec = self.chain._create_diagram_spec(diagram_data)
        
        assert spec.diagram_type == "cloud_architecture"
        assert spec.title == "Test Cloud Architecture"
        assert len(spec.components) == 2
        assert len(spec.connections) == 1
        assert spec.layout_direction == "TB"
        assert "Frontend" in spec.clustering

    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        # Mock generated diagrams
        mock_diagram1 = MagicMock()
        mock_diagram1.spec.components = [MagicMock() for _ in range(8)]  # Optimal count
        
        mock_diagram2 = MagicMock()
        mock_diagram2.spec.components = [MagicMock() for _ in range(25)]  # Too many
        
        diagrams = [mock_diagram1, mock_diagram2]
        metadata = {
            "technical_confidence": 0.9,
            "architecture_pattern": "microservices"
        }
        
        score = self.chain._calculate_confidence_score(diagrams, metadata)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.4  # Should get base score for having diagrams

    def test_get_styling_config(self):
        """Test styling configuration retrieval."""
        config = self.chain._get_styling_config()
        
        assert isinstance(config, dict)
        assert "style" in config
        assert "dpi" in config
        assert "colors" in config
        assert isinstance(config["colors"], dict)

    @pytest.mark.asyncio
    async def test_generate_diagram_specs_disabled(self):
        """Test diagram generation when disabled in settings."""
        project = ProjectDescription(
            description="Test project",
            client_name="Test Client"
        )
        project_analysis = ProjectAnalysisResult()
        document_analysis = DocumentAnalysisResult(analysis="test", source_documents=0)
        
        with patch('src.chains.diagram_generation_chain.settings') as mock_settings:
            mock_settings.enable_diagram_generation = False
            
            result = await self.chain.generate_diagram_specs(
                project, project_analysis, document_analysis
            )
        
        assert isinstance(result, DiagramGenerationResult)
        assert len(result.diagrams) == 0
        assert result.success_count == 0
        assert "disabled" in result.metadata

    @pytest.mark.asyncio
    async def test_generate_diagram_specs_success(self):
        """Test successful diagram generation."""
        project = ProjectDescription(
            description="Build microservices platform with AWS Lambda",
            client_name="Test Client"
        )
        project_analysis = ProjectAnalysisResult(
            technologies=["AWS", "Lambda"],
            requirements=["Scalability"]
        )
        document_analysis = DocumentAnalysisResult(
            analysis="test analysis",
            source_documents=1,
            technologies=["AWS"]
        )
        
        # Mock LLM response
        mock_llm_response = MagicMock()
        mock_llm_response.content = '''
        {
            "diagrams": [
                {
                    "diagram_type": "microservices",
                    "title": "AWS Microservices",
                    "components": [
                        {
                            "name": "API Gateway",
                            "component_type": "api",
                            "icon_provider": "aws",
                            "icon_name": "APIGateway"
                        },
                        {
                            "name": "Lambda Function",
                            "component_type": "service",
                            "icon_provider": "aws", 
                            "icon_name": "Lambda"
                        }
                    ],
                    "connections": [
                        {
                            "source": "API Gateway",
                            "target": "Lambda Function",
                            "connection_type": "arrow"
                        }
                    ]
                }
            ],
            "analysis_metadata": {
                "architecture_pattern": "microservices",
                "technical_confidence": 0.8
            }
        }
        '''
        
        # Mock diagram generation
        mock_generated_diagram = MagicMock(spec=GeneratedDiagram)
        mock_generated_diagram.spec.title = "AWS Microservices"
        
        with patch.object(self.chain.chain, 'ainvoke', return_value=mock_llm_response):
            with patch.object(self.chain.diagram_generator, 'generate_diagram', 
                            return_value=mock_generated_diagram):
                with patch('src.chains.diagram_generation_chain.settings') as mock_settings:
                    mock_settings.enable_diagram_generation = True
                    
                    result = await self.chain.generate_diagram_specs(
                        project, project_analysis, document_analysis
                    )
        
        assert isinstance(result, DiagramGenerationResult)
        assert result.success_count >= 0
        assert result.total_generation_time_ms >= 0
        assert 0.0 <= result.confidence_score <= 1.0

    @pytest.mark.asyncio
    async def test_generate_diagram_specs_llm_failure(self):
        """Test handling of LLM generation failure."""
        project = ProjectDescription(
            description="Test project",
            client_name="Test Client"
        )
        project_analysis = ProjectAnalysisResult()
        document_analysis = DocumentAnalysisResult(analysis="test", source_documents=0)
        
        # Mock LLM to raise exception
        with patch.object(self.chain.chain, 'ainvoke', side_effect=Exception("LLM Error")):
            with patch('src.chains.diagram_generation_chain.settings') as mock_settings:
                mock_settings.enable_diagram_generation = True
                
                result = await self.chain.generate_diagram_specs(
                    project, project_analysis, document_analysis
                )
        
        assert isinstance(result, DiagramGenerationResult)
        assert len(result.diagrams) == 0
        assert result.success_count == 0
        assert result.confidence_score == 0.0
        assert "error" in result.metadata

    @pytest.mark.asyncio 
    async def test_cleanup_resources(self):
        """Test resource cleanup."""
        with patch.object(self.chain.diagram_generator, 'cleanup_old_diagrams', 
                         return_value=5) as mock_cleanup:
            await self.chain.cleanup_resources()
            mock_cleanup.assert_called_once()

    def test_get_generation_stats(self):
        """Test generation statistics retrieval."""
        with patch.object(self.chain.diagram_generator, 'get_supported_providers',
                         return_value=["aws", "azure"]):
            with patch.object(self.chain.diagram_styler, 'get_available_diagram_types',
                             return_value=["microservices", "data_pipeline"]):
                stats = self.chain.get_generation_stats()
        
        assert isinstance(stats, dict)
        assert "supported_providers" in stats
        assert "available_diagram_types" in stats
        assert "max_components" in stats
        assert "generation_enabled" in stats


class TestDiagramGenerationChainIntegration:
    """Integration tests for DiagramGenerationChain."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_diagram_generation(self):
        """Test end-to-end diagram generation with real components."""
        # This would be a real integration test that requires:
        # - OpenAI API key
        # - Diagrams library installed
        # - Graphviz installed
        pytest.skip("Integration test requires external dependencies")


# Test the convenience function
@pytest.mark.asyncio
async def test_generate_diagrams_simple():
    """Test the convenience function for diagram generation."""
    from src.chains.diagram_generation_chain import generate_diagrams_simple
    
    project = ProjectDescription(
        description="Test project",
        client_name="Test Client"
    )
    project_analysis = ProjectAnalysisResult()
    document_analysis = DocumentAnalysisResult(analysis="test", source_documents=0)
    
    with patch('src.chains.diagram_generation_chain.DiagramGenerationChain') as mock_chain_class:
        mock_chain = AsyncMock()
        mock_result = DiagramGenerationResult(diagrams=[], success_count=0)
        mock_chain.generate_diagram_specs.return_value = mock_result
        mock_chain_class.return_value = mock_chain
        
        result = await generate_diagrams_simple(project, project_analysis, document_analysis)
        
        assert isinstance(result, DiagramGenerationResult)
        mock_chain.generate_diagram_specs.assert_called_once_with(
            project, project_analysis, document_analysis
        )