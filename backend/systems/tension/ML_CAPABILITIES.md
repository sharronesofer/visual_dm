# Machine Learning Analytics for Tension System

## Overview

The tension system now includes comprehensive machine learning capabilities that provide advanced analytics, predictive modeling, and pattern recognition. These ML features are designed to enhance gameplay through intelligent automation and insights while maintaining the business logic separation principle.

## Architecture

The ML system is organized into focused modules within `backend/systems/tension/ml/`:

- **`prediction_engine.py`** - Predictive analytics and forecasting
- **`pattern_analyzer.py`** - Pattern recognition and anomaly detection
- **Integration with existing systems** via `integration_manager.py`

## Core ML Capabilities

### 1. Predictive Analytics 🔮

#### Tension Escalation Prediction
- **Purpose**: Predict how tension will change over time in specific locations
- **Input**: Historical data, current events, player actions, faction relationships
- **Output**: Predicted tension level with confidence intervals and trend analysis
- **Use Cases**: 
  - Proactive quest generation before conflicts arise
  - NPC behavior pre-adjustment
  - Player warning systems

**Example Output:**
```python
prediction = TensionPrediction(
    region_id="marketplace_district",
    poi_id="central_market", 
    current_tension=0.45,
    predicted_tension=0.72,
    confidence=PredictionConfidence.HIGH,
    trend=TensionTrend.RISING,
    probability_thresholds={
        'conflict': 0.35,
        'violence': 0.18,
        'mass_exodus': 0.12
    }
)
```

#### Conflict Outbreak Prediction
- **Purpose**: Assess likelihood of major conflicts erupting in regions
- **Analysis**: Risk factors, historical patterns, current tensions
- **Recommendations**: Intervention strategies to prevent conflicts
- **Timeline Estimates**: When conflicts might occur if unchecked

#### Regional Stability Forecasting
- **Purpose**: Multi-day stability outlook for entire regions
- **Scope**: 7-day rolling forecasts with daily granularity
- **Integration**: Considers all POIs and their interactions within a region

#### Player Impact Prediction
- **Purpose**: Predict how specific player actions will affect regional tension
- **Personalization**: Learns individual player behavior patterns
- **Preemptive Response**: Enables systems to prepare for predicted changes

### 2. Pattern Recognition & Anomaly Detection 🔍

#### Pattern Types Detected

**Cyclic Patterns**
- Daily tension cycles (market rush hours, night time calm)
- Weekly patterns (market days, rest days)
- Seasonal variations
- Event-based cycles

**Trending Patterns**
- Long-term tension increases/decreases
- Gradual regional stability changes
- Escalation spirals
- Peace consolidation trends

**Spike Patterns**
- Sudden tension increases from specific events
- Recurring crisis points
- Trigger event identification

**Stability Patterns**
- Consistently stable regions (low variance)
- Highly volatile areas (high variance)
- Baseline establishment

#### Anomaly Detection

**Statistical Anomalies**
- Values significantly outside normal ranges (>2.5 standard deviations)
- Sudden spikes or drops in tension
- Outlier behavior identification

**Temporal Anomalies**
- Unusual tension levels for specific times of day
- Behavior that doesn't match historical time-based patterns
- Schedule-breaking events

**Contextual Anomalies**
- Tension levels that don't match surrounding regions
- Behavior inconsistent with recent events
- Cross-reference pattern violations

**Collective Anomalies**
- Multiple locations showing synchronized unusual behavior
- Region-wide pattern deviations
- Coordinated tension changes

#### Player Behavior Profiling

**Behavioral Pattern Analysis**
- Action frequency (combat, diplomacy, trade, quests)
- Regional preferences
- Impact history on tension levels
- Activity timing patterns

**Risk Assessment**
- Combat escalation likelihood
- Tension destabilization risk
- Unpredictability metrics
- Intervention requirements

### 3. Integration with Game Systems 🎮

#### NPC System Integration
- **Behavior Modification**: NPCs react based on tension levels and predictions
- **Response Levels**: Calm → Anxious → Fearful → Panicked → Fleeing
- **Dynamic Elements**:
  - Pricing adjustments (panic markups, stability discounts)
  - Availability changes (reluctance to trade in high tension)
  - Dialogue variations (tension-appropriate conversations)
  - Movement patterns (fleeing dangerous areas)

**Example NPC Response:**
```python
# High tension area
npc_modifiers = {
    'price_modifier': 1.3,  # 30% markup due to fear
    'item_availability_modifier': 0.6,  # Only selling essentials
    'dialogue_mood': 'panicked',
    'movement_probability': 0.3,  # 30% chance to relocate
    'cooperation_modifier': 0.6  # Less helpful
}
```

#### Quest System Integration
- **Dynamic Generation**: Tension levels trigger appropriate quest types
- **Quest Types by Tension**:
  - **High Tension**: Conflict resolution, emergency rescue, security patrol
  - **Rising Tension**: Investigation quests, mediation missions
  - **Post-Conflict**: Peace restoration, refugee aid, reconciliation
- **Cooldown Management**: Prevents quest spam in volatile areas
- **Completion Effects**: Quest success reduces regional tension

