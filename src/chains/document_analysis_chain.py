"""
Document analysis chain using LangChain.

This module analyzes extracted content from uploaded documents to identify
key themes, technologies, and approaches relevant to the project requirements.
"""

import json
import logging
from typing import Any, Dict, List

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from ..config.settings import settings
from ..models.data_models import DocumentAnalysisResult, ExtractedContent

logger = logging.getLogger(__name__)


class DocumentAnalysisChain:
    """
    LangChain-based document content analysis.
    
    Analyzes uploaded documents to extract relevant information
    for PowerPoint generation, including technologies, approaches,
    and case studies.
    """

    def __init__(self) -> None:
        """Initialize the document analysis chain."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.1,  # Low temperature for consistent analysis
            openai_api_key=settings.openai_api_key
        )
        
        self.analysis_prompt = PromptTemplate(
            input_variables=["documents", "project_description"],
            template=self._get_analysis_template()
        )
        
        # Create chain using RunnableSequence (modern LangChain pattern)
        self.chain = self.analysis_prompt | self.llm

    def _get_analysis_template(self) -> str:
        """
        Get the prompt template for document analysis.

        Returns:
            Formatted prompt template string
        """
        return """
You are an expert business analyst reviewing documents to extract relevant information for a PowerPoint presentation proposal.

PROJECT DESCRIPTION:
{project_description}

DOCUMENTS TO ANALYZE:
{documents}

Please analyze these documents and extract the following information in JSON format:

{{
    "technologies": ["list of technologies mentioned"],
    "approaches": ["list of solution approaches and methodologies"],
    "case_studies": ["relevant case studies or examples"],
    "key_themes": ["main themes and topics"],
    "business_benefits": ["business benefits and value propositions mentioned"],
    "challenges_addressed": ["challenges or problems addressed"],
    "implementation_patterns": ["implementation patterns or best practices"],
    "client_examples": ["examples of similar client work"]
}}

ANALYSIS GUIDELINES:
1. Focus on content most relevant to the project description
2. Extract specific technologies, tools, and platforms mentioned
3. Identify proven methodologies and approaches
4. Note any case studies that demonstrate similar work
5. Capture key business themes and value propositions
6. Look for implementation patterns and best practices
7. Identify challenges addressed that relate to the project

Be thorough but focus on quality over quantity. Only include items that are clearly relevant to the project requirements.

JSON OUTPUT:
"""

    async def analyze_documents(
        self,
        documents: List[ExtractedContent],
        project_description: str
    ) -> DocumentAnalysisResult:
        """
        Analyze uploaded documents for relevant content.

        Args:
            documents: List of extracted content from uploaded documents
            project_description: Description of the project requirements

        Returns:
            DocumentAnalysisResult with structured analysis

        Raises:
            ValueError: If analysis fails or produces invalid results
        """
        if not documents:
            logger.warning("No documents provided for analysis")
            return DocumentAnalysisResult(
                analysis="No documents provided for analysis",
                source_documents=0
            )

        try:
            # Format documents for analysis
            doc_text = self._format_documents_for_analysis(documents)
            
            # Run analysis chain
            logger.info(f"Analyzing {len(documents)} documents...")
            result = await self.chain.ainvoke({
                "documents": doc_text,
                "project_description": project_description
            })
            
            # Parse and validate the JSON result
            # With RunnableSequence, result is the direct content
            result_content = result.content if hasattr(result, 'content') else str(result)
            analysis_data = self._parse_analysis_result(result_content)
            
            # Create structured result
            analysis_result = DocumentAnalysisResult(
                analysis=f"Analyzed {len(documents)} documents for project: {project_description[:100]}...",
                source_documents=len(documents),
                technologies=analysis_data.get("technologies", []),
                approaches=analysis_data.get("approaches", []),
                case_studies=analysis_data.get("case_studies", []),
                key_themes=analysis_data.get("key_themes", [])
            )
            
            # Add additional fields from analysis
            if "business_benefits" in analysis_data:
                analysis_result.business_benefits = analysis_data["business_benefits"]
            if "challenges_addressed" in analysis_data:
                analysis_result.challenges_addressed = analysis_data["challenges_addressed"]
            if "implementation_patterns" in analysis_data:
                analysis_result.implementation_patterns = analysis_data["implementation_patterns"]
            if "client_examples" in analysis_data:
                analysis_result.client_examples = analysis_data["client_examples"]

            logger.info(f"Document analysis completed: {len(analysis_result.technologies)} technologies, "
                       f"{len(analysis_result.approaches)} approaches identified")
            
            return analysis_result

        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return DocumentAnalysisResult(
                analysis=f"Analysis failed: {str(e)}",
                source_documents=len(documents)
            )

    def _format_documents_for_analysis(self, documents: List[ExtractedContent]) -> str:
        """
        Format documents for LLM analysis.

        Args:
            documents: List of extracted content

        Returns:
            Formatted document text for analysis
        """
        formatted_docs = []
        
        for doc in documents:
            doc_section = f"""
