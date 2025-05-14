#!/usr/bin/env python3
"""
Dependency management script for Visual DM.
Provides utilities for auditing, updating, and maintaining dependencies.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DependencyManager:
    """Manages project dependencies."""
    
    def __init__(self):
        self.requirements_dir = Path("requirements")
        self.venv_path = Path("venv_py311")
    
    def run_command(self, command: List[str]) -> str:
        """Run a shell command and return its output."""
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            sys.exit(1)
    
    def get_installed_packages(self) -> Dict[str, str]:
        """Get currently installed packages and their versions."""
        output = self.run_command([sys.executable, "-m", "pip", "freeze"])
        packages = {}
        for line in output.splitlines():
            if "==" in line:
                name, version = line.split("==")
                packages[name] = version
        return packages
    
    def get_dependency_tree(self) -> str:
        """Get the dependency tree using pipdeptree."""
        return self.run_command([sys.executable, "-m", "pipdeptree"])
    
    def check_security(self) -> None:
        """Check for known security vulnerabilities."""
        logger.info("Checking for security vulnerabilities...")
        self.run_command([sys.executable, "-m", "safety", "check"])
    
    def update_dependencies(self) -> None:
        """Update all dependencies to their latest versions."""
        logger.info("Updating dependencies...")
        self.run_command([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements/base.txt"])
        self.run_command([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements/dev.txt"])
    
    def audit_dependencies(self) -> None:
        """Perform a comprehensive dependency audit."""
        logger.info("Starting dependency audit...")
        
        # Get installed packages
        installed = self.get_installed_packages()
        logger.info(f"Found {len(installed)} installed packages")
        
        # Get dependency tree
        tree = self.get_dependency_tree()
        logger.info("Dependency tree generated")
        
        # Check for security issues
        self.check_security()
        
        # Save audit report
        report = {
            "installed_packages": installed,
            "dependency_tree": tree
        }
        
        with open("dependency_audit.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info("Dependency audit completed. Report saved to dependency_audit.json")
    
    def clean_unused(self) -> None:
        """Remove unused dependencies."""
        logger.info("Cleaning unused dependencies...")
        self.run_command([sys.executable, "-m", "pip", "autoremove", "-y"])
    
    def main(self) -> None:
        """Main entry point for the script."""
        import argparse
        
        parser = argparse.ArgumentParser(description="Manage project dependencies")
        parser.add_argument(
            "action",
            choices=["audit", "update", "clean", "security"],
            help="Action to perform"
        )
        
        args = parser.parse_args()
        
        if args.action == "audit":
            self.audit_dependencies()
        elif args.action == "update":
            self.update_dependencies()
        elif args.action == "clean":
            self.clean_unused()
        elif args.action == "security":
            self.check_security()

if __name__ == "__main__":
    manager = DependencyManager()
    manager.main() 