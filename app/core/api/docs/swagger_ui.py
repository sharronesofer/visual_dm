"""Swagger UI customization."""

from typing import Dict, Any
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

def customize_swagger_ui(app: FastAPI) -> None:
    """Customize Swagger UI for the API.
    
    Args:
        app: FastAPI application
    """
    # Override default Swagger UI
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui(request: Request) -> HTMLResponse:
        """Serve customized Swagger UI.
        
        Args:
            request: FastAPI request
            
        Returns:
            HTML response with Swagger UI
        """
        root_path = request.scope.get("root_path", "").rstrip("/")
        openapi_url = root_path + app.openapi_url
        
        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=app.title + " - API Documentation",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
            swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            init_oauth={
                "clientId": "",
                "clientSecret": "",
                "realm": "game-management",
                "appName": "Game Management API",
                "scopes": ["read:games", "write:games"],
                "usePkceWithAuthorizationCodeGrant": True
            },
            swagger_ui_parameters={
                "docExpansion": "none",
                "filter": True,
                "tryItOutEnabled": True,
                "syntaxHighlight.theme": "monokai",
                "persistAuthorization": True,
                "displayRequestDuration": True,
                "defaultModelsExpandDepth": 3,
                "defaultModelExpandDepth": 3,
                "defaultModelRendering": "model",
                "displayOperationId": True,
                "showExtensions": True,
                "showCommonExtensions": True
            }
        ) 