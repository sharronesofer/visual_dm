"""
Language System Models for Population System (Business Logic)

Implements a forgiving language system based on Romance language relationships:
- Languages are grouped into families with natural partial comprehension
- Ancient languages serve as roots that influence modern languages
- Intelligence-based starting languages for player characters
- Progressive learning through abilities and exposure
- Integration with population system for cultural authenticity

This creates immersive linguistic depth without UX frustration.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random
import re

logger = logging.getLogger(__name__)


class LanguageFamily(Enum):
    """Language family classifications"""
    ANCIENT = "ancient"           # Root languages (Latin equivalent)
    COMMON_FAMILY = "common_family"     # Romance family equivalent
    ELDER_FAMILY = "elder_family"       # Celtic/Germanic equivalent  
    EASTERN_FAMILY = "eastern_family"   # Slavic equivalent
    EXOTIC_FAMILY = "exotic_family"     # Unrelated languages
    PLANAR = "planar"             # Celestial/Abyssal/etc
    TRADE_PIDGIN = "trade_pidgin"       # Mixed languages


class Language(Enum):
    """Available languages with their families"""
    # Ancient root languages
    ANCIENT_IMPERIAL = "ancient_imperial"  # Latin equivalent
    OLD_CELESTIAL = "old_celestial"        # Divine Latin
    PRIMORDIAL = "primordial"              # Elemental root
    
    # Common family (Romance equivalents)
    COMMON = "common"                      # Italian equivalent
    ELVISH = "elvish"                      # French equivalent  
    HALFLING = "halfling"                  # Spanish equivalent
    GNOMISH = "gnomish"                    # Portuguese equivalent
    
    # Elder family (Germanic/Celtic equivalents)
    DWARVEN = "dwarven"                    # English equivalent
    ORCISH = "orcish"                      # German equivalent
    GIANT = "giant"                        # Norse equivalent
    
    # Eastern family
    DRACONIC = "draconic"                  # Slavic equivalent
    GOBLIN = "goblin"                      # Hungarian equivalent
    
    # Exotic family (unrelated)
    SYLVAN = "sylvan"                      # Nature-based
    DRUIDIC = "druidic"                    # Secret druid language
    
    # Planar languages
    CELESTIAL = "celestial"                # Angelic
    ABYSSAL = "abyssal"                    # Demonic
    INFERNAL = "infernal"                  # Devilish
    
    # Trade languages
    TRADE_COMMON = "trade_common"          # Merchant pidgin
    SEA_CANT = "sea_cant"                  # Sailor pidgin


@dataclass
class LanguageRelationship:
    """Defines relationship between two languages"""
    base_language: Language
    related_language: Language
    comprehension_bonus: float  # 0.0 to 1.0 bonus for understanding
    relationship_type: str      # "family", "derived", "influenced", "pidgin"
    difficulty_modifier: float = 1.0  # Learning difficulty modifier


@dataclass
class LanguageProficiency:
    """Character's proficiency in a language"""
    language: Language
    comprehension_level: float  # 0.0 to 1.0
    speaking_level: float       # 0.0 to 1.0  
    literacy_level: float       # 0.0 to 1.0
    exposure_hours: int = 0     # Hours of exposure for natural learning
    formal_training: bool = False
    acquired_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SettlementLanguageProfile:
    """Language usage in a settlement"""
    settlement_id: str
    primary_language: Language
    secondary_languages: List[Language] = field(default_factory=list)
    trade_languages: List[Language] = field(default_factory=list)
    
    # Population linguistic characteristics
    language_diversity: float = 0.2  # How linguistically mixed (0.0 = homogeneous, 1.0 = very mixed)
    dialect_strength: float = 0.5    # How different local dialect is (0.0 = standard, 1.0 = very different)
    literacy_rate: float = 0.4       # Percentage who can read/write
    
    # Historical influences
    historical_languages: List[Language] = field(default_factory=list)  # Dead/ancient languages still in use
    recent_linguistic_changes: List[Dict[str, Any]] = field(default_factory=list)


