"""
Warning System

Implements the three-tier escalation system for chaos events as specified in the Development Bible.
Provides rumor phase, early warning phase, and imminent warning phase before actual events.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from backend.systems.chaos.core.config import ChaosConfig

class WarningPhase(Enum):
    """Warning phases for chaos escalation"""
    RUMOR = "rumor"           # Subtle hints and whispers
    EARLY = "early"           # Clear signs of building trouble
    IMMINENT = "imminent"     # Event about to happen

@dataclass
class WarningEvent:
    """A warning event in the escalation chain"""
    warning_id: str
    region_id: str
    phase: WarningPhase
    event_type: str
    severity: float
    triggered_at: datetime
    expires_at: datetime
    description: str
    visible_clues: List[str]
    hidden_indicators: List[str]
    escalation_probability: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['phase'] = self.phase.value
        data['triggered_at'] = self.triggered_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        return data

class WarningSystem:
    """
    Three-tier warning system for chaos events.
    
    Implements the Development Bible requirement for escalating warnings
    that provide players with opportunities to intervene before chaos events.
    Enhanced with LLM-powered contextual narrative generation.
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        
        # LLM service reference (set by chaos manager)
        self.llm_service: Optional[Any] = None
        
        # Active warnings by region and phase
        self.active_warnings: Dict[str, Dict[str, WarningEvent]] = {}
        self.warning_history: List[WarningEvent] = []
        
        # Escalation timings (configurable)
        self.phase_durations = {
            WarningPhase.RUMOR: timedelta(hours=8),      # Rumor phase lasts 8 hours
            WarningPhase.EARLY: timedelta(hours=4),      # Early warning lasts 4 hours
            WarningPhase.IMMINENT: timedelta(hours=1)    # Imminent warning lasts 1 hour
        }
        
        # Escalation probabilities (how likely each phase is to escalate)
        self.escalation_probabilities = {
            WarningPhase.RUMOR: 0.6,        # 60% chance rumor becomes early warning
            WarningPhase.EARLY: 0.8,        # 80% chance early warning becomes imminent
            WarningPhase.IMMINENT: 0.9      # 90% chance imminent warning triggers event
        }
        
        # System state
        self._initialized = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False
        self._paused = False
        
        # Performance tracking
        self.metrics = {
            'warnings_triggered': 0,
            'warnings_escalated': 0,
            'warnings_prevented': 0,
            'events_from_warnings': 0,
            'llm_generated_warnings': 0,
            'template_fallbacks': 0
        }
    
    def set_llm_service(self, llm_service: Any) -> None:
        """Set the LLM service for enhanced warning generation"""
        self.llm_service = llm_service
    
    async def initialize(self) -> None:
        """Initialize the warning system"""
        self._initialized = True
        if self.llm_service:
            print("Warning system initialized with LLM-enhanced narrative generation")
        else:
            print("Warning system initialized with template-based narratives")
    
    async def start(self) -> None:
        """Start warning monitoring"""
        if not self._initialized:
            await self.initialize()
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        print("Warning system started")
    
    async def stop(self) -> None:
        """Stop warning monitoring"""
        self._running = False
        self._paused = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        print("Warning system stopped")
    
    async def pause(self) -> None:
        """Pause warning monitoring without stopping"""
        if not self._running:
            return
        self._paused = True
    
    async def resume(self) -> None:
        """Resume warning monitoring after pause"""
        if not self._running:
            return
        self._paused = False
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for warning escalation"""
        while self._running:
            try:
                # Skip processing if paused, but keep the loop running
                if self._paused:
                    await asyncio.sleep(1.0)  # Short sleep when paused
                    continue
                
                await self._process_warning_escalations()
                await self._cleanup_expired_warnings()
                
                # Check every 30 seconds
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in warning monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def check_and_trigger_warnings(self, region_id: str, chaos_level: float, 
                                        regional_data: Any) -> bool:
        """
        Check if warnings should be triggered for a region.
        
        Args:
            region_id: Region to check
            chaos_level: Current chaos level
            regional_data: Regional chaos data
            
        Returns:
            True if any warning was triggered
        """
        # Determine if we should start warning chain
        if chaos_level < 0.4:  # Below warning threshold
            return False
        
        # Check if we already have warnings for this region
        region_warnings = self.active_warnings.get(region_id, {})
        
        # Determine appropriate event type based on pressure sources
        event_type = self._determine_event_type(regional_data)
        
        triggered = False
        
        # Start with rumor phase if no existing warnings
        if not region_warnings and chaos_level >= 0.4:
            await self.trigger_warning(region_id, WarningPhase.RUMOR.value, event_type, regional_data)
            triggered = True
        
        # Escalate existing warnings if chaos level is high enough
        elif region_warnings and chaos_level >= 0.7:
            # Find highest current phase and escalate if appropriate
            current_phases = [w.phase for w in region_warnings.values()]
            
            if WarningPhase.RUMOR in current_phases and WarningPhase.EARLY not in current_phases:
                await self.trigger_warning(region_id, WarningPhase.EARLY.value, event_type, regional_data)
                triggered = True
            elif WarningPhase.EARLY in current_phases and WarningPhase.IMMINENT not in current_phases:
                await self.trigger_warning(region_id, WarningPhase.IMMINENT.value, event_type, regional_data)
                triggered = True
        
        return triggered
    
    def _determine_event_type(self, regional_data: Any) -> str:
        """Determine the most likely event type based on pressure sources"""
        if not regional_data or not hasattr(regional_data, 'pressure_sources'):
            return "general_chaos"
        
        # Find the highest pressure source
        max_pressure = 0.0
        dominant_source = "general"
        
        for source, pressure in regional_data.pressure_sources.items():
            if pressure > max_pressure:
                max_pressure = pressure
                dominant_source = source
        
        # Map pressure sources to event types
        event_type_mapping = {
            'economic': 'economic_crisis',
            'political': 'political_upheaval', 
            'social': 'civil_unrest',
            'environmental': 'natural_disaster',
            'diplomatic': 'diplomatic_crisis',
            'temporal': 'temporal_anomaly'
        }
        
        return event_type_mapping.get(dominant_source, 'general_chaos')
    
    async def trigger_warning(self, region_id: str, phase: str, event_type: str, 
                            regional_data: Optional[Any] = None) -> bool:
        """
        Trigger a specific warning phase with enhanced context.
        
        Args:
            region_id: Region for the warning
            phase: Warning phase ('rumor', 'early', 'imminent')
            event_type: Type of event being warned about
            regional_data: Regional context data for LLM generation
            
        Returns:
            True if warning was triggered successfully
        """
        try:
            warning_phase = WarningPhase(phase)
            
            # Generate warning details (potentially using LLM)
            warning_event = await self._create_warning_event(
                region_id, warning_phase, event_type, regional_data
            )
            
            # Store the warning
            if region_id not in self.active_warnings:
                self.active_warnings[region_id] = {}
            
            warning_key = f"{phase}_{event_type}"
            self.active_warnings[region_id][warning_key] = warning_event
            
            # Add to history
            self.warning_history.append(warning_event)
            
            self.metrics['warnings_triggered'] += 1
            print(f"Warning triggered: {phase} phase for {event_type} in {region_id}")
            
            return True
            
        except Exception as e:
            print(f"Error triggering warning: {e}")
            return False
    
    async def _create_warning_event(self, region_id: str, phase: WarningPhase, 
                                  event_type: str, regional_data: Optional[Any] = None) -> WarningEvent:
        """Create a warning event with LLM-enhanced or template-based details"""
        now = datetime.now()
        duration = self.phase_durations[phase]
        
        # Generate phase-appropriate content using LLM or templates
        description, clues, indicators = await self._generate_warning_content(
            phase, event_type, region_id, regional_data
        )
        
        return WarningEvent(
            warning_id=f"{region_id}_{phase.value}_{event_type}_{int(now.timestamp())}",
            region_id=region_id,
            phase=phase,
            event_type=event_type,
            severity=self._calculate_warning_severity(phase),
            triggered_at=now,
            expires_at=now + duration,
            description=description,
            visible_clues=clues,
            hidden_indicators=indicators,
            escalation_probability=self.escalation_probabilities[phase]
        )
    
    async def _generate_warning_content(self, phase: WarningPhase, event_type: str, 
                                      region_id: str, regional_data: Optional[Any] = None) -> tuple:
        """Generate warning content using LLM or fallback to templates"""
        
        # Try LLM generation if available
        if self.llm_service:
            try:
                # Prepare context for LLM
                region_context = self._build_region_context(region_id, regional_data)
                
                # Call LLM service
                llm_response = await self.llm_service.generate_warning_narrative(
                    phase.value, event_type, region_context
                )
                
                if llm_response.success:
                    self.metrics['llm_generated_warnings'] += 1
                    
                    # Parse JSON response
                    import json
                    try:
                        content = json.loads(llm_response.content)
                        return (
                            content.get('description', f'{phase.value.title()} signs detected'),
                            content.get('clues', [f'Signs of {event_type}']),
                            content.get('indicators', [f'Monitoring {event_type}'])
                        )
                    except json.JSONDecodeError:
                        # If not JSON, use the raw content as description
                        return (
                            llm_response.content.strip(),
                            [f"Unusual activity related to {event_type}"],
                            [f"Monitoring {event_type} situation"]
                        )
                        
            except Exception as e:
                print(f"LLM warning generation failed: {e}")
                # Continue to template fallback
        
        # Fallback to template-based generation
        self.metrics['template_fallbacks'] += 1
        return self._generate_template_warning_content(phase, event_type)
    
    def _build_region_context(self, region_id: str, regional_data: Optional[Any]) -> Dict[str, Any]:
        """Build context about the region for LLM generation"""
        context = {
            'region_name': region_id,
            'culture': 'unknown',
            'government_type': 'unknown',
            'economic_focus': 'unknown',
            'tensions': [],
            'key_npcs': []
        }
        
        # Extract data from regional_data if available
        if regional_data:
            if hasattr(regional_data, 'culture'):
                context['culture'] = regional_data.culture
            if hasattr(regional_data, 'government_type'):
                context['government_type'] = regional_data.government_type
            if hasattr(regional_data, 'economic_focus'):
                context['economic_focus'] = regional_data.economic_focus
            if hasattr(regional_data, 'pressure_sources'):
                # Convert pressure sources to readable tensions
                context['tensions'] = [
                    f"{source}: {level:.1%}" 
                    for source, level in regional_data.pressure_sources.items()
                    if level > 0.3
                ]
        
        return context
    
    def _generate_template_warning_content(self, phase: WarningPhase, event_type: str) -> tuple:
        """Generate phase and event-type appropriate warning content using templates"""
        content_templates = {
            WarningPhase.RUMOR: {
                'economic_crisis': {
                    'description': "Merchants whisper of concerning market fluctuations",
                    'clues': ["Nervous traders in the marketplace", "Unusual price changes"],
                    'indicators': ["Market volatility index rising", "Trade route disruptions"]
                },
                'political_upheaval': {
                    'description': "Rumors circulate about political tensions",
                    'clues': ["Hushed conversations in taverns", "Officials acting strangely"],
                    'indicators': ["Increased guard patrols", "Secret meetings"]
                },
                'civil_unrest': {
                    'description': "Citizens express growing dissatisfaction",
                    'clues': ["Grumbling in the streets", "Small gatherings forming"],
                    'indicators': ["Rising complaint frequency", "Agitator presence"]
                }
            },
            WarningPhase.EARLY: {
                'economic_crisis': {
                    'description': "Clear signs of economic instability emerge",
                    'clues': ["Shop closures", "Visible unemployment", "Price volatility"],
                    'indicators': ["Market indicators declining", "Supply chain issues"]
                },
                'political_upheaval': {
                    'description': "Political crisis becomes apparent",
                    'clues': ["Public protests", "Official resignations", "Policy changes"],
                    'indicators': ["Government instability", "Power struggles visible"]
                },
                'civil_unrest': {
                    'description': "Social tensions reach concerning levels",
                    'clues': ["Public demonstrations", "Vocal complaints", "Group formations"],
                    'indicators': ["Social pressure metrics high", "Unrest probability rising"]
                }
            },
            WarningPhase.IMMINENT: {
                'economic_crisis': {
                    'description': "Economic crisis is about to break",
                    'clues': ["Market panic", "Bank runs", "Mass closures"],
                    'indicators': ["Economic collapse imminent", "Emergency measures needed"]
                },
                'political_upheaval': {
                    'description': "Political upheaval is imminent",
                    'clues': ["Mass protests", "Government paralysis", "Crisis talks"],
                    'indicators': ["Political system failing", "Revolution possible"]
                },
                'civil_unrest': {
                    'description': "Civil unrest is about to erupt",
                    'clues': ["Angry crowds", "Violence threats", "Authority defiance"],
                    'indicators': ["Social order breaking down", "Riot conditions present"]
                }
            }
        }
        
        # Get template or use generic fallback
        template = content_templates.get(phase, {}).get(event_type, {
            'description': f"{phase.value.title()} signs of {event_type} detected",
            'clues': [f"Indicators of {event_type}"],
            'indicators': [f"Monitoring {event_type} situation"]
        })
        
        return template['description'], template['clues'], template['indicators']
    
    def _calculate_warning_severity(self, phase: WarningPhase) -> float:
        """Calculate severity score for warning phase"""
        severity_mapping = {
            WarningPhase.RUMOR: 0.3,
            WarningPhase.EARLY: 0.6,
            WarningPhase.IMMINENT: 0.9
        }
        return severity_mapping[phase]
    
    async def _process_warning_escalations(self) -> None:
        """Process automatic warning escalations"""
        current_time = datetime.now()
        
        for region_id, warnings in self.active_warnings.items():
            for warning_key, warning in list(warnings.items()):
                
                # Check if warning has expired
                if current_time >= warning.expires_at:
                    # Determine if it escalates or fades
                    import random
                    if random.random() < warning.escalation_probability:
                        # Escalate to next phase
                        await self._escalate_warning(region_id, warning)
                    else:
                        # Warning fades without escalation
                        self._remove_warning(region_id, warning_key)
                        print(f"Warning faded: {warning.phase.value} phase for {warning.event_type} in {region_id}")
    
    async def _escalate_warning(self, region_id: str, warning: WarningEvent) -> None:
        """Escalate warning to next phase"""
        next_phase = None
        
        if warning.phase == WarningPhase.RUMOR:
            next_phase = WarningPhase.EARLY
        elif warning.phase == WarningPhase.EARLY:
            next_phase = WarningPhase.IMMINENT
        elif warning.phase == WarningPhase.IMMINENT:
            # This should trigger actual event
            await self._trigger_event_from_warning(warning)
            return
        
        if next_phase:
            await self.trigger_warning(region_id, next_phase.value, warning.event_type)
            self.metrics['warnings_escalated'] += 1
            print(f"Warning escalated: {warning.phase.value} -> {next_phase.value} for {warning.event_type} in {region_id}")
    
    async def _trigger_event_from_warning(self, warning: WarningEvent) -> None:
        """Trigger actual chaos event from imminent warning"""
        # This would integrate with the event trigger system
        print(f"Event triggered from warning: {warning.event_type} in {warning.region_id}")
        self.metrics['events_from_warnings'] += 1
        
        # Remove the warning as it has now become reality
        self._remove_warning(warning.region_id, f"imminent_{warning.event_type}")
    
    def _remove_warning(self, region_id: str, warning_key: str) -> None:
        """Remove a warning from active warnings"""
        if region_id in self.active_warnings:
            self.active_warnings[region_id].pop(warning_key, None)
            if not self.active_warnings[region_id]:
                del self.active_warnings[region_id]
    
    async def _cleanup_expired_warnings(self) -> None:
        """Remove expired warnings that didn't escalate"""
        current_time = datetime.now()
        
        for region_id in list(self.active_warnings.keys()):
            for warning_key, warning in list(self.active_warnings[region_id].items()):
                if current_time > warning.expires_at + timedelta(hours=1):  # Grace period
                    self._remove_warning(region_id, warning_key)
    
    # Public interface methods
    
    async def get_region_warnings(self, region_id: str) -> Dict[str, Any]:
        """Get all active warnings for a region"""
        warnings = self.active_warnings.get(region_id, {})
        return {
            'region_id': region_id,
            'active_warnings': [w.to_dict() for w in warnings.values()],
            'warning_count': len(warnings),
            'highest_phase': self._get_highest_warning_phase(warnings)
        }
    
    async def get_all_warnings(self) -> Dict[str, Any]:
        """Get all active warnings across all regions"""
        all_warnings = []
        total_count = 0
        
        for region_id, warnings in self.active_warnings.items():
            total_count += len(warnings)
            for warning in warnings.values():
                warning_dict = warning.to_dict()
                all_warnings.append(warning_dict)
        
        return {
            'total_warnings': total_count,
            'active_regions': len(self.active_warnings),
            'warnings': all_warnings,
            'metrics': self.metrics.copy()
        }
    
    def _get_highest_warning_phase(self, warnings: Dict[str, WarningEvent]) -> Optional[str]:
        """Get the highest (most severe) warning phase in a set of warnings"""
        if not warnings:
            return None
        
        phase_priority = {
            WarningPhase.RUMOR: 1,
            WarningPhase.EARLY: 2,
            WarningPhase.IMMINENT: 3
        }
        
        highest_priority = 0
        highest_phase = None
        
        for warning in warnings.values():
            priority = phase_priority.get(warning.phase, 0)
            if priority > highest_priority:
                highest_priority = priority
                highest_phase = warning.phase.value
        
        return highest_phase
    
    async def clear_warning(self, region_id: str, phase: str) -> bool:
        """Clear a specific warning phase (intervention/mitigation)"""
        try:
            warnings = self.active_warnings.get(region_id, {})
            removed = False
            
            for warning_key, warning in list(warnings.items()):
                if warning.phase.value == phase:
                    self._remove_warning(region_id, warning_key)
                    self.metrics['warnings_prevented'] += 1
                    removed = True
                    print(f"Warning cleared: {phase} phase for {warning.event_type} in {region_id}")
            
            return removed
            
        except Exception as e:
            print(f"Error clearing warning: {e}")
            return False 