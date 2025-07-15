"""
Diagram generation chain using LangChain.

This module generates diagram specifications based on project analysis
and document analysis results, then creates actual diagrams using the 
diagram generator tool.
"""

import json
import logging
import time
from typing import Any, Dict, List

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from ..config.settings import settings
from ..models.data_models import (
    DiagramComponent,
    DiagramConnection,
    DiagramGenerationResult,
    DiagramSpec,
    DocumentAnalysisResult,
    GeneratedDiagram,
    ProjectAnalysisResult,
    ProjectDescription,
)
from ..tools.diagram_generator import DiagramGenerator
from ..tools.diagram_styler import DiagramStyler

logger = logging.getLogger(__name__)


class DiagramGenerationChain:
    """
    LangChain-based diagram specification generation and creation.
    
    Analyzes project requirements and generates appropriate architecture
    diagrams with intelligent component selection and layout.
    """

    def __init__(self) -> None:
        """Initialize the diagram generation chain."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.2,  # Lower temperature for technical accuracy
            openai_api_key=settings.openai_api_key
        )
        
        self.diagram_prompt = PromptTemplate(
            input_variables=[
                "project_description",
                "client_name",
                "project_analysis",
                "document_analysis",
                "supported_providers",
                "max_components",
                "diagram_types"
            ],
            template=self._get_diagram_template()
        )
        
        # Create chain using modern LangChain pattern
        self.chain = self.diagram_prompt | self.llm
        
        # Initialize diagram tools
        self.diagram_generator = DiagramGenerator(
            output_dir=settings.diagram_output_dir,
            styling_config=self._get_styling_config()
        )
        self.diagram_styler = DiagramStyler()

    def _get_diagram_template(self) -> str:
        """
        Get the prompt template for diagram specification generation.

        Returns:
            Formatted prompt template string
        """
        return """
You are an expert solution architect analyzing a technology project to generate accurate architecture diagrams.

PROJECT CONTEXT:
Client: {client_name}
Project: {project_description}

PROJECT ANALYSIS:
{project_analysis}

DOCUMENT ANALYSIS (Previous work and capabilities):
{document_analysis}

DIAGRAM CONSTRAINTS:
- Supported providers: {supported_providers}
- Maximum components per diagram: {max_components}
- Available diagram types: {diagram_types}

Generate 1-2 architecture diagrams that best represent the technical solution for this project.

ANALYSIS INSTRUCTIONS:
1. Identify the core architecture pattern (microservices, data pipeline, cloud architecture, etc.)
2. Determine the most appropriate cloud provider based on project context
3. Select components that accurately represent the technical solution
4. Design logical connections between components
5. Group related components into clusters when appropriate

OUTPUT FORMAT (JSON):
{{
    "diagrams": [
        {{
            "diagram_type": "microservices|data_pipeline|cloud_architecture|database_schema",
            "title": "Descriptive diagram title",
            "components": [
                {{
                    "name": "Component Display Name",
                    "component_type": "service|database|queue|api|storage|compute|container|loadbalancer|analytics|etl|streaming",
                    "icon_provider": "aws|azure|gcp|kubernetes|onprem",
                    "icon_name": "specific_icon_name",
                    "position_hint": "top|bottom|left|right|center"
                }}
            ],
            "connections": [
                {{
                    "source": "Source Component Name",
                    "target": "Target Component Name", 
                    "connection_type": "arrow|bidirectional|data_flow|async",
                    "label": "Optional connection label"
                }}
            ],
            "layout_direction": "TB|LR|BT|RL",
            "clustering": {{
                "Cluster Name": ["Component 1", "Component 2"]
            }},
            "styling": {{
                "custom_colors": {{}},
                "layout_spacing": "compact|normal|spacious"
            }}
        }}
    ],
    "analysis_metadata": {{
        "architecture_pattern": "Pattern identified",
        "complexity_level": "low|medium|high",
        "technical_confidence": 0.8,
        "recommended_slides": ["Slide 2", "Slide 4"]
    }}
}}

COMPONENT SELECTION GUIDELINES:

AWS Components:
- api: APIGateway, service: Lambda, database: RDS, nosql: DynamoDB
- queue: SQS, storage: S3, compute: EC2, container: ECS
- loadbalancer: ELB, analytics: EMR, etl: Glue, streaming: Kinesis

