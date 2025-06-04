"""
Repository for enchanting system data persistence.

Handles storage and retrieval of:
- Character enchanting profiles
- Learned enchantments
- Disenchantment attempt history
- Enchantment application records
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

from backend.systems.equipment.models.enchanting import (
    LearnedEnchantment, DisenchantmentAttempt, EnchantmentApplication,
    CharacterEnchantingProfile, DisenchantmentOutcome
)

class EnchantingRepository:
    """Repository for enchanting system data persistence."""
    
    def __init__(self, data_dir: str = "data/enchanting"):
        """Initialize repository with data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "profiles").mkdir(exist_ok=True)
        (self.data_dir / "attempts").mkdir(exist_ok=True)
        (self.data_dir / "applications").mkdir(exist_ok=True)
    
    def _get_profile_path(self, character_id: UUID) -> Path:
        """Get file path for character enchanting profile."""
        return self.data_dir / "profiles" / f"{character_id}.json"
    
    def _get_attempts_path(self, character_id: UUID) -> Path:
        """Get file path for character disenchantment attempts."""
        return self.data_dir / "attempts" / f"{character_id}.json"
    
    def _get_applications_path(self, character_id: UUID) -> Path:
        """Get file path for character enchantment applications."""
        return self.data_dir / "applications" / f"{character_id}.json"
    
    def load_character_profile(self, character_id: UUID) -> CharacterEnchantingProfile:
        """Load character enchanting profile or create default."""
        profile_path = self._get_profile_path(character_id)
        
        if not profile_path.exists():
            # Create default profile
            profile = CharacterEnchantingProfile(character_id=character_id)
            self.save_character_profile(profile)
            return profile
        
        try:
            with open(profile_path, 'r') as f:
                data = json.load(f)
            
            # Convert learned enchantments back to objects
            learned_enchantments = {}
            for enchantment_id, learned_data in data.get('learned_enchantments', {}).items():
                learned_enchantments[enchantment_id] = LearnedEnchantment(
                    enchantment_id=enchantment_id,
                    learned_at=datetime.fromisoformat(learned_data['learned_at']),
                    learned_from_item=learned_data['learned_from_item'],
                    mastery_level=learned_data['mastery_level'],
                    times_applied=learned_data['times_applied'],
                    last_applied=datetime.fromisoformat(learned_data['last_applied']) if learned_data.get('last_applied') else None
                )
            
            # Convert preferred school back to enum
            preferred_school = None
            if data.get('preferred_school'):
                try:
                    preferred_school = EnchantmentSchool(data['preferred_school'])
                except ValueError:
                    pass  # Invalid school, leave as None
            
            profile = CharacterEnchantingProfile(
                character_id=UUID(data['character_id']),
                learned_enchantments=learned_enchantments,
                total_items_disenchanted=data.get('total_items_disenchanted', 0),
                successful_disenchantments=data.get('successful_disenchantments', 0),
                successful_applications=data.get('successful_applications', 0),
                failed_applications=data.get('failed_applications', 0),
                preferred_school=preferred_school,
                notes=data.get('notes', [])
            )
            
            return profile
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # File corrupted, create default
            print(f"Warning: Corrupted enchanting profile for {character_id}, creating default: {e}")
            profile = CharacterEnchantingProfile(character_id=character_id)
            self.save_character_profile(profile)
            return profile
    
    def save_character_profile(self, profile: CharacterEnchantingProfile):
        """Save character enchanting profile."""
        profile_path = self._get_profile_path(profile.character_id)
        
        # Convert learned enchantments to serializable format
        learned_enchantments_data = {}
        for enchantment_id, learned_enchantment in profile.learned_enchantments.items():
            learned_enchantments_data[enchantment_id] = {
                'learned_at': learned_enchantment.learned_at.isoformat(),
                'learned_from_item': learned_enchantment.learned_from_item,
                'mastery_level': learned_enchantment.mastery_level,
                'times_applied': learned_enchantment.times_applied,
                'last_applied': learned_enchantment.last_applied.isoformat() if learned_enchantment.last_applied else None
            }
        
        data = {
            'character_id': str(profile.character_id),
            'learned_enchantments': learned_enchantments_data,
            'total_items_disenchanted': profile.total_items_disenchanted,
            'successful_disenchantments': profile.successful_disenchantments,
            'successful_applications': profile.successful_applications,
            'failed_applications': profile.failed_applications,
            'preferred_school': profile.preferred_school.value if profile.preferred_school else None,
            'notes': profile.notes,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(profile_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_disenchantment_attempt(self, attempt: DisenchantmentAttempt):
        """Record a disenchantment attempt for history tracking."""
        attempts_path = self._get_attempts_path(attempt.character_id)
        
        # Load existing attempts
        attempts = []
        if attempts_path.exists():
            try:
                with open(attempts_path, 'r') as f:
                    attempts = json.load(f)
            except (json.JSONDecodeError, KeyError):
                attempts = []
        
        # Add new attempt
        attempt_data = {
            'id': str(attempt.id),
            'timestamp': attempt.timestamp.isoformat(),
            'item_id': str(attempt.item_id),
            'item_name': attempt.item_name,
            'item_quality': attempt.item_quality,
            'target_enchantment': attempt.target_enchantment,
            'outcome': attempt.outcome.value,
            'enchantment_learned': attempt.enchantment_learned,
            'item_destroyed': attempt.item_destroyed,
            'experience_gained': attempt.experience_gained,
            'character_level': attempt.character_level,
            'arcane_manipulation_level': attempt.arcane_manipulation_level,
            'additional_consequences': attempt.additional_consequences
        }
        
        attempts.append(attempt_data)
        
        # Keep only last 100 attempts to prevent unbounded growth
        attempts = attempts[-100:]
        
        with open(attempts_path, 'w') as f:
            json.dump(attempts, f, indent=2)
    
    def record_enchantment_application(self, application: EnchantmentApplication):
        """Record an enchantment application for history tracking."""
        applications_path = self._get_applications_path(application.character_id)
        
        # Load existing applications
        applications = []
        if applications_path.exists():
            try:
                with open(applications_path, 'r') as f:
                    applications = json.load(f)
            except (json.JSONDecodeError, KeyError):
                applications = []
        
        # Add new application
        application_data = {
            'id': str(application.id),
            'timestamp': application.timestamp.isoformat(),
            'item_id': str(application.item_id),
            'enchantment_id': application.enchantment_id,
            'success': application.success,
            'cost_paid': application.cost_paid,
            'final_power_level': application.final_power_level,
            'failure_reason': application.failure_reason,
            'materials_lost': application.materials_lost
        }
        
        applications.append(application_data)
        
        # Keep only last 100 applications
        applications = applications[-100:]
        
        with open(applications_path, 'w') as f:
            json.dump(applications, f, indent=2)
    
    def get_disenchantment_history(self, character_id: UUID, limit: int = 50) -> List[Dict]:
        """Get disenchantment history for a character."""
        attempts_path = self._get_attempts_path(character_id)
        
        if not attempts_path.exists():
            return []
        
        try:
            with open(attempts_path, 'r') as f:
                attempts = json.load(f)
            
            # Return most recent attempts first
            return attempts[-limit:][::-1]
        
        except (json.JSONDecodeError, KeyError):
            return []
    
    def get_application_history(self, character_id: UUID, limit: int = 50) -> List[Dict]:
        """Get enchantment application history for a character."""
        applications_path = self._get_applications_path(character_id)
        
        if not applications_path.exists():
            return []
        
        try:
            with open(applications_path, 'r') as f:
                applications = json.load(f)
            
            # Return most recent applications first
            return applications[-limit:][::-1]
        
        except (json.JSONDecodeError, KeyError):
            return []
    
    def get_character_statistics(self, character_id: UUID) -> Dict:
        """Get comprehensive statistics for a character's enchanting activities."""
        profile = self.load_character_profile(character_id)
        disenchantment_history = self.get_disenchantment_history(character_id)
        application_history = self.get_application_history(character_id)
        
        # Calculate additional statistics
        enchantment_schools_learned = {}
        for enchantment_id, learned_enchantment in profile.learned_enchantments.items():
            from backend.systems.equipment.models.enchanting import get_enchantment_definition
            enchantment_def = get_enchantment_definition(enchantment_id)
            if enchantment_def:
                school = enchantment_def.school.value
                enchantment_schools_learned[school] = enchantment_schools_learned.get(school, 0) + 1
        
        # Recent activity
        recent_disenchantments = len([a for a in disenchantment_history if 
                                    datetime.fromisoformat(a['timestamp']) > datetime.now().replace(day=datetime.now().day-7)])
        recent_applications = len([a for a in application_history if 
                                 datetime.fromisoformat(a['timestamp']) > datetime.now().replace(day=datetime.now().day-7)])
        
        return {
            'character_id': str(character_id),
            'total_enchantments_learned': len(profile.learned_enchantments),
            'total_items_disenchanted': profile.total_items_disenchanted,
            'successful_disenchantments': profile.successful_disenchantments,
            'successful_applications': profile.successful_applications,
            'failed_applications': profile.failed_applications,
            'disenchantment_success_rate': (profile.successful_disenchantments / max(profile.total_items_disenchanted, 1)) * 100,
            'application_success_rate': (profile.successful_applications / max(profile.successful_applications + profile.failed_applications, 1)) * 100,
            'preferred_school': profile.preferred_school.value if profile.preferred_school else None,
            'schools_learned': enchantment_schools_learned,
            'recent_disenchantments_week': recent_disenchantments,
            'recent_applications_week': recent_applications,
            'most_experienced_school': max(enchantment_schools_learned.items(), key=lambda x: x[1])[0] if enchantment_schools_learned else None
        } 