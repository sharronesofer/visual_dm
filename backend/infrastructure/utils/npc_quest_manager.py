"""
NPC Quest Manager
Handles quest generation based on NPC motivations, needs, and relationships.
Integrates with world tick system and AI generation.
"""

import logging
import random
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from uuid import UUID, uuid4

# Infrastructure imports
from backend.infrastructure.databases.quest_models import Quest, QuestStep
from backend.infrastructure.events.quest.quest_events import get_quest_event_publisher
from backend.infrastructure.llm_clients.ai_quest_generator import AIQuestGenerator

# Business logic imports
from backend.systems.quest.services.generator import QuestGenerationBusinessService
from backend.systems.quest.models import QuestData, QuestDifficulty, QuestTheme

logger = logging.getLogger(__name__)

# Import NPC infrastructure
try:
    from backend.infrastructure.systems.npc.repositories.npc_repository import NPCRepository
    from backend.infrastructure.systems.npc.models.models import NpcEntity, NpcMotif
    HAS_NPC_SYSTEM = True
except ImportError:
    logger.warning("NPC system not available, using fallback")
    HAS_NPC_SYSTEM = False
    
    # Fallback classes
    class NpcEntity:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class NPCRepository:
        def __init__(self, db):
            pass


class NPCQuestManager:
    """Manages quest generation and tracking for NPCs based on their motivations and state"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.npc_repository = NPCRepository(db_session) if HAS_NPC_SYSTEM and db_session else None
        self.quest_generator = QuestGenerator()
        self.ai_generator = AIQuestGenerator()
        self.event_publisher = get_quest_event_publisher()
        
        # Quest history per NPC to track patterns and avoid repetition
        self._npc_quest_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # NPC quest cooldowns to prevent spam
        self._npc_quest_cooldowns: Dict[str, datetime] = {}
        
        # Configuration
        self.config = {
            'max_quests_per_npc': 3,
            'quest_cooldown_hours': 24,
            'ai_generation_chance': 0.3,  # 30% chance to use AI vs procedural
            'world_tick_quest_chance': 0.15,  # 15% chance per tick to generate quest
            'max_failed_quest_memory': 3,  # How many failed quests NPCs remember
            'loyalty_impact_threshold': 0.2  # How much failed quests affect loyalty
        }
    
    def process_world_tick(self, region_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Process quest generation for world tick - main entry point for world tick system"""
        try:
            generated_quests = []
            
            # Get NPCs in the region or all NPCs
            npcs = self._get_npcs_for_quest_generation(region_id)
            
            for npc in npcs:
                # Check if this NPC should generate a quest this tick
                if self._should_generate_quest_for_npc(npc):
                    quest = self._generate_quest_for_npc(npc)
                    if quest:
                        generated_quests.append({
                            'quest_id': quest.id if hasattr(quest, 'id') else str(uuid4()),
                            'npc_id': npc.id if hasattr(npc, 'id') else npc.get('id'),
                            'title': quest.title,
                            'generation_method': getattr(quest, 'generation_method', 'procedural'),
                            'theme': getattr(quest, 'theme', 'exploration')
                        })
            
            logger.info(f"Generated {len(generated_quests)} quests during world tick for region {region_id}")
            return generated_quests
            
        except Exception as e:
            logger.error(f"Error processing quest generation for world tick: {str(e)}")
            return []
    
    def generate_quest_for_npc(self, npc_id: str, player_id: Optional[str] = None, 
                              force_ai: bool = False) -> Optional[Quest]:
        """Generate a quest for a specific NPC based on their current state and motivations"""
        try:
            # Get NPC data
            npc = self._get_npc_data(npc_id)
            if not npc:
                logger.error(f"NPC {npc_id} not found")
                return None
            
            # Check cooldown
            if not self._check_quest_cooldown(npc_id):
                logger.debug(f"NPC {npc_id} is on quest generation cooldown")
                return None
            
            # Generate quest based on NPC state
            quest = self._generate_quest_for_npc(npc, player_id, force_ai)
            
            if quest:
                # Update cooldown
                self._set_quest_cooldown(npc_id)
                
                # Track in history
                self._add_to_quest_history(npc_id, quest)
                
                # Publish event
                self.event_publisher.publish_quest_created(
                    quest_id=UUID(str(quest.id)) if hasattr(quest, 'id') else uuid4(),
                    title=quest.title,
                    npc_id=npc_id,
                    player_id=player_id,
                    difficulty=quest.difficulty,
                    theme=getattr(quest, 'theme', 'exploration'),
                    generation_method=getattr(quest, 'generation_method', 'procedural')
                )
                
                logger.info(f"Generated quest '{quest.title}' for NPC {npc_id}")
                return quest
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating quest for NPC {npc_id}: {str(e)}")
            return None
    
    def handle_quest_outcome(self, quest_id: str, npc_id: str, player_id: str, 
                           outcome: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Handle quest completion/failure and update NPC memory and relationships"""
        try:
            npc = self._get_npc_data(npc_id)
            if not npc:
                return
            
            # Create memory entry for the quest outcome
            memory_content = self._create_quest_memory(quest_id, player_id, outcome, details)
            self._add_npc_memory(npc_id, memory_content, outcome)
            
            # Update NPC relationships and loyalty based on outcome
            if outcome == "completed":
                self._handle_quest_success(npc_id, player_id, details)
            elif outcome in ["failed", "abandoned"]:
                self._handle_quest_failure(npc_id, player_id, outcome, details)
            
            # Update quest history
            self._update_quest_history(npc_id, quest_id, outcome, details)
            
            logger.info(f"Processed quest outcome '{outcome}' for NPC {npc_id}, quest {quest_id}")
            
        except Exception as e:
            logger.error(f"Error handling quest outcome: {str(e)}")
    
    def get_npc_quest_history(self, npc_id: str) -> List[Dict[str, Any]]:
        """Get quest history for an NPC"""
        return self._npc_quest_history.get(npc_id, [])
    
    def can_npc_offer_quest(self, npc_id: str) -> bool:
        """Check if an NPC can offer a quest right now"""
        return self._check_quest_cooldown(npc_id)
    
    # Private methods
    
    def _get_npcs_for_quest_generation(self, region_id: Optional[str] = None) -> List[Any]:
        """Get NPCs that could generate quests"""
        try:
            if self.npc_repository and HAS_NPC_SYSTEM:
                # Get active NPCs from database
                if region_id:
                    # Filter by region if specified
                    npcs = self.npc_repository.db.query(NpcEntity).filter(
                        NpcEntity.is_active == True,
                        NpcEntity.region_id == region_id
                    ).all()
                else:
                    npcs = self.npc_repository.db.query(NpcEntity).filter(
                        NpcEntity.is_active == True
                    ).limit(50).all()  # Limit to prevent performance issues
                
                return [npc.to_dict() for npc in npcs]
            else:
                # Fallback: return mock NPCs for testing
                return [
                    {
                        'id': 'npc_1',
                        'name': 'Village Elder',
                        'region_id': region_id or 'default_region',
                        'hidden_ambition': 7,
                        'hidden_integrity': 8,
                        'loyalty_score': 5,
                        'faction_affiliations': ['village_council'],
                        'motifs': []
                    }
                ]
        except Exception as e:
            logger.error(f"Error getting NPCs for quest generation: {str(e)}")
            return []
    
    def _get_npc_data(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """Get NPC data by ID"""
        try:
            if self.npc_repository and HAS_NPC_SYSTEM:
                npc_entity = self.npc_repository.get_npc(UUID(npc_id))
                return npc_entity.to_dict() if npc_entity else None
            else:
                # Fallback mock data
                return {
                    'id': npc_id,
                    'name': f'NPC {npc_id}',
                    'hidden_ambition': random.randint(1, 10),
                    'hidden_integrity': random.randint(1, 10),
                    'loyalty_score': random.randint(1, 10),
                    'region_id': 'default_region'
                }
        except Exception as e:
            logger.error(f"Error getting NPC data for {npc_id}: {str(e)}")
            return None
    
    def _should_generate_quest_for_npc(self, npc: Dict[str, Any]) -> bool:
        """Determine if an NPC should generate a quest this tick"""
        npc_id = npc.get('id')
        
        # Check cooldown
        if not self._check_quest_cooldown(npc_id):
            return False
        
        # Base chance
        base_chance = self.config['world_tick_quest_chance']
        
        # Modify based on NPC traits
        ambition = npc.get('hidden_ambition', 5)
        integrity = npc.get('hidden_integrity', 5)
        
        # Higher ambition = more likely to have quests
        ambition_modifier = (ambition - 5) * 0.02  # +/- 10% max
        
        # NPCs with goals or motifs are more likely to generate quests
        motif_modifier = len(npc.get('motifs', [])) * 0.05
        
        final_chance = base_chance + ambition_modifier + motif_modifier
        
        return random.random() < final_chance
    
    def _generate_quest_for_npc(self, npc: Dict[str, Any], player_id: Optional[str] = None, 
                               force_ai: bool = False) -> Optional[Quest]:
        """Generate a quest based on NPC's current state and motivations"""
        npc_id = npc.get('id')
        
        # Determine generation method
        use_ai = force_ai or (random.random() < self.config['ai_generation_chance'])
        
        # Analyze NPC to determine quest parameters
        quest_context = self._analyze_npc_for_quest(npc)
        
        if use_ai and self.ai_generator:
            # Use AI generation
            quest = self.ai_generator.generate_quest_from_npc_context(npc, quest_context, player_id)
            if quest:
                quest.generation_method = "ai_generated"
        else:
            # Use procedural generation with NPC context
            quest = self._generate_procedural_quest(npc, quest_context, player_id)
            if quest:
                quest.generation_method = "procedural"
        
        return quest
    
    def _analyze_npc_for_quest(self, npc: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze NPC to determine appropriate quest parameters"""
        context = {
            'npc_id': npc.get('id'),
            'npc_name': npc.get('name', 'Unknown'),
            'region_id': npc.get('region_id'),
            'personality_traits': {},
            'motivations': [],
            'problems': [],
            'relationships': [],
            'suggested_themes': [],
            'suggested_difficulty': 'medium'
        }
        
        # Analyze personality traits
        ambition = npc.get('hidden_ambition', 5)
        integrity = npc.get('hidden_integrity', 5)
        pragmatism = npc.get('hidden_pragmatism', 5)
        
        context['personality_traits'] = {
            'ambition': ambition,
            'integrity': integrity,
            'pragmatism': pragmatism
        }
        
        # Determine motivations based on traits
        if ambition > 7:
            context['motivations'].append('power')
            context['motivations'].append('recognition')
        if integrity > 7:
            context['motivations'].append('justice')
            context['motivations'].append('helping_others')
        if pragmatism > 7:
            context['motivations'].append('efficiency')
            context['motivations'].append('practical_solutions')
        
        # Analyze motifs for specific problems/goals
        motifs = npc.get('motifs', [])
        for motif in motifs:
            motif_type = motif.get('motif_type', '')
            if motif_type == 'revenge':
                context['problems'].append('seeking_vengeance')
                context['suggested_themes'].append('combat')
            elif motif_type == 'romance':
                context['problems'].append('relationship_troubles')
                context['suggested_themes'].append('social')
            elif motif_type == 'ambition':
                context['problems'].append('lacking_resources')
                context['suggested_themes'].append('exploration')
        
        # Determine themes based on NPC background
        faction_affiliations = npc.get('faction_affiliations', [])
        if any('merchant' in str(f).lower() for f in faction_affiliations):
            context['suggested_themes'].extend(['trade', 'exploration'])
        if any('guard' in str(f).lower() or 'military' in str(f).lower() for f in faction_affiliations):
            context['suggested_themes'].extend(['combat', 'social'])
        
        # Default themes if none suggested
        if not context['suggested_themes']:
            context['suggested_themes'] = ['exploration', 'social', 'mystery']
        
        # Determine difficulty based on NPC's position and capabilities
        loyalty_score = npc.get('loyalty_score', 5)
        if loyalty_score > 8 or ambition > 8:
            context['suggested_difficulty'] = 'hard'
        elif loyalty_score < 3 or ambition < 3:
            context['suggested_difficulty'] = 'easy'
        
        return context
    
    def _generate_procedural_quest(self, npc: Dict[str, Any], context: Dict[str, Any], 
                                  player_id: Optional[str] = None) -> Optional[Quest]:
        """Generate a quest using procedural methods based on NPC context"""
        try:
            # Select theme based on context
            theme = random.choice(context['suggested_themes'])
            difficulty = context['suggested_difficulty']
            
            # Generate using existing generator but with NPC context
            quest = self.quest_generator.generate_quest(
                player_id=player_id or "unknown",
                theme=theme,
                difficulty=difficulty,
                location_id=context.get('region_id'),
                npc_id=context['npc_id'],
                level=1  # Could be based on region difficulty
            )
            
            # Enhance description with NPC context
            npc_name = context['npc_name']
            motivations = context.get('motivations', [])
            problems = context.get('problems', [])
            
            # Create more contextual descriptions
            if 'helping_others' in motivations:
                quest.description = f"{npc_name} is concerned about the local community. {quest.description}"
            elif 'power' in motivations:
                quest.description = f"{npc_name} seeks to increase their influence. {quest.description}"
            elif 'seeking_vengeance' in problems:
                quest.description = f"{npc_name} has been wronged and seeks justice. {quest.description}"
            
            # Add NPC-specific context to quest data
            quest.npc_context = context
            quest.theme = theme
            
            return quest
            
        except Exception as e:
            logger.error(f"Error generating procedural quest for NPC: {str(e)}")
            return None
    
    def _check_quest_cooldown(self, npc_id: str) -> bool:
        """Check if NPC is off cooldown for quest generation"""
        if npc_id not in self._npc_quest_cooldowns:
            return True
        
        cooldown_end = self._npc_quest_cooldowns[npc_id]
        return datetime.utcnow() > cooldown_end
    
    def _set_quest_cooldown(self, npc_id: str) -> None:
        """Set quest generation cooldown for an NPC"""
        cooldown_hours = self.config['quest_cooldown_hours']
        self._npc_quest_cooldowns[npc_id] = datetime.utcnow() + timedelta(hours=cooldown_hours)
    
    def _add_to_quest_history(self, npc_id: str, quest: Quest) -> None:
        """Add quest to NPC's history"""
        if npc_id not in self._npc_quest_history:
            self._npc_quest_history[npc_id] = []
        
        quest_record = {
            'quest_id': getattr(quest, 'id', str(uuid4())),
            'title': quest.title,
            'theme': getattr(quest, 'theme', 'unknown'),
            'difficulty': quest.difficulty,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'offered',
            'outcome': None
        }
        
        self._npc_quest_history[npc_id].append(quest_record)
        
        # Keep only recent history
        max_history = 20
        if len(self._npc_quest_history[npc_id]) > max_history:
            self._npc_quest_history[npc_id] = self._npc_quest_history[npc_id][-max_history:]
    
    def _update_quest_history(self, npc_id: str, quest_id: str, outcome: str, 
                            details: Optional[Dict[str, Any]] = None) -> None:
        """Update quest outcome in NPC's history"""
        if npc_id in self._npc_quest_history:
            for quest_record in self._npc_quest_history[npc_id]:
                if quest_record['quest_id'] == quest_id:
                    quest_record['status'] = 'completed'
                    quest_record['outcome'] = outcome
                    quest_record['completed_at'] = datetime.utcnow().isoformat()
                    if details:
                        quest_record['details'] = details
                    break
    
    def _create_quest_memory(self, quest_id: str, player_id: str, outcome: str, 
                           details: Optional[Dict[str, Any]] = None) -> str:
        """Create memory content for quest outcome"""
        if outcome == "completed":
            return f"Player {player_id} successfully completed my quest {quest_id}. They proved reliable and capable."
        elif outcome == "failed":
            failure_reason = details.get('failure_reason', 'unknown reasons') if details else 'unknown reasons'
            return f"Player {player_id} failed to complete my quest {quest_id} due to {failure_reason}. I am disappointed."
        elif outcome == "abandoned":
            return f"Player {player_id} abandoned my quest {quest_id}. I feel let down by their lack of commitment."
        else:
            return f"Player {player_id} had an unexpected outcome with my quest {quest_id}: {outcome}."
    
    def _add_npc_memory(self, npc_id: str, content: str, memory_type: str) -> None:
        """Add memory to NPC"""
        try:
            if self.npc_repository and HAS_NPC_SYSTEM:
                # Add to NPC memory system
                memory_data = {
                    'content': content,
                    'memory_type': f'quest_{memory_type}',
                    'importance': 0.8 if memory_type == 'completed' else 0.6,
                    'context': {'system': 'quest_manager'}
                }
                self.npc_repository.add_memory(UUID(npc_id), memory_data)
            else:
                logger.debug(f"Would add memory to NPC {npc_id}: {content}")
        except Exception as e:
            logger.error(f"Error adding memory to NPC {npc_id}: {str(e)}")
    
    def _handle_quest_success(self, npc_id: str, player_id: str, details: Optional[Dict[str, Any]]) -> None:
        """Handle successful quest completion effects on NPC"""
        try:
            # Increase loyalty/goodwill
            if self.npc_repository and HAS_NPC_SYSTEM:
                npc = self.npc_repository.get_npc(UUID(npc_id))
                if npc:
                    # Increase goodwill and loyalty
                    npc.goodwill = min(20, npc.goodwill + 2)
                    npc.loyalty_score = min(10, npc.loyalty_score + 1)
                    self.npc_repository.db.commit()
            
            logger.info(f"Increased loyalty for NPC {npc_id} due to quest success by {player_id}")
        except Exception as e:
            logger.error(f"Error handling quest success for NPC {npc_id}: {str(e)}")
    
    def _handle_quest_failure(self, npc_id: str, player_id: str, outcome: str, 
                            details: Optional[Dict[str, Any]]) -> None:
        """Handle quest failure/abandonment effects on NPC"""
        try:
            # Decrease loyalty/goodwill
            if self.npc_repository and HAS_NPC_SYSTEM:
                npc = self.npc_repository.get_npc(UUID(npc_id))
                if npc:
                    # Decrease goodwill and loyalty based on failure type
                    penalty = 3 if outcome == "abandoned" else 1
                    npc.goodwill = max(0, npc.goodwill - penalty)
                    if outcome == "abandoned":
                        npc.loyalty_score = max(-5, npc.loyalty_score - 1)
                    self.npc_repository.db.commit()
            
            logger.info(f"Decreased loyalty for NPC {npc_id} due to quest {outcome} by {player_id}")
        except Exception as e:
            logger.error(f"Error handling quest failure for NPC {npc_id}: {str(e)}") 