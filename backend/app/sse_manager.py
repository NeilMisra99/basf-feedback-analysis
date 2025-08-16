"""Server-Sent Events manager for real-time feedback updates."""

import json
import logging
import queue
import threading
import time
from typing import Dict
from app.models import Feedback

logger = logging.getLogger(__name__)

class SSEManager:
    
    def __init__(self):
        self.clients: Dict[str, 'SSEClient'] = {}
        self.client_counter = 0
        self.lock = threading.Lock()
        
    def add_client(self) -> 'SSEClient':
        """Add a new SSE client."""
        with self.lock:
            client_id = f"client_{self.client_counter}"
            self.client_counter += 1
            client = SSEClient(client_id, self)
            self.clients[client_id] = client
            logger.info(f"New SSE client {client_id} connected. Total: {len(self.clients)}")
            return client
        
    def remove_client(self, client_id: str):
        """Remove an SSE client."""
        with self.lock:
            if client_id in self.clients:
                del self.clients[client_id]
                logger.info(f"SSE client {client_id} disconnected. Total: {len(self.clients)}")
        
    def send_feedback_update(self, feedback: Feedback):
        """Send feedback update to all connected clients."""
        from app.routes import _build_complete_feedback_data
        
        event_data = {
            'type': 'feedback_update',
            'data': _build_complete_feedback_data(feedback)
        }
        
        with self.lock:
            disconnected_clients = [
                client_id for client_id, client in self.clients.items()
                if not self._send_event_to_client(client, event_data)
            ]
            
            for client_id in disconnected_clients:
                self.remove_client(client_id)
                
            logger.info(f"Sent feedback update for {feedback.id} to {len(self.clients)} clients")
    
    def _send_event_to_client(self, client, event_data):
        """Send event to a single client. Returns False if client disconnected."""
        try:
            client.send_event(event_data)
            return True
        except Exception as e:
            logger.warning(f"Failed to send event to client {client.client_id}: {str(e)}")
            return False

class SSEClient:
    
    def __init__(self, client_id: str, manager: SSEManager):
        self.client_id = client_id
        self.manager = manager
        self.message_queue = queue.Queue()
        self.is_connected = True
        
    def send_event(self, data: dict):
        """Send an event to this client."""
        if not self.is_connected:
            return
            
        # Format as SSE event
        json_data = json.dumps(data)
        event = f"data: {json_data}\n\n"
        
        # Queue the event for the generator
        try:
            self.message_queue.put(event, block=False)
        except queue.Full:
            # If queue is full, disconnect the client
            self.disconnect()
            
    def get_events(self):
        """Generator for SSE events."""
        try:
            while self.is_connected:
                try:
                    event = self.message_queue.get(timeout=1)
                    yield event
                except queue.Empty:
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
        except Exception as e:
            logger.error(f"Error in SSE event generator for {self.client_id}: {str(e)}")
        finally:
            self.disconnect()
        
    def disconnect(self):
        """Mark client as disconnected and remove from manager."""
        self.is_connected = False
        self.manager.remove_client(self.client_id)

# Global instance
sse_manager = SSEManager()