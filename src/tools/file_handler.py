"""
File upload handler for Streamlit interface.

This module manages file uploads, validation, and processing
for the PowerPoint Assistant Streamlit application.
"""

import logging
from io import BytesIO
from typing import Dict, List, Optional, Tuple

import streamlit as st

from ..config.settings import settings
from ..models.data_models import ExtractedContent, FileUploadInfo, ProcessingStatus
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class FileUploadHandler:
    """
    Handles file uploads in Streamlit with validation and processing.
    
    Manages session state, file validation, and coordinates document processing.
    """

    def __init__(self) -> None:
        """Initialize the file upload handler."""
        self.document_processor = DocumentProcessor()
        self.session_key = "uploaded_files_info"
        self.content_key = "extracted_content"
        
        # Initialize session state if needed
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = []
        if self.content_key not in st.session_state:
            st.session_state[self.content_key] = []

    def render_upload_widget(self) -> Optional[List]:
        """
        Render the file upload widget in Streamlit.

        Returns:
            List of uploaded files or None if no files uploaded
        """
        st.subheader("📁 Upload Reference Documents")
        
        # Display current configuration
        with st.expander("Upload Settings", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Max Files", settings.max_files)
            with col2:
                st.metric("Max Size", f"{settings.max_file_size_mb} MB")
            with col3:
                st.metric("Allowed Types", ", ".join(settings.allowed_extensions_list))

        # File uploader widget
        uploaded_files = st.file_uploader(
            "Choose PowerPoint or PDF files",
            accept_multiple_files=True,
            type=settings.allowed_extensions_list,
            help=f"Upload up to {settings.max_files} files (max {settings.max_file_size_mb} MB each)"
        )

        if uploaded_files:
            return self._process_uploaded_files(uploaded_files)
        
        return None

    def _process_uploaded_files(self, uploaded_files: List) -> List:
        """
        Process and validate uploaded files.

        Args:
            uploaded_files: List of Streamlit uploaded file objects

        Returns:
            List of validated file information
        """
        # Validate number of files
        if len(uploaded_files) > settings.max_files:
            st.error(f"❌ Too many files! Maximum {settings.max_files} files allowed.")
            return []

        validated_files = []
        current_files_info = []

        for uploaded_file in uploaded_files:
            # Validate file
            validation_result = self._validate_file(uploaded_file)
            
            if validation_result["is_valid"]:
                validated_files.append(uploaded_file)
                
                # Create file info
                file_info = FileUploadInfo(
                    filename=uploaded_file.name,
                    file_type=self.document_processor.get_file_type(uploaded_file.name),
                    file_size=uploaded_file.size,
                    processing_status="uploaded"
                )
                current_files_info.append(file_info)
            else:
                st.error(f"❌ {uploaded_file.name}: {validation_result['error']}")

        # Update session state
        st.session_state[self.session_key] = current_files_info

        # Display file summary
        if validated_files:
            self._display_file_summary(current_files_info)

        return validated_files

    def _validate_file(self, uploaded_file) -> Dict[str, any]:
        """
        Validate an uploaded file.

        Args:
            uploaded_file: Streamlit uploaded file object

        Returns:
            Dictionary with validation result
        """
        # Check file size
        if uploaded_file.size > settings.max_file_size_bytes:
            return {
                "is_valid": False,
                "error": f"File too large ({uploaded_file.size / 1024 / 1024:.1f} MB). Maximum size is {settings.max_file_size_mb} MB."
            }

        # Check file type
        if not self.document_processor.validate_file_type(uploaded_file.name):
            return {
                "is_valid": False,
                "error": f"Unsupported file type. Allowed types: {', '.join(settings.allowed_extensions_list)}"
            }

        # Check if file is empty
        if uploaded_file.size == 0:
            return {
                "is_valid": False,
                "error": "File is empty."
            }

        return {"is_valid": True, "error": None}

    def _display_file_summary(self, files_info: List[FileUploadInfo]) -> None:
        """
        Display summary of uploaded files.

        Args:
            files_info: List of file information objects
        """
        st.success(f"✅ {len(files_info)} file(s) uploaded successfully")
        
        # Create a summary table
        summary_data = []
        total_size = 0
        
        for file_info in files_info:
            size_mb = file_info.file_size / 1024 / 1024
            total_size += size_mb
            
            summary_data.append({
                "File": file_info.filename,
                "Type": file_info.file_type.upper(),
                "Size (MB)": f"{size_mb:.1f}",
                "Status": file_info.processing_status.title()
            })

        # Display as a dataframe
        import pandas as pd
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)
        
        # Show total size
        st.info(f"📊 Total size: {total_size:.1f} MB")

    async def process_files_content(
        self,
        uploaded_files: List,
        show_progress: bool = True
    ) -> List[ExtractedContent]:
        """
        Process uploaded files and extract content.

        Args:
            uploaded_files: List of Streamlit uploaded file objects
            show_progress: Whether to show progress indicators

        Returns:
            List of extracted content from all files
        """
        if not uploaded_files:
            return []

        all_content = []
        
        if show_progress:
            progress_bar = st.progress(0)
            status_text = st.empty()

        total_files = len(uploaded_files)
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                if show_progress:
                    progress = i / total_files
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {uploaded_file.name}... ({i+1}/{total_files})")

                # Get file type
                file_type = self.document_processor.get_file_type(uploaded_file.name)
                
                if not file_type:
                    logger.warning(f"Skipping unsupported file: {uploaded_file.name}")
                    continue

                # Convert uploaded file to BytesIO
                file_content = BytesIO(uploaded_file.read())
                
                # Reset file pointer for potential re-reading
                uploaded_file.seek(0)

                # Process the document
                content = await self.document_processor.process_document(
                    file_content, uploaded_file.name, file_type
                )
                
                all_content.extend(content)
                
                # Update file status in session state
                self._update_file_status(uploaded_file.name, "processed", len(content))

            except Exception as e:
                logger.error(f"Error processing {uploaded_file.name}: {e}")
                self._update_file_status(uploaded_file.name, "error", 0)
                
                if show_progress:
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")

        if show_progress:
            progress_bar.progress(1.0)
            status_text.text(f"✅ Completed processing {total_files} files")

        # Store content in session state
        st.session_state[self.content_key] = all_content
        
        logger.info(f"Processed {total_files} files, extracted {len(all_content)} content items")
        return all_content

    def _update_file_status(
        self,
        filename: str,
        status: str,
        content_count: int = 0
    ) -> None:
        """
        Update file processing status in session state.

        Args:
            filename: Name of the file to update
            status: New processing status
            content_count: Number of extracted content items
        """
        files_info = st.session_state.get(self.session_key, [])
        
        for file_info in files_info:
            if file_info.filename == filename:
                file_info.processing_status = status
                file_info.extracted_content_count = content_count
                break

        st.session_state[self.session_key] = files_info

    def get_extracted_content(self) -> List[ExtractedContent]:
        """
        Get extracted content from session state.

        Returns:
            List of extracted content items
        """
        return st.session_state.get(self.content_key, [])

    def get_uploaded_files_info(self) -> List[FileUploadInfo]:
        """
        Get uploaded files information from session state.

        Returns:
            List of file upload information
        """
        return st.session_state.get(self.session_key, [])

    def clear_uploads(self) -> None:
        """Clear uploaded files and extracted content from session state."""
        st.session_state[self.session_key] = []
        st.session_state[self.content_key] = []

    def render_content_preview(self, max_items: int = 5) -> None:
        """
        Render a preview of extracted content.

        Args:
            max_items: Maximum number of content items to preview
        """
        content = self.get_extracted_content()
        
        if not content:
            st.info("No content extracted yet. Upload and process files first.")
            return

        st.subheader("📄 Content Preview")
        
        # Show summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items", len(content))
        with col2:
            pptx_count = sum(1 for c in content if c.file_type == "pptx")
            st.metric("PowerPoint Slides", pptx_count)
        with col3:
            pdf_count = sum(1 for c in content if c.file_type == "pdf")
            st.metric("PDF Pages", pdf_count)

        # Show content preview
        st.write("**Content Preview:**")
        
        for i, item in enumerate(content[:max_items]):
            with st.expander(f"{item.source_file} - {item.title}"):
                st.write(f"**Type:** {item.file_type.upper()}")
                st.write(f"**Layout:** {item.layout_type}")
                st.write(f"**Content Preview:**")
                preview_content = item.content[:300] + "..." if len(item.content) > 300 else item.content
                st.text(preview_content)

        if len(content) > max_items:
            st.info(f"Showing {max_items} of {len(content)} items. Processing will use all content.")

    def estimate_processing_time(self) -> float:
        """
        Estimate total processing time for uploaded files.

        Returns:
            Estimated processing time in seconds
        """
        files_info = self.get_uploaded_files_info()
        file_sizes = [info.file_size for info in files_info]
        
        return self.document_processor.estimate_processing_time(file_sizes)