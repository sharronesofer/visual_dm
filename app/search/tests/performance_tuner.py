"""Performance tuning script for search functionality."""

import json
import logging
import statistics
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)

class PerformanceTuner:
    """Analyzes load test results and tunes performance settings."""
    
    def __init__(
        self,
        es_client: Elasticsearch,
        locust_stats_file: str,
        cache_stats_file: Optional[str] = None
    ):
        """Initialize the tuner.
        
        Args:
            es_client: Elasticsearch client
            locust_stats_file: Path to Locust stats export
            cache_stats_file: Optional path to cache stats export
        """
        self.es_client = es_client
        self.locust_stats = self._load_json(locust_stats_file)
        self.cache_stats = (
            self._load_json(cache_stats_file)
            if cache_stats_file
            else None
        )
        
    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file."""
        with open(file_path) as f:
            return json.load(f)
    
    def analyze_response_times(self) -> Dict[str, Any]:
        """Analyze response time statistics."""
        stats = {}
        for endpoint in self.locust_stats["requests"]:
            times = endpoint["response_times"].values()
            if times:
                stats[endpoint["name"]] = {
                    "avg": statistics.mean(times),
                    "p50": np.percentile(list(times), 50),
                    "p95": np.percentile(list(times), 95),
                    "p99": np.percentile(list(times), 99),
                    "max": max(times),
                    "min": min(times)
                }
        return stats
    
    def analyze_error_rates(self) -> Dict[str, float]:
        """Calculate error rates by endpoint."""
        error_rates = {}
        for endpoint in self.locust_stats["requests"]:
            total = endpoint["num_requests"]
            if total > 0:
                error_rate = (endpoint["num_failures"] / total) * 100
                error_rates[endpoint["name"]] = error_rate
        return error_rates
    
    def analyze_cache_performance(self) -> Optional[Dict[str, Any]]:
        """Analyze cache hit rates and memory usage."""
        if not self.cache_stats:
            return None
            
        return {
            "hit_rate": (
                self.cache_stats["hits"] /
                (self.cache_stats["hits"] + self.cache_stats["misses"])
                * 100
            ),
            "memory_usage_mb": self.cache_stats["memory_usage"] / (1024 * 1024),
            "eviction_rate": (
                self.cache_stats["evicted_keys"] /
                self.cache_stats["total_keys"]
                * 100
                if self.cache_stats["total_keys"] > 0
                else 0
            )
        }
    
    def get_es_stats(self) -> Dict[str, Any]:
        """Get Elasticsearch performance metrics."""
        stats = self.es_client.nodes.stats()
        node_stats = next(iter(stats["nodes"].values()))
        
        return {
            "query_total": node_stats["indices"]["search"]["query_total"],
            "query_time_ms": node_stats["indices"]["search"]["query_time_in_millis"],
            "avg_query_time_ms": (
                node_stats["indices"]["search"]["query_time_in_millis"] /
                node_stats["indices"]["search"]["query_total"]
                if node_stats["indices"]["search"]["query_total"] > 0
                else 0
            ),
            "fetch_total": node_stats["indices"]["search"]["fetch_total"],
            "fetch_time_ms": node_stats["indices"]["search"]["fetch_time_in_millis"],
            "cache_size": node_stats["indices"]["query_cache"]["memory_size_in_bytes"],
            "cache_hit_count": node_stats["indices"]["query_cache"]["hit_count"],
            "cache_miss_count": node_stats["indices"]["query_cache"]["miss_count"],
            "segments_count": node_stats["indices"]["segments"]["count"],
            "segments_memory": node_stats["indices"]["segments"]["memory_in_bytes"]
        }
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate performance tuning recommendations."""
        recommendations = []
        
        # Analyze response times
        response_times = self.analyze_response_times()
        for endpoint, stats in response_times.items():
            if stats["p95"] > 500:  # If 95th percentile > 500ms
                recommendations.append({
                    "type": "response_time",
                    "severity": "high",
                    "endpoint": endpoint,
                    "message": (
                        f"High response time for {endpoint}. "
                        f"95th percentile: {stats['p95']:.2f}ms. "
                        "Consider increasing cache TTL and adjusting "
                        "Elasticsearch query timeout."
                    ),
                    "suggested_settings": {
                        "cache_ttl": 600,  # 10 minutes
                        "query_timeout": "10s"
                    }
                })
        
        # Analyze error rates
        error_rates = self.analyze_error_rates()
        for endpoint, rate in error_rates.items():
            if rate > 1:  # If error rate > 1%
                recommendations.append({
                    "type": "error_rate",
                    "severity": "high",
                    "endpoint": endpoint,
                    "message": (
                        f"High error rate for {endpoint}: {rate:.2f}%. "
                        "Consider adjusting circuit breaker settings and "
                        "increasing connection pool size."
                    ),
                    "suggested_settings": {
                        "circuit_breaker": {
                            "failure_threshold": 10,
                            "reset_timeout": 120
                        },
                        "pool_maxsize": 50
                    }
                })
        
        # Analyze cache performance
        cache_stats = self.analyze_cache_performance()
        if cache_stats:
            if cache_stats["hit_rate"] < 80:
                recommendations.append({
                    "type": "cache_performance",
                    "severity": "medium",
                    "message": (
                        f"Low cache hit rate: {cache_stats['hit_rate']:.2f}%. "
                        "Consider increasing cache size and TTL."
                    ),
                    "suggested_settings": {
                        "cache_size": 2000,
                        "cache_ttl": 600
                    }
                })
            
            if cache_stats["eviction_rate"] > 10:
                recommendations.append({
                    "type": "cache_eviction",
                    "severity": "medium",
                    "message": (
                        f"High cache eviction rate: {cache_stats['eviction_rate']:.2f}%. "
                        "Consider increasing cache size or reducing TTL."
                    ),
                    "suggested_settings": {
                        "cache_size": 2000,
                        "cache_ttl": 300
                    }
                })
        
        # Analyze Elasticsearch performance
        es_stats = self.get_es_stats()
        if es_stats["avg_query_time_ms"] > 100:
            recommendations.append({
                "type": "es_performance",
                "severity": "high",
                "message": (
                    f"High average query time: {es_stats['avg_query_time_ms']:.2f}ms. "
                    "Consider optimizing query complexity and adjusting "
                    "relevance scoring."
                ),
                "suggested_settings": {
                    "min_should_match": "50%",
                    "max_expansions": 30,
                    "query_timeout": "5s"
                }
            })
        
        return recommendations
    
    def apply_recommendations(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> None:
        """Apply recommended settings."""
        es_settings = {}
        cache_settings = {}
        circuit_breaker_settings = {}
        
        for rec in recommendations:
            if "suggested_settings" in rec:
                settings = rec["suggested_settings"]
                
                if "min_should_match" in settings:
                    es_settings["min_should_match"] = settings["min_should_match"]
                if "max_expansions" in settings:
                    es_settings["max_expansions"] = settings["max_expansions"]
                if "query_timeout" in settings:
                    es_settings["query_timeout"] = settings["query_timeout"]
                
                if "cache_size" in settings:
                    cache_settings["max_size"] = settings["cache_size"]
                if "cache_ttl" in settings:
                    cache_settings["ttl"] = settings["cache_ttl"]
                
                if "circuit_breaker" in settings:
                    circuit_breaker_settings.update(settings["circuit_breaker"])
        
        # Update settings files
        if es_settings:
            self._update_settings_file(
                "app/search/config.py",
                "SEARCH_SETTINGS",
                es_settings
            )
        
        if cache_settings:
            self._update_settings_file(
                "app/search/config.py",
                "CACHE_SETTINGS",
                cache_settings
            )
        
        if circuit_breaker_settings:
            self._update_settings_file(
                "app/search/config.py",
                "SEARCH_SETTINGS",
                {"circuit_breaker": circuit_breaker_settings}
            )
    
    def _update_settings_file(
        self,
        file_path: str,
        settings_var: str,
        new_settings: Dict[str, Any]
    ) -> None:
        """Update settings in a Python file."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the settings dictionary
        start = content.find(f"{settings_var} = {{")
        if start == -1:
            logger.error(f"Could not find {settings_var} in {file_path}")
            return
        
        # Find the matching closing brace
        level = 0
        end = start
        for i, char in enumerate(content[start:], start):
            if char == '{':
                level += 1
            elif char == '}':
                level -= 1
                if level == 0:
                    end = i + 1
                    break
        
        if end <= start:
            logger.error(f"Could not find end of {settings_var} in {file_path}")
            return
        
        # Extract current settings
        settings_str = content[start:end]
        settings_dict = eval(settings_str.split('=', 1)[1].strip())
        
        # Update settings
        settings_dict.update(new_settings)
        
        # Format new settings
        new_settings_str = f"{settings_var} = {json.dumps(settings_dict, indent=4)}"
        
        # Replace in file
        new_content = content[:start] + new_settings_str + content[end:]
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        logger.info(f"Updated {settings_var} in {file_path}")

if __name__ == "__main__":
    # Example usage:
    # tuner = PerformanceTuner(
    #     es_client=Elasticsearch(),
    #     locust_stats_file="locust_stats.json",
    #     cache_stats_file="cache_stats.json"
    # )
    # recommendations = tuner.generate_recommendations()
    # tuner.apply_recommendations(recommendations)
    pass 