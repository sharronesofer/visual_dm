"""Configuration settings for search functionality."""

from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field
from redis import Redis

class SearchSettings(BaseSettings):
    """Search configuration settings."""
    
    # Elasticsearch settings
    es_hosts: list[str] = ["http://elasticsearch:9200"]
    es_username: Optional[str] = None
    es_password: Optional[str] = None
    es_verify_certs: bool = False
    es_ca_certs: Optional[str] = None
    es_client_cert: Optional[str] = None
    es_client_key: Optional[str] = None
    es_timeout: int = 30
    es_retry_on_timeout: bool = True
    es_max_retries: int = 3
    es_sniff_on_start: bool = True
    es_sniff_on_connection_fail: bool = True
    es_sniffer_timeout: int = 60
    es_sniff_timeout: int = 10
    
    # Redis settings
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    redis_timeout: int = 5
    
    # Search settings
    default_page_size: int = 20
    max_page_size: int = 100
    min_score: float = 0.1
    highlight_pre_tags: str = "<mark>"
    highlight_post_tags: str = "</mark>"
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 10000  # Maximum number of cached items
    
    # Circuit breaker settings
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_reset_timeout: int = 60  # seconds
    
    # Rate limiting settings
    rate_limit: int = 100  # Default requests per window
    rate_limit_window: int = 3600  # Default window in seconds (1 hour)
    
    # Operation-specific rate limits
    search_rate_limit: int = 100  # searches per minute
    search_rate_limit_window: int = 60
    suggest_rate_limit: int = 200  # suggestions per minute
    suggest_rate_limit_window: int = 60
    index_rate_limit: int = 50  # index operations per hour
    index_rate_limit_window: int = 3600
    bulk_rate_limit: int = 10  # bulk operations per hour
    bulk_rate_limit_window: int = 3600
    
    # Security settings
    auth_required: bool = True
    token_expiration: int = 3600  # 1 hour
    token_algorithm: str = "HS256"
    token_secret_key: str = Field(..., env="SEARCH_TOKEN_SECRET_KEY")
    
    # Role-based access control
    default_roles: Dict[str, list[str]] = {
        "user": ["search:read"],
        "editor": ["search:read", "search:write"],
        "admin": ["search:read", "search:write", "search:admin"]
    }
    
    # IP allowlist/blocklist
    ip_allowlist: Optional[list[str]] = None
    ip_blocklist: Optional[list[str]] = None
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "SEARCH_"
        case_sensitive = False

# Initialize settings
settings = SearchSettings()

# Elasticsearch client settings
ES_SETTINGS = {
    "hosts": settings.es_hosts,
    "http_auth": (settings.es_username, settings.es_password) if settings.es_username else None,
    "verify_certs": settings.es_verify_certs,
    "ca_certs": settings.es_ca_certs,
    "client_cert": settings.es_client_cert,
    "client_key": settings.es_client_key,
    "timeout": settings.es_timeout,
    "retry_on_timeout": settings.es_retry_on_timeout,
    "max_retries": settings.es_max_retries,
    "sniff_on_start": settings.es_sniff_on_start,
    "sniff_on_connection_fail": settings.es_sniff_on_connection_fail,
    "sniffer_timeout": settings.es_sniffer_timeout,
    "sniff_timeout": settings.es_sniff_timeout
}

# Redis client
redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    ssl=settings.redis_ssl,
    socket_timeout=settings.redis_timeout,
    decode_responses=True
)

