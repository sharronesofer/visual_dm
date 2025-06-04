"""
Intelligence Utility Functions

Contains technical utility functions and generators for intelligence operations.
Extracted from business logic to keep domain code pure.
"""

import random
from typing import List, Dict, Union
from uuid import UUID

from backend.systems.diplomacy.models.intelligence_models import (
    IntelligenceType, EspionageOperationType, InformationWarfareType
)


class IntelligenceCodeNameGenerator:
    """Generates code names for intelligence agents"""
    
    @staticmethod
    def generate_code_name() -> str:
        """Generate a random code name for an agent"""
        prefixes = ["Shadow", "Raven", "Ghost", "Phoenix", "Viper", "Falcon", "Wolf", "Fox"]
        suffixes = ["One", "Seven", "Alpha", "Beta", "Prime", "Zero", "Nine", "Six"]
        return f"{random.choice(prefixes)}-{random.choice(suffixes)}"


class IntelligenceCoverGenerator:
    """Generates cover identities for intelligence agents"""
    
    @staticmethod
    def generate_cover_identity(specialization: IntelligenceType) -> str:
        """Generate a cover identity based on specialization"""
        covers = {
            IntelligenceType.DIPLOMATIC_RECONNAISSANCE: "Embassy Cultural Attaché",
            IntelligenceType.ECONOMIC_INTELLIGENCE: "Trade Representative",
            IntelligenceType.MILITARY_INTELLIGENCE: "Defense Contractor",
            IntelligenceType.LEADERSHIP_INTELLIGENCE: "Journalist",
            IntelligenceType.TREATY_INTELLIGENCE: "International Law Scholar"
        }
        return covers.get(specialization, "Business Consultant")


class IntelligenceOperationNameGenerator:
    """Generates names for intelligence operations"""
    
    @staticmethod
    def generate_operation_name(operation_type: Union[IntelligenceType, EspionageOperationType]) -> str:
        """Generate a codename for an intelligence operation"""
        prefixes = ["Operation", "Project", "Mission"]
        return f"{random.choice(prefixes)} {IntelligenceCodeNameGenerator.generate_code_name()}"


