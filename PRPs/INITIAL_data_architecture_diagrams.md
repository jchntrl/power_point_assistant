## FEATURE:

Add capability to automatically generate and incorporate data architecture diagrams into PowerPoint presentations based on project requirements and technical specifications. The system should analyze project descriptions, identify data flow patterns, and create visual diagrams that integrate seamlessly with the existing slide generation workflow.

Key capabilities:
- **Diagram Generation**: Create data architecture diagrams (flow charts, system diagrams, data pipelines) using programmatic drawing libraries
- **Context-Aware Design**: Generate diagrams based on project description, technology stack, and uploaded reference documents
- **Template Integration**: Insert generated diagrams into PowerPoint slides using company branding and layout standards
- **Multiple Diagram Types**: Support various architecture patterns (microservices, data lakes, ETL pipelines, cloud architectures)
- **Smart Positioning**: Automatically position and size diagrams within slide layouts while maintaining professional formatting

## EXAMPLES:

The `examples/` folder should contain:

1. **Sample Architecture Diagrams**:
   - `examples/diagrams/microservices_architecture.png` - Multi-service system with APIs
   - `examples/diagrams/data_pipeline_flow.png` - ETL/ELT data processing workflow
   - `examples/diagrams/cloud_architecture.png` - AWS/Azure cloud infrastructure
   - `examples/diagrams/database_schema.png` - Data model relationships

2. **Reference PowerPoint Files**:
   - `examples/presentations/tech_architecture_deck.pptx` - Contains existing diagram slides for pattern analysis
   - `examples/presentations/data_platform_proposal.pptx` - Shows diagram integration examples

3. **Configuration Examples**:
   - `examples/configs/diagram_templates.json` - Pre-defined diagram templates and styling
   - `examples/configs/architecture_patterns.yaml` - Common architecture pattern definitions

4. **Test Project Descriptions**:
   - `examples/projects/e_commerce_platform.md` - Requires microservices diagram
   - `examples/projects/analytics_platform.md` - Requires data pipeline visualization
   - `examples/projects/iot_system.md` - Requires real-time data flow diagram

## DOCUMENTATION:

### Core Libraries and Tools:
- **Diagrams Library**: https://diagrams.mingrammer.com/
  - Python library for creating system architecture diagrams as code
  - Supports AWS, Azure, GCP, Kubernetes icons and components
  - Generates PNG/SVG output that can be embedded in PowerPoint

- **Graphviz**: https://graphviz.org/documentation/
  - Graph visualization software for creating structured diagrams
  - DOT language for describing graphs and relationships
  - Integration with Python via `python-graphviz` package

- **Matplotlib/Seaborn**: https://matplotlib.org/stable/tutorials/index.html
  - For custom data flow and process diagrams
  - Professional styling and layout capabilities
  - Export to various image formats

- **Python-pptx Image Insertion**: https://python-pptx.readthedocs.io/en/latest/user/slides.html#adding-an-image
  - Documentation for adding images to slides programmatically
  - Positioning, sizing, and layout management
  - Handling different image formats and resolutions

### AI/LLM Integration:
- **LangChain Structured Output**: https://python.langchain.com/docs/how_to/structured_output
  - For generating diagram specifications from project descriptions
  - Parsing technical requirements into visual components

- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling
  - For intelligently determining which diagram types to generate
  - Extracting technical architecture details from project text

### PowerPoint Integration:
- **Template Handling**: https://python-pptx.readthedocs.io/en/latest/user/placeholders-understanding.html
  - Managing slide layouts that accommodate diagrams
  - Placeholder positioning and sizing considerations

## OTHER CONSIDERATIONS:

### Technical Gotchas:
1. **Image Resolution and Scaling**: 
   - Diagrams must be generated at appropriate DPI (300+ for professional presentations)
   - Size calculations need to account for PowerPoint's coordinate system
   - Vector formats (SVG) may need conversion to raster (PNG/JPG) for PowerPoint compatibility

2. **Memory Management**:
   - Large, complex diagrams can consume significant memory during generation
   - Multiple diagram generation in sequence requires careful resource cleanup
   - Streamlit file upload limitations may affect diagram caching

3. **Font and Styling Consistency**:
   - Generated diagrams should match Keyrus branding guidelines
   - Font families used in diagrams must be available on generation system
   - Color schemes should align with company PowerPoint templates

4. **Diagram Complexity vs. Readability**:
   - Auto-generated diagrams can become cluttered with too many components
   - Need intelligent simplification algorithms for complex architectures
   - Different diagram types require different layout algorithms

### Integration Challenges:
1. **Context Understanding**:
   - LLM must accurately parse technical requirements from natural language descriptions
   - Mapping business requirements to specific technical architecture patterns
   - Handling ambiguous or incomplete project specifications

2. **Template Layout Management**:
   - Existing slide templates may not have optimal layouts for diagrams
   - Need fallback layouts when diagram doesn't fit standard placeholders
   - Maintaining text-diagram balance on slides

3. **Performance Considerations**:
   - Diagram generation adds significant processing time to presentation creation
   - Consider async processing and progress indicators for user experience
   - Caching generated diagrams for similar project types

### Architecture Pattern Recognition:
The system should recognize these common patterns and generate appropriate diagrams:
- **Microservices**: Service mesh, API gateway, inter-service communication
- **Data Pipeline**: ETL/ELT flows, data sources, transformations, destinations
- **Cloud Architecture**: Infrastructure components, networking, security boundaries
- **Real-time Systems**: Event streaming, message queues, processing engines
- **Database Design**: Entity relationships, data flow, replication patterns

### Validation Requirements:
- Generated diagrams must be technically accurate based on described requirements
- Diagram positioning within slides must not overlap with existing content
- Image quality must meet professional presentation standards
- Processing time should remain reasonable (<2 minutes for complete presentation)
- Error handling for unsupported architecture patterns or missing dependencies