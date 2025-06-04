"""
Dialogue System Repository

This module provides database access layer for the dialogue system including
conversation management, message storage, analytics, and performance tracking.
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlalchemy import select, update, delete, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError

from backend.infrastructure.database.models.dialogue_models import (
    DialogueConversation,
    DialogueMessage,
    DialogueAnalytics,
    DialogueConversationCache,
    DialogueNPCPersonality,
    DialogueContextWindow,
    DialoguePerformanceMetrics
)
from backend.infrastructure.database.session import get_async_session
from backend.infrastructure.shared.exceptions import (
    DialogueDatabaseError,
    DialogueNotFoundError,
    DialogueValidationError
)

logger = logging.getLogger(__name__)


class ConversationRepository:
    """Repository for conversation-related database operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_conversation(
        self,
        conversation_id: str,
        npc_id: str,
        player_id: str,
        interaction_type: str,
        location: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DialogueConversation:
        """Create a new conversation record"""
        try:
            conversation = DialogueConversation(
                conversation_id=conversation_id,
                npc_id=npc_id,
                player_id=player_id,
                interaction_type=interaction_type,
                location=location,
                status='active',
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.session.add(conversation)
            await self.session.commit()
            await self.session.refresh(conversation)
            
            logger.debug(f"Created conversation {conversation_id}")
            return conversation
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to create conversation {conversation_id}: {e}")
            raise DialogueDatabaseError(f"Failed to create conversation: {e}")
    
    async def get_conversation(self, conversation_id: str) -> Optional[DialogueConversation]:
        """Get conversation by ID"""
        try:
            stmt = select(DialogueConversation).where(
                DialogueConversation.conversation_id == conversation_id
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}")
            raise DialogueDatabaseError(f"Failed to get conversation: {e}")
    
    async def update_conversation_status(
        self,
        conversation_id: str,
        status: str,
        end_reason: Optional[str] = None
    ) -> bool:
        """Update conversation status"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            
            if status in ['completed', 'terminated', 'timeout']:
                update_data['ended_at'] = datetime.utcnow()
                if end_reason:
                    update_data['end_reason'] = end_reason
            
            stmt = update(DialogueConversation).where(
                DialogueConversation.conversation_id == conversation_id
            ).values(**update_data)
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            return result.rowcount > 0
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to update conversation status {conversation_id}: {e}")
            raise DialogueDatabaseError(f"Failed to update conversation status: {e}")
    
    async def get_active_conversations(
        self,
        player_id: Optional[str] = None,
        npc_id: Optional[str] = None,
        limit: int = 100
    ) -> List[DialogueConversation]:
        """Get active conversations with optional filtering"""
        try:
            stmt = select(DialogueConversation).where(
                DialogueConversation.status == 'active'
            )
            
            if player_id:
                stmt = stmt.where(DialogueConversation.player_id == player_id)
            
            if npc_id:
                stmt = stmt.where(DialogueConversation.npc_id == npc_id)
            
            stmt = stmt.order_by(desc(DialogueConversation.created_at)).limit(limit)
            
            result = await self.session.execute(stmt)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get active conversations: {e}")
            raise DialogueDatabaseError(f"Failed to get active conversations: {e}")
    
    async def get_conversation_history(
        self,
        player_id: str,
        npc_id: Optional[str] = None,
        days: int = 30,
        limit: int = 50
    ) -> List[DialogueConversation]:
        """Get conversation history for a player"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stmt = select(DialogueConversation).where(
                and_(
                    DialogueConversation.player_id == player_id,
                    DialogueConversation.created_at >= cutoff_date
                )
            )
            
            if npc_id:
                stmt = stmt.where(DialogueConversation.npc_id == npc_id)
            
            stmt = stmt.order_by(desc(DialogueConversation.created_at)).limit(limit)
            
            result = await self.session.execute(stmt)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get conversation history for {player_id}: {e}")
            raise DialogueDatabaseError(f"Failed to get conversation history: {e}")


class MessageRepository:
    """Repository for message-related database operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_message(
        self,
        conversation_id: str,
        speaker_type: str,
        speaker_id: str,
        content: str,
        message_type: str = 'dialogue',
        metadata: Optional[Dict[str, Any]] = None
    ) -> DialogueMessage:
        """Create a new message record"""
        try:
            message = DialogueMessage(
                message_id=str(uuid4()),
                conversation_id=conversation_id,
                speaker_type=speaker_type,
                speaker_id=speaker_id,
                content=content,
                message_type=message_type,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            self.session.add(message)
            await self.session.commit()
            await self.session.refresh(message)
            
            logger.debug(f"Created message in conversation {conversation_id}")
            return message
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to create message in {conversation_id}: {e}")
            raise DialogueDatabaseError(f"Failed to create message: {e}")
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[DialogueMessage]:
        """Get messages for a conversation"""
        try:
            stmt = select(DialogueMessage).where(
                DialogueMessage.conversation_id == conversation_id
            ).order_by(asc(DialogueMessage.created_at)).offset(offset).limit(limit)
            
            result = await self.session.execute(stmt)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get messages for {conversation_id}: {e}")
            raise DialogueDatabaseError(f"Failed to get conversation messages: {e}")
    
    async def get_recent_messages(
        self,
        conversation_id: str,
        count: int = 10
    ) -> List[DialogueMessage]:
        """Get recent messages for context window"""
        try:
            stmt = select(DialogueMessage).where(
                DialogueMessage.conversation_id == conversation_id
            ).order_by(desc(DialogueMessage.created_at)).limit(count)
            
            result = await self.session.execute(stmt)
            messages = result.scalars().all()
            
            # Return in chronological order
            return list(reversed(messages))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get recent messages for {conversation_id}: {e}")
            raise DialogueDatabaseError(f"Failed to get recent messages: {e}")
    
    async def delete_old_messages(self, days: int = 90) -> int:
        """Delete messages older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stmt = delete(DialogueMessage).where(
                DialogueMessage.created_at < cutoff_date
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"Deleted {deleted_count} old messages")
            return deleted_count
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to delete old messages: {e}")
            raise DialogueDatabaseError(f"Failed to delete old messages: {e}")


class AnalyticsRepository:
    """Repository for analytics and metrics operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def record_analytics_event(
        self,
        conversation_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        npc_id: Optional[str] = None,
        player_id: Optional[str] = None
    ) -> DialogueAnalytics:
        """Record an analytics event"""
        try:
            analytics = DialogueAnalytics(
                event_id=str(uuid4()),
                conversation_id=conversation_id,
                event_type=event_type,
                event_data=event_data,
                npc_id=npc_id,
                player_id=player_id,
                created_at=datetime.utcnow()
            )
            
            self.session.add(analytics)
            await self.session.commit()
            await self.session.refresh(analytics)
            
            return analytics
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to record analytics event: {e}")
            raise DialogueDatabaseError(f"Failed to record analytics event: {e}")
    
    async def get_conversation_analytics(
        self,
        conversation_id: str
    ) -> List[DialogueAnalytics]:
        """Get analytics for a specific conversation"""
        try:
            stmt = select(DialogueAnalytics).where(
                DialogueAnalytics.conversation_id == conversation_id
            ).order_by(asc(DialogueAnalytics.created_at))
            
            result = await self.session.execute(stmt)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get analytics for {conversation_id}: {e}")
            raise DialogueDatabaseError(f"Failed to get conversation analytics: {e}")
    
    async def get_daily_conversation_stats(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get daily conversation statistics"""
        try:
            # Get conversation counts by day
            stmt = select(
                func.date(DialogueConversation.created_at).label('date'),
                func.count(DialogueConversation.id).label('conversation_count'),
                func.count(func.distinct(DialogueConversation.player_id)).label('unique_players'),
                func.count(func.distinct(DialogueConversation.npc_id)).label('unique_npcs')
            ).where(
                and_(
                    DialogueConversation.created_at >= start_date,
                    DialogueConversation.created_at <= end_date
                )
            ).group_by(func.date(DialogueConversation.created_at))
            
            result = await self.session.execute(stmt)
            
            stats = []
            for row in result:
                stats.append({
                    'date': row.date.isoformat(),
                    'conversation_count': row.conversation_count,
                    'unique_players': row.unique_players,
                    'unique_npcs': row.unique_npcs
                })
            
            return stats
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get daily conversation stats: {e}")
            raise DialogueDatabaseError(f"Failed to get daily conversation stats: {e}")
    
    async def get_npc_interaction_stats(
        self,
        npc_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get interaction statistics for an NPC"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get conversation stats
            conv_stmt = select(
                func.count(DialogueConversation.id).label('total_conversations'),
                func.count(func.distinct(DialogueConversation.player_id)).label('unique_players'),
                func.avg(
                    func.extract('epoch', DialogueConversation.ended_at - DialogueConversation.created_at)
                ).label('avg_duration_seconds')
            ).where(
                and_(
                    DialogueConversation.npc_id == npc_id,
                    DialogueConversation.created_at >= cutoff_date
                )
            )
            
            conv_result = await self.session.execute(conv_stmt)
            conv_stats = conv_result.first()
            
            # Get message stats
            msg_stmt = select(
                func.count(DialogueMessage.id).label('total_messages')
            ).join(DialogueConversation).where(
                and_(
                    DialogueConversation.npc_id == npc_id,
                    DialogueMessage.created_at >= cutoff_date
                )
            )
            
            msg_result = await self.session.execute(msg_stmt)
            msg_stats = msg_result.first()
            
            return {
                'npc_id': npc_id,
                'period_days': days,
                'total_conversations': conv_stats.total_conversations or 0,
                'unique_players': conv_stats.unique_players or 0,
                'total_messages': msg_stats.total_messages or 0,
                'average_duration_seconds': float(conv_stats.avg_duration_seconds or 0),
                'messages_per_conversation': (
                    (msg_stats.total_messages or 0) / max(conv_stats.total_conversations or 1, 1)
                )
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get NPC interaction stats for {npc_id}: {e}")
            raise DialogueDatabaseError(f"Failed to get NPC interaction stats: {e}")


class PersonalityRepository:
    """Repository for NPC personality data operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_npc_personality(
        self,
        npc_id: str,
        personality_data: Dict[str, Any],
        version: str = "1.0"
    ) -> DialogueNPCPersonality:
        """Save or update NPC personality data"""
        try:
            # Check if personality already exists
            existing = await self.get_npc_personality(npc_id)
            
            if existing:
                # Update existing
                stmt = update(DialogueNPCPersonality).where(
                    DialogueNPCPersonality.npc_id == npc_id
                ).values(
                    personality_data=personality_data,
                    version=version,
                    updated_at=datetime.utcnow()
                )
                
                await self.session.execute(stmt)
                await self.session.commit()
                
                # Refresh and return
                await self.session.refresh(existing)
                return existing
            else:
                # Create new
                personality = DialogueNPCPersonality(
                    npc_id=npc_id,
                    personality_data=personality_data,
                    version=version,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                self.session.add(personality)
                await self.session.commit()
                await self.session.refresh(personality)
                
                return personality
                
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to save NPC personality for {npc_id}: {e}")
            raise DialogueDatabaseError(f"Failed to save NPC personality: {e}")
    
    async def get_npc_personality(self, npc_id: str) -> Optional[DialogueNPCPersonality]:
        """Get NPC personality data"""
        try:
            stmt = select(DialogueNPCPersonality).where(
                DialogueNPCPersonality.npc_id == npc_id
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get NPC personality for {npc_id}: {e}")
            raise DialogueDatabaseError(f"Failed to get NPC personality: {e}")
    
    async def delete_npc_personality(self, npc_id: str) -> bool:
        """Delete NPC personality data"""
        try:
            stmt = delete(DialogueNPCPersonality).where(
                DialogueNPCPersonality.npc_id == npc_id
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            return result.rowcount > 0
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to delete NPC personality for {npc_id}: {e}")
            raise DialogueDatabaseError(f"Failed to delete NPC personality: {e}")


class PerformanceRepository:
    """Repository for performance metrics operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def record_performance_metrics(
        self,
        conversation_id: str,
        metric_type: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DialoguePerformanceMetrics:
        """Record performance metrics"""
        try:
            metrics = DialoguePerformanceMetrics(
                metric_id=str(uuid4()),
                conversation_id=conversation_id,
                metric_type=metric_type,
                metric_value=metric_value,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            self.session.add(metrics)
            await self.session.commit()
            await self.session.refresh(metrics)
            
            return metrics
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to record performance metrics: {e}")
            raise DialogueDatabaseError(f"Failed to record performance metrics: {e}")
    
    async def get_performance_summary(
        self,
        metric_type: str,
        hours: int = 24
    ) -> Dict[str, float]:
        """Get performance summary for a metric type"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            stmt = select(
                func.avg(DialoguePerformanceMetrics.metric_value).label('avg_value'),
                func.min(DialoguePerformanceMetrics.metric_value).label('min_value'),
                func.max(DialoguePerformanceMetrics.metric_value).label('max_value'),
                func.count(DialoguePerformanceMetrics.id).label('sample_count')
            ).where(
                and_(
                    DialoguePerformanceMetrics.metric_type == metric_type,
                    DialoguePerformanceMetrics.created_at >= cutoff_time
                )
            )
            
            result = await self.session.execute(stmt)
            row = result.first()
            
            return {
                'metric_type': metric_type,
                'period_hours': hours,
                'average_value': float(row.avg_value or 0),
                'min_value': float(row.min_value or 0),
                'max_value': float(row.max_value or 0),
                'sample_count': row.sample_count or 0
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get performance summary for {metric_type}: {e}")
            raise DialogueDatabaseError(f"Failed to get performance summary: {e}")


class DialogueRepository:
    """
    Main repository class that combines all dialogue-related database operations
    """
    
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self._conversation_repo = None
        self._message_repo = None
        self._analytics_repo = None
        self._personality_repo = None
        self._performance_repo = None
    
    async def initialize(self):
        """Initialize repository with database session"""
        if not self.session:
            self.session = await get_async_session()
        
        self._conversation_repo = ConversationRepository(self.session)
        self._message_repo = MessageRepository(self.session)
        self._analytics_repo = AnalyticsRepository(self.session)
        self._personality_repo = PersonalityRepository(self.session)
        self._performance_repo = PerformanceRepository(self.session)
    
    @property
    def conversations(self) -> ConversationRepository:
        """Get conversation repository"""
        if not self._conversation_repo:
            raise DialogueDatabaseError("Repository not initialized")
        return self._conversation_repo
    
    @property
    def messages(self) -> MessageRepository:
        """Get message repository"""
        if not self._message_repo:
            raise DialogueDatabaseError("Repository not initialized")
        return self._message_repo
    
    @property
    def analytics(self) -> AnalyticsRepository:
        """Get analytics repository"""
        if not self._analytics_repo:
            raise DialogueDatabaseError("Repository not initialized")
        return self._analytics_repo
    
    @property
    def personalities(self) -> PersonalityRepository:
        """Get personality repository"""
        if not self._personality_repo:
            raise DialogueDatabaseError("Repository not initialized")
        return self._personality_repo
    
    @property
    def performance(self) -> PerformanceRepository:
        """Get performance repository"""
        if not self._performance_repo:
            raise DialogueDatabaseError("Repository not initialized")
        return self._performance_repo
    
    async def cleanup(self):
        """Cleanup repository resources"""
        if self.session:
            await self.session.close()


async def create_dialogue_repository() -> DialogueRepository:
    """Factory function to create and initialize dialogue repository"""
    repository = DialogueRepository()
    await repository.initialize()
    return repository 