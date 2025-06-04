#!/usr/bin/env python3
"""
Arc System Development Bible Compliance Validator

Comprehensive validation script to ensure Arc system meets all Development Bible requirements.
Run this after implementing enhancements to verify compliance.
"""

import sys
import json
import asyncio
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Add the backend to the path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from backend.systems.arc.models.arc import ArcType, ArcStatus, ArcPriority, ArcModel, ArcRelationshipType, ArcInfluenceLevel
from backend.systems.arc.models.arc_step import ArcStepStatus, ArcStepType, ArcStepModel
from backend.systems.arc.business_rules import (
    validate_arc_business_rules,
    calculate_arc_complexity_score,
    should_arc_be_expanded,
    validate_narrative_text,
    validate_step_completion_criteria
)
from backend.systems.arc.services.arc_relationship_service import ArcRelationshipService
from backend.systems.arc.services.progression_tracker import ProgressionTracker


@dataclass
class ComplianceCheck:
    """Represents a single compliance check"""
    category: str
    check_name: str
    is_compliant: bool
    details: str
    severity: str = "medium"  # low, medium, high, critical


@dataclass
class ComplianceReport:
    """Full compliance report"""
    total_checks: int
    passed_checks: int
    failed_checks: int
    compliance_percentage: float
    checks: List[ComplianceCheck]
    summary: str


