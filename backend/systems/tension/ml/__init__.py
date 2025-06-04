"""
Machine Learning Capabilities for Tension System

Provides advanced AI-driven features for tension prediction and optimization:

1. **Predictive Analytics**:
   - Tension escalation prediction using historical data
   - Conflict outbreak probability modeling
   - Player behavior pattern recognition
   - Regional stability forecasting

2. **Dynamic Balancing**:
   - Real-time difficulty adjustment based on player skill
   - Adaptive tension thresholds per player/region
   - Personalized content generation
   - Optimal quest timing predictions

3. **Pattern Recognition**:
   - Anomaly detection in tension patterns
   - Player preference learning
   - Faction behavior modeling
   - Economic impact correlations

4. **Content Generation**:
   - AI-generated quest narratives based on tension context
   - Dynamic dialogue generation for NPCs
   - Procedural event chain creation
   - Adaptive faction relationship modeling

All ML features are designed to enhance gameplay without being intrusive,
providing behind-the-scenes intelligence to create more engaging experiences.
"""

from .prediction_engine import TensionPredictionEngine
from .pattern_analyzer import TensionPatternAnalyzer  
from .content_generator import AIContentGenerator
from .adaptive_balancer import AdaptiveBalancer

__all__ = [
    'TensionPredictionEngine',
    'TensionPatternAnalyzer', 
    'AIContentGenerator',
    'AdaptiveBalancer'
] 