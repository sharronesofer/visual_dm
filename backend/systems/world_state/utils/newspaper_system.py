"""
Newspaper System
Surfaces selected world events to players as in-game newspaper articles.
See docs/stubs_needs_consolidation_qna.md for requirements.

- Event Filtering: Collects and filters world events by region, severity, type, and player visibility.
- Formatting: Formats events as newspaper articles (headline, body, byline, date); supports extensibility for new event types.
- Player Visibility: Only surfaces events appropriate for player knowledge; supports narrative hooks and redactions.
- Analytics: Tracks which events are published, read, or ignored; supports future analytics integration.
- TODO: Ensure all narrative/mechanical hooks are present and robust; extensibility for new event types; analytics integration.
"""
from datetime import datetime
# from firebase_admin import db  # TODO: Replace with proper database integration

class Newspaper:
    """
    Collects, filters, and formats world events as newspaper articles for player consumption.
    """
    def __init__(self, region=None):
        self.region = region
        self.articles = []

    def fetch_recent_events(self, days=1, severity_min=1, event_type=None):
        """
        Fetch recent world events from the world log, optionally filtered by region, severity, or type.
        """
        now = datetime.utcnow()
        events = db.reference("/global_state/world_log").get() or {}
        filtered = []
        for e in events.values():
            if self.region and e.get("region_id") != self.region:
                continue
            if event_type and e.get("type") != event_type:
                continue
            if "timestamp" in e:
                event_time = datetime.fromisoformat(e["timestamp"])
                if (now - event_time).days > days:
                    continue
            if e.get("severity", 1) < severity_min:
                continue
            filtered.append(e)
        return filtered

    def format_article(self, event):
        """
        Format a world event as a newspaper article (headline, body, byline, date).
        """
        headline = event.get("summary") or f"{event.get('type', 'Event').title()} in {event.get('region_id', 'the world')}!"
        body = event.get("details", "Details are scarce at this time.")
        byline = event.get("byline", "Staff Reporter")
        date = event.get("timestamp", datetime.utcnow().isoformat())
        return {
            "headline": headline,
            "body": body,
            "byline": byline,
            "date": date
        }

    def publish_latest_edition(self, days=1, severity_min=1, event_type=None):
        """
        Publish the latest edition of the newspaper as a list of formatted articles.
        """
        events = self.fetch_recent_events(days, severity_min, event_type)
        self.articles = [self.format_article(e) for e in events]
        return self.articles 