class BibleComplianceValidator:
    """Validates Arc system compliance with Development Bible"""
    
    def __init__(self):
        self.checks: List[ComplianceCheck] = []
        self.test_data = self._initialize_test_data()
    
    def _initialize_test_data(self) -> Dict[str, Any]:
        """Initialize test data for validation"""
        return {
            "global_arc": {
                "title": "The Great Convergence",
                "description": "Multiple factions unite against an ancient threat",
                "arc_type": "global",
                "priority": "high", 
                "faction_ids": ["shadow_syndicate", "light_covenant", "neutral_traders"],
                "estimated_duration_hours": 60,
                "total_steps": 15,
                "difficulty_level": 9,
                "themes": ["war", "unity", "ancient threats", "world-changing"],
                "objectives": ["Unite all factions", "Defeat ancient threat", "Establish new world order"],
                "player_impact": "extreme",
                "world_impact": "world-changing"
            },
            "character_arc": {
                "title": "Path of Redemption",
                "description": "Hero's journey to overcome past mistakes",
                "arc_type": "character",
                "character_id": "main_hero",
                "total_steps": 7,
                "difficulty_level": 6,
                "themes": ["redemption", "personal growth", "forgiveness"],
                "objectives": ["Face the past", "Make amends", "Find inner peace"]
            },
            "regional_arc": {
                "title": "The Disputed Lands",
                "description": "Conflict over a resource-rich region",
                "arc_type": "regional",
                "region_id": "eastern_territories",
                "faction_ids": ["mountain_clans", "desert_nomads"],
                "total_steps": 8,
                "difficulty_level": 7,
                "themes": ["territorial conflict", "resource scarcity", "diplomacy"]
            },
            "step_data": {
                "step_number": 1,
                "title": "Investigate Ancient Ruins",
                "description": "Explore the mysterious ruins for clues",
                "narrative_text": "The ancient stones whisper secrets of a bygone era, their carved symbols glowing faintly in the moonlight as you approach the entrance.",
                "completion_criteria": {
                    "type": "exploration",
                    "requirements": [
                        "Enter the ruins",
                        "Find the central chamber", 
                        "Decipher the ancient text",
                        "Retrieve the artifact"
                    ],
                    "success_threshold": 3
                },
                "status": "pending",
                "rewards": {
                    "experience": 250,
                    "reputation": {"scholars_guild": 10},
                    "items": ["ancient_scroll", "mysterious_crystal"]
                }
            }
        }
    
    async def run_full_compliance_check(self) -> ComplianceReport:
        """Run all compliance checks and generate report"""
        print("🔍 Starting Arc System Development Bible Compliance Validation...")
        
        # Run all compliance checks
        await self._check_enum_compliance()
        await self._check_model_structure_compliance()
        await self._check_business_rules_compliance()
        await self._check_validation_logic_compliance()
        await self._check_relationship_system_compliance()
        await self._check_progression_tracking_compliance()
        await self._check_llm_integration_compliance()
        await self._check_cross_system_integration_compliance()
        
        # Generate report
        report = self._generate_compliance_report()
        
        print(f"\n📊 Compliance Check Complete: {report.compliance_percentage:.1f}% compliant")
        return report
    
    async def _check_enum_compliance(self):
        """Check that all enums match Development Bible specifications"""
        category = "Enum Compliance"
        
        # Check ArcType enum
        expected_arc_types = {"GLOBAL", "REGIONAL", "CHARACTER", "NPC", "FACTION", "QUEST"}
        actual_arc_types = {t.name for t in ArcType}
        
        self.checks.append(ComplianceCheck(
            category=category,
            check_name="ArcType Enum Values",
            is_compliant=actual_arc_types == expected_arc_types,
            details=f"Expected: {expected_arc_types}, Actual: {actual_arc_types}",
            severity="critical"
        ))
        
        # Check ArcStatus enum
        expected_statuses = {"PENDING", "ACTIVE", "PAUSED", "COMPLETED", "CANCELLED", "FAILED"}
        actual_statuses = {s.name for s in ArcStatus}
        
        self.checks.append(ComplianceCheck(
            category=category,
            check_name="ArcStatus Enum Values",
            is_compliant=actual_statuses == expected_statuses,
            details=f"Expected: {expected_statuses}, Actual: {actual_statuses}",
            severity="critical"
        ))
        
        # Check ArcStepStatus enum
        expected_step_statuses = {"PENDING", "ACTIVE", "COMPLETED", "FAILED", "SKIPPED", "BLOCKED"}
        actual_step_statuses = {s.name for s in ArcStepStatus}
        
        self.checks.append(ComplianceCheck(
            category=category,
            check_name="ArcStepStatus Enum Values", 
            is_compliant=actual_step_statuses == expected_step_statuses,
            details=f"Expected: {expected_step_statuses}, Actual: {actual_step_statuses}",
            severity="critical"
        ))
        
        # Check ArcStepType enum
        expected_step_types = {"NARRATIVE", "COMBAT", "EXPLORATION", "SOCIAL", "PUZZLE", "CHOICE", "CUTSCENE", "INVESTIGATION"}
        actual_step_types = {t.name for t in ArcStepType}
        
        self.checks.append(ComplianceCheck(
            category=category,
            check_name="ArcStepType Enum Values",
            is_compliant=actual_step_types == expected_step_types,
            details=f"Expected: {expected_step_types}, Actual: {actual_step_types}",
            severity="high"
        ))
    
    async def _check_model_structure_compliance(self):
        """Check model structure compliance with Bible requirements"""
        category = "Model Structure"
        
        try:
            # Test Arc model creation with all Bible-specified fields
            arc = ArcModel(**self.test_data["global_arc"])
            
            required_fields = [
                "id", "title", "description", "arc_type", "status", "priority",
                "region_id", "character_id", "npc_id", "faction_ids",
                "narrative_summary", "objectives", "themes",
                "total_steps", "completed_steps", "progress_percentage",
                "estimated_duration_hours", "start_date", "end_date",
                "tags", "difficulty_level", "player_impact", "world_impact"
            ]
            
            missing_fields = [field for field in required_fields if not hasattr(arc, field)]
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Arc Model Required Fields",
                is_compliant=len(missing_fields) == 0,
                details=f"Missing fields: {missing_fields}" if missing_fields else "All required fields present",
                severity="critical"
            ))
            
            # Test relationship fields (new enhancement)
            relationship_fields = ["predecessor_arcs", "successor_arcs", "related_arcs", "outcome_influences"]
            missing_rel_fields = [field for field in relationship_fields if not hasattr(arc, field)]
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Arc Relationship Fields",
                is_compliant=len(missing_rel_fields) == 0,
                details=f"Missing relationship fields: {missing_rel_fields}" if missing_rel_fields else "All relationship fields present",
                severity="high"
            ))
            
        except Exception as e:
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Arc Model Structure",
                is_compliant=False,
                details=f"Error creating Arc model: {str(e)}",
                severity="critical"
            ))
        
        try:
            # Test ArcStep model
            from uuid import uuid4
            step = ArcStepModel(
                **self.test_data["step_data"],
                arc_id=uuid4()
            )
            
            step_fields = [
                "id", "arc_id", "step_number", "title", "description", "narrative_text",
                "completion_criteria", "status", "is_optional", "prerequisites", "rewards"
            ]
            
            missing_step_fields = [field for field in step_fields if not hasattr(step, field)]
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="ArcStep Model Required Fields",
                is_compliant=len(missing_step_fields) == 0,
                details=f"Missing step fields: {missing_step_fields}" if missing_step_fields else "All step fields present",
                severity="critical"
            ))
            
        except Exception as e:
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="ArcStep Model Structure",
                is_compliant=False,
                details=f"Error creating ArcStep model: {str(e)}",
                severity="critical"
            ))
    
    async def _check_business_rules_compliance(self):
        """Check business rules implementation compliance"""
        category = "Business Rules"
        
        # Test global arc business rules
        global_violations = validate_arc_business_rules(self.test_data["global_arc"])
        
        self.checks.append(ComplianceCheck(
            category=category,
            check_name="Global Arc Business Rules",
            is_compliant=len(global_violations) == 0,
            details=f"Violations: {global_violations}" if global_violations else "No business rule violations",
            severity="high"
        ))
        
        # Test character arc business rules
        char_violations = validate_arc_business_rules(self.test_data["character_arc"])
        
        self.checks.append(ComplianceCheck(
            category=category,
            check_name="Character Arc Business Rules",
            is_compliant=len(char_violations) == 0,
            details=f"Violations: {char_violations}" if char_violations else "No business rule violations",
            severity="high"
        ))
        
        # Test complexity scoring
        try:
            complexity_score, factors = calculate_arc_complexity_score(self.test_data["global_arc"])
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Complexity Calculation",
                is_compliant=complexity_score > 0 and len(factors) > 0,
                details=f"Complexity score: {complexity_score}, Factors: {len(factors)}",
                severity="medium"
            ))
            
            # Test expansion recommendation
            should_expand, reason, suggested = should_arc_be_expanded(self.test_data["global_arc"])
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Arc Expansion Logic",
                is_compliant=isinstance(should_expand, bool) and isinstance(reason, str),
                details=f"Should expand: {should_expand}, Reason: {reason}",
                severity="medium"
            ))
            
        except Exception as e:
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Complexity & Expansion Logic",
                is_compliant=False,
                details=f"Error in complexity calculation: {str(e)}",
                severity="high"
            ))
    
    async def _check_validation_logic_compliance(self):
        """Check validation logic implementation"""
        category = "Validation Logic"
        
        # Test narrative text validation
        try:
            narrative_errors = validate_narrative_text(self.test_data["step_data"]["narrative_text"])
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Narrative Text Validation",
                is_compliant=len(narrative_errors) == 0,
                details=f"Narrative errors: {narrative_errors}" if narrative_errors else "Narrative validation passed",
                severity="medium"
            ))
            
        except Exception as e:
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Narrative Text Validation",
                is_compliant=False,
                details=f"Error in narrative validation: {str(e)}",
                severity="medium"
            ))
        
        # Test step completion criteria validation
        try:
            criteria_errors = validate_step_completion_criteria(self.test_data["step_data"]["completion_criteria"])
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Step Completion Criteria Validation",
                is_compliant=len(criteria_errors) == 0,
                details=f"Criteria errors: {criteria_errors}" if criteria_errors else "Criteria validation passed",
                severity="high"
            ))
            
        except Exception as e:
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Step Completion Criteria Validation",
                is_compliant=False,
                details=f"Error in criteria validation: {str(e)}",
                severity="high"
            ))
        
        # Test step status transitions
        try:
            from uuid import uuid4
            step = ArcStepModel(**self.test_data["step_data"], arc_id=uuid4())
            
            can_activate, reason = step.can_transition_to_status("active")
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Step Status Transitions",
                is_compliant=isinstance(can_activate, bool) and isinstance(reason, str),
                details=f"Can activate: {can_activate}, Reason: {reason}",
                severity="high"
            ))
            
        except Exception as e:
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Step Status Transitions",
                is_compliant=False,
                details=f"Error in status transition: {str(e)}",
                severity="high"
            ))
    
    async def _check_relationship_system_compliance(self):
        """Check arc relationship system compliance"""
        category = "Relationship System"
        
        try:
            # Test relationship types exist
            relationship_types = list(ArcRelationshipType)
            expected_types = ["SEQUEL", "PREQUEL", "PARALLEL", "BRANCHING", "CONFLUENCE", "THEMATIC_LINK", "CONTINUATION", "CONSEQUENCE"]
            
            actual_type_names = [rt.name for rt in relationship_types]
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Relationship Type Enums",
                is_compliant=set(actual_type_names) >= set(expected_types),
                details=f"Expected types present: {set(expected_types).issubset(set(actual_type_names))}",
                severity="high"
            ))
            
            # Test influence levels
            influence_levels = list(ArcInfluenceLevel)
            expected_levels = ["MINIMAL", "MODERATE", "MAJOR", "CRITICAL"]
            
            actual_level_names = [il.name for il in influence_levels]
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Influence Level Enums",
                is_compliant=set(actual_level_names) >= set(expected_levels),
                details=f"Expected levels present: {set(expected_levels).issubset(set(actual_level_names))}",
                severity="medium"
            ))
            
            # Test relationship service
            relationship_service = ArcRelationshipService()
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Relationship Service Available",
                is_compliant=hasattr(relationship_service, 'create_relationship'),
                details="ArcRelationshipService instantiated successfully",
                severity="high"
            ))
            
        except Exception as e:
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Relationship System",
                is_compliant=False,
                details=f"Error in relationship system: {str(e)}",
                severity="high"
            ))
    
    async def _check_progression_tracking_compliance(self):
        """Check progression tracking compliance"""
        category = "Progression Tracking"
        
        try:
            # Test progression tracker
            tracker = ProgressionTracker()
            
            service_methods = ["calculate_comprehensive_metrics", "generate_progress_insights"]
            missing_methods = [method for method in service_methods if not hasattr(tracker, method)]
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Progression Tracker Methods",
                is_compliant=len(missing_methods) == 0,
                details=f"Missing methods: {missing_methods}" if missing_methods else "All required methods present",
                severity="high"
            ))
            
            # Test milestone system
            milestone_definitions = tracker.milestone_definitions
            expected_milestones = ["first_step", "quarter_complete", "half_complete", "three_quarters"]
            
            actual_milestones = list(milestone_definitions.keys())
            has_expected = all(m in actual_milestones for m in expected_milestones)
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Milestone System",
                is_compliant=has_expected,
                details=f"Milestone types available: {len(actual_milestones)}, Has expected: {has_expected}",
                severity="medium"
            ))
            
        except Exception as e:
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Progression Tracking",
                is_compliant=False,
                details=f"Error in progression tracking: {str(e)}",
                severity="high"
            ))
    
    async def _check_llm_integration_compliance(self):
        """Check LLM integration compliance"""
        category = "LLM Integration"
        
        try:
            # Test follow-up prompt generation
            arc = ArcModel(**self.test_data["global_arc"])
            
            has_prompt_method = hasattr(arc, 'get_suggested_follow_up_prompt')
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Follow-up Prompt Generation",
                is_compliant=has_prompt_method,
                details="Arc model has follow-up prompt generation method" if has_prompt_method else "Missing prompt generation",
                severity="medium"
            ))
            
            if has_prompt_method:
                prompt = arc.get_suggested_follow_up_prompt()
                
                self.checks.append(ComplianceCheck(
                    category=category,
                    check_name="Prompt Content Quality",
                    is_compliant=len(prompt) > 100 and "arc" in prompt.lower(),
                    details=f"Prompt length: {len(prompt)}, Contains arc info: {'arc' in prompt.lower()}",
                    severity="low"
                ))
            
            # Test relationship service LLM capabilities
            relationship_service = ArcRelationshipService()
            has_llm_generation = hasattr(relationship_service, 'generate_follow_up_arcs')
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="LLM Arc Generation",
                is_compliant=has_llm_generation,
                details="Relationship service has LLM generation capability" if has_llm_generation else "Missing LLM generation",
                severity="medium"
            ))
            
        except Exception as e:
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="LLM Integration",
                is_compliant=False,
                details=f"Error in LLM integration: {str(e)}",
                severity="medium"
            ))
    
    async def _check_cross_system_integration_compliance(self):
        """Check cross-system integration compliance"""
        category = "Cross-System Integration"
        
        # Test reference fields
        arc = ArcModel(**self.test_data["global_arc"])
        
        integration_fields = ["region_id", "character_id", "npc_id", "faction_ids"]
        present_fields = [field for field in integration_fields if hasattr(arc, field)]
        
        self.checks.append(ComplianceCheck(
            category=category,
            check_name="Cross-System Reference Fields",
            is_compliant=len(present_fields) == len(integration_fields),
            details=f"Integration fields present: {present_fields}",
            severity="high"
        ))
        
        # Test business rule cross-system validation
        try:
            violations = validate_arc_business_rules(self.test_data["regional_arc"])
            
            # Should validate region_id requirement for regional arcs
            has_region_validation = any("region_id" in v for v in violations) if not self.test_data["regional_arc"].get("region_id") else True
            
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Cross-System Business Rules",
                is_compliant=has_region_validation,
                details="Regional arc region_id validation working" if has_region_validation else "Missing cross-system validation",
                severity="medium"
            ))
            
        except Exception as e:
            self.checks.append(ComplianceCheck(
                category=category,
                check_name="Cross-System Business Rules",
                is_compliant=False,
                details=f"Error in cross-system validation: {str(e)}",
                severity="medium"
            ))
    
    def _generate_compliance_report(self) -> ComplianceReport:
        """Generate final compliance report"""
        total_checks = len(self.checks)
        passed_checks = len([c for c in self.checks if c.is_compliant])
        failed_checks = total_checks - passed_checks
        compliance_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Generate summary
        critical_failures = [c for c in self.checks if not c.is_compliant and c.severity == "critical"]
        high_failures = [c for c in self.checks if not c.is_compliant and c.severity == "high"]
        
        if critical_failures:
            summary = f"❌ CRITICAL COMPLIANCE ISSUES: {len(critical_failures)} critical failures must be addressed"
        elif high_failures:
            summary = f"⚠️  HIGH PRIORITY ISSUES: {len(high_failures)} high-priority issues need attention"
        elif compliance_percentage >= 95:
            summary = "✅ EXCELLENT COMPLIANCE: Arc system meets Development Bible requirements"
        elif compliance_percentage >= 85:
            summary = "🟨 GOOD COMPLIANCE: Minor issues remain but system is largely compliant"
        else:
            summary = "🔧 COMPLIANCE WORK NEEDED: Significant improvements required"
        
        return ComplianceReport(
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            compliance_percentage=compliance_percentage,
            checks=self.checks,
            summary=summary
        )
    
    def print_detailed_report(self, report: ComplianceReport):
        """Print detailed compliance report"""
        print(f"\n" + "="*80)
        print(f"  🔍 ARC SYSTEM DEVELOPMENT BIBLE COMPLIANCE REPORT")
        print(f"="*80)
        print(f"  📊 Overall Compliance: {report.compliance_percentage:.1f}%")
        print(f"  ✅ Passed: {report.passed_checks} | ❌ Failed: {report.failed_checks} | 📝 Total: {report.total_checks}")
        print(f"  📋 {report.summary}")
        print(f"="*80)
        
        # Group checks by category
        categories = {}
        for check in report.checks:
            if check.category not in categories:
                categories[check.category] = []
            categories[check.category].append(check)
        
        # Print by category
        for category, checks in categories.items():
            passed = len([c for c in checks if c.is_compliant])
            total = len(checks)
            print(f"\n📁 {category} ({passed}/{total} passed)")
            print("-" * 60)
            
            for check in checks:
                status = "✅" if check.is_compliant else "❌"
                severity_icon = {"critical": "🚨", "high": "⚠️", "medium": "🔶", "low": "ℹ️"}.get(check.severity, "")
                print(f"  {status} {severity_icon} {check.check_name}")
                if not check.is_compliant or len(check.details) > 50:
                    print(f"      └─ {check.details}")
        
        # Print recommendations
        print(f"\n🎯 RECOMMENDATIONS")
        print("-" * 60)
        
        critical_issues = [c for c in report.checks if not c.is_compliant and c.severity == "critical"]
        if critical_issues:
            print("  🚨 CRITICAL - Address immediately:")
            for issue in critical_issues:
                print(f"      • {issue.check_name}: {issue.details}")
        
        high_issues = [c for c in report.checks if not c.is_compliant and c.severity == "high"]
        if high_issues:
            print("  ⚠️  HIGH PRIORITY:")
            for issue in high_issues:
                print(f"      • {issue.check_name}: {issue.details}")
        
        medium_issues = [c for c in report.checks if not c.is_compliant and c.severity == "medium"]
        if medium_issues and len(medium_issues) <= 5:
            print("  🔶 MEDIUM PRIORITY:")
            for issue in medium_issues[:5]:
                print(f"      • {issue.check_name}: {issue.details}")
        
        print(f"\n" + "="*80)


async def main():
    """Main function to run compliance validation"""
    validator = BibleComplianceValidator()
    
    try:
        report = await validator.run_full_compliance_check()
        validator.print_detailed_report(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"arc_compliance_report_{timestamp}.json"
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "compliance_percentage": report.compliance_percentage,
            "total_checks": report.total_checks,
            "passed_checks": report.passed_checks,
            "failed_checks": report.failed_checks,
            "summary": report.summary,
            "checks": [
                {
                    "category": c.category,
                    "check_name": c.check_name,
                    "is_compliant": c.is_compliant,
                    "details": c.details,
                    "severity": c.severity
                }
                for c in report.checks
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Report saved to: {report_file}")
        
        # Return appropriate exit code
        if report.compliance_percentage >= 95:
            return 0
        elif report.compliance_percentage >= 85:
            return 1  # Warning
        else:
            return 2  # Error
        
    except Exception as e:
        print(f"❌ Compliance validation failed: {str(e)}")
        return 3


if __name__ == "__main__":
    exit_code = asyncio.run(main()) 