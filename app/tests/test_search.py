"""Tests for search functionality."""

import pytest
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, List, Any

from app.search.models import (
    EntityType, FacetType, FacetConfig, EntityMapping,
    FacetValue, FacetResult, SearchResult,
    NPC_MAPPING, ITEM_MAPPING, LOCATION_MAPPING, QUEST_MAPPING
)
from app.search.service import SearchService, SearchableEntity
from app.search.client import SearchClient
from app.search.exceptions import SearchError, IndexError, ConfigurationError
from app.search.pagination import PaginationParams, PaginatedResponse

# Test data
@pytest.fixture
def test_items():
    """Create test items for search testing."""
    return [
        {
            "id": str(uuid4()),
            "name": "Sword of Truth",
            "description": "A powerful magical sword",
            "type": "weapon",
            "rarity": "legendary",
            "value": 1000,
            "level_req": 20,
            "stats": [
                {"name": "damage", "value": 50.0},
                {"name": "speed", "value": 1.2}
            ],
            "tags": ["sword", "magic", "legendary"]
        },
        {
            "id": str(uuid4()),
            "name": "Shield of Protection",
            "description": "A sturdy shield",
            "type": "armor",
            "rarity": "rare",
            "value": 500,
            "level_req": 15,
            "stats": [
                {"name": "defense", "value": 30.0},
                {"name": "block", "value": 20.0}
            ],
            "tags": ["shield", "defense"]
        },
        {
            "id": str(uuid4()),
            "name": "Health Potion",
            "description": "Restores health",
            "type": "consumable",
            "rarity": "common",
            "value": 50,
            "level_req": 1,
            "stats": [
                {"name": "healing", "value": 100.0}
            ],
            "tags": ["potion", "healing"]
        }
    ]

@pytest.fixture
def test_npcs():
    """Create test NPCs for search testing."""
    return [
        {
            "id": str(uuid4()),
            "name": "Master Smith",
            "description": "A skilled blacksmith",
            "personality": "friendly",
            "faction": "craftsmen",
            "location": "market_district",
            "level": 30,
            "tags": ["merchant", "blacksmith"]
        },
        {
            "id": str(uuid4()),
            "name": "Guard Captain",
            "description": "Leader of the city guard",
            "personality": "stern",
            "faction": "city_guard",
            "location": "barracks",
            "level": 25,
            "tags": ["guard", "warrior"]
        }
    ]

@pytest.fixture
def search_service():
    """Create a search service for testing."""
    client = SearchClient(hosts=["localhost:9200"])
    service = SearchService(client)
    
    # Register entity types
    for entity_type, mapping in [
        (EntityType.ITEM, ITEM_MAPPING),
        (EntityType.NPC, NPC_MAPPING),
        (EntityType.LOCATION, LOCATION_MAPPING),
        (EntityType.QUEST, QUEST_MAPPING)
    ]:
        service.register_entity(
            SearchableEntity(
                entity_type=entity_type,
                mapping=mapping,
                model_cls=dict  # Use dict for testing
            )
        )
    
    return service

def test_faceted_search(search_service, test_items):
    """Test faceted search functionality."""
    # Index test items
    for item in test_items:
        search_service.index_document(item)
        
    # Basic search with facets
    result = search_service.search(
        query="",
        entity_type=EntityType.ITEM
    )
    
    assert result.total == len(test_items)
    assert result.facets is not None
    
    # Check facet values
    assert "type" in result.facets
    assert "rarity" in result.facets
    assert "value" in result.facets
    assert "level_req" in result.facets
    
    # Verify facet counts
    type_facets = result.facets["type"]
    assert any(f.value == "weapon" and f.count == 1 for f in type_facets)
    assert any(f.value == "armor" and f.count == 1 for f in type_facets)
    assert any(f.value == "consumable" and f.count == 1 for f in type_facets)
    
    rarity_facets = result.facets["rarity"]
    assert any(f.value == "legendary" and f.count == 1 for f in rarity_facets)
    assert any(f.value == "rare" and f.count == 1 for f in rarity_facets)
    assert any(f.value == "common" and f.count == 1 for f in rarity_facets)
    
    # Test filtering by facet
    result = search_service.search(
        query="",
        entity_type=EntityType.ITEM,
        filters={"rarity": ["legendary", "rare"]}
    )
    
    assert result.total == 2
    assert all(
        item["rarity"] in ["legendary", "rare"]
        for item in result.results
    )
    
    # Test range facets
    result = search_service.search(
        query="",
        entity_type=EntityType.ITEM,
        filters={"value": [{"from": 500}]}
    )
    
    assert result.total == 2
    assert all(
        item["value"] >= 500
        for item in result.results
    )
    
    # Test nested facets
    result = search_service.search(
        query="",
        entity_type=EntityType.ITEM,
        filters={"stats": ["damage"]}
    )
    
    assert result.total == 1
    assert any(
        stat["name"] == "damage"
        for stat in result.results[0]["stats"]
    )

