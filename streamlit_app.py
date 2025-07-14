"""
Main Streamlit application for PowerPoint Assistant.

This is the web interface for the AI-powered PowerPoint generation system
that creates branded presentations from project descriptions and reference documents.
"""

import asyncio
import logging
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path
import traceback

import streamlit as st
import pandas as pd

# Configure logging before other imports
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import application components
try:
    from src.config.settings import load_env, settings
    from src.models.data_models import ProjectDescription
    from src.tools.file_handler import FileUploadHandler
    from src.chains.orchestration_chain import PowerPointOrchestrationChain
    
    # Load environment variables
    load_env()
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.stop()


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = PowerPointOrchestrationChain()
    
    if "file_handler" not in st.session_state:
        st.session_state.file_handler = FileUploadHandler()
    
    if "generation_results" not in st.session_state:
        st.session_state.generation_results = None
    
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = None


def render_header():
    """Render the application header."""
    st.set_page_config(
        page_title=settings.app_title,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 " + settings.app_title)
    st.markdown(f"*{settings.app_description}*")
    
    # Add navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("📈 Analytics", use_container_width=True):
            st.session_state.page = "analytics"
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.page = "settings"


def render_sidebar():
    """Render the sidebar with configuration and status."""
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Status
        if settings.validate_api_key():
            st.success("✅ OpenAI API Connected")
        else:
            st.error("❌ OpenAI API Key Required")
            st.info("Please set OPENAI_API_KEY in your .env file")
        
        # Template Status
        if settings.template_path.exists():
            st.success(f"✅ Template: {settings.template_path.name}")
        else:
            st.warning("⚠️ Template not found")
        
        st.divider()
        
        # Generation Settings
        st.subheader("📝 Generation Settings")
        
        slide_count = st.slider(
            "Target Slide Count",
            min_value=settings.min_slides,
            max_value=settings.max_slides,
            value=8,
            help="Number of slides to generate"
        )
        
        presentation_focus = st.selectbox(
            "Presentation Focus",
            [
                "Technical solution and business value",
                "Business strategy and ROI",
                "Technical implementation details",
                "Executive summary and overview",
                "Project timeline and deliverables"
            ],
            help="Primary focus area for the presentation"
        )
        
        st.session_state.generation_settings = {
            "slide_count": slide_count,
            "presentation_focus": presentation_focus
        }
        
        st.divider()
        
        # Status Display
        if st.session_state.processing_status:
            st.subheader("📊 Processing Status")
            status = st.session_state.processing_status
            
            progress_bar = st.progress(status.progress)
            st.text(f"Status: {status.status}")
            st.text(f"Step: {status.completed_steps}/{status.total_steps}")
            st.text(f"Message: {status.message}")
            
            if status.error:
                st.error(f"Error: {status.error}")


def render_project_input():
    """Render the project description input form."""
    st.subheader("📝 Project Description")
    
    with st.form("project_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            description = st.text_area(
                "Project Description",
                height=150,
                placeholder="Describe your project in detail. Include objectives, scope, technologies, timeline, and any specific requirements...",
                help="Provide a detailed description of your project (minimum 20 characters)"
            )
        
        with col2:
            client_name = st.text_input(
                "Client Name",
                placeholder="Company or Client Name",
                help="Name of the client or company for this proposal"
            )
            
            industry = st.text_input(
                "Industry (Optional)",
                placeholder="e.g., Healthcare, Finance, Technology",
                help="Client's industry sector"
            )
            
            timeline = st.text_input(
                "Timeline (Optional)",
                placeholder="e.g., 6 months, Q2 2024",
                help="Project timeline or deadline"
            )
            
            budget_range = st.text_input(
                "Budget Range (Optional)",
                placeholder="e.g., $100K-500K, Medium",
                help="Estimated budget range"
            )
        
        # Technologies section
        st.write("**Key Technologies (Optional)**")
        tech_col1, tech_col2 = st.columns(2)
        
        with tech_col1:
            tech_input = st.text_input(
                "Technologies",
                placeholder="e.g., Python, AWS, React",
                help="Comma-separated list of technologies"
            )
        
        # Parse technologies
        technologies = []
        if tech_input:
            technologies = [tech.strip() for tech in tech_input.split(",") if tech.strip()]
        
        submitted = st.form_submit_button("📋 Save Project Details", use_container_width=True)
        
        if submitted:
            if len(description.strip()) < 20:
                st.error("Project description must be at least 20 characters long")
                return None
            
            if len(client_name.strip()) < 2:
                st.error("Client name must be at least 2 characters long")
                return None
            
            project = ProjectDescription(
                description=description.strip(),
                client_name=client_name.strip(),
                industry=industry.strip() if industry else None,
                timeline=timeline.strip() if timeline else None,
                budget_range=budget_range.strip() if budget_range else None,
                key_technologies=technologies
            )
            
            st.session_state.project = project
            st.success("✅ Project details saved successfully!")
            return project
    
    return st.session_state.get("project", None)


def render_file_upload():
    """Render the file upload section."""
    st.subheader("📁 Reference Documents")
    
    # File upload widget
    uploaded_files = st.session_state.file_handler.render_upload_widget()
    
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        
        # Process files and extract content
        with st.spinner("Processing uploaded files..."):
            try:
                # Convert Streamlit files to the format expected by orchestrator
                file_tuples = []
                for uploaded_file in uploaded_files:
                    file_content = BytesIO(uploaded_file.read())
                    uploaded_file.seek(0)  # Reset for potential re-reading
                    
                    file_type = st.session_state.file_handler.document_processor.get_file_type(uploaded_file.name)
                    file_tuples.append((file_content, uploaded_file.name, file_type))
                
                st.session_state.file_tuples = file_tuples
                st.success(f"✅ {len(uploaded_files)} files ready for processing")
                
            except Exception as e:
                st.error(f"Error processing files: {e}")
                logger.error(f"File processing error: {e}")
    
    # Display content preview if available
    if hasattr(st.session_state, 'uploaded_files') and st.session_state.uploaded_files:
        with st.expander("📄 Content Preview", expanded=False):
            st.session_state.file_handler.render_content_preview()


async def generate_presentation_async(project, file_tuples, generation_settings):
    """Async wrapper for presentation generation."""
    return await st.session_state.orchestrator.generate_presentation(
        project=project,
        uploaded_files=file_tuples,
        target_slide_count=generation_settings["slide_count"],
        progress_callback=lambda status: setattr(st.session_state, 'processing_status', status)
    )


def render_generation_section():
    """Render the presentation generation section."""
    st.subheader("🚀 Generate Presentation")
    
    project = st.session_state.get("project", None)
    file_tuples = st.session_state.get("file_tuples", [])
    
    if not project:
        st.warning("⚠️ Please complete the project description first")
        return
    
    # Display generation preview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Client", project.client_name)
    with col2:
        st.metric("Documents", len(file_tuples))
    with col3:
        target_slides = st.session_state.generation_settings["slide_count"]
        st.metric("Target Slides", target_slides)
    
    # Generation button
    if st.button("🎯 Generate PowerPoint Presentation", use_container_width=True, type="primary"):
        # Validate inputs
        validation = asyncio.run(
            st.session_state.orchestrator.validate_inputs(project, file_tuples)
        )
        
        if not validation["valid"]:
            for error in validation["errors"]:
                st.error(f"❌ {error}")
            return
        
        for warning in validation["warnings"]:
            st.warning(f"⚠️ {warning}")
        
        # Generate presentation
        with st.spinner("Generating presentation... This may take a few minutes."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Run async generation
                results = asyncio.run(
                    generate_presentation_async(
                        project, 
                        file_tuples, 
                        st.session_state.generation_settings
                    )
                )
                
                if results["success"]:
                    st.session_state.generation_results = results
                    st.success("✅ Presentation generated successfully!")
                    
                    # Display results
                    render_generation_results(results, context="immediate")
                    
                else:
                    st.error(f"❌ Generation failed: {results.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Generation failed: {str(e)}")
                logger.error(f"Generation error: {traceback.format_exc()}")
                
            finally:
                progress_bar.progress(1.0)
                status_text.empty()


def render_generation_results(results, context="default"):
    """Render the generation results and download options.
    
    Args:
        results: Generation results dictionary
        context: Context identifier to ensure unique widget keys
    """
    st.subheader("📊 Generation Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Slides Generated", results["final_slide_count"])
    with col2:
        st.metric("Confidence Score", f"{results['confidence_score']:.2f}")
    with col3:
        st.metric("Documents Used", results["extracted_content_count"])
    with col4:
        file_size = results["summary"]["file_size_mb"]
        st.metric("File Size", f"{file_size} MB")
    
    # Download section
    st.subheader("📥 Download Presentation")
    
    presentation_path = results["presentation_path"]
    
    if presentation_path.exists():
        with open(presentation_path, "rb") as file:
            file_data = file.read()
        
        # Generate unique key with context and timestamp to prevent duplicates
        unique_id = int(time.time() * 1000)  # Millisecond timestamp
        download_key = f"download_{context}_{presentation_path.stem}_{unique_id}"
        
        st.download_button(
            label="📥 Download PowerPoint Presentation",
            data=file_data,
            file_name=presentation_path.name,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
            key=download_key
        )
        
        st.success(f"✅ Presentation ready: {presentation_path.name}")
    else:
        st.error("❌ Presentation file not found")
    
    # Detailed results
    with st.expander("📋 Detailed Results", expanded=False):
        summary = results["summary"]
        
        st.write("**Slide Titles:**")
        for i, title in enumerate(summary["slide_titles"], 1):
            st.write(f"{i}. {title}")
        
        st.write("**Key Technologies Identified:**")
        st.write(", ".join(summary["key_technologies"]))
        
        st.write("**Key Approaches:**")
        st.write(", ".join(summary["key_approaches"]))
        
        # Technical details
        with st.expander("🔧 Technical Details"):
            st.json({
                "confidence_score": results["confidence_score"],
                "processing_time": "Generated successfully",
                "template_used": str(settings.template_path.name),
                "model_used": settings.openai_model
            })


def render_analytics_page():
    """Render analytics and insights page."""
    st.subheader("📈 Analytics & Insights")
    
    if not st.session_state.generation_results:
        st.info("Generate a presentation first to see analytics")
        return
    
    results = st.session_state.generation_results
    
    # Technology analysis
    st.write("**Technology Distribution**")
    tech_data = results["summary"]["key_technologies"]
    if tech_data:
        df_tech = pd.DataFrame({"Technology": tech_data, "Count": [1] * len(tech_data)})
        st.bar_chart(df_tech.set_index("Technology"))
    
    # Content analysis
    st.write("**Content Analysis**")
    doc_analysis = results["document_analysis"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Technologies Found", len(doc_analysis.technologies))
        st.metric("Approaches Identified", len(doc_analysis.approaches))
    with col2:
        st.metric("Case Studies", len(doc_analysis.case_studies))
        st.metric("Key Themes", len(doc_analysis.key_themes))


def render_settings_page():
    """Render settings configuration page."""
    st.subheader("⚙️ Settings")
    
    # API Configuration
    st.write("**API Configuration**")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("OpenAI Model", value=settings.openai_model, disabled=True)
    with col2:
        api_status = "✅ Connected" if settings.validate_api_key() else "❌ Not Connected"
        st.text_input("API Status", value=api_status, disabled=True)
    
    # File Settings
    st.write("**File Upload Settings**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Max Files", settings.max_files)
    with col2:
        st.metric("Max Size (MB)", settings.max_file_size_mb)
    with col3:
        st.metric("Allowed Types", ", ".join(settings.allowed_extensions_list))
    
    # Template Settings
    st.write("**Template Settings**")
    st.text_input("Template Path", value=str(settings.template_path), disabled=True)
    st.text_input("Output Directory", value=str(settings.output_dir), disabled=True)
    
    # Clear session
    if st.button("🗑️ Clear Session Data"):
        keys_to_clear = ["project", "uploaded_files", "file_tuples", "generation_results", "processing_status"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.success("Session data cleared!")
        st.rerun()


def main():
    """Main application function."""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Render header
        render_header()
        
        # Render sidebar
        render_sidebar()
        
        # Main content area
        page = st.session_state.get("page", "home")
        
        if page == "analytics":
            render_analytics_page()
        elif page == "settings":
            render_settings_page()
        else:
            # Home page - main workflow
            st.session_state.page = "home"
            
            # Main workflow tabs
            tab1, tab2, tab3 = st.tabs(["📝 Project Setup", "📁 Upload Documents", "🚀 Generate Presentation"])
            
            with tab1:
                render_project_input()
            
            with tab2:
                render_file_upload()
            
            with tab3:
                render_generation_section()
                
                # Show results if available
                if st.session_state.generation_results:
                    render_generation_results(st.session_state.generation_results, context="session")
        
        # Footer
        st.divider()
        st.markdown("*Powered by LangChain, OpenAI, and Streamlit • Built by Julien Chantrel for Keyrus*")
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {traceback.format_exc()}")


if __name__ == "__main__":
    main()