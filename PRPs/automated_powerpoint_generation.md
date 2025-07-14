name: "Automated PowerPoint Generation for New Prospect Proposals"
description: |

## Purpose
Build a LangChain-powered system with Streamlit frontend that generates branded PowerPoint presentations for new sales prospects by analyzing project descriptions alongside uploaded reference documents (PowerPoint/PDF).

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal
Create a production-ready automated PowerPoint generation system with Streamlit web interface that takes a project description and up to 5 uploaded reference documents (PowerPoint/PDF) as input, then generates a new branded PowerPoint presentation with customized technical solution slides using LangChain chains.

## Why
- **Business value**: Reduces manual effort in creating prospect proposals from days to minutes
- **Integration**: Leverages existing company PowerPoint templates and previous successful proposals
- **Problems solved**: Eliminates repetitive slide creation, ensures consistent branding, and improves proposal quality through RAG-based content retrieval

## What
A Streamlit web application where:
- Users input project descriptions via web form
- Users upload up to 5 reference documents (PowerPoint or PDF files)
- LangChain chains extract and analyze content from uploaded documents
- The system generates a branded PowerPoint using company templates
- Results include 5-10 slides with consistent styling and relevant technical content

### Success Criteria
- [ ] System extracts text content from uploaded PowerPoint and PDF files
- [ ] LangChain chains analyze uploaded content for relevant information
- [ ] LangChain chains generate appropriate technical solution content
- [ ] Final PowerPoint uses company template with correct branding
- [ ] Generated slides are coherent and professionally formatted
- [ ] Streamlit interface provides intuitive file upload and progress feedback

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://python.langchain.com/docs/concepts/chains
  why: Core chain creation patterns for sequential processing
  
- url: https://python.langchain.com/docs/concepts/tools
  why: Tool integration and function calling patterns
  
- url: https://python-pptx.readthedocs.io/en/latest/
  why: PowerPoint manipulation, template loading, placeholder management
  
- url: https://python-pptx.readthedocs.io/en/latest/user/placeholders-using.html
  why: Critical placeholder handling patterns to avoid positioning gotchas
  
- url: https://python-pptx.readthedocs.io/en/latest/user/presentations.html
  why: Template loading and slide layout management
  
- url: https://platform.openai.com/docs/guides/text-generation
  why: LLM integration patterns for content generation
  
- url: https://docs.streamlit.io/
  why: Streamlit web application framework fundamentals
  
- url: https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader
  why: File upload widget for document handling
  
- url: https://python.langchain.com/docs/concepts/document_loaders
  why: Document loading patterns for PowerPoint and PDF processing
  
- url: https://pypdf.readthedocs.io/en/stable/
  why: PDF text extraction and processing
  
- url: https://python.langchain.com/docs/how_to/structured_output
  why: Structured output generation for slide specifications
  
- file: PRPs/templates/prp_base.md
  why: Project structure and validation patterns
