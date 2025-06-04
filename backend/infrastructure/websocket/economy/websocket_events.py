"""
Economy WebSocket Events - Real-time WebSocket communication for economy system.

This module provides WebSocket management and real-time event broadcasting
for economy system updates, integrated with the economy event system.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect

from backend.systems.economy.events import (
    EconomyEventBus, EconomyEvent, EconomyEventType, get_event_bus,
    on_economy_event_async
)

# Set up logging
logger = logging.getLogger(__name__)

class EconomyWebSocketManager:
    """
    WebSocket manager for economy system real-time communication.
    
    Manages WebSocket connections, channel subscriptions, and automatic
    event broadcasting integrated with the economy event system.
    """
    
    def __init__(self):
        # Active WebSocket connections
        self.connections: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Channel subscriptions: channel -> set of websockets
        self.channel_subscribers: Dict[str, Set[WebSocket]] = {
            "economy": set(),
            "markets": set(),
            "prices": set(),
            "transactions": set(),
            "trade_routes": set(),
            "analytics": set(),
            "forecasts": set()
        }
        
        # Client subscriptions: websocket -> set of channels
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
        
        # Economy manager reference (set when available)
        self.economy_manager = None
        
        # Event bus integration
        self.event_bus = get_event_bus()
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Set up automatic event broadcasting from economy event system."""
        
        # Resource events -> economy channel
        self.event_bus.subscribe_async(EconomyEventType.RESOURCE_CREATED, self._handle_resource_event)
        self.event_bus.subscribe_async(EconomyEventType.RESOURCE_UPDATED, self._handle_resource_event)
        self.event_bus.subscribe_async(EconomyEventType.RESOURCE_DELETED, self._handle_resource_event)
        self.event_bus.subscribe_async(EconomyEventType.RESOURCE_AMOUNT_CHANGED, self._handle_resource_event)
        self.event_bus.subscribe_async(EconomyEventType.RESOURCE_TRANSFERRED, self._handle_resource_event)
        
        # Market events -> markets channel
        self.event_bus.subscribe_async(EconomyEventType.MARKET_CREATED, self._handle_market_event)
        self.event_bus.subscribe_async(EconomyEventType.MARKET_UPDATED, self._handle_market_event)
        self.event_bus.subscribe_async(EconomyEventType.MARKET_DELETED, self._handle_market_event)
        self.event_bus.subscribe_async(EconomyEventType.MARKET_CONDITIONS_CHANGED, self._handle_market_event)
        
        # Price events -> prices channel
        self.event_bus.subscribe_async(EconomyEventType.PRICE_UPDATED, self._handle_price_event)
        
        # Trade events -> trade_routes channel
        self.event_bus.subscribe_async(EconomyEventType.TRADE_ROUTE_CREATED, self._handle_trade_event)
        self.event_bus.subscribe_async(EconomyEventType.TRADE_ROUTE_UPDATED, self._handle_trade_event)
        self.event_bus.subscribe_async(EconomyEventType.TRADE_ROUTE_DELETED, self._handle_trade_event)
        self.event_bus.subscribe_async(EconomyEventType.TRADE_EXECUTED, self._handle_trade_event)
        self.event_bus.subscribe_async(EconomyEventType.TRADE_FAILED, self._handle_trade_event)
        
        # Transaction events -> transactions channel
        self.event_bus.subscribe_async(EconomyEventType.TRANSACTION_COMPLETED, self._handle_transaction_event)
        self.event_bus.subscribe_async(EconomyEventType.TRANSACTION_FAILED, self._handle_transaction_event)
        
        # Analytics events -> analytics channel
        self.event_bus.subscribe_async(EconomyEventType.ECONOMIC_ANALYTICS_UPDATED, self._handle_analytics_event)
        
        # Forecast events -> forecasts channel
        self.event_bus.subscribe_async(EconomyEventType.ECONOMIC_FORECAST_GENERATED, self._handle_forecast_event)
        
        # System events -> economy channel
        self.event_bus.subscribe_async(EconomyEventType.ECONOMY_INITIALIZED, self._handle_system_event)
        self.event_bus.subscribe_async(EconomyEventType.ECONOMY_SHUTDOWN, self._handle_system_event)
        self.event_bus.subscribe_async(EconomyEventType.ECONOMY_ERROR, self._handle_system_event)
        self.event_bus.subscribe_async(EconomyEventType.ECONOMIC_TICK_PROCESSED, self._handle_system_event)
        self.event_bus.subscribe_async(EconomyEventType.POPULATION_IMPACT_CALCULATED, self._handle_system_event)
    
    async def _handle_resource_event(self, event: EconomyEvent):
        """Handle resource events and broadcast to economy channel."""
        await self._broadcast_to_channel("economy", {
            "type": "resource_event",
            "event_type": event.event_type.value,
            "payload": event.data,
            "timestamp": event.timestamp.isoformat()
        })
    
    async def _handle_market_event(self, event: EconomyEvent):
        """Handle market events and broadcast to markets channel."""
        await self._broadcast_to_channel("markets", {
            "type": "market_event",
            "event_type": event.event_type.value,
            "payload": event.data,
            "timestamp": event.timestamp.isoformat()
        })
    
    async def _handle_price_event(self, event: EconomyEvent):
        """Handle price events and broadcast to prices channel."""
        await self._broadcast_to_channel("prices", {
            "type": "price_event",
            "event_type": event.event_type.value,
            "payload": event.data,
            "timestamp": event.timestamp.isoformat()
        })
    
    async def _handle_trade_event(self, event: EconomyEvent):
        """Handle trade events and broadcast to trade_routes channel."""
        await self._broadcast_to_channel("trade_routes", {
            "type": "trade_event",
            "event_type": event.event_type.value,
            "payload": event.data,
            "timestamp": event.timestamp.isoformat()
        })
    
    async def _handle_transaction_event(self, event: EconomyEvent):
        """Handle transaction events and broadcast to transactions channel."""
        await self._broadcast_to_channel("transactions", {
            "type": "transaction_event",
            "event_type": event.event_type.value,
            "payload": event.data,
            "timestamp": event.timestamp.isoformat()
        })
    
    async def _handle_analytics_event(self, event: EconomyEvent):
        """Handle analytics events and broadcast to analytics channel."""
        await self._broadcast_to_channel("analytics", {
            "type": "analytics_event",
            "event_type": event.event_type.value,
            "payload": event.data,
            "timestamp": event.timestamp.isoformat()
        })
    
    async def _handle_forecast_event(self, event: EconomyEvent):
        """Handle forecast events and broadcast to forecasts channel."""
        await self._broadcast_to_channel("forecasts", {
            "type": "forecast_event",
            "event_type": event.event_type.value,
            "payload": event.data,
            "timestamp": event.timestamp.isoformat()
        })
    
    async def _handle_system_event(self, event: EconomyEvent):
        """Handle system events and broadcast to economy channel."""
        await self._broadcast_to_channel("economy", {
            "type": "system_event",
            "event_type": event.event_type.value,
            "payload": event.data,
            "timestamp": event.timestamp.isoformat()
        })
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None):
        """
        Accept a WebSocket connection and initialize client data.
        
        Args:
            websocket: WebSocket connection
            client_id: Optional client identifier
        """
        await websocket.accept()
        
        # Store connection info
        self.connections[websocket] = {
            "client_id": client_id or f"client_{id(websocket)}",
            "connected_at": asyncio.get_event_loop().time(),
            "channels": set()
        }
        
        # Initialize subscriptions
        self.subscriptions[websocket] = set()
        
        logger.info(f"WebSocket client connected: {self.connections[websocket]['client_id']}")
        
        # Send welcome message
        await self._send_to_websocket(websocket, {
            "type": "connection_established",
            "payload": {
                "client_id": self.connections[websocket]["client_id"],
                "available_channels": list(self.channel_subscribers.keys()),
                "timestamp": asyncio.get_event_loop().time()
            }
        })
    
    async def disconnect(self, websocket: WebSocket):
        """
        Handle WebSocket disconnection and cleanup.
        
        Args:
            websocket: WebSocket connection to disconnect
        """
        if websocket in self.connections:
            client_id = self.connections[websocket]["client_id"]
            
            # Remove from all channel subscriptions
            for channel in list(self.subscriptions.get(websocket, [])):
                await self.unsubscribe(websocket, channel)
            
            # Clean up connection data
            del self.connections[websocket]
            if websocket in self.subscriptions:
                del self.subscriptions[websocket]
            
            logger.info(f"WebSocket client disconnected: {client_id}")
    
    async def subscribe(self, websocket: WebSocket, channel: str):
        """
        Subscribe a WebSocket to a specific channel.
        
        Args:
            websocket: WebSocket connection
            channel: Channel name to subscribe to
        """
        if channel not in self.channel_subscribers:
            await self._send_to_websocket(websocket, {
                "type": "error",
                "payload": {
                    "message": f"Unknown channel: {channel}",
                    "available_channels": list(self.channel_subscribers.keys())
                }
            })
            return
        
        # Add to channel subscribers
        self.channel_subscribers[channel].add(websocket)
        
        # Add to client subscriptions
        if websocket not in self.subscriptions:
            self.subscriptions[websocket] = set()
        self.subscriptions[websocket].add(channel)
        
        # Update connection info
        if websocket in self.connections:
            self.connections[websocket]["channels"].add(channel)
        
        logger.debug(f"Client {self.connections.get(websocket, {}).get('client_id', 'unknown')} subscribed to {channel}")
        
        # Send confirmation
        await self._send_to_websocket(websocket, {
            "type": "subscribed",
            "payload": {
                "channel": channel,
                "subscriber_count": len(self.channel_subscribers[channel])
            }
        })
    
    async def unsubscribe(self, websocket: WebSocket, channel: str):
        """
        Unsubscribe a WebSocket from a specific channel.
        
        Args:
            websocket: WebSocket connection
            channel: Channel name to unsubscribe from
        """
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(websocket)
        
        if websocket in self.subscriptions:
            self.subscriptions[websocket].discard(channel)
        
        if websocket in self.connections:
            self.connections[websocket]["channels"].discard(channel)
        
        logger.debug(f"Client {self.connections.get(websocket, {}).get('client_id', 'unknown')} unsubscribed from {channel}")
        
        # Send confirmation
        await self._send_to_websocket(websocket, {
            "type": "unsubscribed",
            "payload": {
                "channel": channel,
                "subscriber_count": len(self.channel_subscribers.get(channel, set()))
            }
        })
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """
        Handle incoming WebSocket message.
        
        Args:
            websocket: WebSocket connection
            message: Raw message string
        """
        try:
            data = json.loads(message)
            message_type = data.get("type")
            payload = data.get("payload", {})
            
            if message_type == "subscribe":
                channel = payload.get("channel")
                if channel:
                    await self.subscribe(websocket, channel)
                else:
                    await self._send_to_websocket(websocket, {
                        "type": "error",
                        "payload": {"message": "Channel name required for subscription"}
                    })
            
            elif message_type == "unsubscribe":
                channel = payload.get("channel")
                if channel:
                    await self.unsubscribe(websocket, channel)
                else:
                    await self._send_to_websocket(websocket, {
                        "type": "error",
                        "payload": {"message": "Channel name required for unsubscription"}
                    })
            
            elif message_type == "ping":
                await self._send_to_websocket(websocket, {
                    "type": "pong",
                    "payload": {"timestamp": asyncio.get_event_loop().time()}
                })
            
            elif message_type == "request_status":
                await self._send_economy_status(websocket)
            
            elif message_type == "request_market_data":
                region_id = payload.get("region_id")
                await self._send_market_data(websocket, region_id)
            
            elif message_type == "request_price_updates":
                market_id = payload.get("market_id")
                resource_ids = payload.get("resource_ids", [])
                await self._send_price_updates(websocket, market_id, resource_ids)
            
            else:
                await self._send_to_websocket(websocket, {
                    "type": "error",
                    "payload": {"message": f"Unknown message type: {message_type}"}
                })
                
        except json.JSONDecodeError:
            await self._send_to_websocket(websocket, {
                "type": "error",
                "payload": {"message": "Invalid JSON format"}
            })
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self._send_to_websocket(websocket, {
                "type": "error",
                "payload": {"message": "Internal server error"}
            })
    
    # Legacy broadcast methods for backward compatibility
    async def broadcast_market_update(self, market_data: Dict[str, Any]):
        """Broadcast market update (legacy method)."""
        await self._broadcast_to_channel("markets", {
            "type": "market_update",
            "payload": market_data,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_price_update(self, resource_id: str, market_id: int, 
                               price: float, details: Dict[str, Any]):
        """Broadcast price update (legacy method)."""
        await self._broadcast_to_channel("prices", {
            "type": "price_update",
            "payload": {
                "resource_id": resource_id,
                "market_id": market_id,
                "price": price,
                "details": details
            },
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_transaction_completed(self, transaction_data: Dict[str, Any]):
        """Broadcast transaction completed (legacy method)."""
        await self._broadcast_to_channel("transactions", {
            "type": "transaction_completed",
            "payload": transaction_data,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_trade_route_update(self, trade_route_data: Dict[str, Any]):
        """Broadcast trade route update (legacy method)."""
        await self._broadcast_to_channel("trade_routes", {
            "type": "trade_route_update",
            "payload": trade_route_data,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_economic_analytics(self, region_id: int, analytics: Dict[str, Any]):
        """Broadcast economic analytics (legacy method)."""
        await self._broadcast_to_channel("analytics", {
            "type": "economic_analytics",
            "payload": {
                "region_id": region_id,
                "analytics": analytics
            },
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_economic_forecast(self, region_id: int, forecast: Dict[str, Any]):
        """Broadcast economic forecast (legacy method)."""
        await self._broadcast_to_channel("forecasts", {
            "type": "economic_forecast",
            "payload": {
                "region_id": region_id,
                "forecast": forecast
            },
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_economy_status(self, status: Dict[str, Any]):
        """Broadcast economy status (legacy method)."""
        await self._broadcast_to_channel("economy", {
            "type": "economy_status",
            "payload": status,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_tick_results(self, region_id: int, results: Dict[str, Any]):
        """Broadcast tick results (legacy method)."""
        await self._broadcast_to_channel("economy", {
            "type": "tick_results",
            "payload": {
                "region_id": region_id,
                "results": results
            },
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def _broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """
        Broadcast a message to all subscribers of a channel.
        
        Args:
            channel: Channel name
            message: Message to broadcast
        """
        if channel not in self.channel_subscribers:
            logger.warning(f"Attempted to broadcast to unknown channel: {channel}")
            return
        
        subscribers = self.channel_subscribers[channel].copy()
        disconnected = []
        
        for websocket in subscribers:
            try:
                await self._send_to_websocket(websocket, {
                    **message,
                    "channel": channel
                })
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected WebSockets
        for websocket in disconnected:
            await self.disconnect(websocket)
    
    async def _send_to_websocket(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send a message to a specific WebSocket.
        
        Args:
            websocket: WebSocket connection
            message: Message to send
        """
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            raise
    
    async def _send_economy_status(self, websocket: WebSocket):
        """Send current economy status to a WebSocket."""
        try:
            if self.economy_manager:
                status = self.economy_manager.get_economy_status()
                await self._send_to_websocket(websocket, {
                    "type": "economy_status",
                    "payload": status
                })
            else:
                await self._send_to_websocket(websocket, {
                    "type": "economy_status",
                    "payload": {
                        "initialized": False,
                        "message": "Economy manager not available"
                    }
                })
        except Exception as e:
            logger.error(f"Error sending economy status: {e}")
    
    async def _send_market_data(self, websocket: WebSocket, region_id: Optional[int]):
        """Send market data for a region to a WebSocket."""
        try:
            if self.economy_manager and region_id is not None:
                markets = self.economy_manager.get_markets_by_region(region_id)
                market_data = [
                    {
                        "id": market.id,
                        "name": market.name,
                        "region_id": market.region_id,
                        "market_type": market.market_type,
                        "tax_rate": market.tax_rate,
                        "is_active": market.is_active
                    }
                    for market in markets
                ]
                
                await self._send_to_websocket(websocket, {
                    "type": "market_data",
                    "payload": {
                        "region_id": region_id,
                        "markets": market_data
                    }
                })
            else:
                await self._send_to_websocket(websocket, {
                    "type": "error",
                    "payload": {"message": "Economy manager not available or invalid region_id"}
                })
        except Exception as e:
            logger.error(f"Error sending market data: {e}")
    
    async def _send_price_updates(self, websocket: WebSocket, 
                            market_id: Optional[int], resource_ids: Optional[List[str]]):
        """Send price updates for specific resources in a market."""
        try:
            if self.economy_manager and market_id is not None:
                price_data = []
                
                if resource_ids:
                    for resource_id in resource_ids:
                        try:
                            price_info = self.economy_manager.calculate_price(
                                resource_id=resource_id,
                                market_id=market_id
                            )
                            price_data.append({
                                "resource_id": resource_id,
                                "market_id": market_id,
                                "price": price_info.get("price", 0),
                                "details": price_info.get("details", {})
                            })
                        except Exception as e:
                            logger.warning(f"Could not get price for resource {resource_id}: {e}")
                
                await self._send_to_websocket(websocket, {
                    "type": "price_updates",
                    "payload": {
                        "market_id": market_id,
                        "prices": price_data
                    }
                })
            else:
                await self._send_to_websocket(websocket, {
                    "type": "error",
                    "payload": {"message": "Economy manager not available or invalid market_id"}
                })
        except Exception as e:
            logger.error(f"Error sending price updates: {e}")

# Global WebSocket manager instance
economy_websocket_manager = EconomyWebSocketManager()

# Integration functions for EconomyManager to call
async def notify_market_updated(market_data: Dict[str, Any]):
    """Notify WebSocket clients of market update."""
    await economy_websocket_manager.broadcast_market_update(market_data)

async def notify_price_updated(resource_id: str, market_id: int, 
                         price: float, details: Dict[str, Any]):
    """Notify WebSocket clients of price update."""
    await economy_websocket_manager.broadcast_price_update(resource_id, market_id, price, details)

async def notify_transaction_completed(transaction_data: Dict[str, Any]):
    """Notify WebSocket clients of transaction completion."""
    await economy_websocket_manager.broadcast_transaction_completed(transaction_data)

async def notify_trade_route_updated(trade_route_data: Dict[str, Any]):
    """Notify WebSocket clients of trade route update."""
    await economy_websocket_manager.broadcast_trade_route_update(trade_route_data)

async def notify_economic_analytics(region_id: int, analytics: Dict[str, Any]):
    """Notify WebSocket clients of economic analytics update."""
    await economy_websocket_manager.broadcast_economic_analytics(region_id, analytics)

async def notify_economic_forecast(region_id: int, forecast: Dict[str, Any]):
    """Notify WebSocket clients of economic forecast."""
    await economy_websocket_manager.broadcast_economic_forecast(region_id, forecast)

async def notify_economy_status(status: Dict[str, Any]):
    """Notify WebSocket clients of economy status update."""
    await economy_websocket_manager.broadcast_economy_status(status)

async def notify_tick_results(region_id: int, results: Dict[str, Any]):
    """Notify WebSocket clients of tick processing results."""
    await economy_websocket_manager.broadcast_tick_results(region_id, results) 