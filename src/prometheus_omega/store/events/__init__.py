# Store events module
from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class EventRecord:
    event_id: str
    event_type: str
    timestamp: float
    data: dict
    
class EventStore:
    def __init__(self):
        self.events = {}
    
    def add(self, event: EventRecord):
        self.events[event.event_id] = event
    
    def get(self, event_id: str) -> Optional[EventRecord]:
        return self.events.get(event_id)
