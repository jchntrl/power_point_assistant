"""
Content generation chain using LangChain.

This module generates PowerPoint slide content based on project analysis
and document analysis results, creating structured slide specifications.
"""

import json
import logging
from typing import Any, Dict, List

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from ..config.settings import settings
from ..models.data_models import (
    ContentGenerationResult,
    DocumentAnalysisResult,
    GeneratedSlide,
    ProjectAnalysisResult,
    ProjectDescription,
)

logger = logging.getLogger(__name__)


class ContentGenerationChain:
    """
    LangChain-based content generation for PowerPoint slides.
    
    Uses project analysis and document analysis results to generate
    structured slide specifications with appropriate content and layout.
    """

    def __init__(self) -> None:
        """Initialize the content generation chain."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.3,  # Moderate temperature for creative but focused content
            openai_api_key=settings.openai_api_key
        )
        
        self.generation_prompt = PromptTemplate(
            input_variables=[
                "project_description",
                "client_name",
                "project_analysis",
                "document_analysis",
                "target_slide_count",
                "presentation_focus"
            ],
            template=self._get_generation_template()
        )
        
        # Create chain using RunnableSequence (modern LangChain pattern)
        self.chain = self.generation_prompt | self.llm

    def _get_generation_template(self) -> str:
        """
        Get the prompt template for content generation.

        Returns:
            Formatted prompt template string
        """
        return """
You are an expert presentation designer creating a compelling PowerPoint proposal for a technology consulting engagement.

PROJECT CONTEXT:
Client: {client_name}
Project: {project_description}

PROJECT ANALYSIS:
{project_analysis}

DOCUMENT ANALYSIS (Previous work and capabilities):
{document_analysis}

TARGET: Create {target_slide_count} slides
FOCUS: {presentation_focus}

Generate a PowerPoint presentation structure with detailed slide content in JSON format:

{{
    "slides": [
        {{
            "title": "Slide title",
            "content": ["Bullet point 1", "Bullet point 2", "Bullet point 3"],
            "layout_type": "title|bullet|blank",
            "notes": "Speaker notes for this slide"
        }}
    ],
    "presentation_metadata": {{
        "total_slides": number,
        "presentation_flow": "Brief description of the logical flow",
        "key_messages": ["Key message 1", "Key message 2"],
        "call_to_action": "Main call to action"
    }}
}}

SLIDE STRUCTURE GUIDELINES:
1. Title Slide: Client name, project title, "Prepared by Keyrus"
2. Executive Summary: High-level overview and value proposition
3. Understanding Your Needs: Demonstrate grasp of client requirements
4. Our Approach: Methodology and solution approach
5. Technical Solution: Detailed technical architecture and implementation
6. Relevant Experience: Showcase similar work from document analysis
7. Timeline & Deliverables: Project phases and key milestones
8. Investment & Next Steps: Value proposition and immediate actions

CONTENT GUIDELINES:
- Use specific technologies and approaches from the analysis
- Reference relevant case studies and experience from documents
- Tailor language and technical depth to the target audience
- Include concrete benefits and value propositions
- Make each slide action-oriented and client-focused
- Ensure logical flow from problem to solution to value
- Use bullet points effectively (3-5 per slide maximum)
- Include compelling speaker notes for presentation delivery

TECHNICAL ACCURACY:
- Only reference technologies and approaches mentioned in the analysis
- Ensure solution recommendations align with project requirements
- Use industry-standard terminology and best practices
- Validate technical feasibility of proposed solutions

