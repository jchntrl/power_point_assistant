"""
Configuration settings for PowerPoint Assistant.

This module uses pydantic-settings to manage environment variables
and application configuration with validation.
"""

import logging
import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    openai_api_key: str = Field(
        ..., description="OpenAI API key for LLM integration"
    )
    openai_model: str = Field(
        default="gpt-4o-mini", description="OpenAI model to use for generation"
    )

    # PowerPoint Templates
    template_dir: Path = Field(
        default=Path("./templates"), description="Directory containing PowerPoint templates"
    )
    default_template: str = Field(
        default="Keyrus Commercial - Template.pptx",
        description="Default PowerPoint template filename"
    )

    # Data Directories
    previous_decks_dir: Path = Field(
        default=Path("./data/previous_decks"),
        description="Directory for storing previous deck files"
    )
    output_dir: Path = Field(
        default=Path("./data/generated"),
        description="Directory for generated presentations"
    )

    # File Upload Settings
    max_file_size_mb: int = Field(
        default=10, ge=1, le=100, description="Maximum file size in MB"
    )
    max_files: int = Field(
        default=5, ge=1, le=10, description="Maximum number of files to upload"
    )
    allowed_extensions: str = Field(
        default="pptx,pdf", description="Comma-separated list of allowed file extensions"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    log_file: Optional[Path] = Field(
        default=Path("./logs/powerpoint_assistant.log"),
        description="Log file path (optional)"
    )

    # Application Settings
    app_title: str = Field(
        default="PowerPoint Assistant",
        description="Application title for Streamlit interface"
    )
    app_description: str = Field(
        default="Generate branded PowerPoint presentations using AI",
        description="Application description"
    )

    # Processing Settings
    max_slides: int = Field(
        default=15, ge=3, le=30, description="Maximum number of slides to generate"
    )
    min_slides: int = Field(
        default=3, ge=1, le=10, description="Minimum number of slides to generate"
    )
    
    # LangChain Settings
    langchain_verbose: bool = Field(
        default=False, description="Enable verbose logging for LangChain"
    )
    langchain_debug: bool = Field(
        default=False, description="Enable debug mode for LangChain"
    )

    class Config:
        """Pydantic configuration."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    @validator("template_dir", "previous_decks_dir", "output_dir")
    def validate_directories(cls, v: Path) -> Path:
        """Validate that directories exist or can be created."""
        if not v.exists():
            try:
                v.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Cannot create directory {v}: {e}")
        return v

    @validator("default_template")
    def validate_default_template(cls, v: str, values: dict) -> str:
        """Validate that the default template exists."""
        # First check in template_dir
        template_dir = values.get("template_dir", Path("./templates"))
        template_path = template_dir / v
        
        if template_path.exists():
            return v
            
        # Fallback: check in project root (for Keyrus templates)
        root_template_path = Path(v)
        if root_template_path.exists():
            return v
            
        # Log warning but don't fail - template might be uploaded later
        logging.warning(f"Default template {v} not found in {template_dir} or project root")
        return v

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper

    @validator("allowed_extensions")
    def validate_extensions(cls, v: str) -> str:
        """Validate file extensions."""
        extensions = [ext.strip().lower() for ext in v.split(",")]
        valid_extensions = {"pptx", "pdf"}
        
        for ext in extensions:
            if ext not in valid_extensions:
                raise ValueError(f"Invalid extension: {ext}. Must be one of {valid_extensions}")
        
        return ",".join(extensions)

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed extensions as a list."""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def template_path(self) -> Path:
        """Get the full path to the default template."""
        # First try in template_dir
        template_path = self.template_dir / self.default_template
        if template_path.exists():
            return template_path
            
        # Fallback to project root
        root_template_path = Path(self.default_template)
        if root_template_path.exists():
            return root_template_path
            
        # Return template_dir path anyway - might be created later
        return template_path

    def setup_logging(self) -> None:
        """Setup logging configuration."""
        # Create logs directory if it doesn't exist
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging_config = {
            "level": getattr(logging, self.log_level),
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }

        if self.log_file:
            logging_config["handlers"] = [
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]

        logging.basicConfig(**logging_config)

    def validate_api_key(self) -> bool:
        """Validate that the OpenAI API key is properly configured."""
        if not self.openai_api_key or self.openai_api_key.startswith("sk-your-"):
            return False
        
        # Basic format validation for OpenAI API keys
        if not self.openai_api_key.startswith("sk-"):
            return False
            
        return True


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()


def load_env() -> None:
    """Load environment variables from .env file."""
    from dotenv import load_dotenv
    
    # Load from .env file if it exists
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
    
    # Setup logging
    settings.setup_logging()
    
    # Validate API key
    if not settings.validate_api_key():
        logging.warning(
            "OpenAI API key not properly configured. "
            "Please set OPENAI_API_KEY in your .env file."
        )