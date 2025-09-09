"""
WebSocket message models for worker communication.

This module contains the shared message types and structures used for
WebSocket communication between workers and clients.
"""

import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class MessageType(Enum):
    """Message types for WebSocket communication"""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    MESSAGE = "message"
    STREAM = "stream"
    COMPLETE = "complete"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


@dataclass
class WebSocketMessage:
    """Structured message format for WebSocket communication"""
    type: MessageType
    id: str
    data: Any
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps({
            "type": self.type.value,
            "id": self.id,
            "data": self.data,
            "timestamp": self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WebSocketMessage':
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls(
            type=MessageType(data["type"]),
            id=data["id"],
            data=data["data"],
            timestamp=data.get("timestamp", time.time())
        )