def test_multi_facet_filtering(search_service, test_items):
    """Test filtering by multiple facets."""
    # Index test items
    for item in test_items:
        search_service.index_document(item)
        
    # Filter by type and rarity
    result = search_service.search(
        query="",
        entity_type=EntityType.ITEM,
        filters={
            "type": ["weapon"],
            "rarity": ["legendary"]
        }
    )
    
    assert result.total == 1
    assert result.results[0]["name"] == "Sword of Truth"
    
    # Verify facet counts are updated
    assert result.facets is not None
    type_facets = result.facets["type"]
    assert any(
        f.value == "weapon" and f.count == 1 and f.selected
        for f in type_facets
    )

def test_faceted_search_with_query(search_service, test_items):
    """Test combining faceted search with text search."""
    # Index test items
    for item in test_items:
        search_service.index_document(item)
        
    # Search with query and facets
    result = search_service.search(
        query="shield",
        entity_type=EntityType.ITEM,
        filters={"type": ["armor"]}
    )
    
    assert result.total == 1
    assert result.results[0]["name"] == "Shield of Protection"
    
    # Verify facets are properly filtered
    assert result.facets is not None
    rarity_facets = result.facets["rarity"]
    assert any(f.value == "rare" and f.count == 1 for f in rarity_facets)

def test_empty_facets(search_service):
    """Test faceted search with no results."""
    result = search_service.search(
        query="nonexistent",
        entity_type=EntityType.ITEM
    )
    
    assert result.total == 0
    assert result.facets is not None
    assert all(len(values) == 0 for values in result.facets.values())

def test_cross_entity_search(search_service, test_items, test_npcs):
    """Test searching across multiple entity types."""
    # Index test data
    for item in test_items:
        search_service.index_document(item)
    for npc in test_npcs:
        search_service.index_document(npc)
        
    # Search across all types
    result = search_service.search(query="sword")
    
    assert result.total == 2  # Should find Sword of Truth and Master Smith
    assert any(
        "type" in doc and doc["type"] == "weapon"
        for doc in result.results
    )
    assert any(
        "faction" in doc and doc["faction"] == "craftsmen"
        for doc in result.results
    )
    
    # Facets should be None for cross-entity search
    assert result.facets is None

def test_npc_to_search_document():
    """Test converting an NPC to a search document."""
    doc = NPC.to_search_document(TEST_NPC)
    assert isinstance(doc, SearchDocument)
    assert doc.id == str(TEST_NPC.id)
    assert doc.type == "npc"
    assert doc.name == TEST_NPC.name
    assert doc.description == TEST_NPC.description
    assert doc.tags == TEST_NPC.tags
    assert doc.metadata["level"] == TEST_NPC.level
    assert doc.metadata["faction"] == TEST_NPC.faction
    assert doc.metadata["location"] == TEST_NPC.location
    assert len(doc.metadata["personality_traits"]) == 2

def test_npc_from_search_document():
    """Test creating an NPC from a search document."""
    doc = SearchDocument(
        id=str(TEST_NPC.id),
        type="npc",
        name=TEST_NPC.name,
        description=TEST_NPC.description,
        tags=TEST_NPC.tags,
        metadata={
            "level": TEST_NPC.level,
            "faction": TEST_NPC.faction,
            "location": TEST_NPC.location,
            "personality_traits": [
                {"trait": "friendly", "value": 8},
                {"trait": "brave", "value": 7}
            ],
            "test_key": "test_value"
        }
    )
    npc = NPC.from_search_document(doc)
    assert isinstance(npc, NPC)
    assert npc.id == TEST_NPC.id
    assert npc.name == TEST_NPC.name
    assert npc.description == TEST_NPC.description
    assert npc.level == TEST_NPC.level
    assert npc.faction == TEST_NPC.faction
    assert npc.location == TEST_NPC.location
    assert npc.personality_traits == TEST_NPC.personality_traits
    assert npc.tags == TEST_NPC.tags
    assert npc.metadata == TEST_NPC.metadata

