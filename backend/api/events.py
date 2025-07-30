"""
Server-Sent Events (SSE) for Real-time Notifications
Notifies frontend when new funding opportunities are added
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/events", tags=["events"])

# Global event queue for broadcasting to all connected clients
event_queue: asyncio.Queue = asyncio.Queue()

class EventManager:
    """Manages Server-Sent Events for real-time notifications"""
    
    def __init__(self):
        self.clients = set()
    
    async def add_client(self, client_queue: asyncio.Queue):
        """Add a new client to receive events"""
        self.clients.add(client_queue)
        logger.info(f"New SSE client connected. Total clients: {len(self.clients)}")
    
    async def remove_client(self, client_queue: asyncio.Queue):
        """Remove a client from receiving events"""
        self.clients.discard(client_queue)
        logger.info(f"SSE client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast_event(self, event_type: str, data: dict):
        """Broadcast an event to all connected clients"""
        event_data = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to global queue and all client queues
        await event_queue.put(event_data)
        
        # Send to all connected clients
        disconnected_clients = []
        for client_queue in self.clients.copy():
            try:
                await client_queue.put(event_data)
            except Exception as e:
                logger.error(f"Error sending event to client: {e}")
                disconnected_clients.append(client_queue)
        
        # Clean up disconnected clients
        for client in disconnected_clients:
            await self.remove_client(client)
        
        logger.info(f"Broadcasted {event_type} event to {len(self.clients)} clients")

# Global event manager instance
event_manager = EventManager()

async def event_stream(client_queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    """Generate Server-Sent Events stream for a client"""
    
    try:
        await event_manager.add_client(client_queue)
        
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'message': 'SSE connection established', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        while True:
            try:
                # Wait for events with timeout to send keepalive
                event_data = await asyncio.wait_for(client_queue.get(), timeout=30.0)
                yield f"data: {json.dumps(event_data)}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive ping
                yield f"data: {json.dumps({'type': 'ping', 'timestamp': datetime.now().isoformat()})}\n\n"
            except Exception as e:
                logger.error(f"Error in event stream: {e}")
                break
                
    except Exception as e:
        logger.error(f"Error in event stream setup: {e}")
    finally:
        await event_manager.remove_client(client_queue)

@router.get("/stream")
async def stream_events():
    """
    Server-Sent Events endpoint for real-time notifications
    
    Usage in frontend:
    const eventSource = new EventSource('/api/v1/events/stream');
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'new_funding_opportunity') {
            // Handle new funding opportunity
            console.log('New opportunity:', data.data);
        }
    };
    """
    
    client_queue = asyncio.Queue()
    
    return StreamingResponse(
        event_stream(client_queue),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@router.get("/test")
async def test_event():
    """Test endpoint to trigger a sample event"""
    
    await event_manager.broadcast_event(
        event_type="test",
        data={
            "message": "This is a test event",
            "test_data": {"sample": "value"}
        }
    )
    
    return {"status": "success", "message": "Test event broadcasted"}

# Event broadcasting functions for use by other modules
async def notify_new_funding_opportunity(opportunity_data: dict):
    """Notify clients about a new funding opportunity"""
    await event_manager.broadcast_event(
        event_type="new_funding_opportunity",
        data={
            "id": opportunity_data.get("id"),
            "title": opportunity_data.get("title"),
            "organization": opportunity_data.get("organization"),
            "sector": opportunity_data.get("sector"),
            "amount_exact": opportunity_data.get("amount_exact"),
            "deadline": opportunity_data.get("deadline"),
            "message": f"New funding opportunity: {opportunity_data.get('title')}"
        }
    )

async def notify_pipeline_execution(source_name: str, status: str, records_inserted: int):
    """Notify clients about pipeline execution results"""
    await event_manager.broadcast_event(
        event_type="pipeline_execution",
        data={
            "source_name": source_name,
            "status": status,
            "records_inserted": records_inserted,
            "message": f"Pipeline {source_name}: {status} - {records_inserted} records inserted"
        }
    )

async def notify_cache_refresh():
    """Notify clients that cache has been refreshed"""
    await event_manager.broadcast_event(
        event_type="cache_refresh",
        data={
            "message": "Application cache refreshed - new data available"
        }
    )

async def notify_database_update(table_name: str, operation: str, record_count: int = 1):
    """Generic database update notification"""
    await event_manager.broadcast_event(
        event_type="database_update",
        data={
            "table": table_name,
            "operation": operation,
            "record_count": record_count,
            "message": f"Database updated: {operation} {record_count} record(s) in {table_name}"
        }
    )