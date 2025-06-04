#!/usr/bin/env python3
"""
Personality Interpreter Demo
---------------------------
Demonstrates how numerical personality values are translated into rich descriptive text
for better LLM understanding and human readability.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.systems.character.utils.personality_interpreter import (
    interpret_personality_for_llm, 
    get_attribute_description,
    personality_interpreter
)

def demo_personality_interpretation():
    """Demonstrate the personality interpretation system."""
    
    print("=== PERSONALITY INTERPRETER DEMO ===\n")
    
    # Example personality profiles
    personalities = {
        "Honorable Defender": {
            "ambition": 2,      # Low ambition - serves others
            "integrity": 6,     # Maximum integrity
            "discipline": 5,    # Very disciplined
            "impulsivity": 1,   # Very cautious
            "pragmatism": 2,    # Idealistic
            "resilience": 5     # Very resilient
        },
        "Opportunistic Survivor": {
            "ambition": 5,      # High ambition 
            "integrity": 2,     # Low integrity
            "discipline": 3,    # Moderate discipline
            "impulsivity": 4,   # Somewhat impulsive
            "pragmatism": 6,    # Maximum pragmatism
            "resilience": 4     # High resilience
        },
        "Conflicted Scholar": {
            "ambition": 5,      # High ambition
            "integrity": 5,     # High integrity (creates internal conflict)
            "discipline": 6,    # Maximum discipline
            "impulsivity": 0,   # Never impulsive
            "pragmatism": 2,    # Idealistic 
            "resilience": 3     # Moderate resilience
        }
    }
    
    for character_type, personality in personalities.items():
        print(f"🎭 **{character_type}**")
        print("Raw Values:", personality)
        print()
        
        # Show single attribute interpretation
        print("Single Attribute Examples:")
        print(f"  Integrity {personality['integrity']}: {get_attribute_description('integrity', personality['integrity'])}")
        print(f"  Ambition {personality['ambition']}: {get_attribute_description('ambition', personality['ambition'])}")
        print()
        
        # Show full LLM-ready description
        print("LLM-Ready Description:")
        llm_description = interpret_personality_for_llm(personality)
        print(llm_description)
        print()
        
        # Show full detailed interpretation
        print("Detailed Analysis:")
        full_interpretation = personality_interpreter.interpret_full_personality(personality)
        
        if full_interpretation["personality_dynamics"]["conflicts"]:
            print("⚡ Internal Conflicts:")
            for conflict in full_interpretation["personality_dynamics"]["conflicts"]:
                print(f"   - {conflict}")
        
        if full_interpretation["personality_dynamics"]["synergies"]:
            print("💪 Personality Strengths:")
            for synergy in full_interpretation["personality_dynamics"]["synergies"]:
                print(f"   - {synergy}")
        
        print("📖 Narrative Summary:")
        print(f"   {full_interpretation['narrative_summary']}")
        
        print("\n" + "="*60 + "\n")

def demo_character_creation():
    """Demonstrate how personality interpretation integrates with character creation."""
    
    print("=== CHARACTER CREATION WITH PERSONALITY ===\n")
    
    try:
        from backend.systems.character.services.character_builder import CharacterBuilder
        
        # Create a character
        builder = CharacterBuilder()
        builder.character_name = "Test Character"
        builder.set_race("human")
        builder.assign_attribute("STR", 2)
        builder.assign_attribute("DEX", 3)
        builder.assign_attribute("CON", 2)
        builder.assign_attribute("INT", 4)
        builder.assign_attribute("WIS", 3)
        builder.assign_attribute("CHA", 3)
        
        # Finalize the character (this includes personality generation and interpretation)
        character_data = builder.finalize()
        
        print("🧙 **Generated Character:**")
        print(f"Name: {character_data['character_name']}")
        print(f"Race: {character_data['race']}")
        print()
        
        print("Raw Personality Values:")
        for attr, value in character_data['hidden_personality'].items():
            print(f"  {attr}: {value}")
        print()
        
        print("LLM-Ready Personality Description:")
        print(character_data.get('personality_description', 'Not available'))
        
    except Exception as e:
        print(f"Character creation demo failed: {e}")
        print("This may be due to missing dependencies or configuration files.")

if __name__ == "__main__":
    demo_personality_interpretation()
    demo_character_creation() 