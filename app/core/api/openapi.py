"""
OpenAPI/Swagger configuration and documentation generation.
"""

from typing import Any, Dict, List, Optional
from flask import Flask, jsonify, url_for
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields

class OpenAPIConfig:
    """OpenAPI documentation configuration."""

    def __init__(
        self,
        app: Flask,
        title: str = "Game API",
        version: str = "1.0.0",
        openapi_version: str = "3.0.2"
    ) -> None:
        """
        Initialize OpenAPI configuration.

        Args:
            app: Flask application instance
            title: API title
            version: API version
            openapi_version: OpenAPI specification version
        """
        self.app = app
        self.title = title
        self.version = version
        self.openapi_version = openapi_version
        
        # Initialize APISpec
        self.spec = APISpec(
            title=title,
            version=version,
            openapi_version=openapi_version,
            plugins=[FlaskPlugin(), MarshmallowPlugin()],
            info={
                "description": "RESTful API for game management and interaction",
                "termsOfService": "http://example.com/terms/",
                "contact": {
                    "name": "API Support",
                    "url": "http://example.com/support",
                    "email": "support@example.com"
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT"
                }
            },
            servers=[
                {
                    "url": "http://localhost:5000",
                    "description": "Development server"
                }
            ],
            tags=[
                {"name": "world", "description": "World management operations"},
                {"name": "npc", "description": "NPC management operations"},
                {"name": "quest", "description": "Quest management operations"},
                {"name": "combat", "description": "Combat system operations"},
                {"name": "location", "description": "Location management operations"},
                {"name": "item", "description": "Item management operations"},
                {"name": "faction", "description": "Faction management operations"},
                {"name": "auth", "description": "Authentication operations"}
            ]
        )
        
        # Register common schemas
        self._register_common_schemas()
        
        # Register error responses
        self._register_error_responses()

        # Register security schemes (ApiKeyAuth)
        self._register_security_schemes()

    def _register_common_schemas(self) -> None:
        """Register common schemas used across endpoints."""
        
        class PaginationSchema(Schema):
            """Pagination information schema."""
            page = fields.Integer(required=True, description="Current page number")
            limit = fields.Integer(required=True, description="Items per page")
            total = fields.Integer(required=True, description="Total number of items")

        class MetadataSchema(Schema):
            """Response metadata schema."""
            has_more = fields.Boolean(description="Whether more items exist")
            custom_data = fields.Dict(description="Additional metadata")

        class ErrorSchema(Schema):
            """Error information schema."""
            code = fields.String(required=True, description="Error code")
            message = fields.String(required=True, description="Error message")
            details = fields.Dict(description="Additional error details")

        class APIResponseSchema(Schema):
            """Standard API response schema."""
            status = fields.Integer(required=True, description="HTTP status code")
            data = fields.Raw(description="Response data")
            error = fields.Nested(ErrorSchema, description="Error information")
            timestamp = fields.String(required=True, description="Response timestamp")
            metadata = fields.Nested(MetadataSchema, description="Response metadata")

        # Register schemas
        self.spec.components.schema("Pagination", schema=PaginationSchema)
        self.spec.components.schema("Metadata", schema=MetadataSchema)
        self.spec.components.schema("Error", schema=ErrorSchema)
        self.spec.components.schema("APIResponse", schema=APIResponseSchema)

    def _register_error_responses(self) -> None:
        """Register common error responses."""
        self.spec.components.response(
            "ValidationError",
            {
                "description": "Invalid input parameters",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/APIResponse"}
                    }
                }
            }
        )
        
        self.spec.components.response(
            "AuthenticationError",
            {
                "description": "Authentication required or failed",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/APIResponse"}
                    }
                }
            }
        )
        
        self.spec.components.response(
            "AuthorizationError",
            {
                "description": "Insufficient permissions",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/APIResponse"}
                    }
                }
            }
        )
        
        self.spec.components.response(
            "NotFoundError",
            {
                "description": "Resource not found",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/APIResponse"}
                    }
                }
            }
        )
        
        self.spec.components.response(
            "ConflictError",
            {
                "description": "Resource conflict",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/APIResponse"}
                    }
                }
            }
        )
        
        self.spec.components.response(
            "RateLimitError",
            {
                "description": "Rate limit exceeded",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/APIResponse"}
                    }
                }
            }
        )
        
        self.spec.components.response(
            "InternalError",
            {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/APIResponse"}
                    }
                }
            }
        )

    def register_blueprint(self, blueprint: Any) -> None:
        """
        Register a blueprint's routes in the API specification.

        Args:
            blueprint: Flask Blueprint instance
        """
        with self.app.test_request_context():
            for rule in self.app.url_map.iter_rules():
                if rule.endpoint.startswith(blueprint.name):
                    self.spec.path(
                        view=self.app.view_functions[rule.endpoint],
                        app=self.app,
                        operations=self._get_operations(rule)
                    )

    def _get_operations(self, rule: Any) -> Dict[str, Any]:
        """Get OpenAPI operations from route rule."""
        operations: Dict[str, Any] = {}
        
        for method in rule.methods - {"HEAD", "OPTIONS"}:
            method = method.lower()
            view_func = self.app.view_functions[rule.endpoint]
            
            if hasattr(view_func, f"__apispec__{method}_opts"):
                operations[method] = getattr(
                    view_func,
                    f"__apispec__{method}_opts"
                )
        
        return operations

    def generate_spec(self) -> Dict[str, Any]:
        """Generate complete OpenAPI specification."""
        return self.spec.to_dict()

    def register_world_blueprint(self, world_blueprint: Any) -> None:
        """
        Register the world blueprint's routes and models in the OpenAPI specification.

        Args:
            world_blueprint: The world API blueprint instance
        """
        # Register request/response schemas
        from app.core.api.world.world_blueprint import RegionCreate
        from marshmallow import Schema, fields

        class RegionSchema(Schema):
            name = fields.String(required=True, description="Region name")
            description = fields.String(description="Region description")
            climate = fields.String(required=True, description="Region climate")
            terrain_type = fields.String(required=True, description="Region terrain type")
            population = fields.Integer(required=True, description="Region population")
            danger_level = fields.Integer(required=True, description="Region danger level")

        self.spec.components.schema("Region", schema=RegionSchema)
        self.spec.components.schema("RegionCreate", schema=RegionSchema)

        # Register endpoints
        # List regions
        self.spec.path(
            path="/regions",
            operations={
                "get": {
                    "summary": "List all regions",
                    "description": "Retrieve a paginated list of all regions.",
                    "tags": ["world"],
                    "parameters": [
                        {"name": "page", "in": "query", "required": False, "schema": {"type": "integer"}},
                        {"name": "per_page", "in": "query", "required": False, "schema": {"type": "integer"}},
                        {"name": "climate", "in": "query", "required": False, "schema": {"type": "string"}},
                        {"name": "terrain_type", "in": "query", "required": False, "schema": {"type": "string"}},
                        {"name": "min_danger", "in": "query", "required": False, "schema": {"type": "integer"}},
                        {"name": "max_danger", "in": "query", "required": False, "schema": {"type": "integer"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/APIResponse"}
                                }
                            }
                        },
                        "401": {"$ref": "#/components/responses/AuthenticationError"},
                        "429": {"$ref": "#/components/responses/RateLimitError"}
                    },
                    "security": [{"BearerAuth": []}]
                },
                "post": {
                    "summary": "Create a new region",
                    "description": "Create a new region with the provided data.",
                    "tags": ["world"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RegionCreate"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Region created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/APIResponse"}
                                }
                            }
                        },
                        "400": {"$ref": "#/components/responses/ValidationError"},
                        "401": {"$ref": "#/components/responses/AuthenticationError"},
                        "403": {"$ref": "#/components/responses/AuthorizationError"},
                        "429": {"$ref": "#/components/responses/RateLimitError"}
                    },
                    "security": [{"BearerAuth": []}]
                }
            }
        )
        # Get, update, delete region
        self.spec.path(
            path="/regions/{region_id}",
            operations={
                "get": {
                    "summary": "Get a specific region",
                    "description": "Retrieve a region by its ID.",
                    "tags": ["world"],
                    "parameters": [
                        {"name": "region_id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/APIResponse"}
                                }
                            }
                        },
                        "401": {"$ref": "#/components/responses/AuthenticationError"},
                        "404": {"$ref": "#/components/responses/NotFoundError"},
                        "429": {"$ref": "#/components/responses/RateLimitError"}
                    },
                    "security": [{"BearerAuth": []}]
                },
                "put": {
                    "summary": "Update a region",
                    "description": "Update a region by its ID.",
                    "tags": ["world"],
                    "parameters": [
                        {"name": "region_id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RegionCreate"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Region updated",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/APIResponse"}
                                }
                            }
                        },
                        "400": {"$ref": "#/components/responses/ValidationError"},
                        "401": {"$ref": "#/components/responses/AuthenticationError"},
                        "403": {"$ref": "#/components/responses/AuthorizationError"},
                        "404": {"$ref": "#/components/responses/NotFoundError"},
                        "429": {"$ref": "#/components/responses/RateLimitError"}
                    },
                    "security": [{"BearerAuth": []}]
                },
                "delete": {
                    "summary": "Delete a region",
                    "description": "Delete a region by its ID.",
                    "tags": ["world"],
                    "parameters": [
                        {"name": "region_id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "Region deleted",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/APIResponse"}
                                }
                            }
                        },
                        "401": {"$ref": "#/components/responses/AuthenticationError"},
                        "403": {"$ref": "#/components/responses/AuthorizationError"},
                        "404": {"$ref": "#/components/responses/NotFoundError"},
                        "429": {"$ref": "#/components/responses/RateLimitError"}
                    },
                    "security": [{"BearerAuth": []}]
                }
            }
        )

    def _register_security_schemes(self) -> None:
        """Register security schemes."""
        self.spec.components.security_scheme(
            "ApiKeyAuth",
            {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key required in the X-API-Key header"
            }
        )

