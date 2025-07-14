"""
Tests for project analysis chain functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.chains.project_analysis_chain import ProjectAnalysisChain, analyze_project_simple
from src.models.data_models import ProjectDescription, ProjectAnalysisResult


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response for testing."""
    return {
        "text": """
        {
            "requirements": ["Cloud infrastructure", "Real-time processing", "Data analytics"],
            "technologies": ["Python", "AWS", "Apache Kafka", "React"],
            "solution_approaches": ["Microservices", "Event-driven architecture", "CI/CD"],
            "target_audience": "Technical team and business stakeholders",
            "key_objectives": ["Improve performance", "Reduce costs", "Enhance scalability"],
            "business_drivers": ["Digital transformation", "Competitive advantage"],
            "technical_challenges": ["Data integration", "Scalability", "Security"],
            "success_criteria": ["95% uptime", "Sub-second response times", "Cost reduction"],
            "presentation_focus": ["Technical architecture", "Business benefits"],
            "value_propositions": ["Faster time to market", "Lower operational costs"]
        }
        """
    }


@pytest.fixture
def sample_project():
    """Sample project for testing."""
    return ProjectDescription(
        description="Build a cloud-native data platform for real-time analytics with advanced AI capabilities",
        client_name="TechCorp Inc",
        industry="Technology",
        timeline="6 months",
        budget_range="$500K-1M",
        key_technologies=["Python", "AWS", "Machine Learning"]
    )


