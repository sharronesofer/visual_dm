#!/usr/bin/env python3
"""
Test script to demonstrate the fictional script system for language barriers.

This shows how the system replaces incomprehensible words with fantasy language
characters instead of blanks, creating a more immersive experience.
"""

import sys
import os

# Add the backend directory to Python path for proper imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from systems.population.models.language_models import LanguageEngine, Language, LanguageProficiency

def demonstrate_fictional_scripts():
    """Demonstrate the fictional script system with different languages and comprehension levels"""
    
    print("🎮 Fantasy Language Script System Demo")
    print("=" * 50)
    
    # Initialize the language engine
    engine = LanguageEngine()
    
    # Create a test character with limited language knowledge
    test_character_id = "test_player"
    engine.character_proficiencies[test_character_id] = [
        LanguageProficiency(
            language=Language.COMMON,
            comprehension_level=1.0,
            speaking_level=1.0,
            literacy_level=0.8
        ),
        LanguageProficiency(
            language=Language.ELVISH,
            comprehension_level=0.4,  # Limited Elvish
            speaking_level=0.3,
            literacy_level=0.2
        )
    ]
    
    # Test dialogue in different languages with different comprehension levels
    test_dialogue = "Hello there, traveler! How has your journey been treating you today?"
    
    print("\n📝 Original Dialogue:")
    print(f"   \"{test_dialogue}\"")
    print()
    
    # Test different languages and comprehension scenarios
    test_scenarios = [
        {
            "language": Language.ELVISH,
            "description": "Elvish (40% comprehension - partial understanding)",
            "expected": "Mix of understood words and elvish script"
        },
        {
            "language": Language.DRACONIC,
            "description": "Draconic (0% comprehension - should be mostly foreign script)",
            "expected": "Mostly draconic script with some context clues"
        },
        {
            "language": Language.ANCIENT_IMPERIAL,
            "description": "Ancient Imperial (slight comprehension due to Common relationship)",
            "expected": "Mix of understood words and ancient script"
        },
        {
            "language": Language.CELESTIAL,
            "description": "Celestial (0% comprehension - mystic script)",
            "expected": "Mostly mystic script"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"🗣️  {scenario['description']}:")
        
        # Process the dialogue
        result = engine.process_dialogue_comprehension(
            character_id=test_character_id,
            dialogue_text=test_dialogue,
            speaker_language=scenario['language'],
            text_complexity=0.5,
            context_clues=True
        )
        
        print(f"   Comprehension Level: {result['comprehension_level']:.1%}")
        print(f"   Processed Text: \"{result['processed_text']}\"")
        print(f"   Sources: {', '.join(result['comprehension_sources']) if result['comprehension_sources'] else 'None'}")
        print(f"   Can Respond: {'Yes' if result['can_respond'] else 'No'}")
        print()
    
    print("🎨 Script Style Examples:")
    print("-" * 30)
    
    # Show examples of each script style
    test_word = "greetings"
    script_languages = [
        (Language.ELVISH, "Elvish"),
        (Language.DRACONIC, "Draconic"), 
        (Language.ANCIENT_IMPERIAL, "Ancient Imperial"),
        (Language.CELESTIAL, "Celestial")
    ]
    
    for lang, name in script_languages:
        script_style = engine.get_script_style_for_language(lang)
        foreign_word = engine._generate_foreign_word(test_word, lang)
        print(f"   {name:15} ({script_style:8}): {test_word} → {foreign_word}")
    
    print()
    print("🌟 Key Features:")
    print("   • Words maintain their original length and structure")
    print("   • Proper nouns, numbers, and short words are preserved") 
    print("   • Each language family has a consistent script style")
    print("   • Punctuation and capitalization are maintained")
    print("   • Occasional diacritical marks add authenticity")
    print("   • Context clues still provide emotional understanding")
    
    print("\n🎯 Automatic Language Resolution Demo:")
    print("-" * 40)
    
    # Test automatic language resolution
    npc_id = "test_npc"
    engine.character_proficiencies[npc_id] = [
        LanguageProficiency(
            language=Language.ELVISH,
            comprehension_level=1.0,
            speaking_level=1.0,
            literacy_level=0.9
        ),
        LanguageProficiency(
            language=Language.COMMON,
            comprehension_level=0.6,
            speaking_level=0.6,
            literacy_level=0.5
        )
    ]
    
    resolution_result = engine.find_best_common_language(test_character_id, npc_id)
    if resolution_result:
        language, score, explanation = resolution_result
        print(f"   Best Language: {language.value}")
        print(f"   Mutual Comprehension: {score:.1%}")
        print(f"   Explanation: {explanation}")
        
        # Show how this affects dialogue
        dialogue_context = engine.create_dialogue_context(
            speaker_id=npc_id,
            listener_id=test_character_id,
            dialogue_text="The 𝓌𝑒𝒶𝓉𝒽𝑒𝓇 has been quite pleasant for traveling lately."
        )
        
        print(f"\n   Sample Dialogue Result:")
        print(f"   Language Used: {dialogue_context['selected_language']}")
        print(f"   Listener Comprehension: {dialogue_context['comprehension_level']:.1%}")
        print(f"   Processed Text: \"{dialogue_context['processed_text']}\"")

if __name__ == "__main__":
    demonstrate_fictional_scripts() 