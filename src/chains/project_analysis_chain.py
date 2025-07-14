"""
Project analysis chain using LangChain.

This module analyzes project descriptions to understand requirements,
identify key technologies, and determine the best approach for the presentation.
"""

import json
import logging
from typing import Any, Dict, List

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from ..config.settings import settings
from ..models.data_models import ProjectAnalysisResult, ProjectDescription

logger = logging.getLogger(__name__)


class ProjectAnalysisChain:
    """
    LangChain-based project requirements analysis.
    
    Analyzes project descriptions to extract requirements, identify technologies,
    and recommend solution approaches for PowerPoint generation.
    """

    def __init__(self) -> None:
        """Initialize the project analysis chain."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.2,  # Low temperature for consistent analysis
            openai_api_key=settings.openai_api_key
        )
        
        self.analysis_prompt = PromptTemplate(
            input_variables=["project_description", "client_name", "industry", "timeline", "budget_range", "key_technologies"],
            template=self._get_analysis_template()
        )
        
        # Create chain using RunnableSequence (modern LangChain pattern)
        self.chain = self.analysis_prompt | self.llm

    def _get_analysis_template(self) -> str:
        """
        Get the prompt template for project analysis.

        Returns:
            Formatted prompt template string
        """
        return """
You are an expert solutions architect analyzing a project to create a compelling PowerPoint presentation proposal.

PROJECT DETAILS:
Description: {project_description}
Client: {client_name}
Industry: {industry}
Timeline: {timeline}
Budget Range: {budget_range}
Key Technologies: {key_technologies}

Please analyze this project and provide a structured analysis in JSON format:

{{
    "requirements": ["list of specific project requirements identified"],
    "technologies": ["list of recommended technologies and tools"],
    "solution_approaches": ["list of recommended solution approaches and methodologies"],
    "target_audience": "description of the target audience for this presentation",
    "key_objectives": ["list of key project objectives"],
    "business_drivers": ["business drivers and motivations"],
    "technical_challenges": ["technical challenges to address"],
    "success_criteria": ["criteria for project success"],
    "presentation_focus": ["key areas the presentation should focus on"],
    "value_propositions": ["key value propositions to highlight"]
}}

ANALYSIS GUIDELINES:
1. Extract specific, actionable requirements from the project description
2. Recommend appropriate technologies based on the project scope and industry
3. Suggest proven methodologies and approaches suitable for the project
4. Identify the primary audience (technical team, executives, stakeholders)
5. Define clear objectives that align with business goals
6. Consider industry-specific needs and constraints
7. Focus on practical, implementable solutions
8. Highlight the unique value proposition for this client

Be specific and actionable. Consider the client's industry context and business needs.

