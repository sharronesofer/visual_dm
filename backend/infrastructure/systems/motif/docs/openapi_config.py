"""
OpenAPI documentation configuration for motif system.

Provides enhanced documentation, examples, and comprehensive API specs.
"""

from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from backend.infrastructure.systems.motif.models import (
    MotifCreate, MotifUpdate, Motif, MotifResponse,
    MotifCategory, MotifScope, MotifLifecycle
)


def create_custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Create custom OpenAPI schema with enhanced documentation."""
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Motif System API",
        version="1.0.0",
        description="""
# Motif System API

A comprehensive narrative framework API for managing thematic elements in AI-driven storytelling and role-playing games.

## Overview

The Motif System provides structured management of narrative themes, emotional contexts, and storytelling elements that guide AI systems in creating coherent and engaging story experiences.

## Key Features

- **Narrative Context Management**: Generate contextual information for AI storytelling
- **Lifecycle Management**: Automatic progression and evolution of narrative themes
- **Spatial Integration**: Position-based and regional motif management
- **Conflict Resolution**: Detection and management of opposing narrative tensions
- **Performance Optimization**: Comprehensive caching and monitoring
- **Analytics**: Real-time statistics and system health monitoring

## Authentication

Most endpoints require authentication. Include your API key in the Authorization header:

```
Authorization: Bearer your-api-key-here
```

## Rate Limiting

API calls are rate-limited to ensure system stability:
- **Standard endpoints**: 100 requests per minute
- **AI-powered endpoints**: 10 requests per minute
- **Statistics endpoints**: 200 requests per minute

## Error Handling

All endpoints return structured error responses:

```json
{
    "success": false,
    "error": "Error description",
    "error_code": "VALIDATION_ERROR",
    "details": {
        "field": "specific error details"
    }
}
```

## Data Models

### Motif Categories

The system supports 49 narrative categories organized into themes:

**Dark Themes**: BETRAYAL, CHAOS, DEATH, DESTRUCTION, DESPAIR, DOOM, EVIL, EXILE, FALL, FEAR, GUILT, HATE, HUBRIS, ISOLATION, LOSS, MADNESS, NEMESIS, PRIDE, REVENGE, SACRIFICE, TEMPTATION, TRAGEDY, TREACHERY, VENGEANCE, WRATH

**Light Themes**: HOPE, LOVE, REDEMPTION, COURAGE, WISDOM, HONOR, JUSTICE, MERCY, PEACE, TRIUMPH, UNITY, VICTORY, HEALING, GROWTH, DISCOVERY, FRIENDSHIP, LOYALTY, COMPASSION, FORGIVENESS, RENEWAL, INSPIRATION, WONDER, ADVENTURE, MYSTERY

### Motif Scopes

- **GLOBAL**: Affects entire game world
- **REGIONAL**: Limited to specific geographic areas  
- **LOCAL**: Confined to small areas or settlements
- **PLAYER_CHARACTER**: Personal to individual characters
- **NON_PLAYER_CHARACTER**: Affects NPCs specifically

### Lifecycle Stages

- **DORMANT**: Inactive, waiting for triggers
- **EMERGING**: Beginning to manifest
- **ACTIVE**: Fully manifested and influential
- **INTENSIFYING**: Growing in power and effect
- **PEAK**: Maximum influence achieved
- **DECLINING**: Losing strength
- **RESOLVED**: Concluded naturally
- **INTERRUPTED**: Stopped by external forces

## Usage Examples

### Basic Workflow

1. **Create a motif** for your narrative context
2. **Get narrative context** for AI systems to use
3. **Monitor conflicts** to manage dramatic tension
4. **Update lifecycle** as story progresses
5. **Analyze statistics** for system optimization

### Common Use Cases

- **Story Generation**: Use context endpoints to provide AI with narrative guidance
- **Dynamic Events**: Create motifs for temporary story elements
- **Character Development**: Use character-scoped motifs for personal arcs
- **World Building**: Employ regional motifs for location-specific atmosphere
- **Conflict Management**: Monitor and resolve narrative tensions

## Performance Notes

