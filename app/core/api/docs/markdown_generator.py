"""Markdown documentation generator."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

class MarkdownGenerator:
    """Generates Markdown documentation from OpenAPI schema."""
    
    def __init__(self, app: FastAPI, output_dir: str = "docs/api"):
        """Initialize Markdown generator.
        
        Args:
            app: FastAPI application
            output_dir: Output directory for documentation
        """
        self.app = app
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_docs(self) -> None:
        """Generate Markdown documentation."""
        # Get OpenAPI schema
        schema = get_openapi(
            title=self.app.title,
            version=self.app.version,
            openapi_version=self.app.openapi_version,
            description=self.app.description,
            routes=self.app.routes
        )
        
        # Generate main README
        self._generate_main_readme(schema)
        
        # Generate endpoint documentation
        self._generate_endpoint_docs(schema)
        
        # Generate model documentation
        self._generate_model_docs(schema)
        
    def _generate_main_readme(self, schema: Dict[str, Any]) -> None:
        """Generate main README file.
        
        Args:
            schema: OpenAPI schema
        """
        content = f"""# {schema['info']['title']}

{schema['info']['description']}

## API Versions

The API is versioned to ensure backward compatibility. Currently supported versions:

- v1: Stable release with core functionality
- v2: Beta release with enhanced features (see migration guide)

## Authentication

All endpoints require authentication using OAuth2 with JWT tokens. See the Authentication section for details.

## Rate Limiting

The API implements rate limiting to ensure fair usage. See the Rate Limiting section for details.

## Response Format

All API responses follow a standard envelope format:

```json
{{
    "data": {{
        // Response data here
    }},
    "metadata": {{
        "status": "success",
        "message": null,
        "timestamp": "2024-03-21T10:30:00Z",
        "version": "v2"
    }}
}}
```

## Error Handling

The API uses standard HTTP status codes and provides detailed error messages:

```json
{{
    "error": {{
        "code": "validation_error",
        "message": "Invalid input",
        "details": [
            {{
                "field": "name",
                "error": "Field is required"
            }}
        ]
    }},
    "metadata": {{
        "status": "error",
        "timestamp": "2024-03-21T10:30:00Z",
        "version": "v2"
    }}
}}
```

## Documentation Structure

- [Authentication](auth.md)
- [Rate Limiting](rate-limiting.md)
- [Endpoints](endpoints/README.md)
- [Models](models/README.md)
- [Migration Guides](migrations/README.md)
"""
        
        (self.output_dir / "README.md").write_text(content)
        
    def _generate_endpoint_docs(self, schema: Dict[str, Any]) -> None:
        """Generate endpoint documentation.
        
        Args:
            schema: OpenAPI schema
        """
        endpoints_dir = self.output_dir / "endpoints"
        endpoints_dir.mkdir(exist_ok=True)
        
        # Group endpoints by tag
        endpoints_by_tag = {}
        for path, methods in schema["paths"].items():
            for method, operation in methods.items():
                if "tags" not in operation:
                    continue
                    
                for tag in operation["tags"]:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append({
                        "path": path,
                        "method": method.upper(),
                        "operation": operation
                    })
                    
        # Generate documentation for each tag
        for tag, endpoints in endpoints_by_tag.items():
            content = f"# {tag}\n\n"
            
            for endpoint in endpoints:
                operation = endpoint["operation"]
                content += f"## {operation['summary']}\n\n"
                content += f"`{endpoint['method']} {endpoint['path']}`\n\n"
                
                if "description" in operation:
                    content += f"{operation['description']}\n\n"
                    
                # Parameters
                if "parameters" in operation:
                    content += "### Parameters\n\n"
                    content += "| Name | In | Type | Required | Description |\n"
                    content += "|------|----|----|----------|-------------|\n"
                    
                    for param in operation["parameters"]:
                        content += f"| {param['name']} | {param['in']} | {param['schema']['type']} | {param['required']} | {param.get('description', '')} |\n"
                    content += "\n"
                    
                # Request body
                if "requestBody" in operation:
                    content += "### Request Body\n\n"
                    content += "```json\n"
                    content += json.dumps(
                        operation["requestBody"]["content"]["application/json"]["schema"],
                        indent=2
                    )
                    content += "\n```\n\n"
                    
                # Responses
                content += "### Responses\n\n"
                for status, response in operation["responses"].items():
                    content += f"#### {status}\n\n"
                    if "description" in response:
                        content += f"{response['description']}\n\n"
                    if "content" in response:
                        content += "```json\n"
                        content += json.dumps(
                            response["content"]["application/json"]["schema"],
                            indent=2
                        )
                        content += "\n```\n\n"
                        
                content += "---\n\n"
                
            (endpoints_dir / f"{tag.lower()}.md").write_text(content)
            
    def _generate_model_docs(self, schema: Dict[str, Any]) -> None:
        """Generate model documentation.
        
        Args:
            schema: OpenAPI schema
        """
        models_dir = self.output_dir / "models"
        models_dir.mkdir(exist_ok=True)
        
        content = "# Data Models\n\n"
        
        for name, model in schema["components"]["schemas"].items():
            content += f"## {name}\n\n"
            
            if "description" in model:
                content += f"{model['description']}\n\n"
                
            content += "### Properties\n\n"
            content += "| Name | Type | Required | Description |\n"
            content += "|------|------|----------|-------------|\n"
            
            for prop_name, prop in model["properties"].items():
                required = prop_name in model.get("required", [])
                content += f"| {prop_name} | {prop['type']} | {required} | {prop.get('description', '')} |\n"
                
            content += "\n---\n\n"
            
        (models_dir / "README.md").write_text(content) 