"""
Swagger/OpenAPI configuration for the application.
This module sets up and configures Swagger UI and OpenAPI documentation.
"""

from flask import Flask
from flasgger import Swagger, LazyString
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec

def init_swagger(app: Flask) -> None:
    """
    Initialize Swagger UI and API documentation for the application.
    
    Args:
        app: The Flask application instance
    """
    # Basic Swagger configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
        "swagger_ui_bundle_js": '//unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js',
        "swagger_ui_standalone_preset_js": '//unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js',
        "swagger_ui_css": '//unpkg.com/swagger-ui-dist@5/swagger-ui.css',
        "swagger_ui_config": {
            "deepLinking": True,
            "displayOperationId": True,
            "defaultModelsExpandDepth": 3,
            "defaultModelExpandDepth": 3,
            "defaultModelRendering": 'model',
            "displayRequestDuration": True,
            "docExpansion": 'list',
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "tryItOutEnabled": True
        }
    }

    # Template for Swagger UI
    template = {
        "swagger": "2.0",
        "info": {
            "title": "Visual DM API",
            "description": "API documentation for Visual DM application",
            "version": "1.0.0",
            "contact": {
                "name": "Development Team",
                "url": "https://github.com/yourusername/visual_dm",
            },
            "termsOfService": "http://example.com/terms/",
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "basePath": "/api/v1",
        "schemes": [
            "http",
            "https"
        ],
        "securityDefinitions": {
            "BearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter your bearer token in the format: Bearer <token>"
            }
        },
        "security": [
            {
                "BearerAuth": []
            }
        ],
        "tags": [
            {
                "name": "Authentication",
                "description": "User authentication and token management"
            },
            {
                "name": "Users",
                "description": "User profile and management"
            },
            {
                "name": "Game",
                "description": "Game state and management"
            },
            {
                "name": "Characters",
                "description": "Character creation and management"
            },
            {
                "name": "Maps",
                "description": "Map creation and management"
            },
            {
                "name": "Code",
                "description": "Code version control and analysis"
            },
            {
                "name": "Background Tasks",
                "description": "Management of asynchronous background tasks"
            },
            {
                "name": "Scheduled Jobs",
                "description": "Configuration and control of scheduled jobs"
            },
            {
                "name": "Task Scheduler",
                "description": "Long-running task scheduling and management"
            }
        ],
        "definitions": {
            "Error": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "integer",
                        "format": "int32",
                        "description": "Error code"
                    },
                    "message": {
                        "type": "string",
                        "description": "Error message"
                    },
                    "fields": {
                        "type": "object",
                        "description": "Field-specific error details"
                    }
                }
            },
            "ValidationError": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "integer",
                        "format": "int32",
                        "description": "Error code (400)"
                    },
                    "message": {
                        "type": "string",
                        "description": "Validation error message"
                    },
                    "errors": {
                        "type": "object",
                        "description": "Field-specific validation errors"
                    }
                }
            }
        },
        "responses": {
            "UnauthorizedError": {
                "description": "Access token is missing or invalid",
                "schema": {
                    "$ref": "#/definitions/Error"
                }
            },
            "ValidationError": {
                "description": "Invalid request parameters",
                "schema": {
                    "$ref": "#/definitions/ValidationError"
                }
            }
        }
    }

    # Initialize Swagger plugin
    Swagger(app, config=swagger_config, template=template)

    # Initialize APISpec with marshmallow plugin for schema support
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='Visual DM API',
            version='v1',
            plugins=[MarshmallowPlugin()],
            openapi_version='2.0',
            info=dict(
                description='API documentation for Visual DM application',
                contact=dict(
                    name='Development Team',
                    url='https://github.com/yourusername/visual_dm'
                ),
                termsOfService='http://example.com/terms/',
                license=dict(
                    name='MIT',
                    url='https://opensource.org/licenses/MIT'
                )
            ),
            security=[{"BearerAuth": []}]
        ),
        'APISPEC_SWAGGER_URL': '/apispec.json',  # URI to access API Doc JSON
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui',  # URI to access UI of API Doc
        'APISPEC_SWAGGER_UI_BUNDLE_JS': '//unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js',
        'APISPEC_SWAGGER_UI_STANDALONE_PRESET_JS': '//unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js',
        'APISPEC_SWAGGER_UI_CSS': '//unpkg.com/swagger-ui-dist@5/swagger-ui.css'
    })

    # Initialize flask-apispec
    docs = FlaskApiSpec(app)

    # Register all views with apispec
    with app.test_request_context():
        for view in app.view_functions.values():
            if hasattr(view, '__apispec__'):
                docs.register(view) 