class IntelligenceCalculations:
    """Calculations for intelligence operations"""
    
    @staticmethod
    def calculate_base_success_probability(operation_type: Union[IntelligenceType, EspionageOperationType]) -> int:
        """Calculate base success probability based on operation type"""
        base_probabilities = {
            IntelligenceType.DIPLOMATIC_RECONNAISSANCE: 70,
            IntelligenceType.ECONOMIC_INTELLIGENCE: 60,
            IntelligenceType.MILITARY_INTELLIGENCE: 45,
            IntelligenceType.LEADERSHIP_INTELLIGENCE: 40,
            IntelligenceType.TREATY_INTELLIGENCE: 65,
            EspionageOperationType.INFILTRATION: 35,
            EspionageOperationType.SABOTAGE: 30,
            EspionageOperationType.ASSASSINATION: 20,
            EspionageOperationType.DATA_THEFT: 55,
            EspionageOperationType.COUNTER_ESPIONAGE: 50
        }
        return base_probabilities.get(operation_type, 50)
    
    @staticmethod
    def calculate_base_detection_risk(operation_type: Union[IntelligenceType, EspionageOperationType]) -> int:
        """Calculate base detection risk based on operation type"""
        base_risks = {
            IntelligenceType.DIPLOMATIC_RECONNAISSANCE: 20,
            IntelligenceType.ECONOMIC_INTELLIGENCE: 25,
            IntelligenceType.MILITARY_INTELLIGENCE: 40,
            IntelligenceType.LEADERSHIP_INTELLIGENCE: 35,
            IntelligenceType.TREATY_INTELLIGENCE: 15,
            EspionageOperationType.INFILTRATION: 45,
            EspionageOperationType.SABOTAGE: 60,
            EspionageOperationType.ASSASSINATION: 80,
            EspionageOperationType.DATA_THEFT: 35,
            EspionageOperationType.COUNTER_ESPIONAGE: 30
        }
        return base_risks.get(operation_type, 35)
    
    @staticmethod
    def calculate_political_risk(operation_type: Union[IntelligenceType, EspionageOperationType]) -> int:
        """Calculate political risk based on operation type"""
        political_risks = {
            IntelligenceType.DIPLOMATIC_RECONNAISSANCE: 10,
            IntelligenceType.ECONOMIC_INTELLIGENCE: 15,
            IntelligenceType.MILITARY_INTELLIGENCE: 25,
            IntelligenceType.LEADERSHIP_INTELLIGENCE: 20,
            IntelligenceType.TREATY_INTELLIGENCE: 30,
            EspionageOperationType.INFILTRATION: 40,
            EspionageOperationType.SABOTAGE: 70,
            EspionageOperationType.ASSASSINATION: 90,
            EspionageOperationType.DATA_THEFT: 35,
            EspionageOperationType.COUNTER_ESPIONAGE: 20
        }
        return political_risks.get(operation_type, 25)
    
    @staticmethod
    def calculate_detection_probability(operation, defending_faction: UUID) -> int:
        """Calculate probability of detecting a hostile operation"""
        base_detection = 30
        
        # Adjust based on operation type
        if hasattr(operation, 'operation_type'):
            if operation.operation_type in [EspionageOperationType.SABOTAGE, EspionageOperationType.ASSASSINATION]:
                base_detection += 20
            elif operation.operation_type == EspionageOperationType.INFILTRATION:
                base_detection += 10
        
        # Add randomness
        base_detection += random.randint(-10, 10)
        
        return max(0, min(100, base_detection))
    
    @staticmethod
    def calculate_campaign_effectiveness(campaign) -> int:
        """Calculate information warfare campaign effectiveness"""
        base_effectiveness = 50
        
        # Adjust based on campaign type
        if hasattr(campaign, 'campaign_type'):
            if campaign.campaign_type == InformationWarfareType.PROPAGANDA:
                base_effectiveness += 10
            elif campaign.campaign_type == InformationWarfareType.DISINFORMATION:
                base_effectiveness += 15
            elif campaign.campaign_type == InformationWarfareType.COUNTER_NARRATIVE:
                base_effectiveness += 5
        
        # Add some randomness for realism
        base_effectiveness += random.randint(-15, 15)
        
        return max(0, min(100, base_effectiveness))
    
    @staticmethod
    def calculate_reputation_impacts(campaign, effectiveness: int) -> Dict[str, int]:
        """Calculate reputation impacts from information warfare"""
        impacts = {}
        
        if hasattr(campaign, 'target_factions') and campaign.target_factions:
            for target_faction in campaign.target_factions:
                # Negative impact on targets
                impact = -(effectiveness // 2)
                impacts[str(target_faction)] = impact
        
        # Positive impact on executing faction (smaller)
        if hasattr(campaign, 'executing_faction'):
            impacts[str(campaign.executing_faction)] = effectiveness // 4
        
        return impacts


class IntelligenceContentGenerators:
    """Generates content for intelligence operations"""
    
    @staticmethod
    def generate_intelligence_content(intel_type: IntelligenceType, target_faction: UUID) -> str:
        """Generate content for intelligence reports"""
        content_templates = {
            IntelligenceType.DIPLOMATIC_RECONNAISSANCE: "Diplomatic activities and alliance discussions observed.",
            IntelligenceType.ECONOMIC_INTELLIGENCE: "Economic capabilities and trade relationships analyzed.",
            IntelligenceType.MILITARY_INTELLIGENCE: "Military strength and strategic positions assessed.",
            IntelligenceType.LEADERSHIP_INTELLIGENCE: "Leadership structure and decision-making patterns studied.",
            IntelligenceType.TREATY_INTELLIGENCE: "Treaty compliance and negotiation strategies reviewed."
        }
        
        base_content = content_templates.get(intel_type, "General intelligence gathered.")
        return f"{base_content} Target: {target_faction}"
    
    @staticmethod
    def generate_security_measures() -> List[str]:
        """Generate security measures for counter-intelligence"""
        measures = [
            "Enhanced communication encryption",
            "Regular security sweeps",
            "Personnel background verification",
            "Access control monitoring",
            "Counter-surveillance protocols"
        ]
        return random.sample(measures, random.randint(2, 4))
    
    @staticmethod
    def generate_surveillance_activities() -> List[str]:
        """Generate surveillance activities for counter-intelligence"""
        activities = [
            "Digital communications monitoring",
            "Physical surveillance of key locations",
            "Network traffic analysis",
            "Personnel movement tracking",
            "Document access auditing"
        ]
        return random.sample(activities, random.randint(2, 3))
    
    @staticmethod
    def generate_narratives(campaign_type: InformationWarfareType) -> List[str]:
        """Generate narratives for information warfare campaigns"""
        narratives_by_type = {
            InformationWarfareType.PROPAGANDA: [
                "Highlighting faction achievements and capabilities",
                "Promoting faction ideology and values",
                "Demonstrating faction strength and resolve"
            ],
            InformationWarfareType.DISINFORMATION: [
                "Spreading false information about enemy capabilities",
                "Creating confusion about enemy intentions",
                "Undermining trust in enemy leadership"
            ],
            InformationWarfareType.COUNTER_NARRATIVE: [
                "Refuting false claims made by enemies",
                "Providing factual corrections to misinformation",
                "Clarifying faction positions and policies"
            ]
        }
        
        narratives = narratives_by_type.get(campaign_type, ["Generic information campaign"])
        return random.sample(narratives, random.randint(1, len(narratives)))
    
    @staticmethod
    def generate_media_channels() -> List[str]:
        """Generate media channels for information campaigns"""
        channels = [
            "Public communications networks",
            "Diplomatic channels",
            "Trade communications",
            "Cultural exchange programs",
            "Educational institutions"
        ]
        return random.sample(channels, random.randint(2, 4))
    
    @staticmethod
    def generate_target_audiences(campaign_type: InformationWarfareType) -> List[str]:
        """Generate target audiences for information campaigns"""
        audiences_by_type = {
            InformationWarfareType.PROPAGANDA: [
                "General population",
                "Military personnel",
                "Government officials",
                "Business leaders"
            ],
            InformationWarfareType.DISINFORMATION: [
                "Enemy population",
                "Neutral factions",
                "International observers"
            ],
            InformationWarfareType.COUNTER_NARRATIVE: [
                "Allied populations",
                "International community",
                "Neutral observers"
            ]
        }
        
        audiences = audiences_by_type.get(campaign_type, ["General audience"])
        return random.sample(audiences, random.randint(1, len(audiences)))


class IntelligenceAnalysis:
    """Analysis functions for intelligence operations"""
    
    @staticmethod
    def analyze_reports_for_insights(report_ids: List[UUID]) -> List[str]:
        """Analyze multiple reports to generate insights"""
        # This is a simplified version - real implementation would analyze actual report content
        insights = [
            "Pattern of increased military activity detected",
            "Economic vulnerabilities identified",
            "Diplomatic shifts observed",
            "Leadership changes noted",
            "Strategic planning indicators found"
        ]
        
        # Return a subset based on number of reports
        num_insights = min(len(report_ids), len(insights))
        return random.sample(insights, num_insights)
    
    @staticmethod
    def calculate_assessment_confidence(report_ids: List[UUID]) -> int:
        """Calculate confidence level for intelligence assessment"""
        # Base confidence on number of reports
        base_confidence = min(80, 30 + (len(report_ids) * 10))
        
        # Add some variance
        confidence = base_confidence + random.randint(-10, 10)
        
        return max(20, min(95, confidence)) 