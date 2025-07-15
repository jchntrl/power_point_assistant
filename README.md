# 📊 PowerPoint Assistant

An AI-powered system that generates branded PowerPoint presentations for new sales prospects by analyzing project descriptions alongside uploaded reference documents.

## ✨ Features

- **🤖 AI-Powered Content Generation**: Uses LangChain and OpenAI to analyze project requirements and generate relevant slide content
- **📁 Multi-Format Document Processing**: Supports PowerPoint (.pptx) and PDF file uploads for reference content extraction
- **🎨 Template-Based Design**: Maintains consistent Keyrus branding using company PowerPoint templates
- **🏗️ Architecture Diagram Generation**: Automatically generates professional architecture diagrams on dedicated slides using the diagrams library
- **🌐 User-Friendly Web Interface**: Streamlit-based interface for easy file uploads and project configuration
- **📊 Real-Time Progress Tracking**: Live updates during the presentation generation process
- **🔧 Flexible Configuration**: Customizable slide count, presentation focus, and content parameters
- **☁️ Multi-Cloud Support**: Supports AWS, Azure, GCP, Kubernetes, and on-premises architecture components

## 🏗️ Architecture

The system follows a modular architecture with clear separation of concerns:

```
src/
├── chains/                    # LangChain processing chains
│   ├── document_analysis_chain.py    # Analyzes uploaded documents
│   ├── project_analysis_chain.py     # Analyzes project requirements
│   ├── content_generation_chain.py   # Generates slide specifications
│   ├── diagram_generation_chain.py   # Generates architecture diagrams
│   └── orchestration_chain.py        # Main workflow coordination
├── tools/                     # Core processing tools
│   ├── document_processor.py         # PowerPoint/PDF text extraction
│   ├── file_handler.py              # Streamlit file upload management
│   ├── template_manager.py          # PowerPoint template handling
│   ├── diagram_generator.py         # Architecture diagram generation
│   └── presentation_builder.py      # Final presentation creation
├── models/                    # Pydantic data models
│   └── data_models.py               # Type-safe data structures
└── config/                    # Configuration management
    └── settings.py                  # Environment and settings
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key
- Keyrus PowerPoint template file
- Graphviz (for diagram generation)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd power_point_assistant
   ```

2. **Install system dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install graphviz
   
   # macOS
   brew install graphviz
   
   # Windows (using chocolatey)
   choco install graphviz
   ```

3. **Create and activate virtual environment**
   ```bash
   python3 -m venv linux_venv
   source linux_venv/bin/activate  # On Windows: linux_venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and other settings
   ```

6. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# LLM Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
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

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/powerpoint_assistant.log
```

### Template Setup

1. Place your Keyrus PowerPoint template in the project root directory
2. Update the `DEFAULT_TEMPLATE` environment variable with the template filename
3. Ensure the template has the following slide layouts:
   - Title slide layout (index 0)
   - Content/bullet slide layout (index 1)
   - Blank slide layout (index 6, optional)

## 📖 Usage

### Web Interface

1. **Start the application**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Access the web interface** at `http://localhost:8501`

3. **Follow the workflow:**
   - **Project Setup**: Enter project description, client name, and requirements
   - **Upload Documents**: Upload up to 5 reference documents (PowerPoint or PDF)
   - **Generate Presentation**: Configure settings and generate the presentation
   - **Download**: Download the generated PowerPoint presentation

### API Usage

```python
from src.chains.orchestration_chain import PowerPointOrchestrationChain
from src.models.data_models import ProjectDescription

# Create project description
project = ProjectDescription(
    description="Build a cloud-native data platform with real-time analytics",
    client_name="TechCorp Inc",
    industry="Technology",
    key_technologies=["Python", "AWS", "React"]
)

# Initialize orchestrator
orchestrator = PowerPointOrchestrationChain()

# Generate presentation
results = await orchestrator.generate_presentation(
    project=project,
    uploaded_files=[(file_content, "filename.pptx", "pptx")],
    target_slide_count=8
)

if results["success"]:
    print(f"Presentation created: {results['presentation_path']}")
```

## 🧪 Testing

### Run All Tests
```bash
source linux_venv/bin/activate
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/test_models.py tests/test_tools/ -v

# Integration tests (requires --run-integration flag)
pytest tests/test_integration.py --run-integration -v

# With coverage report
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Linting and Code Quality
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Diagram Generation Testing
```bash
# Test diagram generation with example project
python test_diagram_generation.py

# View generated diagrams
ls examples/diagrams/
```

## 🏗️ Architecture Diagram Generation

The system automatically generates professional architecture diagrams based on project requirements and technologies mentioned in the project description.

### Supported Providers

- **☁️ Cloud Providers**: AWS, Azure, GCP, Alibaba Cloud, Oracle Cloud
- **🔧 Container Orchestration**: Kubernetes, Docker
- **🏢 On-Premises**: PostgreSQL, MySQL, Redis, RabbitMQ
- **🎨 Generic**: Programming languages, frameworks, and custom components

### Diagram Types

- **Multi-Cloud Architecture**: Cross-cloud service integration
- **Data Processing Pipelines**: Stream and batch processing workflows
- **Microservices Architecture**: Container-based service architectures
- **Database Schemas**: Relational and NoSQL database designs

### Example Technologies

```python
# AWS Services
EC2, Lambda, S3, RDS, DynamoDB, Kinesis, Glue, EMR, Redshift, API Gateway, SQS, SNS

# Azure Services
Container Instances, Functions, Blob Storage, SQL Database, Cosmos DB, Event Hubs, 
Data Factory, Synapse Analytics, Service Bus, Application Gateway

