#!/usr/bin/env python3
"""
Visual DM Mock Server
--------------------
Comprehensive mock server implementing all API contracts for Unity integration testing.
Provides realistic data and responses for development and testing purposes.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Mock Server Configuration
MOCK_SERVER_PORT = 8001
MOCK_SERVER_HOST = "localhost"

# Mock Data Storage (In-memory for testing)
mock_data = {
    "characters": {},
    "quests": {},
    "combat_sessions": {},
    "regions": {},
    "world_state": {},
    "users": {},
    "time_state": {
        "year": 1024,
        "month": 3,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "is_paused": False,
        "time_scale": 1.0
    }
}

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Remove dead connections
                self.disconnect(connection)

# Data Models
class CharacterAttributes(BaseModel):
    strength: int = Field(ge=-3, le=5)
    dexterity: int = Field(ge=-3, le=5)
    constitution: int = Field(ge=-3, le=5)
    intelligence: int = Field(ge=-3, le=5)
    wisdom: int = Field(ge=-3, le=5)
    charisma: int = Field(ge=-3, le=5)

class Character(BaseModel):
    id: str
    character_id: str
    character_name: str
    race: str
    level: int = 1
    experience_points: int = 0
    attributes: CharacterAttributes
    skills: Dict[str, int] = {}
    abilities: List[str] = []
    background: Optional[str] = None
    personality: Optional[str] = None
    alignment: str = "neutral"
    hit_points: int = 10
    max_hit_points: int = 10
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class CharacterCreate(BaseModel):
    character_id: str
    character_name: str
    race: str
    attributes: CharacterAttributes
    background: Optional[str] = None
    personality: Optional[str] = None
    alignment: str = "neutral"

class CharacterUpdate(BaseModel):
    character_name: Optional[str] = None
    background: Optional[str] = None
    personality: Optional[str] = None
    alignment: Optional[str] = None
    experience_points: Optional[int] = None
    level: Optional[int] = None

class QuestObjective(BaseModel):
    id: str
    description: str
    completed: bool = False

class QuestRewards(BaseModel):
    experience: int = 0
    gold: int = 0
    items: List[str] = []

class Quest(BaseModel):
    id: str
    title: str
    description: str
    status: str = "available"  # available, active, completed, failed
    objectives: List[QuestObjective] = []
    rewards: QuestRewards = QuestRewards()
    prerequisites: List[str] = []
    created_at: datetime

class CombatParticipant(BaseModel):
    character_id: str
    initiative: int
    hit_points: int
    max_hit_points: int
    position: Dict[str, float] = {"x": 0.0, "y": 0.0}
    status_effects: List[str] = []

class CombatState(BaseModel):
    combat_id: str
    status: str = "active"  # active, ended, paused
    participants: List[CombatParticipant] = []
    current_turn: int = 0
    created_at: datetime

class GameTime(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    is_paused: bool = False
    time_scale: float = 1.0

class Region(BaseModel):
    id: str
    name: str
    type: str = "rural"  # urban, rural, wilderness
    population: int = 0
    coordinates: Dict[str, float] = {"latitude": 0.0, "longitude": 0.0}
    biome: str = "plains"
    resources: Dict[str, float] = {}
    settlements: List[str] = []

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user_id: str

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int

# Initialize FastAPI app
app = FastAPI(
    title="Visual DM Mock Server",
    description="Mock API server for Visual DM Unity client testing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
manager = ConnectionManager()

# Initialize mock data
def initialize_mock_data():
    """Initialize the mock server with sample data."""
    
    # Sample users
    mock_data["users"]["testuser"] = {
        "id": "user_001",
        "username": "testuser",
        "password": "testpass",  # In real implementation, this would be hashed
        "email": "test@example.com"
    }
    
    # Sample characters
    char_1 = Character(
        id="char_001",
        character_id="char_001",
        character_name="Aragorn",
        race="human",
        level=5,
        experience_points=6500,
        attributes=CharacterAttributes(
            strength=2, dexterity=1, constitution=2,
            intelligence=0, wisdom=1, charisma=1
        ),
        skills={"Athletics": 3, "Survival": 4, "Perception": 2},
        abilities=["Leadership", "Ranger Training", "Sword Mastery"],
        background="Noble Ranger",
        personality="Stoic leader with a strong sense of duty",
        alignment="lawful_good",
        hit_points=45,
        max_hit_points=45,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    char_2 = Character(
        id="char_002",
        character_id="char_002", 
        character_name="Gandalf",
        race="wizard",
        level=10,
        experience_points=15000,
        attributes=CharacterAttributes(
            strength=-1, dexterity=0, constitution=1,
            intelligence=4, wisdom=5, charisma=3
        ),
        skills={"Arcana": 8, "History": 6, "Insight": 5},
        abilities=["Spellcasting", "Ancient Knowledge", "Telepathy"],
        background="Ancient Wizard",
        personality="Wise and mysterious, speaks in riddles",
        alignment="chaotic_good",
        hit_points=60,
        max_hit_points=60,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    mock_data["characters"]["char_001"] = char_1.dict()
    mock_data["characters"]["char_002"] = char_2.dict()
    
    # Sample quests
    quest_1 = Quest(
        id="quest_001",
        title="Rescue the Princess",
        description="The princess has been captured by the dark wizard. Find her location and rescue her safely.",
        status="active",
        objectives=[
            QuestObjective(id="obj_001", description="Find the wizard's tower", completed=True),
            QuestObjective(id="obj_002", description="Defeat the tower guards", completed=False),
            QuestObjective(id="obj_003", description="Rescue the princess", completed=False)
        ],
        rewards=QuestRewards(experience=1000, gold=500, items=["magic_sword", "healing_potion"]),
        prerequisites=[],
        created_at=datetime.now()
    )
    
    quest_2 = Quest(
        id="quest_002",
        title="Gather Ancient Herbs",
        description="The village healer needs rare herbs from the enchanted forest.",
        status="available",
        objectives=[
            QuestObjective(id="obj_004", description="Enter the enchanted forest", completed=False),
            QuestObjective(id="obj_005", description="Find moonleaf herb", completed=False),
            QuestObjective(id="obj_006", description="Find starbloom flower", completed=False)
        ],
        rewards=QuestRewards(experience=300, gold=150, items=["healing_kit"]),
        prerequisites=["quest_001"],
        created_at=datetime.now()
    )
    
    mock_data["quests"]["quest_001"] = quest_1.dict()
    mock_data["quests"]["quest_002"] = quest_2.dict()
    
    # Sample regions
    region_1 = Region(
        id="region_001",
        name="Rivendell",
        type="urban",
        population=5000,
        coordinates={"latitude": 45.5, "longitude": -122.6},
        biome="forest",
        resources={"wood": 0.8, "food": 0.6, "minerals": 0.3},
        settlements=["elven_hall", "marketplace", "library"]
    )
    
    mock_data["regions"]["region_001"] = region_1.dict()

# API Endpoints

@app.get("/")
async def root():
    return {"message": "Visual DM Mock Server", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication Endpoints
@app.post("/auth/login", response_model=AuthResponse)
async def login(credentials: Dict[str, str]):
    username = credentials.get("username")
    password = credentials.get("password")
    
    user = mock_data["users"].get(username)
    if not user or user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate mock JWT token
    token = f"mock_jwt_token_{uuid.uuid4().hex[:16]}"
    
    return AuthResponse(
        access_token=token,
        user_id=user["id"]
    )

# Character Endpoints
@app.post("/characters", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_character(character_data: CharacterCreate):
    char_id = str(uuid.uuid4())
    now = datetime.now()
    
    # Calculate derived stats
    con_modifier = character_data.attributes.constitution
    base_hp = 10 + con_modifier
    
    character = Character(
        id=char_id,
        character_id=character_data.character_id,
        character_name=character_data.character_name,
        race=character_data.race,
        attributes=character_data.attributes,
        background=character_data.background,
        personality=character_data.personality,
        alignment=character_data.alignment,
        hit_points=base_hp,
        max_hit_points=base_hp,
        created_at=now,
        updated_at=now
    )
    
    mock_data["characters"][char_id] = character.dict()
    
    # Broadcast character creation event
    await manager.broadcast({
        "type": "character_update",
        "data": {
            "event": "created",
            "character": character.dict()
        },
        "timestamp": now.isoformat()
    })
    
    return character

@app.get("/characters/{character_id}", response_model=Character)
async def get_character(character_id: str):
    character = mock_data["characters"].get(character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    return Character(**character)

@app.get("/characters/by-game-id/{character_id}", response_model=Character)
async def get_character_by_game_id(character_id: str):
    for char_data in mock_data["characters"].values():
        if char_data["character_id"] == character_id:
            return Character(**char_data)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Character not found"
    )

@app.put("/characters/{character_id}", response_model=Character)
async def update_character(character_id: str, updates: CharacterUpdate):
    character = mock_data["characters"].get(character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Apply updates
    update_data = updates.dict(exclude_unset=True)
    character.update(update_data)
    character["updated_at"] = datetime.now().isoformat()
    
    mock_data["characters"][character_id] = character
    
    # Broadcast character update event
    await manager.broadcast({
        "type": "character_update",
        "data": {
            "event": "updated",
            "character_id": character_id,
            "changes": update_data
        },
        "timestamp": datetime.now().isoformat()
    })
    
    return Character(**character)

@app.get("/characters")
async def search_characters(
    name: Optional[str] = Query(None),
    race: Optional[str] = Query(None),
    level_min: Optional[int] = Query(None),
    level_max: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    characters = list(mock_data["characters"].values())
    
    # Apply filters
    if name:
        characters = [c for c in characters if name.lower() in c["character_name"].lower()]
    if race:
        characters = [c for c in characters if c["race"] == race]
    if level_min:
        characters = [c for c in characters if c["level"] >= level_min]
    if level_max:
        characters = [c for c in characters if c["level"] <= level_max]
    
    # Apply pagination
    total = len(characters)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_chars = characters[start:end]
    
    return {
        "items": paginated_chars,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }

@app.post("/characters/{character_id}/experience", response_model=Character)
async def grant_experience(character_id: str, xp_data: Dict[str, int]):
    character = mock_data["characters"].get(character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    xp_amount = xp_data.get("amount", 0)
    character["experience_points"] += xp_amount
    
    # Check for level up (simple formula: level = sqrt(xp/100))
    new_level = int((character["experience_points"] / 100) ** 0.5) + 1
    if new_level > character["level"]:
        character["level"] = new_level
        character["max_hit_points"] += 5  # Simple HP increase
        character["hit_points"] = character["max_hit_points"]  # Full heal on level up
    
    character["updated_at"] = datetime.now().isoformat()
    mock_data["characters"][character_id] = character
    
    return Character(**character)

# Quest Endpoints
@app.get("/quests")
async def get_quests(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    quests = list(mock_data["quests"].values())
    
    if status:
        quests = [q for q in quests if q["status"] == status]
    
    # Apply pagination
    total = len(quests)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_quests = quests[start:end]
    
    return {
        "items": paginated_quests,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }

@app.get("/quests/{quest_id}")
async def get_quest(quest_id: str):
    quest = mock_data["quests"].get(quest_id)
    if not quest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quest not found"
        )
    return quest

@app.post("/quests/{quest_id}/progress")
async def update_quest_progress(quest_id: str, progress_data: Dict[str, Any]):
    quest = mock_data["quests"].get(quest_id)
    if not quest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quest not found"
        )
    
    # Update quest progress
    objective_id = progress_data.get("objective_id")
    completed = progress_data.get("completed", False)
    
    for objective in quest["objectives"]:
        if objective["id"] == objective_id:
            objective["completed"] = completed
            break
    
    # Check if all objectives are completed
    all_completed = all(obj["completed"] for obj in quest["objectives"])
    if all_completed and quest["status"] == "active":
        quest["status"] = "completed"
    
    mock_data["quests"][quest_id] = quest
    
    # Broadcast quest update
    await manager.broadcast({
        "type": "quest_update",
        "data": {
            "quest_id": quest_id,
            "status": quest["status"],
            "objectives_completed": [obj["id"] for obj in quest["objectives"] if obj["completed"]]
        },
        "timestamp": datetime.now().isoformat()
    })
    
    return quest

# Time System Endpoints
@app.get("/time/current", response_model=GameTime)
async def get_current_time():
    return GameTime(**mock_data["time_state"])

@app.post("/time/advance")
async def advance_time(time_data: Dict[str, Any]):
    amount = time_data.get("amount", 1)
    unit = time_data.get("unit", "minute")
    
    time_state = mock_data["time_state"]
    
    if unit == "minute":
        time_state["minute"] += amount
        if time_state["minute"] >= 60:
            time_state["hour"] += time_state["minute"] // 60
            time_state["minute"] = time_state["minute"] % 60
    elif unit == "hour":
        time_state["hour"] += amount
    elif unit == "day":
        time_state["day"] += amount
    
    # Handle hour overflow
    if time_state["hour"] >= 24:
        time_state["day"] += time_state["hour"] // 24
        time_state["hour"] = time_state["hour"] % 24
    
    # Handle month overflow (simplified)
    if time_state["day"] > 30:
        time_state["month"] += time_state["day"] // 30
        time_state["day"] = time_state["day"] % 30
    
    # Handle year overflow
    if time_state["month"] > 12:
        time_state["year"] += time_state["month"] // 12
        time_state["month"] = time_state["month"] % 12
    
    # Broadcast time update
    await manager.broadcast({
        "type": "time_update",
        "data": {
            "current_time": time_state,
            "time_scale": time_state.get("time_scale", 1.0),
            "is_paused": time_state.get("is_paused", False)
        },
        "timestamp": datetime.now().isoformat()
    })
    
    return {"status": "success", "new_time": time_state}

# Combat System Endpoints
@app.post("/combat/state", response_model=CombatState, status_code=status.HTTP_201_CREATED)
async def create_combat_state(combat_data: Optional[Dict[str, Any]] = None):
    combat_id = str(uuid.uuid4())
    now = datetime.now()
    
    combat_state = CombatState(
        combat_id=combat_id,
        created_at=now
    )
    
    if combat_data:
        participants = combat_data.get("participants", [])
        combat_state.participants = [CombatParticipant(**p) for p in participants]
    
    mock_data["combat_sessions"][combat_id] = combat_state.dict()
    
    return combat_state

@app.get("/combat/state/{combat_id}", response_model=CombatState)
async def get_combat_state(combat_id: str):
    combat = mock_data["combat_sessions"].get(combat_id)
    if not combat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found"
        )
    return CombatState(**combat)

# Region System Endpoints
@app.get("/regions")
async def get_regions():
    return {"items": list(mock_data["regions"].values())}

@app.get("/regions/{region_id}")
async def get_region(region_id: str):
    region = mock_data["regions"].get(region_id)
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Region not found"
        )
    return region

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Send welcome message
    await websocket.send_json({
        "type": "system_message",
        "data": {
            "message": "Connected to Visual DM Mock Server",
            "timestamp": datetime.now().isoformat()
        }
    })
    
    try:
        while True:
            # Listen for messages from client
            data = await websocket.receive_json()
            
            # Echo message back with server timestamp
            response = {
                "type": "echo",
                "data": data,
                "server_timestamp": datetime.now().isoformat()
            }
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Visual DM Mock Server...")
    initialize_mock_data()
    print(f"📊 Initialized with {len(mock_data['characters'])} characters, {len(mock_data['quests'])} quests")
    print(f"🌐 Server running at http://{MOCK_SERVER_HOST}:{MOCK_SERVER_PORT}")
    print(f"📚 API docs available at http://{MOCK_SERVER_HOST}:{MOCK_SERVER_PORT}/docs")

if __name__ == "__main__":
    print("=" * 60)
    print("🎮 Visual DM Mock Server")
    print("=" * 60)
    print(f"🔧 Port: {MOCK_SERVER_PORT}")
    print(f"🌍 Host: {MOCK_SERVER_HOST}")
    print(f"📁 CORS: Enabled for all origins (development mode)")
    print(f"🔌 WebSocket: ws://{MOCK_SERVER_HOST}:{MOCK_SERVER_PORT}/ws")
    print("=" * 60)
    
    uvicorn.run(
        "mock_server:app",
        host=MOCK_SERVER_HOST,
        port=MOCK_SERVER_PORT,
        reload=True,
        log_level="info"
    ) 