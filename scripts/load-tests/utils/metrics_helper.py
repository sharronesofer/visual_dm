#!/usr/bin/env python3
"""
Helper module to work with split metric files.
Provides functions to read split metric files and process them as if they were a single file.
"""

import os
import json
import glob
from pathlib import Path
from typing import Dict, List, Generator, Any, Optional, Union


def get_metrics_path(metric_type: str) -> str:
    """
    Get the path to the split metrics directory for a specific metric type.
    
    Args:
        metric_type: One of 'load', 'spike', or 'stress'
    
    Returns:
        Path to the split metrics directory
    """
    base_path = Path(__file__).parent.parent / "results" / "split"
    return str(base_path / f"{metric_type}_metrics")


def iter_metrics(metric_type: str) -> Generator[Dict[str, Any], None, None]:
    """
    Iterate through all metrics of a specific type, reading from split files.
    
    Args:
        metric_type: One of 'load', 'spike', or 'stress'
    
    Yields:
        Each metric object from the split files
    """
    metrics_path = get_metrics_path(metric_type)
    part_files = sorted(glob.glob(os.path.join(metrics_path, f"{metric_type}_metrics_part*.json")))
    
    for file_path in part_files:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        print(f"Warning: Skipping invalid JSON in {file_path}")


def count_metrics(metric_type: str) -> int:
    """
    Count the total number of metrics across all split files.
    
    Args:
        metric_type: One of 'load', 'spike', or 'stress'
    
    Returns:
        Total count of metrics
    """
    count = 0
    for _ in iter_metrics(metric_type):
        count += 1
    return count


def filter_metrics(
    metric_type: str, 
    field_filter: Optional[Dict[str, Any]] = None,
    tag_filter: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Filter metrics by field values and/or tags.
    
    Args:
        metric_type: One of 'load', 'spike', or 'stress'
        field_filter: Dictionary of fields to match at the top level
        tag_filter: Dictionary of tags to match in the data.tags field
    
    Returns:
        List of matching metric objects
    """
    results = []
    
    field_filter = field_filter or {}
    tag_filter = tag_filter or {}
    
    for metric in iter_metrics(metric_type):
        # Check if all field filters match
        field_match = all(
            metric.get(field) == value
            for field, value in field_filter.items()
        )
        
        # Check if all tag filters match
        tag_match = True
        if 'data' in metric and 'tags' in metric['data']:
            tags = metric['data']['tags']
            tag_match = all(
                tags.get(tag) == value
                for tag, value in tag_filter.items()
            )
        elif tag_filter:
            # If tag filters specified but no tags in data, it's not a match
            tag_match = False
        
        if field_match and tag_match:
            results.append(metric)
    
    return results


def get_metric_stats(metric_type: str, metric_name: str) -> Dict[str, Union[int, float]]:
    """
    Calculate statistics for a specific metric.
    
    Args:
        metric_type: One of 'load', 'spike', or 'stress'
        metric_name: Name of the metric to analyze
    
    Returns:
        Dictionary with metric statistics (count, min, max, avg)
    """
    values = []
    
    for metric in filter_metrics(metric_type, {'metric': metric_name, 'type': 'Point'}):
        if 'data' in metric and 'value' in metric['data']:
            try:
                value = float(metric['data']['value'])
                values.append(value)
            except (ValueError, TypeError):
                pass
    
    if not values:
        return {
            'count': 0,
            'min': None,
            'max': None,
            'avg': None
        }
    
    return {
        'count': len(values),
        'min': min(values),
        'max': max(values),
        'avg': sum(values) / len(values)
    }


if __name__ == "__main__":
    # Example usage
    print("Load Metrics Stats:")
    print(f"Total metrics: {count_metrics('load')}")
    
    # Get stats for HTTP request duration
    print("\nHTTP Request Duration Stats:")
    http_req_stats = get_metric_stats('load', 'http_req_duration')
    print(f"Count: {http_req_stats['count']}")
    print(f"Min: {http_req_stats['min']}")
    print(f"Max: {http_req_stats['max']}")
    print(f"Avg: {http_req_stats['avg']}") 