JSON OUTPUT:
"""

    async def generate_content(
        self,
        project: ProjectDescription,
        project_analysis: ProjectAnalysisResult,
        document_analysis: DocumentAnalysisResult,
        target_slide_count: int = 8,
        presentation_focus: str = "technical solution and business value"
    ) -> ContentGenerationResult:
        """
        Generate slide content based on analysis results.

        Args:
            project: Project description and details
            project_analysis: Analysis of project requirements
            document_analysis: Analysis of uploaded documents
            target_slide_count: Number of slides to generate
            presentation_focus: Focus area for the presentation

        Returns:
            ContentGenerationResult with generated slides

        Raises:
            ValueError: If content generation fails
        """
        try:
            logger.info(f"Generating {target_slide_count} slides for {project.client_name}")
            
            # Prepare analysis summaries
            project_summary = self._summarize_project_analysis(project_analysis)
            document_summary = self._summarize_document_analysis(document_analysis)
            
            # Run content generation chain
            result = await self.chain.ainvoke({
                "project_description": project.description,
                "client_name": project.client_name,
                "project_analysis": project_summary,
                "document_analysis": document_summary,
                "target_slide_count": target_slide_count,
                "presentation_focus": presentation_focus
            })
            
            # Parse and validate the JSON result
            # With RunnableSequence, result is the direct content
            result_content = result.content if hasattr(result, 'content') else str(result)
            generation_data = self._parse_generation_result(result_content)
            
            # Create slide specifications
            slides = []
            for slide_data in generation_data.get("slides", []):
                try:
                    slide = GeneratedSlide(
                        title=slide_data.get("title", "Untitled Slide"),
                        content=slide_data.get("content", ["No content generated"]),
                        layout_type=slide_data.get("layout_type", "bullet"),
                        notes=slide_data.get("notes", "")
                    )
                    slides.append(slide)
                except Exception as e:
                    logger.warning(f"Invalid slide data: {e}")
                    continue
            
            # Ensure we have minimum required slides
            if len(slides) < 3:
                slides.extend(self._generate_fallback_slides(project, max(3 - len(slides), 0)))
            
            # Limit to maximum allowed slides
            if len(slides) > settings.max_slides:
                slides = slides[:settings.max_slides]
            
            # Create result
            generation_result = ContentGenerationResult(
                slides=slides,
                generation_metadata=generation_data.get("presentation_metadata", {}),
                confidence_score=self._calculate_confidence_score(slides, generation_data)
            )
            
            logger.info(f"Generated {len(slides)} slides with {generation_result.confidence_score:.2f} confidence")
            return generation_result

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            # Return fallback content
            fallback_slides = self._generate_fallback_slides(project, target_slide_count)
            return ContentGenerationResult(
                slides=fallback_slides,
                generation_metadata={"error": str(e)},
                confidence_score=0.3
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
        
        if analysis.key_objectives:
            summary_parts.append(f"Objectives: {', '.join(analysis.key_objectives[:3])}")
        
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
        
        summary_parts.append(f"Documents analyzed: {analysis.source_documents}")
        
        if analysis.technologies:
            summary_parts.append(f"Experience with: {', '.join(analysis.technologies[:5])}")
        
        if analysis.approaches:
            summary_parts.append(f"Proven approaches: {', '.join(analysis.approaches[:3])}")
        
        if analysis.case_studies:
            summary_parts.append(f"Case studies: {', '.join(analysis.case_studies[:2])}")
        
        if analysis.key_themes:
            summary_parts.append(f"Key themes: {', '.join(analysis.key_themes[:3])}")
        
        return " | ".join(summary_parts) if summary_parts else "No document analysis available"

    def _parse_generation_result(self, result_text: str) -> Dict[str, Any]:
        """
        Parse and validate the generation result JSON.

        Args:
            result_text: Raw text result from LLM

        Returns:
            Parsed generation data dictionary

        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            # Try to find JSON in the response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in generation result")
            
            json_text = result_text[json_start:json_end]
            generation_data = json.loads(json_text)
            
            # Validate required structure
            if "slides" not in generation_data:
                generation_data["slides"] = []
            
            if "presentation_metadata" not in generation_data:
                generation_data["presentation_metadata"] = {}
            
            # Validate slide structure
            valid_slides = []
            for slide in generation_data["slides"]:
                if isinstance(slide, dict) and "title" in slide and "content" in slide:
                    # Ensure content is a list
                    if not isinstance(slide["content"], list):
                        slide["content"] = [str(slide["content"])]
                    valid_slides.append(slide)
            
            generation_data["slides"] = valid_slides
            return generation_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse generation JSON: {e}")
            return {"slides": [], "presentation_metadata": {"error": str(e)}}

    def _calculate_confidence_score(
        self,
        slides: List[GeneratedSlide],
        generation_data: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score for generated content.

        Args:
            slides: List of generated slides
            generation_data: Raw generation data

        Returns:
            Confidence score between 0 and 1
        """
        score = 0.0
        
        # Base score for having slides
        if slides:
            score += 0.3
        
        # Score for slide count appropriateness
        if 5 <= len(slides) <= 10:
            score += 0.2
        elif 3 <= len(slides) <= 15:
            score += 0.1
        
        # Score for content quality
        for slide in slides:
            if slide.title and len(slide.title.strip()) > 5:
                score += 0.05
            if slide.content and len(slide.content) >= 2:
                score += 0.05
            if slide.notes and len(slide.notes.strip()) > 10:
                score += 0.02
        
        # Score for metadata presence
        metadata = generation_data.get("presentation_metadata", {})
        if metadata.get("presentation_flow"):
            score += 0.1
        if metadata.get("key_messages"):
            score += 0.1
        
        return min(score, 1.0)

    def _generate_fallback_slides(
        self,
        project: ProjectDescription,
        count: int
    ) -> List[GeneratedSlide]:
        """
        Generate fallback slides when main generation fails.

        Args:
            project: Project description
            count: Number of slides to generate

        Returns:
            List of fallback slide specifications
        """
        logger.info(f"Generating {count} fallback slides for {project.client_name}")
        
        # Use template manager's default slides as fallback
        from ..tools.template_manager import TemplateManager
        
        default_slides = TemplateManager.get_default_slide_specs(
            project.description[:50] + "...",
            project.client_name
        )
        
        # Adjust to requested count
        if count <= len(default_slides):
            return default_slides[:count]
        else:
            # Add additional generic slides if needed
            additional_slides = []
            for i in range(count - len(default_slides)):
                additional_slides.append(GeneratedSlide(
                    title=f"Additional Topic {i + 1}",
                    content=[
                        "Key point to be developed",
                        "Supporting information",
                        "Benefits and implications"
                    ],
                    layout_type="bullet",
                    notes="This slide requires further customization based on project specifics"
                ))
            
            return default_slides + additional_slides

    async def generate_slide_variations(
        self,
        base_slide: GeneratedSlide,
        variation_count: int = 3
    ) -> List[GeneratedSlide]:
        """
        Generate variations of a specific slide.

        Args:
            base_slide: Base slide to create variations from
            variation_count: Number of variations to generate

        Returns:
            List of slide variations
        """
        variation_prompt = PromptTemplate(
            input_variables=["slide_title", "slide_content", "slide_notes"],
            template="""
Create {variation_count} different variations of this slide while maintaining the core message:

Original Slide:
Title: {slide_title}
Content: {slide_content}
Notes: {slide_notes}

Generate variations with different:
- Phrasing and word choice
- Content organization
- Level of detail
- Presentation style

Return as JSON array:
[
    {{
        "title": "Variation title",
        "content": ["bullet 1", "bullet 2", "bullet 3"],
        "notes": "Speaker notes"
    }}
]
"""
        )
        
        try:
            variation_chain = LLMChain(llm=self.llm, prompt=variation_prompt)
            
            result = await variation_chain.ainvoke({
                "slide_title": base_slide.title,
                "slide_content": base_slide.content,
                "slide_notes": base_slide.notes or "",
                "variation_count": variation_count
            })
            
            # Parse variations
            variations_data = json.loads(result["text"])
            
            variations = []
            for var_data in variations_data:
                variations.append(GeneratedSlide(
                    title=var_data.get("title", base_slide.title),
                    content=var_data.get("content", base_slide.content),
                    layout_type=base_slide.layout_type,
                    notes=var_data.get("notes", base_slide.notes)
                ))
            
            return variations

        except Exception as e:
            logger.error(f"Failed to generate slide variations: {e}")
            return [base_slide]  # Return original slide as fallback


# Convenience function for simple content generation
async def generate_content_simple(
    project: ProjectDescription,
    project_analysis: ProjectAnalysisResult,
    document_analysis: DocumentAnalysisResult,
    slide_count: int = 8
) -> ContentGenerationResult:
    """
    Simple function to generate content without creating a chain instance.

    Args:
        project: Project description
        project_analysis: Project analysis result
        document_analysis: Document analysis result
        slide_count: Number of slides to generate

    Returns:
        Content generation result
    """
    chain = ContentGenerationChain()
    return await chain.generate_content(
        project, project_analysis, document_analysis, slide_count
    )