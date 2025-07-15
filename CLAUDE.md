# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

This is a Python 3.11+ project using Poetry and traditional pip for dependency management. The system includes advanced diagram generation capabilities using the diagrams library.

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

# Test diagram generation
python test_diagram_generation.py
```

### Environment Configuration
- Copy `.env.example` to `.env` and configure:
  - `OPENAI_API_KEY`: Required for LLM functionality
  - `DEFAULT_TEMPLATE`: PowerPoint template filename (default: "Keyrus Commercial - Template.pptx")
  - Template file should be placed in project root directory

### System Dependencies
- **Graphviz**: Required for diagram generation
  ```bash
  # Ubuntu/Debian
  sudo apt-get install graphviz
  
  # macOS
  brew install graphviz
  
  # Windows (using chocolatey)
  choco install graphviz
  ```

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

This is a LangChain-powered PowerPoint generation system with a Streamlit web interface. The system analyzes project descriptions and uploaded reference documents to generate branded presentations with automatically generated architecture diagrams.

### Core Components

- **`src/chains/`**: LangChain processing chains
  - `orchestration_chain.py`: Main workflow coordinator
  - `document_analysis_chain.py`: Analyzes uploaded documents  
  - `project_analysis_chain.py`: Analyzes project requirements
  - `content_generation_chain.py`: Generates slide specifications
  - `diagram_generation_chain.py`: Generates architecture diagrams

- **`src/tools/`**: Core processing tools
  - `document_processor.py`: PowerPoint/PDF text extraction
  - `presentation_builder.py`: Final presentation creation
  - `template_manager.py`: PowerPoint template handling
  - `file_handler.py`: Streamlit file upload management
  - `diagram_generator.py`: Architecture diagram generation using diagrams library

- **`src/models/data_models.py`**: Pydantic data models for type safety
- **`src/config/settings.py`**: Environment and configuration management using pydantic-settings

### Processing Workflow

1. **Document Analysis**: Extract and analyze uploaded PowerPoint/PDF files
2. **Project Analysis**: Analyze project requirements and specifications  
3. **Diagram Generation**: Generate architecture diagrams based on identified technologies
4. **Content Generation**: Generate slide specifications using LLM
5. **Presentation Building**: Create final branded PowerPoint presentation with embedded diagrams

## Key Technologies

- **LangChain**: LLM orchestration and chains
- **OpenAI**: Language model API (default: gpt-4o-mini)
- **Streamlit**: Web interface framework
- **python-pptx**: PowerPoint file manipulation
- **pypdf**: PDF text extraction
- **Pydantic**: Data validation and settings management
- **diagrams**: Architecture diagram generation with multi-cloud provider support
- **graphviz**: Diagram layout engine for professional visualizations
- **Pillow**: Image processing for diagram integration

## File Structure

- Templates: Place PowerPoint template files in project root
- Generated presentations: `./data/generated/`
- Generated diagrams: `./examples/diagrams/` (test diagrams) and `./data/generated/` (production diagrams)
- Reference documents: Upload via Streamlit interface
- Logs: `./logs/powerpoint_assistant.log`
- Example projects: `project_example_cloud_analytics.md`
- Test scripts: `test_diagram_generation.py`

## Diagram Generation Details

### Supported Providers and Components

The system supports the following diagram providers and components:

#### Cloud Providers
- **AWS**: 15 components including EC2, Lambda, S3, RDS, DynamoDB, Kinesis, Glue, EMR, Redshift, API Gateway, SQS, SNS
- **Azure**: 14 components including Functions, Blob Storage, SQL Database, Cosmos DB, Event Hubs, Data Factory, Synapse Analytics, Service Bus, Application Gateway
- **GCP**: 14 components including BigQuery, Cloud Functions, Cloud Storage, Cloud SQL, Firestore, Pub/Sub, Dataflow, Kubernetes Engine

#### Infrastructure
- **Kubernetes**: 3 components including Pods, Services (from k8s module, not kubernetes)
- **On-Premises**: 4 components including PostgreSQL, MySQL, Redis, RabbitMQ

### Technical Implementation

#### Key Files
- `src/tools/diagram_generator.py`: Core diagram generation using diagrams library
- `src/chains/diagram_generation_chain.py`: LangChain integration for diagram specifications
- `src/models/data_models.py`: Pydantic models for diagram components and specifications

#### Import Fixes Applied
- **Azure Analytics**: Fixed `DataFactory` → `DataFactories` (correct plural form)
- **GCP Database**: Fixed `Sql` → `SQL` (correct uppercase)
- **Kubernetes**: Fixed `diagrams.kubernetes` → `diagrams.k8s` (correct module name)

#### Parameter Validation
- Invalid diagram parameters (like `custom_colors`, `layout_spacing`) are filtered out
- Only valid Diagram constructor parameters are passed: `name`, `filename`, `direction`, `curvestyle`, `outformat`, `autolabel`, `show`, `strict`, `graph_attr`, `node_attr`, `edge_attr`

### Testing

Run comprehensive diagram generation tests:
```bash
python test_diagram_generation.py
```

This generates three test diagrams:
1. Multi-Cloud Architecture (AWS, Azure, GCP integration)
2. Data Processing Pipeline (stream and batch processing)
3. Kubernetes Microservices Architecture

Generated diagrams are saved to `examples/diagrams/` with detailed performance metrics.

## Development Notes

- All async operations use proper asyncio patterns
- Comprehensive logging throughout the application
- Type hints enforced with mypy
- Code formatting with Black (88 character line length)
- Linting with ruff
- Test coverage expected for new functionality
- Integration tests require explicit flag to run
- Diagram generation uses async/await patterns with proper error handling