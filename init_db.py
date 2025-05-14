from app import create_app
from app.db_init import init_db
from app import db
from app.models.faction import Faction
from app.models.region import Region
from app.models.point_of_interest import PointOfInterest
from app.models.npc import NPC
from app.models.item import Item
from app.models.character import Character
from app.models.quest import Quest
from app.models.arc import Arc
from app.models.quest_log import QuestLog

app = create_app()
with app.app_context():
    # Drop all tables
    db.drop_all()
    
    # Create tables in order
    db.create_all()
    
    # Initialize data
    init_db()
    print("Database initialized successfully!") 