def test_item_to_search_document():
    """Test converting an Item to a search document."""
    doc = Item.to_search_document(TEST_ITEM)
    assert isinstance(doc, SearchDocument)
    assert doc.id == str(TEST_ITEM.id)
    assert doc.type == "item"
    assert doc.name == TEST_ITEM.name
    assert doc.description == TEST_ITEM.description
    assert doc.tags == TEST_ITEM.tags
    assert doc.metadata["rarity"] == TEST_ITEM.rarity
    assert doc.metadata["category"] == TEST_ITEM.category
    assert doc.metadata["level_requirement"] == TEST_ITEM.level_requirement
    assert doc.metadata["value"] == TEST_ITEM.value

def test_item_from_search_document():
    """Test creating an Item from a search document."""
    doc = SearchDocument(
        id=str(TEST_ITEM.id),
        type="item",
        name=TEST_ITEM.name,
        description=TEST_ITEM.description,
        tags=TEST_ITEM.tags,
        metadata={
            "rarity": TEST_ITEM.rarity,
            "category": TEST_ITEM.category,
            "level_requirement": TEST_ITEM.level_requirement,
            "value": TEST_ITEM.value,
            "test_key": "test_value"
        }
    )
    item = Item.from_search_document(doc)
    assert isinstance(item, Item)
    assert item.id == TEST_ITEM.id
    assert item.name == TEST_ITEM.name
    assert item.description == TEST_ITEM.description
    assert item.rarity == TEST_ITEM.rarity
    assert item.category == TEST_ITEM.category
    assert item.level_requirement == TEST_ITEM.level_requirement
    assert item.value == TEST_ITEM.value
    assert item.tags == TEST_ITEM.tags
    assert item.metadata == TEST_ITEM.metadata

