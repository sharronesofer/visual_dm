#!/usr/bin/env python3
"""Script to generate API documentation."""

import sys
from pathlib import Path
import logging

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.api.docs.openapi import OpenAPIGenerator
from app.core.api.version_manager import VersionManager
from app.core.api.fastapi.app import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Generate API documentation."""
    try:
        # Create FastAPI app to get version manager
        app = create_app()
        
        # Get version manager from app state
        version_manager = app.state.version_manager
        
        # Create OpenAPI generator
        generator = OpenAPIGenerator(version_manager)
        
        # Generate docs for all versions
        logger.info("Generating OpenAPI documentation...")
        generator.generate_all()
        logger.info("Documentation generated successfully!")
        
        # Print locations of generated files
        docs_path = Path("docs/api/openapi")
        for spec_file in docs_path.glob("*.json"):
            logger.info(f"Generated spec: {spec_file}")
            
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 