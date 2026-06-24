# Prometheus Omega - Lifecycle Module (简化版)
from __future__ import annotations
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import IntEnum, Enum

class MemoryLayer(IntEnum):
    WORKING = 0
    EPISODIC = 1
    SEMANTIC = 2

class NodeType(Enum):
    CONCEPT = "concept"
    EVENT = "event"
    RELATION = "relation"

@dataclass
class Node:
    content: str
    type: NodeType
    utility: float = 1.0
    layer: MemoryLayer = MemoryLayer.WORKING
    trust: int = 0

class LifecycleManager:
    """简化的生命周期管理"""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
    
    def add(self, node_id: str, content: str) -> str:
        node = Node(content=content, type=NodeType.CONCEPT)
        self.nodes[node_id] = node
        return node_id
    
    def get(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)
