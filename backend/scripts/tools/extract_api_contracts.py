#!/usr/bin/env python3
"""
API Contract Extraction Script

Extracts HTTP methods, paths, request/response schemas, error codes, and version tags 
from all backend systems and generates a comprehensive api_contracts.yaml file following 
OpenAPI 3.0 specification standards.

Task 43 Implementation - Backend Development Protocol compliance
"""

import os
import re
import ast
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG to see more detail
logger = logging.getLogger(__name__)


@dataclass
class EndpointInfo:
    """Information about an API endpoint"""
    method: str
    path: str
    function_name: str
    description: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    summary: str = ""
    operation_id: str = ""
    security: List[Dict[str, List[str]]] = field(default_factory=list)


@dataclass
class SystemAPI:
    """API information for a complete system"""
    name: str
    description: str
    version: str = "1.0.0"
    endpoints: List[EndpointInfo] = field(default_factory=list)
    tags: List[Dict[str, str]] = field(default_factory=list)
    schemas: Dict[str, Any] = field(default_factory=dict)


class APIContractExtractor:
    """Extract API contracts from FastAPI router files"""
    
    def __init__(self, backend_path: str = "systems"):
        self.backend_path = Path(backend_path)
        self.systems: Dict[str, SystemAPI] = {}
        self.all_schemas: Dict[str, Any] = {}
        self.common_responses = {
            "200": {"description": "Successful Response"},
            "201": {"description": "Created"},
            "204": {"description": "No Content"},
            "400": {"description": "Bad Request"},
            "401": {"description": "Unauthorized"},
            "403": {"description": "Forbidden"},
            "404": {"description": "Not Found"},
            "422": {"description": "Validation Error"},
            "500": {"description": "Internal Server Error"}
        }
    
    def extract_all_contracts(self) -> Dict[str, SystemAPI]:
        """Extract API contracts from all backend systems"""
        logger.info(f"Scanning backend systems in: {self.backend_path}")
        
        # Get all system directories
        system_dirs = [d for d in self.backend_path.iterdir() 
                      if d.is_dir() and not d.name.startswith('_')]
        
        logger.info(f"Found {len(system_dirs)} systems to process")
        
        for system_dir in system_dirs:
            system_name = system_dir.name
            logger.info(f"Processing system: {system_name}")
            
            try:
                system_api = self.extract_system_contract(system_dir)
                if system_api.endpoints:
                    self.systems[system_name] = system_api
                    logger.info(f"  -> Found {len(system_api.endpoints)} endpoints")
                else:
                    logger.info(f"  -> No API endpoints found")
            except Exception as e:
                logger.error(f"Error processing system {system_name}: {e}")
        
        return self.systems
    
    def extract_system_contract(self, system_dir: Path) -> SystemAPI:
        """Extract API contract from a single system directory"""
        system_name = system_dir.name
        
        # Find all router files
        router_files = self.find_router_files(system_dir)
        
        # Extract endpoints from all router files
        all_endpoints = []
        for router_file in router_files:
            logger.debug(f"  Processing router: {router_file.relative_to(self.backend_path)}")
            endpoints = self.extract_router_endpoints(router_file, system_name)
            all_endpoints.extend(endpoints)
        
        # Remove duplicates
        unique_endpoints = self.deduplicate_endpoints(all_endpoints)
        if len(all_endpoints) != len(unique_endpoints):
            logger.debug(f"  Removed {len(all_endpoints) - len(unique_endpoints)} duplicate endpoints")
        
        # Create system API object
        system_api = SystemAPI(
            name=system_name,
            description=f"API endpoints for the {system_name} system",
            tags=[{"name": system_name, "description": f"{system_name.title()} system endpoints"}]
        )
        
        system_api.endpoints = unique_endpoints
        
        return system_api
    
    def find_router_files(self, system_dir: Path) -> List[Path]:
        """Find all router files in a system directory"""
        router_files = []
        patterns = ['**/*router*.py', '**/*api*.py']
        
        found_files = set()  # Use set to prevent duplicates
        
        for pattern in patterns:
            for file_path in system_dir.glob(pattern):
                if file_path.is_file() and file_path not in found_files:
                    found_files.add(file_path)
        
        logger.debug(f"  Found {len(found_files)} potential router files")
        
        # Confirm these are actual router files by content
        confirmed_files = set()  # Use set to prevent duplicates
        for file_path in found_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file contains FastAPI router patterns
                if self.is_router_file(content):
                    relative_path = file_path.relative_to(self.backend_path)
                    logger.debug(f"  Confirmed router file: {relative_path}")
                    confirmed_files.add(file_path)
                else:
                    relative_path = file_path.relative_to(self.backend_path)
                    logger.debug(f"  Skipped non-router file: {relative_path}")
                    
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
        
        router_files = list(confirmed_files)  # Convert set back to list
        logger.debug(f"  Processing {len(router_files)} confirmed router files")
        
        return router_files
    
    def extract_router_endpoints(self, router_file: Path, system_name: str) -> List[EndpointInfo]:
        """Extract endpoints from a single router file"""
        endpoints = []
        
        try:
            with open(router_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the Python file
            tree = ast.parse(content)
            
            # Extract router prefix and tags
            router_prefix, router_tags = self.extract_router_info(content)
            logger.debug(f"    Router prefix: '{router_prefix}', tags: {router_tags}")
            
            # Find all functions (both sync and async)
            functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
            logger.debug(f"    Found {len(functions)} functions")
            
            # Find all route decorators
            for func_node in functions:
                logger.debug(f"    Processing function: {func_node.name}")
                logger.debug(f"      Function has {len(func_node.decorator_list)} decorators")
                
                for i, decorator in enumerate(func_node.decorator_list):
                    logger.debug(f"        Decorator {i}: {ast.dump(decorator)}")
                
                endpoint = self.extract_endpoint_from_function(
                    func_node, content, router_prefix, router_tags, system_name
                )
                if endpoint:
                    endpoints.append(endpoint)
        
        except Exception as e:
            logger.error(f"Error parsing router file {router_file}: {e}")
        
        return endpoints
    
    def extract_router_info(self, content: str) -> Tuple[str, List[str]]:
        """Extract router prefix and tags from router definition"""
        prefix = ""
        tags = []
        
        # Look for APIRouter definition
        router_pattern = r'router\s*=\s*APIRouter\s*\((.*?)\)'
        match = re.search(router_pattern, content, re.DOTALL)
        
        if match:
            router_args = match.group(1)
            
            # Extract prefix
            prefix_match = re.search(r'prefix\s*=\s*["\']([^"\']+)["\']', router_args)
            if prefix_match:
                prefix = prefix_match.group(1)
            
            # Extract tags
            tags_match = re.search(r'tags\s*=\s*\[(.*?)\]', router_args)
            if tags_match:
                tags_str = tags_match.group(1)
                tags = [tag.strip(' "\',') for tag in tags_str.split(',') if tag.strip()]
        
        return prefix, tags
    
    def extract_endpoint_from_function(
        self, 
        func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef], 
        content: str, 
        router_prefix: str,
        router_tags: List[str],
        system_name: str
    ) -> Optional[EndpointInfo]:
        """Extract endpoint information from a function with route decorator"""
        
        # Get function definition line
        func_line_start = func_node.lineno
        lines = content.split('\n')
        
        # Look for router decorator in the decorators of the function
        route_decorator = None
        method = None
        path = None
        
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call):
                # Check if this is a router.method(...) call
                if (isinstance(decorator.func, ast.Attribute) and 
                    isinstance(decorator.func.value, ast.Name) and 
                    decorator.func.value.id == 'router'):
                    
                    # Extract method from the attribute
                    method = decorator.func.attr
                    
                    # Extract path from the first argument
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        path = decorator.args[0].value
                    
                    logger.debug(f"    Found router decorator: @router.{method}('{path}')")
                    break
        
        if not method or not path:
            logger.debug(f"    No valid router decorator found for function {func_node.name}")
            return None
        
        # Combine router prefix with endpoint path
        full_path = router_prefix + path if router_prefix else path
        
        # Extract function details
        description = self.extract_docstring(func_node)
        parameters = self.extract_parameters(func_node, content)
        responses = self.extract_responses_from_decorator(decorator, func_node)
        
        endpoint = EndpointInfo(
            method=method.upper(),
            path=full_path,
            function_name=func_node.name,
            description=description,
            parameters=parameters,
            responses=responses,
            tags=router_tags or [system_name],
            summary=description.split('.')[0] if description else func_node.name.replace('_', ' ').title(),
            operation_id=f"{system_name}_{func_node.name}"
        )
        
        logger.debug(f"    Created endpoint: {method.upper()} {full_path}")
        return endpoint
    
    def parse_route_decorator(self, decorator: str) -> Tuple[str, str]:
        """Parse @router.method(path, ...) decorator"""
        # Clean up the decorator text
        decorator = decorator.replace('\n', ' ').replace('\r', '')
        
        # Pattern to match @router.method("path") or @router.method("/path")
        # Handle both quoted strings and various parameter formats
        pattern = r'@router\.(\w+)\s*\(\s*["\']([^"\']+)["\']'
        match = re.search(pattern, decorator)
        
        if match:
            method = match.group(1)
            path = match.group(2)
            logger.debug(f"      Parsed: method={method}, path={path}")
            return method, path
        
        # Alternative pattern for edge cases
        alt_pattern = r'@router\.(\w+)\s*\(\s*([^,\)]+)'
        alt_match = re.search(alt_pattern, decorator)
        if alt_match:
            method = alt_match.group(1)
            path_raw = alt_match.group(2).strip()
            # Clean up path if it's quoted
            if path_raw.startswith('"') and path_raw.endswith('"'):
                path = path_raw[1:-1]
            elif path_raw.startswith("'") and path_raw.endswith("'"):
                path = path_raw[1:-1]
            else:
                path = path_raw
            logger.debug(f"      Parsed (alt): method={method}, path={path}")
            return method, path
        
        logger.debug(f"      Failed to parse decorator: {decorator}")
        return "", ""
    
    def extract_docstring(self, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> str:
        """Extract docstring from function"""
        if (func_node.body and 
            isinstance(func_node.body[0], ast.Expr) and 
            isinstance(func_node.body[0].value, ast.Constant) and 
            isinstance(func_node.body[0].value.value, str)):
            return func_node.body[0].value.value.strip()
        return ""
    
    def extract_parameters(self, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef], content: str) -> List[Dict[str, Any]]:
        """Extract parameters from function signature"""
        parameters = []
        
        for arg in func_node.args.args:
            if arg.arg in ['self', 'request', 'response']:
                continue
            
            param_info = {
                "name": arg.arg,
                "in": "query",  # Default, might be path or body
                "required": True,  # Default
                "schema": {"type": "string"}  # Default
            }
            
            # Try to infer parameter details from annotation
            if arg.annotation:
                param_info["schema"] = self.infer_schema_from_annotation(arg.annotation)
            
            # Check if parameter is in path
            func_line = func_node.lineno
            lines = content.split('\n')
            if func_line <= len(lines):
                for i in range(max(0, func_line - 5), min(len(lines), func_line + 5)):
                    if f"{{{arg.arg}}}" in lines[i]:
                        param_info["in"] = "path"
                        break
            
            parameters.append(param_info)
        
        return parameters
    
    def extract_responses_from_decorator(self, decorator: ast.Call, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> Dict[str, Dict[str, Any]]:
        """Extract response information from decorator AST node"""
        responses = {}
        
        # Default successful response
        status_code = "200"
        
        # Check for status_code in decorator keywords
        for keyword in decorator.keywords:
            if keyword.arg == "status_code":
                if isinstance(keyword.value, ast.Attribute):
                    # Handle status.HTTP_201_CREATED format
                    if keyword.value.attr.startswith("HTTP_"):
                        status_code = keyword.value.attr.replace("HTTP_", "").replace("_", "")[:3]
                elif isinstance(keyword.value, ast.Constant):
                    status_code = str(keyword.value.value)
        
        # Check for response_model in decorator keywords
        response_model_name = None
        for keyword in decorator.keywords:
            if keyword.arg == "response_model":
                if isinstance(keyword.value, ast.Name):
                    response_model_name = keyword.value.id
                elif isinstance(keyword.value, ast.Subscript):
                    # Handle List[ResponseModel] format
                    if isinstance(keyword.value.value, ast.Name) and keyword.value.value.id == "List":
                        if isinstance(keyword.value.slice, ast.Name):
                            response_model_name = f"List[{keyword.value.slice.id}]"
                # Handle Dict[str, Any] format could be added here if needed
        
        if response_model_name:
            responses[status_code] = {
                "description": self.common_responses.get(status_code, {}).get("description", "Success"),
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{response_model_name}"}
                    }
                }
            }
        else:
            responses[status_code] = {
                "description": self.common_responses.get(status_code, {}).get("description", "Success")
            }
        
        # Add common error responses
        for error_code in ["400", "401", "404", "422", "500"]:
            if error_code not in responses:
                responses[error_code] = self.common_responses[error_code]
        
        return responses
    
    def infer_schema_from_annotation(self, annotation) -> Dict[str, Any]:
        """Infer JSON schema from Python type annotation"""
        if isinstance(annotation, ast.Name):
            type_name = annotation.id
            if type_name in ["str", "string"]:
                return {"type": "string"}
            elif type_name in ["int", "integer"]:
                return {"type": "integer"}
            elif type_name in ["float", "number"]:
                return {"type": "number"}
            elif type_name in ["bool", "boolean"]:
                return {"type": "boolean"}
            elif type_name == "dict":
                return {"type": "object"}
            elif type_name == "list":
                return {"type": "array"}
        
        return {"type": "string"}  # Default
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate complete OpenAPI 3.0 specification"""
        
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Visual DM Backend API",
                "description": "Comprehensive API for the Visual DM tabletop game management system",
                "version": "1.0.0",
                "contact": {
                    "name": "Visual DM Development Team",
                    "url": "https://github.com/user/visual-dm"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:8000",
                    "description": "Development server"
                },
                {
                    "url": "https://api.visualdm.com",
                    "description": "Production server"
                }
            ],
            "tags": [],
            "paths": {},
            "components": {
                "schemas": self.generate_common_schemas(),
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }
        
        # Collect all tags
        all_tags = set()
        
        # Process each system
        for system_name, system_api in self.systems.items():
            # Add system tags
            for tag in system_api.tags:
                if tag["name"] not in all_tags:
                    spec["tags"].append(tag)
                    all_tags.add(tag["name"])
            
            # Add endpoints
            for endpoint in system_api.endpoints:
                path_key = endpoint.path
                
                if path_key not in spec["paths"]:
                    spec["paths"][path_key] = {}
                
                # Create operation object
                operation = {
                    "tags": endpoint.tags,
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "operationId": endpoint.operation_id,
                    "parameters": endpoint.parameters,
                    "responses": endpoint.responses
                }
                
                # Add request body if needed
                if endpoint.request_body:
                    operation["requestBody"] = endpoint.request_body
                
                # Add security if needed
                if endpoint.security:
                    operation["security"] = endpoint.security
                
                spec["paths"][path_key][endpoint.method.lower()] = operation
        
        return spec
    
    def generate_common_schemas(self) -> Dict[str, Any]:
        """Generate common schema definitions"""
        return {
            "Error": {
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "description": "Error message"
                    },
                    "code": {
                        "type": "string",
                        "description": "Error code"
                    }
                },
                "required": ["detail"]
            },
            "SuccessResponse": {
                "type": "object", 
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "success"
                    },
                    "message": {
                        "type": "string",
                        "description": "Success message"
                    }
                },
                "required": ["status"]
            },
            "ValidationError": {
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "loc": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "msg": {"type": "string"},
                                "type": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    
    def is_router_file(self, content: str) -> bool:
        """Check if a file contains FastAPI router definitions"""
        return ('APIRouter' in content or '@router.' in content) and not content.strip().startswith('#')
    
    def deduplicate_endpoints(self, endpoints: List[EndpointInfo]) -> List[EndpointInfo]:
        """Remove duplicate endpoints based on method and path"""
        seen = set()
        unique_endpoints = []
        
        for endpoint in endpoints:
            key = (endpoint.method, endpoint.path)
            if key not in seen:
                seen.add(key)
                unique_endpoints.append(endpoint)
        
        return unique_endpoints


def main():
    """Main execution function"""
    logger.info("Starting API contract extraction for Task 43")
    
    # Check for debug mode with specific systems
    test_systems = None
    if len(sys.argv) > 1:
        test_systems = sys.argv[1].split(',')
        logger.info(f"Testing specific systems: {test_systems}")
    
    # Initialize extractor
    extractor = APIContractExtractor()
    
    # Extract all contracts
    if test_systems:
        # Only process specified systems for debugging
        systems = {}
        for system_name in test_systems:
            system_dir = extractor.backend_path / system_name.strip()
            if system_dir.exists():
                logger.info(f"Processing test system: {system_name}")
                try:
                    system_api = extractor.extract_system_contract(system_dir)
                    if system_api.endpoints:
                        systems[system_name] = system_api
                        logger.info(f"  -> Found {len(system_api.endpoints)} endpoints")
                    else:
                        logger.info(f"  -> No API endpoints found")
                except Exception as e:
                    logger.error(f"Error processing system {system_name}: {e}")
            else:
                logger.error(f"System directory not found: {system_dir}")
        extractor.systems = systems
    else:
        systems = extractor.extract_all_contracts()
    
    logger.info(f"Extracted contracts from {len(systems)} systems")
    for name, system in systems.items():
        logger.info(f"  {name}: {len(system.endpoints)} endpoints")
    
    # Generate OpenAPI specification
    spec = extractor.generate_openapi_spec()
    
    # Write to YAML file in repository root
    output_file = Path("../api_contracts.yaml")  # This will go to the project root
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, indent=2)
    
    logger.info(f"Generated API contracts YAML: {output_file}")
    logger.info(f"Total paths: {len(spec['paths'])}")
    logger.info(f"Total tags: {len(spec['tags'])}")
    
    # Also generate JSON version for tooling
    json_file = Path("../api_contracts.json")  # This will go to the project root
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    
    logger.info(f"Generated API contracts JSON: {json_file}")
    
    # Generate summary report
    generate_summary_report(systems, spec)
    
    logger.info("API contract extraction completed successfully")


def generate_summary_report(systems: Dict[str, SystemAPI], spec: Dict[str, Any]):
    """Generate a summary report of extracted API contracts"""
    
    report = f"""# API Contract Extraction Summary - Task 43

Generated: {datetime.now().isoformat()}

## Overview
- **Total Systems**: {len(systems)}
- **Total Endpoints**: {sum(len(s.endpoints) for s in systems.values())}
- **Total Paths**: {len(spec['paths'])}
- **OpenAPI Version**: {spec['openapi']}

## Systems Overview

"""
    
    for name, system in sorted(systems.items()):
        report += f"### {name.title()} System\n"
        report += f"- **Endpoints**: {len(system.endpoints)}\n"
        report += f"- **Description**: {system.description}\n"
        
        if system.endpoints:
            report += "- **Endpoints**:\n"
            for endpoint in system.endpoints:
                report += f"  - `{endpoint.method} {endpoint.path}` - {endpoint.summary}\n"
        
        report += "\n"
    
    # Write summary report to project root
    summary_file = Path("../api_contracts_summary.md")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"Generated summary report: {summary_file}")


if __name__ == "__main__":
    from datetime import datetime
    main() 