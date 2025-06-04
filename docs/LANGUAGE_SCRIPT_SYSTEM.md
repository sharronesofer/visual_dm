# Fantasy Language Script System

## Overview

The Fantasy Language Script System enhances immersion by replacing incomprehensible words with **completely unreadable fictional script characters** instead of blanks or placeholder text. This creates a truly authentic language barrier experience where foreign text looks genuinely alien and incomprehensible, while maintaining visual flow and readability of preserved words.

## Key Features

### 🎨 **Complete Unreadability**
- Uses real Unicode scripts from ancient and foreign writing systems
- **No recognizable English letter shapes** - truly alien appearance
- Words maintain their original length and structure
- Proper nouns, numbers, and short words are preserved for context
- Punctuation and capitalization are maintained

### 🌍 **Language Consistency**
- Each language family has a distinct script from different Unicode blocks
- **Elvish Family** uses Tibetan script: `ཀ་ཁ་ག་ང་ཅ`
- **Draconic Family** uses Runic script: `ᚠᚢᚦᚨᚱᚲᚷ`
- **Ancient Family** uses Cuneiform script: `𒀀𒀁𒀂𒀃𒀄𒀅𒀆`
- **Mystic Family** uses Geometric symbols: `◊◈◉◎○◐◑`

### ✨ **Authenticity Details**
- Connector symbols occasionally added: `·`, `‧`, `⁞`
- Language-specific script selection based on speaker
- No trademarked or real-world scripts used inappropriately
- Truly foreign appearance that cannot be easily read

## Script Families

### Elvish Family (Tibetan Script)
**Languages:** Elvish, Sylvan, Gnomish, Halfling
**Style:** Mystical, flowing characters with spiritual appearance
**Example:** `Hello` → `ཆཞཛྷཛྷཞ`
**Unicode Range:** Tibetan (U+0F00-U+0FFF)

### Draconic Family (Runic Script)
**Languages:** Draconic, Abyssal, Infernal, Goblin, Orcish
**Style:** Angular, harsh symbols suggesting ancient power
**Example:** `Hello` → `ᚺᚱᛚᛚᛟ`
**Unicode Range:** Runic (U+16A0-U+16FF)

### Ancient Family (Cuneiform Script)
**Languages:** Ancient Imperial, Old Celestial, Primordial, Giant, Dwarven
**Style:** Wedge-shaped marks resembling clay tablets
**Example:** `Hello` → `𒀈𒀊𒀛𒀛𒀡`
**Unicode Range:** Cuneiform (U+12000-U+123FF)

### Mystic Family (Geometric Symbols)
**Languages:** Celestial, Druidic
**Style:** Abstract geometric shapes suggesting otherworldly origin
**Example:** `Hello` → `◈◓◛◛◡`
**Unicode Range:** Geometric Shapes (U+25A0-U+25FF)

## How It Works

### 1. **Character Selection Algorithm**
Instead of mapping `a→𝒶`, the system now:
- Takes each letter's position in the alphabet
- Adds the character's position in the word
- Uses modulo arithmetic to select from the script array
- **Result:** Same word always produces same foreign script

### 2. **Word Replacement Logic**
- **Keep:** Proper nouns, numbers, short words (≤3 letters), common articles
- **Replace:** Complex words based on comprehension percentage
- **Script:** Use completely unreadable characters from appropriate Unicode block

### 3. **Script Assignment**
```python
# Language families mapped to unreadable scripts
script_families = {
    'elvish': ['ཀ', 'ཁ', 'ག', 'གྷ', 'ང', ...],    # Tibetan
    'draconic': ['ᚠ', 'ᚢ', 'ᚦ', 'ᚨ', 'ᚱ', ...],   # Runic  
    'ancient': ['𒀀', '𒀁', '𒀂', '𒀃', '𒀄', ...],   # Cuneiform
    'mystic': ['◊', '◈', '◉', '◎', '○', ...]       # Geometric
}
```

## Example Output

### Original Text
```
"Hello there, brave traveler! How has your dangerous journey been treating you today?"
```

### Elvish (40% Comprehension)
```
"Hello ཙཉཆཚཉ, brave ཙམགཞཉབཐཞ! How has ཞཕཛྷཚ dangerous journey ཁཅཆབ ཙམཆགྷཝནཙན you today?"
```

### Draconic (25% Comprehension)  
```
"Hello ᛇᚺᛖᚱᛖ, brave ᛇᚱᚨᚹᛖᛚᛖᚱ! How has your ᛞᚨᚾᚷᛖᚱᛟᚢᛊ ᛃᛟᚢᚱᚾᛖᚤ ᛒᛖᛖᚾ ᛇᚱᛖᚨᛇᛁᚾᚷ you ᛇᛟᛞᚨᚤ?"
```

