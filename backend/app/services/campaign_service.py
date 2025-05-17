"""Campaign service for managing campaign entities."""

from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..models.campaign import Campaign
from .base_service import BaseService
from ..database import get_db

class CampaignService(BaseService[Campaign]):
    """Service for managing campaign entities."""
    
    def __init__(self, db: Session = Depends(get_db)):
        """Initialize the campaign service.
        
        Args:
            db: Database session
        """
        super().__init__(Campaign, db)
    
    async def add_player_to_campaign(self, campaign_id: int, player_id: int) -> Campaign:
        """Add a player to a campaign.
        
        Args:
            campaign_id: Campaign ID
            player_id: Player ID
            
        Returns:
            Updated campaign entity
            
        Raises:
            HTTPException: If campaign not found or update fails
        """
        campaign = await self.get_by_id(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign with ID {campaign_id} not found"
            )
        
        # Check if player is already in campaign
        if player_id in campaign.players:
            return campaign
        
        # Add player to campaign
        players = campaign.players or []
        players.append(player_id)
        
        return await self.update(campaign_id, {"players": players})
    
    async def remove_player_from_campaign(self, campaign_id: int, player_id: int) -> Campaign:
        """Remove a player from a campaign.
        
        Args:
            campaign_id: Campaign ID
            player_id: Player ID
            
        Returns:
            Updated campaign entity
            
        Raises:
            HTTPException: If campaign not found or update fails
        """
        campaign = await self.get_by_id(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign with ID {campaign_id} not found"
            )
        
        # Check if player is in campaign
        players = campaign.players or []
        if player_id not in players:
            return campaign
        
        # Remove player from campaign
        players.remove(player_id)
        
        return await self.update(campaign_id, {"players": players})
    
    async def update_campaign_state(self, campaign_id: int, state_data: Dict[str, Any]) -> Campaign:
        """Update the state of a campaign.
        
        Args:
            campaign_id: Campaign ID
            state_data: Updated state data
            
        Returns:
            Updated campaign entity
            
        Raises:
            HTTPException: If campaign not found or update fails
        """
        campaign = await self.get_by_id(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign with ID {campaign_id} not found"
            )
        
        # Update only state-related fields
        update_data = {}
        state_fields = ["status", "current_session", "sessions", "notes", "dm_notes"]
        
        for field in state_fields:
            if field in state_data:
                update_data[field] = state_data[field]
        
        return await self.update(campaign_id, update_data)
    
    async def get_campaigns_by_player(self, player_id: int) -> List[Campaign]:
        """Get all campaigns for a player.
        
        Args:
            player_id: Player ID
            
        Returns:
            List of campaigns
        """
        # In a real implementation, you would use a proper query to find
        # campaigns where the player is a member
        all_campaigns = await self.get_all()
        player_campaigns = [
            campaign for campaign in all_campaigns 
            if campaign.players and player_id in campaign.players
        ]
        
        return player_campaigns 