--- Document: {doc.source_file} ---
Type: {doc.file_type.upper()}
Slide/Page: {doc.slide_number}
Title: {doc.title}
Layout: {doc.layout_type}

Content:
{doc.content}
"""
            formatted_docs.append(doc_section)

        return "\n".join(formatted_docs)

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
            
            # Validate required fields
            required_fields = ["technologies", "approaches", "case_studies", "key_themes"]
            for field in required_fields:
                if field not in analysis_data:
                    analysis_data[field] = []
                elif not isinstance(analysis_data[field], list):
                    analysis_data[field] = [str(analysis_data[field])]

            return analysis_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis JSON: {e}")
            # Return minimal valid structure
            return {
                "technologies": [],
                "approaches": [],
                "case_studies": [],
                "key_themes": [f"Analysis parsing failed: {str(e)}"]
            }

    async def analyze_single_document(
        self,
        document: ExtractedContent,
        project_description: str
    ) -> Dict[str, Any]:
        """
        Analyze a single document for relevant content.

        Args:
            document: Single extracted content item
            project_description: Project requirements

        Returns:
            Analysis results for single document
        """
        return await self.analyze_documents([document], project_description)

    def get_technology_relevance_score(
        self,
        analysis_result: DocumentAnalysisResult,
        target_technologies: List[str]
    ) -> float:
        """
        Calculate relevance score based on technology overlap.

        Args:
            analysis_result: Document analysis result
            target_technologies: List of target technologies for the project

        Returns:
            Relevance score between 0 and 1
        """
        if not target_technologies or not analysis_result.technologies:
            return 0.0

        # Convert to lowercase for comparison
        found_techs = [tech.lower() for tech in analysis_result.technologies]
        target_techs = [tech.lower() for tech in target_technologies]

        # Calculate overlap
        matches = sum(1 for tech in target_techs if any(tech in found_tech for found_tech in found_techs))
        
        return matches / len(target_technologies)

    def summarize_analysis_results(
        self,
        analysis_results: List[DocumentAnalysisResult]
    ) -> Dict[str, Any]:
        """
        Summarize multiple document analysis results.

        Args:
            analysis_results: List of analysis results

        Returns:
            Consolidated summary of all analyses
        """
        if not analysis_results:
            return {"error": "No analysis results provided"}

        # Consolidate all findings
        all_technologies = []
        all_approaches = []
        all_case_studies = []
        all_themes = []
        total_documents = 0

        for result in analysis_results:
            all_technologies.extend(result.technologies)
            all_approaches.extend(result.approaches)
            all_case_studies.extend(result.case_studies)
            all_themes.extend(result.key_themes)
            total_documents += result.source_documents

        # Remove duplicates while preserving order
        unique_technologies = list(dict.fromkeys(all_technologies))
        unique_approaches = list(dict.fromkeys(all_approaches))
        unique_case_studies = list(dict.fromkeys(all_case_studies))
        unique_themes = list(dict.fromkeys(all_themes))

        return {
            "total_documents": total_documents,
            "unique_technologies": unique_technologies,
            "unique_approaches": unique_approaches,
            "unique_case_studies": unique_case_studies,
            "unique_themes": unique_themes,
            "technology_frequency": self._count_frequency(all_technologies),
            "approach_frequency": self._count_frequency(all_approaches),
            "theme_frequency": self._count_frequency(all_themes)
        }

    def _count_frequency(self, items: List[str]) -> Dict[str, int]:
        """
        Count frequency of items in list.

        Args:
            items: List of strings

        Returns:
            Dictionary with item frequencies
        """
        frequency = {}
        for item in items:
            frequency[item] = frequency.get(item, 0) + 1
        
        # Sort by frequency (descending)
        return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))


# Convenience function for simple document analysis
async def analyze_documents_simple(
    documents: List[ExtractedContent],
    project_description: str
) -> DocumentAnalysisResult:
    """
    Simple function to analyze documents without creating a chain instance.

    Args:
        documents: List of extracted content
        project_description: Project requirements

    Returns:
        Document analysis result
    """
    chain = DocumentAnalysisChain()
    return await chain.analyze_documents(documents, project_description)