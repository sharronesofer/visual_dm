from typing import Dict, Any

class RewardService:
    """Service for managing quest rewards of various types."""
    def grant_rewards(self, player, rewards: Dict[str, Any]) -> None:
        """Grant rewards to a player (items, currency, experience, reputation)."""
        if 'gold' in rewards:
            player.gold += rewards['gold']
        if 'experience' in rewards:
            player.experience += rewards['experience']
        if 'items' in rewards:
            for item in rewards['items']:
                player.add_to_inventory(item)
        if 'reputation' in rewards:
            for faction, value in rewards['reputation'].items():
                player.update_reputation(faction, value)

    def scale_rewards(self, base_rewards: Dict[str, Any], difficulty: str, player_level: int) -> Dict[str, Any]:
        """Scale rewards based on quest difficulty and player level."""
        multipliers = {'easy': 1, 'medium': 2, 'hard': 3, 'epic': 5}
        multiplier = multipliers.get(difficulty, 1)
        scaled = {}
        for k, v in base_rewards.items():
            if isinstance(v, int):
                scaled[k] = v * multiplier * max(1, player_level)
            else:
                scaled[k] = v
        return scaled 