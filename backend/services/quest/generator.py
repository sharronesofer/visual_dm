"""
Quest Generation Business Logic

This module provides pure business logic for quest generation
according to the Development Bible standards.
Enhanced with template system integration.
"""

import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .models import (
    QuestData,
    QuestStepData,
    QuestRewardData,
    QuestDifficulty,
    QuestTheme,
    QuestStatus,
    QuestGenerationService
)


class QuestGenerator:
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

    def generate_quest_for_npc(self, npc_data: Dict[str, Any], context: Dict[str, Any] = None) -> Optional[QuestData]:
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
    
    def generate_quest_from_template(self, template_id: str, context: Dict[str, Any]) -> Optional[QuestData]:
        """
        Generate a quest from a specific template
        
        Args:
            template_id: ID of the template to use
            context: Context data for template interpolation
            
        Returns:
            Generated quest or None if template not found
        """
        if not self.config_loader:
            return None
        
        template = self.config_loader.get_template_by_id(template_id)
        if not template:
            return None
        
        return self._instantiate_template(template, context)
    
    def generate_quest_by_theme(self, theme: QuestTheme, difficulty: QuestDifficulty, context: Dict[str, Any] = None) -> Optional[QuestData]:
        """
        Generate a quest for a specific theme and difficulty using templates
        
        Args:
            theme: Desired quest theme
            difficulty: Desired quest difficulty  
            context: Additional context
            
        Returns:
            Generated quest or None
        """
        if context is None:
            context = {}
        
        if self.config_loader:
            # Get templates matching theme and difficulty
            theme_templates = self.config_loader.get_templates_by_theme(theme.value)
            difficulty_templates = self.config_loader.get_templates_by_difficulty(difficulty.value)
            
            # Find templates that match both criteria
            matching_templates = [
                t for t in theme_templates 
                if t in difficulty_templates
            ]
            
            if matching_templates:
                template = random.choice(matching_templates)
                return self._instantiate_template(template, context)
        
        # Fallback to algorithmic generation
        return self._generate_algorithmic_quest_with_params(theme, difficulty, context)
    
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
        from uuid import uuid4
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
                'generated_at': datetime.now().isoformat()
            },
            created_at=datetime.now(),
            updated_at=None,
            expires_at=self._calculate_expiry_date(difficulty)
        )
    
    def _generate_steps_from_template(self, step_templates: List[Dict[str, Any]], context: Dict[str, Any]) -> List[QuestStepData]:
        """Generate quest steps from template definitions"""
        steps = []
        
        for i, step_template in enumerate(step_templates):
            step = QuestStepData(
                id=step_template.get('id', i + 1),
                title=self._interpolate_string(step_template.get('title', f'Step {i + 1}'), context),
                description=self._interpolate_string(step_template.get('description', 'Complete this step'), context),
                completed=False,
                required=step_template.get('required', True),
                order=step_template.get('order', i + 1),
                metadata=step_template.get('metadata', {})
            )
            steps.append(step)
        
        return steps
    
    def _generate_rewards_from_template(self, reward_template: Dict[str, Any], difficulty: QuestDifficulty, context: Dict[str, Any]) -> QuestRewardData:
        """Generate quest rewards from template with difficulty scaling"""
        base_gold = reward_template.get('base_gold', 50)
        base_exp = reward_template.get('base_experience', 100)
        
        # Apply difficulty multipliers
        multipliers = {
            QuestDifficulty.EASY: 1.0,
            QuestDifficulty.MEDIUM: 1.5,
            QuestDifficulty.HARD: 2.0,
            QuestDifficulty.EPIC: 3.0
        }
        multiplier = multipliers.get(difficulty, 1.0)
        
        return QuestRewardData(
            gold=int(base_gold * multiplier),
            experience=int(base_exp * multiplier),
            reputation=reward_template.get('reputation', {}),
            items=reward_template.get('items', []),
            special=reward_template.get('special', {})
        )
    
    def _get_matching_templates(self, theme: QuestTheme, difficulty: QuestDifficulty) -> List[Dict[str, Any]]:
        """Get templates matching theme and difficulty"""
        if not self.config_loader:
            return []
        
        all_templates = self.config_loader.get_quest_templates()
        return [
            t for t in all_templates 
            if t.get('theme') == theme.value and t.get('difficulty') == difficulty.value
        ]
    
    def _interpolate_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """Simple string interpolation for templates"""
        try:
            # Simple placeholder replacement: {npc_name}, {location}, etc.
            result = template_string
            for key, value in context.items():
                if isinstance(value, (str, int, float)):
                    result = result.replace(f'{{{key}}}', str(value))
                elif isinstance(value, dict) and 'name' in value:
                    result = result.replace(f'{{{key}_name}}', str(value['name']))
            return result
        except Exception:
            return template_string
    
    def _calculate_expiry_date(self, difficulty: QuestDifficulty) -> Optional[datetime]:
        """Calculate quest expiry based on difficulty"""
        expiry_days = {
            QuestDifficulty.EASY: 7,
            QuestDifficulty.MEDIUM: 14,
            QuestDifficulty.HARD: 21,
            QuestDifficulty.EPIC: 30
        }
        
        days = expiry_days.get(difficulty, 14)
        return datetime.now() + timedelta(days=days)
    
    def _generate_algorithmic_quest(self, npc_data: Dict[str, Any], context: Dict[str, Any]) -> QuestData:
        """Fallback algorithmic quest generation (existing logic)"""
        # Extract NPC characteristics
        npc_profession = npc_data.get('profession', 'commoner')
        npc_personality = npc_data.get('personality', {})
        npc_location = npc_data.get('location_id')
        npc_level = npc_data.get('level', 1)
        
        # Determine quest theme based on NPC profession
        theme = self._determine_theme_from_profession(npc_profession)
        
        # Determine difficulty based on NPC importance and context
        difficulty = self._determine_difficulty_from_context(npc_data, context)
        
        return self._generate_algorithmic_quest_with_params(theme, difficulty, context, npc_data)
    
    def _generate_algorithmic_quest_with_params(self, theme: QuestTheme, difficulty: QuestDifficulty, context: Dict[str, Any], npc_data: Dict[str, Any] = None) -> QuestData:
        """Generate quest using algorithmic approach (existing logic)"""
        if npc_data is None:
            npc_data = context.get('npc', {})
        
        # Generate quest title
        title = self.generate_quest_title(theme, difficulty)
        
        # Generate quest description
        description = self._generate_quest_description(theme, difficulty, npc_data)
        
        # Generate quest steps
        steps = self.generate_quest_steps(theme, difficulty, context)
        
        # Generate rewards
        rewards = self.generate_quest_rewards(difficulty, npc_data.get('level', 1))
        
        # Calculate expiry date
        expires_at = datetime.utcnow() + timedelta(days=self.config['default_expiry_days'])
        
        # Create quest data
        from uuid import uuid4
        quest = QuestData(
            id=uuid4(),
            title=title,
            description=description,
            status=QuestStatus.PENDING,
            difficulty=difficulty,
            theme=theme,
            npc_id=npc_data.get('id'),
            location_id=npc_data.get('location_id'),
            level=npc_data.get('level', 1),
            steps=steps,
            rewards=rewards,
            properties={
                'generated_from_npc': True,
                'npc_profession': npc_data.get('profession'),
                'generation_context': context,
                'generated_algorithmically': True
            },
            expires_at=expires_at
        )
        
        return quest

    def generate_quest_title(self, theme: QuestTheme, difficulty: QuestDifficulty) -> str:
        """Generate a quest title based on theme and difficulty"""
        template = self.quest_templates.get(theme, self.quest_templates[QuestTheme.GENERAL])
        
        prefix = random.choice(template['title_prefixes'])
        adjective = random.choice(self.difficulty_adjectives[difficulty])
        noun = random.choice(template['nouns'])
        
        return f"{prefix} {adjective} {noun}"

    def generate_quest_steps(self, theme: QuestTheme, difficulty: QuestDifficulty, context: Dict[str, Any]) -> List[QuestStepData]:
        """Generate quest steps based on theme and difficulty"""
        # Determine number of steps
        min_steps, max_steps = self.config['step_count_by_difficulty'][difficulty]
        step_count = random.randint(min_steps, max_steps)
        
        # Get step types for this theme
        template = self.quest_templates.get(theme, self.quest_templates[QuestTheme.GENERAL])
        step_types = template['step_types']
        
        steps = []
        for i in range(step_count):
            step_type = random.choice(step_types)
            step = self._generate_step_by_type(step_type, i + 1, theme, difficulty, context)
            steps.append(step)
        
        return steps

    def generate_quest_rewards(self, difficulty: QuestDifficulty, level: int) -> QuestRewardData:
        """Generate quest rewards based on difficulty and level"""
        base_rewards = self.config['base_rewards_by_difficulty'][difficulty]
        
        # Apply level multiplier
        level_multiplier = 1.0 + (level - 1) * self.config['level_multiplier']
        
        gold = int(base_rewards['gold'] * level_multiplier)
        experience = int(base_rewards['experience'] * level_multiplier)
        
        # Generate reputation rewards
        reputation = {}
        if difficulty in [QuestDifficulty.HARD, QuestDifficulty.EPIC]:
            reputation = {
                'amount': random.randint(10, 50),
                'faction': 'local'  # Would be determined by context in real implementation
            }
        
        # Generate item rewards for higher difficulties
        items = []
        if difficulty in [QuestDifficulty.HARD, QuestDifficulty.EPIC]:
            items = self._generate_item_rewards(difficulty, level)
        
        return QuestRewardData(
            gold=gold,
            experience=experience,
            reputation=reputation,
            items=items,
            special={}
        )

    def _determine_theme_from_profession(self, profession: str) -> QuestTheme:
        """Determine quest theme based on NPC profession"""
        profession_themes = {
            'warrior': QuestTheme.COMBAT,
            'guard': QuestTheme.COMBAT,
            'soldier': QuestTheme.COMBAT,
            'scout': QuestTheme.EXPLORATION,
            'explorer': QuestTheme.EXPLORATION,
            'ranger': QuestTheme.EXPLORATION,
            'merchant': QuestTheme.TRADE,
            'trader': QuestTheme.TRADE,
            'shopkeeper': QuestTheme.TRADE,
            'scholar': QuestTheme.KNOWLEDGE,
            'librarian': QuestTheme.KNOWLEDGE,
            'researcher': QuestTheme.KNOWLEDGE,
            'detective': QuestTheme.MYSTERY,
            'investigator': QuestTheme.MYSTERY,
            'noble': QuestTheme.SOCIAL,
            'diplomat': QuestTheme.SOCIAL,
            'blacksmith': QuestTheme.CRAFTING,
            'craftsman': QuestTheme.CRAFTING,
            'healer': QuestTheme.AID,
            'priest': QuestTheme.AID
        }
        
        return profession_themes.get(profession.lower(), QuestTheme.GENERAL)

    def _determine_difficulty_from_context(self, npc_data: Dict[str, Any], context: Dict[str, Any]) -> QuestDifficulty:
        """Determine quest difficulty based on NPC and context"""
        npc_level = npc_data.get('level', 1)
        npc_importance = npc_data.get('importance', 1)  # 1-5 scale
        location_danger = context.get('location_danger', 1)  # 1-5 scale
        
        # Combine factors for difficulty score
        difficulty_score = (npc_level + npc_importance * 5 + location_danger * 3) / 3
        
        if difficulty_score <= 5:
            return QuestDifficulty.EASY
        elif difficulty_score <= 15:
            return QuestDifficulty.MEDIUM
        elif difficulty_score <= 25:
            return QuestDifficulty.HARD
        else:
            return QuestDifficulty.EPIC

    def _generate_quest_description(self, theme: QuestTheme, difficulty: QuestDifficulty, npc_data: Dict[str, Any]) -> str:
        """Generate quest description based on theme, difficulty, and NPC"""
        npc_name = npc_data.get('name', 'someone')
        npc_profession = npc_data.get('profession', 'citizen')
        
        theme_descriptions = {
            QuestTheme.COMBAT: f"{npc_name} the {npc_profession} needs help dealing with a dangerous threat.",
            QuestTheme.EXPLORATION: f"{npc_name} the {npc_profession} has discovered something that needs investigation.",
            QuestTheme.SOCIAL: f"{npc_name} the {npc_profession} needs assistance with a delicate social matter.",
            QuestTheme.MYSTERY: f"{npc_name} the {npc_profession} has encountered a puzzling situation that requires investigation.",
            QuestTheme.CRAFTING: f"{npc_name} the {npc_profession} needs help creating something important.",
            QuestTheme.TRADE: f"{npc_name} the {npc_profession} has goods that need to be transported safely.",
            QuestTheme.AID: f"{npc_name} the {npc_profession} knows of someone who desperately needs help.",
            QuestTheme.KNOWLEDGE: f"{npc_name} the {npc_profession} seeks knowledge about an important matter.",
            QuestTheme.GENERAL: f"{npc_name} the {npc_profession} has a task that needs completing."
        }
        
        base_description = theme_descriptions.get(theme, theme_descriptions[QuestTheme.GENERAL])
        
        # Add difficulty-based flavor
        difficulty_flavors = {
            QuestDifficulty.EASY: "This should be a straightforward task.",
            QuestDifficulty.MEDIUM: "This task may present some challenges.",
            QuestDifficulty.HARD: "This is a dangerous undertaking that requires skill and preparation.",
            QuestDifficulty.EPIC: "This is an extremely perilous quest that will test your limits."
        }
        
        flavor = difficulty_flavors.get(difficulty, "")
        return f"{base_description} {flavor}".strip()

    def _generate_step_by_type(self, step_type: str, step_id: int, theme: QuestTheme, difficulty: QuestDifficulty, context: Dict[str, Any]) -> QuestStepData:
        """Generate a quest step based on its type"""
        step_descriptions = {
            'kill': 'Eliminate the specified target',
            'defeat_boss': 'Defeat the area boss',
            'clear_area': 'Clear all enemies from the area',
            'explore': 'Explore the designated area',
            'discover': 'Discover the hidden location',
            'collect': 'Collect the required items',
            'dialogue': 'Speak with the designated person',
            'persuade': 'Convince someone to help',
            'deliver_message': 'Deliver an important message',
            'investigate': 'Investigate the scene',
            'gather_clues': 'Gather evidence and clues',
            'interrogate': 'Question witnesses or suspects',
            'gather_materials': 'Collect the required materials',
            'craft_item': 'Craft the specified item',
            'deliver_item': 'Deliver the completed item',
            'collect_goods': 'Collect the goods for transport',
            'transport': 'Transport goods safely',
            'deliver': 'Deliver goods to destination',
            'rescue': 'Rescue someone in danger',
            'heal': 'Provide healing to those in need',
            'escort': 'Safely escort someone',
            'provide_aid': 'Provide assistance to those in need',
            'study': 'Study the subject matter',
            'research': 'Research the topic thoroughly',
            'translate': 'Translate ancient texts',
            'learn': 'Learn new skills or knowledge'
        }
        
        description = step_descriptions.get(step_type, 'Complete this objective')
        
        return QuestStepData(
            id=step_id,
            title=f"Step {step_id}: {step_type.replace('_', ' ').title()}",
            description=description,
            completed=False,
            required=True,  # Most steps are required
            order=step_id,
            metadata={
                'step_type': step_type,
                'theme': theme.value,
                'difficulty': difficulty.value
            }
        )

    def _generate_item_rewards(self, difficulty: QuestDifficulty, level: int) -> List[Dict[str, Any]]:
        """Generate item rewards based on difficulty and level"""
        items = []
        
        # Chance of item rewards increases with difficulty
        item_chances = {
            QuestDifficulty.EASY: 0.1,
            QuestDifficulty.MEDIUM: 0.3,
            QuestDifficulty.HARD: 0.6,
            QuestDifficulty.EPIC: 0.9
        }
        
        chance = item_chances.get(difficulty, 0.1)
        
        if random.random() < chance:
            # Generate a simple item reward
            item_types = ['weapon', 'armor', 'accessory', 'consumable']
            item_type = random.choice(item_types)
            
            items.append({
                'item_id': f'generated_{item_type}_{level}',
                'type': item_type,
                'level': level,
                'rarity': difficulty.value,
                'quantity': 1
            })
        
        return items 