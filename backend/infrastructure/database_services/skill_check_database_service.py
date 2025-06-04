"""
Skill Check Database Service
---------------------------
Service for logging skill checks, tracking progression, and providing analytics
for the noncombat skills system.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from collections import defaultdict

from backend.systems.character.models.skill_check_history import (
    SkillCheckHistory, CharacterSkillProgression, SocialRelationship,
    SkillCheckSession, SkillSynergy, EnvironmentalImpact
)
from backend.systems.character.models.character import Character
from backend.systems.character.services.skill_check_service import SkillCheckResult
from backend.infrastructure.config_loaders.skill_config_loader import skill_config

logger = logging.getLogger(__name__)

class SkillCheckDatabaseService:
    """Service for database operations related to skill checks."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
    # === SKILL CHECK LOGGING ===
    
    def log_skill_check(
        self,
        character: Character,
        skill_check_result: SkillCheckResult,
        environmental_conditions: List[str] = None,
        session_id: Optional[str] = None,
        roll_duration_ms: Optional[int] = None
    ) -> str:
        """
        Log a skill check to the database for analytics and progression tracking.
        
        Args:
            character: Character who made the check
            skill_check_result: Result of the skill check
            environmental_conditions: Environmental conditions that applied
            session_id: ID of the current gameplay session
            roll_duration_ms: Time taken to make the decision
            
        Returns:
            UUID of the created skill check history record
        """
        if environmental_conditions is None:
            environmental_conditions = []
        
        # Determine difficulty category
        difficulty_category = None
        if skill_check_result.dc:
            dc = skill_check_result.dc
            if dc <= 10:
                difficulty_category = 'easy'
            elif dc <= 15:
                difficulty_category = 'medium'
            elif dc <= 20:
                difficulty_category = 'hard'
            elif dc <= 25:
                difficulty_category = 'very_hard'
            else:
                difficulty_category = 'nearly_impossible'
        
        # Create skill check history record
        skill_check_history = SkillCheckHistory(
            character_id=character.uuid,
            session_id=session_id,
            skill_name=skill_check_result.skill_name,
            dc=skill_check_result.dc,
            base_roll=skill_check_result.base_roll,
            skill_modifier=skill_check_result.skill_modifier,
            final_modifiers=skill_check_result.final_modifiers,
            total_roll=skill_check_result.total_roll,
            success=skill_check_result.success,
            degree_of_success=skill_check_result.degree_of_success,
            critical_success=skill_check_result.critical_success,
            critical_failure=skill_check_result.critical_failure,
            advantage_type=skill_check_result.advantage_type.value,
            description=skill_check_result.description,
            environmental_conditions=environmental_conditions,
            character_level=character.level,
            roll_duration_ms=roll_duration_ms,
            difficulty_category=difficulty_category,
            skill_check_type='standard'  # Default, could be extended
        )
        
        self.db.add(skill_check_history)
        self.db.flush()  # Get the ID
        
        # Log environmental impacts
        self._log_environmental_impacts(skill_check_history.id, environmental_conditions, skill_check_result)
        
        # Update character progression
        self._update_character_progression(character, skill_check_result)
        
        # Log skill synergies if any
        self._log_skill_synergies(character, skill_check_history.id, skill_check_result)
        
        self.db.commit()
        
        logger.info(f"Logged skill check: {character.name} - {skill_check_result.skill_name} "
                   f"({skill_check_result.total_roll} vs DC {skill_check_result.dc})")
        
        return str(skill_check_history.id)
    
    def _log_environmental_impacts(
        self,
        skill_check_id: str,
        environmental_conditions: List[str],
        skill_check_result: SkillCheckResult
    ) -> None:
        """Log environmental impact details."""
        env_modifiers = skill_config.get_environmental_modifiers()
        
        for condition in environmental_conditions:
            # Find the modifier value and category
            modifier_value = 0
            condition_category = 'unknown'
            
            for category, modifiers in env_modifiers.items():
                if condition in modifiers:
                    modifier_value = modifiers[condition]
                    condition_category = category
                    break
            
            # Calculate impact significance
            impact_significance = 'none'
            would_succeed_without = None
            would_fail_without = None
            
            if skill_check_result.dc and modifier_value != 0:
                roll_without_condition = skill_check_result.total_roll - modifier_value
                would_succeed_without = roll_without_condition >= skill_check_result.dc
                would_fail_without = roll_without_condition < skill_check_result.dc
                
                # Determine significance
                if abs(modifier_value) >= 5:
                    impact_significance = 'major'
                elif abs(modifier_value) >= 3:
                    impact_significance = 'minor'
                
                # Critical impact if it changed the outcome
                if (skill_check_result.success and would_fail_without) or \
                   (not skill_check_result.success and would_succeed_without):
                    impact_significance = 'critical'
            
            environmental_impact = EnvironmentalImpact(
                skill_check_id=skill_check_id,
                condition_name=condition,
                modifier_value=modifier_value,
                condition_category=condition_category,
                would_have_succeeded_without=would_succeed_without,
                would_have_failed_without=would_fail_without,
                impact_significance=impact_significance
            )
            
            self.db.add(environmental_impact)
    
    def _update_character_progression(
        self,
        character: Character,
        skill_check_result: SkillCheckResult
    ) -> None:
        """Update character skill progression tracking."""
        # Get or create progression record
        progression = self.db.query(CharacterSkillProgression).filter_by(
            character_id=character.uuid,
            skill_name=skill_check_result.skill_name
        ).first()
        
        if not progression:
            skill_info = character.skills.get(skill_check_result.skill_name, {})
            progression = CharacterSkillProgression(
                character_id=character.uuid,
                skill_name=skill_check_result.skill_name,
                current_level=character.level,
                is_proficient=skill_info.get('proficient', False),
                has_expertise=skill_info.get('expertise', False),
                skill_bonus=skill_info.get('bonus', 0),
                first_check_date=datetime.utcnow()
            )
            self.db.add(progression)
        
        # Update statistics
        progression.total_checks += 1
        progression.last_check_date = datetime.utcnow()
        
        if skill_check_result.success:
            progression.successful_checks += 1
        
        if skill_check_result.critical_success:
            progression.critical_successes += 1
        elif skill_check_result.critical_failure:
            progression.critical_failures += 1
        
        # Update DC statistics
        if skill_check_result.dc:
            if progression.avg_dc_attempted:
                # Running average
                progression.avg_dc_attempted = (
                    (progression.avg_dc_attempted * (progression.total_checks - 1) + skill_check_result.dc)
                    / progression.total_checks
                )
            else:
                progression.avg_dc_attempted = skill_check_result.dc
            
            if skill_check_result.success and (
                not progression.highest_dc_success or 
                skill_check_result.dc > progression.highest_dc_success
            ):
                progression.highest_dc_success = skill_check_result.dc
        
        # Update recent performance (last 20 checks)
        self._update_recent_performance(progression)
        
        # Check for milestones
        self._check_skill_milestones(progression)
    
    def _update_recent_performance(self, progression: CharacterSkillProgression) -> None:
        """Update recent performance metrics for a character's skill."""
        # Get last 20 checks
        recent_checks = self.db.query(SkillCheckHistory).filter_by(
            character_id=progression.character_id,
            skill_name=progression.skill_name
        ).order_by(desc(SkillCheckHistory.created_at)).limit(20).all()
        
        if recent_checks:
            recent_successes = sum(1 for check in recent_checks if check.success)
            progression.recent_success_rate = recent_successes / len(recent_checks)
            
            recent_rolls = [check.total_roll for check in recent_checks]
            progression.recent_avg_roll = sum(recent_rolls) / len(recent_rolls)
            
            # Determine trend (compare first half vs second half of recent checks)
            if len(recent_checks) >= 10:
                first_half = recent_checks[10:]  # Older checks
                second_half = recent_checks[:10]  # Newer checks
                
                first_half_avg = sum(check.total_roll for check in first_half) / len(first_half)
                second_half_avg = sum(check.total_roll for check in second_half) / len(second_half)
                
                diff = second_half_avg - first_half_avg
                if diff > 2:
                    progression.improvement_trend = 'improving'
                elif diff < -2:
                    progression.improvement_trend = 'declining'
                else:
                    progression.improvement_trend = 'stable'
    
    def _check_skill_milestones(self, progression: CharacterSkillProgression) -> None:
        """Check and record skill milestones."""
        milestones = progression.milestones_achieved or []
        new_milestones = []
        
        # Define milestones
        milestone_checks = [
            (10, "first_10_checks"),
            (50, "skilled_practitioner"),
            (100, "experienced_user"),
            (250, "expert_user"),
            (500, "master_user")
        ]
        
        for check_count, milestone_name in milestone_checks:
            if (progression.total_checks >= check_count and 
                milestone_name not in milestones):
                new_milestones.append(milestone_name)
        
        # Success rate milestones
        if progression.total_checks >= 20:  # Need enough data
            success_rate = progression.successful_checks / progression.total_checks
            if success_rate >= 0.8 and "high_success_rate" not in milestones:
                new_milestones.append("high_success_rate")
        
        # Critical success milestones
        if progression.critical_successes >= 5 and "critical_master" not in milestones:
            new_milestones.append("critical_master")
        
        # High DC success
        if (progression.highest_dc_success and 
            progression.highest_dc_success >= 25 and 
            "legendary_success" not in milestones):
            new_milestones.append("legendary_success")
        
        if new_milestones:
            milestones.extend(new_milestones)
            progression.milestones_achieved = milestones
            logger.info(f"New milestones achieved for {progression.skill_name}: {new_milestones}")
    
    def _log_skill_synergies(
        self,
        character: Character,
        skill_check_id: str,
        skill_check_result: SkillCheckResult
    ) -> None:
        """Log skill synergy usage and effectiveness."""
        # This would integrate with the synergy calculation from the skill check service
        # For now, we'll create a placeholder based on configuration
        synergies = skill_config.get_skill_synergies(skill_check_result.skill_name)
        
        if synergies:
            character_skills = character.skills
            active_synergies = []
            
            for synergy_skill in synergies:
                skill_info = character_skills.get(synergy_skill, {})
                if skill_info.get('proficient', False):
                    active_synergies.append(synergy_skill)
            
            if active_synergies:
                synergy_bonus = min(len(active_synergies) * 2, 4)  # +2 per synergy, max +4
                was_beneficial = False
                
                # Check if synergy was beneficial
                if skill_check_result.dc:
                    roll_without_synergy = skill_check_result.total_roll - synergy_bonus
                    would_have_failed = roll_without_synergy < skill_check_result.dc
                    was_beneficial = skill_check_result.success and would_have_failed
                
                skill_synergy = SkillSynergy(
                    character_id=character.uuid,
                    primary_skill=skill_check_result.skill_name,
                    synergy_skills=active_synergies,
                    synergy_bonus=synergy_bonus,
                    skill_check_id=skill_check_id,
                    was_beneficial=was_beneficial
                )
                
                self.db.add(skill_synergy)
    
    # === SOCIAL RELATIONSHIP TRACKING ===
    
    def update_social_relationship(
        self,
        character_id: str,
        npc_id: str,
        interaction_type: str,
        outcome: str,
        attitude_change: int,
        location: Optional[str] = None
    ) -> None:
        """Update social relationship between character and NPC."""
        # Get or create relationship
        relationship = self.db.query(SocialRelationship).filter_by(
            character_id=character_id,
            npc_id=npc_id
        ).first()
        
        if not relationship:
            relationship = SocialRelationship(
                character_id=character_id,
                npc_id=npc_id,
                first_meeting_location=location
            )
            self.db.add(relationship)
        
        # Update relationship state
        relationship.current_attitude += attitude_change
        relationship.current_attitude = max(-100, min(100, relationship.current_attitude))  # Clamp
        
        relationship.total_interactions += 1
        relationship.last_interaction_type = interaction_type
        relationship.last_interaction_outcome = outcome
        relationship.last_interaction = datetime.utcnow()
        
        # Update interaction-specific counters
        if interaction_type == 'persuasion' and 'success' in outcome:
            relationship.successful_persuasions += 1
        elif interaction_type == 'deception' and 'failure' in outcome:
            relationship.failed_deceptions += 1
        elif interaction_type == 'intimidation':
            relationship.intimidation_attempts += 1
        
        # Update relationship type based on attitude
        if relationship.current_attitude >= 50:
            relationship.relationship_type = 'friend'
        elif relationship.current_attitude >= 20:
            relationship.relationship_type = 'acquaintance'
        elif relationship.current_attitude <= -50:
            relationship.relationship_type = 'enemy'
        elif relationship.current_attitude <= -20:
            relationship.relationship_type = 'rival'
        else:
            relationship.relationship_type = 'neutral'
        
        self.db.commit()
    
    # === SESSION MANAGEMENT ===
    
    def start_skill_check_session(
        self,
        campaign_id: Optional[str] = None,
        dm_id: Optional[str] = None,
        session_name: Optional[str] = None,
        session_type: Optional[str] = None,
        location: Optional[str] = None
    ) -> str:
        """Start a new skill check session for analytics grouping."""
        session = SkillCheckSession(
            campaign_id=campaign_id,
            dm_id=dm_id,
            session_name=session_name,
            session_type=session_type,
            location=location
        )
        
        self.db.add(session)
        self.db.commit()
        
        return str(session.id)
    
    def end_skill_check_session(self, session_id: str) -> None:
        """End a skill check session and calculate final statistics."""
        session = self.db.query(SkillCheckSession).filter_by(id=session_id).first()
        if not session:
            return
        
        session.session_end = datetime.utcnow()
        
        # Calculate session statistics
        skill_checks = self.db.query(SkillCheckHistory).filter_by(
            session_id=session_id
        ).all()
        
        if skill_checks:
            session.total_skill_checks = len(skill_checks)
            session.unique_skills_used = list(set(check.skill_name for check in skill_checks))
            
            dcs = [check.dc for check in skill_checks if check.dc]
            if dcs:
                session.average_dc = sum(dcs) / len(dcs)
            
            successes = sum(1 for check in skill_checks if check.success)
            session.overall_success_rate = successes / len(skill_checks)
            
            # Environmental conditions
            all_conditions = []
            for check in skill_checks:
                if check.environmental_conditions:
                    all_conditions.extend(check.environmental_conditions)
            
            condition_counts = defaultdict(int)
            for condition in all_conditions:
                condition_counts[condition] += 1
            
            # Get most common conditions
            session.dominant_conditions = dict(condition_counts)
            
            # Difficulty distribution
            difficulty_counts = defaultdict(int)
            for check in skill_checks:
                if check.difficulty_category:
                    difficulty_counts[check.difficulty_category] += 1
            
            session.difficulty_distribution = dict(difficulty_counts)
        
        self.db.commit()
    
    # === ANALYTICS QUERIES ===
    
    def get_character_skill_analytics(
        self,
        character_id: str,
        skill_name: Optional[str] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a character's skill usage."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = self.db.query(SkillCheckHistory).filter(
            SkillCheckHistory.character_id == character_id,
            SkillCheckHistory.created_at >= cutoff_date
        )
        
        if skill_name:
            query = query.filter(SkillCheckHistory.skill_name == skill_name)
        
        skill_checks = query.all()
        
        if not skill_checks:
            return {"message": "No skill checks found for this period"}
        
        # Basic statistics
        total_checks = len(skill_checks)
        successful_checks = sum(1 for check in skill_checks if check.success)
        success_rate = successful_checks / total_checks
        
        # By skill breakdown
        by_skill = defaultdict(lambda: {"total": 0, "successes": 0, "avg_roll": 0})
        
        for check in skill_checks:
            skill_data = by_skill[check.skill_name]
            skill_data["total"] += 1
            if check.success:
                skill_data["successes"] += 1
            skill_data["avg_roll"] = (
                (skill_data["avg_roll"] * (skill_data["total"] - 1) + check.total_roll) 
                / skill_data["total"]
            )
        
        # Add success rates
        for skill_data in by_skill.values():
            skill_data["success_rate"] = skill_data["successes"] / skill_data["total"]
        
        # Environmental impact analysis
        env_impacts = self.db.query(EnvironmentalImpact).join(SkillCheckHistory).filter(
            SkillCheckHistory.character_id == character_id,
            SkillCheckHistory.created_at >= cutoff_date
        ).all()
        
        environmental_analysis = defaultdict(lambda: {"count": 0, "critical_impacts": 0})
        for impact in env_impacts:
            env_data = environmental_analysis[impact.condition_name]
            env_data["count"] += 1
            if impact.impact_significance == 'critical':
                env_data["critical_impacts"] += 1
        
        return {
            "period_days": days_back,
            "total_checks": total_checks,
            "success_rate": round(success_rate, 3),
            "critical_successes": sum(1 for check in skill_checks if check.critical_success),
            "critical_failures": sum(1 for check in skill_checks if check.critical_failure),
            "skills_used": dict(by_skill),
            "environmental_impacts": dict(environmental_analysis),
            "recent_trend": self._calculate_trend(skill_checks)
        }
    
    def _calculate_trend(self, skill_checks: List[SkillCheckHistory]) -> str:
        """Calculate performance trend from skill check history."""
        if len(skill_checks) < 10:
            return "insufficient_data"
        
        # Sort by date
        sorted_checks = sorted(skill_checks, key=lambda x: x.created_at)
        
        # Compare first half vs second half
        mid_point = len(sorted_checks) // 2
        first_half = sorted_checks[:mid_point]
        second_half = sorted_checks[mid_point:]
        
        first_half_success = sum(1 for check in first_half if check.success) / len(first_half)
        second_half_success = sum(1 for check in second_half if check.success) / len(second_half)
        
        diff = second_half_success - first_half_success
        
        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "declining"
        else:
            return "stable"
    
    def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a specific session."""
        session = self.db.query(SkillCheckSession).filter_by(id=session_id).first()
        if not session:
            return {"error": "Session not found"}
        
        skill_checks = self.db.query(SkillCheckHistory).filter_by(
            session_id=session_id
        ).all()
        
        return {
            "session_info": {
                "name": session.session_name,
                "type": session.session_type,
                "location": session.location,
                "start_time": session.session_start.isoformat(),
                "end_time": session.session_end.isoformat() if session.session_end else None
            },
            "statistics": {
                "total_checks": session.total_skill_checks,
                "unique_skills": session.unique_skills_used,
                "average_dc": session.average_dc,
                "success_rate": session.overall_success_rate,
                "dominant_conditions": session.dominant_conditions,
                "difficulty_distribution": session.difficulty_distribution
            },
            "skill_checks": [
                {
                    "skill": check.skill_name,
                    "result": check.total_roll,
                    "dc": check.dc,
                    "success": check.success,
                    "critical": check.critical_success or check.critical_failure,
                    "conditions": check.environmental_conditions
                }
                for check in skill_checks
            ]
        }

# Global service instance (would be injected with actual DB session)
# skill_check_db_service = SkillCheckDatabaseService(db_session) 