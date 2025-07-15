"""
Diagram styling manager for Keyrus branding.

This module provides styling configuration and management for generated diagrams
to ensure consistent Keyrus branding and professional appearance.
"""

import logging
from typing import Any, Dict, List, Optional

from ..config.settings import settings

logger = logging.getLogger(__name__)


class DiagramStyler:
    """
    Manages diagram styling and branding for Keyrus presentations.
    
    Provides configuration-driven styling approach with consistent
    color schemes, fonts, and layout options.
    """

    def __init__(self):
        """Initialize diagram styler with Keyrus brand configuration."""
        self.brand_colors = self._initialize_brand_colors()
        self.style_templates = self._initialize_style_templates()
        self.layout_configurations = self._initialize_layout_configurations()
        
        logger.info("DiagramStyler initialized with Keyrus branding")

    def _initialize_brand_colors(self) -> Dict[str, str]:
        """
        Initialize Keyrus brand color palette.

        Returns:
            Dictionary of color names to hex values
        """
        return {
            "primary": settings.keyrus_primary_color,      # #0066CC
            "secondary": settings.keyrus_secondary_color,  # #333333
            "accent": settings.keyrus_accent_color,        # #FFFFFF
            "success": "#28A745",
            "warning": "#FFC107",
            "danger": "#DC3545",
            "info": "#17A2B8",
            "light_gray": "#F8F9FA",
            "medium_gray": "#6C757D",
            "dark_gray": "#343A40"
        }

    def _initialize_style_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize predefined style templates.

        Returns:
            Dictionary of style template configurations
        """
        return {
            "keyrus_brand": {
                "graph_attr": {
                    "bgcolor": "transparent",
                    "fontname": "Arial",
                    "fontsize": "16",
                    "fontcolor": self.brand_colors["secondary"],
                    "dpi": str(settings.diagram_dpi),
                    "margin": "0.3",
                    "nodesep": "0.6",
                    "ranksep": "1.0",
                    "splines": "ortho"
                },
                "node_attr": {
                    "fontname": "Arial",
                    "fontsize": "12",
                    "fontcolor": self.brand_colors["secondary"],
                    "style": "filled",
                    "fillcolor": self.brand_colors["accent"],
                    "color": self.brand_colors["primary"],
                    "penwidth": "2"
                },
                "edge_attr": {
                    "fontname": "Arial",
                    "fontsize": "10",
                    "fontcolor": self.brand_colors["secondary"],
                    "color": self.brand_colors["primary"],
                    "penwidth": "2",
                    "arrowsize": "0.8"
                }
            },
            "minimal": {
                "graph_attr": {
                    "bgcolor": "white",
                    "fontname": "Arial",
                    "fontsize": "14",
                    "dpi": str(settings.diagram_dpi),
                    "margin": "0.2",
                    "nodesep": "0.5",
                    "ranksep": "0.8"
                },
                "node_attr": {
                    "fontname": "Arial",
                    "fontsize": "11",
                    "style": "rounded,filled",
                    "fillcolor": "#F0F0F0",
                    "color": "#808080"
                },
                "edge_attr": {
                    "color": "#606060",
                    "penwidth": "1.5"
                }
            },
            "high_contrast": {
                "graph_attr": {
                    "bgcolor": "white",
                    "fontname": "Arial Bold",
                    "fontsize": "18",
                    "dpi": str(settings.diagram_dpi),
                    "margin": "0.4"
                },
                "node_attr": {
                    "fontname": "Arial Bold",
                    "fontsize": "14",
                    "style": "filled,bold",
                    "fillcolor": self.brand_colors["accent"],
                    "color": self.brand_colors["secondary"],
                    "penwidth": "3"
                },
                "edge_attr": {
                    "color": self.brand_colors["secondary"],
                    "penwidth": "3",
                    "arrowsize": "1.0"
                }
            }
        }

    def _initialize_layout_configurations(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize layout configurations for different diagram types.

        Returns:
            Dictionary of layout configurations
        """
        return {
            "microservices": {
                "direction": "TB",
                "cluster_style": {
                    "style": "rounded,filled",
                    "fillcolor": self.brand_colors["light_gray"],
                    "color": self.brand_colors["primary"],
                    "penwidth": "2",
                    "fontname": "Arial Bold",
                    "fontsize": "14"
                },
                "spacing": {
                    "nodesep": "0.8",
                    "ranksep": "1.2"
                }
            },
            "data_pipeline": {
                "direction": "LR",
                "cluster_style": {
                    "style": "rounded,dashed",
                    "color": self.brand_colors["info"],
                    "penwidth": "2"
                },
                "spacing": {
                    "nodesep": "1.0",
                    "ranksep": "1.5"
                }
            },
            "cloud_architecture": {
                "direction": "TB",
                "cluster_style": {
                    "style": "rounded,filled",
                    "fillcolor": self.brand_colors["light_gray"],
                    "color": self.brand_colors["primary"],
                    "penwidth": "2"
                },
                "spacing": {
                    "nodesep": "0.7",
                    "ranksep": "1.0"
                }
            },
            "database_schema": {
                "direction": "TB",
                "cluster_style": {
                    "style": "rounded,filled",
                    "fillcolor": "#E8F4FD",
                    "color": self.brand_colors["info"],
                    "penwidth": "2"
                },
                "spacing": {
                    "nodesep": "0.6",
                    "ranksep": "0.8"
                }
            }
        }

    def get_style_config(self, 
                        style_name: str = "keyrus_brand",
                        diagram_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get complete style configuration for diagram generation.

        Args:
            style_name: Name of style template to use
            diagram_type: Type of diagram for layout optimization

        Returns:
            Complete style configuration dictionary
        """
        # Get base style template
        base_style = self.style_templates.get(style_name, self.style_templates["keyrus_brand"])
        
        # Clone the base style to avoid modification
        style_config = {
            "graph_attr": dict(base_style.get("graph_attr", {})),
            "node_attr": dict(base_style.get("node_attr", {})),
            "edge_attr": dict(base_style.get("edge_attr", {}))
        }
        
        # Apply diagram type specific configurations
        if diagram_type and diagram_type in self.layout_configurations:
            layout_config = self.layout_configurations[diagram_type]
            
            # Update spacing
            if "spacing" in layout_config:
                style_config["graph_attr"].update(layout_config["spacing"])
            
            # Store cluster style for later use
            if "cluster_style" in layout_config:
                style_config["cluster_attr"] = layout_config["cluster_style"]
            
            # Update direction if specified
            if "direction" in layout_config:
                style_config["direction"] = layout_config["direction"]
        
        logger.debug(f"Generated style config for {style_name} ({diagram_type})")
        return style_config

    def get_component_styling(self, 
                             component_type: str,
                             provider: str = "aws") -> Dict[str, str]:
        """
        Get component-specific styling.

        Args:
            component_type: Type of component
            provider: Cloud provider

        Returns:
            Component styling dictionary
        """
        # Define component type color mappings
        component_colors = {
            "api": self.brand_colors["primary"],
            "service": self.brand_colors["info"],
            "microservice": self.brand_colors["info"],
            "database": self.brand_colors["success"],
            "nosql": self.brand_colors["success"],
            "queue": self.brand_colors["warning"],
            "notification": self.brand_colors["warning"],
            "storage": self.brand_colors["medium_gray"],
            "compute": self.brand_colors["primary"],
            "container": self.brand_colors["info"],
            "loadbalancer": self.brand_colors["danger"],
            "analytics": "#8A2BE2",  # Purple for analytics
            "etl": "#FF6347",        # Tomato for ETL
            "streaming": "#32CD32"   # Lime for streaming
        }
        
        color = component_colors.get(component_type, self.brand_colors["secondary"])
        
        return {
            "fillcolor": self.brand_colors["accent"],
            "color": color,
            "fontcolor": self.brand_colors["secondary"],
            "penwidth": "2",
            "style": "filled,rounded"
        }

    def get_cluster_styling(self, 
                           cluster_name: str,
                           diagram_type: str = "microservices") -> Dict[str, str]:
        """
        Get cluster-specific styling.

        Args:
            cluster_name: Name of the cluster
            diagram_type: Type of diagram

        Returns:
            Cluster styling dictionary
        """
        layout_config = self.layout_configurations.get(diagram_type, {})
        base_cluster_style = layout_config.get("cluster_style", {})
        
        # Custom cluster colors based on common naming patterns
        cluster_colors = {
            "web": self.brand_colors["primary"],
            "api": self.brand_colors["info"],
            "database": self.brand_colors["success"],
            "data": self.brand_colors["success"],
            "queue": self.brand_colors["warning"],
            "cache": self.brand_colors["danger"],
            "analytics": "#8A2BE2",
            "processing": "#FF6347",
            "storage": self.brand_colors["medium_gray"]
        }
        
        # Match cluster name to color pattern
        cluster_color = self.brand_colors["primary"]  # Default
        for pattern, color in cluster_colors.items():
            if pattern.lower() in cluster_name.lower():
                cluster_color = color
                break
        
        # Merge with base style
        cluster_style = dict(base_cluster_style)
        cluster_style["color"] = cluster_color
        
        return cluster_style

    def get_connection_styling(self, 
                              connection_type: str = "arrow",
                              source_type: str = "service",
                              target_type: str = "service") -> Dict[str, str]:
        """
        Get connection-specific styling.

        Args:
            connection_type: Type of connection
            source_type: Source component type
            target_type: Target component type

        Returns:
            Connection styling dictionary
        """
        base_style = {
            "color": self.brand_colors["secondary"],
            "penwidth": "2",
            "fontcolor": self.brand_colors["secondary"],
            "fontsize": "10"
        }
        
        # Customize based on connection type
        if connection_type == "bidirectional":
            base_style.update({
                "dir": "both",
                "arrowhead": "normal",
                "arrowtail": "normal",
                "penwidth": "2.5"
            })
        elif connection_type == "data_flow":
            base_style.update({
                "color": self.brand_colors["info"],
                "style": "bold",
                "penwidth": "3"
            })
        elif connection_type == "async":
            base_style.update({
                "style": "dashed",
                "color": self.brand_colors["warning"]
            })
        
        return base_style

    def validate_style_config(self, style_config: Dict[str, Any]) -> bool:
        """
        Validate style configuration for completeness.

        Args:
            style_config: Style configuration to validate

        Returns:
            True if valid, False otherwise
        """
        required_sections = ["graph_attr", "node_attr", "edge_attr"]
        
        for section in required_sections:
            if section not in style_config:
                logger.warning(f"Missing required style section: {section}")
                return False
        
        # Validate required graph attributes
        required_graph_attrs = ["dpi", "fontname"]
        graph_attrs = style_config.get("graph_attr", {})
        
        for attr in required_graph_attrs:
            if attr not in graph_attrs:
                logger.warning(f"Missing required graph attribute: {attr}")
                return False
        
        return True

    def get_available_styles(self) -> List[str]:
        """
        Get list of available style templates.

        Returns:
            List of style template names
        """
        return list(self.style_templates.keys())

    def get_available_diagram_types(self) -> List[str]:
        """
        Get list of supported diagram types.

        Returns:
            List of diagram type names
        """
        return list(self.layout_configurations.keys())

    def customize_style(self, 
                       base_style: str,
                       customizations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply custom modifications to a base style.

        Args:
            base_style: Name of base style template
            customizations: Custom style modifications

        Returns:
            Customized style configuration
        """
        style_config = self.get_style_config(base_style)
        
        # Apply customizations with deep merge
        for section, attrs in customizations.items():
            if section in style_config:
                style_config[section].update(attrs)
            else:
                style_config[section] = attrs
        
        logger.debug(f"Applied customizations to {base_style} style")
        return style_config