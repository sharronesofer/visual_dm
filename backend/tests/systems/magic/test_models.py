"""
Tests for Magic System Models
"""

import pytest
from uuid import uuid4
from datetime import datetime
from backend.systems.magic.models import (
    MagicSchool, SpellLevel, SpellComponent, SpellDuration,
    Spell, Character, Spellbook, KnownSpell, PreparedSpell,
    SpellSlots, ActiveSpellEffect, SpellPreparation,
    SpellComponentRequirement, SpellDurationTracking
)

def test_magic_school_enum():
    """Test magic school enum values."""
    assert MagicSchool.ABJURATION == "abjuration"
    assert MagicSchool.CONJURATION == "conjuration"
    assert MagicSchool.DIVINATION == "divination"
    assert MagicSchool.ENCHANTMENT == "enchantment"
    assert MagicSchool.EVOCATION == "evocation"
    assert MagicSchool.ILLUSION == "illusion"
    assert MagicSchool.NECROMANCY == "necromancy"
    assert MagicSchool.TRANSMUTATION == "transmutation"
    assert len(list(MagicSchool)) == 8

def test_spell_level_enum():
    """Test spell level enum values."""
    assert SpellLevel.CANTRIP == 0
    assert SpellLevel.FIRST == 1
    assert SpellLevel.NINTH == 9

def test_spell_component_enum():
    """Test spell component enum values."""
    assert SpellComponent.VERBAL == "verbal"
    assert SpellComponent.SOMATIC == "somatic"
    assert SpellComponent.MATERIAL == "material"

def test_spell_duration_enum():
    """Test spell duration enum values."""
    assert SpellDuration.INSTANTANEOUS == "instantaneous"
    assert SpellDuration.CONCENTRATION == "concentration"
    assert SpellDuration.TIMED == "timed"
    assert SpellDuration.PERMANENT == "permanent"

def test_spell_model():
    """Test spell model creation."""
    spell = Spell(
        name="Magic Missile",
        school=MagicSchool.EVOCATION,
        level=1,
        casting_time="1 action",
        range="120 feet",
        components=["verbal", "somatic"],
        duration="Instantaneous",
        description="Test spell",
        concentration=False,
        ritual=False
    )
    assert spell.name == "Magic Missile"
    assert spell.school == MagicSchool.EVOCATION
    assert spell.level == 1
    assert not spell.concentration
    assert not spell.ritual

def test_character_model():
    """Test character model creation."""
    character = Character(
        name="Test Wizard",
        level=5,
        spellcasting_ability="Intelligence",
        spell_attack_bonus=7,
        spell_save_dc=15
    )
    assert character.name == "Test Wizard"
    assert character.level == 5
    assert character.spell_save_dc == 15

def test_spellbook_model():
    """Test spellbook model creation."""
    character_id = uuid4()
    spellbook = Spellbook(
        character_id=character_id,
        name="Wizard's Spellbook",
        description="A leather-bound tome"
    )
    assert spellbook.character_id == character_id
    assert spellbook.name == "Wizard's Spellbook"

def test_spell_slots_model():
    """Test spell slots model creation."""
    character_id = uuid4()
    slots = SpellSlots(
        character_id=character_id,
        level=1,
        total_slots=4,
        used_slots=2
    )
    assert slots.character_id == character_id
    assert slots.level == 1
    assert slots.total_slots == 4
    assert slots.used_slots == 2

def test_active_spell_effect_model():
    """Test active spell effect model creation."""
    character_id = uuid4()
    spell_id = uuid4()
    effect = ActiveSpellEffect(
        character_id=character_id,
        spell_id=spell_id,
        concentration=True,
        effect_data={"damage": "1d4+1"}
    )
    assert effect.character_id == character_id
    assert effect.spell_id == spell_id
    assert effect.concentration
    assert effect.effect_data["damage"] == "1d4+1"
