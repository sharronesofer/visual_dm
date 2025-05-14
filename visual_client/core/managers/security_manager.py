"""
Security management system with auditing and vulnerability scanning.
"""

import logging
import subprocess
import json
import os
import sys
import time
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

@dataclass
class SecurityIssue:
    """Security issue information."""
    id: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str
    description: str
    location: str
    timestamp: datetime
    status: str  # 'open', 'fixed', 'false_positive'
    details: Optional[Dict[str, Any]] = None

class SecurityManager:
    """Manages security auditing and vulnerability scanning."""
    
    def __init__(
        self,
        scan_interval: int = 24 * 60 * 60,  # 24 hours
        report_dir: str = "security_reports",
        tools: Optional[Dict[str, str]] = None
    ):
        """Initialize the security manager.
        
        Args:
            scan_interval: Interval for security scans in seconds
            report_dir: Directory for security reports
            tools: Security scanning tools configuration
        """
        try:
            self.scan_interval = scan_interval
            self.report_dir = Path(report_dir)
            self.report_dir.mkdir(parents=True, exist_ok=True)
            
            # Default security tools
            self.tools = tools or {
                "dependency_scanner": "safety",
                "code_scanner": "bandit",
                "vulnerability_scanner": "zap"
            }
            
            self.issues: Dict[str, SecurityIssue] = {}
            self.scan_thread = None
            self.running = False
            
            logger.info("Security manager initialized")
            
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def scan_dependencies(self) -> List[SecurityIssue]:
        """Scan dependencies for vulnerabilities.
        
        Returns:
            List of security issues
        """
        try:
            issues = []
            
            # Run dependency scanner
            result = subprocess.run(
                [sys.executable, "-m", self.tools["dependency_scanner"], "check"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Parse issues
                for line in result.stdout.splitlines():
                    if "Vulnerability" in line:
                        parts = line.split("|")
                        if len(parts) >= 3:
                            issue = SecurityIssue(
                                id=f"dep-{len(issues)}",
                                severity="high",
                                category="dependency",
                                description=parts[1].strip(),
                                location=parts[0].strip(),
                                timestamp=datetime.now(),
                                status="open",
                                details={"output": line}
                            )
                            issues.append(issue)
                            
            return issues
            
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "scan_dependencies",
                e,
                ErrorSeverity.ERROR
            )
            return []
            
    def scan_code(self) -> List[SecurityIssue]:
        """Scan code for security issues.
        
        Returns:
            List of security issues
        """
        try:
            issues = []
            
            # Run code scanner
            result = subprocess.run(
                [sys.executable, "-m", self.tools["code_scanner"], "-r", "."],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Parse issues
                for line in result.stdout.splitlines():
                    if "Issue" in line:
                        parts = line.split(":")
                        if len(parts) >= 3:
                            issue = SecurityIssue(
                                id=f"code-{len(issues)}",
                                severity="medium",
                                category="code",
                                description=parts[2].strip(),
                                location=parts[0].strip(),
                                timestamp=datetime.now(),
                                status="open",
                                details={"output": line}
                            )
                            issues.append(issue)
                            
            return issues
            
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "scan_code",
                e,
                ErrorSeverity.ERROR
            )
            return []
            
    def scan_vulnerabilities(self) -> List[SecurityIssue]:
        """Scan for general vulnerabilities.
        
        Returns:
            List of security issues
        """
        try:
            issues = []
            
            # Run vulnerability scanner
            result = subprocess.run(
                [self.tools["vulnerability_scanner"], "-t", "http://localhost:8000"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Parse issues
                for line in result.stdout.splitlines():
                    if "Alert" in line:
                        parts = line.split("|")
                        if len(parts) >= 3:
                            issue = SecurityIssue(
                                id=f"vuln-{len(issues)}",
                                severity=parts[1].strip().lower(),
                                category="vulnerability",
                                description=parts[2].strip(),
                                location="http://localhost:8000",
                                timestamp=datetime.now(),
                                status="open",
                                details={"output": line}
                            )
                            issues.append(issue)
                            
            return issues
            
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "scan_vulnerabilities",
                e,
                ErrorSeverity.ERROR
            )
            return []
            
    def run_scan(self) -> None:
        """Run all security scans."""
        try:
            # Run all scanners
            dependency_issues = self.scan_dependencies()
            code_issues = self.scan_code()
            vulnerability_issues = self.scan_vulnerabilities()
            
            # Combine all issues
            all_issues = dependency_issues + code_issues + vulnerability_issues
            
            # Update issues dictionary
            for issue in all_issues:
                self.issues[issue.id] = issue
                
            # Generate report
            self._generate_report()
            
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "run_scan",
                e,
                ErrorSeverity.ERROR
            )
            
    def _generate_report(self) -> None:
        """Generate security report."""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "issues": [
                    {
                        "id": issue.id,
                        "severity": issue.severity,
                        "category": issue.category,
                        "description": issue.description,
                        "location": issue.location,
                        "status": issue.status,
                        "details": issue.details
                    }
                    for issue in self.issues.values()
                ]
            }
            
            # Save report
            report_path = self.report_dir / f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
                
            logger.info(f"Security report generated: {report_path}")
            
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "_generate_report",
                e,
                ErrorSeverity.ERROR
            )
            
    def start(self) -> None:
        """Start the security manager."""
        try:
            if self.running:
                return
                
            self.running = True
            self.scan_thread = threading.Thread(
                target=self._scan_loop,
                daemon=True
            )
            self.scan_thread.start()
            
            logger.info("Security manager started")
            
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "start",
                e,
                ErrorSeverity.ERROR
            )
            
    def stop(self) -> None:
        """Stop the security manager."""
        try:
            self.running = False
            if self.scan_thread:
                self.scan_thread.join()
                
            logger.info("Security manager stopped")
            
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "stop",
                e,
                ErrorSeverity.ERROR
            )
            
    def _scan_loop(self) -> None:
        """Run security scans in a loop."""
        try:
            while self.running:
                self.run_scan()
                time.sleep(self.scan_interval)
                
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "_scan_loop",
                e,
                ErrorSeverity.ERROR
            )
            
    def get_issues(
        self,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[SecurityIssue]:
        """Get security issues with optional filtering.
        
        Args:
            severity: Filter by severity
            category: Filter by category
            status: Filter by status
            
        Returns:
            List of filtered security issues
        """
        try:
            issues = list(self.issues.values())
            
            if severity:
                issues = [i for i in issues if i.severity == severity]
                
            if category:
                issues = [i for i in issues if i.category == category]
                
            if status:
                issues = [i for i in issues if i.status == status]
                
            return issues
            
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "get_issues",
                e,
                ErrorSeverity.ERROR
            )
            return []
            
    def update_issue_status(self, issue_id: str, status: str) -> None:
        """Update issue status.
        
        Args:
            issue_id: Issue ID
            status: New status
        """
        try:
            if issue_id in self.issues:
                self.issues[issue_id].status = status
                
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "update_issue_status",
                e,
                ErrorSeverity.ERROR
            )
            
    def cleanup(self) -> None:
        """Clean up security resources."""
        try:
            self.stop()
            self.issues.clear()
            
            logger.info("Security manager cleaned up")
            
        except Exception as e:
            handle_component_error(
                "SecurityManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            ) 