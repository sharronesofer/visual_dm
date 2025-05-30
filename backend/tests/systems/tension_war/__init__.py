"""
Test package for the tension_war system.
This package contains tests for the tension and war management system.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock


# Create MagickMock classes for FastAPI modules
class MockFastAPIRouter(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def include_router(self, router, *args, **kwargs):
        return self

    def get(self, *args, **kwargs):
        return lambda func: func

    def post(self, *args, **kwargs):
        return lambda func: func

    def put(self, *args, **kwargs):
        return lambda func: func

    def delete(self, *args, **kwargs):
        return lambda func: func


# Mock FastAPI responses
mock_fastapi_responses = MagicMock()
mock_fastapi_responses.JSONResponse = MagicMock()

# Mock FastAPI dependencies
mock_fastapi_depends = MagicMock()
mock_fastapi_depends.Depends = lambda x: x

# Set up the fastapi mock
mock_fastapi = MagicMock()
mock_fastapi.APIRouter = MockFastAPIRouter
mock_fastapi.Depends = lambda x: x
mock_fastapi.HTTPException = type("HTTPException", (Exception,), {})
mock_fastapi.responses = mock_fastapi_responses
mock_fastapi.status = MagicMock()
mock_fastapi.status.HTTP_200_OK = 200
mock_fastapi.status.HTTP_201_CREATED = 201
mock_fastapi.status.HTTP_400_BAD_REQUEST = 400
mock_fastapi.status.HTTP_401_UNAUTHORIZED = 401
mock_fastapi.status.HTTP_403_FORBIDDEN = 403
mock_fastapi.status.HTTP_404_NOT_FOUND = 404
mock_fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR = 500

# Create comprehensive mocks for all modules that might be imported
# Mock the entire app.core module and its submodules
mock_core_module = MagicMock()
sys.modules["app"] = MagicMock()
sys.modules["app.core"] = mock_core_module
sys.modules["app.core.logging"] = MagicMock()
sys.modules["app.core.logging.logger"] = MagicMock()
sys.modules["app.core.events"] = MagicMock()
sys.modules["app.core.events.event_dispatcher"] = MagicMock()
sys.modules["app.core.auth"] = MagicMock()
sys.modules["app.core.auth.get_current_user"] = MagicMock()
sys.modules["app.core.database"] = MagicMock()

# Mock FastAPI components
sys.modules["fastapi"] = mock_fastapi
sys.modules["fastapi.responses"] = mock_fastapi_responses
sys.modules["fastapi.Depends"] = mock_fastapi_depends

# Skip importing the router module when running tests
sys.modules["backend.systems.tension_war.router"] = MagicMock()


# Create a patch context that prevents actual imports from tension_war modules
def patch_imports():
    """
    Patch tension_war module imports to use direct imports of models, utils, and services
    without going through the package __init__ which pulls in router and other dependencies.
    """
    tension_war_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../systems/tension_war")
    )

    if tension_war_path not in sys.path:
        sys.path.insert(0, tension_war_path)


# Call the patch function to set up the environment
patch_imports()
