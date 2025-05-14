"""
World system API endpoints.
"""

from flask_restx import Resource, fields
from pydantic import BaseModel, Field
from typing import List, Optional

from app.core.api.base_blueprint import BaseBlueprint
from app.core.utils.api_response import APIResponse, ErrorResponse
from app.core.auth.auth_middleware import (
    login_required,
    roles_required,
    permission_required
)
from app.core.middleware.rate_limiter import rate_limit
from app.core.middleware.cache import cache

class RegionCreate(BaseModel):
    """Region creation request schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    climate: str = Field(..., min_length=1, max_length=50)
    terrain_type: str = Field(..., min_length=1, max_length=50)
    population: int = Field(..., ge=0)
    danger_level: int = Field(..., ge=1, le=10)

class WorldBlueprint(BaseBlueprint):
    """World system endpoints blueprint."""

    def __init__(self):
        super().__init__("world", __name__, url_prefix="/api/v1/world")
        
        # Initialize Flask-RESTX API
        self.api = Api(
            self,
            title="World API",
            description="Endpoints for managing world regions and locations",
            doc="/docs"
        )

        # Define request/response models
        self.region_model = self.api.model("Region", {
            "id": fields.String(description="Region ID"),
            "name": fields.String(required=True, description="Region name"),
            "description": fields.String(description="Region description"),
            "climate": fields.String(required=True, description="Region climate"),
            "terrain_type": fields.String(required=True, description="Region terrain type"),
            "population": fields.Integer(required=True, description="Region population"),
            "danger_level": fields.Integer(required=True, description="Region danger level (1-10)")
        })

        self.region_list_response = self.api.model("RegionList", {
            "regions": fields.List(fields.Nested(self.region_model)),
            "total": fields.Integer(description="Total number of regions"),
            "page": fields.Integer(description="Current page number"),
            "per_page": fields.Integer(description="Items per page")
        })

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register blueprint routes."""

        @self.api.route("/regions")
        class RegionsResource(Resource):
            @rate_limit(limit=100, period=60)  # 100 requests per minute
            @cache(timeout=300)  # Cache for 5 minutes
            @login_required
            @self.api.doc(security="Bearer")
            @self.api.response(200, "Success", self.region_list_response)
            @self.api.response(401, "Authentication required")
            @self.api.response(429, "Too many requests")
            def get(self):
                """List all regions."""
                try:
                    # Get pagination parameters
                    page = request.args.get("page", 1, type=int)
                    per_page = request.args.get("per_page", 20, type=int)
                    
                    # Get filter parameters
                    climate = request.args.get("climate")
                    terrain_type = request.args.get("terrain_type")
                    min_danger = request.args.get("min_danger", type=int)
                    max_danger = request.args.get("max_danger", type=int)
                    
                    # Build filter query
                    filters = {}
                    if climate:
                        filters["climate"] = climate
                    if terrain_type:
                        filters["terrain_type"] = terrain_type
                    if min_danger is not None:
                        filters["danger_level__gte"] = min_danger
                    if max_danger is not None:
                        filters["danger_level__lte"] = max_danger
                    
                    # Get regions from database
                    regions, total = Region.get_paginated(
                        page=page,
                        per_page=per_page,
                        filters=filters
                    )
                    
                    return APIResponse(
                        data={
                            "regions": [region.to_dict() for region in regions],
                            "total": total,
                            "page": page,
                            "per_page": per_page
                        }
                    ).to_dict(), 200
                    
                except Exception as e:
                    current_app.logger.error(f"Failed to list regions: {str(e)}")
                    return ErrorResponse(
                        "Failed to list regions",
                        status_code=500
                    ).to_dict(), 500

            @rate_limit(limit=20, period=60)  # 20 creations per minute
            @roles_required("world_admin", "game_master")
            @self.api.doc(security="Bearer")
            @self.api.expect(self.region_model)
            @self.api.response(201, "Region created", self.region_model)
            @self.api.response(400, "Invalid request")
            @self.api.response(401, "Authentication required")
            @self.api.response(403, "Insufficient permissions")
            @self.api.response(429, "Too many requests")
            def post(self):
                """Create a new region."""
                try:
                    # Validate request data
                    data = RegionCreate(**request.json)
                    
                    # Create region in database
                    region = Region.create(**data.dict())
                    
                    return APIResponse(
                        data=region.to_dict(),
                        message="Region created successfully"
                    ).to_dict(), 201
                    
                except ValidationError as e:
                    return ErrorResponse(
                        "Invalid request data",
                        errors=e.errors(),
                        status_code=400
                    ).to_dict(), 400
                except Exception as e:
                    current_app.logger.error(f"Failed to create region: {str(e)}")
                    return ErrorResponse(
                        "Failed to create region",
                        status_code=500
                    ).to_dict(), 500

        @self.api.route("/regions/<string:region_id>")
        class RegionResource(Resource):
            @rate_limit(limit=100, period=60)
            @cache(timeout=300)
            @login_required
            @self.api.doc(security="Bearer")
            @self.api.response(200, "Success", self.region_model)
            @self.api.response(401, "Authentication required")
            @self.api.response(404, "Region not found")
            @self.api.response(429, "Too many requests")
            def get(self, region_id: str):
                """Get a specific region."""
                try:
                    region = Region.get_by_id(region_id)
                    if not region:
                        return ErrorResponse(
                            "Region not found",
                            status_code=404
                        ).to_dict(), 404
                        
                    return APIResponse(
                        data=region.to_dict()
                    ).to_dict(), 200
                    
                except Exception as e:
                    current_app.logger.error(f"Failed to get region: {str(e)}")
                    return ErrorResponse(
                        "Failed to get region",
                        status_code=500
                    ).to_dict(), 500

            @rate_limit(limit=20, period=60)
            @roles_required("world_admin", "game_master")
            @self.api.doc(security="Bearer")
            @self.api.expect(self.region_model)
            @self.api.response(200, "Region updated", self.region_model)
            @self.api.response(400, "Invalid request")
            @self.api.response(401, "Authentication required")
            @self.api.response(403, "Insufficient permissions")
            @self.api.response(404, "Region not found")
            @self.api.response(429, "Too many requests")
            def put(self, region_id: str):
                """Update a region."""
                try:
                    # Validate request data
                    data = RegionCreate(**request.json)
                    
                    # Get and update region
                    region = Region.get_by_id(region_id)
                    if not region:
                        return ErrorResponse(
                            "Region not found",
                            status_code=404
                        ).to_dict(), 404
                        
                    region.update(**data.dict())
                    
                    return APIResponse(
                        data=region.to_dict(),
                        message="Region updated successfully"
                    ).to_dict(), 200
                    
                except ValidationError as e:
                    return ErrorResponse(
                        "Invalid request data",
                        errors=e.errors(),
                        status_code=400
                    ).to_dict(), 400
                except Exception as e:
                    current_app.logger.error(f"Failed to update region: {str(e)}")
                    return ErrorResponse(
                        "Failed to update region",
                        status_code=500
                    ).to_dict(), 500

            @rate_limit(limit=10, period=60)
            @roles_required("world_admin")
            @self.api.doc(security="Bearer")
            @self.api.response(200, "Region deleted")
            @self.api.response(401, "Authentication required")
            @self.api.response(403, "Insufficient permissions")
            @self.api.response(404, "Region not found")
            @self.api.response(429, "Too many requests")
            def delete(self, region_id: str):
                """Delete a region."""
                try:
                    # Get and delete region
                    region = Region.get_by_id(region_id)
                    if not region:
                        return ErrorResponse(
                            "Region not found",
                            status_code=404
                        ).to_dict(), 404
                        
                    region.delete()
                    
                    return APIResponse(
                        message="Region deleted successfully"
                    ).to_dict(), 200
                    
                except Exception as e:
                    current_app.logger.error(f"Failed to delete region: {str(e)}")
                    return ErrorResponse(
                        "Failed to delete region",
                        status_code=500
                    ).to_dict(), 500

# Create blueprint instance
world_blueprint = WorldBlueprint() 