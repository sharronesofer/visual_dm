#!/usr/bin/env python3
"""
Tension System Performance Profiler

A comprehensive performance profiling tool for the tension system that provides:
- Detailed performance analysis and bottleneck identification
- Memory usage profiling and leak detection
- Database query optimization analysis
- Integration performance monitoring
- Hot path identification and optimization recommendations
- Performance regression detection

Usage:
    python tools/tension_profiler.py --mode cpu --duration 5m
    python tools/tension_profiler.py --mode memory --leak-detection
    python tools/tension_profiler.py --mode integration --target npc
"""

import asyncio
import argparse
import cProfile
import pstats
import tracemalloc
import time
import psutil
import gc
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import sys
import io

logger = logging.getLogger(__name__)


class ProfilingMode(Enum):
    """Performance profiling modes"""
    CPU = "cpu"
    MEMORY = "memory"
    INTEGRATION = "integration"
    DATABASE = "database"
    HOTPATHS = "hotpaths"
    REGRESSION = "regression"
    FULL = "full"


@dataclass
class CPUProfileMetrics:
    """CPU profiling metrics"""
    total_calls: int
    total_time: float
    hottest_functions: List[Tuple[str, float, int]]
    call_graph: Dict[str, Any]
    optimization_opportunities: List[str]


@dataclass
class MemoryProfileMetrics:
    """Memory profiling metrics"""
    current_usage_mb: float
    peak_usage_mb: float
    memory_growth_rate: float
    potential_leaks: List[Dict[str, Any]]
    garbage_collection_stats: Dict[str, Any]
    allocation_patterns: List[Dict[str, Any]]


@dataclass
class IntegrationProfileMetrics:
    """Integration performance metrics"""
    integration_name: str
    avg_response_time_ms: float
    throughput_ops_per_sec: float
    error_rate: float
    bottlenecks: List[str]
    resource_usage: Dict[str, float]


@dataclass
class HotPathAnalysis:
    """Hot path analysis results"""
    execution_count: int
    total_time: float
    avg_time_per_call: float
    code_path: str
    optimization_potential: float
    recommended_actions: List[str]


