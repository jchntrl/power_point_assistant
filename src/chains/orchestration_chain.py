"""
Orchestration chain for PowerPoint Assistant.

This module coordinates the complete workflow from document processing
through analysis to final presentation generation.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..config.settings import settings
from ..models.data_models import (
    ContentGenerationResult,
    DiagramGenerationResult,
    DocumentAnalysisResult,
    ExtractedContent,
    ProcessingStatus,
    ProjectAnalysisResult,
    ProjectDescription,
)
from ..tools.document_processor import DocumentProcessor
from ..tools.presentation_builder import PresentationBuilder
from .content_generation_chain import ContentGenerationChain
from .diagram_generation_chain import DiagramGenerationChain
from .document_analysis_chain import DocumentAnalysisChain
from .project_analysis_chain import ProjectAnalysisChain

logger = logging.getLogger(__name__)


class PowerPointOrchestrationChain:
    """
    Main orchestration chain for PowerPoint generation workflow.
    
    Coordinates the complete process:
    1. Document Analysis → Extract and analyze uploaded documents
    2. Project Analysis → Analyze project requirements
    3. Diagram Generation → Generate architecture diagrams
    4. Content Generation → Generate slide specifications
    5. Presentation Building → Create final PowerPoint file with diagrams
    """

    def __init__(self) -> None:
        """Initialize the orchestration chain with all components."""
        self.document_processor = DocumentProcessor()
        self.document_analysis_chain = DocumentAnalysisChain()
        self.project_analysis_chain = ProjectAnalysisChain()
        self.diagram_generation_chain = DiagramGenerationChain()
        self.content_generation_chain = ContentGenerationChain()
        self.presentation_builder = PresentationBuilder()
        
        self.current_status = ProcessingStatus(
            status="initialized",
            message="Orchestration chain ready"
        )

    async def generate_presentation(
        self,
        project: ProjectDescription,
        uploaded_files: List[Tuple[Any, str, str]],  # (file_source, filename, file_type)
        target_slide_count: int = 8,
        template_path: Optional[Path] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Generate complete PowerPoint presentation from project and documents.

        Args:
            project: Project description and requirements
            uploaded_files: List of (file_source, filename, file_type) tuples
            target_slide_count: Number of slides to generate
            template_path: Optional custom template path
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with generation results and presentation path

        Raises:
            ValueError: If generation fails at any stage
        """
        try:
            logger.info(f"Starting presentation generation for {project.client_name}")
            
            # Step 1: Document Processing and Analysis
            self._update_status("processing_documents", 0.1, "Processing uploaded documents...")
            if progress_callback:
                progress_callback(self.current_status)
            
            extracted_content = await self._process_documents(uploaded_files)
            
            self._update_status("analyzing_documents", 0.2, "Analyzing document content...")
            if progress_callback:
                progress_callback(self.current_status)
            
            document_analysis = await self.document_analysis_chain.analyze_documents(
                extracted_content, project.description
            )
            
            # Step 2: Project Analysis
            self._update_status("analyzing_project", 0.3, "Analyzing project requirements...")
            if progress_callback:
                progress_callback(self.current_status)
            
            project_analysis = await self.project_analysis_chain.analyze_project(project)
            
            # Step 3: Diagram Generation
            self._update_status("generating_diagrams", 0.5, "Generating architecture diagrams...")
            if progress_callback:
                progress_callback(self.current_status)
            
            diagram_generation_result = DiagramGenerationResult(diagrams=[], success_count=0)
            if settings.enable_diagram_generation:
                try:
                    diagram_generation_result = await self.diagram_generation_chain.generate_diagram_specs(
                        project=project,
                        project_analysis=project_analysis,
                        document_analysis=document_analysis
                    )
                    logger.info(f"Generated {diagram_generation_result.success_count} diagrams")
                except Exception as e:
                    logger.warning(f"Diagram generation failed: {e}")
            else:
                logger.info("Diagram generation is disabled")
            
            # Step 4: Content Generation
            self._update_status("generating_content", 0.7, "Generating slide content...")
            if progress_callback:
                progress_callback(self.current_status)
            
            generation_result = await self.content_generation_chain.generate_content(
                project=project,
                project_analysis=project_analysis,
                document_analysis=document_analysis,
                target_slide_count=target_slide_count
            )
            
            # Step 5: Presentation Building
            self._update_status("building_presentation", 0.85, "Creating PowerPoint presentation...")
            if progress_callback:
                progress_callback(self.current_status)
            
            presentation_path = await self.presentation_builder.build_presentation(
                project=project,
                generation_result=generation_result,
                template_path=template_path
            )
            
            # Step 6: Insert Diagrams
            diagram_insertion_results = {}
            if diagram_generation_result.diagrams:
                self._update_status("inserting_diagrams", 0.95, "Inserting diagrams into presentation...")
                if progress_callback:
                    progress_callback(self.current_status)
                
                try:
                    diagram_insertion_results = await self.presentation_builder.insert_diagrams_into_presentation(
                        presentation_path=presentation_path,
                        diagrams=diagram_generation_result.diagrams
                    )
                    logger.info(
                        f"Inserted {diagram_insertion_results.get('successful_insertions', 0)} diagrams "
                        f"into presentation"
                    )
                except Exception as e:
                    logger.error(f"Failed to insert diagrams: {e}")
                    diagram_insertion_results = {"error": str(e)}
            
            # Final step: Complete
            self._update_status("completed", 1.0, f"Presentation created successfully: {presentation_path.name}")
            if progress_callback:
                progress_callback(self.current_status)
            
            # Compile comprehensive results
            results = {
                "success": True,
                "presentation_path": presentation_path,
                "project_analysis": project_analysis,
                "document_analysis": document_analysis,
                "diagram_generation_result": diagram_generation_result,
                "diagram_insertion_results": diagram_insertion_results,
                "generation_result": generation_result,
                "extracted_content_count": len(extracted_content),
                "final_slide_count": len(generation_result.slides),
                "diagram_count": len(diagram_generation_result.diagrams),
                "confidence_score": generation_result.confidence_score,
                "processing_status": self.current_status,
                "summary": self._generate_summary(
                    project, project_analysis, document_analysis, generation_result, 
                    presentation_path, diagram_generation_result
                )
            }
            
            logger.info(f"Successfully generated presentation: {presentation_path}")
            return results

        except Exception as e:
            error_msg = f"Presentation generation failed: {str(e)}"
            logger.error(error_msg)
            
            self._update_status("error", 0.0, error_msg)
            if progress_callback:
                progress_callback(self.current_status)
            
            return {
                "success": False,
                "error": error_msg,
                "processing_status": self.current_status
            }

    async def _process_documents(
        self,
        uploaded_files: List[Tuple[Any, str, str]]
    ) -> List[ExtractedContent]:
        """
        Process uploaded documents and extract content.

        Args:
            uploaded_files: List of (file_source, filename, file_type) tuples

        Returns:
            List of extracted content from all documents
        """
        if not uploaded_files:
            logger.warning("No documents provided for processing")
            return []

        all_content = []
        
        for file_source, filename, file_type in uploaded_files:
            try:
                logger.debug(f"Processing document: {filename}")
                
                content = await self.document_processor.process_document(
                    file_source, filename, file_type
                )
                
                all_content.extend(content)
                logger.info(f"Extracted {len(content)} items from {filename}")
                
            except Exception as e:
                logger.error(f"Failed to process {filename}: {e}")
                # Continue with other documents
                continue

        logger.info(f"Total extracted content: {len(all_content)} items from {len(uploaded_files)} documents")
        return all_content

    def _update_status(
        self,
        status: str,
        progress: float,
        message: str,
        error: Optional[str] = None
    ) -> None:
        """
        Update current processing status.

        Args:
            status: Current status string
            progress: Progress value (0-1)
            message: Status message
            error: Optional error message
        """
        self.current_status = ProcessingStatus(
            status=status,
            progress=progress,
            message=message,
            error=error,
            current_step=message,
            total_steps=6,
            completed_steps=int(progress * 6)
        )

    def _generate_summary(
        self,
        project: ProjectDescription,
        project_analysis: ProjectAnalysisResult,
        document_analysis: DocumentAnalysisResult,
        generation_result: ContentGenerationResult,
        presentation_path: Path,
        diagram_generation_result: DiagramGenerationResult
    ) -> Dict[str, Any]:
        """
        Generate comprehensive summary of the generation process.

        Args:
            project: Project description
            project_analysis: Project analysis results
            document_analysis: Document analysis results
            generation_result: Content generation results
            presentation_path: Path to created presentation

        Returns:
            Summary dictionary
        """
        return {
            "client": project.client_name,
            "project_description": project.description[:100] + "...",
            "documents_analyzed": document_analysis.source_documents,
            "technologies_identified": len(document_analysis.technologies),
            "approaches_identified": len(document_analysis.approaches),
            "project_requirements": len(project_analysis.requirements),
            "target_audience": project_analysis.target_audience,
            "slides_generated": len(generation_result.slides),
            "diagrams_generated": len(diagram_generation_result.diagrams),
            "diagram_generation_enabled": settings.enable_diagram_generation,
            "diagram_types": [diagram.spec.diagram_type for diagram in diagram_generation_result.diagrams],
            "confidence_score": generation_result.confidence_score,
            "diagram_confidence_score": diagram_generation_result.confidence_score,
            "presentation_file": presentation_path.name,
            "file_size_mb": round(presentation_path.stat().st_size / (1024 * 1024), 2) if presentation_path.exists() else 0,
            "key_technologies": document_analysis.technologies[:5],
            "key_approaches": document_analysis.approaches[:3],
            "slide_titles": [slide.title for slide in generation_result.slides],
            "diagram_titles": [diagram.spec.title for diagram in diagram_generation_result.diagrams]
        }

    async def validate_inputs(
        self,
        project: ProjectDescription,
        uploaded_files: List[Tuple[Any, str, str]]
    ) -> Dict[str, Any]:
        """
        Validate inputs before processing.

        Args:
            project: Project description
            uploaded_files: List of uploaded files

        Returns:
            Validation results dictionary
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Validate project description
        if not project.description or len(project.description.strip()) < 20:
            validation_results["errors"].append("Project description too short (minimum 20 characters)")
            validation_results["valid"] = False

        if not project.client_name or len(project.client_name.strip()) < 2:
            validation_results["errors"].append("Client name too short (minimum 2 characters)")
            validation_results["valid"] = False

        # Validate uploaded files
        if not uploaded_files:
            validation_results["warnings"].append("No reference documents provided - using default content patterns")
        elif len(uploaded_files) > settings.max_files:
            validation_results["errors"].append(f"Too many files ({len(uploaded_files)}), maximum {settings.max_files}")
            validation_results["valid"] = False

        # Validate file types
        for _, filename, file_type in uploaded_files:
            if file_type not in ["pptx", "pdf"]:
                validation_results["errors"].append(f"Unsupported file type: {filename}")
                validation_results["valid"] = False

        # Check API key configuration
        if not settings.validate_api_key():
            validation_results["errors"].append("OpenAI API key not properly configured")
            validation_results["valid"] = False

        # Check template availability
        if not settings.template_path.exists():
            validation_results["warnings"].append(f"Default template not found: {settings.template_path}")

        return validation_results

    async def get_preview_data(
        self,
        project: ProjectDescription,
        uploaded_files: List[Tuple[Any, str, str]]
    ) -> Dict[str, Any]:
        """
        Generate preview data without full processing.

        Args:
            project: Project description
            uploaded_files: List of uploaded files

        Returns:
            Preview data dictionary
        """
        try:
            # Quick document processing for preview
            extracted_content = await self._process_documents(uploaded_files[:2])  # Limit for preview
            
            # Quick project analysis
            project_analysis = await self.project_analysis_chain.analyze_project(project)
            
            # Generate estimated timeline
            estimated_time = self._estimate_processing_time(len(uploaded_files))
            
            return {
                "success": True,
                "estimated_processing_time": estimated_time,
                "document_count": len(uploaded_files),
                "extracted_items_preview": len(extracted_content),
                "identified_technologies": project_analysis.technologies[:5],
                "target_audience": project_analysis.target_audience,
                "estimated_slides": max(5, min(10, len(project_analysis.requirements) + 3)),
                "key_requirements": project_analysis.requirements[:3]
            }

        except Exception as e:
            logger.error(f"Failed to generate preview: {e}")
            return {
                "success": False,
                "error": str(e),
                "estimated_processing_time": 60.0  # Default estimate
            }

    def _estimate_processing_time(self, file_count: int) -> float:
        """
        Estimate total processing time.

        Args:
            file_count: Number of files to process

        Returns:
            Estimated time in seconds
        """
        # Base time for analysis and generation
        base_time = 30.0
        
        # Time per document (processing + analysis)
        time_per_doc = 15.0
        
        # Content generation time (scales with complexity)
        generation_time = 20.0
        
        # Presentation building time
        building_time = 10.0
        
        total_time = base_time + (file_count * time_per_doc) + generation_time + building_time
        
        return max(45.0, total_time)  # Minimum 45 seconds

    def get_current_status(self) -> ProcessingStatus:
        """
        Get current processing status.

        Returns:
            Current ProcessingStatus object
        """
        return self.current_status

    async def cleanup_resources(self) -> None:
        """Clean up any resources used during processing."""
        try:
            # Clean up diagram generation resources
            await self.diagram_generation_chain.cleanup_resources()
        except Exception as e:
            logger.warning(f"Error cleaning up diagram resources: {e}")
        
        logger.info("Orchestration chain cleanup completed")


# Convenience function for simple presentation generation
async def generate_presentation_simple(
    project: ProjectDescription,
    uploaded_files: List[Tuple[Any, str, str]],
    slide_count: int = 8,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Simple function to generate presentation without creating orchestration instance.

    Args:
        project: Project description
        uploaded_files: List of uploaded files
        slide_count: Number of slides to generate
        progress_callback: Optional progress callback

    Returns:
        Generation results dictionary
    """
    orchestrator = PowerPointOrchestrationChain()
    return await orchestrator.generate_presentation(
        project, uploaded_files, slide_count, progress_callback=progress_callback
    )