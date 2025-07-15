"""
Data models for PowerPoint Assistant.

This module contains all Pydantic models used throughout the application
for data validation and type safety.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProjectDescription(BaseModel):
    """Input project requirements."""

    description: str = Field(
        ..., min_length=10, description="Detailed project description"
    )
    client_name: str = Field(..., min_length=1, description="Client company name")
    industry: Optional[str] = Field(None, description="Client industry sector")
    budget_range: Optional[str] = Field(None, description="Estimated budget range")
    timeline: Optional[str] = Field(None, description="Project timeline requirements")
    key_technologies: List[str] = Field(
        default_factory=list, description="Required technologies"
    )


class PowerPointSource(BaseModel):
    """Source PowerPoint file metadata."""

    file_path: Path = Field(..., description="Path to PowerPoint file")
    title: str = Field(..., description="Presentation title")
    client_industry: Optional[str] = Field(None, description="Related industry")
    technologies: List[str] = Field(
        default_factory=list, description="Technologies mentioned"
    )
    last_modified: datetime = Field(default_factory=datetime.now)


class ExtractedContent(BaseModel):
    """Content extracted from PowerPoint slides or PDF pages."""

    slide_number: int = Field(
        ..., ge=1, description="Slide number in source presentation"
    )
    title: str = Field(..., description="Slide title")
    content: str = Field(..., description="Slide text content")
    layout_type: str = Field(..., description="Slide layout type")
    source_file: str = Field(..., description="Source PowerPoint file name")
    file_type: str = Field(
        default="pptx", description="Source file type (pptx or pdf)"
    )


class GeneratedSlide(BaseModel):
    """Specification for a slide to be generated."""

    title: str = Field(..., min_length=1, description="Slide title")
    content: List[str] = Field(
        ..., min_items=1, description="Bullet points or content sections"
    )
    layout_type: str = Field(default="bullet", description="bullet|title|diagram|split")
    notes: Optional[str] = Field(None, description="Speaker notes")
    diagram: Optional["GeneratedDiagram"] = Field(None, description="Associated diagram for this slide")


class PresentationSpec(BaseModel):
    """Complete specification for generated presentation."""

    project: ProjectDescription
    slides: List[GeneratedSlide] = Field(
        ..., min_items=3, max_items=15, description="List of slides to generate"
    )
    template_path: Path = Field(..., description="Path to company template file")
    output_path: Path = Field(..., description="Output file path")


class DocumentAnalysisResult(BaseModel):
    """Result of document content analysis."""

    analysis: str = Field(..., description="Structured analysis of document content")
    source_documents: int = Field(
        ..., ge=0, description="Number of documents analyzed"
    )
    technologies: List[str] = Field(
        default_factory=list, description="Technologies identified in documents"
    )
    approaches: List[str] = Field(
        default_factory=list, description="Solution approaches identified"
    )
    case_studies: List[str] = Field(
        default_factory=list, description="Relevant case studies found"
    )
    key_themes: List[str] = Field(
        default_factory=list, description="Key themes identified"
    )


class ProjectAnalysisResult(BaseModel):
    """Result of project requirements analysis."""

    requirements: List[str] = Field(
        default_factory=list, description="Identified project requirements"
    )
    technologies: List[str] = Field(
        default_factory=list, description="Required technologies"
    )
    solution_approaches: List[str] = Field(
        default_factory=list, description="Recommended solution approaches"
    )
    target_audience: str = Field(
        default="", description="Identified target audience for presentation"
    )
    key_objectives: List[str] = Field(
        default_factory=list, description="Key project objectives"
    )
    # Optional extended analysis fields
    business_drivers: List[str] = Field(
        default_factory=list, description="Business drivers and motivations"
    )
    technical_challenges: List[str] = Field(
        default_factory=list, description="Technical challenges identified"
    )
    success_criteria: List[str] = Field(
        default_factory=list, description="Success criteria and metrics"
    )
    presentation_focus: List[str] = Field(
        default_factory=list, description="Recommended presentation focus areas"
    )
    value_propositions: List[str] = Field(
        default_factory=list, description="Key value propositions"
    )


class ContentGenerationResult(BaseModel):
    """Result of content generation process."""

    slides: List[GeneratedSlide] = Field(
        ..., description="Generated slide specifications"
    )
    generation_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata about the generation process"
    )
    confidence_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confidence in generated content"
    )


class ProcessingStatus(BaseModel):
    """Status of document processing and presentation generation."""

    status: str = Field(..., description="Current processing status")
    progress: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Processing progress (0-1)"
    )
    message: str = Field(default="", description="Status message")
    error: Optional[str] = Field(None, description="Error message if any")
    current_step: str = Field(default="", description="Current processing step")
    total_steps: int = Field(default=5, description="Total number of processing steps")
    completed_steps: int = Field(
        default=0, description="Number of completed steps"
    )


class FileUploadInfo(BaseModel):
    """Information about uploaded files."""

    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (pptx or pdf)")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    upload_timestamp: datetime = Field(
        default_factory=datetime.now, description="When file was uploaded"
    )
    processing_status: str = Field(
        default="pending", description="Processing status of the file"
    )
    extracted_content_count: int = Field(
        default=0, description="Number of extracted content items"
    )


class DiagramComponent(BaseModel):
    """Individual component in an architecture diagram."""
    
    name: str = Field(..., min_length=1, description="Component display name")
    component_type: str = Field(..., description="Type: service, database, queue, api, storage")
    icon_provider: str = Field(default="aws", description="Icon provider: aws, azure, gcp, kubernetes")
    icon_name: str = Field(..., description="Specific icon name from provider")
    position_hint: Optional[str] = Field(None, description="Layout hint: top, bottom, left, right, center")


class DiagramConnection(BaseModel):
    """Connection between diagram components."""
    
    source: str = Field(..., description="Source component name")
    target: str = Field(..., description="Target component name")
    connection_type: str = Field(default="arrow", description="Connection type: arrow, edge, bidirectional")
    label: Optional[str] = Field(None, description="Connection label")


class DiagramSpec(BaseModel):
    """Complete specification for diagram generation."""
    
    diagram_type: str = Field(..., description="Type: microservices, data_pipeline, cloud_architecture")
    title: str = Field(..., min_length=1, description="Diagram title")
    components: List[DiagramComponent] = Field(..., min_items=2, max_items=20)
    connections: List[DiagramConnection] = Field(default_factory=list)
    layout_direction: str = Field(default="TB", description="Layout: TB, LR, BT, RL")
    clustering: Dict[str, List[str]] = Field(default_factory=dict, description="Component grouping")
    styling: Dict[str, Any] = Field(default_factory=dict, description="Custom styling options")


class GeneratedDiagram(BaseModel):
    """Result of diagram generation process."""
    
    spec: DiagramSpec
    image_path: Path = Field(..., description="Path to generated diagram image")
    file_size_kb: int = Field(..., ge=0, description="Generated file size")
    generation_time_ms: int = Field(..., ge=0, description="Time taken to generate")
    slide_target: int = Field(..., ge=1, description="Target slide number for insertion")
    position: Dict[str, float] = Field(..., description="Slide position: left, top, width, height")


class DiagramGenerationResult(BaseModel):
    """Complete result of diagram generation chain."""
    
    diagrams: List[GeneratedDiagram] = Field(..., description="Generated diagrams")
    success_count: int = Field(default=0, ge=0, description="Number of successfully generated diagrams")
    total_generation_time_ms: int = Field(default=0, ge=0, description="Total processing time")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Generation confidence")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional generation metadata")


# Update forward references for type hints
GeneratedSlide.model_rebuild()