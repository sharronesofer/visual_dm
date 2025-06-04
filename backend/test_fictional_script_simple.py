#!/usr/bin/env python3
"""
Simple test to demonstrate the fictional script system.
"""

import random
import re

def generate_foreign_word(original_word, speaker_language=None):
    """Generate a foreign-looking word using completely unreadable fictional script characters."""
    
    # Remove punctuation for processing
    clean_word = re.sub(r'[^\w]', '', original_word)
    if not clean_word:
        return original_word
        
    # Completely unreadable character sets from various Unicode blocks
    script_sets = {
        'elvish': [
            # Tibetan script - looks mystical and flowing
            'ཀ', 'ཁ', 'ག', 'གྷ', 'ང', 'ཅ', 'ཆ', 'ཇ', 'ཉ', 'ཏ', 'ཐ', 'ད', 'དྷ', 'ན', 'པ', 'ཕ', 'བ', 'བྷ', 'མ', 'ཙ',
            'ཚ', 'ཛ', 'ཛྷ', 'ཝ', 'ཞ', 'ཟ', 'འ', 'ཡ', 'ར', 'ལ', 'ཤ', 'ས', 'ཧ', 'ཨ', 'ི', 'ུ', 'ེ', 'ོ', 'ྭ', 'ྱ'
        ],
        'draconic': [
            # Runic and ancient symbols - looks harsh and angular
            'ᚠ', 'ᚢ', 'ᚦ', 'ᚨ', 'ᚱ', 'ᚲ', 'ᚷ', 'ᚹ', 'ᚺ', 'ᚾ', 'ᛁ', 'ᛃ', 'ᛇ', 'ᛈ', 'ᛉ', 'ᛊ', 'ᛏ', 'ᛒ', 'ᛖ', 'ᛗ',
            'ᛚ', 'ᛜ', 'ᛝ', 'ᛟ', 'ᛞ', 'ᚤ', 'ᚣ', 'ᚧ', 'ᚥ', 'ᚦ', 'ᚩ', 'ᚪ', 'ᚫ', 'ᚬ', 'ᚭ', 'ᚮ', 'ᚯ', 'ᚰ', 'ᚱ', 'ᚲ'
        ],
        'ancient': [
            # Ancient scripts and cuneiform-like symbols
            '𒀀', '𒀁', '𒀂', '𒀃', '𒀄', '𒀅', '𒀆', '𒀇', '𒀈', '𒀉', '𒀊', '𒀋', '𒀌', '𒀍', '𒀎', '𒀏', '𒀐', '1', '2', '3',
            '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N'
        ],
        'mystic': [
            # Geometric and mathematical symbols - looks otherworldly
            '◊', '◈', '◉', '◎', '○', '◐', '◑', '◒', '◓', '◔', '◕', '◖', '◗', '◘', '◙', '◚', '◛', '◜', '◝', '◞',
            '◟', '◠', '◡', '◢', '◣', '◤', '◥', '◦', '◧', '◨', '◩', '◪', '◫', '◬', '◭', '◮', '◯', '◰', '◱', '◲'
        ]
    }
    
    # Language script mapping
    language_script_mapping = {
        'elvish': 'elvish',
        'sylvan': 'elvish',
        'gnomish': 'elvish',
        'halfling': 'elvish',
        'draconic': 'draconic',
        'abyssal': 'draconic',
        'infernal': 'draconic',
        'goblin': 'draconic',
        'orcish': 'draconic',
        'ancient imperial': 'ancient',  # Fixed spacing
        'ancient_imperial': 'ancient',
        'old_celestial': 'ancient',
        'primordial': 'ancient',
        'giant': 'ancient',
        'dwarven': 'ancient',
        'celestial': 'mystic',
        'druidic': 'mystic'
    }
    
    # Choose script set based on language or fallback to word length
    if speaker_language and speaker_language.lower() in language_script_mapping:
        script_style = language_script_mapping[speaker_language.lower()]
    else:
        script_names = list(script_sets.keys())
        script_style = script_names[len(clean_word) % len(script_names)]
    
    chosen_script = script_sets.get(script_style, script_sets['mystic'])
    
    # Generate completely foreign characters - no mapping to English letters
    foreign_chars = []
    for i, char in enumerate(clean_word):
        if char.isalpha():
            # Use character position and word position to select symbols
            char_index = (ord(char.lower()) - ord('a') + i) % len(chosen_script)
            foreign_chars.append(chosen_script[char_index])
        else:
            foreign_chars.append(char)  # Keep non-alphabetic characters
    
    foreign_word = ''.join(foreign_chars)
    
    # Occasionally add connector symbols between characters for authenticity
    if len(foreign_word) > 2 and random.random() < 0.2:
        connectors = ['·', '‧', '⁞', '᭟', '᭞']
        connector = random.choice(connectors)
        insert_pos = random.randint(1, len(foreign_word) - 1)
        foreign_word = foreign_word[:insert_pos] + connector + foreign_word[insert_pos:]
    
    # Preserve punctuation from original word
    original_punct = re.findall(r'[^\w]', original_word)
    if original_punct:
        foreign_word += ''.join(original_punct)
        
    return foreign_word

