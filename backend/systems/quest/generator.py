"""
Quest Generation Business Logic

This module provides pure business logic for quest generation
according to the Development Bible standards.
Enhanced with template system integration.
"""

import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4

from .models import (
    QuestData,
    QuestStepData,
    QuestRewardData,
    QuestDifficulty,
    QuestTheme,
    QuestStatus,
    QuestGenerationService
)


class QuestGeneratorService(QuestGenerationService):
    """Pure business logic service for quest generation with template support"""
    
    def __init__(self, config_loader=None):
        """
        Initialize generator with optional template system
        
        Args:
            config_loader: Optional configuration loader for template access
        """
        self.config_loader = config_loader
        
        # Business configuration for quest generation
        self.config = {
            'step_count_by_difficulty': {
                QuestDifficulty.EASY: (1, 2),
                QuestDifficulty.MEDIUM: (2, 3),
                QuestDifficulty.HARD: (3, 4),
                QuestDifficulty.EPIC: (4, 6)
            },
            'base_rewards_by_difficulty': {
                QuestDifficulty.EASY: {'gold': 50, 'experience': 100},
                QuestDifficulty.MEDIUM: {'gold': 150, 'experience': 300},
                QuestDifficulty.HARD: {'gold': 400, 'experience': 800},
                QuestDifficulty.EPIC: {'gold': 1000, 'experience': 2000}
            },
            'level_multiplier': 0.1,
            'default_expiry_days': 7
        }
        
        # Business data for quest generation (fallback templates)
        self.quest_templates = {
            QuestTheme.COMBAT: {
                'title_prefixes': ['Slay the', 'Defeat the', 'Conquer the', 'Vanquish the'],
                'nouns': ['Dragon', 'Beast', 'Warband', 'Champion', 'Demon', 'Giant'],
                'step_types': ['kill', 'defeat_boss', 'clear_area']
            },
            QuestTheme.EXPLORATION: {
                'title_prefixes': ['Discover the', 'Find the', 'Explore the', 'Search for the'],
                'nouns': ['Ruins', 'Cavern', 'Shrine', 'Artifact', 'Temple', 'Treasure'],
                'step_types': ['explore', 'discover', 'collect']
            },
            QuestTheme.SOCIAL: {
                'title_prefixes': ['Convince the', 'Persuade the', 'Negotiate with the', 'Mediate between'],
                'nouns': ['Noble', 'Merchant', 'Guild', 'Council', 'Elder', 'Leader'],
                'step_types': ['dialogue', 'persuade', 'deliver_message']
            },
            QuestTheme.MYSTERY: {
                'title_prefixes': ['Investigate the', 'Uncover the', 'Solve the', 'Decipher the'],
                'nouns': ['Conspiracy', 'Disappearance', 'Secret', 'Prophecy', 'Murder', 'Theft'],
                'step_types': ['investigate', 'gather_clues', 'interrogate']
            },
            QuestTheme.CRAFTING: {
                'title_prefixes': ['Craft the', 'Create the', 'Forge the', 'Build the'],
                'nouns': ['Weapon', 'Armor', 'Tool', 'Potion', 'Artifact', 'Device'],
                'step_types': ['gather_materials', 'craft_item', 'deliver_item']
            },
            QuestTheme.TRADE: {
                'title_prefixes': ['Deliver the', 'Transport the', 'Trade the', 'Sell the'],
                'nouns': ['Goods', 'Message', 'Cargo', 'Package', 'Supplies', 'Documents'],
                'step_types': ['collect_goods', 'transport', 'deliver']
            },
            QuestTheme.AID: {
                'title_prefixes': ['Help the', 'Assist the', 'Rescue the', 'Heal the'],
                'nouns': ['Villager', 'Traveler', 'Wounded', 'Lost', 'Sick', 'Trapped'],
                'step_types': ['rescue', 'heal', 'escort', 'provide_aid']
            },
            QuestTheme.KNOWLEDGE: {
                'title_prefixes': ['Learn about the', 'Study the', 'Research the', 'Understand the'],
                'nouns': ['Ancient Text', 'Ritual', 'Language', 'History', 'Magic', 'Lore'],
                'step_types': ['study', 'research', 'translate', 'learn']
            },
            QuestTheme.GENERAL: {
                'title_prefixes': ['Complete the', 'Fulfill the', 'Accomplish the', 'Finish the'],
                'nouns': ['Task', 'Mission', 'Request', 'Assignment', 'Job', 'Duty'],
                'step_types': ['collect', 'deliver', 'explore', 'dialogue']
            }
        }
        
        self.difficulty_adjectives = {
            QuestDifficulty.EASY: ['Curious', 'Local', 'Minor', 'Small', 'Simple'],
            QuestDifficulty.MEDIUM: ['Dangerous', 'Forgotten', 'Hidden', 'Valuable', 'Important'],
            QuestDifficulty.HARD: ['Ancient', 'Cursed', 'Legendary', 'Powerful', 'Forbidden'],
            QuestDifficulty.EPIC: ['Dreadful', 'Divine', 'Infernal', 'Primordial', 'World-Shaking']
        }

    def generate_quest_for_npc(self, npc_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[QuestData]:
        """Generate a quest for an NPC using templates when available"""
        if context is None:
            context = {}
            
        # Try template-based generation first
        if self.config_loader:
            template_quest = self._generate_from_templates(npc_data, context)
            if template_quest:
                return template_quest
        
        # Fallback to algorithmic generation
        return self._generate_algorithmic_quest(npc_data, context)

    def generate_quest_steps(self, theme: QuestTheme, difficulty: QuestDifficulty, context: Dict[str, Any]) -> List[QuestStepData]:
        """Generate quest steps for theme and difficulty"""
        steps = []
        step_count_range = self.config['step_count_by_difficulty'][difficulty]
        step_count = random.randint(*step_count_range)
        
        template = self.quest_templates.get(theme, self.quest_templates[QuestTheme.GENERAL])
        step_types = template['step_types']
        
        for i in range(step_count):
            step_type = random.choice(step_types)
            step = self._generate_step_by_type(step_type, i + 1, theme, difficulty, context)
            steps.append(step)
        
        return steps

    def generate_quest_rewards(self, difficulty: QuestDifficulty, level: int) -> QuestRewardData:
        """Generate quest rewards based on difficulty and level"""
        base_rewards = self.config['base_rewards_by_difficulty'][difficulty]
        level_bonus = level * self.config['level_multiplier']
        
        gold = int(base_rewards['gold'] * (1 + level_bonus))
        experience = int(base_rewards['experience'] * (1 + level_bonus))
        
        # Generate item rewards based on difficulty
        items = self._generate_item_rewards(difficulty, level)
        
        return QuestRewardData(
            gold=gold,
            experience=experience,
            reputation={},
            items=items,
            special={}
        )

    def _generate_from_templates(self, npc_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[QuestData]:
        """Generate quest using template system based on NPC data"""
        try:
            # Determine appropriate theme based on NPC
            theme = self._determine_theme_from_profession(npc_data.get('profession', 'commoner'))
            difficulty = self._determine_difficulty_from_context(npc_data, context)
            
            # Get matching templates
            templates = self._get_matching_templates(theme, difficulty)
            if not templates:
                return None
            
            # Select random template
            template = random.choice(templates)
            
            # Add NPC context
            template_context = {
                **context,
                'npc': npc_data,
                'npc_name': npc_data.get('name', 'Someone'),
                'npc_profession': npc_data.get('profession', 'citizen'),
                'npc_level': npc_data.get('level', 1)
            }
            
            return self._instantiate_template(template, template_context)
            
        except Exception:
            # Fallback on any template error
            return None

    def _instantiate_template(self, template: Dict[str, Any], context: Dict[str, Any]) -> QuestData:
        """Create a quest instance from a template"""
        # Template interpolation for dynamic content
        title = self._interpolate_string(template.get('title', 'Quest'), context)
        description = self._interpolate_string(template.get('description', 'Complete this quest'), context)
        
        # Parse template parameters
        theme = QuestTheme(template.get('theme', 'general'))
        difficulty = QuestDifficulty(template.get('difficulty', 'medium'))
        level = template.get('level', context.get('npc_level', 5))
        
        # Generate steps from template
        steps = self._generate_steps_from_template(template.get('steps', []), context)
        
        # Generate rewards from template
        rewards = self._generate_rewards_from_template(template.get('rewards', {}), difficulty, context)
        
        # Create quest data
        return QuestData(
            id=uuid4(),
            title=title,
            description=description,
            status=QuestStatus.PENDING,
            difficulty=difficulty,
            theme=theme,
            npc_id=context.get('npc', {}).get('id'),
            player_id=None,
            location_id=context.get('location_id'),
            level=level,
            steps=steps,
            rewards=rewards,
            is_main_quest=template.get('is_main_quest', False),
            tags=template.get('tags', []),
            properties={
                'template_id': template.get('id'),
                'generated_at': datetime.utcnow().isoformat()
            },
            created_at=datetime.utcnow(),
            updated_at=None,
            expires_at=self._calculate_expiry_date(difficulty)
        )

    def _generate_steps_from_template(self, step_templates: List[Dict[str, Any]], context: Dict[str, Any]) -> List[QuestStepData]:
        """Generate steps from template"""
        steps = []
        for i, step_template in enumerate(step_templates):
            title = self._interpolate_string(step_template.get('title', f'Step {i+1}'), context)
            description = self._interpolate_string(step_template.get('description', 'Complete this step'), context)
            
            step = QuestStepData(
                id=i + 1,
                title=title,
                description=description,
                completed=False,
                required=step_template.get('required', True),
                order=i,
                metadata=step_template.get('metadata', {})
            )
            steps.append(step)
        
        return steps

    def _generate_rewards_from_template(self, reward_template: Dict[str, Any], difficulty: QuestDifficulty, context: Dict[str, Any]) -> QuestRewardData:
        """Generate rewards from template"""
        if not reward_template:
            return self.generate_quest_rewards(difficulty, context.get('npc_level', 5))
        
        return QuestRewardData(
            gold=reward_template.get('gold', 0),
            experience=reward_template.get('experience', 0),
            reputation=reward_template.get('reputation', {}),
            items=reward_template.get('items', []),
            special=reward_template.get('special', {})
        )

    def _get_matching_templates(self, theme: QuestTheme, difficulty: QuestDifficulty) -> List[Dict[str, Any]]:
        """Get templates matching theme and difficulty"""
        if not self.config_loader:
            return []
        
        theme_templates = self.config_loader.get_templates_by_theme(theme.value)
        difficulty_templates = self.config_loader.get_templates_by_difficulty(difficulty.value)
        
        return [t for t in theme_templates if t in difficulty_templates]

    def _interpolate_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """Simple template string interpolation"""
        result = template_string
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result

    def _calculate_expiry_date(self, difficulty: QuestDifficulty) -> Optional[datetime]:
        """Calculate quest expiry date based on difficulty"""
        days_by_difficulty = {
            QuestDifficulty.EASY: 3,
            QuestDifficulty.MEDIUM: 7,
            QuestDifficulty.HARD: 14,
            QuestDifficulty.EPIC: 30
        }
        days = days_by_difficulty.get(difficulty, self.config['default_expiry_days'])
        return datetime.utcnow() + timedelta(days=days)

    def _generate_algorithmic_quest(self, npc_data: Dict[str, Any], context: Dict[str, Any]) -> QuestData:
        """Generate quest algorithmically without templates"""
        theme = self._determine_theme_from_profession(npc_data.get('profession', 'commoner'))
        difficulty = self._determine_difficulty_from_context(npc_data, context)
        
        return self._generate_algorithmic_quest_with_params(theme, difficulty, context, npc_data)

    def _generate_algorithmic_quest_with_params(
        self, 
        theme: QuestTheme, 
        difficulty: QuestDifficulty, 
        context: Dict[str, Any], 
        npc_data: Dict[str, Any] = None
    ) -> QuestData:
        """Generate quest with specific parameters algorithmically"""
        if npc_data is None:
            npc_data = {}
        
        # Generate quest components
        title = self.generate_quest_title(theme, difficulty)
        description = self._generate_quest_description(theme, difficulty, npc_data)
        level = npc_data.get('level', context.get('default_level', 5))
        steps = self.generate_quest_steps(theme, difficulty, context)
        rewards = self.generate_quest_rewards(difficulty, level)
        
        return QuestData(
            id=uuid4(),
            title=title,
            description=description,
            status=QuestStatus.PENDING,
            difficulty=difficulty,
            theme=theme,
            npc_id=npc_data.get('id'),
            player_id=None,
            location_id=context.get('location_id'),
            level=level,
            steps=steps,
            rewards=rewards,
            properties={
                'generation_method': 'algorithmic',
                'generated_at': datetime.utcnow().isoformat()
            },
            created_at=datetime.utcnow(),
            expires_at=self._calculate_expiry_date(difficulty)
        )

    def generate_quest_title(self, theme: QuestTheme, difficulty: QuestDifficulty) -> str:
        """Generate quest title"""
        template = self.quest_templates.get(theme, self.quest_templates[QuestTheme.GENERAL])
        prefix = random.choice(template['title_prefixes'])
        noun = random.choice(template['nouns'])
        adjective = random.choice(self.difficulty_adjectives[difficulty])
        
        return f"{prefix} {adjective} {noun}"

    def _determine_theme_from_profession(self, profession: str) -> QuestTheme:
        """Determine quest theme based on NPC profession"""
        profession_themes = {
            'blacksmith': QuestTheme.CRAFTING,
            'warrior': QuestTheme.COMBAT,
            'merchant': QuestTheme.TRADE,
            'scholar': QuestTheme.KNOWLEDGE,
            'guard': QuestTheme.COMBAT,
            'healer': QuestTheme.AID,
            'explorer': QuestTheme.EXPLORATION,
            'diplomat': QuestTheme.SOCIAL,
            'detective': QuestTheme.MYSTERY,
            'commoner': QuestTheme.GENERAL
        }
        return profession_themes.get(profession.lower(), QuestTheme.GENERAL)

    def _determine_difficulty_from_context(self, npc_data: Dict[str, Any], context: Dict[str, Any]) -> QuestDifficulty:
        """Determine quest difficulty based on context"""
        npc_level = npc_data.get('level', 5)
        player_level = context.get('player_level', 5)
        location_danger = context.get('location_danger_level', 1)
        
        # Calculate base difficulty from levels
        level_diff = npc_level - player_level
        
        if level_diff <= -3 or location_danger <= 2:
            return QuestDifficulty.EASY
        elif level_diff <= 0 or location_danger <= 4:
            return QuestDifficulty.MEDIUM
        elif level_diff <= 3 or location_danger <= 7:
            return QuestDifficulty.HARD
        else:
            return QuestDifficulty.EPIC

    def _generate_quest_description(self, theme: QuestTheme, difficulty: QuestDifficulty, npc_data: Dict[str, Any]) -> str:
        """Generate quest description"""
        npc_name = npc_data.get('name', 'A local resident')
        profession = npc_data.get('profession', 'citizen')
        
        theme_descriptions = {
            QuestTheme.COMBAT: f"{npc_name} the {profession} needs help dealing with dangerous creatures threatening the area.",
            QuestTheme.EXPLORATION: f"{npc_name} the {profession} seeks brave adventurers to explore unknown territories.",
            QuestTheme.SOCIAL: f"{npc_name} the {profession} requires assistance with delicate negotiations.",
            QuestTheme.MYSTERY: f"{npc_name} the {profession} has uncovered strange occurrences that need investigation.",
            QuestTheme.CRAFTING: f"{npc_name} the {profession} needs skilled hands to create something important.",
            QuestTheme.TRADE: f"{npc_name} the {profession} requires reliable couriers for valuable cargo.",
            QuestTheme.AID: f"{npc_name} the {profession} desperately needs help with a crisis.",
            QuestTheme.KNOWLEDGE: f"{npc_name} the {profession} seeks wisdom about ancient mysteries.",
            QuestTheme.GENERAL: f"{npc_name} the {profession} has an important task that needs completion."
        }
        
        return theme_descriptions.get(theme, "A quest awaits.")

    def _generate_step_by_type(
        self, 
        step_type: str, 
        step_id: int, 
        theme: QuestTheme, 
        difficulty: QuestDifficulty, 
        context: Dict[str, Any]
    ) -> QuestStepData:
        """Generate a specific quest step by type"""
        step_generators = {
            'kill': lambda: QuestStepData(
                id=step_id,
                title=f"Eliminate {random.choice(['enemies', 'creatures', 'threats'])}",
                description=f"Defeat the hostile forces in the area.",
                completed=False,
                required=True,
                order=step_id - 1,
                metadata={'type': 'combat', 'targets': random.randint(3, 8)}
            ),
            'collect': lambda: QuestStepData(
                id=step_id,
                title=f"Gather {random.choice(['items', 'materials', 'resources'])}",
                description=f"Collect the required materials.",
                completed=False,
                required=True,
                order=step_id - 1,
                metadata={'type': 'collection', 'quantity': random.randint(3, 10)}
            ),
            'deliver': lambda: QuestStepData(
                id=step_id,
                title=f"Deliver to destination",
                description=f"Take the items to their intended recipient.",
                completed=False,
                required=True,
                order=step_id - 1,
                metadata={'type': 'delivery'}
            ),
            'explore': lambda: QuestStepData(
                id=step_id,
                title=f"Explore the area",
                description=f"Investigate the location thoroughly.",
                completed=False,
                required=True,
                order=step_id - 1,
                metadata={'type': 'exploration'}
            )
        }
        
        generator = step_generators.get(step_type, step_generators['collect'])
        return generator()

    def _generate_item_rewards(self, difficulty: QuestDifficulty, level: int) -> List[Dict[str, Any]]:
        """Generate item rewards based on difficulty and level"""
        item_chances = {
            QuestDifficulty.EASY: 0.2,
            QuestDifficulty.MEDIUM: 0.4,
            QuestDifficulty.HARD: 0.6,
            QuestDifficulty.EPIC: 0.8
        }
        
        items = []
        if random.random() < item_chances[difficulty]:
            item_types = ['weapon', 'armor', 'accessory', 'consumable']
            item_type = random.choice(item_types)
            
            item = {
                'id': f"{item_type}_{level}_{difficulty.value}",
                'type': item_type,
                'level': level,
                'rarity': difficulty.value,
                'quantity': 1
            }
            items.append(item)
        
        return items


# Alias for backward compatibility
QuestGenerator = QuestGeneratorService 