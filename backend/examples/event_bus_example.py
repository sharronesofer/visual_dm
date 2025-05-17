"""
Example usage of the EventBus system.

This file demonstrates how to use the EventBus for both synchronous and asynchronous event communication.
"""

import asyncio
import time
from pydantic import BaseModel
from typing import List

# Import the EventBus
from backend.core.events.event_bus import event_bus, EventPriority

# Define some typed events using Pydantic models
class UserEvent(BaseModel):
    """Event related to user actions."""
    user_id: str
    action: str
    timestamp: float = time.time()

class ChatMessage(BaseModel):
    """Chat message event."""
    sender_id: str
    content: str
    room_id: str
    timestamp: float = time.time()

class GameState(BaseModel):
    """Game state update event."""
    state: str
    players: List[str]
    current_turn: int
    timestamp: float = time.time()

# Define some event handlers
def log_user_events(event: UserEvent):
    """Log all user events."""
    print(f"USER EVENT: User {event.user_id} performed {event.action} at {event.timestamp}")

def notify_chat_message(event: ChatMessage):
    """Handler for new chat messages."""
    print(f"CHAT: [{event.room_id}] {event.sender_id}: {event.content}")

def game_state_changed(event: GameState):
    """Handler for game state changes."""
    print(f"GAME: State changed to {event.state}, current turn: {event.current_turn}")
    print(f"Players: {', '.join(event.players)}")

# Define an async handler
async def process_user_action_async(event: UserEvent):
    """Process user actions asynchronously."""
    print(f"Starting async processing of user action: {event.action}")
    await asyncio.sleep(1)  # Simulate async work
    print(f"Finished async processing of user action: {event.action}")

# Subscribe to events
def setup_subscribers():
    """Set up event subscribers."""
    # Subscribe to typed events
    event_bus.subscribe(UserEvent, log_user_events)
    event_bus.subscribe(ChatMessage, notify_chat_message)
    event_bus.subscribe(GameState, game_state_changed)
    
    # Subscribe to async handler
    event_bus.subscribe_async(UserEvent, process_user_action_async)
    
    # Subscribe with priority and filtering
    event_bus.subscribe(
        UserEvent, 
        lambda e: print(f"HIGH PRIORITY: {e.user_id} did {e.action}"), 
        priority=EventPriority.HIGH
    )
    
    # Only process logout events
    event_bus.subscribe(
        UserEvent,
        lambda e: print(f"LOGOUT: User {e.user_id} logged out"),
        filter_func=lambda e: e.action == "logout"
    )

# Example function to emit events
async def emit_example_events():
    """Emit some example events."""
    # User login event
    user_login = UserEvent(user_id="user123", action="login")
    print("\nEmitting user login event...")
    event_bus.emit(UserEvent, user_login)
    await asyncio.sleep(1.5)  # Wait for async handlers
    
    # Chat message
    chat_msg = ChatMessage(sender_id="user123", content="Hello world!", room_id="general")
    print("\nEmitting chat message...")
    event_bus.emit(ChatMessage, chat_msg)
    
    # Game state
    game = GameState(state="playing", players=["user123", "user456"], current_turn=1)
    print("\nEmitting game state update...")
    event_bus.emit(GameState, game)
    
    # User logout - will trigger filtered handler
    user_logout = UserEvent(user_id="user123", action="logout")
    print("\nEmitting user logout event...")
    event_bus.emit(UserEvent, user_logout)
    await asyncio.sleep(1.5)  # Wait for async handlers

# Main async function to run the example
async def main():
    """Run the example."""
    print("EventBus Example - Setting up subscribers")
    setup_subscribers()
    
    print("Starting event emission...")
    await emit_example_events()
    
    print("\nExample completed!")

if __name__ == "__main__":
    asyncio.run(main()) 