def modify_text_for_comprehension(text, comprehension_level, speaker_language=None):
    """Modify text based on comprehension level, replacing unknown words with fictional script."""
    
    if comprehension_level >= 0.8:
        return text
    
    if comprehension_level < 0.15:  # Lower threshold to show more examples
        return "[You can barely understand what they're saying]"
    
    words = text.split()
    modified_words = []
    
    for word in words:
        # Keep important words (proper nouns, numbers, short words)
        if (word and word[0].isupper() or  # Proper nouns
            word.isdigit() or             # Numbers  
            len(word) <= 3 or             # Short words
            word.lower() in ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'from', 'a', 'an']):
            modified_words.append(word)
        elif random.random() < comprehension_level:
            modified_words.append(word)
        else:
            # Replace with foreign script
            modified_words.append(generate_foreign_word(word, speaker_language))
    
    return ' '.join(modified_words)

def main():
    """Demonstrate the fictional script system."""
    
    print("🎮 Fantasy Language Script System Demo")
    print("=" * 50)
    
    # Test dialogue
    original_text = "Hello there, brave traveler! How has your dangerous journey been treating you today?"
    
    print(f"\n📝 Original Dialogue:")
    print(f"   \"{original_text}\"")
    print()
    
    # Test different comprehension levels and languages
    test_scenarios = [
        ("Elvish", 0.4, "Partial elvish comprehension"),
        ("Draconic", 0.1, "Almost no draconic comprehension"),
        ("Ancient Imperial", 0.25, "Some ancient imperial comprehension"),
        ("Celestial", 0.15, "Very limited celestial comprehension")
    ]
    
    for language, comprehension, description in test_scenarios:
        print(f"🗣️  {description} ({comprehension:.0%}):")
        
        # Set random seed for consistent demo
        random.seed(42)
        
        result = modify_text_for_comprehension(original_text, comprehension, language)
        print(f"   \"{result}\"")
        print()
    
    print("🎨 Script Style Examples:")
    print("-" * 30)
    
    test_word = "greetings"
    languages = ["Elvish", "Draconic", "Ancient Imperial", "Celestial"]
    
    for language in languages:
        # Set seed for consistent output
        random.seed(hash(language))
        foreign_word = generate_foreign_word(test_word, language)
        print(f"   {language:15}: {test_word} → {foreign_word}")
    
    print()
    print("🌟 Key Features:")
    print("   • Words maintain their original length and structure")
    print("   • Proper nouns, numbers, and short words are preserved") 
    print("   • Each language family has a consistent script style")
    print("   • Punctuation and capitalization are maintained")
    print("   • Occasional diacritical marks add authenticity")
    print("   • No trademarked or real-world scripts are used")

if __name__ == "__main__":
    main() 