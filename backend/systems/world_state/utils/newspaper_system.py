"""
Regional Newspaper System

Comprehensive newspaper system that creates region-specific publications with:
- Printing press requirements based on settlement size
- Regional news filtering and aggregation
- Rumor mill and editorial sections for flavor
- Integration with world events and POI systems
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple, Protocol
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from backend.systems.world_state.utils.world_event_utils import (
    filter_events_by_visibility, 
    format_event_for_newspaper,
    aggregate_similar_events
)

logger = logging.getLogger(__name__)


class NewspaperType(Enum):
    """Types of newspapers based on settlement size and resources"""
    BROADSHEET = "broadsheet"      # Major cities with large printing presses
    LOCAL_HERALD = "local_herald"  # Towns with small printing presses
    TOWN_CRIER = "town_crier"      # Villages with public announcements
    RUMOR_MILL = "rumor_mill"      # Informal gossip networks


class ContentSection(Enum):
    """Newspaper content sections"""
    HEADLINE_NEWS = "headline_news"
    REGIONAL_NEWS = "regional_news"
    TRADE_REPORTS = "trade_reports"
    RUMORS = "rumors"
    EDITORIAL = "editorial"
    OBITUARIES = "obituaries"
    WEATHER = "weather"
    ANNOUNCEMENTS = "announcements"


@dataclass
class PrintingPress:
    """Represents a printing press in a settlement"""
    settlement_id: str
    settlement_name: str
    press_size: str  # "large", "medium", "small"
    max_circulation: int
    operating_cost: int
    condition: float  # 0.0 to 1.0, affects quality
    last_maintenance: datetime
    region_id: str
    
    def get_quality_modifier(self) -> float:
        """Get quality modifier based on press condition"""
        return min(1.0, self.condition + 0.2)
    
    def needs_maintenance(self) -> bool:
        """Check if press needs maintenance"""
        days_since_maintenance = (datetime.utcnow() - self.last_maintenance).days
        return days_since_maintenance > 30


@dataclass
class NewsArticle:
    """Individual news article"""
    headline: str
    body: str
    byline: str
    date: str
    section: ContentSection
    region_relevance: float  # 0.0 to 1.0
    importance: int  # 1-10
    source_event_id: Optional[str] = None
    is_rumor: bool = False
    credibility: float = 1.0  # 0.0 to 1.0, lower for rumors


@dataclass
class NewspaperEdition:
    """Complete newspaper edition"""
    title: str
    edition_number: int
    publication_date: datetime
    region_id: str
    settlement_id: str
    newspaper_type: NewspaperType
    articles: List[NewsArticle] = field(default_factory=list)
    circulation: int = 0
    production_cost: int = 0
    
    def add_article(self, article: NewsArticle):
        """Add an article to this edition"""
        self.articles.append(article)
    
    def get_articles_by_section(self, section: ContentSection) -> List[NewsArticle]:
        """Get articles from a specific section"""
        return [article for article in self.articles if article.section == section]


# Business Logic Protocols (dependency injection)
class SettlementDataProvider(Protocol):
    """Protocol for accessing settlement data"""
    
    def get_settlements_in_region(self, region_id: str) -> List[Dict[str, Any]]:
        """Get settlements in a region"""
        ...
    
    def get_settlement_by_id(self, settlement_id: str) -> Optional[Dict[str, Any]]:
        """Get settlement by ID"""
        ...


class EventDataProvider(Protocol):
    """Protocol for accessing event data"""
    
    def get_recent_events(self, region_id: str, days: int = 7, min_severity: int = 1) -> List[Dict[str, Any]]:
        """Get recent events for a region"""
        ...


class RegionalNewspaperSystem:
    """
    Manages regional newspaper production and distribution.
    
    Features:
    - Printing press requirements based on settlement size
    - Regional news filtering and content generation
    - Rumor mill and editorial content
    - Economic costs and circulation management
    """
    
    def __init__(self, 
                 settlement_provider: Optional[SettlementDataProvider] = None,
                 event_provider: Optional[EventDataProvider] = None):
        self.settlement_provider = settlement_provider
        self.event_provider = event_provider
        self.printing_presses: Dict[str, PrintingPress] = {}
        self.newspaper_archives: Dict[str, List[NewspaperEdition]] = {}
        self.rumor_pool: List[Dict[str, Any]] = []
        
        # Content generation templates
        self.rumor_templates = [
            "Some say {target} has been seen {activity} near {location}.",
            "Word from {location} is that {event} happened last {timeframe}.",
            "Travelers report {observation} while passing through {location}.",
            "Local gossips claim {person} was spotted {doing_what} at {location}.",
            "Strange {phenomenon} observed in {location} - locals are {reaction}."
        ]
        
        self.editorial_topics = [
            "The state of trade in our region",
            "Recent political developments", 
            "Concerns about regional security",
            "Seasonal agricultural outlook",
            "The importance of community cooperation",
            "Recent changes to local laws",
            "Infrastructure improvements needed",
            "Cultural events and celebrations"
        ]
    
    def discover_printing_presses(self, region_id: Optional[str] = None) -> Dict[str, PrintingPress]:
        """
        Discover and create printing presses based on settlement size and population.
        
        Args:
            region_id: Optional region to limit discovery to
            
        Returns:
            Dictionary of settlement_id -> PrintingPress
        """
        try:
            if not self.settlement_provider:
                logger.warning("No settlement provider available for press discovery")
                return {}
            
            # Get settlements that could have printing presses
            if region_id:
                settlements = self.settlement_provider.get_settlements_in_region(region_id)
            else:
                # For now, we'll need to implement a get_all_settlements method
                # or iterate through known regions
                settlements = []
            
            discovered_presses = {}
            
            for settlement in settlements:
                press = self._create_printing_press_for_settlement(settlement)
                if press:
                    discovered_presses[settlement['id']] = press
                    logger.info(f"Discovered {press.press_size} printing press in {settlement['name']}")
            
            self.printing_presses.update(discovered_presses)
            return discovered_presses
            
        except Exception as e:
            logger.error(f"Error discovering printing presses: {str(e)}")
            return {}
    
    def _create_printing_press_for_settlement(self, settlement: Dict[str, Any]) -> Optional[PrintingPress]:
        """Create a printing press for a settlement if it qualifies"""
        population = settlement.get('population', 0)
        settlement_type = settlement.get('type', 'village')
        
        # Determine if settlement qualifies for a printing press
        if population < 100:
            return None  # Too small for printing press
        
        # Determine press size based on population and settlement type
        if population >= 1000 or settlement_type in ['city', 'metropolis']:
            press_size = "large"
            max_circulation = population * 0.8
            operating_cost = 100
        elif population >= 300 or settlement_type in ['town']:
            press_size = "medium" 
            max_circulation = population * 0.6
            operating_cost = 50
        else:
            press_size = "small"
            max_circulation = population * 0.4
            operating_cost = 25
        
        return PrintingPress(
            settlement_id=settlement['id'],
            settlement_name=settlement['name'],
            press_size=press_size,
            max_circulation=int(max_circulation),
            operating_cost=operating_cost,
            condition=random.uniform(0.7, 1.0),
            last_maintenance=datetime.utcnow() - timedelta(days=random.randint(1, 29)),
            region_id=settlement.get('region_id', 'unknown')
        )
    
    def publish_regional_edition(self, region_id: str, settlement_id: Optional[str] = None) -> Optional[NewspaperEdition]:
        """
        Publish a newspaper edition for a specific region.
        
        Args:
            region_id: ID of the region
            settlement_id: Optional specific settlement, otherwise use largest in region
            
        Returns:
            Published newspaper edition or None if no printing press available
        """
        try:
            # Find appropriate printing press
            if settlement_id:
                press = self.printing_presses.get(settlement_id)
            else:
                # Find the largest press in the region
                region_presses = [p for p in self.printing_presses.values() if p.region_id == region_id]
                press = max(region_presses, key=lambda p: p.max_circulation) if region_presses else None
            
            if not press:
                logger.warning(f"No printing press available for region {region_id}")
                return None
            
            # Determine newspaper type based on press
            newspaper_type = self._get_newspaper_type(press)
            
            # Create edition
            edition = NewspaperEdition(
                title=self._generate_newspaper_title(press.settlement_name, newspaper_type),
                edition_number=self._get_next_edition_number(press.settlement_id),
                publication_date=datetime.utcnow(),
                region_id=region_id,
                settlement_id=press.settlement_id,
                newspaper_type=newspaper_type,
                circulation=press.max_circulation,
                production_cost=press.operating_cost
            )
            
            # Generate content
            self._add_headline_news(edition, region_id)
            self._add_regional_news(edition, region_id)
            self._add_trade_reports(edition, region_id)
            self._add_rumors(edition, region_id)
            self._add_editorial(edition)
            self._add_weather_report(edition, region_id)
            self._add_announcements(edition, region_id)
            
            # Store in archives
            if press.settlement_id not in self.newspaper_archives:
                self.newspaper_archives[press.settlement_id] = []
            self.newspaper_archives[press.settlement_id].append(edition)
            
            # Apply press condition to article quality
            self._apply_press_quality_effects(edition, press)
            
            logger.info(f"Published {edition.title} #{edition.edition_number} in {press.settlement_name}")
            return edition
            
        except Exception as e:
            logger.error(f"Error publishing regional edition: {str(e)}")
            return None
    
    def _get_newspaper_type(self, press: PrintingPress) -> NewspaperType:
        """Determine newspaper type based on printing press capabilities"""
        if press.press_size == "large":
            return NewspaperType.BROADSHEET
        elif press.press_size == "medium":
            return NewspaperType.LOCAL_HERALD
        else:
            return NewspaperType.TOWN_CRIER
    
    def _generate_newspaper_title(self, settlement_name: str, newspaper_type: NewspaperType) -> str:
        """Generate a newspaper title based on settlement and type"""
        if newspaper_type == NewspaperType.BROADSHEET:
            return f"The {settlement_name} Chronicle"
        elif newspaper_type == NewspaperType.LOCAL_HERALD:
            return f"{settlement_name} Herald"
        else:
            return f"{settlement_name} Town Crier"
    
    def _add_headline_news(self, edition: NewspaperEdition, region_id: str):
        """Add major headline news to the edition"""
        try:
            if not self.event_provider:
                logger.warning("No event provider available for headline news")
                return
                
            # Get recent high-importance events
            events = self.event_provider.get_recent_events(region_id, days=7, min_severity=7)
            events = filter_events_by_visibility(events, region_id, player_knowledge_level=8, max_events=3)
            
            for event in events[:2]:  # Top 2 headlines
                article_data = format_event_for_newspaper(event)
                article = NewsArticle(
                    headline=article_data['headline'],
                    body=article_data['body'],
                    byline=article_data['byline'],
                    date=article_data['date'],
                    section=ContentSection.HEADLINE_NEWS,
                    region_relevance=1.0,
                    importance=event.get('severity', 5),
                    source_event_id=event.get('id')
                )
                edition.add_article(article)
                
        except Exception as e:
            logger.error(f"Error adding headline news: {str(e)}")
    
    def _add_regional_news(self, edition: NewspaperEdition, region_id: str):
        """Add regional news stories"""
        try:
            if not self.event_provider:
                logger.warning("No event provider available for regional news")
                return
                
            # Get medium-importance regional events
            events = self.event_provider.get_recent_events(region_id, days=14, min_severity=4)
            events = filter_events_by_visibility(events, region_id, player_knowledge_level=6, max_events=8)
            
            for event in events[:5]:  # Up to 5 regional stories
                article_data = format_event_for_newspaper(event)
                article = NewsArticle(
                    headline=article_data['headline'],
                    body=self._shorten_article_for_regional(article_data['body']),
                    byline=article_data['byline'],
                    date=article_data['date'],
                    section=ContentSection.REGIONAL_NEWS,
                    region_relevance=0.8,
                    importance=event.get('severity', 3),
                    source_event_id=event.get('id')
                )
                edition.add_article(article)
                
        except Exception as e:
            logger.error(f"Error adding regional news: {str(e)}")
    
    def _add_trade_reports(self, edition: NewspaperEdition, region_id: str):
        """Add trade and economic reports"""
        try:
            # Generate trade content based on regional economic activity
            trade_report = self._generate_trade_report(region_id)
            if trade_report:
                article = NewsArticle(
                    headline="Regional Trade Report",
                    body=trade_report,
                    byline="Trade Correspondent",
                    date=datetime.utcnow().isoformat(),
                    section=ContentSection.TRADE_REPORTS,
                    region_relevance=0.9,
                    importance=4
                )
                edition.add_article(article)
                
        except Exception as e:
            logger.error(f"Error adding trade reports: {str(e)}")
    
    def _add_rumors(self, edition: NewspaperEdition, region_id: str):
        """Add rumors and gossip for flavor"""
        try:
            # Generate 2-4 rumors
            num_rumors = random.randint(2, 4)
            
            for _ in range(num_rumors):
                rumor = self._generate_rumor(region_id)
                if rumor:
                    article = NewsArticle(
                        headline="Local Gossip",
                        body=rumor,
                        byline="Town Gossip",
                        date=datetime.utcnow().isoformat(),
                        section=ContentSection.RUMORS,
                        region_relevance=0.6,
                        importance=1,
                        is_rumor=True,
                        credibility=random.uniform(0.3, 0.8)
                    )
                    edition.add_article(article)
                    
        except Exception as e:
            logger.error(f"Error adding rumors: {str(e)}")
    
    def _add_editorial(self, edition: NewspaperEdition):
        """Add editorial content"""
        try:
            topic = random.choice(self.editorial_topics)
            editorial_content = self._generate_editorial(topic, edition.region_id)
            
            article = NewsArticle(
                headline=f"Editorial: {topic}",
                body=editorial_content,
                byline="Editor",
                date=datetime.utcnow().isoformat(),
                section=ContentSection.EDITORIAL,
                region_relevance=0.7,
                importance=3
            )
            edition.add_article(article)
            
        except Exception as e:
            logger.error(f"Error adding editorial: {str(e)}")
    
    def _add_weather_report(self, edition: NewspaperEdition, region_id: str):
        """Add weather and seasonal information"""
        try:
            weather_report = self._generate_weather_report(region_id)
            
            article = NewsArticle(
                headline="Weather and Seasonal Outlook",
                body=weather_report,
                byline="Weather Observer",
                date=datetime.utcnow().isoformat(),
                section=ContentSection.WEATHER,
                region_relevance=1.0,
                importance=2
            )
            edition.add_article(article)
            
        except Exception as e:
            logger.error(f"Error adding weather report: {str(e)}")
    
    def _add_announcements(self, edition: NewspaperEdition, region_id: str):
        """Add local announcements and notices"""
        try:
            announcements = self._generate_announcements(region_id)
            
            for announcement in announcements:
                article = NewsArticle(
                    headline="Public Notice",
                    body=announcement,
                    byline="Town Clerk",
                    date=datetime.utcnow().isoformat(),
                    section=ContentSection.ANNOUNCEMENTS,
                    region_relevance=1.0,
                    importance=2
                )
                edition.add_article(article)
                
        except Exception as e:
            logger.error(f"Error adding announcements: {str(e)}")
    
    def _generate_rumor(self, region_id: str) -> str:
        """Generate a rumor based on regional context"""
        template = random.choice(self.rumor_templates)
        
        # Get regional context for rumor generation
        locations = self._get_regional_locations(region_id)
        
        # Fill in template with regional information
        rumor = template.format(
            target=random.choice(["a mysterious figure", "a traveling merchant", "a local noble", "strange creatures"]),
            activity=random.choice(["gathering herbs", "conducting secret meetings", "surveying the land", "practicing magic"]),
            location=random.choice(locations) if locations else "the old ruins",
            event=random.choice(["a celebration", "a dispute", "strange lights", "unusual weather"]),
            timeframe=random.choice(["week", "fortnight", "month"]),
            observation=random.choice(["strange lights", "unusual creatures", "armed groups", "merchant caravans"]),
            person=random.choice(["the mayor", "a traveling bard", "mysterious visitors", "local guards"]),
            doing_what=random.choice(["having secret meetings", "counting coins", "arguing loudly", "acting suspiciously"]),
            phenomenon=random.choice(["lights", "sounds", "weather", "animal behavior"]),
            reaction=random.choice(["worried", "excited", "confused", "preparing"])
        )
        
        return rumor
    
    def _generate_editorial(self, topic: str, region_id: str) -> str:
        """Generate editorial content on a given topic"""
        editorial_intros = [
            f"Recent events in our region have highlighted the importance of {topic.lower()}.",
            f"It is the opinion of this publication that {topic.lower()} deserves our immediate attention.",
            f"The citizens of our region must come together to address {topic.lower()}.",
            f"We have observed concerning trends regarding {topic.lower()} in our community."
        ]
        
        editorial_body = [
            "Local leaders must take action to ensure the prosperity of our region.",
            "The safety and wellbeing of our citizens should be the highest priority.",
            "We encourage all residents to participate in community discussions.",
            "Working together, we can overcome any challenges we face.",
            "The future of our region depends on the choices we make today."
        ]
        
        intro = random.choice(editorial_intros)
        body_sentences = random.sample(editorial_body, 2)
        
        return f"{intro} {' '.join(body_sentences)}"
    
    def _generate_weather_report(self, region_id: str) -> str:
        """Generate weather report for the region"""
        current_conditions = random.choice([
            "Clear skies with mild temperatures",
            "Overcast with occasional light rain", 
            "Partly cloudy with gentle breezes",
            "Heavy clouds suggesting incoming storms",
            "Unusually warm for this time of year",
            "Cooler than normal temperatures observed"
        ])
        
        outlook = random.choice([
            "Weather patterns expected to continue through the week.",
            "Conditions may change as seasonal patterns shift.",
            "Farmers should prepare for potential weather changes.",
            "Travelers are advised to plan accordingly.",
            "Local wildlife has been responding to the changing conditions."
        ])
        
        return f"{current_conditions}. {outlook}"
    
    def _generate_announcements(self, region_id: str) -> List[str]:
        """Generate local announcements"""
        announcements = []
        
        announcement_types = [
            "The annual harvest festival will be held next month in the town square.",
            "New trade agreements have been established with neighboring regions.",
            "Road maintenance will begin on the main thoroughfare next week.",
            "The local guard is recruiting able-bodied citizens for patrol duty.",
            "A traveling merchant caravan is expected to arrive within the fortnight.",
            "Local taxes for the upcoming season are due by month's end."
        ]
        
        # Select 1-3 random announcements
        num_announcements = random.randint(1, 3)
        return random.sample(announcement_types, min(num_announcements, len(announcement_types)))
    
    def _get_regional_locations(self, region_id: str) -> List[str]:
        """Get location names within a region for rumor generation"""
        try:
            # This would query the POI database for location names
            return ["the old mill", "the crossroads", "the forest grove", "the merchant quarter", "the town hall"]
        except Exception as e:
            logger.error(f"Error getting regional locations: {str(e)}")
            return ["the local area"]
    
    def _generate_trade_report(self, region_id: str) -> str:
        """Generate trade report content"""
        commodities = ["grain", "textiles", "metals", "livestock", "crafted goods"]
        trends = ["rising", "falling", "stable", "volatile"]
        
        commodity = random.choice(commodities)
        trend = random.choice(trends)
        
        return f"Prices for {commodity} have been {trend} this month. Regional merchants report " \
               f"{'increased' if trend in ['rising', 'volatile'] else 'steady'} demand from neighboring areas. " \
               f"Traders are advised to monitor market conditions closely."
    
    def _shorten_article_for_regional(self, body: str) -> str:
        """Shorten article body for regional news section"""
        sentences = body.split('. ')
        if len(sentences) > 2:
            return '. '.join(sentences[:2]) + '.'
        return body
    
    def _apply_press_quality_effects(self, edition: NewspaperEdition, press: PrintingPress):
        """Apply printing press quality effects to the edition"""
        quality_modifier = press.get_quality_modifier()
        
        if quality_modifier < 0.8:
            # Poor quality press affects readability
            for article in edition.articles:
                if random.random() < 0.3:  # 30% chance of quality issues
                    article.body += " [Text partially illegible due to press conditions]"
    
    def _get_next_edition_number(self, settlement_id: str) -> int:
        """Get the next edition number for a settlement's newspaper"""
        if settlement_id in self.newspaper_archives:
            return len(self.newspaper_archives[settlement_id]) + 1
        return 1
    
    def get_recent_editions(self, settlement_id: str, count: int = 5) -> List[NewspaperEdition]:
        """Get recent newspaper editions for a settlement"""
        if settlement_id not in self.newspaper_archives:
            return []
        
        archives = self.newspaper_archives[settlement_id]
        return sorted(archives, key=lambda e: e.publication_date, reverse=True)[:count]
    
    def get_printing_press_status(self, settlement_id: str) -> Optional[Dict[str, Any]]:
        """Get status information for a printing press"""
        press = self.printing_presses.get(settlement_id)
        if not press:
            return None
        
        return {
            'settlement_id': press.settlement_id,
            'settlement_name': press.settlement_name,
            'press_size': press.press_size,
            'max_circulation': press.max_circulation,
            'condition': press.condition,
            'needs_maintenance': press.needs_maintenance(),
            'operating_cost': press.operating_cost,
            'last_maintenance': press.last_maintenance.isoformat()
        }


# Global instance for easy access
regional_newspaper_system = RegionalNewspaperSystem() 