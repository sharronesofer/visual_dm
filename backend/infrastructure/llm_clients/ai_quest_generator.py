"""
AI Quest Generator
Uses AI/LLM services to generate contextual quests based on NPC motivations and world state.
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from uuid import UUID
from datetime import datetime
import random

# Import from the new locations
from backend.infrastructure.databases.quest_models import Quest, QuestStep
from backend.systems.quest.models import QuestData, QuestDifficulty, QuestTheme  # Business models
from backend.systems.quest.services.generator import QuestGenerationBusinessService  # Business service

# LLM integration imports
from backend.infrastructure.llm.rag_adapter import RAGAdapter

logger = logging.getLogger(__name__)

# Import AI/LLM services
try:
    import openai
    from anthropic import Anthropic
    HAS_AI_SERVICES = True
except ImportError:
    logger.warning("AI services not available, using fallback generation")
    HAS_AI_SERVICES = False

# Try to import environment configuration
try:
    import os
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    AI_MODEL = os.getenv('AI_MODEL', 'claude-3-haiku-20240307')
except ImportError:
    ANTHROPIC_API_KEY = None
    OPENAI_API_KEY = None
    AI_MODEL = 'claude-3-haiku-20240307'


class AIQuestGenerator:
    """AI-powered quest generator using LLM services"""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        
        # Initialize AI clients
        if HAS_AI_SERVICES:
            if ANTHROPIC_API_KEY:
                try:
                    self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
                    logger.info("Anthropic client initialized for quest generation")
                except Exception as e:
                    logger.error(f"Failed to initialize Anthropic client: {str(e)}")
            
            if OPENAI_API_KEY:
                try:
                    openai.api_key = OPENAI_API_KEY
                    self.openai_client = openai
                    logger.info("OpenAI client initialized for quest generation")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        
        # Configuration
        self.config = {
            'max_retries': 3,
            'temperature': 0.7,
            'max_tokens': 1000,
            'fallback_to_procedural': True,
            'validation_enabled': True
        }
        
        # Quest validation rules
        self.validation_rules = {
            'min_title_length': 5,
            'max_title_length': 100,
            'min_description_length': 20,
            'max_description_length': 500,
            'required_fields': ['title', 'description', 'steps', 'difficulty'],
            'valid_difficulties': ['easy', 'medium', 'hard', 'epic'],
            'valid_themes': ['combat', 'exploration', 'social', 'mystery', 'crafting', 'trade', 'aid', 'knowledge'],
            'min_steps': 1,
            'max_steps': 6
        }
        
        # Use business logic service as fallback for generation
        if self.fallback_service is None:
            # Late import to avoid circular dependencies
            from backend.systems.quest.services.generator import QuestGenerationBusinessService
            self.fallback_service = QuestGenerationBusinessService()
    
    def generate_quest_from_npc_context(self, npc_data: Dict[str, Any], 
                                      quest_context: Dict[str, Any],
                                      player_id: Optional[str] = None) -> Optional[Quest]:
        """Generate a quest using AI based on NPC context and motivations"""
        try:
            # Try AI generation first
            if self._has_ai_service():
                quest_data = self._generate_with_ai(npc_data, quest_context, player_id)
                if quest_data and self._validate_quest_data(quest_data):
                    quest = self._create_quest_from_ai_data(quest_data, npc_data, quest_context)
                    if quest:
                        logger.info(f"Generated AI quest: {quest.title}")
                        return quest
            
            # Fallback to enhanced procedural generation if AI fails
            if self.config['fallback_to_procedural']:
                logger.warning("AI generation failed, falling back to enhanced procedural generation")
                return self._generate_enhanced_procedural(npc_data, quest_context, player_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error in AI quest generation: {str(e)}")
            if self.config['fallback_to_procedural']:
                return self._generate_enhanced_procedural(npc_data, quest_context, player_id)
            return None
    
    def _has_ai_service(self) -> bool:
        """Check if any AI service is available"""
        return self.anthropic_client is not None or self.openai_client is not None
    
    def _generate_with_ai(self, npc_data: Dict[str, Any], quest_context: Dict[str, Any], 
                         player_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Generate quest using AI service"""
        try:
            prompt = self._create_quest_generation_prompt(npc_data, quest_context, player_id)
            
            # Try Anthropic first
            if self.anthropic_client:
                return self._generate_with_anthropic(prompt)
            
            # Fall back to OpenAI
            elif self.openai_client:
                return self._generate_with_openai(prompt)
            
            return None
            
        except Exception as e:
            logger.error(f"Error in AI generation: {str(e)}")
            return None
    
    def _generate_with_anthropic(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Generate quest using Anthropic Claude"""
        try:
            response = self.anthropic_client.messages.create(
                model=AI_MODEL,
                max_tokens=self.config['max_tokens'],
                temperature=self.config['temperature'],
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text if response.content else ""
            return self._parse_ai_response(content)
            
        except Exception as e:
            logger.error(f"Anthropic generation error: {str(e)}")
            return None
    
    def _generate_with_openai(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Generate quest using OpenAI GPT"""
        try:
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a quest designer for a fantasy RPG game."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config['max_tokens'],
                temperature=self.config['temperature']
            )
            
            content = response.choices[0].message.content
            return self._parse_ai_response(content)
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {str(e)}")
            return None
    
    def _create_quest_generation_prompt(self, npc_data: Dict[str, Any], 
                                      quest_context: Dict[str, Any],
                                      player_id: Optional[str] = None) -> str:
        """Create a detailed prompt for quest generation"""
        npc_name = npc_data.get('name', 'Unknown NPC')
        npc_id = npc_data.get('id', 'unknown')
        region_id = npc_data.get('region_id', 'unknown region')
        
        # Extract personality and motivations
        personality = quest_context.get('personality_traits', {})
        motivations = quest_context.get('motivations', [])
        problems = quest_context.get('problems', [])
        suggested_themes = quest_context.get('suggested_themes', ['exploration'])
        suggested_difficulty = quest_context.get('suggested_difficulty', 'medium')
        
        # Build character background context
        background_context = ""
        if npc_data.get('backstory'):
            background_context = f"Background: {npc_data['backstory']}\n"
        
        # Build personality description
        personality_desc = []
        ambition = personality.get('ambition', 5)
        integrity = personality.get('integrity', 5)
        pragmatism = personality.get('pragmatism', 5)
        
        if ambition > 7:
            personality_desc.append("highly ambitious")
        elif ambition < 4:
            personality_desc.append("content with current status")
        
        if integrity > 7:
            personality_desc.append("strongly principled")
        elif integrity < 4:
            personality_desc.append("morally flexible")
        
        if pragmatism > 7:
            personality_desc.append("very practical")
        
        personality_str = ", ".join(personality_desc) if personality_desc else "average temperament"
        
        # Build motivations and problems
        motivation_str = ", ".join(motivations) if motivations else "general well-being"
        problems_str = ", ".join(problems) if problems else "no specific current problems"
        
        prompt = f"""
Create a quest for a fantasy RPG game based on the following NPC and context:

NPC DETAILS:
- Name: {npc_name}
- Location: {region_id}
- Personality: {personality_str}
- Current Motivations: {motivation_str}
- Current Problems/Concerns: {problems_str}
{background_context}

QUEST REQUIREMENTS:
- Theme should be one of: {', '.join(suggested_themes)}
- Difficulty: {suggested_difficulty}
- The quest should reflect the NPC's personality and current motivations
- Should feel personal to this specific NPC, not generic
- Include 1-4 clear, actionable steps
- Provide appropriate rewards for the difficulty level

RESPONSE FORMAT (JSON):
{{
    "title": "Quest Title",
    "description": "Quest description explaining why the NPC needs help and what's at stake",
    "theme": "chosen theme from the list",
    "difficulty": "{suggested_difficulty}",
    "steps": [
        {{
            "id": 1,
            "description": "First step description",
            "type": "step_type",
            "completed": false
        }}
    ],
    "rewards": {{
        "gold": 50,
        "experience": 100,
        "items": []
    }},
    "motivation_explanation": "Brief explanation of why this quest fits the NPC's motivations"
}}

Generate a quest that feels authentic to this NPC's character and situation. Make it specific and personal, not generic.
"""
        
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse AI response and extract quest data"""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                logger.error("No JSON found in AI response")
                return None
            
            json_str = response_text[start_idx:end_idx + 1]
            quest_data = json.loads(json_str)
            
            return quest_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            logger.debug(f"Raw response: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return None
    
    def _validate_quest_data(self, quest_data: Dict[str, Any]) -> bool:
        """Validate AI-generated quest data"""
        if not self.config['validation_enabled']:
            return True
        
        try:
            # Check required fields
            for field in self.validation_rules['required_fields']:
                if field not in quest_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate title
            title = quest_data.get('title', '')
            if len(title) < self.validation_rules['min_title_length'] or \
               len(title) > self.validation_rules['max_title_length']:
                logger.error(f"Invalid title length: {len(title)}")
                return False
            
            # Validate description
            desc = quest_data.get('description', '')
            if len(desc) < self.validation_rules['min_description_length'] or \
               len(desc) > self.validation_rules['max_description_length']:
                logger.error(f"Invalid description length: {len(desc)}")
                return False
            
            # Validate difficulty
            difficulty = quest_data.get('difficulty', '')
            if difficulty not in self.validation_rules['valid_difficulties']:
                logger.error(f"Invalid difficulty: {difficulty}")
                return False
            
            # Validate theme
            theme = quest_data.get('theme', '')
            if theme not in self.validation_rules['valid_themes']:
                logger.warning(f"Unusual theme: {theme}")
                # Don't fail for theme, just warn
            
            # Validate steps
            steps = quest_data.get('steps', [])
            if len(steps) < self.validation_rules['min_steps'] or \
               len(steps) > self.validation_rules['max_steps']:
                logger.error(f"Invalid number of steps: {len(steps)}")
                return False
            
            # Validate each step
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    logger.error(f"Step {i} is not a dictionary")
                    return False
                if 'description' not in step:
                    logger.error(f"Step {i} missing description")
                    return False
                if len(step['description']) < 5:
                    logger.error(f"Step {i} description too short")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating quest data: {str(e)}")
            return False
    
    def _create_quest_from_ai_data(self, quest_data: Dict[str, Any], npc_data: Dict[str, Any],
                                  quest_context: Dict[str, Any]) -> Optional[Quest]:
        """Create a Quest object from AI-generated data"""
        try:
            # Create quest steps
            steps = []
            for step_data in quest_data.get('steps', []):
                step = QuestStep(
                    id=step_data.get('id', len(steps) + 1),
                    description=step_data.get('description', ''),
                    type=step_data.get('type', 'generic'),
                    completed=step_data.get('completed', False),
                    target_location_id=quest_context.get('region_id'),
                    data=step_data.get('data', {})
                )
                steps.append(step)
            
            # Create quest
            quest = Quest(
                title=quest_data['title'],
                description=quest_data['description'],
                status="available",
                difficulty=quest_data['difficulty'],
                npc_id=npc_data.get('id'),
                steps=steps,
                reward_type="multiple",
                reward_details=quest_data.get('rewards', {}),
                is_main_quest=False,
                tags=[quest_data.get('theme', 'ai_generated'), 'ai_generated']
            )
            
            # Add AI-specific metadata
            quest.ai_metadata = {
                'motivation_explanation': quest_data.get('motivation_explanation', ''),
                'generation_timestamp': datetime.utcnow().isoformat(),
                'npc_context': quest_context,
                'validation_passed': True
            }
            quest.theme = quest_data.get('theme', 'exploration')
            
            return quest
            
        except Exception as e:
            logger.error(f"Error creating quest from AI data: {str(e)}")
            return None
    
    def _generate_enhanced_procedural(self, npc_data: Dict[str, Any], quest_context: Dict[str, Any],
                                    player_id: Optional[str] = None) -> Optional[Quest]:
        """Generate an enhanced procedural quest when AI is not available"""
        try:
            from backend.systems.quest.services.generator import QuestGenerationBusinessService
            
            generator = QuestGenerationBusinessService()
            
            # Use context to enhance procedural generation
            suggested_themes = quest_context.get('suggested_themes', ['exploration'])
            theme = random.choice(suggested_themes)
            difficulty = quest_context.get('suggested_difficulty', 'medium')
            
            # Generate base quest using business logic
            quest_data = generator.generate_quest_for_npc(npc_data, quest_context)
            
            if quest_data:
                # Convert business model to infrastructure model
                quest = self._convert_business_to_infrastructure_quest(quest_data, npc_data, quest_context)
                
                if quest:
                    logger.info(f"Generated enhanced procedural quest: {quest.title}")
                    return quest
            
            return None
            
        except Exception as e:
            logger.error(f"Error in enhanced procedural generation: {str(e)}")
            return None

    def _convert_business_to_infrastructure_quest(self, quest_data: QuestData, npc_data: Dict[str, Any], quest_context: Dict[str, Any]) -> Optional[Quest]:
        """Convert business quest model to infrastructure quest model"""
        try:
            # Convert quest steps
            steps = []
            for step_data in quest_data.steps:
                step = QuestStep(
                    id=step_data.id,
                    description=step_data.description,
                    type=step_data.metadata.get('step_type', 'generic'),
                    completed=step_data.completed,
                    target_location_id=quest_context.get('region_id'),
                    data=step_data.metadata
                )
                steps.append(step)
            
            # Create infrastructure quest model
            quest = Quest(
                title=quest_data.title,
                description=quest_data.description,
                status=quest_data.status.value,
                difficulty=quest_data.difficulty.value,
                npc_id=quest_data.npc_id,
                steps=steps,
                reward_type="multiple",
                reward_details=quest_data.rewards.to_dict(),
                is_main_quest=False,
                tags=[quest_data.theme.value, 'ai_generated']
            )
            
            # Add AI-specific metadata
            quest.ai_metadata = {
                'generation_method': 'enhanced_procedural',
                'npc_context': quest_context,
                'fallback_reason': 'ai_unavailable'
            }
            quest.theme = quest_data.theme.value
            
            return quest
            
        except Exception as e:
            logger.error(f"Error converting business quest to infrastructure quest: {str(e)}")
            return None 