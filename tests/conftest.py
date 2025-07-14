"""
Pytest configuration and fixtures for PowerPoint Assistant tests.
"""

import pytest
from pathlib import Path
import os
import tempfile
from unittest.mock import Mock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def pytest_addoption(parser):
    """Add custom command line options for pytest."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests that require external services"
    )
    parser.addoption(
        "--run-slow",
        action="store_true", 
        default=False,
        help="run slow tests"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring external services"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    if not config.getoption("--run-integration"):
        # Skip integration tests unless --run-integration is passed
        skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
    
    if not config.getoption("--run-slow"):
        # Skip slow tests unless --run-slow is passed
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_env = {
        "OPENAI_API_KEY": "test-api-key-sk-1234567890",
        "OPENAI_MODEL": "gpt-4",
        "MAX_FILE_SIZE_MB": "10",
        "MAX_FILES": "5",
        "LOG_LEVEL": "INFO"
    }
    
    os.environ.update(test_env)
    
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_extracted_content():
    """Sample extracted content for testing."""
    from src.models.data_models import ExtractedContent
    
    return [
        ExtractedContent(
            slide_number=1,
            title="Introduction",
            content="Welcome to our presentation about cloud architecture",
            layout_type="title",
            source_file="sample.pptx",
            file_type="pptx"
        ),
        ExtractedContent(
            slide_number=2,
            title="Technical Overview",
            content="Our solution uses Python, AWS, and microservices architecture",
            layout_type="bullet",
            source_file="sample.pptx",
            file_type="pptx"
        ),
        ExtractedContent(
            slide_number=3,
            title="Implementation Plan",
            content="Phase 1: Setup\nPhase 2: Development\nPhase 3: Deployment",
            layout_type="bullet",
            source_file="sample.pptx",
            file_type="pptx"
        )
    ]


@pytest.fixture
def sample_project_description():
    """Sample project description for testing."""
    from src.models.data_models import ProjectDescription
    
    return ProjectDescription(
        description="Build a modern cloud-native application with real-time data processing capabilities",
        client_name="Acme Corporation",
        industry="Technology",
        timeline="6 months",
        budget_range="$250K-500K",
        key_technologies=["Python", "AWS", "React", "PostgreSQL"]
    )


@pytest.fixture
def sample_generated_slides():
    """Sample generated slides for testing."""
    from src.models.data_models import GeneratedSlide
    
    return [
        GeneratedSlide(
            title="Executive Summary",
            content=[
                "Project overview and objectives",
                "Key benefits and value proposition",
                "High-level timeline and deliverables"
            ],
            layout_type="bullet",
            notes="Opening slide introducing the project"
        ),
        GeneratedSlide(
            title="Technical Architecture",
            content=[
                "Cloud-native microservices design",
                "Event-driven data processing",
                "Scalable and resilient infrastructure"
            ],
            layout_type="bullet",
            notes="Technical details of the proposed solution"
        ),
        GeneratedSlide(
            title="Implementation Roadmap",
            content=[
                "Phase 1: Foundation setup (Month 1-2)",
                "Phase 2: Core development (Month 3-4)",
                "Phase 3: Testing and deployment (Month 5-6)"
            ],
            layout_type="bullet",
            notes="Project timeline and milestones"
        )
    ]


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    
    # Mock successful response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """
    {
        "requirements": ["Scalable architecture", "Real-time processing"],
        "technologies": ["Python", "AWS", "React"],
        "solution_approaches": ["Microservices", "Event-driven"],
        "target_audience": "Technical team",
        "key_objectives": ["Performance", "Scalability"]
    }
    """
    
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def sample_document_analysis():
    """Sample document analysis result for testing."""
    from src.models.data_models import DocumentAnalysisResult
    
    return DocumentAnalysisResult(
        analysis="Comprehensive analysis of uploaded documents",
        source_documents=3,
        technologies=["Python", "AWS", "Docker", "Kubernetes"],
        approaches=["Microservices", "DevOps", "Agile"],
        case_studies=["E-commerce platform", "Data analytics system"],
        key_themes=["Cloud migration", "Digital transformation", "Automation"]
    )


@pytest.fixture
def sample_project_analysis():
    """Sample project analysis result for testing."""
    from src.models.data_models import ProjectAnalysisResult
    
    return ProjectAnalysisResult(
        requirements=["High availability", "Real-time processing", "Data security"],
        technologies=["Python", "AWS", "React", "PostgreSQL"],
        solution_approaches=["Microservices", "Event-driven architecture", "CI/CD"],
        target_audience="Technical stakeholders and business leaders",
        key_objectives=["Improve performance", "Reduce costs", "Enhance user experience"]
    )


@pytest.fixture
def mock_streamlit_file():
    """Mock Streamlit uploaded file for testing."""
    from io import BytesIO
    
    mock_file = Mock()
    mock_file.name = "test_document.pptx"
    mock_file.size = 1024000  # 1MB
    mock_file.read.return_value = b"mock file content"
    mock_file.seek = Mock()
    
    return mock_file


@pytest.fixture(autouse=True)
def setup_test_environment(mock_env_vars, temp_dir):
    """Set up test environment automatically for all tests."""
    # Ensure settings are loaded with test environment
    try:
        from src.config.settings import settings
        # Force reload settings with test environment
        settings.__init__()
    except ImportError:
        # Settings not available, skip
        pass
    
    yield
    
    # Cleanup after test
    pass


class TestHelpers:
    """Helper functions for tests."""
    
    @staticmethod
    def create_mock_presentation_file(content: str = "test content") -> BytesIO:
        """Create a mock presentation file for testing."""
        return BytesIO(content.encode())
    
    @staticmethod
    def assert_valid_extracted_content(content_list):
        """Assert that extracted content list is valid."""
        from src.models.data_models import ExtractedContent
        
        assert isinstance(content_list, list)
        assert len(content_list) > 0
        
        for content in content_list:
            assert isinstance(content, ExtractedContent)
            assert content.slide_number > 0
            assert len(content.title.strip()) > 0
            assert len(content.source_file.strip()) > 0
    
    @staticmethod
    def assert_valid_generated_slides(slides_list):
        """Assert that generated slides list is valid."""
        from src.models.data_models import GeneratedSlide
        
        assert isinstance(slides_list, list)
        assert len(slides_list) >= 3  # Minimum slides
        
        for slide in slides_list:
            assert isinstance(slide, GeneratedSlide)
            assert len(slide.title.strip()) > 0
            assert len(slide.content) > 0
            assert all(len(point.strip()) > 0 for point in slide.content)


# Make test helpers available
@pytest.fixture
def test_helpers():
    """Provide test helper functions."""
    return TestHelpers