from backend.schemas.search import SearchResponse
from backend.config import search as search_config
from elasticsearch import Elasticsearch, NotFoundError
from typing import List, Any, Optional, Dict

class SearchService:
    """
    Service for handling search logic and index management for various entities using Elasticsearch.
    """
    def __init__(self):
        self.es = Elasticsearch(search_config.ELASTICSEARCH_URL)
        self.index_names = search_config.INDEX_NAMES
        self.index_settings = search_config.INDEX_SETTINGS

    def get_index(self, entity_type: str) -> str:
        return self.index_names[entity_type]

    def create_index(self, entity_type: str, mappings: dict):
        """
        Create an Elasticsearch index for the given entity type with provided mappings.
        """
        index = self.get_index(entity_type)
        if not self.es.indices.exists(index=index):
            self.es.indices.create(index=index, body={**self.index_settings, "mappings": mappings})

    def index_document(self, entity_type: str, doc_id: str, document: dict):
        """
        Index a single document for the given entity type.
        """
        index = self.get_index(entity_type)
        self.es.index(index=index, id=doc_id, body=document)

    def _build_advanced_query(self, entity_type: str, q: Optional[str], filter: Optional[List[str]], extra: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Build an advanced Elasticsearch query supporting AND/OR, range, nested, geo, and full-text search.
        """
        query = {"bool": {"must": [], "filter": []}}
        # Full-text search with fuzziness and boosting
        if q:
            query["bool"]["must"].append({
                "multi_match": {
                    "query": q,
                    "fields": ["name^3", "title^2", "description", "tags"],
                    "fuzziness": "AUTO"
                }
            })
        # Advanced filter parsing
        if filter:
            for f in filter:
                # AND/OR logic: filter[or][field]=value1,value2 or filter[and][field]=value1,value2
                if f.startswith("or[") and "]=" in f:
                    field = f[3:f.index("]=")]
                    values = f.split("=", 1)[1].split(",")
                    query["bool"]["filter"].append({"bool": {"should": [{"term": {field: v}} for v in values]}})
                elif f.startswith("and[") and "]=" in f:
                    field = f[4:f.index("]=")]
                    values = f.split("=", 1)[1].split(",")
                    query["bool"]["filter"].extend([{"term": {field: v}} for v in values])
                # Range queries: filter[range][field]=min,max
                elif f.startswith("range[") and "]=" in f:
                    field = f[6:f.index("]=")]
                    minmax = f.split("=", 1)[1].split(",")
                    range_query = {}
                    if minmax[0]:
                        range_query["gte"] = float(minmax[0])
                    if len(minmax) > 1 and minmax[1]:
                        range_query["lte"] = float(minmax[1])
                    query["bool"]["filter"].append({"range": {field: range_query}})
                # Geo filtering for worlds: filter[geo][lat]=..., filter[geo][lon]=..., filter[geo][distance]=...
                elif entity_type == "world" and f.startswith("geo[") and "]=" in f:
                    geo_field = f[4:f.index("]=")]
                    value = f.split("=", 1)[1]
                    if geo_field in ("lat", "lon", "distance"):
                        if not extra:
                            extra = {}
                        extra[geo_field] = value
                # Nested property filtering for items: filter[property]=value
                elif entity_type == "item" and f.startswith("property="):
                    prop_val = f.split("=", 1)[1]
                    query["bool"]["filter"].append({"term": {"properties.value": prop_val}})
                # Default: filter[field]=value or field:value
                elif "=" in f:
                    field, value = f.split("=", 1)
                    query["bool"]["filter"].append({"term": {field: value}})
                elif ":" in f:
                    field, value = f.split(":", 1)
                    query["bool"]["filter"].append({"term": {field: value}})
        # Geo filter for worlds
        if entity_type == "world" and extra and all(k in extra for k in ("lat", "lon", "distance")):
            query["bool"]["filter"].append({
                "geo_distance": {
                    "distance": extra["distance"],
                    "location": {
                        "lat": float(extra["lat"]),
                        "lon": float(extra["lon"])
                    }
                }
            })
        return query

    def _build_aggregations(self, entity_type: str) -> Dict:
        """
        Build aggregations for faceted search (e.g., by type, status, tags).
        """
        aggs = {
            "by_type": {"terms": {"field": "type.keyword"}},
            "by_status": {"terms": {"field": "status.keyword"}},
            "by_tags": {"terms": {"field": "tags.keyword"}}
        }
        # Entity-specific facets
        if entity_type == "quest":
            aggs["by_stage"] = {"terms": {"field": "stage.keyword"}}
        if entity_type == "item":
            aggs["by_rarity"] = {"terms": {"field": "rarity.keyword"}}
        return aggs

    def search_entity(self, entity_type: str, q: Optional[str], filter: Optional[List[str]], sort: Optional[str], page: int, pageSize: int) -> SearchResponse:
        """
        Perform a search for the given entity type with advanced filtering, faceted search, and efficient query execution.
        """
        index = self.get_index(entity_type)
        extra = {}
        query = self._build_advanced_query(entity_type, q, filter, extra)
        body = {
            "query": query,
            "from": (page - 1) * pageSize,
            "size": pageSize,
            "aggs": self._build_aggregations(entity_type)
        }
        if sort:
            if ":" in sort:
                field, direction = sort.split(":", 1)
                body["sort"] = [{field: {"order": direction}}]
            else:
                body["sort"] = [{sort: {"order": "asc"}}]
        try:
            resp = self.es.search(index=index, body=body)
            hits = resp["hits"]["hits"]
            results = [h["_source"] for h in hits]
            total = resp["hits"]["total"]["value"]
            facets = {k: v["buckets"] for k, v in resp.get("aggregations", {}).items()} if "aggregations" in resp else None
        except NotFoundError:
            results = []
            total = 0
            facets = None
        return SearchResponse(
            results=results,
            total=total,
            page=page,
            pageSize=pageSize,
            facets=facets
        ) 