#### Combat System Integration
- **Difficulty Scaling**: Tension affects encounter rates and enemy behavior
- **Combat Effects by Tension Level**:
  - **Peaceful**: Reduced spawn rates, friendly encounters
  - **Watchful**: Normal rates, alert guards
  - **Aggressive**: Increased encounters, hostile NPCs
  - **Hostile**: Frequent combat, combat-ready enemies
  - **Warfare**: Constant danger, faction conflicts

**Combat Modifiers:**
```python
# Warfare-level tension
combat_modifiers = {
    'spawn_rate_multiplier': 2.0,
    'enemy_aggression': 2.0,
    'enemy_damage_multiplier': 1.4,
    'faction_conflict_chance': 0.8,
    'civilian_flee_chance': 0.9
}
```

## Technical Implementation

### Business Logic Focus
- **Separation of Concerns**: ML business logic is separated from infrastructure
- **Integration Points**: Clean interfaces with existing game systems
- **Placeholder Infrastructure**: Ready for actual ML model integration
- **Event-Driven Architecture**: Responds to and emits events for cross-system coordination

### Event Coordination
The `TensionIntegrationManager` orchestrates responses across all systems:

```python
# Major tension change triggers:
# 1. ML analysis (anomaly detection, predictions)
# 2. NPC behavior updates
# 3. Combat modifier adjustments  
# 4. Quest generation evaluation
# 5. Cross-system event emission
```

### Performance Considerations
- **Caching**: Pattern and prediction results cached for performance
- **Thresholds**: Configurable sensitivity to prevent noise
- **Batch Processing**: Efficient handling of multiple events
- **Lazy Loading**: Analysis triggered only when needed

## Usage Examples

### Getting Comprehensive Analysis
```python
integration_manager = TensionIntegrationManager()

# Get full analysis for a location
analysis = integration_manager.get_comprehensive_analysis(
    region_id="trade_district",
    poi_id="merchant_quarter"
)

# Results include:
# - Current tension and predictions
# - Pattern analysis and anomalies
# - NPC behavior modifications
# - Combat difficulty adjustments
# - Quest recommendations
# - ML-generated recommendations
```

### Predictive Player Impact
```python
# Before player takes major action
impact_prediction = prediction_engine.analyze_player_impact_prediction(
    player_id="player_123",
    region_id="diplomatic_quarter", 
    action_type="combat"
)

# Enables preemptive system adjustments
if abs(impact_prediction['predicted_tension_change']) > 0.1:
    # Coordinate preemptive responses across systems
    await integration_manager._coordinate_preemptive_responses(...)
```

### Pattern-Based Insights
```python
# Analyze regional patterns
patterns = pattern_analyzer.analyze_tension_patterns("merchant_district")

# Check for anomalies
anomalies = pattern_analyzer.detect_anomalies(
    region_id="merchant_district",
    poi_id="main_bazaar", 
    current_tension=0.8  # Unusually high
)

# Get player behavioral profile
player_profile = pattern_analyzer.analyze_player_behavior("player_123")
```

## Future Extensions

### Ready for ML Infrastructure
The current implementation provides business logic interfaces ready for:
- **Model Training Pipelines**: Historical data → trained models
- **Real-time Inference**: Live prediction serving
- **A/B Testing**: Model performance comparison
- **Continuous Learning**: Models that improve over time

### Advanced Features (Planned)
- **Deep Learning Models**: More sophisticated pattern recognition
- **Ensemble Methods**: Combining multiple prediction approaches
- **Transfer Learning**: Cross-region knowledge sharing
- **Reinforcement Learning**: Dynamic parameter optimization

### Content Generation AI
- **Narrative Generation**: AI-written quest descriptions
- **Dialogue Generation**: Context-appropriate NPC conversations  
- **Dynamic Storytelling**: Adaptive narrative based on tension patterns

## Integration Health Monitoring

The system includes comprehensive health monitoring:

```python
health_status = integration_manager.get_integration_health()

# Monitor:
# - Individual system status
# - ML component availability  
# - Cross-system coordination health
# - Performance metrics
# - Error rates and recovery
```

## Benefits for Gameplay

### For Players
- **Immersive World**: NPCs and world react intelligently to tensions
- **Meaningful Choices**: Actions have predictable but complex consequences
- **Dynamic Content**: Quests and challenges adapt to world state
- **Reduced Grinding**: Smart difficulty scaling maintains engagement

### For Game Masters/Developers
- **Automated Management**: System handles complex cross-system interactions
- **Predictive Insights**: Early warning of potential issues
- **Balanced Gameplay**: ML-driven difficulty and content adjustments
- **Rich Analytics**: Deep understanding of player impact and world dynamics

### For the Game World
- **Believable Simulation**: Realistic cause-and-effect relationships
- **Emergent Storytelling**: Organic narrative development from system interactions
- **Adaptive Difficulty**: Maintains optimal challenge level
- **Living World**: Continuous evolution based on player actions

The ML capabilities transform the tension system from a reactive mechanism into a predictive, adaptive intelligence that enhances every aspect of the gaming experience while maintaining the architectural principles of clean separation and focused business logic. 