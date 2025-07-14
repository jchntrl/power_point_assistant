# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

This is a Python 3.11+ project using Poetry and traditional pip for dependency management.

### Setup Commands
```bash
# Activate virtual environment (Linux/WSL)
source linux_venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For development dependencies
pip install -e ".[dev]"

# Run the application
streamlit run streamlit_app.py
```

### Environment Configuration
- Copy `.env.example` to `.env` and configure:
  - `OPENAI_API_KEY`: Required for LLM functionality
  - `DEFAULT_TEMPLATE`: PowerPoint template filename (default: "Keyrus Commercial - Template.pptx")
  - Template file should be placed in project root directory

## Code Quality Commands

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/

# Run tests
pytest tests/ -v

# Integration tests (requires --run-integration flag)
pytest tests/test_integration.py --run-integration -v

# Tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Architecture Overview

This is a LangChain-powered PowerPoint generation system with a Streamlit web interface. The system analyzes project descriptions and uploaded reference documents to generate branded presentations.

### Core Components

- **`src/chains/`**: LangChain processing chains
  - `orchestration_chain.py`: Main workflow coordinator
  - `document_analysis_chain.py`: Analyzes uploaded documents  
  - `project_analysis_chain.py`: Analyzes project requirements
  - `content_generation_chain.py`: Generates slide specifications

- **`src/tools/`**: Core processing tools
  - `document_processor.py`: PowerPoint/PDF text extraction
  - `presentation_builder.py`: Final presentation creation
  - `template_manager.py`: PowerPoint template handling
  - `file_handler.py`: Streamlit file upload management

- **`src/models/data_models.py`**: Pydantic data models for type safety
- **`src/config/settings.py`**: Environment and configuration management using pydantic-settings

### Processing Workflow

1. **Document Analysis**: Extract and analyze uploaded PowerPoint/PDF files
2. **Project Analysis**: Analyze project requirements and specifications  
3. **Content Generation**: Generate slide specifications using LLM
4. **Presentation Building**: Create final branded PowerPoint presentation

## Key Technologies

- **LangChain**: LLM orchestration and chains
- **OpenAI**: Language model API (default: gpt-4o-mini)
- **Streamlit**: Web interface framework
- **python-pptx**: PowerPoint file manipulation
- **pypdf**: PDF text extraction
- **Pydantic**: Data validation and settings management

## File Structure

- Templates: Place PowerPoint template files in project root
- Generated presentations: `./data/generated/`
- Reference documents: Upload via Streamlit interface
- Logs: `./logs/powerpoint_assistant.log`

## Development Notes

- All async operations use proper asyncio patterns
- Comprehensive logging throughout the application
- Type hints enforced with mypy
- Code formatting with Black (88 character line length)
- Linting with ruff
- Test coverage expected for new functionality
- Integration tests require explicit flag to run