"""Memory Module - 记忆层"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict, Callable
import time

# 核心类定义
@dataclass
class KeyNode:
    """关键记忆节点"""
    node_id: str
    content: str
    importance: float = 0.5
    utility: float = 0.5
    veracity: float = 0.5
    timestamp: float = field(default_factory=time.time)

class Bank:
    """记忆银行"""
    def __init__(self):
        self._storage: Dict[str, Any] = {}
    
    def store(self, key: str, value: Any) -> bool:
        self._storage[key] = value
        return True
    
    def retrieve(self, key: str) -> Optional[Any]:
        return self._storage.get(key)
    
    def delete(self, key: str) -> bool:
        return bool(self._storage.pop(key, None))
    
    def list_all(self) -> List[str]:
        return list(self._storage.keys())

class BankLayer:
    """分层记忆"""
    def __init__(self, layers: int = 3):
        self.layers = [Bank() for _ in range(layers)]
    
    def store(self, key: str, value: Any, layer: int = 0) -> bool:
        if 0 <= layer < len(self.layers):
            return self.layers[layer].store(key, value)
        return False
    
    def retrieve(self, key: str, layer: int = 0) -> Optional[Any]:
        if 0 <= layer < len(self.layers):
            return self.layers[layer].retrieve(key)
        return None

class MinervaStore:
    """Minerva记忆存储"""
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._storage: Dict[str, Any] = {}
    
    def insert(self, node) -> bool:
        node_id = getattr(node, 'node_id', str(id(node)))
        self._storage[node_id] = node
        return True
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Any]:
        return list(self._storage.values())[:top_k]
    
    def search(self, key: str) -> Optional[Any]:
        return self._storage.get(key)
    
    def delete(self, key: str) -> bool:
        return bool(self._storage.pop(key, None))
    
    def __len__(self):
        return len(self._storage)