Azure Components:
- api: ApplicationGateway, service: FunctionApps, database: SQLDatabases
- nosql: CosmosDB, queue: ServiceBus, storage: BlobStorage
- compute: ContainerInstances, analytics: SynapseAnalytics, etl: DataFactory

GCP Components:
- api: LoadBalancing, service: Functions, database: SQL, nosql: Firestore
- queue: Pub_Sub, storage: Storage, compute: ComputeEngine, container: GKE
- analytics: BigQuery, etl: DataFlow, streaming: Pub_Sub

Kubernetes:
- service: Pod, network: Service

On-Premise:
- database: PostgreSQL, mysql: MySQL, cache: Redis, queue: RabbitMQ

DIAGRAM DESIGN PRINCIPLES:
1. Keep diagrams focused and readable (5-15 components maximum)
2. Use appropriate cloud provider based on project context
3. Show logical data flow and component relationships
4. Group related components into meaningful clusters
5. Choose layout direction that best represents the flow
6. Only include components that are explicitly mentioned or strongly implied
7. Ensure technical accuracy - don't add speculative components

DIAGRAM TYPE SELECTION:
- microservices: For distributed service architectures
- data_pipeline: For ETL/data processing workflows  
- cloud_architecture: For general cloud infrastructure
- database_schema: For data model representations

CLUSTERING GUIDELINES:
- "Web Tier": Frontend components, load balancers
- "Application Tier": Business logic, APIs, microservices
- "Data Tier": Databases, caches, storage
- "Processing": ETL, analytics, streaming components
- "Integration": Queues, message buses, event systems