```

### Current Codebase tree
```bash
.
├── CLAUDE.md                          # Project rules and conventions
├── INITIAL.md                         # Feature requirements
├── PRPs/
│   ├── templates/prp_base.md         # PRP template pattern
│   └── EXAMPLE_multi_agent_prp.md    # Multi-agent example
├── README.md                          # Project documentation
├── LICENSE                           # License file
├── Keyrus Commercial - Template.pptx  # Company PowerPoint template
├── Keyrus Commercial - Master Deck 2024.pptx  # Example company deck
├── [New] PPT_Template _Keyrus Group(2024).pptx  # Updated template
└── examples/                         # Currently empty
```

### Desired Codebase tree with files to be added and responsibility of file
```bash
.
├── src/
│   ├── __init__.py                   # Package initialization
│   ├── chains/
│   │   ├── __init__.py              # Chains package init
│   │   ├── document_analysis_chain.py # Document content analysis chain
│   │   ├── project_analysis_chain.py # Project requirements analysis chain
│   │   ├── content_generation_chain.py # Content generation chain
│   │   └── orchestration_chain.py   # Main workflow orchestration
│   ├── tools/
│   │   ├── __init__.py              # Tools package init
│   │   ├── document_processor.py    # PowerPoint and PDF text extraction
│   │   ├── file_handler.py          # Streamlit file upload handling
│   │   └── template_manager.py      # PowerPoint template handling
│   ├── models/
│   │   ├── __init__.py              # Models package init
│   │   └── data_models.py           # Pydantic models for data validation
│   ├── config/
│   │   ├── __init__.py              # Config package init
│   │   └── settings.py              # Environment and configuration
│   └── main.py                      # CLI entry point
├── tests/
│   ├── __init__.py                  # Tests package init
│   ├── test_chains/                 # Chain-specific tests
│   ├── test_tools/                  # Tool-specific tests
│   └── test_integration.py          # End-to-end integration tests
├── templates/                       # PowerPoint template storage
│   └── .gitkeep                    # Keep directory in git
├── data/
│   ├── previous_decks/              # Storage for input PowerPoint files
│   └── generated/                   # Output directory for generated presentations
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── pyproject.toml                   # Project configuration and dependencies
└── streamlit_app.py                # Main Streamlit web interface
```

### Known Gotchas of our codebase & Library Quirks
```python
# CRITICAL: LangChain supports both sync and async - use async for I/O operations
# CRITICAL: python-pptx placeholder positioning is all-or-nothing - set all properties together
# CRITICAL: python-pptx placeholder references become invalid after content insertion
# CRITICAL: Use idx values for placeholder access, not positional indexing
# CRITICAL: PowerPoint template inheritance: Master → Layout → Slide
# CRITICAL: Rate limits on OpenAI API - implement proper error handling and retries
# CRITICAL: Large PowerPoint files can cause memory issues during text extraction
# CRITICAL: Document processing must handle both PowerPoint and PDF formats efficiently
# CRITICAL: Company templates (Keyrus) are located in root directory
# CRITICAL: Streamlit file uploads are stored in memory - handle large files efficiently
# CRITICAL: Streamlit session state management for uploaded files and processing results
# CRITICAL: Use python-dotenv and load_env() for environment variables per CLAUDE.md
# CRITICAL: Always create Pytest unit tests and follow 500-line file limit per CLAUDE.md
# CRITICAL: Use relative imports within packages per CLAUDE.md guidelines
```

## Implementation Blueprint

### Data models and structure

Create the core data models to ensure type safety and consistency.
```python
# src/models/data_models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

class ProjectDescription(BaseModel):
    """Input project requirements."""
    description: str = Field(..., min_length=10, description="Detailed project description")
    client_name: str = Field(..., min_length=1, description="Client company name")
    industry: Optional[str] = Field(None, description="Client industry sector")
    budget_range: Optional[str] = Field(None, description="Estimated budget range")
    timeline: Optional[str] = Field(None, description="Project timeline requirements")
    key_technologies: List[str] = Field(default_factory=list, description="Required technologies")

class PowerPointSource(BaseModel):
    """Source PowerPoint file metadata."""
    file_path: Path = Field(..., description="Path to PowerPoint file")
    title: str = Field(..., description="Presentation title")
    client_industry: Optional[str] = Field(None, description="Related industry")
    technologies: List[str] = Field(default_factory=list, description="Technologies mentioned")
    last_modified: datetime = Field(default_factory=datetime.now)

class ExtractedContent(BaseModel):
    """Content extracted from PowerPoint slides."""
    slide_number: int = Field(..., ge=1, description="Slide number in source presentation")
    title: str = Field(..., description="Slide title")
    content: str = Field(..., description="Slide text content")
    layout_type: str = Field(..., description="Slide layout type")
    source_file: str = Field(..., description="Source PowerPoint file name")
    
class GeneratedSlide(BaseModel):
    """Specification for a slide to be generated."""
    title: str = Field(..., min_length=1, description="Slide title")
    content: List[str] = Field(..., min_items=1, description="Bullet points or content sections")
    layout_type: str = Field(default="bullet", description="Slide layout type")
    notes: Optional[str] = Field(None, description="Speaker notes")

class PresentationSpec(BaseModel):
    """Complete specification for generated presentation."""
    project: ProjectDescription
    slides: List[GeneratedSlide] = Field(..., min_items=3, max_items=15)
    template_path: Path = Field(..., description="Path to company template file")
    output_path: Path = Field(..., description="Output file path")
```

### List of tasks to be completed to fulfill the PRP in the order they should be completed

```yaml
Task 1: Setup Project Configuration and Dependencies
CREATE pyproject.toml:
  - PATTERN: Follow CLAUDE.md guidelines for Python project structure
  - Include CrewAI, python-pptx, openai, chromadb, pydantic, pytest
  - Configure black, ruff, mypy for code quality