class LanguageEngine:
    """Engine for managing language systems and comprehension"""
    
    def __init__(self):
        self.language_families = self._initialize_language_families()
        self.language_relationships = self._initialize_language_relationships()
        self.settlement_profiles: Dict[str, SettlementLanguageProfile] = {}
        self.character_proficiencies: Dict[str, List[LanguageProficiency]] = {}
        
        logger.info("Language Engine initialized with Romance-based language families")
    
    def _initialize_language_families(self) -> Dict[Language, LanguageFamily]:
        """Map languages to their families"""
        return {
            # Ancient root languages
            Language.ANCIENT_IMPERIAL: LanguageFamily.ANCIENT,
            Language.OLD_CELESTIAL: LanguageFamily.ANCIENT,
            Language.PRIMORDIAL: LanguageFamily.ANCIENT,
            
            # Common family (Romance)
            Language.COMMON: LanguageFamily.COMMON_FAMILY,
            Language.ELVISH: LanguageFamily.COMMON_FAMILY,
            Language.HALFLING: LanguageFamily.COMMON_FAMILY,
            Language.GNOMISH: LanguageFamily.COMMON_FAMILY,
            
            # Elder family (Germanic/Celtic)
            Language.DWARVEN: LanguageFamily.ELDER_FAMILY,
            Language.ORCISH: LanguageFamily.ELDER_FAMILY,
            Language.GIANT: LanguageFamily.ELDER_FAMILY,
            
            # Eastern family
            Language.DRACONIC: LanguageFamily.EASTERN_FAMILY,
            Language.GOBLIN: LanguageFamily.EASTERN_FAMILY,
            
            # Exotic
            Language.SYLVAN: LanguageFamily.EXOTIC_FAMILY,
            Language.DRUIDIC: LanguageFamily.EXOTIC_FAMILY,
            
            # Planar
            Language.CELESTIAL: LanguageFamily.PLANAR,
            Language.ABYSSAL: LanguageFamily.PLANAR,
            Language.INFERNAL: LanguageFamily.PLANAR,
            
            # Trade pidgins
            Language.TRADE_COMMON: LanguageFamily.TRADE_PIDGIN,
            Language.SEA_CANT: LanguageFamily.TRADE_PIDGIN
        }
    
    def _initialize_language_relationships(self) -> List[LanguageRelationship]:
        """Define relationships between languages (like Romance language family)"""
        relationships = []
        
        # Common family relationships (high mutual intelligibility)
        common_family = [Language.COMMON, Language.ELVISH, Language.HALFLING, Language.GNOMISH]
        for i, lang1 in enumerate(common_family):
            for lang2 in common_family[i+1:]:
                relationships.extend([
                    LanguageRelationship(lang1, lang2, 0.4, "family"),  # 40% base comprehension
                    LanguageRelationship(lang2, lang1, 0.4, "family")
                ])
        
        # Elder family relationships (moderate mutual intelligibility)
        elder_family = [Language.DWARVEN, Language.ORCISH, Language.GIANT]
        for i, lang1 in enumerate(elder_family):
            for lang2 in elder_family[i+1:]:
                relationships.extend([
                    LanguageRelationship(lang1, lang2, 0.3, "family"),
                    LanguageRelationship(lang2, lang1, 0.3, "family")
                ])
        
        # Eastern family relationships
        eastern_family = [Language.DRACONIC, Language.GOBLIN]
        relationships.extend([
            LanguageRelationship(Language.DRACONIC, Language.GOBLIN, 0.25, "family"),
            LanguageRelationship(Language.GOBLIN, Language.DRACONIC, 0.25, "family")
        ])
        
        # Ancient language influences (everyone gets some benefit from ancient languages)
        ancient_languages = [Language.ANCIENT_IMPERIAL, Language.OLD_CELESTIAL]
        modern_languages = [l for l in Language if l not in ancient_languages and l != Language.PRIMORDIAL]
        
        for ancient in ancient_languages:
            for modern in modern_languages:
                bonus = 0.2 if self.language_families.get(modern) == LanguageFamily.COMMON_FAMILY else 0.1
                relationships.append(
                    LanguageRelationship(ancient, modern, bonus, "derived")
                )
        
        # Trade language relationships (everyone understands trade pidgin a bit)
        trade_languages = [Language.TRADE_COMMON, Language.SEA_CANT]
        for trade_lang in trade_languages:
            for lang in modern_languages:
                if lang not in trade_languages:
                    relationships.append(
                        LanguageRelationship(trade_lang, lang, 0.15, "pidgin")
                    )
        
        # Cross-family influences (historical contact)
        cross_family_pairs = [
            (Language.COMMON, Language.DWARVEN, 0.2),      # Extensive trade contact
            (Language.ELVISH, Language.SYLVAN, 0.3),       # Nature connection
            (Language.DRACONIC, Language.ANCIENT_IMPERIAL, 0.4),  # Ancient heritage
            (Language.CELESTIAL, Language.OLD_CELESTIAL, 0.6),    # Divine connection
            (Language.ABYSSAL, Language.INFERNAL, 0.5),    # Planar similarity
        ]
        
        for lang1, lang2, bonus in cross_family_pairs:
            relationships.extend([
                LanguageRelationship(lang1, lang2, bonus, "influenced"),
                LanguageRelationship(lang2, lang1, bonus, "influenced")
            ])
        
        return relationships
    
    def create_character_starting_languages(
        self,
        character_id: str,
        intelligence_score: int,
        background_languages: Optional[List[Language]] = None
    ) -> List[LanguageProficiency]:
        """Create starting languages for a character based on intelligence"""
        proficiencies = []
        
        # Everyone gets Common
        proficiencies.append(LanguageProficiency(
            language=Language.COMMON,
            comprehension_level=1.0,
            speaking_level=1.0,
            literacy_level=0.8,  # Most people can read Common
            formal_training=True
        ))
        
        # Additional languages based on intelligence (14+ gets 1 extra, 16+ gets 2, etc.)
        bonus_languages = max(0, (intelligence_score - 12) // 2)
        
        # Add background languages first
        if background_languages:
            for lang in background_languages[:bonus_languages]:
                proficiencies.append(LanguageProficiency(
                    language=lang,
                    comprehension_level=0.8,
                    speaking_level=0.8,
                    literacy_level=0.5,
                    formal_training=True
                ))
                bonus_languages -= 1
        
        # Fill remaining slots with common languages
        common_choices = [Language.ELVISH, Language.DWARVEN, Language.HALFLING, Language.TRADE_COMMON]
        for i in range(bonus_languages):
            if i < len(common_choices):
                proficiencies.append(LanguageProficiency(
                    language=common_choices[i],
                    comprehension_level=0.6,
                    speaking_level=0.6,
                    literacy_level=0.3,
                    formal_training=False
                ))
        
        self.character_proficiencies[character_id] = proficiencies
        logger.info(f"Created starting languages for character {character_id}: {[p.language.value for p in proficiencies]}")
        return proficiencies
    
    def calculate_comprehension(
        self,
        character_id: str,
        target_language: Language,
        text_complexity: float = 0.5
    ) -> Tuple[float, List[str]]:
        """Calculate how well a character understands text in a target language"""
        
        if character_id not in self.character_proficiencies:
            return 0.0, ["Character language proficiencies not found"]
        
        proficiencies = self.character_proficiencies[character_id]
        character_languages = {p.language: p for p in proficiencies}
        
        # Direct knowledge
        if target_language in character_languages:
            base_comprehension = character_languages[target_language].comprehension_level
            complexity_penalty = text_complexity * 0.3  # Complex text is harder
            final_comprehension = max(0.1, base_comprehension - complexity_penalty)
            return final_comprehension, [f"Direct knowledge of {target_language.value}"]
        
        # Find best comprehension through related languages
        best_comprehension = 0.0
        comprehension_sources = []
        
        for known_lang, proficiency in character_languages.items():
            # Find relationships between known language and target
            for relationship in self.language_relationships:
                if relationship.base_language == known_lang and relationship.related_language == target_language:
                    # Comprehension bonus based on known language proficiency and relationship strength
                    bonus_comprehension = proficiency.comprehension_level * relationship.comprehension_bonus
                    
                    if bonus_comprehension > best_comprehension:
                        best_comprehension = bonus_comprehension
                        comprehension_sources = [f"{known_lang.value} -> {target_language.value} ({relationship.relationship_type})"]
                    elif bonus_comprehension == best_comprehension and bonus_comprehension > 0:
                        comprehension_sources.append(f"{known_lang.value} -> {target_language.value} ({relationship.relationship_type})")
        
        # Apply complexity penalty
        complexity_penalty = text_complexity * 0.5  # Harder for non-native speakers
        final_comprehension = max(0.0, best_comprehension - complexity_penalty)
        
        return final_comprehension, comprehension_sources
    
    def process_dialogue_comprehension(
        self,
        character_id: str,
        dialogue_text: str,
        speaker_language: Language,
        text_complexity: float = 0.5,
        context_clues: bool = True
    ) -> Dict[str, Any]:
        """Process dialogue text based on character's language comprehension"""
        
        comprehension_level, sources = self.calculate_comprehension(
            character_id, speaker_language, text_complexity
        )
        
        # Apply context clues bonus (gestures, expressions, etc.)
        if context_clues:
            comprehension_level = min(1.0, comprehension_level + 0.15)
        
        # Generate processed text based on comprehension level with language-specific script
        processed_text = self._generate_partial_text(dialogue_text, comprehension_level, speaker_language)
        
        # Determine emotional/tonal understanding (easier than words)
        emotional_comprehension = min(1.0, comprehension_level + 0.3)
        emotional_context = self._determine_emotional_context(dialogue_text, emotional_comprehension)
        
        return {
            "original_text": dialogue_text,
            "processed_text": processed_text,
            "comprehension_level": comprehension_level,
            "comprehension_sources": sources,
            "speaker_language": speaker_language.value,
            "emotional_context": emotional_context,
            "can_respond": comprehension_level >= 0.3,  # Need 30% to attempt response
            "learning_opportunity": comprehension_level < 0.9  # Can learn if not fluent
        }
    
    def _generate_partial_text(self, text: str, comprehension_level: float, speaker_language: Language = None) -> str:
        """Generate partially comprehensible text based on comprehension level"""
        if comprehension_level >= 0.95:
            return text
        
        words = text.split()
        if len(words) <= 1:
            return text if comprehension_level > 0.5 else self._generate_foreign_word(text, speaker_language)
        
        # Determine which words to obscure
        num_words_to_keep = int(len(words) * comprehension_level)
        
        # Always keep important words (proper nouns, numbers, simple words)
        important_words = []
        regular_words = []
        
        for i, word in enumerate(words):
            if (word[0].isupper() or  # Proper nouns
                word.isdigit() or     # Numbers
                len(word) <= 3 or     # Short words
                word.lower() in ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'from']):
                important_words.append(i)
            else:
                regular_words.append(i)
        
        # Keep all important words plus some regular words
        words_to_keep = set(important_words)
        regular_words_to_keep = max(0, num_words_to_keep - len(important_words))
        
        if regular_words_to_keep > 0 and regular_words:
            import random
            random.shuffle(regular_words)
            words_to_keep.update(regular_words[:regular_words_to_keep])
        
        # Generate final text with foreign script appropriate to the language
        result_words = []
        for i, word in enumerate(words):
            if i in words_to_keep:
                result_words.append(word)
            else:
                # Replace with foreign-looking script specific to the speaker's language
                foreign_word = self._generate_foreign_word(word, speaker_language)
                result_words.append(foreign_word)
        
        return " ".join(result_words)
    
    def _generate_foreign_word(self, original_word: str, speaker_language: Language = None) -> str:
        """
        Generate a foreign-looking word using completely unreadable fictional script characters.
        
        Uses Unicode characters from various non-Latin scripts and symbol blocks to create
        truly alien text that is completely incomprehensible to English readers.
        
        Args:
            original_word: The word to convert to foreign script
            speaker_language: The language being spoken (determines script style)
        """
        # Remove punctuation for processing
        import re
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
                '𒀀', '𒀁', '𒀂', '𒀃', '𒀄', '𒀅', '𒀆', '𒀇', '𒀈', '𒀉', '𒀊', '𒀋', '𒀌', '𒀍', '𒀎', '𒀏', '𒀐', '𒀑', '𒀒', '𒀓',
                '𒀔', '𒀕', '𒀖', '𒀗', '𒀘', '𒀙', '𒀚', '𒀛', '𒀜', '𒀝', '𒀞', '𒀟', '𒀠', '𒀡', '𒀢', '𒀣', '𒀤', '𒀥', '𒀦', '𒀧'
            ],
            'mystic': [
                # Geometric and mathematical symbols - looks otherworldly
                '◊', '◈', '◉', '◎', '○', '◐', '◑', '◒', '◓', '◔', '◕', '◖', '◗', '◘', '◙', '◚', '◛', '◜', '◝', '◞',
                '◟', '◠', '◡', '◢', '◣', '◤', '◥', '◦', '◧', '◨', '◩', '◪', '◫', '◬', '◭', '◮', '◯', '◰', '◱', '◲'
            ]
        }
        
        # Choose script set based on language or fallback to word length
        if speaker_language:
            script_style = self.get_script_style_for_language(speaker_language)
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
    
    def _determine_emotional_context(self, text: str, emotional_comprehension: float) -> List[str]:
        """Determine emotional context even with limited language comprehension"""
        emotional_indicators = []
        
        if emotional_comprehension >= 0.8:
            # Can understand subtle emotions
            if "!" in text:
                emotional_indicators.append("excited" if text.count("!") == 1 else "very excited")
            if "?" in text:
                emotional_indicators.append("questioning")
            if text.isupper():
                emotional_indicators.append("shouting")
            if "..." in text:
                emotional_indicators.append("hesitant")
        elif emotional_comprehension >= 0.5:
            # Basic emotional understanding
            if "!" in text or text.isupper():
                emotional_indicators.append("emotional")
            if "?" in text:
                emotional_indicators.append("asking something")
        elif emotional_comprehension >= 0.2:
            # Very basic tone
            if "!" in text or text.isupper():
                emotional_indicators.append("intense")
            else:
                emotional_indicators.append("calm")
        
        return emotional_indicators if emotional_indicators else ["neutral"]
    
    def create_settlement_language_profile(
        self,
        settlement_id: str,
        primary_language: Language,
        population_size: int,
        cultural_background: str = "mixed"
    ) -> SettlementLanguageProfile:
        """Create language profile for a settlement"""
        
        # Determine secondary languages based on cultural background and size
        secondary_languages = []
        trade_languages = [Language.TRADE_COMMON]
        
        if population_size > 1000:  # Large settlements are more diverse
            secondary_languages.extend([Language.COMMON, Language.ELVISH, Language.DWARVEN])
            trade_languages.append(Language.SEA_CANT)
        elif population_size > 500:  # Medium settlements
            secondary_languages.append(Language.COMMON if primary_language != Language.COMMON else Language.ELVISH)
        
        # Remove primary language from secondary
        secondary_languages = [lang for lang in secondary_languages if lang != primary_language]
        
        # Calculate diversity and dialect based on size and background
        base_diversity = min(0.8, population_size / 5000)  # Larger = more diverse
        diversity_modifier = {"isolated": -0.3, "crossroads": +0.4, "mixed": 0.0}.get(cultural_background, 0.0)
        language_diversity = max(0.1, min(0.9, base_diversity + diversity_modifier))
        
        dialect_strength = max(0.1, min(0.9, 0.5 + random.uniform(-0.2, 0.2)))
        literacy_rate = min(0.9, 0.3 + (population_size / 10000))  # Larger settlements = more literate
        
        profile = SettlementLanguageProfile(
            settlement_id=settlement_id,
            primary_language=primary_language,
            secondary_languages=secondary_languages,
            trade_languages=trade_languages,
            language_diversity=language_diversity,
            dialect_strength=dialect_strength,
            literacy_rate=literacy_rate
        )
        
        self.settlement_profiles[settlement_id] = profile
        logger.info(f"Created language profile for {settlement_id}: {primary_language.value} primary, {len(secondary_languages)} secondary")
        return profile
    
    def simulate_language_exposure(
        self,
        character_id: str,
        exposure_language: Language,
        hours: int,
        interaction_quality: float = 0.5
    ) -> Dict[str, Any]:
        """Simulate natural language learning through exposure"""
        
        if character_id not in self.character_proficiencies:
            return {"error": "Character not found"}
        
        proficiencies = self.character_proficiencies[character_id]
        character_languages = {p.language: p for p in proficiencies}
        
        # Find or create proficiency for this language
        if exposure_language in character_languages:
            proficiency = character_languages[exposure_language]
        else:
            # Create new basic proficiency
            proficiency = LanguageProficiency(
                language=exposure_language,
                comprehension_level=0.0,
                speaking_level=0.0,
                literacy_level=0.0
            )
            proficiencies.append(proficiency)
        
        # Calculate learning rate (modified by related languages)
        base_learning_rate = 0.001  # Very slow natural learning
        
        # Get bonus from related languages
        related_bonus = 0.0
        for known_lang, known_prof in character_languages.items():
            for relationship in self.language_relationships:
                if (relationship.base_language == known_lang and 
                    relationship.related_language == exposure_language):
                    related_bonus += known_prof.comprehension_level * relationship.comprehension_bonus * 0.5
        
        # Apply learning
        learning_rate = base_learning_rate * (1.0 + related_bonus) * interaction_quality
        comprehension_gain = hours * learning_rate
        speaking_gain = hours * learning_rate * 0.7  # Speaking develops slower
        
        old_comprehension = proficiency.comprehension_level
        proficiency.comprehension_level = min(0.8, proficiency.comprehension_level + comprehension_gain)  # Cap natural learning at 80%
        proficiency.speaking_level = min(0.6, proficiency.speaking_level + speaking_gain)  # Speaking caps lower
        proficiency.exposure_hours += hours
        
        return {
            "language": exposure_language.value,
            "hours_added": hours,
            "total_exposure_hours": proficiency.exposure_hours,
            "comprehension_gain": proficiency.comprehension_level - old_comprehension,
            "new_comprehension_level": proficiency.comprehension_level,
            "learning_rate_modifier": 1.0 + related_bonus
        }
    
    def get_language_learning_recommendations(self, character_id: str) -> List[Dict[str, Any]]:
        """Get recommendations for which languages would be most useful to learn"""
        if character_id not in self.character_proficiencies:
            return []
        
        proficiencies = self.character_proficiencies[character_id]
        known_languages = {p.language for p in proficiencies if p.comprehension_level >= 0.3}
        
        recommendations = []
        
        # Analyze all possible languages
        for target_lang in Language:
            if target_lang in known_languages:
                continue
            
            # Calculate potential benefit
            family_synergy = 0.0
            for known_lang in known_languages:
                for relationship in self.language_relationships:
                    if (relationship.base_language == known_lang and 
                        relationship.related_language == target_lang):
                        family_synergy += relationship.comprehension_bonus
            
            # Practical utility scores
            utility_scores = {
                Language.TRADE_COMMON: 0.9,  # Very practical
                Language.ELVISH: 0.7,       # Common cultural language
                Language.DWARVEN: 0.7,      # Common trading partner
                Language.ANCIENT_IMPERIAL: 0.6,  # Historical texts
                Language.CELESTIAL: 0.4,    # Specialized but powerful
                Language.DRACONIC: 0.5,     # Magical knowledge
            }
            
            utility = utility_scores.get(target_lang, 0.3)
            learning_ease = family_synergy
            
            recommendations.append({
                "language": target_lang.value,
                "utility_score": utility,
                "learning_ease": learning_ease,
                "total_benefit": utility + learning_ease,
                "family_synergy": family_synergy > 0.2,
                "reason": self._get_learning_reason(target_lang, family_synergy, utility)
            })
        
        # Sort by total benefit
        recommendations.sort(key=lambda x: x["total_benefit"], reverse=True)
        return recommendations[:5]  # Top 5 recommendations
    
    def _get_learning_reason(self, language: Language, family_synergy: float, utility: float) -> str:
        """Generate a reason why this language would be good to learn"""
        reasons = []
        
        if family_synergy > 0.3:
            reasons.append("easy to learn due to related languages you know")
        
        utility_reasons = {
            Language.TRADE_COMMON: "essential for commerce and trade",
            Language.ELVISH: "widely spoken and culturally significant",
            Language.DWARVEN: "useful for trade and crafting knowledge",
            Language.ANCIENT_IMPERIAL: "unlocks historical texts and scholarly works",
            Language.CELESTIAL: "grants access to divine knowledge",
            Language.DRACONIC: "provides access to magical lore",
            Language.ABYSSAL: "useful for dealing with dark entities",
            Language.SYLVAN: "helpful for nature-based interactions"
        }
        
        if language in utility_reasons:
            reasons.append(utility_reasons[language])
        
        return "; ".join(reasons) if reasons else "expands communication options"

    def find_best_common_language(
        self,
        character1_id: str,
        character2_id: str,
        minimum_comprehension: float = 0.3,
        prefer_trade_languages: bool = True
    ) -> Optional[Tuple[Language, float, str]]:
        """
        Find the best language for communication between two characters.
        
        This implements automatic language resolution - prioritizing communication
        over realism to avoid frustrating language barriers.
        
        Args:
            character1_id: First character's ID
            character2_id: Second character's ID  
            minimum_comprehension: Minimum comprehension level needed (0.3 = 30%)
            prefer_trade_languages: Prioritize trade languages for strangers
            
        Returns:
            Tuple of (Language, mutual_comprehension_score, explanation) or None
        """
        if character1_id not in self.character_proficiencies or character2_id not in self.character_proficiencies:
            # Fallback to Common if either character's languages aren't loaded
            return (Language.COMMON, 1.0, "Defaulting to Common for unregistered character")
        
        char1_langs = {p.language: p for p in self.character_proficiencies[character1_id]}
        char2_langs = {p.language: p for p in self.character_proficiencies[character2_id]}
        
        best_options = []
        
        # 1. Check for perfect matches (both know the language well)
        for lang in char1_langs:
            if lang in char2_langs:
                char1_comp = char1_langs[lang].comprehension_level
                char2_comp = char2_langs[lang].comprehension_level
                avg_comprehension = (char1_comp + char2_comp) / 2.0
                
                if avg_comprehension >= minimum_comprehension:
                    # Bonus for trade languages in initial meetings
                    bonus = 0.1 if self.language_families.get(lang) == LanguageFamily.TRADE_PIDGIN else 0.0
                    if prefer_trade_languages and self.language_families.get(lang) == LanguageFamily.TRADE_PIDGIN:
                        bonus += 0.2
                    
                    best_options.append((
                        lang, 
                        min(1.0, avg_comprehension + bonus),
                        f"Both characters know {lang.value}"
                    ))
        
        # 2. Check for family relationships (Romance language style comprehension)
        if not best_options or max(opt[1] for opt in best_options) < 0.7:
            for lang1 in char1_langs:
                for lang2 in char2_langs:
                    if lang1 != lang2:
                        # Check if languages are related
                        comprehension1, _ = self.calculate_comprehension(character1_id, lang2)
                        comprehension2, _ = self.calculate_comprehension(character2_id, lang1)
                        
                        # Use the better direction
                        if comprehension1 >= minimum_comprehension and comprehension2 >= minimum_comprehension:
                            avg_mutual = (comprehension1 + comprehension2) / 2.0
                            
                            # Choose the language the speaker knows better
                            speaker_lang = lang1 if char1_langs[lang1].comprehension_level > char2_langs[lang2].comprehension_level else lang2
                            
                            best_options.append((
                                speaker_lang,
                                avg_mutual,
                                f"Related languages: {lang1.value} ↔ {lang2.value}"
                            ))
        
        # 3. Fallback to Common with partial comprehension
        if not best_options:
            # Everyone has some understanding of Common (like English in modern world)
            common_comp = 0.6  # Assume basic Common comprehension
            best_options.append((
                Language.COMMON,
                common_comp,
                "Fallback to Common with basic comprehension"
            ))
        
        # 4. If still nothing, use Trade Common (universal fallback)
        if not best_options:
            best_options.append((
                Language.TRADE_COMMON,
                0.4,
                "Using trade pidgin as last resort"
            ))
        
        # Return the best option
        best_options.sort(key=lambda x: x[1], reverse=True)
        return best_options[0]

    def create_dialogue_context(
        self,
        speaker_id: str,
        listener_id: str,
        dialogue_text: str,
        force_language: Optional[Language] = None
    ) -> Dict[str, Any]:
        """
        Create dialogue context with automatic language resolution.
        
        This handles the full dialogue comprehension process with automatic
        language selection, making communication seamless for players.
        
        Args:
            speaker_id: Character who is speaking
            listener_id: Character who is listening  
            dialogue_text: The text being spoken
            force_language: Override automatic language selection
            
        Returns:
            Dialogue context with comprehension data
        """
        # Determine the language being used
        if force_language:
            selected_language = force_language
            explanation = f"Forced to use {force_language.value}"
            mutual_score = 1.0
        else:
            language_result = self.find_best_common_language(speaker_id, listener_id)
            if language_result:
                selected_language, mutual_score, explanation = language_result
            else:
                selected_language = Language.COMMON
                mutual_score = 0.5
                explanation = "No common language found, using Common"
        
        # Process comprehension for the listener
        comprehension_data = self.process_dialogue_comprehension(
            listener_id,
            dialogue_text,
            selected_language,
            text_complexity=0.5,
            context_clues=True
        )
        
        return {
            "speaker_id": speaker_id,
            "listener_id": listener_id,
            "selected_language": selected_language.value,
            "mutual_comprehension_score": mutual_score,
            "language_explanation": explanation,
            "original_text": dialogue_text,
            "processed_text": comprehension_data["processed_text"],
            "comprehension_level": comprehension_data["comprehension_level"],
            "emotional_context": comprehension_data["emotional_context"],
            "can_respond": comprehension_data["can_respond"],
            "learning_opportunity": comprehension_data["learning_opportunity"],
            "auto_resolved": force_language is None
        }

    def get_script_style_for_language(self, language: Language) -> str:
        """
        Get the appropriate script style for different languages to maintain consistency.
        
        This ensures that Elvish always uses the same script style, Draconic another, etc.
        """
        language_script_mapping = {
            Language.ELVISH: 'elvish',
            Language.SYLVAN: 'elvish',
            Language.DRACONIC: 'draconic',
            Language.ANCIENT_IMPERIAL: 'ancient',
            Language.OLD_CELESTIAL: 'ancient',
            Language.PRIMORDIAL: 'ancient',
            Language.CELESTIAL: 'mystic',
            Language.ABYSSAL: 'draconic',
            Language.INFERNAL: 'draconic',
            Language.GOBLIN: 'draconic',
            Language.ORCISH: 'draconic',
            Language.GIANT: 'ancient',
            Language.DWARVEN: 'ancient',
            Language.GNOMISH: 'elvish',
            Language.HALFLING: 'elvish',
            Language.DRUIDIC: 'mystic'
        }
        
        return language_script_mapping.get(language, 'mystic')


# Global language engine instance
language_engine = LanguageEngine()

# Export functions
__all__ = [
    "LanguageFamily",
    "Language", 
    "LanguageRelationship",
    "LanguageProficiency",
    "SettlementLanguageProfile",
    "LanguageEngine",
    "language_engine"
] 