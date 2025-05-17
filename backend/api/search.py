from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List
from backend.schemas.search import SearchResponse
from backend.services.search_service import SearchService
from backend.middleware.validation import validate_search_query

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.get("/worlds", response_model=SearchResponse, summary="Search Worlds", description="Search for worlds with filtering, sorting, and pagination.")
def search_worlds(
    params: dict = Depends(validate_search_query),
    search_service: SearchService = Depends()
):
    return search_service.search_entity("world", params["q"], params["filter"], params["sort"], params["page"], params["pageSize"])

@router.get("/npcs", response_model=SearchResponse, summary="Search NPCs", description="Search for NPCs with filtering, sorting, and pagination.")
def search_npcs(
    params: dict = Depends(validate_search_query),
    search_service: SearchService = Depends()
):
    return search_service.search_entity("npc", params["q"], params["filter"], params["sort"], params["page"], params["pageSize"])

@router.get("/quests", response_model=SearchResponse, summary="Search Quests", description="Search for quests with filtering, sorting, and pagination.")
def search_quests(
    params: dict = Depends(validate_search_query),
    search_service: SearchService = Depends()
):
    return search_service.search_entity("quest", params["q"], params["filter"], params["sort"], params["page"], params["pageSize"])

@router.get("/items", response_model=SearchResponse, summary="Search Items", description="Search for items with filtering, sorting, and pagination.")
def search_items(
    params: dict = Depends(validate_search_query),
    search_service: SearchService = Depends()
):
    return search_service.search_entity("item", params["q"], params["filter"], params["sort"], params["page"], params["pageSize"])

@router.get("/factions", response_model=SearchResponse, summary="Search Factions", description="Search for factions with filtering, sorting, and pagination.")
def search_factions(
    params: dict = Depends(validate_search_query),
    search_service: SearchService = Depends()
):
    return search_service.search_entity("faction", params["q"], params["filter"], params["sort"], params["page"], params["pageSize"])

@router.get("/locations", response_model=SearchResponse, summary="Search Locations", description="Search for locations with filtering, sorting, and pagination.")
def search_locations(
    params: dict = Depends(validate_search_query),
    search_service: SearchService = Depends()
):
    return search_service.search_entity("location", params["q"], params["filter"], params["sort"], params["page"], params["pageSize"]) 