CREATE .env.example:
  - Include OpenAI API key, template paths, data directories
  - Follow examples from research with proper documentation

CREATE src/config/settings.py:
  - PATTERN: Use pydantic-settings with environment variable loading
  - Validate required API keys and file paths exist

Task 2: Implement Document Processing Tool
CREATE src/tools/document_processor.py:
  - PATTERN: Support both PowerPoint and PDF extraction
  - Extract text from slides using python-pptx
  - Extract text from PDFs using pypdf
  - Handle large files efficiently to avoid memory issues
  - Return structured ExtractedContent models

Task 3: Implement File Upload Handler
CREATE src/tools/file_handler.py:
  - PATTERN: Streamlit file upload integration
  - Validate file types (pptx, pdf) and size limits
  - Handle multiple file uploads (max 5)
  - Manage file processing workflow
  - Provide upload progress feedback

Task 4: Create Template Manager
CREATE src/tools/template_manager.py:
  - PATTERN: Handle Keyrus PowerPoint templates from root directory
  - CRITICAL: Implement placeholder management avoiding positioning gotchas
  - Load and validate template layouts
  - Provide slide creation utilities

Task 5: Implement Document Analysis Chain
CREATE src/chains/document_analysis_chain.py:
  - PATTERN: LangChain chain for document content analysis
  - Analyze extracted content from uploaded documents
  - Identify key themes, technologies, and approaches
  - Extract relevant examples and case studies

Task 6: Implement Project Analysis Chain
CREATE src/chains/project_analysis_chain.py:
  - PATTERN: LangChain chain with structured output
  - Analyze project description and requirements using LLM
  - Identify key technologies and solution approaches
  - Match project needs with document content

Task 7: Implement Content Generation Chain
CREATE src/chains/content_generation_chain.py:
  - PATTERN: LangChain chain with document content integration
  - Use analyzed content from uploaded documents to generate slide specifications
  - Ensure technical accuracy and relevance using prompt templates
  - Create structured GeneratedSlide models with output parsers

Task 8: Implement Presentation Builder
CREATE src/tools/presentation_builder.py:
  - PATTERN: LangChain tool for file operations
  - Use template_manager to create final PowerPoint
  - CRITICAL: Handle placeholder positioning correctly
  - Generate professional slides with company branding

Task 9: Create Chain Orchestration
CREATE src/chains/orchestration_chain.py:
  - PATTERN: LangChain sequential chain composition
  - Orchestrate workflow: Document Analysis → Project Analysis → Generation → Building
  - Handle chain communication and data passing
  - Implement error handling and logging

Task 10: Implement Streamlit Interface
CREATE streamlit_app.py:
  - PATTERN: Streamlit multi-page application
  - File upload widget supporting up to 5 documents
  - Project description input form
  - Real-time processing progress indicators
  - Download link for generated presentation

Task 11: Add Comprehensive Testing
CREATE tests/ directory structure:
  - PATTERN: Mirror src/ structure following CLAUDE.md
  - Unit tests for each chain and tool
  - Integration tests for full workflow
  - Mock file uploads and Streamlit components
  - Mock external API calls appropriately

Task 12: Create Documentation and Examples
UPDATE README.md:
  - Installation and setup instructions
  - Usage examples with sample commands
  - Configuration requirements
  - Troubleshooting guide
```

### Per task pseudocode as needed

```python
# Task 2: PowerPoint Text Extraction
async def extract_text_from_pptx(file_path: Path) -> List[ExtractedContent]:
    """Extract structured text content from PowerPoint file."""
    # PATTERN: Use python-pptx with careful error handling
    from pptx import Presentation
    
    presentation = Presentation(file_path)
    extracted_content = []
    
    for slide_num, slide in enumerate(presentation.slides, 1):
        # GOTCHA: Handle different slide layouts safely
        title = ""
        content = ""
        
        # CRITICAL: Use try-except for placeholder access
        try:
            if slide.shapes.title:
                title = slide.shapes.title.text
        except AttributeError:
            title = f"Slide {slide_num}"
        
        # Extract text from all text shapes
        text_content = []
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                text_content.append(shape.text.strip())
        
        content = "\n".join(text_content)
        
        extracted_content.append(ExtractedContent(
            slide_number=slide_num,
            title=title,
            content=content,
            layout_type=slide.slide_layout.name,
            source_file=file_path.name
        ))
    
    return extracted_content