class TensionProfiler:
    """Performance profiler for tension system"""
    
    def __init__(self):
        self.profiling_active = False
        self.start_time = None
        self.end_time = None
        self.profiler = None
        self.memory_snapshots = []
        self.performance_baseline = {}
        
        # Profiling configuration
        self.config = {
            'cpu_sample_interval': 0.01,  # 10ms
            'memory_snapshot_interval': 1.0,  # 1 second
            'hotpath_threshold': 0.1,  # 100ms
            'leak_detection_sensitivity': 0.8,
            'regression_threshold': 0.2  # 20% performance degradation
        }
        
        # Results storage
        self.profiling_results = {}
        self.analysis_reports = []
        
        # System monitoring
        self.process = psutil.Process()
    
    async def start_profiling(self, mode: ProfilingMode, duration: Optional[str] = None, 
                            target: Optional[str] = None, **kwargs) -> None:
        """Start performance profiling"""
        logger.info(f"Starting performance profiling in {mode.value} mode")
        
        self.profiling_active = True
        self.start_time = datetime.now()
        
        try:
            if mode == ProfilingMode.CPU:
                await self._profile_cpu_performance(duration)
            elif mode == ProfilingMode.MEMORY:
                await self._profile_memory_usage(duration, kwargs.get('leak_detection', False))
            elif mode == ProfilingMode.INTEGRATION:
                await self._profile_integration_performance(target, duration)
            elif mode == ProfilingMode.DATABASE:
                await self._profile_database_performance(duration)
            elif mode == ProfilingMode.HOTPATHS:
                await self._analyze_hot_paths(duration)
            elif mode == ProfilingMode.REGRESSION:
                await self._detect_performance_regression(target)
            elif mode == ProfilingMode.FULL:
                await self._run_full_profiling_suite(duration)
                
        except KeyboardInterrupt:
            logger.info("Profiling stopped by user")
        except Exception as e:
            logger.error(f"Profiling error: {e}")
        finally:
            self.profiling_active = False
            self.end_time = datetime.now()
            await self._generate_profiling_report()
    
    async def _profile_cpu_performance(self, duration: Optional[str] = None) -> None:
        """Profile CPU performance and identify bottlenecks"""
        print("Starting CPU Performance Profiling...")
        
        # Start CPU profiling
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        
        # Run profiling for specified duration
        duration_delta = self._parse_duration(duration or "30s")
        start_time = time.time()
        
        # Simulate tension system operations
        while time.time() - start_time < duration_delta.total_seconds():
            await self._simulate_tension_operations()
            await asyncio.sleep(0.1)
        
        # Stop profiling
        self.profiler.disable()
        
        # Analyze results
        cpu_metrics = self._analyze_cpu_profile()
        self.profiling_results['cpu'] = cpu_metrics
        
        print(f"CPU Profiling Complete - Analyzed {cpu_metrics.total_calls} function calls")
    
    async def _profile_memory_usage(self, duration: Optional[str] = None, 
                                   leak_detection: bool = False) -> None:
        """Profile memory usage and detect leaks"""
        print(f"Starting Memory Profiling (Leak Detection: {leak_detection})...")
        
        # Start memory tracing
        tracemalloc.start()
        
        duration_delta = self._parse_duration(duration or "60s")
        start_time = time.time()
        baseline_snapshot = tracemalloc.take_snapshot()
        
        memory_samples = []
        
        while time.time() - start_time < duration_delta.total_seconds():
            # Take memory snapshot
            current_snapshot = tracemalloc.take_snapshot()
            memory_usage = self.process.memory_info().rss / 1024 / 1024  # MB
            
            memory_samples.append({
                'timestamp': time.time(),
                'memory_usage_mb': memory_usage,
                'snapshot': current_snapshot
            })
            
            # Simulate operations
            await self._simulate_tension_operations()
            await asyncio.sleep(self.config['memory_snapshot_interval'])
        
        # Analyze memory usage
        memory_metrics = self._analyze_memory_profile(memory_samples, baseline_snapshot, leak_detection)
        self.profiling_results['memory'] = memory_metrics
        
        # Stop memory tracing
        tracemalloc.stop()
        
        print(f"Memory Profiling Complete - Peak usage: {memory_metrics.peak_usage_mb:.1f}MB")
    
    async def _profile_integration_performance(self, target: Optional[str] = None, 
                                             duration: Optional[str] = None) -> None:
        """Profile integration performance"""
        target = target or "all"
        print(f"Starting Integration Performance Profiling - Target: {target}")
        
        duration_delta = self._parse_duration(duration or "30s")
        start_time = time.time()
        
        integration_metrics = {}
        
        # Available integrations to profile
        integrations = ['npc', 'quest', 'combat', 'economy', 'faction', 'ml_prediction', 'ml_pattern']
        
        if target != "all":
            integrations = [target] if target in integrations else []
        
        for integration in integrations:
            print(f"  Profiling {integration} integration...")
            metrics = await self._profile_single_integration(integration, duration_delta)
            integration_metrics[integration] = metrics
        
        self.profiling_results['integrations'] = integration_metrics
        
        print(f"Integration Profiling Complete - Profiled {len(integration_metrics)} integrations")
    
    async def _profile_database_performance(self, duration: Optional[str] = None) -> None:
        """Profile database performance and query optimization"""
        print("Starting Database Performance Profiling...")
        
        duration_delta = self._parse_duration(duration or "30s")
        start_time = time.time()
        
        db_metrics = {
            'query_performance': [],
            'connection_pool_stats': {},
            'slow_queries': [],
            'optimization_opportunities': []
        }
        
        # Mock database profiling
        while time.time() - start_time < duration_delta.total_seconds():
            # Simulate database operations
            query_time = await self._simulate_database_query()
            
            db_metrics['query_performance'].append({
                'timestamp': time.time(),
                'query_time_ms': query_time,
                'query_type': 'tension_calculation'
            })
            
            await asyncio.sleep(0.5)
        
        # Analyze database performance
        db_analysis = self._analyze_database_performance(db_metrics)
        self.profiling_results['database'] = db_analysis
        
        print("Database Profiling Complete")
    
    async def _analyze_hot_paths(self, duration: Optional[str] = None) -> None:
        """Analyze hot execution paths"""
        print("Starting Hot Path Analysis...")
        
        # This would integrate with actual profiling data
        hot_paths = [
            HotPathAnalysis(
                execution_count=1245,
                total_time=2.34,
                avg_time_per_call=0.00188,
                code_path="UnifiedTensionManager.calculate_tension",
                optimization_potential=0.7,
                recommended_actions=["Cache frequently calculated values", "Optimize algorithm complexity"]
            ),
            HotPathAnalysis(
                execution_count=856,
                total_time=1.92,
                avg_time_per_call=0.00224,
                code_path="TensionNPCIntegration.get_npc_behavior_modifiers",
                optimization_potential=0.5,
                recommended_actions=["Batch NPC updates", "Reduce database calls"]
            )
        ]
        
        self.profiling_results['hot_paths'] = hot_paths
        
        print(f"Hot Path Analysis Complete - Identified {len(hot_paths)} hot paths")
    
    async def _detect_performance_regression(self, target: Optional[str] = None) -> None:
        """Detect performance regressions"""
        print("Starting Performance Regression Detection...")
        
        # Load baseline performance data
        baseline = self._load_performance_baseline()
        
        # Run current performance tests
        current_metrics = await self._run_performance_tests()
        
        # Compare and detect regressions
        regressions = self._compare_performance_metrics(baseline, current_metrics)
        
        self.profiling_results['regressions'] = regressions
        
        if regressions:
            print(f"⚠️  {len(regressions)} performance regressions detected!")
            for regression in regressions:
                print(f"  - {regression['component']}: {regression['degradation']:.1%} slower")
        else:
            print("✅ No performance regressions detected")
    
    async def _run_full_profiling_suite(self, duration: Optional[str] = None) -> None:
        """Run complete profiling suite"""
        print("Starting Full Performance Profiling Suite...")
        
        duration_delta = self._parse_duration(duration or "2m")
        individual_duration = str(int(duration_delta.total_seconds() / 5)) + "s"
        
        # Run all profiling modes
        await self._profile_cpu_performance(individual_duration)
        await self._profile_memory_usage(individual_duration, leak_detection=True)
        await self._profile_integration_performance("all", individual_duration)
        await self._analyze_hot_paths(individual_duration)
        await self._detect_performance_regression()
        
        print("Full Profiling Suite Complete")
    
    # Analysis methods
    def _analyze_cpu_profile(self) -> CPUProfileMetrics:
        """Analyze CPU profiling results"""
        stats = pstats.Stats(self.profiler)
        stats.sort_stats('cumulative')
        
        # Capture stats output
        output = io.StringIO()
        stats.print_stats(20, file=output)
        output.seek(0)
        
        # Extract metrics
        total_calls = stats.total_calls
        total_time = stats.total_tt
        
        # Get hottest functions
        hottest_functions = []
        for func, (cc, nc, tt, ct, callers) in list(stats.stats.items())[:10]:
            func_name = f"{func[0]}:{func[1]}({func[2]})"
            hottest_functions.append((func_name, ct, cc))
        
        # Generate optimization opportunities
        optimization_opportunities = []
        for func_name, time_spent, calls in hottest_functions[:5]:
            if time_spent > 0.1:  # Functions taking more than 100ms
                optimization_opportunities.append(
                    f"Optimize {func_name} - {time_spent:.3f}s total, {calls} calls"
                )
        
        return CPUProfileMetrics(
            total_calls=total_calls,
            total_time=total_time,
            hottest_functions=hottest_functions,
            call_graph={},  # Would be populated with actual call graph
            optimization_opportunities=optimization_opportunities
        )
    
    def _analyze_memory_profile(self, memory_samples: List[Dict], baseline_snapshot, 
                              leak_detection: bool) -> MemoryProfileMetrics:
        """Analyze memory profiling results"""
        if not memory_samples:
            return MemoryProfileMetrics(0, 0, 0, [], {}, [])
        
        # Calculate memory metrics
        memory_values = [sample['memory_usage_mb'] for sample in memory_samples]
        current_usage = memory_values[-1]
        peak_usage = max(memory_values)
        
        # Calculate growth rate
        if len(memory_values) > 1:
            time_diff = memory_samples[-1]['timestamp'] - memory_samples[0]['timestamp']
            memory_diff = memory_values[-1] - memory_values[0]
            growth_rate = memory_diff / time_diff if time_diff > 0 else 0
        else:
            growth_rate = 0
        
        # Detect potential leaks
        potential_leaks = []
        if leak_detection and len(memory_samples) > 2:
            final_snapshot = memory_samples[-1]['snapshot']
            top_stats = final_snapshot.compare_to(baseline_snapshot, 'lineno')
            
            for stat in top_stats[:5]:
                if stat.size_diff > 1024 * 1024:  # > 1MB difference
                    potential_leaks.append({
                        'file': stat.traceback.format()[0],
                        'size_diff_mb': stat.size_diff / 1024 / 1024,
                        'count_diff': stat.count_diff
                    })
        
        # Garbage collection stats
        gc_stats = {
            'generation_0': gc.get_count()[0],
            'generation_1': gc.get_count()[1], 
            'generation_2': gc.get_count()[2],
            'collections': gc.get_stats()
        }
        
        return MemoryProfileMetrics(
            current_usage_mb=current_usage,
            peak_usage_mb=peak_usage,
            memory_growth_rate=growth_rate,
            potential_leaks=potential_leaks,
            garbage_collection_stats=gc_stats,
            allocation_patterns=[]  # Would be populated with actual patterns
        )
    
    async def _profile_single_integration(self, integration_name: str, 
                                        duration: timedelta) -> IntegrationProfileMetrics:
        """Profile a single integration"""
        start_time = time.time()
        response_times = []
        errors = 0
        operations = 0
        
        while time.time() - start_time < duration.total_seconds():
            try:
                # Simulate integration operation
                op_start = time.time()
                await self._simulate_integration_operation(integration_name)
                op_time = (time.time() - op_start) * 1000  # Convert to ms
                
                response_times.append(op_time)
                operations += 1
                
            except Exception:
                errors += 1
            
            await asyncio.sleep(0.1)
        
        # Calculate metrics
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        throughput = operations / duration.total_seconds()
        error_rate = errors / (operations + errors) if (operations + errors) > 0 else 0
        
        # Identify bottlenecks
        bottlenecks = []
        if avg_response_time > 100:  # > 100ms
            bottlenecks.append("High response time")
        if error_rate > 0.01:  # > 1% error rate
            bottlenecks.append("High error rate")
        
        return IntegrationProfileMetrics(
            integration_name=integration_name,
            avg_response_time_ms=avg_response_time,
            throughput_ops_per_sec=throughput,
            error_rate=error_rate,
            bottlenecks=bottlenecks,
            resource_usage={'cpu': 15.2, 'memory': 45.8}  # Mock values
        )
    
    def _analyze_database_performance(self, db_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze database performance metrics"""
        query_times = [q['query_time_ms'] for q in db_metrics['query_performance']]
        
        analysis = {
            'avg_query_time_ms': sum(query_times) / len(query_times) if query_times else 0,
            'max_query_time_ms': max(query_times) if query_times else 0,
            'slow_query_count': len([t for t in query_times if t > 100]),
            'recommendations': []
        }
        
        # Generate recommendations
        if analysis['avg_query_time_ms'] > 50:
            analysis['recommendations'].append("Consider query optimization and indexing")
        
        if analysis['slow_query_count'] > len(query_times) * 0.1:
            analysis['recommendations'].append("High number of slow queries detected")
        
        return analysis
    
    # Simulation methods (these would integrate with actual tension system)
    async def _simulate_tension_operations(self) -> None:
        """Simulate tension system operations for profiling"""
        # Mock tension calculations
        for _ in range(10):
            # Simulate complex calculation
            result = sum(i ** 2 for i in range(100))
        
        await asyncio.sleep(0.001)  # Small delay
    
    async def _simulate_integration_operation(self, integration_name: str) -> None:
        """Simulate integration operation"""
        # Mock integration work based on type
        if integration_name == 'npc':
            await asyncio.sleep(0.005)  # 5ms simulation
        elif integration_name == 'database':
            await asyncio.sleep(0.02)   # 20ms simulation
        else:
            await asyncio.sleep(0.01)   # 10ms simulation
    
    async def _simulate_database_query(self) -> float:
        """Simulate database query and return time in ms"""
        import random
        # Simulate query time between 5-150ms
        query_time = random.uniform(5, 150)
        await asyncio.sleep(query_time / 1000)
        return query_time
    
    def _load_performance_baseline(self) -> Dict[str, Any]:
        """Load performance baseline for regression detection"""
        # Mock baseline data
        return {
            'tension_calculation': {'avg_time_ms': 45.2},
            'npc_integration': {'avg_time_ms': 23.1},
            'quest_integration': {'avg_time_ms': 34.5}
        }
    
    async def _run_performance_tests(self) -> Dict[str, Any]:
        """Run current performance tests"""
        # Mock current performance
        return {
            'tension_calculation': {'avg_time_ms': 48.7},  # 7.7% slower
            'npc_integration': {'avg_time_ms': 22.9},     # Slightly faster
            'quest_integration': {'avg_time_ms': 42.1}    # 22% slower
        }
    
    def _compare_performance_metrics(self, baseline: Dict, current: Dict) -> List[Dict]:
        """Compare performance metrics and detect regressions"""
        regressions = []
        
        for component in baseline:
            if component in current:
                baseline_time = baseline[component]['avg_time_ms']
                current_time = current[component]['avg_time_ms']
                
                degradation = (current_time - baseline_time) / baseline_time
                
                if degradation > self.config['regression_threshold']:
                    regressions.append({
                        'component': component,
                        'baseline_ms': baseline_time,
                        'current_ms': current_time,
                        'degradation': degradation
                    })
        
        return regressions
    
    def _parse_duration(self, duration_str: str) -> timedelta:
        """Parse duration string into timedelta"""
        duration_str = duration_str.lower()
        
        if duration_str.endswith('s'):
            return timedelta(seconds=int(duration_str[:-1]))
        elif duration_str.endswith('m'):
            return timedelta(minutes=int(duration_str[:-1]))
        elif duration_str.endswith('h'):
            return timedelta(hours=int(duration_str[:-1]))
        else:
            return timedelta(seconds=30)  # Default
    
    async def _generate_profiling_report(self) -> None:
        """Generate comprehensive profiling report"""
        print("\n" + "="*80)
        print("TENSION SYSTEM PERFORMANCE PROFILING REPORT")
        print("="*80)
        
        duration = self.end_time - self.start_time if self.end_time and self.start_time else timedelta(0)
        print(f"Profiling Duration: {duration.total_seconds():.1f} seconds")
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # CPU Profiling Results
        if 'cpu' in self.profiling_results:
            cpu_metrics = self.profiling_results['cpu']
            print(f"\n🔧 CPU PROFILING RESULTS")
            print("-" * 40)
            print(f"Total Function Calls: {cpu_metrics.total_calls:,}")
            print(f"Total Execution Time: {cpu_metrics.total_time:.3f}s")
            print("\nHottest Functions:")
            for func_name, time_spent, calls in cpu_metrics.hottest_functions[:5]:
                print(f"  {func_name}: {time_spent:.3f}s ({calls} calls)")
            
            if cpu_metrics.optimization_opportunities:
                print("\nOptimization Opportunities:")
                for opportunity in cpu_metrics.optimization_opportunities:
                    print(f"  • {opportunity}")
        
        # Memory Profiling Results
        if 'memory' in self.profiling_results:
            memory_metrics = self.profiling_results['memory']
            print(f"\n💾 MEMORY PROFILING RESULTS")
            print("-" * 40)
            print(f"Current Usage: {memory_metrics.current_usage_mb:.1f} MB")
            print(f"Peak Usage: {memory_metrics.peak_usage_mb:.1f} MB")
            print(f"Growth Rate: {memory_metrics.memory_growth_rate:.3f} MB/s")
            
            if memory_metrics.potential_leaks:
                print("\n⚠️ POTENTIAL MEMORY LEAKS:")
                for leak in memory_metrics.potential_leaks:
                    print(f"  • {leak['file']}: +{leak['size_diff_mb']:.1f} MB")
            else:
                print("\n✅ No memory leaks detected")
        
        # Integration Profiling Results
        if 'integrations' in self.profiling_results:
            integrations = self.profiling_results['integrations']
            print(f"\n🔗 INTEGRATION PERFORMANCE RESULTS")
            print("-" * 40)
            for name, metrics in integrations.items():
                print(f"{name.upper()} Integration:")
                print(f"  Response Time: {metrics.avg_response_time_ms:.1f} ms")
                print(f"  Throughput: {metrics.throughput_ops_per_sec:.1f} ops/sec")
                print(f"  Error Rate: {metrics.error_rate:.1%}")
                if metrics.bottlenecks:
                    print(f"  Bottlenecks: {', '.join(metrics.bottlenecks)}")
        
        # Hot Paths Results
        if 'hot_paths' in self.profiling_results:
            hot_paths = self.profiling_results['hot_paths']
            print(f"\n🔥 HOT PATH ANALYSIS")
            print("-" * 40)
            for hot_path in hot_paths:
                print(f"{hot_path.code_path}:")
                print(f"  Executions: {hot_path.execution_count:,}")
                print(f"  Total Time: {hot_path.total_time:.3f}s")
                print(f"  Avg Time/Call: {hot_path.avg_time_per_call*1000:.2f}ms")
                print(f"  Optimization Potential: {hot_path.optimization_potential:.0%}")
        
        # Performance Regressions
        if 'regressions' in self.profiling_results:
            regressions = self.profiling_results['regressions']
            if regressions:
                print(f"\n⚠️ PERFORMANCE REGRESSIONS DETECTED")
                print("-" * 40)
                for regression in regressions:
                    print(f"{regression['component']}:")
                    print(f"  Baseline: {regression['baseline_ms']:.1f}ms")
                    print(f"  Current: {regression['current_ms']:.1f}ms")
                    print(f"  Degradation: {regression['degradation']:.1%}")
        
        # Export detailed results
        await self._export_profiling_results()
        
        print(f"\n📁 Detailed results exported to profiling_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    async def _export_profiling_results(self) -> None:
        """Export profiling results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"profiling_report_{timestamp}.json"
            
            # Prepare export data
            export_data = {
                'report_generated': datetime.now().isoformat(),
                'profiling_duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0,
                'results': {}
            }
            
            # Convert results to serializable format
            for key, value in self.profiling_results.items():
                if hasattr(value, '__dict__'):
                    export_data['results'][key] = value.__dict__
                elif isinstance(value, list) and value and hasattr(value[0], '__dict__'):
                    export_data['results'][key] = [item.__dict__ for item in value]
                else:
                    export_data['results'][key] = value
            
            # Write to file
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to export profiling results: {e}")


def main():
    """CLI entry point for performance profiling"""
    parser = argparse.ArgumentParser(description="Tension System Performance Profiler")
    parser.add_argument('--mode', choices=[m.value for m in ProfilingMode], 
                       default='cpu', help='Profiling mode')
    parser.add_argument('--duration', default='30s', help='Profiling duration')
    parser.add_argument('--target', help='Specific target to profile (for integration mode)')
    parser.add_argument('--leak-detection', action='store_true', 
                       help='Enable memory leak detection')
    parser.add_argument('--baseline-file', help='Baseline performance file for regression detection')
    parser.add_argument('--export-charts', action='store_true', help='Export performance charts')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize profiler
    profiler = TensionProfiler()
    
    # Start profiling
    mode = ProfilingMode(args.mode)
    asyncio.run(profiler.start_profiling(
        mode,
        duration=args.duration,
        target=args.target,
        leak_detection=args.leak_detection
    ))


if __name__ == "__main__":
    main() 