@pytest.mark.asyncio
async def test_search_api(client):
    """Test the search API endpoints."""
    # Test search endpoint
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "test",
            "entity_type": "npc",
            "pagination": {
                "page": 1,
                "limit": 10
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert "page" in data
    assert "limit" in data
    assert "total_pages" in data
    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total_pages"] >= 0

    # Test pagination limits
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "test",
            "entity_type": "npc",
            "pagination": {
                "page": 1,
                "limit": 200  # Should be capped at 100
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] <= 100  # Verify limit is capped

    # Test invalid pagination
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "test",
            "entity_type": "npc",
            "pagination": {
                "page": 0,  # Invalid page number
                "limit": 10
            }
        }
    )
    assert response.status_code == 422  # Validation error

    # Test health check endpoint
    response = await client.get("/api/v1/search/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "cluster_name" in data
    assert "number_of_nodes" in data
    assert "active_shards" in data

    # Test suggest endpoint
    response = await client.get(
        "/api/v1/search/suggest",
        params={
            "query": "test",
            "entity_type": "npc",
            "limit": 5
        }
    )
    assert response.status_code == 200
    suggestions = response.json()
    assert isinstance(suggestions, list)
    assert len(suggestions) <= 5

@pytest.mark.asyncio
async def test_search_service_pagination(search_service):
    """Test search service pagination."""
    # Test basic pagination
    result = await search_service.search(
        query="test",
        entity_type=EntityType.NPC,
        pagination=PaginationParams(page=1, limit=10)
    )
    assert isinstance(result, PaginatedResponse)
    assert result.page == 1
    assert result.limit == 10
    assert len(result.items) <= result.limit
    assert result.total >= 0
    assert result.total_pages >= 0

    # Test empty results
    result = await search_service.search(
        query="nonexistent",
        entity_type=EntityType.NPC,
        pagination=PaginationParams(page=1, limit=10)
    )
    assert isinstance(result, PaginatedResponse)
    assert result.total == 0
    assert result.total_pages == 0
    assert len(result.items) == 0

    # Test last page
    result = await search_service.search(
        query="test",
        entity_type=EntityType.NPC,
        pagination=PaginationParams(page=999999, limit=10)  # Very high page number
    )
    assert isinstance(result, PaginatedResponse)
    assert len(result.items) == 0  # Should be empty for non-existent page

@pytest.mark.integration
def test_search_service_integration(search_service):
    """Integration test for SearchService with Elasticsearch."""
    # Index test entities
    search_service.index_entity(TEST_NPC, "npc")
    search_service.index_entity(TEST_ITEM, "item")
    search_service.index_entity(TEST_LOCATION, "location")
    search_service.index_entity(TEST_QUEST, "quest")
    
    # Force refresh to ensure indexed documents are searchable
    search_service.refresh_index("npc")
    search_service.refresh_index("item")
    search_service.refresh_index("location")
    search_service.refresh_index("quest")
    
    # Test searching NPCs
    result = search_service.search_entities(
        entity_type="npc",
        query="test",
        facets=["faction", "level"]
    )
    assert isinstance(result, SearchResult)
    assert result.total >= 1
    assert len(result.hits) >= 1
    assert len(result.facets) == 2
    
    # Test searching with filters
    result = search_service.search_entities(
        entity_type="npc",
        query="test",
        filters={"faction": "Test Faction"}
    )
    assert result.total >= 1
    assert all(hit.faction == "Test Faction" for hit in result.hits)
    
    # Clean up test data
    search_service.delete_entity("npc", str(TEST_NPC.id))
    search_service.delete_entity("item", str(TEST_ITEM.id))
    search_service.delete_entity("location", str(TEST_LOCATION.id))
    search_service.delete_entity("quest", str(TEST_QUEST.id))

def test_search_service_error_handling(search_service):
    """Test error handling in SearchService."""
    # Test invalid entity type
    with pytest.raises(ConfigurationError):
        search_service.search_entities(
            entity_type="invalid",
            query="test"
        )
    
    # Test invalid filter
    with pytest.raises(SearchError):
        search_service.search_entities(
            entity_type="npc",
            query="test",
            filters={"invalid_field": "value"}
        )
    
    # Test invalid sort field
    with pytest.raises(SearchError):
        search_service.search_entities(
            entity_type="npc",
            query="test",
            sort_by="invalid_field"
        )

def test_init_search():
    """Test search service initialization."""
    service = init_search(hosts=["localhost:9200"])
    assert isinstance(service, SearchService)
    
    # Verify indices were created
    for entity_type in ["npc", "item", "location", "quest"]:
        index_name = service.client.get_index_name(entity_type)
        assert service.client.client.indices.exists(index=index_name)
    
    # Verify health
    health = service.health_check()
    assert health["status"] in ["green", "yellow"]  # yellow is acceptable for single-node
    assert health["number_of_nodes"] >= 1

def test_fuzzy_search(search_service):
    """Test fuzzy matching in search."""
    # Index test documents
    sword = Item(
        id=str(uuid4()),
        name="Sword of Truth",
        description="A powerful magical sword",
        type="weapon",
        rarity="legendary",
        value=1000
    )
    shield = Item(
        id=str(uuid4()),
        name="Shield of Protection",
        description="A sturdy shield",
        type="armor",
        rarity="rare",
        value=500
    )
    search_service.index_document(sword)
    search_service.index_document(shield)
    
    # Test fuzzy matching
    results = search_service.search("sord", fuzzy=True)  # Misspelled "sword"
    assert len(results.results) == 1
    assert results.results[0]["name"] == "Sword of Truth"
    
    # Test without fuzzy matching
    results = search_service.search("sord", fuzzy=False)
    assert len(results.results) == 0
    
    # Test synonym matching
    results = search_service.search("blade", fuzzy=True)
    assert len(results.results) == 1
    assert results.results[0]["name"] == "Sword of Truth"

def test_field_boosting(search_service):
    """Test field boosting in search results."""
    # Index test documents
    doc1 = Item(
        id=str(uuid4()),
        name="Magic Sword",
        description="A regular sword with some magic",
        type="weapon",
        rarity="common",
        value=100
    )
    doc2 = Item(
        id=str(uuid4()),
        name="Regular Sword",
        description="This magic weapon is very powerful",
        type="weapon",
        rarity="common",
        value=100
    )
    search_service.index_document(doc1)
    search_service.index_document(doc2)
    
    # Search for "magic" - doc1 should score higher due to name field boosting
    results = search_service.search("magic")
    assert len(results.results) == 2
    assert results.results[0]["name"] == "Magic Sword"  # Should be first due to name boost
    assert results.results[0]["_score"] > results.results[1]["_score"]

def test_phrase_matching(search_service):
    """Test exact phrase matching."""
    # Index test documents
    doc1 = NPC(
        id=str(uuid4()),
        name="John Smith",
        description="The village blacksmith",
        personality="friendly",
        faction="Village",
        location="Marketplace"
    )
    doc2 = NPC(
        id=str(uuid4()),
        name="Smith John",
        description="A wandering smith",
        personality="mysterious",
        faction="None",
        location="Roads"
    )
    search_service.index_document(doc1)
    search_service.index_document(doc2)
    
    # Test exact phrase matching
    results = search_service.search("John Smith")
    assert len(results.results) >= 1
    assert results.results[0]["name"] == "John Smith"
    assert results.results[0]["_score"] > 1.0  # Exact phrase should have high score 