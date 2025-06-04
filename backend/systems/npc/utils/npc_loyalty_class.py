#This class governs the NPC loyalty and goodwill dynamics, simulating emotional drift, bonding, abandonment, and resistance to relationship change over time or in response to events.
#It supports the npc, relationship, party, and motif systems.

from datetime import datetime, timedelta
from backend.systems.npc.config import get_npc_config

class LoyaltyManager:
    """
    Manages NPC loyalty and relationship dynamics with both a direct score and goodwill buffer system.
    - score: -10 to 10 loyalty (negative = disloyal, positive = loyal)
    - goodwill: 0 to 36 buffer that influences loyalty shifts
    - auto_abandon: Flag that indicates NPC likely to abandon party
    - tags: Special relationship flags that modify behavior
    """
    def __init__(self, loyalty_data=None):
        config = get_npc_config()
        self.config = config.get_loyalty_settings()
        self.ranges = self.config.get('loyalty_ranges', {})
        self.tags_config = self.config.get('relationship_tags', {})
        
        if loyalty_data is None:
            self.score = 0
            self.goodwill = self.ranges.get('default_goodwill', 18)
            self.tags = []
            self.last_tick = datetime.utcnow()
        else:
            self.score = loyalty_data.get("score", 0)
            self.goodwill = loyalty_data.get("goodwill", self.ranges.get('default_goodwill', 18))
            self.tags = loyalty_data.get("tags", [])
            last_tick_str = loyalty_data.get("last_tick")
            if last_tick_str:
                try:
                    self.last_tick = datetime.fromisoformat(last_tick_str.replace('Z', '+00:00'))
                except:
                    self.last_tick = datetime.utcnow()
            else:
                self.last_tick = datetime.utcnow()

    def _get_tag_modifier(self, tag_name, modifier_type):
        """Get modifier for a specific tag"""
        tag_config = self.tags_config.get(tag_name, {})
        return tag_config.get(modifier_type, 1.0)

    def _apply_tag_modifiers(self, base_value, modifier_type):
        """Apply all tag modifiers to a base value"""
        result = base_value
        for tag in self.tags:
            modifier = self._get_tag_modifier(tag, modifier_type)
            result *= modifier
        return int(result)

    def has_loyalty_tag(self, tag):
        return tag in self.tags

    def add_loyalty_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
            # Apply immediate bonuses/penalties from config
            tag_config = self.tags_config.get(tag, {})
            if 'goodwill_bonus' in tag_config:
                self.goodwill = min(self.ranges.get('goodwill_max', 36), 
                                  self.goodwill + tag_config['goodwill_bonus'])
            if 'goodwill_penalty' in tag_config:
                self.goodwill = max(self.ranges.get('goodwill_min', 0), 
                                  self.goodwill - tag_config['goodwill_penalty'])

    def remove_loyalty_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)

    def gain_loyalty(self, amount=1):
        if "bestie" in self.tags:
            self.score = self.ranges.get('max_score', 10)
            return
        if "nemesis" in self.tags:
            return
        
        adjusted_amount = self._apply_tag_modifiers(amount, 'gain_modifier')
        self.score = min(self.ranges.get('max_score', 10), self.score + adjusted_amount)

    def lose_loyalty(self, amount=1):
        if "bestie" in self.tags:
            return
        if "nemesis" in self.tags:
            self.score = self.ranges.get('min_score', -10)
            return
            
        adjusted_amount = self._apply_tag_modifiers(amount, 'loss_modifier')
        self.score = max(self.ranges.get('min_score', -10), self.score - adjusted_amount)

    def gain_goodwill(self, amount=2):
        max_goodwill = self.ranges.get('goodwill_max', 36)
        self.goodwill = min(max_goodwill, self.goodwill + amount)
        
        # Check for loyalty gain threshold
        threshold = self.config.get('loyalty_thresholds', {}).get('goodwill_to_loyalty_gain', 30)
        if self.goodwill >= threshold:
            self.gain_loyalty(1)
            self.goodwill = max_goodwill

    def lose_goodwill(self, amount=2):
        min_goodwill = self.ranges.get('goodwill_min', 0)
        self.goodwill = max(min_goodwill, self.goodwill - amount)
        
        # Check for loyalty loss threshold
        threshold = self.config.get('loyalty_thresholds', {}).get('goodwill_to_loyalty_loss', 6)
        if self.goodwill <= threshold:
            self.lose_loyalty(1)
            self.goodwill = min_goodwill

    def check_abandonment(self):
        """Check if NPC should abandon due to low loyalty"""
        abandon_conditions = self.config.get('loyalty_thresholds', {}).get('auto_abandon_conditions', {})
        loyalty_threshold = abandon_conditions.get('loyalty_max', -5)
        goodwill_threshold = abandon_conditions.get('goodwill_max', 0)
        
        return self.score <= loyalty_threshold and self.goodwill <= goodwill_threshold

    def process_time_tick(self):
        """Process time-based loyalty changes"""
        now = datetime.utcnow()
        
        # Skip if less than a day has passed
        if (now - self.last_tick).days < 1:
            return
            
        regeneration_config = self.config.get('goodwill_regeneration', {})
        
        # High loyalty regeneration
        if self.score >= regeneration_config.get('high_loyalty', {}).get('threshold', 5):
            rate = regeneration_config.get('high_loyalty', {}).get('regeneration_rate', 1)
            max_goodwill = regeneration_config.get('high_loyalty', {}).get('max_goodwill', 36)
            self.goodwill = min(max_goodwill, self.goodwill + rate)
            
        # Low loyalty degeneration
        elif self.score <= regeneration_config.get('low_loyalty', {}).get('threshold', -5):
            rate = regeneration_config.get('low_loyalty', {}).get('degeneration_rate', 1)
            min_goodwill = regeneration_config.get('low_loyalty', {}).get('min_goodwill', 0)
            self.goodwill = max(min_goodwill, self.goodwill - rate)
            
        self.last_tick = now

    def to_dict(self):
        return {
            "score": self.score,
            "goodwill": self.goodwill,
            "tags": self.tags,
            "last_tick": self.last_tick.isoformat()
        }