# GCP Services
Compute Engine, Cloud Functions, Cloud Storage, Cloud SQL, Firestore, Pub/Sub, 
Dataflow, BigQuery, Kubernetes Engine

# Kubernetes Components
Pods, Services, Deployments, StatefulSets, ConfigMaps, Secrets

# On-Premises
PostgreSQL, MySQL, Redis, RabbitMQ
```

### Generated Diagram Features

- **📊 Professional Layout**: Automatic component positioning and clustering
- **🔗 Smart Connections**: Labeled relationships between components
- **🎨 Consistent Styling**: Brand-compliant colors and formatting
- **📱 High Resolution**: PNG format optimized for presentation slides
- **⚡ Fast Generation**: Sub-2 second generation times
- **📄 Dedicated Slides**: Each diagram gets its own dedicated slide for optimal viewing
- **🎯 Smart Positioning**: Diagrams are positioned to maximize slide real estate (9.0" x 5.5")
- **📝 Automatic Titles**: Each diagram slide includes descriptive titles
- **🗣️ Speaker Notes**: Auto-generated notes describing diagram components and relationships

## 📋 Supported File Types

- **PowerPoint**: `.pptx` files (Microsoft PowerPoint 2007+)
- **PDF**: `.pdf` files with extractable text content

## 🎯 Generated Presentation Structure

The system generates presentations with the following typical structure:

1. **Title Slide**: Project title and client information
2. **Executive Summary**: High-level overview and value proposition
3. **Understanding Your Needs**: Analysis of client requirements
4. **Our Approach**: Proposed methodology and solution approach
5. **Technical Solution**: Detailed technical architecture overview
6. **Architecture Diagrams**: Auto-generated technical architecture visualizations on dedicated slides
7. **Relevant Experience**: Showcase of similar work from reference documents
8. **Timeline & Deliverables**: Project phases and milestones
9. **Investment & Next Steps**: Value proposition and immediate actions

## 🔧 Advanced Configuration

### Custom Slide Generation

```python
from src.tools.template_manager import TemplateManager

# Create custom slide specifications
custom_slides = TemplateManager.get_default_slide_specs(
    "Custom Project Title",
    "Custom Client Name"
)

# Modify slides as needed
custom_slides[0].content = ["Custom bullet point 1", "Custom bullet point 2"]
```

### Content Generation Parameters

```python
# Configure content generation
generation_result = await content_chain.generate_content(
    project=project,
    project_analysis=project_analysis,
    document_analysis=document_analysis,
    target_slide_count=10,
    presentation_focus="technical implementation details"
)
```

## 🚨 Troubleshooting

### Common Issues

**1. OpenAI API Key Not Found**
```
Error: OpenAI API key not properly configured
```
**Solution**: Ensure your `.env` file contains a valid `OPENAI_API_KEY`

**2. Template Not Found**
```
Warning: Default template not found
```
**Solution**: Place the Keyrus template file in the project root directory

**3. File Upload Errors**
```
Error: Unsupported file type
```
**Solution**: Ensure uploaded files are `.pptx` or `.pdf` format and under the size limit

**4. Memory Issues with Large Files**
```
Error: File processing failed
```
**Solution**: Reduce file size or split large documents into smaller files

### Debugging

Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Follow code style**: Run `black` and `ruff` before committing
4. **Add tests**: Ensure new functionality is tested
5. **Create pull request**: Submit for review

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pre-commit install

# Run tests before committing
pytest tests/ -v
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Dependencies

### Core Dependencies
- **LangChain**: LLM orchestration and chains
- **OpenAI**: Language model API
- **Streamlit**: Web interface framework
- **Pydantic**: Data validation and settings
- **python-pptx**: PowerPoint file manipulation
- **pypdf**: PDF text extraction
- **diagrams**: Architecture diagram generation
- **graphviz**: Diagram layout engine
- **Pillow**: Image processing

### Development Dependencies
- **pytest**: Testing framework
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review the logs in `./logs/powerpoint_assistant.log`

## 🔄 Version History

- **v0.2.1**: Enhanced diagram integration
  - **🆕 Dedicated Diagram Slides**: Diagrams now appear on separate slides instead of being embedded in content slides
  - **🎯 Optimized Positioning**: Diagrams use nearly full slide space (9.0" x 5.5") for better visibility
  - **🎨 Smart Layout Selection**: Automatically selects optimal slide layouts (blank, diagram, title_content) for diagram slides
  - **📝 Enhanced Documentation**: Added speaker notes and descriptive titles for each diagram
  - **⚡ Improved Workflow**: Streamlined presentation building process with better diagram integration

- **v0.2.0**: Enhanced with diagram generation capabilities
  - Architecture diagram generation using diagrams library
  - Multi-cloud provider support (AWS, Azure, GCP, Kubernetes)
  - Automatic component recognition and layout
  - Professional diagram styling and branding
  - Example project templates and test suite

- **v0.1.0**: Initial release with core functionality
  - LangChain-based content generation
  - Streamlit web interface
  - PowerPoint and PDF document processing
  - Keyrus template integration

## 📝 Documentation Maintenance

**Important Note for Developers**: When making changes to this project, **always update both `README.md` and `CLAUDE.md` files** to maintain accurate documentation. This ensures that both human developers and AI assistants have access to current information about the system's capabilities and architecture.

**Required updates when modifying:**
- Feature additions or changes
- Architecture modifications
- API changes
- Configuration updates
- Dependencies changes
- Testing procedures

---

*Powered by LangChain, OpenAI, and Streamlit • Built by Julien Chantrel for Keyrus*