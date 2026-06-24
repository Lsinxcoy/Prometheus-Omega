# Prometheus Omega - Lifecycle Module
# 重新实现，保留Z系统设计思想，确保无语法错误

from __future__ import annotations
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import IntEnum, Enum, auto
from collections import defaultdict

# Foundation imports
from prometheus_omega.foundation import (
    Node, Edge, NodeType, EdgeType, MemoryLayer,
    ZConfig, OmegaConfig, Strictness, SecurityPosture,
    GateCheckResult, WriteGateResult, EvolutionCheckResult,
    TrustLevel, ProvenanceType
)

# Memory imports
from prometheus_omega.memory import MinervaStore


class BeliefSystem:
    """E17: Three-layer belief state management."""
    
    def __init__(self, store: MinervaStore, config: Optional[ZConfig] = None):
        self._store = store
        self._config = config or ZConfig()
        self._event_buffer: Dict[str, Node] = {}
        self._preference_memory: Dict[str, Node] = {}
        self._profile_narrative: str = ""
    
    def record_event(self, content: str, branch: str = "main", creator_agent: str = "") -> str:
        """Layer 1: Record a raw event in EventBuffer."""
        node = Node(
            content=content,
            type=NodeType.EVENT,
            utility=1.0,
            layer=MemoryLayer.WORKING,
            trust=TrustLevel.PENDING,
            creator_agent=creator_agent,
            branch=branch
        )
        node_id = self._store._system_insert(node, reason="belief")
        self._event_buffer[node_id] = node
        return node_id
    
    def form_preference(self, event_id: str, branch: str = "main") -> Optional[Node]:
        """Layer 2: Promote to PreferenceMemory if reinforced."""
        event = self._store.get(event_id, branch)
        if event and event.trust >= TrustLevel.MEDIUM:
            event.layer = MemoryLayer.EPISODIC
            self._preference_memory[event_id] = event
            return event
        return None
    
    def get_preferences(self) -> List[Node]:
        """Get all preferences."""
        return list(self._preference_memory.values())


class DreamCycle:
    """Sleep-wake cycle for memory consolidation."""
    
    def __init__(self, store: MinervaStore):
        self._store = store
        self._dream_buffer: List[Node] = []
        self._last_dream_time = 0.0
    
    def wake_collect(self, layer: MemoryLayer = MemoryLayer.WORKING) -> List[Node]:
        """Collect memories during wake state."""
        # Simplified: return recent nodes
        return []
    
    def dream_consolidate(self, nodes: List[Node]) -> List[str]:
        """Consolidate during dream state."""
        consolidated = []
        for node in nodes:
            # Move to deeper memory layer
            if node.layer == MemoryLayer.WORKING:
                node.layer = MemoryLayer.EPISODIC
                consolidated.append(node.content)
        self._last_dream_time = time.time()
        return consolidated
    
    def should_dream(self) -> bool:
        """Check if dream cycle should trigger."""
        return time.time() - self._last_dream_time > 3600  # 1 hour


class MemoryTrajectory:
    """Track memory evolution over time."""
    
    def __init__(self):
        self._history: Dict[str, List[Tuple[float, str]]] = defaultdict(list)
    
    def record(self, node_id: str, event: str):
        """Record an event in trajectory."""
        self._history[node_id].append((time.time(), event))
    
    def get_trajectory(self, node_id: str) -> List[Tuple[float, str]]:
        """Get full trajectory for a node."""
        return self._history.get(node_id, [])
    
    def summarize(self, node_id: str) -> str:
        """Generate natural language summary."""
        trajectory = self.get_trajectory(node_id)
        if not trajectory:
            return "No history"
        return f"Events: {len(trajectory)}, Last: {trajectory[-1][1]}"


class ConsolidationGuard:
    """Guard against excessive consolidation."""
    
    def __init__(self, max_per_hour: int = 100):
        self._max_per_hour = max_per_hour
        self._consolidation_times: List[float] = []
    
    def can_consolidate(self) -> bool:
        """Check if consolidation is allowed."""
        now = time.time()
        # Remove entries older than 1 hour
        self._consolidation_times = [t for t in self._consolidation_times if now - t < 3600]
        return len(self._consolidation_times) < self._max_per_hour
    
    def record_consolidation(self):
        """Record a consolidation event."""
        self._consolidation_times.append(time.time())


class LifecycleManager:
    """Main lifecycle coordinator."""
    
    def __init__(self, store: MinervaStore, config: Optional[ZConfig] = None):
        self._store = store
        self._config = config or ZConfig()
        self.belief = BeliefSystem(store, config)
        self.dream = DreamCycle(store)
        self.trajectory = MemoryTrajectory()
        self._consolidation_guard = ConsolidationGuard()
    
    def tick(self) -> Dict[str, Any]:
        """Main lifecycle tick."""
        results = {"status": "ok"}
        
        # Dream cycle check
        if self.dream.should_dream():
            nodes = self.dream.wake_collect()
            if self._consolidation_guard.can_consolidate():
                consolidated = self.dream.dream_consolidate(nodes)
                self._consolidation_guard.record_consolidation()
                results["consolidated"] = len(consolidated)
        
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """Get lifecycle statistics."""
        return {
            "belief_events": len(self.belief._event_buffer),
            "preferences": len(self.belief._preference_memory),
            "dream_buffer": len(self.dream._dream_buffer),
            "trajectory_count": len(self.trajectory._history)
        }


# Factory function
def create_lifecycle_manager(store: MinervaStore, config: Optional[ZConfig] = None) -> LifecycleManager:
    """Create a lifecycle manager instance."""
    return LifecycleManager(store, config)
