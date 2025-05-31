"""
Economy WebSocket Routes - FastAPI WebSocket endpoints for real-time economy updates.

Provides WebSocket endpoints for real-time economy system communication including
market updates, price changes, and economic analytics.
"""

import logging
import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.systems.economy.websocket_events import economy_websocket_manager

# Set up logging
logger = logging.getLogger(__name__)

# Create WebSocket router
economy_websocket_router = APIRouter(prefix="/ws/economy", tags=["economy-websocket"])

@economy_websocket_router.websocket("/connect")
async def economy_websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
    client_type: Optional[str] = Query("player")
):
    """
    Main WebSocket endpoint for economy system real-time communication.
    
    Query Parameters:
        client_id: Unique identifier for the client
        client_type: Type of client (player, admin, observer)
    
    Supported Channels:
        - economy: General economy system updates
        - markets: Market creation, updates, and events
        - prices: Price changes and calculations
        - transactions: Transaction completions
        - trade_routes: Trade route updates
        - analytics: Economic analytics updates
        - forecasts: Economic forecast updates
    
    Message Format:
        {
            "type": "message_type",
            "payload": { ... },
            "channel": "channel_name" (for broadcasts)
        }
    
    Subscription Messages:
        - {"type": "subscribe", "payload": {"channel": "markets"}}
        - {"type": "unsubscribe", "payload": {"channel": "prices"}}
        - {"type": "ping", "payload": {}}
        - {"type": "request_status", "payload": {}}
        - {"type": "request_market_data", "payload": {"region_id": 1}}
        - {"type": "request_price_updates", "payload": {"market_id": 1, "resource_ids": ["1", "2"]}}
    """
    await economy_websocket_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Wait for message from client
            message = await websocket.receive_text()
            
            # Handle the message
            await economy_websocket_manager.handle_message(websocket, message)
            
    except WebSocketDisconnect:
        logger.info(f"Economy WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error in economy WebSocket connection: {e}")
    finally:
        # Clean up connection
        await economy_websocket_manager.disconnect(websocket)

@economy_websocket_router.websocket("/markets/{region_id}")
async def market_specific_websocket(
    websocket: WebSocket,
    region_id: int,
    client_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint specifically for market updates in a region.
    
    Args:
        region_id: Region ID to monitor markets for
        client_id: Optional client identifier
    
    This endpoint automatically subscribes to markets and prices channels
    for the specified region.
    """
    await economy_websocket_manager.connect(websocket, client_id)
    
    try:
        # Auto-subscribe to relevant channels for this region
        await economy_websocket_manager.subscribe(websocket, "markets")
        await economy_websocket_manager.subscribe(websocket, "prices")
        
        # Send initial market data for the region
        await economy_websocket_manager._send_market_data(websocket, region_id)
        
        while True:
            # Wait for message from client
            message = await websocket.receive_text()
            
            # Handle the message
            await economy_websocket_manager.handle_message(websocket, message)
            
    except WebSocketDisconnect:
        logger.info(f"Market WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error in market WebSocket connection: {e}")
    finally:
        # Clean up connection
        await economy_websocket_manager.disconnect(websocket)

@economy_websocket_router.websocket("/analytics/{region_id}")
async def analytics_websocket(
    websocket: WebSocket,
    region_id: int,
    client_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time economic analytics and forecasts.
    
    Args:
        region_id: Region ID to monitor analytics for
        client_id: Optional client identifier
    
    This endpoint automatically subscribes to analytics and forecasts channels
    for the specified region.
    """
    await economy_websocket_manager.connect(websocket, client_id)
    
    try:
        # Auto-subscribe to analytics channels
        await economy_websocket_manager.subscribe(websocket, "analytics")
        await economy_websocket_manager.subscribe(websocket, "forecasts")
        await economy_websocket_manager.subscribe(websocket, "economy")
        
        # Send initial analytics data
        try:
            if economy_websocket_manager.economy_manager:
                analytics = economy_websocket_manager.economy_manager.get_economic_analytics(region_id)
                await economy_websocket_manager._send_to_websocket(websocket, {
                    "type": "initial_analytics",
                    "payload": {
                        "region_id": region_id,
                        "analytics": analytics
                    }
                })
        except Exception as e:
            logger.warning(f"Could not send initial analytics: {e}")
        
        while True:
            # Wait for message from client
            message = await websocket.receive_text()
            
            # Handle the message
            await economy_websocket_manager.handle_message(websocket, message)
            
    except WebSocketDisconnect:
        logger.info(f"Analytics WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error in analytics WebSocket connection: {e}")
    finally:
        # Clean up connection
        await economy_websocket_manager.disconnect(websocket)

# Helper functions for triggering WebSocket events from other parts of the system

async def trigger_market_update(market_data: dict):
    """Trigger a market update WebSocket broadcast."""
    await economy_websocket_manager.broadcast_market_update(market_data)

async def trigger_price_update(resource_id: str, market_id: int, price: float, details: dict):
    """Trigger a price update WebSocket broadcast."""
    await economy_websocket_manager.broadcast_price_update(resource_id, market_id, price, details)

async def trigger_transaction_completed(transaction_data: dict):
    """Trigger a transaction completed WebSocket broadcast."""
    await economy_websocket_manager.broadcast_transaction_completed(transaction_data)

async def trigger_economic_analytics(region_id: int, analytics: dict):
    """Trigger an economic analytics WebSocket broadcast."""
    await economy_websocket_manager.broadcast_economic_analytics(region_id, analytics)

async def trigger_economy_status(status: dict):
    """Trigger an economy status WebSocket broadcast."""
    await economy_websocket_manager.broadcast_economy_status(status)

async def trigger_tick_results(region_id: int, results: dict):
    """Trigger a tick results WebSocket broadcast."""
    await economy_websocket_manager.broadcast_tick_results(region_id, results)

# Connection status endpoint
async def get_websocket_status():
    """Get current WebSocket connection status."""
    return {
        "active_connections": len(economy_websocket_manager.connections),
        "total_subscriptions": sum(len(subs) for subs in economy_websocket_manager.subscriptions.values()),
        "channels": list(economy_websocket_manager.channel_subscribers.keys()),
        "channel_counts": {
            channel: len(subscribers) 
            for channel, subscribers in economy_websocket_manager.channel_subscribers.items()
        }
    } 