def setup_swagger_ui(app: Flask, openapi_config: OpenAPIConfig) -> None:
    """
    Set up Swagger UI routes.

    Args:
        app: Flask application instance
        openapi_config: OpenAPI configuration instance
    """
    @app.route("/api/docs/openapi.json")
    def openapi_spec() -> Any:
        """Serve OpenAPI specification."""
        return jsonify(openapi_config.generate_spec())

    @app.route("/api/docs")
    def swagger_ui() -> str:
        """Serve Swagger UI."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{openapi_config.title} - API Documentation</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
            <script>
                window.onload = function() {{
                    window.ui = SwaggerUIBundle({{
                        url: "{url_for('openapi_spec')}",
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIBundle.SwaggerUIStandalonePreset
                        ],
                        plugins: [
                            SwaggerUIBundle.plugins.DownloadUrl
                        ],
                    }});
                }}
            </script>
        </body>
        </html>
        """

def document_response(
    status_code: int,
    description: str,
    schema: Optional[Schema] = None
) -> Dict[str, Any]:
    """
    Generate OpenAPI response documentation.

    Args:
        status_code: HTTP status code
        description: Response description
        schema: Marshmallow schema for response data

    Returns:
        Response documentation
    """
    response_doc = {
        "description": description,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/APIResponse"}
            }
        }
    }
    
    if schema:
        response_doc["content"]["application/json"]["schema"] = {
            "allOf": [
                {"$ref": "#/components/schemas/APIResponse"},
                {
                    "properties": {
                        "data": {"$ref": f"#/components/schemas/{schema.__name__}"}
                    }
                }
            ]
        }
    
    return {str(status_code): response_doc}

def document_endpoint(
    summary: str,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    parameters: Optional[List[Dict[str, Any]]] = None,
    request_body: Optional[Dict[str, Any]] = None,
    responses: Optional[Dict[str, Any]] = None,
    security: Optional[List[Dict[str, List[str]]]] = None,
    deprecated: bool = False
) -> Dict[str, Any]:
    """
    Generate OpenAPI endpoint documentation.

    Args:
        summary: Short summary of the endpoint
        description: Detailed description
        tags: List of tags for categorization
        parameters: List of parameters
        request_body: Request body schema
        responses: Response schemas
        security: Security requirements
        deprecated: Whether the endpoint is deprecated

    Returns:
        Endpoint documentation
    """
    doc = {
        "summary": summary,
        "responses": responses or {},
        "deprecated": deprecated
    }
    
    if description:
        doc["description"] = description
    
    if tags:
        doc["tags"] = tags
    
    if parameters:
        doc["parameters"] = parameters
    
    if request_body:
        doc["requestBody"] = {
            "content": {
                "application/json": request_body
            },
            "required": True
        }
    
    if security:
        doc["security"] = security
    
    return doc 