### Ancient Imperial (25% Comprehension)
```
"Hello 𒀈𒀆𒀈𒀊, brave 𒀓𒀒𒀂𒀅𒀈𒀒𒀊𒀒! How has your 𒀞𒀈𒀚𒀌𒀈𒀒𒀟𒀥𒀊 𒀔𒀟𒀥𒀒𒀚𒀈𒀧 𒀁𒀅𒀈𒀚 𒀓𒀒𒀈𒀃𒀓𒀁𒀚𒀌 you 𒀓𒀟𒀞𒀃𒀧?"
```

### Celestial (15% Comprehension)
```
"Hello ◞◑◟◓, ◈◝◉◣◓ ◞◝◉◣◓◛◕◣! How has your ◎◈◚◔◓◡◟◦◥ ◔◚◡◟◜◔◩ ◈◐◑◛ ◞◝◑◎◢◘◞◘ you ◞◚◐◎◧?"
```

## Implementation

### Backend (Python)
Location: `backend/systems/population/models/language_models.py`

Key functions:
- `_generate_foreign_word()` - Converts words to completely unreadable script
- `_generate_partial_text()` - Processes full dialogue text
- `get_script_style_for_language()` - Maps languages to script families

### Unity (C#)  
Location: `VDM/Assets/Scripts/Runtime/Systems/npc/Services/LanguageInteractionService.cs`

Key functions:
- `GenerateForeignWord()` - Unity version of unreadable script generation
- `ModifyTextForComprehension()` - Unity text processing
- `GetScriptStyleForLanguage()` - Unity language mapping

## Configuration

### Comprehension Thresholds
- **≥80%:** Full comprehension, no script replacement
- **30-79%:** Partial script replacement based on percentage
- **15-29%:** Heavy script replacement, some context preserved
- **<15%:** "[You can barely understand what they're saying]"

### Word Preservation Rules
Always keep:
- Proper nouns (capitalized words)
- Numbers and digits
- Short words (3 letters or less)
- Common articles: the, and, or, but, in, on, at, to, from, a, an

### Connector Symbol Application
- 20% chance for words longer than 2 characters
- Symbols: `·`, `‧`, `⁞`, `᭟`, `᭞`
- Applied between characters for authenticity

## Benefits

### 🎮 **Gameplay**
- **Truly immersive language barriers** - no recognizable patterns
- Players cannot "decode" the foreign text
- Context clues from preserved words still allow educated guessing
- Visual consistency maintains dialogue flow

### 🎨 **Artistic**
- Each language family has **genuinely distinct** appearance
- Scripts look authentically foreign and ancient
- No copyright or trademark concerns
- Unicode support ensures broad compatibility

### 🔧 **Technical**
- Deterministic generation (same word = same foreign script)
- Language-family consistency across all uses
- Efficient character selection algorithm
- Easy to extend with new Unicode script blocks

## Future Enhancements

### Possible Additions
- **Script Density:** More/fewer symbols per word based on language complexity
- **Directional Text:** Right-to-left scripts for certain language families
- **Script Mixing:** Combine multiple Unicode blocks for hybrid languages
- **Audio Integration:** Different voice filters per script family

### Additional Unicode Blocks
- **Linear B:** `𐀀𐀁𐀂` (Ancient Greek syllabic)
- **Phoenician:** `𐤀𐤁𐤂` (Ancient Semitic)
- **Ogham:** `ᚁᚂᚃ` (Celtic tree alphabet)
- **Yi Syllables:** `ꀀꀁꀂ` (Chinese minority script)

## Testing

Run the demo script to see the unreadable characters in action:
```bash
python backend/test_fictional_script_simple.py
```

This demonstrates all script families with completely foreign, unreadable output that maintains word structure while being genuinely incomprehensible.

## Unicode Blocks Used

The system uses these completely unreadable Unicode ranges:
- **Tibetan:** `ཀ-ྱ` (U+0F00-U+0FFF) - Mystical flowing script
- **Runic:** `ᚠ-ᛯ` (U+16A0-U+16FF) - Angular ancient symbols  
- **Cuneiform:** `𒀀-𒎙` (U+12000-U+123FF) - Wedge-shaped marks
- **Geometric Shapes:** `◊-◲` (U+25A0-U+25FF) - Abstract symbols
- **Connector Marks:** `·‧⁞᭟᭞` - Between-character symbols

All characters are standard Unicode but **completely unreadable** to English speakers, creating true language immersion. 