- Use caching-enabled endpoints for frequently accessed data
- Leverage filtering and pagination for large datasets
- Monitor system health via health check endpoints
- Consider batch operations for multiple motif updates
        """,
        routes=app.routes,
    )
    
    # Enhanced security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token for API authentication"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for service authentication"
        }
    }
    
    # Add global security
    openapi_schema["security"] = [
        {"BearerAuth": []},
        {"ApiKeyAuth": []}
    ]
    
    # Enhanced server information
    openapi_schema["servers"] = [
        {
            "url": "https://api.motif.example.com",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.motif.example.com",
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
    
    # Add tags for better organization
    openapi_schema["tags"] = [
        {
            "name": "Core Operations",
            "description": "Basic CRUD operations for motifs"
        },
        {
            "name": "Lifecycle Management", 
            "description": "Motif state transitions and progression"
        },
        {
            "name": "Spatial Queries",
            "description": "Position-based and regional motif operations"
        },
        {
            "name": "Narrative Context",
            "description": "AI-ready context generation for storytelling"
        },
        {
            "name": "Conflict Resolution",
            "description": "Detection and management of narrative tensions"
        },
        {
            "name": "Analytics & Monitoring",
            "description": "System statistics and health monitoring"
        },
        {
            "name": "System Management",
            "description": "Administrative and maintenance operations"
        }
    ]
    
    # Add detailed examples to schemas
    add_examples_to_schemas(openapi_schema)
    
    # Add response examples
    add_response_examples(openapi_schema)
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def add_examples_to_schemas(openapi_schema: Dict[str, Any]) -> None:
    """Add detailed examples to schema components."""
    
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    if "schemas" not in openapi_schema["components"]:
        return
    
    schemas = openapi_schema["components"]["schemas"]
    
    # MotifCreate examples
    if "MotifCreate" in schemas:
        schemas["MotifCreate"]["examples"] = [
            {
                "summary": "Hope Rising",
                "description": "A global motif representing emerging hope",
                "value": {
                    "name": "Dawn of Hope",
                    "description": "A sense of renewal and possibility emerges across the land",
                    "category": "HOPE",
                    "scope": "GLOBAL",
                    "intensity": 6,
                    "theme": "renewal and new beginnings",
                    "descriptors": ["inspiring", "uplifting", "peaceful"],
                    "metadata": {
                        "source": "player_action",
                        "campaign_event": "defeat_of_tyrant"
                    }
                }
            },
            {
                "summary": "Personal Betrayal",
                "description": "Character-specific betrayal motif",
                "value": {
                    "name": "Trusted Friend's Deception",
                    "description": "A close ally reveals their true, malevolent nature",
                    "category": "BETRAYAL",
                    "scope": "PLAYER_CHARACTER",
                    "intensity": 8,
                    "theme": "broken trust and personal pain",
                    "player_id": "char_123",
                    "descriptors": ["painful", "shocking", "personal"],
                    "metadata": {
                        "betrayer": "npc_456",
                        "relationship": "mentor"
                    }
                }
            },
            {
                "summary": "Regional Mystery",
                "description": "Area-specific mysterious happenings",
                "value": {
                    "name": "The Whispering Woods",
                    "description": "Strange voices echo through the ancient forest",
                    "category": "MYSTERY",
                    "scope": "REGIONAL",
                    "intensity": 5,
                    "theme": "ancient secrets and hidden knowledge",
                    "region_id": "forest_region_1",
                    "position": {"x": 100.5, "y": 200.0},
                    "descriptors": ["eerie", "ancient", "mystical"],
                    "metadata": {
                        "discovery_method": "investigation",
                        "clues_found": 3
                    }
                }
            }
        ]
    
    # MotifUpdate examples
    if "MotifUpdate" in schemas:
        schemas["MotifUpdate"]["examples"] = [
            {
                "summary": "Increase Intensity",
                "description": "Escalate an existing motif",
                "value": {
                    "intensity": 8,
                    "metadata": {
                        "escalation_reason": "player_actions",
                        "updated_by": "game_master"
                    }
                }
            },
            {
                "summary": "Change Lifecycle",
                "description": "Advance motif to next stage",
                "value": {
                    "lifecycle": "INTENSIFYING",
                    "intensity": 7,
                    "metadata": {
                        "trigger": "time_passage",
                        "duration_days": 5
                    }
                }
            }
        ]
    
    # MotifFilter examples
    if "MotifFilter" in schemas:
        schemas["MotifFilter"]["examples"] = [
            {
                "summary": "Active Hope Motifs",
                "description": "Find all active hope-themed motifs",
                "value": {
                    "categories": ["HOPE", "TRIUMPH", "VICTORY"],
                    "lifecycle": ["ACTIVE", "INTENSIFYING"],
                    "active_only": True,
                    "min_intensity": 5
                }
            },
            {
                "summary": "Regional Dark Themes",
                "description": "Dark motifs in specific region",
                "value": {
                    "scope": "REGIONAL",
                    "region_id": "dark_forest_1",
                    "categories": ["FEAR", "DEATH", "EVIL"],
                    "max_intensity": 8
                }
            }
        ]


def add_response_examples(openapi_schema: Dict[str, Any]) -> None:
    """Add response examples to API endpoints."""
    
    if "paths" not in openapi_schema:
        return
    
    for path, methods in openapi_schema["paths"].items():
        for method, operation in methods.items():
            if "responses" not in operation:
                continue
            
            # Add examples based on endpoint type
            add_endpoint_examples(operation, path, method)


def add_endpoint_examples(operation: Dict[str, Any], path: str, method: str) -> None:
    """Add specific examples for different endpoint types."""
    
    responses = operation.get("responses", {})
    
    # Success response examples
    if "200" in responses:
        response_200 = responses["200"]
        
        if "/motifs" in path and method == "get":
            # List motifs examples
            if "content" not in response_200:
                response_200["content"] = {}
            if "application/json" not in response_200["content"]:
                response_200["content"]["application/json"] = {}
            
            response_200["content"]["application/json"]["examples"] = {
                "motif_list": {
                    "summary": "List of motifs",
                    "value": {
                        "success": True,
                        "data": [
                            {
                                "id": "motif_123",
                                "name": "Rising Darkness",
                                "category": "EVIL",
                                "scope": "GLOBAL",
                                "intensity": 7,
                                "lifecycle": "ACTIVE",
                                "created_at": "2024-01-15T10:30:00Z"
                            }
                        ],
                        "pagination": {
                            "total": 1,
                            "limit": 50,
                            "offset": 0,
                            "has_more": False
                        }
                    }
                }
            }
        
        elif "/context" in path:
            # Context examples
            if "content" not in response_200:
                response_200["content"] = {}
            if "application/json" not in response_200["content"]:
                response_200["content"]["application/json"] = {}
            
            response_200["content"]["application/json"]["examples"] = {
                "narrative_context": {
                    "summary": "Narrative context for AI",
                    "value": {
                        "success": True,
                        "data": {
                            "active_motifs": [
                                {
                                    "name": "Rising Darkness",
                                    "category": "EVIL",
                                    "intensity": 7,
                                    "influence": "high"
                                }
                            ],
                            "dominant_motif": {
                                "name": "Rising Darkness",
                                "category": "EVIL",
                                "influence_score": 8.5
                            },
                            "narrative_themes": [
                                "growing_evil",
                                "impending_doom",
                                "need_for_heroes"
                            ],
                            "context_guidance": "The world grows darker as evil forces gather strength. Heroes are needed to stand against the rising darkness.",
                            "tone_suggestions": ["serious", "ominous", "urgent"],
                            "recommended_actions": [
                                "seek_allies",
                                "gather_power",
                                "investigate_threat"
                            ]
                        }
                    }
                }
            }
        
        elif "/statistics" in path:
            # Statistics examples
            if "content" not in response_200:
                response_200["content"] = {}
            if "application/json" not in response_200["content"]:
                response_200["content"]["application/json"] = {}
            
            response_200["content"]["application/json"]["examples"] = {
                "system_stats": {
                    "summary": "System statistics",
                    "value": {
                        "success": True,
                        "data": {
                            "total_motifs": 156,
                            "active_motifs": 23,
                            "canonical_motifs": 50,
                            "system_health": "healthy",
                            "motifs_by_category": {
                                "HOPE": 12,
                                "EVIL": 8,
                                "MYSTERY": 15
                            },
                            "motifs_by_scope": {
                                "GLOBAL": 5,
                                "REGIONAL": 18,
                                "LOCAL": 89
                            },
                            "recent_activity": {
                                "motifs_created_today": 3,
                                "evolutions_processed": 7,
                                "conflicts_resolved": 2
                            }
                        }
                    }
                }
            }
    
    # Error response examples
    if "400" in responses:
        response_400 = responses["400"]
        if "content" not in response_400:
            response_400["content"] = {}
        if "application/json" not in response_400["content"]:
            response_400["content"]["application/json"] = {}
        
        response_400["content"]["application/json"]["examples"] = {
            "validation_error": {
                "summary": "Validation error",
                "value": {
                    "success": False,
                    "error": "Validation failed",
                    "error_code": "VALIDATION_ERROR",
                    "details": {
                        "intensity": "Value must be between 1 and 10",
                        "category": "Invalid category specified"
                    }
                }
            }
        }
    
    if "404" in responses:
        response_404 = responses["404"]
        if "content" not in response_404:
            response_404["content"] = {}
        if "application/json" not in response_404["content"]:
            response_404["content"]["application/json"] = {}
        
        response_404["content"]["application/json"]["examples"] = {
            "not_found": {
                "summary": "Resource not found",
                "value": {
                    "success": False,
                    "error": "Motif not found",
                    "error_code": "NOT_FOUND",
                    "details": {
                        "motif_id": "motif_123",
                        "message": "No motif exists with the specified ID"
                    }
                }
            }
        }
    
    if "500" in responses:
        response_500 = responses["500"]
        if "content" not in response_500:
            response_500["content"] = {}
        if "application/json" not in response_500["content"]:
            response_500["content"]["application/json"] = {}
        
        response_500["content"]["application/json"]["examples"] = {
            "server_error": {
                "summary": "Internal server error",
                "value": {
                    "success": False,
                    "error": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                    "details": {
                        "message": "An unexpected error occurred",
                        "request_id": "req_abc123"
                    }
                }
            }
        }


def get_api_documentation_config() -> Dict[str, Any]:
    """Get API documentation configuration."""
    return {
        "title": "Motif System API",
        "description": "Comprehensive narrative framework for AI-driven storytelling",
        "version": "1.0.0",
        "contact": {
            "name": "Motif System Support",
            "email": "support@motif.example.com",
            "url": "https://docs.motif.example.com"
        },
        "license": {
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT"
        },
        "terms_of_service": "https://motif.example.com/terms",
        "external_docs": {
            "description": "Full Documentation",
            "url": "https://docs.motif.example.com"
        }
    } 