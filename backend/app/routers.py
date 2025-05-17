from fastapi import APIRouter
from .schemas import WorldData, User, Event

world_router = APIRouter(prefix="/world", tags=["world"])
user_router = APIRouter(prefix="/user", tags=["user"])
event_router = APIRouter(prefix="/event", tags=["event"])

# World endpoints
@world_router.get("/", response_model=list[WorldData])
def list_worlds():
    return []

@world_router.post("/", response_model=WorldData)
def create_world(world: WorldData):
    return world

# User endpoints
@user_router.get("/", response_model=list[User])
def list_users():
    return []

@user_router.post("/", response_model=User)
def create_user(user: User):
    return user

# Event endpoints
@event_router.get("/", response_model=list[Event])
def list_events():
    return []

@event_router.post("/", response_model=Event)
def create_event(event: Event):
    return event
