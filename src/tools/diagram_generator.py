"""
Core diagram generation using diagrams library.

This module provides the core functionality for generating architecture diagrams
from specifications using the Python diagrams library with proper async support.
"""

import asyncio
import gc
import logging
import time
from pathlib import Path
from typing import Any, Dict, List

# Initialize logger first
logger = logging.getLogger(__name__)

try:
    from diagrams import Cluster, Diagram
    from diagrams.aws.analytics import EMR, Glue, Kinesis, Redshift
    from diagrams.aws.compute import EC2, ECS, Lambda
    from diagrams.aws.database import Dynamodb, RDS
    from diagrams.aws.integration import SQS, SNS
    from diagrams.aws.network import APIGateway, ElasticLoadBalancing
    from diagrams.aws.storage import S3
    from diagrams.azure.analytics import DataFactories, EventHubs, SynapseAnalytics
    from diagrams.azure.compute import FunctionApps, ContainerInstances
    from diagrams.azure.database import CosmosDb, SQLDatabases
    from diagrams.azure.integration import ServiceBus
    from diagrams.azure.network import LoadBalancers, ApplicationGateway
    from diagrams.azure.storage import BlobStorage
    from diagrams.gcp.analytics import Bigquery, Dataflow, Pubsub
    from diagrams.gcp.compute import Functions, KubernetesEngine, ComputeEngine  
    from diagrams.gcp.database import SQL, Firestore
    from diagrams.gcp.network import LoadBalancing
    from diagrams.gcp.storage import Storage
    from diagrams.k8s.compute import Pod
    from diagrams.k8s.network import Service
    from diagrams.onprem.database import PostgreSQL, MySQL
    from diagrams.onprem.inmemory import Redis
    from diagrams.onprem.queue import RabbitMQ
    
    DIAGRAMS_AVAILABLE = True
    
except ImportError as e:
    # Create dummy classes as fallbacks
    logger.warning(f"Diagrams library not fully available: {e}")
    DIAGRAMS_AVAILABLE = False
    
    # Create placeholder classes
    class DummyDiagramComponent:
        def __init__(self, name):
            self.name = name
    
    # AWS placeholders
    EMR = Glue = Kinesis = Redshift = DummyDiagramComponent
    EC2 = ECS = Lambda = DummyDiagramComponent
    Dynamodb = RDS = DummyDiagramComponent
    SQS = SNS = DummyDiagramComponent
    APIGateway = ElasticLoadBalancing = DummyDiagramComponent
    S3 = DummyDiagramComponent
    
    # Azure placeholders
    DataFactories = EventHubs = SynapseAnalytics = DummyDiagramComponent
    FunctionApps = ContainerInstances = DummyDiagramComponent
    CosmosDb = SQLDatabases = DummyDiagramComponent
    ServiceBus = DummyDiagramComponent
    LoadBalancers = ApplicationGateway = DummyDiagramComponent
    BlobStorage = DummyDiagramComponent
    
    # GCP placeholders
    Bigquery = Dataflow = Pubsub = DummyDiagramComponent
    Functions = KubernetesEngine = ComputeEngine = DummyDiagramComponent
    SQL = Firestore = DummyDiagramComponent
    LoadBalancing = DummyDiagramComponent
    Storage = DummyDiagramComponent
    
    # Kubernetes placeholders
    Pod = Service = DummyDiagramComponent
    
    # OnPrem placeholders
    PostgreSQL = MySQL = DummyDiagramComponent
    Redis = DummyDiagramComponent
    RabbitMQ = DummyDiagramComponent
    
    # Diagram placeholders
    class DummyDiagram:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    
    class DummyCluster:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    
    Diagram = DummyDiagram
    Cluster = DummyCluster

from ..config.settings import settings
from ..models.data_models import DiagramComponent, DiagramSpec, GeneratedDiagram


