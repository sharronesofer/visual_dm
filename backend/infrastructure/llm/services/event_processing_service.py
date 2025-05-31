"""Event processing service"""
from typing import Dict, List, Optional, Any
import asyncio
import logging

from backend.infrastructure.llm.repositories.event_repository import EventRepository

logger = logging.getLogger(__name__)

class EventProcessingService:
    """Event-driven LLM processing"""
    
    def __init__(self):
        self.event_repo = EventRepository()
        self.logger = logger
    
    async def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process single event"""
        event_id = await self.event_repo.save_event(event_data)
        
        # Event processing logic
        result = {"event_id": event_id, "status": "processed"}
        
        self.logger.info(f"Processed event: {event_id}")
        return result
    
    async def process_event_queue(self) -> List[Dict[str, Any]]:
        """Process pending events"""
        events = await self.event_repo.process_event_queue()
        results = []
        
        for event in events:
            result = await self.process_event(event)
            results.append(result)
        
        return results
