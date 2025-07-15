#!/usr/bin/env python3
"""
Test script for diagram generation based on the Cloud Analytics Platform Migration Project.

This script tests the diagram generation capabilities using the technologies
mentioned in the project_example_cloud_analytics.md file.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List

# Add src to path
sys.path.append('/mnt/c/Users/Julien.Chantrel/Documents/Tools/power_point_assistant')

# Define output directory for test diagrams
OUTPUT_DIR = Path('/mnt/c/Users/Julien.Chantrel/Documents/Tools/power_point_assistant/examples/diagrams')

from src.tools.diagram_generator import DiagramGenerator
from src.models.data_models import DiagramSpec, DiagramComponent, DiagramConnection


async def test_multi_cloud_architecture():
    """Test multi-cloud architecture diagram generation."""
    print("🔧 Testing Multi-Cloud Architecture Diagram...")
    
    spec = DiagramSpec(
        title="Multi-Cloud Architecture for Financial Analytics",
        diagram_type="cloud_architecture",
        layout_direction="TB",
        components=[
            # AWS Components
            DiagramComponent(
                name="AWS API Gateway",
                component_type="api",
                icon_provider="aws",
                icon_name="apigateway"
            ),
            DiagramComponent(
                name="AWS Lambda",
                component_type="service",
                icon_provider="aws",
                icon_name="lambda"
            ),
            DiagramComponent(
                name="AWS S3 Data Lake",
                component_type="storage",
                icon_provider="aws",
                icon_name="s3"
            ),
            DiagramComponent(
                name="AWS RDS",
                component_type="database",
                icon_provider="aws",
                icon_name="rds"
            ),
            DiagramComponent(
                name="AWS Kinesis",
                component_type="streaming",
                icon_provider="aws",
                icon_name="kinesis"
            ),
            DiagramComponent(
                name="AWS Redshift",
                component_type="warehouse",
                icon_provider="aws",
                icon_name="redshift"
            ),
            
            # Azure Components
            DiagramComponent(
                name="Azure Functions",
                component_type="service",
                icon_provider="azure",
                icon_name="functions"
            ),
            DiagramComponent(
                name="Azure Blob Storage",
                component_type="storage",
                icon_provider="azure",
                icon_name="blob"
            ),
            DiagramComponent(
                name="Azure SQL Database",
                component_type="database",
                icon_provider="azure",
                icon_name="sql"
            ),
            DiagramComponent(
                name="Azure Synapse",
                component_type="analytics",
                icon_provider="azure",
                icon_name="synapse"
            ),
            
            # GCP Components
            DiagramComponent(
                name="GCP BigQuery",
                component_type="analytics",
                icon_provider="gcp",
                icon_name="bigquery"
            ),
            DiagramComponent(
                name="GCP Cloud Functions",
                component_type="service",
                icon_provider="gcp",
                icon_name="functions"
            ),
            DiagramComponent(
                name="GCP Cloud Storage",
                component_type="storage",
                icon_provider="gcp",
                icon_name="storage"
            )
        ],
        connections=[
            DiagramConnection(
                source="AWS API Gateway",
                target="AWS Lambda",
                connection_type="arrow",
                label="API Calls"
            ),
            DiagramConnection(
                source="AWS Lambda",
                target="AWS S3 Data Lake",
                connection_type="arrow",
                label="Data Storage"
            ),
            DiagramConnection(
                source="AWS Kinesis",
                target="AWS Redshift",
                connection_type="arrow",
                label="Stream Processing"
            ),
            DiagramConnection(
                source="Azure Functions",
                target="Azure Synapse",
                connection_type="arrow",
                label="Analytics"
            ),
            DiagramConnection(
                source="GCP Cloud Functions",
                target="GCP BigQuery",
                connection_type="arrow",
                label="ML Processing"
            )
        ],
        clustering={
            "AWS Services": ["AWS API Gateway", "AWS Lambda", "AWS S3 Data Lake", "AWS RDS", "AWS Kinesis", "AWS Redshift"],
            "Azure Services": ["Azure Functions", "Azure Blob Storage", "Azure SQL Database", "Azure Synapse"],
            "GCP Services": ["GCP BigQuery", "GCP Cloud Functions", "GCP Cloud Storage"]
        },
        styling={
            "direction": "TB",
            "curvestyle": "ortho"
        }
    )
    
    return spec


async def test_data_processing_pipeline():
    """Test data processing pipeline diagram generation."""
    print("🔧 Testing Data Processing Pipeline Diagram...")
    
    spec = DiagramSpec(
        title="Real-Time Data Processing Pipeline",
        diagram_type="data_pipeline",
        layout_direction="LR",
        components=[
            # Data Sources
            DiagramComponent(
                name="PostgreSQL Legacy DB",
                component_type="database",
                icon_provider="onprem",
                icon_name="postgresql"
            ),
            DiagramComponent(
                name="MySQL CRM",
                component_type="mysql",
                icon_provider="onprem",
                icon_name="mysql"
            ),
            
            # Message Queues
            DiagramComponent(
                name="RabbitMQ",
                component_type="queue",
                icon_provider="onprem",
                icon_name="rabbitmq"
            ),
            DiagramComponent(
                name="AWS SQS",
                component_type="queue",
                icon_provider="aws",
                icon_name="sqs"
            ),
            
            # Stream Processing
            DiagramComponent(
                name="AWS Kinesis",
                component_type="streaming",
                icon_provider="aws",
                icon_name="kinesis"
            ),
            DiagramComponent(
                name="Azure Event Hubs",
                component_type="streaming",
                icon_provider="azure",
                icon_name="eventhubs"
            ),
            DiagramComponent(
                name="GCP Pub/Sub",
                component_type="streaming",
                icon_provider="gcp",
                icon_name="pubsub"
            ),
            
            # Processing
            DiagramComponent(
                name="AWS Glue ETL",
                component_type="etl",
                icon_provider="aws",
                icon_name="glue"
            ),
            DiagramComponent(
                name="Azure Data Factory",
                component_type="etl",
                icon_provider="azure",
                icon_name="datafactory"
            ),
            DiagramComponent(
                name="GCP Dataflow",
                component_type="etl",
                icon_provider="gcp",
                icon_name="dataflow"
            ),
            
            # Storage & Analytics
            DiagramComponent(
                name="AWS S3",
                component_type="storage",
                icon_provider="aws",
                icon_name="s3"
            ),
            DiagramComponent(
                name="Redis Cache",
                component_type="cache",
                icon_provider="onprem",
                icon_name="redis"
            ),
            DiagramComponent(
                name="AWS Redshift",
                component_type="warehouse",
                icon_provider="aws",
                icon_name="redshift"
            ),
            DiagramComponent(
                name="GCP BigQuery",
                component_type="analytics",
                icon_provider="gcp",
                icon_name="bigquery"
            )
        ],
        connections=[
            DiagramConnection(
                source="PostgreSQL Legacy DB",
                target="RabbitMQ",
                connection_type="arrow",
                label="CDC"
            ),
            DiagramConnection(
                source="MySQL CRM",
                target="AWS SQS",
                connection_type="arrow",
                label="Events"
            ),
            DiagramConnection(
                source="RabbitMQ",
                target="AWS Kinesis",
                connection_type="arrow",
                label="Stream"
            ),
            DiagramConnection(
                source="AWS SQS",
                target="Azure Event Hubs",
                connection_type="arrow",
                label="Multi-Cloud"
            ),
            DiagramConnection(
                source="AWS Kinesis",
                target="AWS Glue ETL",
                connection_type="arrow",
                label="Process"
            ),
            DiagramConnection(
                source="Azure Event Hubs",
                target="Azure Data Factory",
                connection_type="arrow",
                label="Transform"
            ),
            DiagramConnection(
                source="GCP Pub/Sub",
                target="GCP Dataflow",
                connection_type="arrow",
                label="ML Pipeline"
            ),
            DiagramConnection(
                source="AWS Glue ETL",
                target="AWS S3",
                connection_type="arrow",
                label="Store"
            ),
            DiagramConnection(
                source="AWS S3",
                target="Redis Cache",
                connection_type="arrow",
                label="Cache"
            ),
            DiagramConnection(
                source="AWS S3",
                target="AWS Redshift",
                connection_type="arrow",
                label="Analytics"
            ),
            DiagramConnection(
                source="GCP Dataflow",
                target="GCP BigQuery",
                connection_type="arrow",
                label="ML Results"
            )
        ],
        clustering={
            "Data Sources": ["PostgreSQL Legacy DB", "MySQL CRM"],
            "Message Queues": ["RabbitMQ", "AWS SQS"],
            "Stream Processing": ["AWS Kinesis", "Azure Event Hubs", "GCP Pub/Sub"],
            "ETL Processing": ["AWS Glue ETL", "Azure Data Factory", "GCP Dataflow"],
            "Storage & Analytics": ["AWS S3", "Redis Cache", "AWS Redshift", "GCP BigQuery"]
        },
        styling={
            "direction": "LR",
            "curvestyle": "curved"
        }
    )
    
    return spec


async def test_kubernetes_microservices():
    """Test Kubernetes microservices diagram generation."""
    print("🔧 Testing Kubernetes Microservices Diagram...")
    
    spec = DiagramSpec(
        title="Kubernetes Microservices Architecture",
        diagram_type="microservices",
        layout_direction="TB",
        components=[
            # Load Balancers
            DiagramComponent(
                name="AWS Load Balancer",
                component_type="loadbalancer",
                icon_provider="aws",
                icon_name="elb"
            ),
            DiagramComponent(
                name="Azure Load Balancer",
                component_type="loadbalancer",
                icon_provider="azure",
                icon_name="loadbalancer"
            ),
            
            # API Gateways
            DiagramComponent(
                name="AWS API Gateway",
                component_type="api",
                icon_provider="aws",
                icon_name="apigateway"
            ),
            DiagramComponent(
                name="Azure App Gateway",
                component_type="api",
                icon_provider="azure",
                icon_name="appgateway"
            ),
            
            # Kubernetes Services
            DiagramComponent(
                name="Auth Service Pod",
                component_type="service",
                icon_provider="kubernetes",
                icon_name="pod"
            ),
            DiagramComponent(
                name="Payment Service Pod",
                component_type="microservice",
                icon_provider="kubernetes",
                icon_name="pod"
            ),
            DiagramComponent(
                name="Analytics Service Pod",
                component_type="microservice",
                icon_provider="kubernetes",
                icon_name="pod"
            ),
            DiagramComponent(
                name="K8s Service Discovery",
                component_type="network",
                icon_provider="kubernetes",
                icon_name="service"
            ),
            
            # Databases
            DiagramComponent(
                name="AWS RDS",
                component_type="database",
                icon_provider="aws",
                icon_name="rds"
            ),
            DiagramComponent(
                name="Azure Cosmos DB",
                component_type="nosql",
                icon_provider="azure",
                icon_name="cosmosdb"
            ),
            DiagramComponent(
                name="GCP Cloud SQL",
                component_type="database",
                icon_provider="gcp",
                icon_name="sql"
            ),
            
            # Container Orchestration
            DiagramComponent(
                name="GCP Kubernetes Engine",
                component_type="container",
                icon_provider="gcp",
                icon_name="k8s"
            )
        ],
        connections=[
            DiagramConnection(
                source="AWS Load Balancer",
                target="AWS API Gateway",
                connection_type="arrow",
                label="Route"
            ),
            DiagramConnection(
                source="Azure Load Balancer",
                target="Azure App Gateway",
                connection_type="arrow",
                label="Route"
            ),
            DiagramConnection(
                source="AWS API Gateway",
                target="K8s Service Discovery",
                connection_type="arrow",
                label="Service Mesh"
            ),
            DiagramConnection(
                source="Azure App Gateway",
                target="K8s Service Discovery",
                connection_type="arrow",
                label="Service Mesh"
            ),
            DiagramConnection(
                source="K8s Service Discovery",
                target="Auth Service Pod",
                connection_type="arrow",
                label="Auth"
            ),
            DiagramConnection(
                source="K8s Service Discovery",
                target="Payment Service Pod",
                connection_type="arrow",
                label="Payment"
            ),
            DiagramConnection(
                source="K8s Service Discovery",
                target="Analytics Service Pod",
                connection_type="arrow",
                label="Analytics"
            ),
            DiagramConnection(
                source="Auth Service Pod",
                target="AWS RDS",
                connection_type="arrow",
                label="User Data"
            ),
            DiagramConnection(
                source="Payment Service Pod",
                target="Azure Cosmos DB",
                connection_type="arrow",
                label="Transactions"
            ),
            DiagramConnection(
                source="Analytics Service Pod",
                target="GCP Cloud SQL",
                connection_type="arrow",
                label="Metrics"
            )
        ],
        clustering={
            "Load Balancing": ["AWS Load Balancer", "Azure Load Balancer"],
            "API Layer": ["AWS API Gateway", "Azure App Gateway"],
            "Microservices": ["Auth Service Pod", "Payment Service Pod", "Analytics Service Pod", "K8s Service Discovery"],
            "Data Layer": ["AWS RDS", "Azure Cosmos DB", "GCP Cloud SQL"],
            "Orchestration": ["GCP Kubernetes Engine"]
        },
        styling={
            "direction": "TB",
            "curvestyle": "ortho"
        }
    )
    
    return spec


async def generate_and_test_diagram(spec: DiagramSpec, test_name: str) -> bool:
    """Generate and test a single diagram."""
    try:
        start_time = time.time()
        
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        generator = DiagramGenerator(OUTPUT_DIR, {})
        result = await generator.generate_diagram(spec)
        
        generation_time = time.time() - start_time
        
        print(f"✅ {test_name} - SUCCESS")
        print(f"   📁 File: {result.image_path.name}")
        print(f"   📂 Saved to: {result.image_path}")
        print(f"   📊 Size: {result.file_size_kb}KB")
        print(f"   ⏱️  Generation Time: {result.generation_time_ms}ms")
        print(f"   🎯 Slide Target: {result.slide_target}")
        print(f"   📍 Position: {result.position}")
        print(f"   🔧 Total Test Time: {generation_time:.2f}s")
        print(f"   🏗️  Components: {len(spec.components)}")
        print(f"   🔗 Connections: {len(spec.connections)}")
        print(f"   📦 Clusters: {len(spec.clustering)}")
        print()
        
        return True
            
    except Exception as e:
        print(f"❌ {test_name} - FAILED")
        print(f"   Error: {str(e)}")
        print()
        return False


async def main():
    """Main test function."""
    print("🚀 Starting Diagram Generation Tests")
    print("=" * 60)
    print()
    
    # Test specifications
    test_specs = [
        (await test_multi_cloud_architecture(), "Multi-Cloud Architecture"),
        (await test_data_processing_pipeline(), "Data Processing Pipeline"),
        (await test_kubernetes_microservices(), "Kubernetes Microservices")
    ]
    
    results = []
    total_start_time = time.time()
    
    for spec, test_name in test_specs:
        print(f"🔧 Running: {test_name}")
        print(f"   Components: {len(spec.components)} | Connections: {len(spec.connections)} | Clusters: {len(spec.clustering)}")
        
        success = await generate_and_test_diagram(spec, test_name)
        results.append((test_name, success))
    
    total_time = time.time() - total_start_time
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print()
    print(f"🎯 Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"⏱️  Total Test Time: {total_time:.2f}s")
    
    if successful == total:
        print("🎉 All tests passed! Diagram generation is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    print()
    print(f"📂 Diagrams saved to: {OUTPUT_DIR}")
    print("   You can view the generated diagrams in the examples/diagrams directory")
    print()
    print("🛠️  Technologies Tested:")
    print("   • AWS: EC2, Lambda, S3, RDS, DynamoDB, Kinesis, Glue, Redshift, API Gateway, SQS")
    print("   • Azure: Functions, Blob Storage, SQL Database, Cosmos DB, Event Hubs, Data Factory, Synapse")
    print("   • GCP: BigQuery, Cloud Functions, Cloud Storage, Cloud SQL, Pub/Sub, Dataflow, Kubernetes Engine")
    print("   • Kubernetes: Pods, Services")
    print("   • On-Premises: PostgreSQL, MySQL, Redis, RabbitMQ")
    print()


if __name__ == "__main__":
    asyncio.run(main())