# Search settings dictionary
SEARCH_SETTINGS = {
    "default_page_size": settings.default_page_size,
    "max_page_size": settings.max_page_size,
    "min_score": settings.min_score,
    "highlight_pre_tags": settings.highlight_pre_tags,
    "highlight_post_tags": settings.highlight_post_tags,
    "cache_enabled": settings.cache_enabled,
    "cache_ttl": settings.cache_ttl,
    "cache_max_size": settings.cache_max_size,
    "circuit_breaker_enabled": settings.circuit_breaker_enabled,
    "circuit_breaker_failure_threshold": settings.circuit_breaker_failure_threshold,
    "circuit_breaker_reset_timeout": settings.circuit_breaker_reset_timeout,
    "rate_limit": settings.rate_limit,
    "rate_limit_window": settings.rate_limit_window,
    "search_rate_limit": settings.search_rate_limit,
    "search_rate_limit_window": settings.search_rate_limit_window,
    "suggest_rate_limit": settings.suggest_rate_limit,
    "suggest_rate_limit_window": settings.suggest_rate_limit_window,
    "index_rate_limit": settings.index_rate_limit,
    "index_rate_limit_window": settings.index_rate_limit_window,
    "bulk_rate_limit": settings.bulk_rate_limit,
    "bulk_rate_limit_window": settings.bulk_rate_limit_window,
    "auth_required": settings.auth_required,
    "token_expiration": settings.token_expiration,
    "token_algorithm": settings.token_algorithm,
    "token_secret_key": settings.token_secret_key,
    "default_roles": settings.default_roles,
    "ip_allowlist": settings.ip_allowlist,
    "ip_blocklist": settings.ip_blocklist,
    "redis_client": redis_client
}

# Default index mappings for different entity types
DEFAULT_MAPPINGS: Dict[str, Dict[str, Any]] = {
    "npc": {
        "properties": {
            "id": {"type": "keyword"},
            "type": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "game_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "description": {
                "type": "text",
                "analyzer": "game_analyzer"
            },
            "tags": {
                "type": "keyword"
            },
            "metadata": {
                "type": "object",
                "dynamic": True
            },
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            # NPC-specific fields
            "personality_traits": {
                "type": "nested",
                "properties": {
                    "trait": {"type": "keyword"},
                    "value": {"type": "integer"}
                }
            },
            "faction": {"type": "keyword"},
            "level": {"type": "integer"},
            "location": {"type": "keyword"}
        }
    },
    "item": {
        "properties": {
            "id": {"type": "keyword"},
            "type": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "game_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "description": {
                "type": "text",
                "analyzer": "game_analyzer"
            },
            "tags": {
                "type": "keyword"
            },
            "metadata": {
                "type": "object",
                "dynamic": True
            },
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            # Item-specific fields
            "rarity": {"type": "keyword"},
            "category": {"type": "keyword"},
            "level_requirement": {"type": "integer"},
            "value": {"type": "float"}
        }
    },
    "location": {
        "properties": {
            "id": {"type": "keyword"},
            "type": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "game_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "description": {
                "type": "text",
                "analyzer": "game_analyzer"
            },
            "tags": {
                "type": "keyword"
            },
            "metadata": {
                "type": "object",
                "dynamic": True
            },
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            # Location-specific fields
            "region": {"type": "keyword"},
            "terrain_type": {"type": "keyword"},
            "danger_level": {"type": "integer"},
            "coordinates": {"type": "geo_point"}
        }
    },
    "quest": {
        "properties": {
            "id": {"type": "keyword"},
            "type": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "game_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "description": {
                "type": "text",
                "analyzer": "game_analyzer"
            },
            "tags": {
                "type": "keyword"
            },
            "metadata": {
                "type": "object",
                "dynamic": True
            },
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            # Quest-specific fields
            "difficulty": {"type": "keyword"},
            "level_range": {
                "type": "integer_range",
                "fields": {
                    "min": {"type": "integer"},
                    "max": {"type": "integer"}
                }
            },
            "rewards": {
                "type": "nested",
                "properties": {
                    "type": {"type": "keyword"},
                    "value": {"type": "float"}
                }
            },
            "status": {"type": "keyword"}
        }
    }
}

# Default facets for each entity type
DEFAULT_FACETS = {
    "npc": ["faction", "level", "location", "tags"],
    "item": ["rarity", "category", "level_requirement", "tags"],
    "location": ["region", "terrain_type", "danger_level", "tags"],
    "quest": ["difficulty", "status", "tags"]
}

# Search settings
SEARCH_SETTINGS = {
    "max_page_size": 100,
    "default_page_size": 20,
    "min_should_match": "75%",
    "fuzziness": "AUTO",
    "highlight_pre_tags": ["<em>"],
    "highlight_post_tags": ["</em>"],
    "max_expansions": 50,
    "cache_expiry": 300,  # 5 minutes
    "query": {
        "timeout": "5s",
        "terminate_after": 1000,  # Maximum number of docs to collect per shard
        "allow_partial_search_results": True,
        "track_total_hits": 10000,  # Track up to 10k hits for better performance
        "track_scores": True,
        "explain": False,  # Disable score explanation for better performance
        "preference": "_local"  # Prefer local shard copies
    },
    "circuit_breaker": {
        "enabled": True,
        "max_memory": "75%",
        "type": "memory"
    }
}

