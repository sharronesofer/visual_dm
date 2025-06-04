"""
Narrative Moderator

Implements narrative intelligence weighting for chaos events.
Ensures chaos serves the narrative and enhances player engagement rather than disrupting it.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from backend.systems.chaos.core.config import ChaosConfig

class NarrativePriority(Enum):
    """Priority levels for narrative themes"""
    BACKGROUND = "background"    # Low priority, ambient elements
    SUPPORTING = "supporting"    # Moderate priority, supports main story
    CENTRAL = "central"         # High priority, key to current narrative
    CRITICAL = "critical"       # Highest priority, must not be disrupted

@dataclass
class NarrativeTheme:
    """A narrative theme with weighting information"""
    theme_id: str
    name: str
    description: str
    priority: NarrativePriority
    weight_modifier: float
    active_until: Optional[datetime]
    related_events: List[str]
    
    def is_active(self) -> bool:
        """Check if theme is currently active"""
        return self.active_until is None or datetime.now() < self.active_until

@dataclass
class StoryBeat:
    """A story beat that affects chaos weighting"""
    beat_id: str
    name: str
    description: str
    drama_level: float  # 0.0 to 1.0
    engagement_impact: float  # How much this affects player engagement
    chaos_compatibility: float  # How compatible this is with chaos events
    duration_hours: float
    created_at: datetime
    
    def is_active(self) -> bool:
        """Check if story beat is still active"""
        return datetime.now() < self.created_at + timedelta(hours=self.duration_hours)

class NarrativeModerator:
    """
    Narrative intelligence system for chaos weighting.
    
    This system ensures chaos events serve the narrative by:
    - Analyzing current story context and player engagement
    - Applying narrative weights to event probabilities
    - Preventing chaos from disrupting critical story moments
    - Enhancing narrative tension through strategic chaos placement
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        
        # Narrative state
        self.active_themes: Dict[str, NarrativeTheme] = {}
        self.active_story_beats: Dict[str, StoryBeat] = {}
        self.theme_priorities: Dict[str, float] = {}
        
        # Player engagement tracking
        self.engagement_history: List[Tuple[datetime, float]] = []
        self.current_engagement: float = 0.7  # Default moderate engagement
        
        # Dramatic tension tracking
        self.tension_history: List[Tuple[datetime, float]] = []
        self.current_tension: float = 0.5  # Default moderate tension
        
        # Event compatibility matrix
        self.event_theme_compatibility = self._initialize_event_compatibility()
        
        # System state
        self._initialized = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False
        self._paused = False
        
        # Performance tracking
        self.metrics = {
            'weight_calculations': 0,
            'narrative_interventions': 0,
            'engagement_adjustments': 0,
            'tension_modifications': 0,
            'themes_processed': 0
        }
    
    async def initialize(self) -> None:
        """Initialize the narrative moderator"""
        # Load default themes
        self._load_default_themes()
        
        self._initialized = True
        print("Narrative moderator initialized with intelligence weighting")
    
    async def start(self) -> None:
        """Start narrative monitoring"""
        if not self._initialized:
            await self.initialize()
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        print("Narrative moderator started")
    
    async def stop(self) -> None:
        """Stop narrative monitoring"""
        self._running = False
        self._paused = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        print("Narrative moderator stopped")
    
    async def pause(self) -> None:
        """Pause narrative monitoring without stopping"""
        if not self._running:
            return
        self._paused = True
    
    async def resume(self) -> None:
        """Resume narrative monitoring after pause"""
        if not self._running:
            return
        self._paused = False
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for narrative analysis"""
        while self._running:
            try:
                # Skip processing if paused, but keep the loop running
                if self._paused:
                    await asyncio.sleep(1.0)  # Short sleep when paused
                    continue
                
                await self._update_narrative_analysis()
                await self._cleanup_expired_elements()
                
                # Update every 2 minutes
                await asyncio.sleep(120)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in narrative monitoring loop: {e}")
                await asyncio.sleep(300)  # Wait longer on error
    
    async def _update_narrative_analysis(self) -> None:
        """Update narrative analysis and engagement tracking"""
        current_time = datetime.now()
        
        # Analyze current narrative state
        tension_level = self._calculate_current_tension()
        engagement_level = self._calculate_current_engagement()
        
        # Update history
        self.tension_history.append((current_time, tension_level))
        self.engagement_history.append((current_time, engagement_level))
        
        # Keep only recent history (last 24 hours)
        cutoff_time = current_time - timedelta(hours=24)
        self.tension_history = [(t, v) for t, v in self.tension_history if t > cutoff_time]
        self.engagement_history = [(t, v) for t, v in self.engagement_history if t > cutoff_time]
        
        # Update current values
        self.current_tension = tension_level
        self.current_engagement = engagement_level
    
    def _calculate_current_tension(self) -> float:
        """Calculate current dramatic tension level"""
        tension = 0.5  # Base tension
        
        # Add tension from active story beats
        for beat in self.active_story_beats.values():
            if beat.is_active():
                tension += beat.drama_level * 0.2
        
        # Add tension from high-priority themes
        for theme in self.active_themes.values():
            if theme.is_active() and theme.priority in [NarrativePriority.CENTRAL, NarrativePriority.CRITICAL]:
                tension += 0.1
        
        return min(1.0, max(0.0, tension))
    
    def _calculate_current_engagement(self) -> float:
        """Calculate current player engagement level"""
        engagement = 0.7  # Base engagement
        
        # Adjust based on story beats
        for beat in self.active_story_beats.values():
            if beat.is_active():
                engagement += beat.engagement_impact * 0.15
        
        # Critical themes boost engagement
        critical_themes = sum(1 for theme in self.active_themes.values() 
                            if theme.is_active() and theme.priority == NarrativePriority.CRITICAL)
        engagement += critical_themes * 0.1
        
        return min(1.0, max(0.0, engagement))
    
    async def get_event_weights(self, narrative_context: Any, pressure_data: Any) -> Dict[str, float]:
        """
        Calculate narrative weights for different regions/event types.
        
        Args:
            narrative_context: Current narrative context
            pressure_data: Current pressure data
            
        Returns:
            Dict mapping region/event identifiers to weight modifiers
        """
        self.metrics['weight_calculations'] += 1
        
        weights = {}
        
        # Base regional weights
        regional_weights = await self._calculate_regional_narrative_weights()
        weights.update(regional_weights)
        
        # Event type weights
        event_type_weights = self._calculate_event_type_weights()
        weights.update(event_type_weights)
        
        # Apply global narrative modifiers
        global_modifier = self._calculate_global_narrative_modifier()
        
        # Apply global modifier to all weights
        for key in weights:
            weights[key] *= global_modifier
        
        self.metrics['narrative_interventions'] += len([w for w in weights.values() if w != 1.0])
        
        return weights
    
    async def _calculate_regional_narrative_weights(self) -> Dict[str, float]:
        """Calculate narrative weights for different regions"""
        weights = {}
        
        # Get active narrative themes and their regional preferences
        for theme in self.active_themes.values():
            if not theme.is_active():
                continue
            
            # Themes may specify preferred regions for events
            for event_type in theme.related_events:
                # This would ideally query region data to determine theme relevance
                # For now, apply theme modifiers broadly
                if theme.priority == NarrativePriority.CRITICAL:
                    # Critical themes heavily modify event probability
                    modifier = theme.weight_modifier * 2.0
                elif theme.priority == NarrativePriority.CENTRAL:
                    modifier = theme.weight_modifier * 1.5
                else:
                    modifier = theme.weight_modifier
                
                weights[f"theme_{theme.theme_id}"] = modifier
        
        return weights
    
    def _calculate_event_type_weights(self) -> Dict[str, float]:
        """Calculate weights for different event types based on narrative compatibility"""
        weights = {}
        
        for event_type, compatibility in self.event_theme_compatibility.items():
            base_weight = 1.0
            
            # Check compatibility with active themes
            for theme in self.active_themes.values():
                if not theme.is_active():
                    continue
                
                if event_type in theme.related_events:
                    # Event type matches theme
                    if theme.priority == NarrativePriority.CRITICAL:
                        base_weight *= 1.8
                    elif theme.priority == NarrativePriority.CENTRAL:
                        base_weight *= 1.4
                    elif theme.priority == NarrativePriority.SUPPORTING:
                        base_weight *= 1.2
                else:
                    # Event type doesn't match theme - reduce weight
                    if theme.priority == NarrativePriority.CRITICAL:
                        base_weight *= 0.3  # Strong reduction for non-matching events
                    elif theme.priority == NarrativePriority.CENTRAL:
                        base_weight *= 0.6
            
            weights[f"event_type_{event_type}"] = base_weight
        
        return weights
    
    def _calculate_global_narrative_modifier(self) -> float:
        """Calculate global modifier based on tension and engagement"""
        modifier = 1.0
        
        # Tension-based modification
        if self.current_tension > 0.8:
            # Very high tension - reduce chaos
            modifier *= 0.4
            self.metrics['tension_modifications'] += 1
        elif self.current_tension > 0.6:
            # High tension - moderate reduction
            modifier *= 0.7
        elif self.current_tension < 0.3:
            # Low tension - increase chaos for excitement
            modifier *= 1.4
            self.metrics['tension_modifications'] += 1
        
        # Engagement-based modification
        if self.current_engagement < 0.4:
            # Low engagement - increase chaos for interest
            modifier *= 1.5
            self.metrics['engagement_adjustments'] += 1
        elif self.current_engagement > 0.8:
            # High engagement - maintain current level
            modifier *= 0.9
        
        return modifier
    
    def _initialize_event_compatibility(self) -> Dict[str, float]:
        """Initialize event-theme compatibility matrix"""
        return {
            'economic_crisis': 1.0,
            'political_upheaval': 1.2,
            'civil_unrest': 0.8,
            'natural_disaster': 0.9,
            'diplomatic_crisis': 1.1,
            'temporal_anomaly': 0.7,
            'faction_conflict': 1.3,
            'resource_shortage': 0.9,
            'technological_failure': 0.8,
            'social_movement': 1.0
        }
    
    def _load_default_themes(self) -> None:
        """Load default narrative themes"""
        default_themes = [
            NarrativeTheme(
                theme_id="political_intrigue",
                name="Political Intrigue",
                description="Themes of political maneuvering and power struggles",
                priority=NarrativePriority.SUPPORTING,
                weight_modifier=1.2,
                active_until=None,
                related_events=["political_upheaval", "faction_conflict", "diplomatic_crisis"]
            ),
            NarrativeTheme(
                theme_id="economic_drama",
                name="Economic Drama",
                description="Themes of trade, commerce, and economic instability",
                priority=NarrativePriority.SUPPORTING,
                weight_modifier=1.1,
                active_until=None,
                related_events=["economic_crisis", "resource_shortage"]
            ),
            NarrativeTheme(
                theme_id="social_upheaval",
                name="Social Upheaval",
                description="Themes of social change and civil movements",
                priority=NarrativePriority.BACKGROUND,
                weight_modifier=1.0,
                active_until=None,
                related_events=["civil_unrest", "social_movement"]
            ),
            NarrativeTheme(
                theme_id="mystical_forces",
                name="Mystical Forces",
                description="Themes involving supernatural or temporal elements",
                priority=NarrativePriority.BACKGROUND,
                weight_modifier=0.8,
                active_until=None,
                related_events=["temporal_anomaly"]
            )
        ]
        
        for theme in default_themes:
            self.active_themes[theme.theme_id] = theme
    
    async def _cleanup_expired_elements(self) -> None:
        """Clean up expired themes and story beats"""
        current_time = datetime.now()
        
        # Clean up expired themes
        expired_themes = [
            theme_id for theme_id, theme in self.active_themes.items()
            if not theme.is_active()
        ]
        for theme_id in expired_themes:
            del self.active_themes[theme_id]
        
        # Clean up expired story beats
        expired_beats = [
            beat_id for beat_id, beat in self.active_story_beats.items()
            if not beat.is_active()
        ]
        for beat_id in expired_beats:
            del self.active_story_beats[beat_id]
    
    # Public interface methods
    
    async def add_narrative_theme(self, theme_id: str, name: str, description: str,
                                 priority: str, weight_modifier: float,
                                 related_events: List[str],
                                 duration_hours: Optional[float] = None) -> bool:
        """Add a new narrative theme"""
        try:
            priority_enum = NarrativePriority(priority)
            
            active_until = None
            if duration_hours:
                active_until = datetime.now() + timedelta(hours=duration_hours)
            
            theme = NarrativeTheme(
                theme_id=theme_id,
                name=name,
                description=description,
                priority=priority_enum,
                weight_modifier=weight_modifier,
                active_until=active_until,
                related_events=related_events
            )
            
            self.active_themes[theme_id] = theme
            self.metrics['themes_processed'] += 1
            
            print(f"Narrative theme added: {name} ({priority}) with modifier {weight_modifier}")
            return True
            
        except ValueError as e:
            print(f"Error adding narrative theme: Invalid priority '{priority}': {e}")
            return False
        except Exception as e:
            print(f"Error adding narrative theme: {e}")
            return False
    
    async def remove_narrative_theme(self, theme_id: str) -> bool:
        """Remove a narrative theme"""
        if theme_id in self.active_themes:
            del self.active_themes[theme_id]
            print(f"Narrative theme removed: {theme_id}")
            return True
        return False
    
    async def add_story_beat(self, beat_id: str, name: str, description: str,
                           drama_level: float, engagement_impact: float,
                           chaos_compatibility: float, duration_hours: float) -> bool:
        """Add a new story beat"""
        try:
            beat = StoryBeat(
                beat_id=beat_id,
                name=name,
                description=description,
                drama_level=max(0.0, min(1.0, drama_level)),
                engagement_impact=max(-0.5, min(0.5, engagement_impact)),
                chaos_compatibility=max(0.0, min(2.0, chaos_compatibility)),
                duration_hours=duration_hours,
                created_at=datetime.now()
            )
            
            self.active_story_beats[beat_id] = beat
            
            print(f"Story beat added: {name} (drama: {drama_level}, engagement: {engagement_impact})")
            return True
            
        except Exception as e:
            print(f"Error adding story beat: {e}")
            return False
    
    async def set_theme_priority(self, theme: str, priority: float) -> bool:
        """Set priority for a narrative theme"""
        try:
            self.theme_priorities[theme] = max(0.0, min(2.0, priority))
            print(f"Theme priority set: {theme} = {priority}")
            return True
        except Exception as e:
            print(f"Error setting theme priority: {e}")
            return False
    
    async def update_engagement_level(self, engagement: float) -> bool:
        """Update player engagement level"""
        try:
            self.current_engagement = max(0.0, min(1.0, engagement))
            self.engagement_history.append((datetime.now(), self.current_engagement))
            print(f"Engagement level updated: {engagement}")
            return True
        except Exception as e:
            print(f"Error updating engagement level: {e}")
            return False
    
    async def update_tension_level(self, tension: float) -> bool:
        """Update dramatic tension level"""
        try:
            self.current_tension = max(0.0, min(1.0, tension))
            self.tension_history.append((datetime.now(), self.current_tension))
            print(f"Tension level updated: {tension}")
            return True
        except Exception as e:
            print(f"Error updating tension level: {e}")
            return False
    
    def get_narrative_status(self) -> Dict[str, Any]:
        """Get current narrative status"""
        return {
            'current_tension': self.current_tension,
            'current_engagement': self.current_engagement,
            'active_themes': {
                theme_id: {
                    'name': theme.name,
                    'priority': theme.priority.value,
                    'weight_modifier': theme.weight_modifier,
                    'is_active': theme.is_active(),
                    'related_events': theme.related_events
                }
                for theme_id, theme in self.active_themes.items()
            },
            'active_story_beats': {
                beat_id: {
                    'name': beat.name,
                    'drama_level': beat.drama_level,
                    'engagement_impact': beat.engagement_impact,
                    'is_active': beat.is_active()
                }
                for beat_id, beat in self.active_story_beats.items()
            },
            'metrics': self.metrics.copy()
        } 