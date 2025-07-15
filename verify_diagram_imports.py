#!/usr/bin/env python3
"""
Simple script to verify that the diagram generator imports work correctly.
Run this after fixing the import issues.
"""

def test_diagram_generator_import():
    """Test importing the diagram generator with fixed imports."""
    try:
        # Import the settings first to ensure it's available
        import sys
        sys.path.append('.')
        
        from src.config.settings import settings
        print("✅ Settings imported successfully")
        
        # Test the diagram generator import
        from src.tools.diagram_generator import DiagramGenerator
        print("✅ DiagramGenerator imported successfully")
        
        # Test initialization
        from pathlib import Path
        temp_dir = Path('./temp_test')
        styling_config = {"style": "keyrus_brand"}
        
        generator = DiagramGenerator(temp_dir, styling_config)
        print("✅ DiagramGenerator initialized successfully")
        
        # Test getting supported providers
        providers = generator.get_supported_providers()
        print(f"✅ Supported providers: {providers}")
        
        # Test getting supported components
        aws_components = generator.get_supported_components("aws")
        print(f"✅ AWS components: {aws_components[:5]}...")  # Show first 5
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def test_diagram_chain_import():
    """Test importing the diagram generation chain."""
    try:
        from src.chains.diagram_generation_chain import DiagramGenerationChain
        print("✅ DiagramGenerationChain imported successfully")
        
        # Test getting generation stats (this doesn't require external dependencies)
        chain = DiagramGenerationChain()
        stats = chain.get_generation_stats()
        print(f"✅ Generation stats retrieved: {list(stats.keys())}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Chain import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Chain other error: {e}")
        return False

def test_model_imports():
    """Test importing the data models."""
    try:
        from src.models.data_models import (
            DiagramComponent, 
            DiagramConnection, 
            DiagramSpec,
            GeneratedDiagram,
            DiagramGenerationResult
        )
        print("✅ All diagram data models imported successfully")
        
        # Test creating a simple component
        component = DiagramComponent(
            name="Test Service",
            component_type="service",
            icon_provider="aws",
            icon_name="Lambda"
        )
        print(f"✅ Created test component: {component.name}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Model import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Model other error: {e}")
        return False

if __name__ == "__main__":
    print("Verifying Diagram Module Imports")
    print("=" * 40)
    
    # Test data models first (minimal dependencies)
    model_success = test_model_imports()
    
    # Test diagram generator (requires diagrams library)
    generator_success = test_diagram_generator_import()
    
    # Test diagram chain (requires langchain)
    chain_success = test_diagram_chain_import()
    
    print("\n" + "=" * 40)
    print("Import Test Results:")
    print(f"Data Models: {'✅ PASS' if model_success else '❌ FAIL'}")
    print(f"Diagram Generator: {'✅ PASS' if generator_success else '❌ FAIL'}")
    print(f"Diagram Chain: {'✅ PASS' if chain_success else '❌ FAIL'}")
    
    if all([model_success, generator_success, chain_success]):
        print("\n🎉 All imports working correctly!")
    else:
        print("\n⚠️ Some imports still have issues - check error messages above")