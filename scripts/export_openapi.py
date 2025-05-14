"""
Script to export OpenAPI documentation to a JSON file.
"""

import json
import sys
from pathlib import Path
from flask import Flask
from app.app import create_app
from app.core.swagger import init_swagger

def export_openapi(output_file: str = 'openapi.json') -> None:
    """
    Export OpenAPI documentation to a JSON file.
    
    Args:
        output_file: Path to the output JSON file
    """
    # Create Flask app instance
    app = create_app()
    
    # Initialize Swagger
    init_swagger(app)
    
    # Get OpenAPI spec
    with app.test_request_context():
        spec = app.extensions['flasgger'].spec.to_dict()
    
    # Write to file
    output_path = Path(output_file)
    with output_path.open('w') as f:
        json.dump(spec, f, indent=2)
    
    print(f"OpenAPI documentation exported to {output_path.absolute()}")

if __name__ == '__main__':
    # Get output file from command line args or use default
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'openapi.json'
    export_openapi(output_file) 