# Examples

This directory contains example projects and generated diagrams for the PowerPoint Assistant application.

## 📁 Directory Structure

```
examples/
├── diagrams/                 # Generated architecture diagrams
│   ├── multi_cloud_*.png    # Multi-cloud architecture examples
│   ├── real_time_data_*.png # Data processing pipeline examples
│   └── kubernetes_*.png     # Kubernetes microservices examples
└── README.md                # This file
```

## 🏗️ Example Diagrams

The following diagrams are automatically generated using the `test_diagram_generation.py` script:

### 1. Multi-Cloud Architecture
- **File Pattern**: `multi_cloud_architecture_for_financial_analytics_*.png`
- **Components**: 13 components across AWS, Azure, and GCP
- **Features**: Cross-cloud integration, clustered by provider
- **Technologies**: API Gateway, Lambda, S3, Functions, BigQuery, etc.

### 2. Data Processing Pipeline
- **File Pattern**: `real_time_data_processing_pipeline_*.png`
- **Components**: 14 components including streaming, ETL, and storage
- **Features**: End-to-end data flow from sources to analytics
- **Technologies**: Kinesis, Event Hubs, Glue, Data Factory, BigQuery, etc.

### 3. Kubernetes Microservices
- **File Pattern**: `kubernetes_microservices_architecture_*.png`
- **Components**: 12 components including load balancers, services, and databases
- **Features**: Container orchestration with multi-cloud databases
- **Technologies**: Kubernetes Pods, Services, RDS, Cosmos DB, Cloud SQL, etc.

## 🚀 Generating New Diagrams

To generate fresh example diagrams:

```bash
# Activate virtual environment
source linux_venv/bin/activate

# Run diagram generation test
python test_diagram_generation.py

# View generated diagrams
ls examples/diagrams/
```

## 📊 Example Performance Metrics

Typical diagram generation performance:
- **Generation Time**: 1.2 - 1.7 seconds per diagram
- **File Size**: 700KB - 900KB (high-quality PNG)
- **Components**: 12-14 components per diagram
- **Connections**: 5-11 labeled connections per diagram
- **Clusters**: 3-5 logical groupings per diagram

## 🛠️ Technologies Demonstrated

### Cloud Providers
- **AWS**: EC2, Lambda, S3, RDS, DynamoDB, Kinesis, Glue, EMR, Redshift, API Gateway, SQS, SNS
- **Azure**: Container Instances, Functions, Blob Storage, SQL Database, Cosmos DB, Event Hubs, Data Factory, Synapse Analytics, Service Bus, Application Gateway, Load Balancer
- **GCP**: Compute Engine, Cloud Functions, Cloud Storage, Cloud SQL, Firestore, Pub/Sub, Dataflow, BigQuery, Kubernetes Engine, Load Balancing

### Infrastructure
- **Kubernetes**: Pods, Services, Deployments
- **On-Premises**: PostgreSQL, MySQL, Redis, RabbitMQ

### Architecture Patterns
- **Multi-Cloud**: Cross-provider integration and failover
- **Data Pipeline**: Stream processing and batch analytics
- **Microservices**: Container-based service architecture
- **Event-Driven**: Asynchronous message processing

## 📈 Usage in Presentations

These diagrams are designed to be embedded in PowerPoint presentations:
- **High Resolution**: 300 DPI for crisp presentation quality
- **Professional Styling**: Consistent branding and color schemes
- **Optimal Sizing**: Designed for standard slide dimensions
- **Clear Labels**: Readable component names and connection labels

## 🔄 Regeneration

Diagrams are regenerated with timestamps to prevent conflicts:
- Each run creates new files with unique timestamps
- Old diagrams are preserved unless manually cleaned
- Test script provides detailed generation metrics

Run the test script whenever you need fresh examples or want to verify the diagram generation system is working correctly.