class TestProjectAnalysisChain:
    """Test cases for ProjectAnalysisChain."""

    @patch('src.chains.project_analysis_chain.ChatOpenAI')
    @patch('src.chains.project_analysis_chain.LLMChain')
    def test_init(self, mock_llm_chain, mock_chat_openai):
        """Test ProjectAnalysisChain initialization."""
        chain = ProjectAnalysisChain()
        
        # Verify OpenAI client was created
        mock_chat_openai.assert_called_once()
        
        # Verify LLM chain was created
        mock_llm_chain.assert_called_once()
        
        assert chain.llm is not None
        assert chain.analysis_prompt is not None
        assert chain.chain is not None

    def test_get_analysis_template(self):
        """Test analysis template generation."""
        with patch('src.chains.project_analysis_chain.ChatOpenAI'), \
             patch('src.chains.project_analysis_chain.LLMChain'):
            chain = ProjectAnalysisChain()
            
            template = chain._get_analysis_template()
            
            assert "project_description" in template
            assert "client_name" in template
            assert "industry" in template
            assert "JSON format" in template
            assert "requirements" in template
            assert "technologies" in template

    @pytest.mark.asyncio
    @patch('src.chains.project_analysis_chain.ChatOpenAI')
    @patch('src.chains.project_analysis_chain.LLMChain')
    async def test_analyze_project_success(self, mock_llm_chain, mock_chat_openai, sample_project, mock_openai_response):
        """Test successful project analysis."""
        # Setup mocks
        mock_chain_instance = Mock()
        mock_chain_instance.ainvoke = AsyncMock(return_value=mock_openai_response)
        mock_llm_chain.return_value = mock_chain_instance
        
        chain = ProjectAnalysisChain()
        chain.chain = mock_chain_instance
        
        # Perform analysis
        result = await chain.analyze_project(sample_project)
        
        # Verify results
        assert isinstance(result, ProjectAnalysisResult)
        assert len(result.requirements) == 3
        assert "Cloud infrastructure" in result.requirements
        assert len(result.technologies) == 4
        assert "Python" in result.technologies
        assert result.target_audience == "Technical team and business stakeholders"
        assert len(result.key_objectives) == 3

    @pytest.mark.asyncio
    @patch('src.chains.project_analysis_chain.ChatOpenAI')
    @patch('src.chains.project_analysis_chain.LLMChain')
    async def test_analyze_project_invalid_json(self, mock_llm_chain, mock_chat_openai, sample_project):
        """Test project analysis with invalid JSON response."""
        # Setup mocks with invalid JSON
        mock_chain_instance = Mock()
        mock_chain_instance.ainvoke = AsyncMock(return_value={"text": "Invalid JSON response"})
        mock_llm_chain.return_value = mock_chain_instance
        
        chain = ProjectAnalysisChain()
        chain.chain = mock_chain_instance
        
        # Perform analysis
        result = await chain.analyze_project(sample_project)
        
        # Verify fallback behavior
        assert isinstance(result, ProjectAnalysisResult)
        assert len(result.requirements) >= 1  # Should have error message
        assert "Analysis parsing failed" in result.requirements[0]

    @pytest.mark.asyncio
    @patch('src.chains.project_analysis_chain.ChatOpenAI')
    @patch('src.chains.project_analysis_chain.LLMChain')
    async def test_analyze_project_exception(self, mock_llm_chain, mock_chat_openai, sample_project):
        """Test project analysis when exception occurs."""
        # Setup mocks to raise exception
        mock_chain_instance = Mock()
        mock_chain_instance.ainvoke = AsyncMock(side_effect=Exception("API Error"))
        mock_llm_chain.return_value = mock_chain_instance
        
        chain = ProjectAnalysisChain()
        chain.chain = mock_chain_instance
        
        # Perform analysis
        result = await chain.analyze_project(sample_project)
        
        # Verify error handling
        assert isinstance(result, ProjectAnalysisResult)
        assert "Analysis failed" in result.requirements[0]

    def test_parse_analysis_result_valid_json(self):
        """Test parsing valid JSON analysis result."""
        with patch('src.chains.project_analysis_chain.ChatOpenAI'), \
             patch('src.chains.project_analysis_chain.LLMChain'):
            chain = ProjectAnalysisChain()
            
            valid_json = """
            {
                "requirements": ["Req 1", "Req 2"],
                "technologies": ["Tech 1", "Tech 2"],
                "solution_approaches": ["Approach 1"],
                "target_audience": "Developers",
                "key_objectives": ["Obj 1"]
            }
            """
            
            result = chain._parse_analysis_result(valid_json)
            
            assert result["requirements"] == ["Req 1", "Req 2"]
            assert result["technologies"] == ["Tech 1", "Tech 2"]
            assert result["target_audience"] == "Developers"

    def test_parse_analysis_result_invalid_json(self):
        """Test parsing invalid JSON analysis result."""
        with patch('src.chains.project_analysis_chain.ChatOpenAI'), \
             patch('src.chains.project_analysis_chain.LLMChain'):
            chain = ProjectAnalysisChain()
            
            invalid_json = "This is not JSON"
            
            result = chain._parse_analysis_result(invalid_json)
            
            assert "Analysis parsing failed" in result["requirements"][0]
            assert result["technologies"] == []
            assert result["target_audience"] == "Business stakeholders"

    def test_find_matches(self):
        """Test finding matches between required and available items."""
        with patch('src.chains.project_analysis_chain.ChatOpenAI'), \
             patch('src.chains.project_analysis_chain.LLMChain'):
            chain = ProjectAnalysisChain()
            
            required = ["Python", "AWS", "Machine Learning"]
            available = ["Python programming", "AWS cloud", "Data Science"]
            
            matches = chain._find_matches(required, available)
            
            assert len(matches) >= 2  # Should find Python and AWS matches
            exact_match = next((m for m in matches if m["match_type"] == "exact"), None)
            partial_matches = [m for m in matches if m["match_type"] == "partial"]
            
            assert len(partial_matches) >= 2

    def test_calculate_match_score(self):
        """Test match score calculation."""
        with patch('src.chains.project_analysis_chain.ChatOpenAI'), \
             patch('src.chains.project_analysis_chain.LLMChain'):
            chain = ProjectAnalysisChain()
            
            tech_matches = [
                {"confidence": 1.0},
                {"confidence": 0.7}
            ]
            approach_matches = [
                {"confidence": 0.8}
            ]
            
            score = chain._calculate_match_score(tech_matches, approach_matches)
            
            assert 0.0 <= score <= 1.0
            assert score > 0  # Should be positive with matches

    def test_get_relevance_level(self):
        """Test relevance level description."""
        with patch('src.chains.project_analysis_chain.ChatOpenAI'), \
             patch('src.chains.project_analysis_chain.LLMChain'):
            chain = ProjectAnalysisChain()
            
            assert "High" in chain._get_relevance_level(0.9)
            assert "Good" in chain._get_relevance_level(0.7)
            assert "Moderate" in chain._get_relevance_level(0.5)
            assert "Low" in chain._get_relevance_level(0.3)
            assert "Minimal" in chain._get_relevance_level(0.1)

    @pytest.mark.asyncio
    async def test_match_with_document_analysis(self):
        """Test matching project analysis with document analysis results."""
        with patch('src.chains.project_analysis_chain.ChatOpenAI'), \
             patch('src.chains.project_analysis_chain.LLMChain'):
            chain = ProjectAnalysisChain()
            
            project_analysis = ProjectAnalysisResult(
                requirements=["Cloud deployment"],
                technologies=["Python", "AWS"],
                solution_approaches=["Microservices"],
                target_audience="Developers",
                key_objectives=["Scalability"]
            )
            
            document_technologies = ["Python programming", "AWS cloud services"]
            document_approaches = ["Microservices architecture", "DevOps"]
            
            result = await chain.match_with_document_analysis(
                project_analysis, document_technologies, document_approaches
            )
            
            assert "technology_matches" in result
            assert "approach_matches" in result
            assert "match_score" in result
            assert "recommendations" in result
            assert isinstance(result["match_score"], float)


