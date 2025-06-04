"""
Equipment WebSocket Endpoints

FastAPI WebSocket endpoints for the equipment system.
Integrates the equipment WebSocket handler with the main application.
"""

import json
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session

from backend.infrastructure.database import get_db
from backend.infrastructure.websocket.equipment_websocket import equipment_websocket_handler


async def equipment_websocket_endpoint(
    websocket: WebSocket,
    character_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for equipment system real-time communication.
    
    Query Parameters:
    - character_id: UUID of character to subscribe to (optional)
    - client_id: Unique client identifier (optional)
    """
    
    await equipment_websocket_handler.connect(websocket, character_id, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                # Parse JSON message
                message = json.loads(data)
                
                # Handle message with database session
                await equipment_websocket_handler.handle_message(websocket, message, db)
                
            except json.JSONDecodeError:
                await equipment_websocket_handler.send_error(
                    websocket, 
                    "Invalid JSON message format"
                )
            except Exception as e:
                await equipment_websocket_handler.send_error(
                    websocket, 
                    f"Error processing message: {str(e)}"
                )
                
    except WebSocketDisconnect:
        await equipment_websocket_handler.disconnect(websocket)
    except Exception as e:
        print(f"Equipment WebSocket error: {e}")
        await equipment_websocket_handler.disconnect(websocket) 