JSON OUTPUT:
"""

    async def analyze_project(
        self,
        project: ProjectDescription
    ) -> ProjectAnalysisResult:
        """
        Analyze project description and requirements.

        Args:
            project: ProjectDescription with all project details

        Returns:
            ProjectAnalysisResult with structured analysis

        Raises:
            ValueError: If analysis fails or produces invalid results
        """
        try:
            logger.info(f"Analyzing project for {project.client_name}")
            
            # Run analysis chain
            result = await self.chain.ainvoke({
                "project_description": project.description,
                "client_name": project.client_name,
                "industry": project.industry or "Not specified",
                "timeline": project.timeline or "Not specified",
                "budget_range": project.budget_range or "Not specified",
                "key_technologies": ", ".join(project.key_technologies) if project.key_technologies else "Not specified"
            })
            
            # Parse and validate the JSON result
            # With RunnableSequence, result is the direct content
            result_content = result.content if hasattr(result, 'content') else str(result)
            analysis_data = self._parse_analysis_result(result_content)
            
            # Create structured result with all fields
            analysis_result = ProjectAnalysisResult(
                requirements=analysis_data.get("requirements", []),
                technologies=analysis_data.get("technologies", []),
                solution_approaches=analysis_data.get("solution_approaches", []),
                target_audience=analysis_data.get("target_audience", "Business stakeholders"),
                key_objectives=analysis_data.get("key_objectives", []),
                business_drivers=analysis_data.get("business_drivers", []),
                technical_challenges=analysis_data.get("technical_challenges", []),
                success_criteria=analysis_data.get("success_criteria", []),
                presentation_focus=analysis_data.get("presentation_focus", []),
                value_propositions=analysis_data.get("value_propositions", [])
            )

            logger.info(f"Project analysis completed: {len(analysis_result.requirements)} requirements, "
                       f"{len(analysis_result.technologies)} technologies identified")
            
            return analysis_result

        except Exception as e:
            logger.error(f"Project analysis failed: {e}")
            # Return minimal valid result
            return ProjectAnalysisResult(
                requirements=[f"Analysis failed: {str(e)}"],
                technologies=[],
                solution_approaches=[],
                target_audience="Business stakeholders",
                key_objectives=[]
            )

    def _parse_analysis_result(self, result_text: str) -> Dict[str, Any]:
        """
        Parse and validate the analysis result JSON.

        Args:
            result_text: Raw text result from LLM

        Returns:
            Parsed analysis data dictionary

        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            # Try to find JSON in the response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in analysis result")
            
            json_text = result_text[json_start:json_end]
            analysis_data = json.loads(json_text)
            
            # Validate and clean required fields
            required_fields = {
                "requirements": [],
                "technologies": [],
                "solution_approaches": [],
                "target_audience": "Business stakeholders",
                "key_objectives": []
            }
            
            for field, default in required_fields.items():
                if field not in analysis_data:
                    analysis_data[field] = default
                elif field != "target_audience" and not isinstance(analysis_data[field], list):
                    analysis_data[field] = [str(analysis_data[field])] if analysis_data[field] else default

            return analysis_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis JSON: {e}")
            # Return minimal valid structure
            return {
                "requirements": [f"Analysis parsing failed: {str(e)}"],
                "technologies": [],
                "solution_approaches": [],
                "target_audience": "Business stakeholders",
                "key_objectives": []
            }

    async def match_with_document_analysis(
        self,
        project_analysis: ProjectAnalysisResult,
        document_technologies: List[str],
        document_approaches: List[str]
    ) -> Dict[str, Any]:
        """
        Match project requirements with document analysis results.

        Args:
            project_analysis: Project analysis result
            document_technologies: Technologies found in documents
            document_approaches: Approaches found in documents

        Returns:
            Dictionary with matching analysis and recommendations
        """
        try:
            # Calculate technology matches
            tech_matches = self._find_matches(
                project_analysis.technologies,
                document_technologies
            )
            
            # Calculate approach matches
            approach_matches = self._find_matches(
                project_analysis.solution_approaches,
                document_approaches
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                project_analysis,
                tech_matches,
                approach_matches
            )
            
            return {
                "technology_matches": tech_matches,
                "approach_matches": approach_matches,
                "match_score": self._calculate_match_score(tech_matches, approach_matches),
                "recommendations": recommendations,
                "content_relevance": self._assess_content_relevance(
                    project_analysis,
                    document_technologies,
                    document_approaches
                )
            }

        except Exception as e:
            logger.error(f"Failed to match project with document analysis: {e}")
            return {
                "error": str(e),
                "technology_matches": [],
                "approach_matches": [],
                "match_score": 0.0,
                "recommendations": []
            }

    def _find_matches(self, required_items: List[str], available_items: List[str]) -> List[Dict]:
        """
        Find matches between required and available items.

        Args:
            required_items: List of required items
            available_items: List of available items

        Returns:
            List of match dictionaries
        """
        matches = []
        
        for required in required_items:
            required_lower = required.lower()
            for available in available_items:
                available_lower = available.lower()
                
                # Exact match
                if required_lower == available_lower:
                    matches.append({
                        "required": required,
                        "available": available,
                        "match_type": "exact",
                        "confidence": 1.0
                    })
                # Partial match
                elif required_lower in available_lower or available_lower in required_lower:
                    matches.append({
                        "required": required,
                        "available": available,
                        "match_type": "partial",
                        "confidence": 0.7
                    })
        
        return matches

    def _calculate_match_score(
        self,
        tech_matches: List[Dict],
        approach_matches: List[Dict]
    ) -> float:
        """
        Calculate overall match score.

        Args:
            tech_matches: Technology matches
            approach_matches: Approach matches

        Returns:
            Match score between 0 and 1
        """
        if not tech_matches and not approach_matches:
            return 0.0
        
        # Weight exact matches higher
        tech_score = sum(
            match["confidence"] for match in tech_matches
        ) / max(len(tech_matches), 1)
        
        approach_score = sum(
            match["confidence"] for match in approach_matches
        ) / max(len(approach_matches), 1)
        
        # Average of technology and approach scores
        return (tech_score + approach_score) / 2

    def _generate_recommendations(
        self,
        project_analysis: ProjectAnalysisResult,
        tech_matches: List[Dict],
        approach_matches: List[Dict]
    ) -> List[str]:
        """
        Generate recommendations based on analysis and matches.

        Args:
            project_analysis: Project analysis result
            tech_matches: Technology matches
            approach_matches: Approach matches

        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Technology recommendations
        if tech_matches:
            matched_techs = [match["available"] for match in tech_matches]
            recommendations.append(
                f"Leverage experience with {', '.join(matched_techs[:3])} from previous projects"
            )
        
        # Approach recommendations
        if approach_matches:
            matched_approaches = [match["available"] for match in approach_matches]
            recommendations.append(
                f"Apply proven {', '.join(matched_approaches[:2])} methodologies"
            )
        
        # General recommendations based on project analysis
        if project_analysis.target_audience:
            recommendations.append(
                f"Tailor presentation content for {project_analysis.target_audience}"
            )
        
        if project_analysis.key_objectives:
            recommendations.append(
                f"Focus on achieving {len(project_analysis.key_objectives)} key objectives"
            )
        
        return recommendations

    def _assess_content_relevance(
        self,
        project_analysis: ProjectAnalysisResult,
        document_technologies: List[str],
        document_approaches: List[str]
    ) -> Dict[str, Any]:
        """
        Assess relevance of document content to project.

        Args:
            project_analysis: Project analysis result
            document_technologies: Technologies from documents
            document_approaches: Approaches from documents

        Returns:
            Content relevance assessment
        """
        # Calculate coverage of project requirements
        project_tech_coverage = len([
            tech for tech in project_analysis.technologies
            if any(tech.lower() in doc_tech.lower() for doc_tech in document_technologies)
        ]) / max(len(project_analysis.technologies), 1)
        
        project_approach_coverage = len([
            approach for approach in project_analysis.solution_approaches
            if any(approach.lower() in doc_approach.lower() for doc_approach in document_approaches)
        ]) / max(len(project_analysis.solution_approaches), 1)
        
        overall_relevance = (project_tech_coverage + project_approach_coverage) / 2
        
        return {
            "technology_coverage": project_tech_coverage,
            "approach_coverage": project_approach_coverage,
            "overall_relevance": overall_relevance,
            "relevance_level": self._get_relevance_level(overall_relevance),
            "missing_technologies": [
                tech for tech in project_analysis.technologies
                if not any(tech.lower() in doc_tech.lower() for doc_tech in document_technologies)
            ],
            "missing_approaches": [
                approach for approach in project_analysis.solution_approaches
                if not any(approach.lower() in doc_approach.lower() for doc_approach in document_approaches)
            ]
        }

    def _get_relevance_level(self, score: float) -> str:
        """
        Get relevance level description.

        Args:
            score: Relevance score (0-1)

        Returns:
            Relevance level string
        """
        if score >= 0.8:
            return "High - Excellent alignment with project requirements"
        elif score >= 0.6:
            return "Good - Strong alignment with most requirements"
        elif score >= 0.4:
            return "Moderate - Some alignment with project requirements"
        elif score >= 0.2:
            return "Low - Limited alignment with project requirements"
        else:
            return "Minimal - Little alignment with project requirements"


# Convenience function for simple project analysis
async def analyze_project_simple(project: ProjectDescription) -> ProjectAnalysisResult:
    """
    Simple function to analyze project without creating a chain instance.

    Args:
        project: Project description

    Returns:
        Project analysis result
    """
    chain = ProjectAnalysisChain()
    return await chain.analyze_project(project)