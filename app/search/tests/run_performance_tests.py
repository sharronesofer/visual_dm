"""Script to run load tests and performance tuning."""

import os
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from elasticsearch import Elasticsearch

from app.search.cache import SearchCache
from app.search.client import SearchClient
from .performance_tuner import PerformanceTuner

logger = logging.getLogger(__name__)

class PerformanceTestRunner:
    """Runs load tests and performance tuning process."""
    
    def __init__(
        self,
        host: str = "http://localhost:8000",
        users: int = 50,
        spawn_rate: int = 5,
        run_time: str = "5m",
        es_hosts: Optional[list[str]] = None
    ):
        """Initialize the test runner.
        
        Args:
            host: Host to test against
            users: Number of concurrent users
            spawn_rate: Users to spawn per second
            run_time: How long to run the test
            es_hosts: Elasticsearch hosts
        """
        self.host = host
        self.users = users
        self.spawn_rate = spawn_rate
        self.run_time = run_time
        self.es_hosts = es_hosts or ["http://localhost:9200"]
        
        # Create output directory
        self.output_dir = Path("test_results") / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / "test_run.log"),
                logging.StreamHandler()
            ]
        )
    
    def _run_locust(self) -> None:
        """Run Locust load test."""
        logger.info("Starting Locust load test")
        
        # Build command
        cmd = [
            "locust",
            "-f", "app/search/tests/load_test.py",
            "--host", self.host,
            "--users", str(self.users),
            "--spawn-rate", str(self.spawn_rate),
            "--run-time", self.run_time,
            "--headless",
            "--csv", str(self.output_dir / "locust"),
            "--json"
        ]
        
        # Run Locust
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Save JSON stats
            stats = json.loads(result.stdout)
            with open(self.output_dir / "locust_stats.json", "w") as f:
                json.dump(stats, f, indent=2)
                
            logger.info("Locust test completed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Locust test failed: {e.stderr}")
            raise
    
    def _collect_cache_stats(self) -> None:
        """Collect Redis cache statistics."""
        logger.info("Collecting cache statistics")
        
        try:
            # Initialize cache client
            cache = SearchCache()
            
            # Get stats
            stats = {
                "hits": cache.client.info()["keyspace_hits"],
                "misses": cache.client.info()["keyspace_misses"],
                "memory_usage": cache.client.info()["used_memory"],
                "total_keys": cache.client.dbsize(),
                "evicted_keys": cache.client.info()["evicted_keys"]
            }
            
            # Save stats
            with open(self.output_dir / "cache_stats.json", "w") as f:
                json.dump(stats, f, indent=2)
                
            logger.info("Cache statistics collected")
            
        except Exception as e:
            logger.error(f"Failed to collect cache stats: {str(e)}")
            raise
    
    def _tune_performance(self) -> None:
        """Run performance tuning process."""
        logger.info("Starting performance tuning")
        
        try:
            # Initialize Elasticsearch client
            es_client = Elasticsearch(self.es_hosts)
            
            # Create tuner
            tuner = PerformanceTuner(
                es_client=es_client,
                locust_stats_file=str(self.output_dir / "locust_stats.json"),
                cache_stats_file=str(self.output_dir / "cache_stats.json")
            )
            
            # Generate and apply recommendations
            recommendations = tuner.generate_recommendations()
            
            # Save recommendations
            with open(self.output_dir / "recommendations.json", "w") as f:
                json.dump(recommendations, f, indent=2)
            
            # Apply if any recommendations
            if recommendations:
                logger.info(f"Applying {len(recommendations)} recommendations")
                tuner.apply_recommendations(recommendations)
            else:
                logger.info("No performance recommendations generated")
                
        except Exception as e:
            logger.error(f"Performance tuning failed: {str(e)}")
            raise
    
    def run(self) -> None:
        """Run the complete test and tuning process."""
        try:
            # Run load test
            self._run_locust()
            
            # Collect cache stats
            self._collect_cache_stats()
            
            # Run performance tuning
            self._tune_performance()
            
            logger.info(
                f"Performance testing completed. "
                f"Results saved in {self.output_dir}"
            )
            
        except Exception as e:
            logger.error(f"Performance testing failed: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage:
    runner = PerformanceTestRunner(
        host="http://localhost:8000",
        users=50,
        spawn_rate=5,
        run_time="5m"
    )
    runner.run() 