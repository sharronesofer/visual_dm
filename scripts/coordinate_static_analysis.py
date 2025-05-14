#!/usr/bin/env python3
"""
Coordinate System Static Analysis Tool

This script runs static analysis checks on Python files to detect potential issues
with the coordinate system conventions. It can be integrated into CI pipelines
to enforce coordinate standards.

Usage:
    python coordinate_static_analysis.py [options] [path...]

Options:
    --verbose, -v           Enable verbose output
    --strict                Fail on any warning (exit code 1)
    --summary               Show summary statistics only
    --output=FILE           Write results to file instead of stdout
    --include-pattern=GLOB  Only check files matching this pattern (default: **/*.py)
    --exclude-pattern=GLOB  Exclude files matching this pattern
    --max-coord-value=N     Flag coordinates with absolute value > N (default: 10000)
    --help, -h              Show this help message and exit

Examples:
    python coordinate_static_analysis.py visual_client/
    python coordinate_static_analysis.py --strict --exclude-pattern="**/test_*.py" visual_client/
"""

import os
import re
import sys
import glob
import json
import logging
import argparse
import ast
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("coordinate_analysis")

# Constants
DEFAULT_MAX_COORD_VALUE = 10000.0
DEFAULT_INCLUDE_PATTERN = "**/*.py"
COORDINATE_TYPES = {"GlobalCoord", "LocalCoord"}
COORDINATE_METHODS = {
    # Methods that should return GlobalCoord
    "global": {
        "get_global_position", "global_to_tuple", "tuple_to_global", 
        "local_to_global", "get_position", "screen_to_world"
    },
    # Methods that should return LocalCoord
    "local": {
        "get_local_position", "local_to_tuple", "tuple_to_local",
        "global_to_local"
    }
}
TUPLE_FUNCTIONS = {
    # Functions that convert from tuples
    "from_tuple": {
        "tuple_to_global", "tuple_to_local"
    },
    # Functions that convert to tuples
    "to_tuple": {
        "global_to_tuple", "local_to_tuple"
    }
}

@dataclass
class Issue:
    """Represents a coordinate system issue found during analysis."""
    file: str
    line: int
    col: int
    msg: str
    severity: str  # 'error', 'warning', or 'info'

@dataclass
class AnalysisStats:
    """Statistics from the analysis run."""
    files_analyzed: int = 0
    issues_found: int = 0
    raw_tuples_used: int = 0
    large_coords: int = 0
    wrong_return_types: int = 0
    missing_type_hints: int = 0
    bad_conventions: int = 0
    
    def to_dict(self) -> Dict[str, int]:
        """Convert stats to a dictionary."""
        return {
            "files_analyzed": self.files_analyzed,
            "issues_found": self.issues_found,
            "raw_tuples_used": self.raw_tuples_used,
            "large_coords": self.large_coords,
            "wrong_return_types": self.wrong_return_types,
            "missing_type_hints": self.missing_type_hints,
            "bad_conventions": self.bad_conventions,
        }

@dataclass
class AnalysisOptions:
    """Configuration options for analysis."""
    verbose: bool = False
    strict: bool = False
    summary: bool = False
    output_file: Optional[str] = None
    include_pattern: str = DEFAULT_INCLUDE_PATTERN
    exclude_pattern: Optional[str] = None
    max_coord_value: float = DEFAULT_MAX_COORD_VALUE
    paths: List[str] = field(default_factory=list)