# Task 5: Document Analysis Chain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document

class DocumentAnalysisChain:
    """LangChain-based document content analysis."""
    
    def __init__(self, llm):
        self.llm = llm
        self.analysis_prompt = PromptTemplate(
            input_variables=["documents", "project_description"],
            template="""
            Analyze the following documents and extract key information relevant to this project:
            Project: {project_description}
            
            Documents:
            {documents}
            
            Extract:
            1. Key technologies mentioned
            2. Solution approaches and methodologies
            3. Relevant case studies or examples
            4. Technical architecture patterns
            
            Provide structured analysis:
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)
    
    async def analyze_documents(
        self,
        documents: List[ExtractedContent],
        project_description: str
    ) -> Dict[str, Any]:
        """Analyze uploaded documents for relevant content."""
        try:
            # Format documents for analysis
            doc_text = "\n\n".join([
                f"Document: {doc.source_file}\n"
                f"Title: {doc.title}\n"
                f"Content: {doc.content}"
                for doc in documents
            ])
            
            # Run analysis chain
            result = await self.chain.ainvoke({
                "documents": doc_text,
                "project_description": project_description
            })
            
            return {
                "analysis": result["text"],
                "source_documents": len(documents),
                "technologies": [],  # Parse from analysis result
                "approaches": [],    # Parse from analysis result
            }
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return {"analysis": "", "source_documents": 0}

# Task 8: Presentation Builder with Template
async def create_presentation_from_spec(
    spec: PresentationSpec,
    template_path: Path
) -> Path:
    """Create PowerPoint presentation from specification using template."""
    # PATTERN: Load company template safely
    from pptx import Presentation
    
    # CRITICAL: Use template from root directory per codebase structure
    prs = Presentation(template_path)
    
    # Clear existing slides except master
    slide_layouts = prs.slide_layouts
    
    for slide_spec in spec.slides:
        # GOTCHA: Choose appropriate layout by name/index
        if slide_spec.layout_type == "title":
            layout = slide_layouts[0]  # Title slide layout
        elif slide_spec.layout_type == "bullet":
            layout = slide_layouts[1]  # Bullet slide layout
        else:
            layout = slide_layouts[6]  # Blank layout
        
        slide = prs.slides.add_slide(layout)
        
        # CRITICAL: Set all positioning properties together
        try:
            # Set title
            if slide.shapes.title:
                slide.shapes.title.text = slide_spec.title
            
            # Add content to content placeholder
            if hasattr(slide.placeholders, '1'):  # Content placeholder
                content_placeholder = slide.placeholders[1]
                text_frame = content_placeholder.text_frame
                text_frame.clear()  # Clear default text
                
                for bullet_point in slide_spec.content:
                    p = text_frame.add_paragraph()
                    p.text = bullet_point
                    p.level = 0  # Main bullet level
                    
        except (KeyError, AttributeError) as e:
            # PATTERN: Handle template inconsistencies gracefully
            logger.warning(f"Template placeholder issue: {e}")
            continue
    
    # Save presentation
    output_path = spec.output_path
    prs.save(output_path)
    return output_path
```

### Integration Points
```yaml
ENVIRONMENT:
  - add to: .env
  - vars: |
      # LLM Configuration
      OPENAI_API_KEY=sk-...
      OPENAI_MODEL=gpt-4
      
      # PowerPoint Templates
      TEMPLATE_DIR=./templates
      DEFAULT_TEMPLATE=Keyrus Commercial - Template.pptx
      
      # Data Directories
      PREVIOUS_DECKS_DIR=./data/previous_decks
      OUTPUT_DIR=./data/generated
      
      # File Upload Settings
      MAX_FILE_SIZE_MB=10
      MAX_FILES=5
      ALLOWED_EXTENSIONS=pptx,pdf

CONFIG:
  - Template loading: Use Keyrus templates from root directory
  - File uploads: Handle PowerPoint and PDF files up to 10MB each
  - Session state: Manage uploaded files and processing results
  - Logging: Structured logging with file and console output
  
DEPENDENCIES:
  - Update requirements.txt with:
    - langchain>=0.1.0
    - langchain-openai>=0.1.0
    - langchain-community>=0.1.0
    - python-pptx>=0.6.21
    - pypdf>=4.0.0
    - openai>=1.0.0
    - pydantic>=2.0.0
    - python-dotenv>=1.0.0
    - streamlit>=1.28.0
    - streamlit-extras>=0.3.0  # For enhanced UI components
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
uv run ruff check --fix src/ tests/    # Auto-fix style issues
uv run mypy src/                       # Type checking
uv run black src/ tests/               # Code formatting

# Expected: No errors. If errors, READ and fix.
```

### Level 2: Unit Tests
```python
# test_chains/test_retrieval_chain.py
async def test_content_extraction():
    """Test PowerPoint content extraction with LangChain."""
    extractor = PowerPointExtractor()
    # Use actual Keyrus template for testing
    content = await extractor.extract_text_from_pptx(
        Path("Keyrus Commercial - Template.pptx")
    )
    assert len(content) > 0
    assert all(isinstance(item, ExtractedContent) for item in content)

async def test_vector_store_indexing():
    """Test content indexing and retrieval."""
    vector_store = VectorStore()
    test_content = [
        ExtractedContent(
            slide_number=1,
            title="Test Slide",
            content="Test content about cloud architecture",
            layout_type="bullet",
            source_file="test.pptx"
        )
    ]
    
    await vector_store.index_content(test_content)
    results = await vector_store.similarity_search("cloud architecture")
    assert len(results) > 0

# test_tools/test_template_manager.py
def test_template_loading():
    """Test company template loading."""
    manager = TemplateManager()
    template_path = Path("Keyrus Commercial - Template.pptx")
    
    # Should load without errors
    presentation = manager.load_template(template_path)
    assert presentation is not None
    assert len(presentation.slide_layouts) > 0

def test_slide_creation():
    """Test slide creation with proper placeholder handling."""
    manager = TemplateManager()
    spec = GeneratedSlide(
        title="Test Architecture",
        content=["Cloud-native design", "Microservices approach"],
        layout_type="bullet"
    )
    
    # Should create slide without positioning errors
    slide = manager.create_slide_from_spec(spec)
    assert slide is not None
```

```bash
# Run tests iteratively until passing:
uv run pytest tests/ -v --cov=src --cov-report=term-missing

# If failing: Debug specific test, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Test full Streamlit workflow
streamlit run streamlit_app.py

# Manual testing steps:
# 1. Open browser to localhost:8501
# 2. Upload 2-3 reference documents (PowerPoint/PDF)
# 3. Enter project description: "Cloud-native data platform for real-time analytics with Snowflake"
# 4. Click "Generate Presentation"
# 5. Download generated presentation

# Expected behavior:
# ✅ Files upload successfully with progress indicators
# ✅ Content extracted from uploaded documents
# ✅ Generated 7 relevant slides for proposal
# ✅ Download link appears for generated presentation

# Verify output file
ls -la ./data/generated/techcorp_proposal.pptx
# Should exist and be > 100KB

# Open in PowerPoint to verify:
# - Keyrus branding preserved
# - Slides have relevant technical content
# - Formatting is professional
```

## Final Validation Checklist
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check src/`
- [ ] No type errors: `uv run mypy src/`
- [ ] Streamlit app generates valid PowerPoint files
- [ ] Generated presentations use company template correctly
- [ ] Content retrieval produces relevant results
- [ ] Document upload and processing workflow completes successfully
- [ ] Error cases handled gracefully (missing files, API failures)
- [ ] Documentation includes clear setup and usage instructions
- [ ] Example data and templates are properly organized

---

## Anti-Patterns to Avoid
- ❌ Don't hardcode file paths - use configuration and Path objects
- ❌ Don't skip placeholder positioning validation in python-pptx
- ❌ Don't ignore OpenAI API rate limits and token limits
- ❌ Don't commit API keys or large PowerPoint files to git
- ❌ Don't mix sync and async operations improperly in LangChain chains
- ❌ Don't assume template layouts are consistent across files
- ❌ Don't process files larger than memory limits in Streamlit
- ❌ Don't create files longer than 500 lines per CLAUDE.md rules

## Confidence Score: 8/10

High confidence due to:
- Mature LangChain ecosystem with extensive documentation
- Comprehensive python-pptx and pypdf documentation
- Established patterns for Streamlit file upload and processing
- Detailed validation gates and testing strategy
- Existing company templates available in codebase

Minor uncertainty areas:
- Specific Keyrus template placeholder layouts (requires testing)
- Memory management for large uploaded files in Streamlit
- Performance with multiple simultaneous file uploads

The comprehensive context and validation loops should enable successful one-pass implementation.