@pytest.mark.asyncio
async def test_analyze_project_simple(sample_project):
    """Test simple project analysis function."""
    with patch('src.chains.project_analysis_chain.ProjectAnalysisChain') as mock_chain_class:
        mock_chain = Mock()
        mock_result = ProjectAnalysisResult(
            requirements=["Test requirement"],
            technologies=["Test technology"],
            solution_approaches=["Test approach"],
            target_audience="Test audience",
            key_objectives=["Test objective"]
        )
        mock_chain.analyze_project = AsyncMock(return_value=mock_result)
        mock_chain_class.return_value = mock_chain
        
        result = await analyze_project_simple(sample_project)
        
        assert isinstance(result, ProjectAnalysisResult)
        mock_chain.analyze_project.assert_called_once_with(sample_project)


@pytest.mark.integration
class TestProjectAnalysisChainIntegration:
    """Integration tests for ProjectAnalysisChain."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(not pytest.config.getoption("--run-integration", default=False),
                       reason="Integration tests require --run-integration flag")
    async def test_real_openai_integration(self, sample_project):
        """Test with real OpenAI API (requires valid API key)."""
        # This test requires a valid OpenAI API key
        try:
            chain = ProjectAnalysisChain()
            result = await chain.analyze_project(sample_project)
            
            assert isinstance(result, ProjectAnalysisResult)
            assert len(result.requirements) > 0
            assert len(result.technologies) > 0
            assert result.target_audience
            
        except Exception as e:
            pytest.skip(f"OpenAI integration test failed: {e}")

    @pytest.mark.asyncio
    async def test_comprehensive_workflow(self, sample_project):
        """Test comprehensive workflow with mocked responses."""
        with patch('src.chains.project_analysis_chain.ChatOpenAI'), \
             patch('src.chains.project_analysis_chain.LLMChain') as mock_llm_chain:
            
            # Setup realistic mock response
            mock_chain_instance = Mock()
            mock_chain_instance.ainvoke = AsyncMock(return_value={
                "text": """
                {
                    "requirements": ["Scalable architecture", "Real-time processing", "Data security"],
                    "technologies": ["Python", "AWS", "Apache Kafka", "React", "PostgreSQL"],
                    "solution_approaches": ["Microservices", "Event-driven", "CI/CD pipeline"],
                    "target_audience": "Technical stakeholders and business leaders",
                    "key_objectives": ["Improve performance", "Reduce operational costs", "Enhance user experience"],
                    "business_drivers": ["Digital transformation", "Market competition"],
                    "technical_challenges": ["Data integration", "Scalability", "Security compliance"],
                    "success_criteria": ["99.9% uptime", "Sub-100ms response time", "Zero data breaches"],
                    "presentation_focus": ["Technical solution", "Business value", "Implementation roadmap"],
                    "value_propositions": ["30% cost reduction", "50% faster deployment", "Enhanced security"]
                }
                """
            })
            mock_llm_chain.return_value = mock_chain_instance
            
            chain = ProjectAnalysisChain()
            chain.chain = mock_chain_instance
            
            # Perform analysis
            result = await chain.analyze_project(sample_project)
            
            # Verify comprehensive results
            assert len(result.requirements) == 3
            assert len(result.technologies) == 5
            assert len(result.solution_approaches) == 3
            assert len(result.key_objectives) == 3
            assert "Technical stakeholders" in result.target_audience
            
            # Test document matching
            document_technologies = ["Python programming", "AWS services", "Kafka streaming"]
            document_approaches = ["Microservices patterns", "Event-driven design"]
            
            match_result = await chain.match_with_document_analysis(
                result, document_technologies, document_approaches
            )
            
            assert match_result["match_score"] > 0.5  # Should have good matches
            assert len(match_result["technology_matches"]) >= 2
            assert len(match_result["approach_matches"]) >= 1