class CoordinateAnalysisVisitor(ast.NodeVisitor):
    """AST visitor that checks for coordinate system issues."""
    
    def __init__(self, filename: str, options: AnalysisOptions):
        self.filename = filename
        self.options = options
        self.issues: List[Issue] = []
        self.stats = AnalysisStats()
        self.in_function = None  # Track current function name
        self.defined_types: Dict[str, str] = {}  # Track variable types
        self.function_returns: Dict[str, str] = {}  # Track function return types
        
        # Load file content for getting source lines
        try:
            with open(filename, 'r') as f:
                self.file_content = f.readlines()
        except Exception as e:
            logger.error(f"Could not read file {filename}: {e}")
            self.file_content = []
    
    def add_issue(self, node: ast.AST, msg: str, severity: str = "warning") -> None:
        """Add an issue to the list."""
        issue = Issue(
            file=self.filename,
            line=getattr(node, "lineno", 0),
            col=getattr(node, "col_offset", 0),
            msg=msg,
            severity=severity
        )
        self.issues.append(issue)
        self.stats.issues_found += 1
        
        # Update specific issue stats
        if "raw tuple" in msg.lower():
            self.stats.raw_tuples_used += 1
        elif "large coordinate" in msg.lower():
            self.stats.large_coords += 1
        elif "return type" in msg.lower():
            self.stats.wrong_return_types += 1
        elif "type hint" in msg.lower():
            self.stats.missing_type_hints += 1
        elif "convention" in msg.lower():
            self.stats.bad_conventions += 1
    
    def get_line(self, lineno: int) -> str:
        """Get the source line at the given line number."""
        if 0 < lineno <= len(self.file_content):
            return self.file_content[lineno - 1].strip()
        return ""
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition."""
        self.in_function = node.name
        
        # Check return type annotation
        returns = None
        if node.returns:
            # Extract return type annotation
            if isinstance(node.returns, ast.Name):
                returns = node.returns.id
            elif isinstance(node.returns, ast.Attribute):
                returns = node.returns.attr
            
            # Store function return type
            if returns in COORDINATE_TYPES:
                self.function_returns[node.name] = returns
        
        # Check if function name suggests a coordinate return type but lacks annotation
        for coord_type, methods in COORDINATE_METHODS.items():
            if any(method in node.name.lower() for method in methods) and not returns:
                expected_type = "GlobalCoord" if coord_type == "global" else "LocalCoord"
                self.add_issue(
                    node,
                    f"Function '{node.name}' appears to handle {coord_type} coordinates "
                    f"but lacks {expected_type} return type annotation",
                    "warning"
                )
        
        # Visit children
        self.generic_visit(node)
        self.in_function = None
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit an assignment."""
        # Check for raw tuple assignments that might be coordinates
        if isinstance(node.value, ast.Tuple):
            # Check if the tuple has 2 or 3 elements (likely a coordinate)
            if len(node.value.elts) in (2, 3) and all(
                isinstance(elt, (ast.Num, ast.Constant, ast.UnaryOp)) 
                for elt in node.value.elts
            ):
                # Extract target variable name
                target_name = ""
                if isinstance(node.targets[0], ast.Name):
                    target_name = node.targets[0].id
                
                # Heuristic: Check for coordinate-like variable names
                coord_patterns = [
                    "coord", "pos", "position", "location", "point",
                    "world", "screen", "global", "local"
                ]
                
                if any(pattern in target_name.lower() for pattern in coord_patterns):
                    self.add_issue(
                        node,
                        f"Raw tuple that appears to be a coordinate assigned to '{target_name}', "
                        f"use GlobalCoord or LocalCoord instead",
                        "warning"
                    )
        
        # Visit children
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit a function call."""
        # Check if call is to a constructor for GlobalCoord or LocalCoord
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        # Check coordinate constructors for large values
        if func_name in COORDINATE_TYPES:
            # Check for large coordinate values
            for arg_idx, arg in enumerate(node.args):
                if isinstance(arg, ast.Num) and abs(arg.n) > self.options.max_coord_value:
                    self.add_issue(
                        node,
                        f"Large coordinate value {arg.n} in {func_name} constructor may cause precision issues",
                        "warning"
                    )
                elif isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)) and abs(arg.value) > self.options.max_coord_value:
                    self.add_issue(
                        node,
                        f"Large coordinate value {arg.value} in {func_name} constructor may cause precision issues",
                        "warning"
                    )
        
        # Check for tuple conversion function usage
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in TUPLE_FUNCTIONS.get("from_tuple", set()):
                # Check that the results are properly used
                if not isinstance(node.parent, ast.Assign):
                    self.add_issue(
                        node,
                        f"Result of tuple conversion function '{node.func.attr}' should be assigned to a variable",
                        "warning"
                    )
            elif node.func.attr in TUPLE_FUNCTIONS.get("to_tuple", set()):
                # Check if the tuple result is immediately used for something else,
                # which might suggest coordinate_utils functions should be used instead
                if not isinstance(node.parent, (ast.Assign, ast.Return)):
                    self.add_issue(
                        node,
                        f"Consider using coordinate_utils methods instead of manual conversion via '{node.func.attr}'",
                        "info"
                    )
        
        # Visit children
        self.generic_visit(node)
    
    def visit_Return(self, node: ast.Return) -> None:
        """Visit a return statement."""
        # Check if we're returning a raw tuple from a function that should return a coordinate
        if self.in_function and self.in_function in self.function_returns:
            expected_type = self.function_returns[self.in_function]
            if isinstance(node.value, ast.Tuple) and len(node.value.elts) in (2, 3):
                self.add_issue(
                    node,
                    f"Function '{self.in_function}' should return {expected_type} but returns raw tuple",
                    "error"
                )
        
        # Visit children
        self.generic_visit(node)


def get_files_to_analyze(options: AnalysisOptions) -> List[str]:
    """Get list of files to analyze based on options."""
    all_files = []
    
    # Handle paths provided on command line
    for path in options.paths:
        if os.path.isdir(path):
            # Use glob to find Python files in the directory
            pattern = os.path.join(path, options.include_pattern)
            matched_files = glob.glob(pattern, recursive=True)
            all_files.extend(matched_files)
        elif os.path.isfile(path):
            all_files.append(path)
    
    # Apply exclude pattern if specified
    if options.exclude_pattern:
        excluded_files = set(glob.glob(options.exclude_pattern, recursive=True))
        all_files = [f for f in all_files if f not in excluded_files]
    
    return all_files

def analyze_file(filename: str, options: AnalysisOptions) -> Tuple[List[Issue], AnalysisStats]:
    """Analyze a single file for coordinate system issues."""
    try:
        with open(filename, 'r') as f:
            tree = ast.parse(f.read(), filename=filename)
        
        # Add parent references to make analysis easier
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        visitor = CoordinateAnalysisVisitor(filename, options)
        visitor.visit(tree)
        
        return visitor.issues, visitor.stats
    
    except SyntaxError as e:
        # Handle Python syntax errors
        logger.error(f"Syntax error in {filename}: {e}")
        return [Issue(
            file=filename,
            line=e.lineno or 0,
            col=e.offset or 0,
            msg=f"Syntax error: {e}",
            severity="error"
        )], AnalysisStats(files_analyzed=1, issues_found=1)
    
    except Exception as e:
        # Handle other errors
        logger.error(f"Error analyzing {filename}: {e}")
        return [Issue(
            file=filename,
            line=0,
            col=0,
            msg=f"Error analyzing file: {e}",
            severity="error"
        )], AnalysisStats(files_analyzed=1, issues_found=1)

def format_issues(issues: List[Issue], options: AnalysisOptions) -> str:
    """Format a list of issues as a string."""
    if options.summary:
        return f"Found {len(issues)} issues."
    
    if not issues:
        return "No issues found."
    
    lines = []
    for issue in sorted(issues, key=lambda i: (i.file, i.line, i.col)):
        severity_marker = "ERROR" if issue.severity == "error" else "WARN " if issue.severity == "warning" else "INFO "
        location = f"{issue.file}:{issue.line}:{issue.col}"
        lines.append(f"{severity_marker} {location}: {issue.msg}")
    
    return "\n".join(lines)

def run_analysis(options: AnalysisOptions) -> Tuple[List[Issue], AnalysisStats]:
    """Run coordinate system analysis on all specified files."""
    files = get_files_to_analyze(options)
    all_issues = []
    total_stats = AnalysisStats()
    
    if options.verbose:
        logger.info(f"Analyzing {len(files)} files")
    
    for filename in files:
        if options.verbose:
            logger.info(f"Analyzing {filename}")
        
        issues, file_stats = analyze_file(filename, options)
        all_issues.extend(issues)
        
        # Update total stats
        total_stats.files_analyzed += file_stats.files_analyzed
        total_stats.issues_found += file_stats.issues_found
        total_stats.raw_tuples_used += file_stats.raw_tuples_used
        total_stats.large_coords += file_stats.large_coords
        total_stats.wrong_return_types += file_stats.wrong_return_types
        total_stats.missing_type_hints += file_stats.missing_type_hints
        total_stats.bad_conventions += file_stats.bad_conventions
    
    if options.verbose or options.summary:
        logger.info(f"Analysis complete. Found {total_stats.issues_found} issues in {total_stats.files_analyzed} files")
    
    return all_issues, total_stats

def parse_args() -> AnalysisOptions:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--strict", action="store_true", help="Fail on any warning (exit code 1)")
    parser.add_argument("--summary", action="store_true", help="Show summary statistics only")
    parser.add_argument("--output", help="Write results to file instead of stdout")
    parser.add_argument("--include-pattern", default=DEFAULT_INCLUDE_PATTERN, 
                        help=f"Only check files matching this pattern (default: {DEFAULT_INCLUDE_PATTERN})")
    parser.add_argument("--exclude-pattern", help="Exclude files matching this pattern")
    parser.add_argument("--max-coord-value", type=float, default=DEFAULT_MAX_COORD_VALUE,
                        help=f"Flag coordinates with absolute value > N (default: {DEFAULT_MAX_COORD_VALUE})")
    parser.add_argument("paths", metavar="path", nargs="*", help="Files or directories to analyze")
    
    args = parser.parse_args()
    
    # Convert args to options object
    options = AnalysisOptions(
        verbose=args.verbose,
        strict=args.strict,
        summary=args.summary,
        output_file=args.output,
        include_pattern=args.include_pattern,
        exclude_pattern=args.exclude_pattern,
        max_coord_value=args.max_coord_value,
        paths=args.paths
    )
    
    if not options.paths:
        # Default to current directory if no paths provided
        options.paths = ["."]
    
    return options

def main() -> int:
    """Main entry point."""
    options = parse_args()
    issues, stats = run_analysis(options)
    
    # Prepare output
    output = format_issues(issues, options)
    if options.summary:
        # Add summary statistics
        output += "\n\nStatistics:\n"
        for key, value in stats.to_dict().items():
            output += f"  {key}: {value}\n"
    
    # Write output
    if options.output_file:
        try:
            with open(options.output_file, 'w') as f:
                f.write(output)
        except Exception as e:
            logger.error(f"Error writing to output file: {e}")
            return 1
    else:
        print(output)
    
    # Determine exit code
    exit_code = 0
    if options.strict and issues:
        exit_code = 1
    elif any(i.severity == "error" for i in issues):
        exit_code = 1
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main()) 