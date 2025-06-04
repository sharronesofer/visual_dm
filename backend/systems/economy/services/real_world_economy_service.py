"""
Real World Economy Integration Service

Integrates real-world economic data (DOW, NASDAQ, etc.) into the game's 
economic cycles to create realistic economic patterns and crisis events.
"""

import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import os
from dataclasses import dataclass

from backend.infrastructure.database.economy.advanced_models import EconomicCycle
from backend.systems.economy.models.advanced_economy import EconomicCyclePhase

logger = logging.getLogger(__name__)


@dataclass
class MarketIndicator:
    """Market indicator data from real world"""
    symbol: str
    current_price: float
    change_percent: float
    volume: int
    timestamp: datetime
    market_cap: Optional[float] = None


@dataclass
class EconomicIndicator:
    """Economic indicator from real world"""
    indicator_name: str
    current_value: float
    change_percent: float
    timestamp: datetime
    description: str


class RealWorldEconomyService:
    """Service for integrating real-world economic data"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        
        # API configuration
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.marketstack_key = os.getenv('MARKETSTACK_API_KEY', '')
        
        # Market indicators to track
        self.major_indices = {
            'DJI': 'Dow Jones Industrial Average',
            'SPX': 'S&P 500',
            'IXIC': 'NASDAQ Composite',
            'RUT': 'Russell 2000',
            'VIX': 'Volatility Index'
        }
        
        # Economic indicators to track
        self.economic_indicators = {
            'GDP': 'Gross Domestic Product',
            'CPI': 'Consumer Price Index',
            'UNEMPLOYMENT': 'Unemployment Rate',
            'FEDERAL_FUNDS_RATE': 'Federal Funds Rate',
            'TREASURY_YIELD': '10-Year Treasury Yield'
        }
        
        # Mapping real-world changes to game economic phases
        self.economic_phase_thresholds = {
            'severe_decline': (-10.0, EconomicCyclePhase.BUST),      # -10% or worse
            'decline': (-5.0, EconomicCyclePhase.RECESSION),        # -5% to -10%
            'mild_decline': (-2.0, EconomicCyclePhase.STABLE),      # -2% to -5%
            'stable': (2.0, EconomicCyclePhase.STABLE),             # -2% to +2%
            'growth': (5.0, EconomicCyclePhase.GROWTH),             # +2% to +5%
            'strong_growth': (10.0, EconomicCyclePhase.BOOM),       # +5% to +10%
            'extreme_growth': (float('inf'), EconomicCyclePhase.BOOM) # +10% or more
        }
    
    def fetch_market_data(self) -> Dict[str, MarketIndicator]:
        """Fetch current market data from real-world APIs"""
        market_data = {}
        
        # Try Alpha Vantage first (free tier allows 5 calls per minute)
        if self.alpha_vantage_key and self.alpha_vantage_key != 'demo':
            market_data.update(self._fetch_alpha_vantage_data())
        
        # Fallback to Marketstack if available
        if self.marketstack_key and len(market_data) < 3:
            market_data.update(self._fetch_marketstack_data())
        
        # If no API keys available, use mock data
        if not market_data:
            market_data = self._generate_mock_market_data()
        
        return market_data
    
    def _fetch_alpha_vantage_data(self) -> Dict[str, MarketIndicator]:
        """Fetch data from Alpha Vantage API"""
        indicators = {}
        
        try:
            # Fetch major indices one by one (API limits)
            for symbol, name in list(self.major_indices.items())[:3]:  # Limit to 3 to stay within rate limits
                url = f"https://www.alphavantage.co/query"
                params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': self.alpha_vantage_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse Alpha Vantage response
                    if 'Global Quote' in data:
                        quote = data['Global Quote']
                        indicators[symbol] = MarketIndicator(
                            symbol=symbol,
                            current_price=float(quote.get('05. price', 0)),
                            change_percent=float(quote.get('10. change percent', '0%').rstrip('%')),
                            volume=int(quote.get('06. volume', 0)),
                            timestamp=datetime.now()
                        )
                
                # Rate limiting
                import time
                time.sleep(12)  # Alpha Vantage free tier: 5 calls per minute
        
        except Exception as e:
            logger.warning(f"Error fetching Alpha Vantage data: {e}")
        
        return indicators
    
    def _fetch_marketstack_data(self) -> Dict[str, MarketIndicator]:
        """Fetch data from Marketstack API as fallback"""
        indicators = {}
        
        try:
            url = "http://api.marketstack.com/v1/eod/latest"
            params = {
                'access_key': self.marketstack_key,
                'symbols': ','.join(self.major_indices.keys()),
                'limit': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('data', []):
                    symbol = item.get('symbol')
                    if symbol in self.major_indices:
                        # Calculate change percent (requires previous day data)
                        change_percent = 0.0  # Simplified for demo
                        
                        indicators[symbol] = MarketIndicator(
                            symbol=symbol,
                            current_price=float(item.get('close', 0)),
                            change_percent=change_percent,
                            volume=int(item.get('volume', 0)),
                            timestamp=datetime.now()
                        )
        
        except Exception as e:
            logger.warning(f"Error fetching Marketstack data: {e}")
        
        return indicators
    
    def _generate_mock_market_data(self) -> Dict[str, MarketIndicator]:
        """Generate realistic mock market data when APIs are unavailable"""
        import random
        
        indicators = {}
        
        # Base values for major indices (approximate 2024 values)
        base_values = {
            'DJI': 38000,
            'SPX': 4800,
            'IXIC': 15000,
            'RUT': 2000,
            'VIX': 15
        }
        
        for symbol, name in self.major_indices.items():
            # Generate realistic daily movement
            base_price = base_values.get(symbol, 1000)
            daily_change = random.uniform(-3.0, 3.0)  # ±3% daily movement
            current_price = base_price * (1 + daily_change / 100)
            
            indicators[symbol] = MarketIndicator(
                symbol=symbol,
                current_price=current_price,
                change_percent=daily_change,
                volume=random.randint(1000000, 10000000),
                timestamp=datetime.now()
            )
        
        return indicators
    
    def fetch_economic_indicators(self) -> Dict[str, EconomicIndicator]:
        """Fetch economic indicators from real-world APIs"""
        indicators = {}
        
        try:
            if self.alpha_vantage_key and self.alpha_vantage_key != 'demo':
                # Fetch key economic indicators
                for indicator_code, description in self.economic_indicators.items():
                    url = f"https://www.alphavantage.co/query"
                    params = {
                        'function': 'TREASURY_YIELD' if 'TREASURY' in indicator_code else 'ECONOMIC_INDICATOR',
                        'interval': 'monthly',
                        'apikey': self.alpha_vantage_key
                    }
                    
                    # Note: In production, you'd implement specific API calls for each indicator
                    # For now, using mock data with realistic patterns
                    break
        
        except Exception as e:
            logger.warning(f"Error fetching economic indicators: {e}")
        
        # Generate mock economic indicators
        indicators = self._generate_mock_economic_indicators()
        
        return indicators
    
    def _generate_mock_economic_indicators(self) -> Dict[str, EconomicIndicator]:
        """Generate realistic mock economic indicators"""
        import random
        
        indicators = {}
        
        # Mock current economic conditions (2024-style)
        mock_indicators = {
            'GDP': {'value': 2.1, 'change': random.uniform(-0.5, 0.8)},
            'CPI': {'value': 3.2, 'change': random.uniform(-0.3, 0.4)},
            'UNEMPLOYMENT': {'value': 3.8, 'change': random.uniform(-0.2, 0.3)},
            'FEDERAL_FUNDS_RATE': {'value': 5.25, 'change': random.uniform(-0.25, 0.25)},
            'TREASURY_YIELD': {'value': 4.5, 'change': random.uniform(-0.15, 0.20)}
        }
        
        for code, data in mock_indicators.items():
            indicators[code] = EconomicIndicator(
                indicator_name=self.economic_indicators[code],
                current_value=data['value'],
                change_percent=data['change'],
                timestamp=datetime.now(),
                description=f"Current {self.economic_indicators[code]}: {data['value']}%"
            )
        
        return indicators
    
    def analyze_market_sentiment(self, market_data: Dict[str, MarketIndicator]) -> Dict[str, Any]:
        """Analyze overall market sentiment from real-world data"""
        
        if not market_data:
            return {"sentiment": "neutral", "confidence": 0.0, "analysis": "No market data available"}
        
        # Calculate weighted sentiment
        sentiment_scores = []
        weights = {'DJI': 0.3, 'SPX': 0.4, 'IXIC': 0.2, 'RUT': 0.1}  # Weight by market importance
        
        for symbol, indicator in market_data.items():
            weight = weights.get(symbol, 0.1)
            sentiment_scores.append(indicator.change_percent * weight)
        
        average_sentiment = sum(sentiment_scores)
        
        # Determine sentiment category
        if average_sentiment > 2.0:
            sentiment = "very_bullish"
        elif average_sentiment > 0.5:
            sentiment = "bullish"
        elif average_sentiment > -0.5:
            sentiment = "neutral"
        elif average_sentiment > -2.0:
            sentiment = "bearish"
        else:
            sentiment = "very_bearish"
        
        # Calculate confidence based on volume and consistency
        volume_factor = sum(indicator.volume for indicator in market_data.values()) / len(market_data)
        volume_confidence = min(1.0, volume_factor / 5000000)  # Normalize volume
        
        # Consistency factor (less spread = higher confidence)
        change_values = [ind.change_percent for ind in market_data.values()]
        if len(change_values) > 1:
            consistency = 1.0 - (max(change_values) - min(change_values)) / 10.0
        else:
            consistency = 0.5
        
        confidence = (volume_confidence + max(0, consistency)) / 2.0
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "average_change": average_sentiment,
            "market_indicators": {symbol: ind.change_percent for symbol, ind in market_data.items()},
            "analysis": f"Market showing {sentiment} sentiment with {confidence:.1%} confidence"
        }
    
    def determine_economic_phase_from_real_world(self, market_data: Dict[str, MarketIndicator],
                                               economic_indicators: Dict[str, EconomicIndicator]) -> EconomicCyclePhase:
        """Determine appropriate economic phase based on real-world data"""
        
        sentiment_analysis = self.analyze_market_sentiment(market_data)
        average_market_change = sentiment_analysis.get("average_change", 0.0)
        
        # Factor in economic indicators
        economic_factor = 0.0
        if economic_indicators:
            gdp_indicator = economic_indicators.get('GDP')
            unemployment_indicator = economic_indicators.get('UNEMPLOYMENT')
            
            if gdp_indicator:
                economic_factor += gdp_indicator.change_percent * 2  # GDP has high weight
            
            if unemployment_indicator:
                # Higher unemployment is bad, so invert the change
                economic_factor -= unemployment_indicator.change_percent * 1.5
        
        # Combine market and economic factors
        combined_score = (average_market_change * 0.7) + (economic_factor * 0.3)
        
        # Determine phase based on combined score
        for threshold_name, (threshold, phase) in self.economic_phase_thresholds.items():
            if combined_score <= threshold:
                return phase
        
        return EconomicCyclePhase.STABLE  # Default fallback
    
    def update_game_economic_cycles(self, region_ids: List[str] = None) -> Dict[str, Any]:
        """Update game economic cycles based on real-world data"""
        
        if not region_ids:
            # Get all active regions
            active_cycles = self.db_session.query(EconomicCycle).filter(
                EconomicCycle.is_active == True
            ).all()
            region_ids = list(set([cycle.region_id for cycle in active_cycles]))
        
        # Fetch real-world data
        market_data = self.fetch_market_data()
        economic_indicators = self.fetch_economic_indicators()
        
        # Analyze sentiment and determine appropriate phase
        sentiment_analysis = self.analyze_market_sentiment(market_data)
        target_phase = self.determine_economic_phase_from_real_world(market_data, economic_indicators)
        
        updated_cycles = []
        
        for region_id in region_ids:
            # Get current cycle for region
            current_cycle = self.db_session.query(EconomicCycle).filter(
                EconomicCycle.region_id == region_id,
                EconomicCycle.is_active == True
            ).first()
            
            if current_cycle:
                # Calculate if cycle should change
                should_update = self._should_update_cycle(current_cycle, target_phase, sentiment_analysis)
                
                if should_update:
                    # Update cycle to match real-world conditions
                    self._update_cycle_to_real_world_conditions(
                        current_cycle, target_phase, market_data, economic_indicators, sentiment_analysis
                    )
                    updated_cycles.append({
                        "region_id": region_id,
                        "old_phase": current_cycle.current_phase,
                        "new_phase": target_phase.value,
                        "reason": "real_world_integration"
                    })
        
        self.db_session.commit()
        
        return {
            "updated_cycles": updated_cycles,
            "market_sentiment": sentiment_analysis,
            "target_phase": target_phase.value,
            "market_data_summary": {
                symbol: {"price": ind.current_price, "change": ind.change_percent}
                for symbol, ind in market_data.items()
            },
            "economic_indicators_summary": {
                code: {"value": ind.current_value, "change": ind.change_percent}
                for code, ind in economic_indicators.items()
            }
        }
    
    def _should_update_cycle(self, current_cycle: EconomicCycle, target_phase: EconomicCyclePhase,
                           sentiment_analysis: Dict[str, Any]) -> bool:
        """Determine if a cycle should be updated based on real-world conditions"""
        
        # Don't update if already in the correct phase
        if current_cycle.current_phase == target_phase.value:
            return False
        
        # Check confidence threshold
        confidence = sentiment_analysis.get("confidence", 0.0)
        if confidence < 0.6:  # Require at least 60% confidence
            return False
        
        # Check if enough time has passed since last update
        time_since_start = datetime.utcnow() - current_cycle.phase_start_date
        min_phase_duration = timedelta(days=7)  # At least 1 week
        
        if time_since_start < min_phase_duration:
            return False
        
        # Check magnitude of change required
        phase_severity = {
            EconomicCyclePhase.BUST: -3,
            EconomicCyclePhase.RECESSION: -2,
            EconomicCyclePhase.RECOVERY: -1,
            EconomicCyclePhase.STABLE: 0,
            EconomicCyclePhase.GROWTH: 1,
            EconomicCyclePhase.BOOM: 2
        }
        
        current_severity = phase_severity.get(EconomicCyclePhase(current_cycle.current_phase), 0)
        target_severity = phase_severity.get(target_phase, 0)
        
        # Require strong signal for major phase changes
        change_magnitude = abs(target_severity - current_severity)
        if change_magnitude >= 2:  # Major change (e.g., stable to boom/bust)
            return sentiment_analysis.get("confidence", 0.0) > 0.8
        
        return True
    
    def _update_cycle_to_real_world_conditions(self, cycle: EconomicCycle, target_phase: EconomicCyclePhase,
                                             market_data: Dict[str, MarketIndicator],
                                             economic_indicators: Dict[str, EconomicIndicator],
                                             sentiment_analysis: Dict[str, Any]):
        """Update a cycle to reflect real-world economic conditions"""
        
        # Update basic cycle information
        cycle.current_phase = target_phase.value
        cycle.phase_start_date = datetime.utcnow()
        
        # Calculate new economic indicators based on real-world data
        sentiment = sentiment_analysis.get("sentiment", "neutral")
        confidence = sentiment_analysis.get("confidence", 0.5)
        
        # Map sentiment to prosperity level
        sentiment_prosperity_map = {
            "very_bullish": 0.9,
            "bullish": 0.7,
            "neutral": 0.5,
            "bearish": 0.3,
            "very_bearish": 0.1
        }
        
        base_prosperity = sentiment_prosperity_map.get(sentiment, 0.5)
        cycle.prosperity_level = base_prosperity * confidence + (1 - confidence) * cycle.prosperity_level
        
        # Update inflation rate based on economic indicators
        if 'CPI' in economic_indicators:
            cpi_change = economic_indicators['CPI'].change_percent
            cycle.inflation_rate = max(-0.5, min(0.5, cpi_change / 10.0))  # Normalize to game scale
        
        # Update unemployment rate
        if 'UNEMPLOYMENT' in economic_indicators:
            unemployment = economic_indicators['UNEMPLOYMENT'].current_value
            cycle.unemployment_rate = max(0.01, min(0.5, unemployment / 100.0))  # Convert percentage
        
        # Update trade volume based on market activity
        if market_data:
            average_volume = sum(ind.volume for ind in market_data.values()) / len(market_data)
            volume_factor = min(2.0, average_volume / 5000000)  # Normalize
            cycle.trade_volume = volume_factor
        
        # Add trigger events
        trigger_events = cycle.trigger_events or []
        trigger_events.append(f"Real-world integration: {sentiment} market sentiment")
        cycle.trigger_events = trigger_events
        
        # Calculate appropriate phase duration based on volatility
        market_volatility = abs(sentiment_analysis.get("average_change", 0.0))
        if market_volatility > 3.0:  # High volatility
            cycle.phase_duration_days = 14  # Shorter phases during volatile times
        elif market_volatility < 1.0:  # Low volatility
            cycle.phase_duration_days = 60  # Longer phases during stable times
        else:
            cycle.phase_duration_days = 30  # Normal duration
    
    def create_crisis_from_real_world_event(self, market_crash_threshold: float = -8.0) -> Optional[Dict[str, Any]]:
        """Create economic crisis events based on real-world market crashes"""
        
        market_data = self.fetch_market_data()
        sentiment_analysis = self.analyze_market_sentiment(market_data)
        
        average_change = sentiment_analysis.get("average_change", 0.0)
        
        if average_change <= market_crash_threshold:
            # Severe market decline detected
            crisis_severity = min(10.0, abs(average_change))
            
            crisis_event = {
                "event_type": "market_crash",
                "severity": crisis_severity,
                "description": f"Global market crash: {average_change:.1f}% decline",
                "trigger_data": {
                    "real_world_data": {
                        symbol: {"price": ind.current_price, "change": ind.change_percent}
                        for symbol, ind in market_data.items()
                    },
                    "sentiment_analysis": sentiment_analysis
                },
                "recommended_actions": [
                    "Trigger emergency economic cycles",
                    "Increase unemployment rates",
                    "Reduce trade volumes",
                    "Activate crisis response systems"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return crisis_event
        
        return None
    
    def get_real_world_economic_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of real-world economic conditions"""
        
        market_data = self.fetch_market_data()
        economic_indicators = self.fetch_economic_indicators()
        sentiment_analysis = self.analyze_market_sentiment(market_data)
        recommended_phase = self.determine_economic_phase_from_real_world(market_data, economic_indicators)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "market_data": {
                symbol: {
                    "price": indicator.current_price,
                    "change_percent": indicator.change_percent,
                    "volume": indicator.volume,
                    "name": self.major_indices.get(symbol, symbol)
                }
                for symbol, indicator in market_data.items()
            },
            "economic_indicators": {
                code: {
                    "name": indicator.indicator_name,
                    "value": indicator.current_value,
                    "change_percent": indicator.change_percent,
                    "description": indicator.description
                }
                for code, indicator in economic_indicators.items()
            },
            "sentiment_analysis": sentiment_analysis,
            "recommended_game_phase": recommended_phase.value,
            "crisis_detected": sentiment_analysis.get("average_change", 0.0) < -5.0,
            "api_status": {
                "alpha_vantage_configured": bool(self.alpha_vantage_key and self.alpha_vantage_key != 'demo'),
                "marketstack_configured": bool(self.marketstack_key),
                "using_mock_data": not (self.alpha_vantage_key or self.marketstack_key)
            }
        } 