class DiagramGenerator:
    """
    Core diagram generation using diagrams library.
    
    Generates architecture diagrams from specifications with proper
    async support and resource management.
    """

    def __init__(self, output_dir: Path, styling_config: Dict[str, Any]):
        """
        Initialize diagram generator.

        Args:
            output_dir: Directory for generated diagram files
            styling_config: Styling configuration for diagrams
        """
        self.output_dir = output_dir
        self.styling = styling_config
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Component icon mappings
        self.icon_mappings = self._initialize_icon_mappings()
        
        logger.info(f"DiagramGenerator initialized with output dir: {output_dir}")

    def _initialize_icon_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize icon mappings for different providers and component types."""
        return {
            "aws": {
                "api": APIGateway,
                "service": Lambda,
                "microservice": Lambda,
                "database": RDS,
                "nosql": Dynamodb,
                "queue": SQS,
                "notification": SNS,
                "storage": S3,
                "compute": EC2,
                "container": ECS,
                "loadbalancer": ElasticLoadBalancing,
                "analytics": EMR,
                "etl": Glue,
                "streaming": Kinesis,
                "warehouse": Redshift
            },
            "azure": {
                "api": ApplicationGateway,
                "service": FunctionApps,
                "microservice": FunctionApps,
                "database": SQLDatabases,
                "nosql": CosmosDb,
                "queue": ServiceBus,
                "notification": ServiceBus,
                "storage": BlobStorage,
                "compute": ContainerInstances,
                "container": ContainerInstances,
                "loadbalancer": LoadBalancers,
                "analytics": SynapseAnalytics,
                "etl": DataFactories,
                "streaming": EventHubs
            },
            "gcp": {
                "api": LoadBalancing,
                "service": Functions,
                "microservice": Functions,
                "database": SQL,
                "nosql": Firestore,
                "queue": Pubsub,
                "notification": Pubsub,
                "storage": Storage,
                "compute": ComputeEngine,
                "container": KubernetesEngine,
                "loadbalancer": LoadBalancing,
                "analytics": Bigquery,
                "etl": Dataflow,
                "streaming": Pubsub
            },
            "kubernetes": {
                "service": Pod,
                "microservice": Pod,
                "network": Service
            },
            "onprem": {
                "database": PostgreSQL,
                "mysql": MySQL,
                "cache": Redis,
                "queue": RabbitMQ
            }
        }

    async def generate_diagram(self, spec: DiagramSpec) -> GeneratedDiagram:
        """
        Generate diagram from specification.

        Args:
            spec: Diagram specification with components and connections

        Returns:
            GeneratedDiagram object with path and metadata

        Raises:
            ValueError: If diagram generation fails
            FileNotFoundError: If generated file is not found
        """
        start_time = time.time() * 1000  # Start timing in milliseconds
        
        try:
            logger.info(f"Starting diagram generation: {spec.title}")
            
            # Check if diagrams library is available
            if not DIAGRAMS_AVAILABLE:
                raise ValueError(
                    "Diagrams library not available. Please install: pip install diagrams graphviz"
                )
            
            # Create safe filename
            safe_title = spec.title.lower().replace(' ', '_').replace('-', '_')
            diagram_filename = f"{safe_title}_{int(start_time)}"
            diagram_path = self.output_dir / f"{diagram_filename}.png"
            
            # Run diagram generation in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._generate_diagram_sync, spec, str(diagram_path.with_suffix(''))
            )
            
            # Verify file was created
            if not diagram_path.exists():
                raise FileNotFoundError(f"Diagram generation failed: {diagram_path}")
            
            # Calculate generation time and file size
            generation_time = int(time.time() * 1000 - start_time)
            file_size_kb = diagram_path.stat().st_size // 1024
            
            # Determine slide target and positioning
            slide_target = 2  # Default to second slide for diagrams
            position = self._calculate_slide_position(spec.diagram_type)
            
            result = GeneratedDiagram(
                spec=spec,
                image_path=diagram_path,
                file_size_kb=file_size_kb,
                generation_time_ms=generation_time,
                slide_target=slide_target,
                position=position
            )
            
            logger.info(
                f"Successfully generated diagram: {diagram_path.name} "
                f"({file_size_kb}KB, {generation_time}ms)"
            )
            return result
            
        except Exception as e:
            error_msg = f"Diagram generation failed for {spec.title}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        finally:
            # Force garbage collection to free memory
            gc.collect()

    def _generate_diagram_sync(self, spec: DiagramSpec, output_path: str) -> None:
        """
        Generate diagram synchronously using diagrams library.

        Args:
            spec: Diagram specification
            output_path: Output path without extension
        """
        # Configure diagram styling
        diagram_attrs = {
            "show": False,
            "direction": spec.layout_direction,
            "filename": output_path,
            "outformat": "png",
            "graph_attr": self._get_graph_attributes()
        }
        
        # Add custom styling if provided, filtering out invalid parameters
        if spec.styling:
            # Valid Diagram parameters
            valid_params = {
                'name', 'filename', 'direction', 'curvestyle', 'outformat', 
                'autolabel', 'show', 'strict', 'graph_attr', 'node_attr', 'edge_attr'
            }
            
            # Filter out invalid parameters
            valid_styling = {k: v for k, v in spec.styling.items() if k in valid_params}
            invalid_params = {k: v for k, v in spec.styling.items() if k not in valid_params}
            
            if invalid_params:
                logger.debug(f"Filtering out invalid diagram parameters: {list(invalid_params.keys())}")
            
            diagram_attrs.update(valid_styling)

        # Generate diagram using context manager
        with Diagram(spec.title, **diagram_attrs):
            # Create components
            components = self._create_components(spec.components)
            
            # Apply clustering if specified
            if spec.clustering:
                components = self._apply_clustering(components, spec.clustering)
            
            # Create connections
            self._create_connections(components, spec.connections)

    def _create_components(self, component_specs: List[DiagramComponent]) -> Dict[str, Any]:
        """
        Create diagram components from specifications.

        Args:
            component_specs: List of component specifications

        Returns:
            Dictionary mapping component names to diagram objects
        """
        components = {}
        
        for comp_spec in component_specs:
            try:
                # Get appropriate icon class
                icon_class = self._get_icon_class(
                    comp_spec.icon_provider, 
                    comp_spec.component_type,
                    comp_spec.icon_name
                )
                
                # Create component instance
                component = icon_class(comp_spec.name)
                components[comp_spec.name] = component
                
                logger.debug(f"Created component: {comp_spec.name} ({comp_spec.component_type})")
                
            except Exception as e:
                logger.warning(
                    f"Failed to create component {comp_spec.name}: {e}. "
                    f"Using default component."
                )
                # Fallback to basic AWS service
                components[comp_spec.name] = Lambda(comp_spec.name)
        
        return components

    def _get_icon_class(self, provider: str, component_type: str, icon_name: str) -> Any:
        """
        Get appropriate icon class for component.

        Args:
            provider: Icon provider (aws, azure, gcp, etc.)
            component_type: Type of component
            icon_name: Specific icon name

        Returns:
            Icon class from diagrams library
        """
        provider_icons = self.icon_mappings.get(provider, {})
        
        # Try exact component type match first
        if component_type in provider_icons:
            return provider_icons[component_type]
        
        # Try icon name match
        if icon_name.lower() in provider_icons:
            return provider_icons[icon_name.lower()]
        
        # Fallback to default service for provider
        if provider in self.icon_mappings:
            return provider_icons.get("service", Lambda)
        
        # Ultimate fallback
        return Lambda

    def _apply_clustering(
        self, 
        components: Dict[str, Any], 
        clustering: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Apply clustering to components.

        Args:
            components: Component dictionary
            clustering: Clustering specification

        Returns:
            Updated components dictionary with clusters
        """
        clustered_components = {}
        unclustered = dict(components)
        
        for cluster_name, component_names in clustering.items():
            with Cluster(cluster_name):
                cluster_components = {}
                for comp_name in component_names:
                    if comp_name in unclustered:
                        cluster_components[comp_name] = unclustered.pop(comp_name)
                
                clustered_components.update(cluster_components)
        
        # Add remaining unclustered components
        clustered_components.update(unclustered)
        
        return clustered_components

    def _create_connections(
        self, 
        components: Dict[str, Any], 
        connections: List[Any]
    ) -> None:
        """
        Create connections between components.

        Args:
            components: Component dictionary
            connections: List of connection specifications
        """
        for connection in connections:
            try:
                source = components.get(connection.source)
                target = components.get(connection.target)
                
                if source and target:
                    if connection.connection_type == "bidirectional":
                        source - target  # Bidirectional connection
                    else:
                        source >> target  # Default arrow connection
                    
                    logger.debug(f"Connected {connection.source} -> {connection.target}")
                else:
                    logger.warning(
                        f"Cannot connect {connection.source} -> {connection.target}: "
                        f"Component not found"
                    )
                    
            except Exception as e:
                logger.warning(f"Failed to create connection: {e}")

    def _get_graph_attributes(self) -> Dict[str, str]:
        """
        Get Graphviz graph attributes for styling.

        Returns:
            Dictionary of graph attributes
        """
        return {
            "fontsize": "16",
            "fontcolor": settings.keyrus_secondary_color,
            "bgcolor": "transparent",
            "dpi": str(settings.diagram_dpi),
            "margin": "0.2",
            "nodesep": "0.5",
            "ranksep": "0.8"
        }

    def _calculate_slide_position(self, diagram_type: str) -> Dict[str, float]:
        """
        Calculate optimal slide position for diagram type.

        Args:
            diagram_type: Type of diagram

        Returns:
            Position dictionary with left, top, width, height
        """
        # Standard positioning for different diagram types
        positions = {
            "microservices": {"left": 0.5, "top": 1.5, "width": 9.0, "height": 5.5},
            "data_pipeline": {"left": 0.5, "top": 1.5, "width": 9.0, "height": 5.0},
            "cloud_architecture": {"left": 0.5, "top": 1.5, "width": 9.0, "height": 6.0},
            "database_schema": {"left": 1.0, "top": 2.0, "width": 8.0, "height": 5.0}
        }
        
        return positions.get(diagram_type, positions["microservices"])

    async def cleanup_old_diagrams(self, max_age_hours: int = 24) -> int:
        """
        Clean up old diagram files.

        Args:
            max_age_hours: Maximum age of files to keep in hours

        Returns:
            Number of files cleaned up
        """
        try:
            import time
            
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            cleanup_count = 0
            
            for file_path in self.output_dir.glob("*.png"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        cleanup_count += 1
                        logger.debug(f"Cleaned up old diagram: {file_path.name}")
            
            if cleanup_count > 0:
                logger.info(f"Cleaned up {cleanup_count} old diagram files")
            
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Error during diagram cleanup: {e}")
            return 0

    def get_supported_providers(self) -> List[str]:
        """
        Get list of supported icon providers.

        Returns:
            List of provider names
        """
        return list(self.icon_mappings.keys())

    def get_supported_components(self, provider: str) -> List[str]:
        """
        Get list of supported component types for a provider.

        Args:
            provider: Icon provider name

        Returns:
            List of component type names
        """
        return list(self.icon_mappings.get(provider, {}).keys())