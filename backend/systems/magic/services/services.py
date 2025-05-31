"""
Magic System Services - D&D Compliant Business Logic

Implements comprehensive spell system including:
- Spell casting with validation
- Spellbook management
- Spell slot tracking
- Concentration management
- Effect duration tracking
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.systems.magic.models import (
    Spell, Character, Spellbook, KnownSpell, PreparedSpell,
    SpellSlots, ActiveSpellEffect, CastSpellRequest
)

class MagicService:
    """Service class for magic system operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_spells(self, school: Optional[str] = None, level: Optional[int] = None) -> List[Spell]:
        """Get spells with optional filtering."""
        query = self.db.query(Spell)
        
        if school:
            query = query.filter(Spell.school == school)
        if level is not None:
            query = query.filter(Spell.level == level)
            
        return query.all()
    
    async def get_spell(self, spell_id: UUID) -> Optional[Spell]:
        """Get specific spell by ID."""
        return self.db.query(Spell).filter(Spell.id == spell_id).first()
    
    async def get_spellbook(self, character_id: UUID) -> Optional[Spellbook]:
        """Get character's spellbook with known and prepared spells."""
        return self.db.query(Spellbook).filter(Spellbook.character_id == character_id).first()
    
    async def prepare_spells(self, character_id: UUID, spell_ids: List[UUID]) -> Dict[str, Any]:
        """Prepare daily spells for character."""
        spellbook = await self.get_spellbook(character_id)
        if not spellbook:
            raise ValueError("Spellbook not found")
        
        # Clear existing prepared spells
        self.db.query(PreparedSpell).filter(PreparedSpell.spellbook_id == spellbook.id).delete()
        
        # Add new prepared spells
        for spell_id in spell_ids:
            prepared = PreparedSpell(
                spellbook_id=spellbook.id,
                spell_id=spell_id
            )
            self.db.add(prepared)
        
        self.db.commit()
        return {"message": f"Prepared {len(spell_ids)} spells"}
    
    async def cast_spell(self, request: CastSpellRequest) -> Dict[str, Any]:
        """Cast a spell with full validation."""
        spell = await self.get_spell(request.spell_id)
        if not spell:
            raise ValueError("Spell not found")
        
        # Validate spell slot usage
        if spell.level > 0:
            spell_level = request.spell_level or spell.level
            if not await self._use_spell_slot(request.target_id, spell_level):
                raise ValueError("No spell slots available")
        
        # Handle concentration
        if spell.concentration:
            await self._handle_concentration(request.target_id, spell)
        
        # Create spell effect
        effect = ActiveSpellEffect(
            character_id=request.target_id,
            spell_id=spell.id,
            caster_id=request.target_id,
            concentration=spell.concentration,
            effect_data=request.metadata or {}
        )
        
        # Set expiration for timed spells
        if "minute" in spell.duration.lower():
            minutes = self._parse_duration_minutes(spell.duration)
            effect.expires_at = datetime.utcnow() + timedelta(minutes=minutes)
        elif "hour" in spell.duration.lower():
            hours = self._parse_duration_hours(spell.duration)
            effect.expires_at = datetime.utcnow() + timedelta(hours=hours)
        
        self.db.add(effect)
        self.db.commit()
        
        return {
            "message": f"Cast {spell.name}",
            "effect_id": str(effect.id),
            "expires_at": effect.expires_at.isoformat() if effect.expires_at else None
        }
    
    async def get_spell_slots(self, character_id: UUID) -> List[Dict[str, Any]]:
        """Get character's spell slots."""
        slots = self.db.query(SpellSlots).filter(SpellSlots.character_id == character_id).all()
        return [
            {
                "level": slot.level,
                "total_slots": slot.total_slots,
                "used_slots": slot.used_slots,
                "remaining_slots": slot.total_slots - slot.used_slots
            }
            for slot in slots
        ]
    
    async def restore_spell_slots(self, character_id: UUID) -> Dict[str, Any]:
        """Restore all spell slots after long rest."""
        self.db.query(SpellSlots).filter(SpellSlots.character_id == character_id).update({"used_slots": 0})
        self.db.commit()
        return {"message": "Spell slots restored"}
    
    async def get_active_effects(self, character_id: UUID) -> List[Dict[str, Any]]:
        """Get active spell effects for character."""
        effects = self.db.query(ActiveSpellEffect).filter(
            and_(
                ActiveSpellEffect.character_id == character_id,
                ActiveSpellEffect.expires_at > datetime.utcnow()
            )
        ).all()
        
        return [
            {
                "id": str(effect.id),
                "spell_name": effect.spell.name,
                "cast_at": effect.cast_at.isoformat(),
                "expires_at": effect.expires_at.isoformat() if effect.expires_at else None,
                "concentration": effect.concentration,
                "effect_data": effect.effect_data
            }
            for effect in effects
        ]
    
    async def dispel_effect(self, effect_id: UUID) -> Dict[str, Any]:
        """Dispel an active spell effect."""
        effect = self.db.query(ActiveSpellEffect).filter(ActiveSpellEffect.id == effect_id).first()
        if not effect:
            raise ValueError("Effect not found")
        
        self.db.delete(effect)
        self.db.commit()
        return {"message": "Effect dispelled"}
    
    async def _use_spell_slot(self, character_id: UUID, level: int) -> bool:
        """Use a spell slot of the specified level."""
        slot = self.db.query(SpellSlots).filter(
            and_(
                SpellSlots.character_id == character_id,
                SpellSlots.level == level,
                SpellSlots.used_slots < SpellSlots.total_slots
            )
        ).first()
        
        if slot:
            slot.used_slots += 1
            self.db.commit()
            return True
        return False
    
    async def _handle_concentration(self, character_id: UUID, spell: Spell):
        """Handle concentration spell casting."""
        # End existing concentration spells
        existing = self.db.query(ActiveSpellEffect).filter(
            and_(
                ActiveSpellEffect.character_id == character_id,
                ActiveSpellEffect.concentration == True
            )
        ).all()
        
        for effect in existing:
            self.db.delete(effect)
    
    def _parse_duration_minutes(self, duration: str) -> int:
        """Parse duration string to extract minutes."""
        import re
        match = re.search(r'(\d+)\s*minute', duration.lower())
        return int(match.group(1)) if match else 10
    
    def _parse_duration_hours(self, duration: str) -> int:
        """Parse duration string to extract hours."""
        import re
        match = re.search(r'(\d+)\s*hour', duration.lower())
        return int(match.group(1)) if match else 1
