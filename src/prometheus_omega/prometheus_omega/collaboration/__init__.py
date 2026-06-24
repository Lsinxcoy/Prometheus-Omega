"""L10 Collaboration - 协作层 (Multi-agent+EventBus)"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid, time


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    EVENT = "event"


@dataclass
class AgentMessage:
    msg_id: str
    sender: str
    receiver: str
    msg_type: MessageType
    content: Any
    timestamp: float = field(default_factory=time.time)


class MultiAgentSystem:
    """多代理系统 - 来自X系统"""
    
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.messages: List[AgentMessage] = []
    
    def register_agent(self, agent_id: str, config: Dict):
        self.agents[agent_id] = {"config": config, "status": "active"}
    
    def send_message(self, sender: str, receiver: str, content: Any, 
                     msg_type: MessageType = MessageType.REQUEST) -> str:
        msg = AgentMessage(
            msg_id=str(uuid.uuid4()),
            sender=sender,
            receiver=receiver,
            msg_type=msg_type,
            content=content
        )
        self.messages.append(msg)
        return msg.msg_id


class CIPEventBus:
    """CIP事件总线 - 来自X系统"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
    
    def subscribe(self, event: str, callback: callable):
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(callback)
    
    def publish(self, event: str, data: Any):
        for callback in self.subscribers.get(event, []):
            callback(data)


class KnowledgeBridge:
    """知识桥接 - 来自X系统#67"""
    
    def __init__(self):
        self.bridges: Dict[str, str] = {}
    
    def register(self, from_agent: str, to_agent: str, knowledge: str):
        key = f"{from_agent}->{to_agent}"
        self.bridges[key] = knowledge
    
    def transfer(self, from_agent: str, to_agent: str) -> Optional[str]:
        key = f"{from_agent}->{to_agent}"
        return self.bridges.get(key)


class VectorClock:
    """向量时钟 - 来自X系统#64"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.vector: Dict[str, int] = {agent_id: 0}
    
    def increment(self):
        self.vector[self.agent_id] = self.vector.get(self.agent_id, 0) + 1
    
    def merge(self, other: Dict[str, int]):
        for agent, time in other.items():
            self.vector[agent] = max(self.vector.get(agent, 0), time)


class CausalKG:
    """因果知识图谱 - 来自X系统#65"""
    
    def __init__(self):
        self.edges: Dict[str, List[str]] = {}
    
    def add_causality(self, cause: str, effect: str):
        if cause not in self.edges:
            self.edges[cause] = []
        self.edges[cause].append(effect)
    
    def get_effects(self, cause: str) -> List[str]:
        return self.edges.get(cause, [])


# 工厂
def create_multi_agent_system() -> MultiAgentSystem:
    return MultiAgentSystem()

def create_event_bus() -> CIPEventBus:
    return CIPEventBus()

def create_causal_kg() -> CausalKG:
    return CausalKG()