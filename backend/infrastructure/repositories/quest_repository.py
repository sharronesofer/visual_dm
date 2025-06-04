"""
Quest Repository Implementation

Infrastructure layer repository that implements the quest repository interface
from the business logic, providing database persistence.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from backend.infrastructure.databases.quest_models import QuestEntity, QuestChainEntity
from backend.systems.quest.models import (
    QuestData,
    QuestStepData,
    QuestRewardData,
    QuestRepository,
    QuestStatus,
    QuestDifficulty,
    QuestTheme
)


class QuestRepositoryImpl(QuestRepository):
    """SQLAlchemy implementation of quest repository interface"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_quest_by_id(self, quest_id: UUID) -> Optional[QuestData]:
        """Get quest by ID"""
        entity = self.db.query(QuestEntity).filter(QuestEntity.id == quest_id).first()
        return self._entity_to_domain(entity) if entity else None
    
    def get_quest_by_title(self, title: str) -> Optional[QuestData]:
        """Get quest by title"""
        entity = self.db.query(QuestEntity).filter(QuestEntity.title == title).first()
        return self._entity_to_domain(entity) if entity else None
    
    def create_quest(self, quest_data: QuestData) -> QuestData:
        """Create new quest"""
        entity = self._domain_to_entity(quest_data)
        entity.created_at = datetime.utcnow()
        
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        
        return self._entity_to_domain(entity)
    
    def update_quest(self, quest_data: QuestData) -> QuestData:
        """Update existing quest"""
        entity = self.db.query(QuestEntity).filter(QuestEntity.id == quest_data.id).first()
        if not entity:
            raise ValueError(f"Quest {quest_data.id} not found")
        
        # Update entity with new data
        entity.title = quest_data.title
        entity.description = quest_data.description
        entity.status = quest_data.status.value
        entity.difficulty = quest_data.difficulty.value
        entity.theme = quest_data.theme.value
        entity.npc_id = quest_data.npc_id
        entity.player_id = quest_data.player_id
        entity.location_id = quest_data.location_id
        entity.level = quest_data.level
        entity.steps = [step.to_dict() for step in quest_data.steps]
        entity.rewards = quest_data.rewards.to_dict() if quest_data.rewards else {}
        entity.is_main_quest = quest_data.is_main_quest
        entity.tags = quest_data.tags
        entity.properties = quest_data.properties
        entity.expires_at = quest_data.expires_at
        entity.chain_id = quest_data.chain_id
        entity.chain_position = quest_data.chain_position
        entity.chain_prerequisites = quest_data.chain_prerequisites
        entity.chain_unlocks = quest_data.chain_unlocks
        entity.is_chain_final = quest_data.is_chain_final
        entity.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(entity)
        
        return self._entity_to_domain(entity)
    
    def delete_quest(self, quest_id: UUID) -> bool:
        """Delete quest"""
        entity = self.db.query(QuestEntity).filter(QuestEntity.id == quest_id).first()
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.commit()
        return True
    
    def list_quests(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[QuestData], int]:
        """List quests with pagination"""
        query = self.db.query(QuestEntity)
        
        # Apply filters
        if status:
            query = query.filter(QuestEntity.status == status)
        
        if search:
            search_filter = or_(
                QuestEntity.title.ilike(f"%{search}%"),
                QuestEntity.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        entities = query.order_by(desc(QuestEntity.created_at)).offset(offset).limit(size).all()
        
        # Convert to domain objects
        quest_data_list = [self._entity_to_domain(entity) for entity in entities]
        
        return quest_data_list, total
    
    def get_player_quests(self, player_id: str, status: Optional[str] = None) -> List[QuestData]:
        """Get quests for player"""
        query = self.db.query(QuestEntity).filter(QuestEntity.player_id == player_id)
        
        if status:
            query = query.filter(QuestEntity.status == status)
        
        entities = query.order_by(desc(QuestEntity.created_at)).all()
        return [self._entity_to_domain(entity) for entity in entities]
    
    def get_npc_quests(self, npc_id: str, status: Optional[str] = None) -> List[QuestData]:
        """Get quests for NPC"""
        query = self.db.query(QuestEntity).filter(QuestEntity.npc_id == npc_id)
        
        if status:
            query = query.filter(QuestEntity.status == status)
        
        entities = query.order_by(desc(QuestEntity.created_at)).all()
        return [self._entity_to_domain(entity) for entity in entities]
    
    def get_location_quests(self, location_id: str, status: Optional[str] = None) -> List[QuestData]:
        """Get quests for location"""
        query = self.db.query(QuestEntity).filter(QuestEntity.location_id == location_id)
        
        if status:
            query = query.filter(QuestEntity.status == status)
        
        entities = query.order_by(desc(QuestEntity.created_at)).all()
        return [self._entity_to_domain(entity) for entity in entities]
    
    def get_quest_statistics(self) -> Dict[str, Any]:
        """Get quest statistics"""
        total_quests = self.db.query(QuestEntity).count()
        
        # Status breakdown
        status_counts = {}
        for status in ["pending", "active", "completed", "failed", "abandoned", "expired"]:
            count = self.db.query(QuestEntity).filter(QuestEntity.status == status).count()
            status_counts[status] = count
        
        # Difficulty breakdown
        difficulty_counts = {}
        for difficulty in ["easy", "medium", "hard", "epic"]:
            count = self.db.query(QuestEntity).filter(QuestEntity.difficulty == difficulty).count()
            difficulty_counts[difficulty] = count
        
        # Theme breakdown
        theme_counts = {}
        for theme in ["combat", "exploration", "social", "mystery", "crafting", "trade", "aid", "knowledge", "general"]:
            count = self.db.query(QuestEntity).filter(QuestEntity.theme == theme).count()
            theme_counts[theme] = count
        
        return {
            "total_quests": total_quests,
            "status_breakdown": status_counts,
            "difficulty_breakdown": difficulty_counts,
            "theme_breakdown": theme_counts,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _entity_to_domain(self, entity: QuestEntity) -> QuestData:
        """Convert database entity to domain object"""
        # Convert steps
        steps = []
        if entity.steps:
            for step_data in entity.steps:
                step = QuestStepData(
                    id=step_data.get('id', 0),
                    title=step_data.get('title', ''),
                    description=step_data.get('description', ''),
                    completed=step_data.get('completed', False),
                    required=step_data.get('required', True),
                    order=step_data.get('order', 0),
                    metadata=step_data.get('metadata', {})
                )
                steps.append(step)
        
        # Convert rewards
        rewards = None
        if entity.rewards:
            rewards = QuestRewardData(
                gold=entity.rewards.get('gold', 0),
                experience=entity.rewards.get('experience', 0),
                reputation=entity.rewards.get('reputation', {}),
                items=entity.rewards.get('items', []),
                special=entity.rewards.get('special', {})
            )
        
        return QuestData(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            status=QuestStatus(entity.status),
            difficulty=QuestDifficulty(entity.difficulty),
            theme=QuestTheme(entity.theme),
            npc_id=entity.npc_id,
            player_id=entity.player_id,
            location_id=entity.location_id,
            level=entity.level,
            steps=steps,
            rewards=rewards,
            is_main_quest=entity.is_main_quest,
            tags=entity.tags or [],
            properties=entity.properties or {},
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            expires_at=entity.expires_at,
            chain_id=entity.chain_id,
            chain_position=entity.chain_position,
            chain_prerequisites=entity.chain_prerequisites or [],
            chain_unlocks=entity.chain_unlocks or [],
            is_chain_final=entity.is_chain_final
        )
    
    def _domain_to_entity(self, quest_data: QuestData) -> QuestEntity:
        """Convert domain object to database entity"""
        entity = QuestEntity()
        entity.id = quest_data.id
        entity.title = quest_data.title
        entity.description = quest_data.description
        entity.status = quest_data.status.value
        entity.difficulty = quest_data.difficulty.value
        entity.theme = quest_data.theme.value
        entity.npc_id = quest_data.npc_id
        entity.player_id = quest_data.player_id
        entity.location_id = quest_data.location_id
        entity.level = quest_data.level
        entity.steps = [step.to_dict() for step in quest_data.steps]
        entity.rewards = quest_data.rewards.to_dict() if quest_data.rewards else {}
        entity.is_main_quest = quest_data.is_main_quest
        entity.tags = quest_data.tags
        entity.properties = quest_data.properties
        entity.expires_at = quest_data.expires_at
        entity.chain_id = quest_data.chain_id
        entity.chain_position = quest_data.chain_position
        entity.chain_prerequisites = quest_data.chain_prerequisites
        entity.chain_unlocks = quest_data.chain_unlocks
        entity.is_chain_final = quest_data.is_chain_final
        entity.created_at = quest_data.created_at
        entity.updated_at = quest_data.updated_at
        
        return entity 