OUTPUT JSON ONLY:
"""

    async def generate_diagram_specs(
        self,
        project: ProjectDescription,
        project_analysis: ProjectAnalysisResult,
        document_analysis: DocumentAnalysisResult
    ) -> DiagramGenerationResult:
        """
        Generate diagram specifications and create actual diagrams.

        Args:
            project: Project description and details
            project_analysis: Analysis of project requirements
            document_analysis: Analysis of uploaded documents

        Returns:
            DiagramGenerationResult with generated diagrams
        """
        start_time = time.time() * 1000

        try:
            logger.info(f"Generating diagram specifications for {project.client_name}")
            
            # Check if diagram generation is enabled
            if not settings.enable_diagram_generation:
                logger.info("Diagram generation is disabled")
                return DiagramGenerationResult(
                    diagrams=[],
                    success_count=0,
                    total_generation_time_ms=0,
                    confidence_score=0.0,
                    metadata={"disabled": True}
                )
            
            # Prepare analysis summaries
            project_summary = self._summarize_project_analysis(project_analysis)
            document_summary = self._summarize_document_analysis(document_analysis)
            
            # Get supported capabilities
            supported_providers = self.diagram_generator.get_supported_providers()
            diagram_types = self.diagram_styler.get_available_diagram_types()
            
            # Generate diagram specifications using LLM
            result = await self.chain.ainvoke({
                "project_description": project.description,
                "client_name": project.client_name,
                "project_analysis": project_summary,
                "document_analysis": document_summary,
                "supported_providers": ", ".join(supported_providers),
                "max_components": settings.max_diagram_components,
                "diagram_types": ", ".join(diagram_types)
            })
            
            # Parse LLM response
            result_content = result.content if hasattr(result, 'content') else str(result)
            spec_data = self._parse_diagram_specifications(result_content)
            
            # Generate actual diagrams
            generated_diagrams = []
            for diagram_spec_data in spec_data.get("diagrams", []):
                try:
                    # Create diagram specification
                    diagram_spec = self._create_diagram_spec(diagram_spec_data)
                    
                    # Generate the actual diagram image
                    generated_diagram = await self.diagram_generator.generate_diagram(diagram_spec)
                    generated_diagrams.append(generated_diagram)
                    
                    logger.info(f"Successfully generated diagram: {diagram_spec.title}")
                    
                except Exception as e:
                    logger.error(f"Failed to generate diagram: {e}")
                    continue
            
            # Calculate total processing time
            total_time = int(time.time() * 1000 - start_time)
            
            # Create result
            analysis_metadata = spec_data.get("analysis_metadata", {})
            confidence_score = self._calculate_confidence_score(
                generated_diagrams, analysis_metadata
            )
            
            result = DiagramGenerationResult(
                diagrams=generated_diagrams,
                success_count=len(generated_diagrams),
                total_generation_time_ms=total_time,
                confidence_score=confidence_score,
                metadata={
                    "architecture_pattern": analysis_metadata.get("architecture_pattern", "unknown"),
                    "complexity_level": analysis_metadata.get("complexity_level", "medium"),
                    "technical_confidence": analysis_metadata.get("technical_confidence", 0.5),
                    "recommended_slides": analysis_metadata.get("recommended_slides", []),
                    "source": "ai_generated",
                    "model": settings.openai_model
                }
            )
            
            logger.info(
                f"Generated {len(generated_diagrams)} diagrams in {total_time}ms "
                f"with confidence {confidence_score:.2f}"
            )
            return result

        except Exception as e:
            error_msg = f"Diagram generation failed: {str(e)}"
            logger.error(error_msg)
            
            # Return graceful failure result
            total_time = int(time.time() * 1000 - start_time)
            return DiagramGenerationResult(
                diagrams=[],
                success_count=0,
                total_generation_time_ms=total_time,
                confidence_score=0.0,
                metadata={"error": error_msg}
            )

    def _summarize_project_analysis(self, analysis: ProjectAnalysisResult) -> str:
        """
        Create a summary of project analysis for the prompt.

        Args:
            analysis: Project analysis result

        Returns:
            Formatted summary string
        """
        summary_parts = []
        
        if analysis.requirements:
            summary_parts.append(f"Requirements: {', '.join(analysis.requirements[:5])}")
        
        if analysis.technologies:
            summary_parts.append(f"Technologies: {', '.join(analysis.technologies[:5])}")
        
        if analysis.solution_approaches:
            summary_parts.append(f"Approaches: {', '.join(analysis.solution_approaches[:3])}")
        
        if analysis.target_audience:
            summary_parts.append(f"Audience: {analysis.target_audience}")
        
        if analysis.technical_challenges:
            summary_parts.append(f"Challenges: {', '.join(analysis.technical_challenges[:3])}")
        
        return " | ".join(summary_parts) if summary_parts else "No project analysis available"

    def _summarize_document_analysis(self, analysis: DocumentAnalysisResult) -> str:
        """
        Create a summary of document analysis for the prompt.

        Args:
            analysis: Document analysis result

        Returns:
            Formatted summary string
        """
        summary_parts = []
        
        if analysis.technologies:
            summary_parts.append(f"Experience with: {', '.join(analysis.technologies[:5])}")
        
        if analysis.approaches:
            summary_parts.append(f"Proven approaches: {', '.join(analysis.approaches[:3])}")
        
        if analysis.case_studies:
            summary_parts.append(f"Case studies: {', '.join(analysis.case_studies[:2])}")
        
        return " | ".join(summary_parts) if summary_parts else "No document analysis available"

    def _parse_diagram_specifications(self, result_text: str) -> Dict[str, Any]:
        """
        Parse and validate diagram specifications from LLM response.

        Args:
            result_text: Raw text result from LLM

        Returns:
            Parsed diagram specifications dictionary
        """
        try:
            # Extract JSON from response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in diagram specification result")
            
            json_text = result_text[json_start:json_end]
            spec_data = json.loads(json_text)
            
            # Validate and normalize structure
            if "diagrams" not in spec_data:
                spec_data["diagrams"] = []
            
            if "analysis_metadata" not in spec_data:
                spec_data["analysis_metadata"] = {}
            
            # Validate each diagram specification
            valid_diagrams = []
            for diagram in spec_data["diagrams"]:
                if self._validate_diagram_spec(diagram):
                    valid_diagrams.append(diagram)
                else:
                    logger.warning(f"Invalid diagram specification: {diagram.get('title', 'Unknown')}")
            
            spec_data["diagrams"] = valid_diagrams
            return spec_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse diagram specification JSON: {e}")
            return {"diagrams": [], "analysis_metadata": {"error": str(e)}}

    def _validate_diagram_spec(self, diagram: Dict[str, Any]) -> bool:
        """
        Validate diagram specification structure.

        Args:
            diagram: Diagram specification dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["diagram_type", "title", "components"]
        
        for field in required_fields:
            if field not in diagram:
                return False
        
        # Validate components
        components = diagram.get("components", [])
        if not isinstance(components, list) or len(components) < 2:
            return False
        
        # Validate component structure
        for component in components:
            if not isinstance(component, dict):
                return False
            if not all(key in component for key in ["name", "component_type", "icon_provider"]):
                return False
        
        return True

    def _create_diagram_spec(self, diagram_data: Dict[str, Any]) -> DiagramSpec:
        """
        Create DiagramSpec from parsed data.

        Args:
            diagram_data: Parsed diagram specification data

        Returns:
            DiagramSpec instance
        """
        # Create components
        components = []
        for comp_data in diagram_data.get("components", []):
            component = DiagramComponent(
                name=comp_data.get("name", "Unknown"),
                component_type=comp_data.get("component_type", "service"),
                icon_provider=comp_data.get("icon_provider", "aws"),
                icon_name=comp_data.get("icon_name", comp_data.get("component_type", "service")),
                position_hint=comp_data.get("position_hint")
            )
            components.append(component)
        
        # Create connections
        connections = []
        for conn_data in diagram_data.get("connections", []):
            connection = DiagramConnection(
                source=conn_data.get("source", ""),
                target=conn_data.get("target", ""),
                connection_type=conn_data.get("connection_type", "arrow"),
                label=conn_data.get("label")
            )
            connections.append(connection)
        
        # Create diagram specification
        diagram_spec = DiagramSpec(
            diagram_type=diagram_data.get("diagram_type", "cloud_architecture"),
            title=diagram_data.get("title", "Architecture Diagram"),
            components=components,
            connections=connections,
            layout_direction=diagram_data.get("layout_direction", "TB"),
            clustering=diagram_data.get("clustering", {}),
            styling=diagram_data.get("styling", {})
        )
        
        return diagram_spec

    def _calculate_confidence_score(
        self,
        diagrams: List[GeneratedDiagram],
        metadata: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score for diagram generation.

        Args:
            diagrams: List of generated diagrams
            metadata: Analysis metadata

        Returns:
            Confidence score between 0 and 1
        """
        score = 0.0
        
        # Base score for successful generation
        if diagrams:
            score += 0.4
        
        # Score for number of diagrams
        if len(diagrams) >= 1:
            score += 0.2
        if len(diagrams) >= 2:
            score += 0.1
        
        # Score for technical confidence from analysis
        technical_confidence = metadata.get("technical_confidence", 0.5)
        score += technical_confidence * 0.3
        
        # Score for diagram complexity appropriateness
        for diagram in diagrams:
            component_count = len(diagram.spec.components)
            if 5 <= component_count <= 15:  # Optimal range
                score += 0.05
            elif 3 <= component_count <= 20:  # Acceptable range
                score += 0.02
        
        return min(score, 1.0)

    def _get_styling_config(self) -> Dict[str, Any]:
        """
        Get styling configuration for diagram generation.

        Returns:
            Styling configuration dictionary
        """
        return {
            "style": settings.diagram_style,
            "dpi": settings.diagram_dpi,
            "colors": {
                "primary": settings.keyrus_primary_color,
                "secondary": settings.keyrus_secondary_color,
                "accent": settings.keyrus_accent_color
            }
        }

    async def cleanup_resources(self) -> None:
        """Clean up diagram generation resources."""
        try:
            # Clean up old diagram files
            await self.diagram_generator.cleanup_old_diagrams(max_age_hours=24)
            logger.info("Diagram generation resources cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up diagram resources: {e}")

    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get diagram generation statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "supported_providers": self.diagram_generator.get_supported_providers(),
            "available_diagram_types": self.diagram_styler.get_available_diagram_types(),
            "max_components": settings.max_diagram_components,
            "output_directory": str(settings.diagram_output_dir),
            "generation_enabled": settings.enable_diagram_generation,
            "cache_enabled": settings.diagram_cache_enabled
        }


# Convenience function for simple diagram generation
async def generate_diagrams_simple(
    project: ProjectDescription,
    project_analysis: ProjectAnalysisResult,
    document_analysis: DocumentAnalysisResult
) -> DiagramGenerationResult:
    """
    Simple function to generate diagrams without creating chain instance.

    Args:
        project: Project description
        project_analysis: Project analysis result
        document_analysis: Document analysis result

    Returns:
        Diagram generation result
    """
    chain = DiagramGenerationChain()
    return await chain.generate_diagram_specs(project, project_analysis, document_analysis)