"""Cross-system integration service"""
from typing import Dict, List, Optional, Any
import logging

from backend.infrastructure.llm.repositories.integration_repository import IntegrationRepository

logger = logging.getLogger(__name__)

class IntegrationService:
    """Cross-system communication service"""
    
    def __init__(self):
        self.integration_repo = IntegrationRepository()
        self.logger = logger
    
    async def sync_with_system(self, system_name: str, data: Dict[str, Any]) -> bool:
        """Sync with another system"""
        try:
            success = await self.integration_repo.sync_system_state(system_name, data)
            self.logger.info(f"Synced with {system_name}: {success}")
            return success
        except Exception as e:
            self.logger.error(f"Integration error with {system_name}: {e}")
            return False
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        return await self.integration_repo.get_system_health()