# Rate limiting settings
RATE_LIMIT_SETTINGS = {
    "requests_per_minute": 60,
    "burst_size": 10,
    "timeframe": 60  # seconds
}

# Cache settings
CACHE_SETTINGS = {
    "enabled": True,
    "ttl": 300,  # 5 minutes
    "max_size": 1000,  # Maximum number of cached queries
    "circuit_breaker": {
        "enabled": True,
        "max_memory": "100mb"
    }
}

# Analyzer settings
ANALYZER_SETTINGS = {
    "game_analyzer": {
        "type": "custom",
        "tokenizer": "standard",
        "char_filter": [
            "html_strip"
        ],
        "filter": [
            "lowercase",
            "stop",
            "snowball",
            "game_synonyms",
            "word_delimiter_graph",
            "unique"
        ]
    },
    "ngram_analyzer": {
        "type": "custom",
        "tokenizer": "ngram_tokenizer",
        "filter": ["lowercase"]
    }
}

# Filter settings
FILTER_SETTINGS = {
    "game_synonyms": {
        "type": "synonym",
        "synonyms": [
            "sword, blade, saber => sword",
            "shield, buckler, aegis => shield",
            "armor, armour, protection => armor",
            "potion, elixir, brew => potion",
            "spell, magic, incantation => spell",
            "quest, mission, task => quest",
            "monster, creature, beast => monster",
            "warrior, fighter, soldier => warrior",
            "mage, wizard, sorcerer => mage",
            "rogue, thief, assassin => rogue"
        ]
    }
}

# Index settings
INDEX_SETTINGS = {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "refresh_interval": "1s",
    "analysis": {
        "analyzer": ANALYZER_SETTINGS,
        "tokenizer": {
            "ngram_tokenizer": {
                "type": "ngram",
                "min_gram": 2,
                "max_gram": 3,
                "token_chars": ["letter", "digit"]
            }
        },
        "filter": FILTER_SETTINGS
    },
    "index": {
        "max_ngram_diff": 10,
        "highlight": {
            "max_analyzed_offset": 1000000
        },
        "routing": {
            "allocation": {
                "total_shards_per_node": 2
            }
        },
        "search": {
            "slowlog": {
                "threshold": {
                    "query": {
                        "warn": "5s",
                        "info": "2s"
                    },
                    "fetch": {
                        "warn": "1s",
                        "info": "500ms"
                    }
                }
            }
        },
        "refresh_interval": "5s",  # Increased for better indexing performance
        "translog": {
            "durability": "async",  # Better indexing performance
            "sync_interval": "5s",
            "flush_threshold_size": "512mb"
        },
        "blocks": {
            "read_only_allow_delete": "false"
        }
    }
}

# Field boost settings
FIELD_BOOST_SETTINGS = {
    "name": 3.0,
    "description": 2.0,
    "tags": 2.0,
    "metadata": 1.0
}

# Query settings by entity type
QUERY_SETTINGS = {
    "npc": {
        "fields": ["name^3", "description^2", "faction^1.5", "tags^2"],
        "fuzziness": "AUTO:4,7",
        "prefix_length": 2,
        "max_expansions": 50
    },
    "item": {
        "fields": ["name^3", "description^2", "category^1.5", "tags^2"],
        "fuzziness": "AUTO:4,7",
        "prefix_length": 2,
        "max_expansions": 50
    },
    "location": {
        "fields": ["name^3", "description^2", "region^1.5", "tags^2"],
        "fuzziness": "AUTO:4,7",
        "prefix_length": 2,
        "max_expansions": 50
    },
    "quest": {
        "fields": ["name^3", "description^2", "difficulty^1.5", "tags^2"],
        "fuzziness": "AUTO:4,7",
        "prefix_length": 2,
        "max_expansions": 50
    }
} 