"""
Command-line interface for the World Validation System.

This module provides a command-line interface for validating worlds,
running property-based tests, and generating validation reports.
"""

import argparse
import logging
import json
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path
import time
from datetime import datetime

from app.core.models.world import World
from app.core.persistence.world_persistence import WorldPersistenceManager, FileSystemStorageStrategy
from .world_validation import WorldValidator, ValidationResult
from .property_testing import PropertyBasedTesting, PropertyTestResult
from .validation_api import validate_world_cli, property_test_world_cli

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False):
    """Set up logging for the CLI."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="World Validation System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Validate world command
    validate_parser = subparsers.add_parser("validate", help="Validate a world")
    validate_parser.add_argument("world_id", help="ID of the world to validate")
    validate_parser.add_argument("--rules", "-r", nargs="+", help="Specific validation rules to apply")
    validate_parser.add_argument("--output", "-o", help="Output file for validation report (JSON)")
    validate_parser.add_argument("--storage", "-s", default="data/worlds", help="Storage root directory")
    validate_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    # Property test command
    property_parser = subparsers.add_parser("property-test", help="Run property-based tests on a world")
    property_parser.add_argument("world_id", help="ID of the world to test")
    property_parser.add_argument("--properties", "-p", nargs="+", help="Specific properties to test")
    property_parser.add_argument("--output", "-o", help="Output file for test report (JSON)")
    property_parser.add_argument("--storage", "-s", default="data/worlds", help="Storage root directory")
    property_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    # Batch validate command
    batch_parser = subparsers.add_parser("batch", help="Validate multiple worlds")
    batch_parser.add_argument("--world-ids", "-w", nargs="+", required=True, help="IDs of worlds to validate")
    batch_parser.add_argument("--rules", "-r", nargs="+", help="Specific validation rules to apply")
    batch_parser.add_argument("--output", "-o", help="Output file for validation report (JSON)")
    batch_parser.add_argument("--storage", "-s", default="data/worlds", help="Storage root directory")
    batch_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    # List rules command
    rules_parser = subparsers.add_parser("list-rules", help="List available validation rules")
    rules_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    # List properties command
    properties_parser = subparsers.add_parser("list-properties", help="List available world properties")
    properties_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    return parser.parse_args()

def command_validate(args):
    """Run the validate command."""
    # Set up logging
    setup_logging(args.verbose)
    
    # Validate the world
    logger.info(f"Validating world {args.world_id}")
    
    report = validate_world_cli(args.world_id, args.rules)
    
    # Print summary
    if "error" in report:
        logger.error(f"Error: {report['error']}")
        return 1
    
    summary = report.get("summary", {})
    total_rules = summary.get("total_rules", 0)
    passed_rules = summary.get("passed_rules", 0)
    failed_rules = summary.get("failed_rules", 0)
    
    print(f"World: {report.get('world_name', args.world_id)}")
    print(f"Total rules: {total_rules}")
    print(f"Passed rules: {passed_rules}")
    print(f"Failed rules: {failed_rules}")
    print(f"Pass percentage: {summary.get('pass_percentage', 0):.2f}%")
    
    # Print failed rules
    results = report.get("results", {})
    if failed_rules > 0:
        print("\nFailed rules:")
        for rule_id, result in results.items():
            if not result.get("is_valid", True):
                print(f"  {rule_id}: {result.get('message', 'No message')}")
    
    # Save report if output file is specified
    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Saved validation report to {args.output}")
    
    return 0 if failed_rules == 0 else 1

def command_property_test(args):
    """Run the property-test command."""
    # Set up logging
    setup_logging(args.verbose)
    
    # Run property tests on the world
    logger.info(f"Running property tests on world {args.world_id}")
    
    report = property_test_world_cli(args.world_id, args.properties)
    
    # Print summary
    if "error" in report:
        logger.error(f"Error: {report['error']}")
        return 1
    
    summary = report.get("summary", {})
    total_properties = summary.get("total_properties", 0)
    passed_properties = summary.get("passed_properties", 0)
    failed_properties = summary.get("failed_properties", 0)
    
    print(f"World: {args.world_id}")
    print(f"Total properties: {total_properties}")
    print(f"Passed properties: {passed_properties}")
    print(f"Failed properties: {failed_properties}")
    print(f"Pass percentage: {summary.get('pass_percentage', 0):.2f}%")
    
    # Print failed properties
    results = report.get("results", {})
    if failed_properties > 0:
        print("\nFailed properties:")
        for property_name, result in results.items():
            if not result.get("is_valid", True):
                print(f"  {property_name}: {result.get('message', 'No message')}")
    
    # Save report if output file is specified
    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Saved property test report to {args.output}")
    
    return 0 if failed_properties == 0 else 1

def command_batch(args):
    """Run the batch validate command."""
    # Set up logging
    setup_logging(args.verbose)
    
    # Validate multiple worlds
    world_ids = args.world_ids
    logger.info(f"Batch validating {len(world_ids)} worlds")
    
    results = {}
    success_count = 0
    failure_count = 0
    error_count = 0
    
    for world_id in world_ids:
        logger.info(f"Validating world {world_id}")
        report = validate_world_cli(world_id, args.rules)
        
        results[world_id] = report
        
        if "error" in report:
            error_count += 1
        else:
            summary = report.get("summary", {})
            failed_rules = summary.get("failed_rules", 0)
            
            if failed_rules == 0:
                success_count += 1
            else:
                failure_count += 1
    
    # Print summary
    print(f"Total worlds: {len(world_ids)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"Errors: {error_count}")
    
    # Save report if output file is specified
    if args.output:
        batch_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_worlds": len(world_ids),
                "successful": success_count,
                "failed": failure_count,
                "errors": error_count
            },
            "results": results
        }
        
        with open(args.output, "w") as f:
            json.dump(batch_report, f, indent=2)
        logger.info(f"Saved batch validation report to {args.output}")
    
    return 0 if failure_count == 0 and error_count == 0 else 1

def command_list_rules(args):
    """Run the list-rules command."""
    # Set up logging
    setup_logging(args.verbose)
    
    # Create validator
    validator = WorldValidator()
    
    # List rules
    print("Available validation rules:")
    for rule in validator.validation_rules:
        print(f"  {rule['id']}: {rule['description']}")
    
    return 0

def command_list_properties(args):
    """Run the list-properties command."""
    # Set up logging
    setup_logging(args.verbose)
    
    # Create property tester
    property_tester = PropertyBasedTesting()
    
    # List properties
    print("Available world properties:")
    for prop in property_tester.properties:
        print(f"  {prop.name}: {prop.description}")
    
    return 0

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    if args.command == "validate":
        return command_validate(args)
    elif args.command == "property-test":
        return command_property_test(args)
    elif args.command == "batch":
        return command_batch(args)
    elif args.command == "list-rules":
        return command_list_rules(args)
    elif args.command == "list-properties":
        return command_list_properties(args)
    else:
        print("No command specified. Use --help for usage information.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 