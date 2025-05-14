"""Load testing script for search functionality using locust."""

from locust import HttpUser, task, between
from typing import List, Dict, Any
import random
import json

# Sample test data
SEARCH_QUERIES = [
    "dragon",
    "magic sword",
    "ancient temple",
    "goblin king",
    "enchanted forest",
    "mystic portal",
    "dark dungeon",
    "crystal cave",
    "fire elemental",
    "frost giant"
]

ENTITY_TYPES = ["npc", "item", "location", "quest"]

FACET_FILTERS = {
    "npc": ["faction", "level", "class"],
    "item": ["rarity", "type", "level"],
    "location": ["region", "difficulty", "type"],
    "quest": ["level", "type", "faction"]
}

class SearchLoadTest(HttpUser):
    """Load test for search functionality."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Setup before tests."""
        # Verify API is accessible
        with self.client.get("/api/v1/search/health") as response:
            if response.status_code != 200:
                raise Exception("Search API is not healthy")
    
    @task(10)
    def simple_search(self):
        """Basic search without filters."""
        query = random.choice(SEARCH_QUERIES)
        with self.client.get(
            f"/api/v1/search?q={query}",
            name="Simple Search"
        ) as response:
            if response.status_code != 200:
                response.failure("Search failed")
    
    @task(5)
    def filtered_search(self):
        """Search with entity type and facet filters."""
        query = random.choice(SEARCH_QUERIES)
        entity_type = random.choice(ENTITY_TYPES)
        facets = FACET_FILTERS[entity_type]
        
        # Randomly select 1-2 facets to filter by
        num_filters = random.randint(1, 2)
        selected_facets = random.sample(facets, num_filters)
        
        # Build filter string
        filters = "&".join(f"filter_{facet}=value" for facet in selected_facets)
        
        with self.client.get(
            f"/api/v1/search?q={query}&type={entity_type}&{filters}",
            name="Filtered Search"
        ) as response:
            if response.status_code != 200:
                response.failure("Filtered search failed")
    
    @task(3)
    def complex_search(self):
        """Complex search with multiple filters and sorting."""
        query = " ".join(random.sample(SEARCH_QUERIES, 2))  # Combine two queries
        entity_type = random.choice(ENTITY_TYPES)
        facets = FACET_FILTERS[entity_type]
        
        # Use multiple filters
        filters = "&".join(f"filter_{facet}=value" for facet in facets)
        
        # Add sorting and pagination
        sort_field = random.choice(["name", "created_at", "updated_at"])
        sort_order = random.choice(["asc", "desc"])
        page = random.randint(1, 5)
        page_size = random.choice([10, 20, 50])
        
        url = (
            f"/api/v1/search?q={query}&type={entity_type}&{filters}"
            f"&sort={sort_field}&order={sort_order}"
            f"&page={page}&page_size={page_size}"
        )
        
        with self.client.get(url, name="Complex Search") as response:
            if response.status_code != 200:
                response.failure("Complex search failed")
    
    @task(1)
    def stress_test(self):
        """Rapid sequence of searches to stress test the system."""
        for _ in range(5):
            query = random.choice(SEARCH_QUERIES)
            entity_type = random.choice(ENTITY_TYPES)
            
            with self.client.get(
                f"/api/v1/search?q={query}&type={entity_type}",
                name="Stress Test Search"
            ) as response:
                if response.status_code != 200:
                    response.failure("Stress test search failed")
                    break

if __name__ == "__main__":
    # Run with: locust -f load_test.py --host=http://localhost:8000
    pass 