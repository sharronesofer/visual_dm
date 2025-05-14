"""
Benchmark utility for the floating origin system.
Tests performance with different numbers of entities and shift scenarios.
"""

import time
import random
import argparse
import logging
import json
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt

from visual_client.core.utils.coordinates import GlobalCoord, LocalCoord
from visual_client.core.utils.floating_origin import FloatingOrigin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FloatingOriginBenchmark:
    """Benchmark for floating origin performance."""
    
    def __init__(self, floating_origin: FloatingOrigin):
        """Initialize benchmark with a floating origin instance."""
        self.floating_origin = floating_origin
        self.results = []
        self.entity_positions = {}  # entity_id -> (x, y, z)
        
    def setup_entities(self, count: int, batch_size: int = 100, group_pattern: str = "group_{batch}") -> None:
        """
        Set up entities for benchmarking.
        
        Args:
            count: Number of entities to create
            batch_size: Number of entities per batch for batch registration
            group_pattern: Pattern for group names with {batch} placeholder
        """
        logger.info(f"Setting up {count} entities with batch size {batch_size}")
        
        # Clear any existing entities
        for entity_id in list(self.floating_origin.registered_entities.keys()):
            self.floating_origin.unregister_entity(entity_id)
        
        self.entity_positions = {}
        
        # Create entities in batches
        for batch_idx in range(0, count, batch_size):
            batch_count = min(batch_size, count - batch_idx)
            batch_entities = []
            group_name = group_pattern.format(batch=batch_idx // batch_size)
            
            for i in range(batch_count):
                entity_idx = batch_idx + i
                entity_id = f"entity_{entity_idx}"
                
                # Random position within 10000 units
                pos = (
                    random.uniform(-5000, 5000),
                    random.uniform(-5000, 5000),
                    random.uniform(-1000, 1000)
                )
                self.entity_positions[entity_id] = pos
                
                batch_entities.append((
                    entity_id,
                    lambda eid=entity_id: GlobalCoord(*self.entity_positions[eid]),
                    lambda dx, dy, dz, eid=entity_id: self._update_entity_position(eid, dx, dy, dz)
                ))
            
            self.floating_origin.batch_register_entities(batch_entities, group=group_name)
        
        logger.info(f"Created {count} entities in {(count + batch_size - 1) // batch_size} batches")
    
    def _update_entity_position(self, entity_id: str, dx: float, dy: float, dz: float) -> None:
        """Update entity position (called during origin shift)."""
        if entity_id in self.entity_positions:
            x, y, z = self.entity_positions[entity_id]
            self.entity_positions[entity_id] = (x + dx, y + dy, z + dz)
    
    def run_single_benchmark(self, entity_count: int, shifts: int) -> Dict[str, Any]:
        """
        Run a single benchmark with specified parameters.
        
        Args:
            entity_count: Number of entities to use
            shifts: Number of origin shifts to perform
            
        Returns:
            Dictionary with benchmark results
        """
        logger.info(f"Running benchmark with {entity_count} entities and {shifts} shifts")
        
        # Set up entities
        self.setup_entities(entity_count)
        
        # Prepare player positions for shifts
        player_positions = []
        for i in range(shifts):
            # Move in a spiral pattern
            angle = (i / 10) * 2 * 3.14159
            distance = 1000 + i * 100
            x = distance * (angle / 10) * 0.5 * random.uniform(0.9, 1.1)
            y = distance * (angle / 10) * 0.5 * random.uniform(0.9, 1.1)
            z = i * 10 * random.uniform(0.9, 1.1)
            player_positions.append(GlobalCoord(x, y, z))
        
        # Reset metrics
        self.floating_origin.metrics = type(self.floating_origin.metrics)()
        
        # Run benchmark
        start_time = time.time()
        
        for pos in player_positions:
            self.floating_origin.update_player_position(pos)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Collect results
        metrics = self.floating_origin.get_metrics()
        
        result = {
            "entity_count": entity_count,
            "shifts": shifts,
            "total_time": total_time,
            "avg_time_per_shift": total_time / shifts if shifts > 0 else 0,
            "metrics": metrics
        }
        
        self.results.append(result)
        return result
    
    def run_benchmarks(self, entity_counts: List[int], shifts: int = 10) -> List[Dict[str, Any]]:
        """
        Run benchmarks with different entity counts.
        
        Args:
            entity_counts: List of entity counts to benchmark
            shifts: Number of origin shifts per benchmark
            
        Returns:
            List of benchmark results
        """
        results = []
        for count in entity_counts:
            result = self.run_single_benchmark(count, shifts)
            results.append(result)
            logger.info(f"Benchmark result: {count} entities, {shifts} shifts, {result['avg_time_per_shift']*1000:.2f}ms per shift")
        
        return results
    
    def plot_results(self, output_file: str = None) -> None:
        """
        Plot benchmark results.
        
        Args:
            output_file: Optional file path to save plot
        """
        if not self.results:
            logger.warning("No benchmark results to plot")
            return
        
        entity_counts = [r["entity_count"] for r in self.results]
        avg_times = [r["avg_time_per_shift"] * 1000 for r in self.results]  # Convert to ms
        
        plt.figure(figsize=(10, 6))
        plt.plot(entity_counts, avg_times, 'o-', linewidth=2)
        plt.title('Floating Origin Shift Performance')
        plt.xlabel('Number of Entities')
        plt.ylabel('Average Shift Time (ms)')
        plt.grid(True)
        
        # Add annotations for data points
        for i, (count, time_ms) in enumerate(zip(entity_counts, avg_times)):
            plt.annotate(
                f"{time_ms:.2f} ms",
                (count, time_ms),
                textcoords="offset points",
                xytext=(0, 10),
                ha='center'
            )
        
        if output_file:
            plt.savefig(output_file)
            logger.info(f"Saved plot to {output_file}")
        else:
            plt.show()
    
    def save_results(self, output_file: str) -> None:
        """
        Save benchmark results to a JSON file.
        
        Args:
            output_file: Path to output file
        """
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Saved benchmark results to {output_file}")
    
def run_benchmark():
    """Run benchmark from command line."""
    parser = argparse.ArgumentParser(description='Floating Origin Benchmark')
    parser.add_argument('--counts', type=str, default="100,1000,5000,10000",
                        help='Comma-separated list of entity counts to benchmark')
    parser.add_argument('--shifts', type=int, default=20,
                        help='Number of origin shifts per benchmark')
    parser.add_argument('--plot', action='store_true',
                        help='Plot the results')
    parser.add_argument('--output', type=str, default="benchmark_results.json",
                        help='Output file for benchmark results')
    parser.add_argument('--plot-output', type=str, default="benchmark_plot.png",
                        help='Output file for benchmark plot')
    
    args = parser.parse_args()
    
    # Parse entity counts
    entity_counts = [int(count) for count in args.counts.split(',')]
    
    # Create benchmark
    floating_origin = FloatingOrigin()
    benchmark = FloatingOriginBenchmark(floating_origin)
    
    # Run benchmarks
    benchmark.run_benchmarks(entity_counts, args.shifts)
    
    # Save results
    benchmark.save_results(args.output)
    
    # Plot results if requested
    if args.plot:
        benchmark.plot_results(args.plot_output)

if __name__ == '__main__':
    run_benchmark() 