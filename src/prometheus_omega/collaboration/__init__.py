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
    """Agent间通信的消息结构"""
    msg_id: str
    sender: str
    receiver: str
    msg_type: MessageType
    content: Any
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    reply_to: Optional[str] = None
    ttl: int = 300  # 消息生存时间(秒)
    
    def is_expired(self) -> bool:
        """检查消息是否过期"""
        return (time.time() - self.timestamp) > self.ttl
    
    def age(self) -> float:
        """获取消息年龄(秒)"""
        return time.time() - self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'msg_id': self.msg_id,
            'sender': self.sender,
            'receiver': self.receiver,
            'msg_type': self.msg_type.value,
            'content': self.content,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
            'reply_to': self.reply_to,
            'ttl': self.ttl,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """从字典创建"""
        if isinstance(data.get('msg_type'), str):
            data['msg_type'] = MessageType(data['msg_type'])
        return cls(**data)


class MultiAgentSystem:
    """多代理系统 - 来自X系统"""
    
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.messages: List[AgentMessage] = []
        self.message_queues: Dict[str, List[AgentMessage]] = {}
        self._history_size = 1000
    
    def register_agent(self, agent_id: str, config: Dict):
        """注册Agent"""
        self.agents[agent_id] = {"config": config, "status": "active"}
        self.message_queues[agent_id] = []
    
    def unregister_agent(self, agent_id: str) -> bool:
        """注销Agent"""
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = "inactive"
            return True
        return False
    
    def send_message(self, sender: str, receiver: str, content: Any, 
                     msg_type: MessageType = MessageType.REQUEST) -> str:
        """发送消息"""
        # 检查sender和receiver是否存在
        if sender not in self.agents:
            raise ValueError(f"Unknown sender: {sender}")
        if receiver not in self.agents:
            raise ValueError(f"Unknown receiver: {receiver}")
        
        msg = AgentMessage(
            msg_id=str(uuid.uuid4()),
            sender=sender,
            receiver=receiver,
            msg_type=msg_type,
            content=content
        )
        self.messages.append(msg)
        
        # 限制历史大小
        if len(self.messages) > self._history_size:
            self.messages = self.messages[-self._history_size:]
        
        # 加入接收者队列
        if receiver in self.message_queues:
            self.message_queues[receiver].append(msg)
        
        return msg.msg_id
    
    def get_messages(self, agent_id: str, unread_only: bool = False) -> List[AgentMessage]:
        """获取Agent的消息"""
        if agent_id not in self.message_queues:
            return []
        
        messages = self.message_queues[agent_id]
        
        if unread_only:
            # 只返回未读消息(简化处理)
            return [m for m in messages if m.receiver == agent_id]
        
        return messages
    
    def clear_messages(self, agent_id: str):
        """清空Agent的消息队列"""
        if agent_id in self.message_queues:
            self.message_queues[agent_id] = []
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """获取Agent状态"""
        return self.agents.get(agent_id)
    
    def broadcast(self, sender: str, content: Any) -> List[str]:
        """广播消息给所有活跃Agent"""
        msg_ids = []
        for agent_id in self.agents:
            if agent_id != sender and self.agents[agent_id].get("status") == "active":
                msg_id = self.send_message(sender, agent_id, content, MessageType.BROADCAST)
                msg_ids.append(msg_id)
        return msg_ids


class CIPEventBus:
    """CIP事件总线 - 来自X系统"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        self.event_history: List[Dict] = []
        self._max_history = 500
    
    def subscribe(self, event: str, callback: callable):
        """订阅事件"""
        if event not in self.subscribers:
            self.subscribers[event] = []
        if callback not in self.subscribers[event]:
            self.subscribers[event].append(callback)
    
    def unsubscribe(self, event: str, callback: callable) -> bool:
        """取消订阅"""
        if event in self.subscribers and callback in self.subscribers[event]:
            self.subscribers[event].remove(callback)
            return True
        return False
    
    def publish(self, event: str, data: Any):
        """发布事件"""
        # 记录历史
        self.event_history.append({
            'event': event,
            'data': data,
            'timestamp': time.time(),
        })
        
        # 限制历史大小
        if len(self.event_history) > self._max_history:
            self.event_history = self.event_history[-self._max_history:]
        
        # 通知订阅者
        for callback in self.subscribers.get(event, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Event callback error: {e}")
    
    def get_history(self, event: str = None, limit: int = 50) -> List[Dict]:
        """获取事件历史"""
        if event:
            return [h for h in self.event_history[-limit:] if h['event'] == event]
        return self.event_history[-limit:]
    
    def clear_history(self):
        """清空历史"""
        self.event_history = []


class KnowledgeBridge:
    """知识桥接 - 来自X系统#67
    
    在Agent之间转移知识/上下文
    """
    
    def __init__(self):
        self.bridges: Dict[str, str] = {}
        self.transfer_log: List[Dict] = []
        self._max_log = 200
    
    def register(self, from_agent: str, to_agent: str, knowledge: str):
        """注册知识桥接"""
        key = f"{from_agent}->{to_agent}"
        self.bridges[key] = knowledge
    
    def unregister(self, from_agent: str, to_agent: str) -> bool:
        """注销知识桥接"""
        key = f"{from_agent}->{to_agent}"
        if key in self.bridges:
            del self.bridges[key]
            return True
        return False
    
    def transfer(self, from_agent: str, to_agent: str) -> Optional[str]:
        """转移知识"""
        key = f"{from_agent}->{to_agent}"
        knowledge = self.bridges.get(key)
        
        # 记录转移
        if knowledge:
            self.transfer_log.append({
                'from': from_agent,
                'to': to_agent,
                'knowledge_size': len(knowledge),
                'timestamp': time.time(),
            })
            if len(self.transfer_log) > self._max_log:
                self.transfer_log = self.transfer_log[-self._max_log:]
        
        return knowledge
    
    def has_bridge(self, from_agent: str, to_agent: str) -> bool:
        """检查是否存在桥接"""
        key = f"{from_agent}->{to_agent}"
        return key in self.bridges
    
    def list_bridges(self, agent_id: str = None) -> List[Dict]:
        """列出桥接"""
        result = []
        for key, knowledge in self.bridges.items():
            from_a, to_a = key.split('->')
            if agent_id is None or from_a == agent_id or to_a == agent_id:
                result.append({
                    'from': from_a,
                    'to': to_a,
                    'knowledge_size': len(knowledge),
                })
        return result


class VectorClock:
    """向量时钟 - 来自X系统#64
    
    用于分布式系统中的因果顺序
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.vector: Dict[str, int] = {agent_id: 0}
    
    def increment(self):
        """递增当前Agent的时钟"""
        self.vector[self.agent_id] = self.vector.get(self.agent_id, 0) + 1
    
    def merge(self, other: Dict[str, int]):
        """合并另一个向量时钟"""
        for agent, clock in other.items():
            self.vector[agent] = max(self.vector.get(agent, 0), clock)
    
    def happens_before(self, other: Dict[str, int]) -> bool:
        """检查是否happens-before"""
        # self <= other 当且仅当对于所有agent, self[agent] <= other[agent]
        # 且至少一个严格小于
        all_less_or_equal = True
        some_less = False
        
        # 合并后比较
        merged = {**self.vector}
        for agent, clock in other.items():
            merged[agent] = max(merged.get(agent, 0), clock)
        
        for agent in set(self.vector.keys()) | set(other.keys()):
            self_val = self.vector.get(agent, 0)
            other_val = other.get(agent, 0)
            
            if self_val > other_val:
                return False
            if self_val < other_val:
                some_less = True
        
        return some_less
    
    def concurrent_with(self, other: Dict[str, int]) -> bool:
        """检查是否并发(既不happens-before也不之后)"""
        return not self.happens_before(other) and not self._happens_after(other)
    
    def _happens_after(self, other: Dict[str, int]) -> bool:
        """检查other是否happens-before self"""
        return self.happens_before(other)
    
    def get_clock(self) -> Dict[str, int]:
        """获取当前时钟快照"""
        return dict(self.vector)
    
    def set_clock(self, clock: Dict[str, int]):
        """设置时钟"""
        self.vector = dict(clock)


class CausalKG:
    """因果知识图谱 - 来自X系统#65
    
    表示因果关系的知识图谱
    """
    
    def __init__(self):
        self.edges: Dict[str, List[str]] = {}
        self.reverse_edges: Dict[str, List[str]] = {}
        self.edge_weights: Dict[str, Dict[str, float]] = {}
    
    def add_causality(self, cause: str, effect: str, weight: float = 1.0):
        """添加因果边"""
        if cause not in self.edges:
            self.edges[cause] = []
        if effect not in self.edges[cause]:
            self.edges[cause].append(effect)
        
        # 反向索引
        if effect not in self.reverse_edges:
            self.reverse_edges[effect] = []
        if cause not in self.reverse_edges[effect]:
            self.reverse_edges[effect].append(cause)
        
        # 权重
        if cause not in self.edge_weights:
            self.edge_weights[cause] = {}
        self.edge_weights[cause][effect] = weight
    
    def remove_causality(self, cause: str, effect: str) -> bool:
        """移除因果边"""
        if cause in self.edges and effect in self.edges[cause]:
            self.edges[cause].remove(effect)
            if effect in self.reverse_edges and cause in self.reverse_edges[effect]:
                self.reverse_edges[effect].remove(cause)
            return True
        return False
    
    def get_effects(self, cause: str) -> List[str]:
        """获取因的所有果"""
        return self.edges.get(cause, [])
    
    def get_causes(self, effect: str) -> List[str]:
        """获取果的所有因"""
        return self.reverse_edges.get(effect, [])
    
    def get_weight(self, cause: str, effect: str) -> float:
        """获取因果权重"""
        return self.edge_weights.get(cause, {}).get(effect, 0.0)
    
    def get_all_concepts(self) -> List[str]:
        """获取所有概念节点"""
        return list(set(self.edges.keys()) | set(self.reverse_edges.keys()))
    
    def get_causal_chain(self, start: str, max_depth: int = 3) -> List[List[str]]:
        """获取从start出发的所有因果链"""
        result = []
        
        def dfs(current: str, path: List[str], depth: int):
            if depth >= max_depth:
                result.append(path)
                return
            
            for effect in self.edges.get(current, []):
                dfs(effect, path + [effect], depth + 1)
        
        dfs(start, [start], 0)
        return result


# 工厂
def create_multi_agent_system() -> MultiAgentSystem:
    return MultiAgentSystem()

def create_event_bus() -> CIPEventBus:
    return CIPEventBus()

def create_causal_kg() -> CausalKG:
    return CausalKG()


# ===== 来自XYZ系统 =====
class BehaviorMirror:
    """K9: Mirror user behavior for preference inference.

    Uses both frequency counting and 2nd-order Markov chain modeling
    to capture not just what users do, but what they do NEXT given
    the last TWO actions (context-aware prediction).
    """

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._observations: list[dict] = []
        self._style_counters: dict[str, dict[str, int]] = {}

        # 1st-order Markov chain: state → next_state → count
        self._transitions: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._state_totals: dict[str, int] = defaultdict(int)

        # 2nd-order Markov chain: (prev, curr) → next → count
        self._transitions_2: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._state_totals_2: dict[tuple[str, str], int] = defaultdict(int)

        self._last_action: str = ""
        self._prev_action: str = ""  # For 2nd-order chain
        self._stats = {"observations": 0, "inferences": 0, "transitions": 0}

    def observe(self, action: str, category: str = "general",
                metadata: dict | None = None) -> dict:
        """Observe a user action.

        Args:
            action: What the user did (e.g., "approved concise summary")
            category: Action category (e.g., "communication", "decision")
            metadata: Additional context
        """
        self._stats["observations"] += 1
        entry = {
            "action": action,
            "category": category,
            "metadata": metadata or {},
        }
        self._observations.append(entry)

        # Update style counters
        if category not in self._style_counters:
            self._style_counters[category] = {}
        self._style_counters[category][action] = \
            self._style_counters[category].get(action, 0) + 1

        # Update 1st-order Markov chain
        if self._last_action:
            self._transitions[self._last_action][action] += 1
            self._state_totals[self._last_action] += 1
            self._stats["transitions"] += 1

        # Update 2nd-order Markov chain: (prev, last) → action
        if self._prev_action and self._last_action:
            key = (self._prev_action, self._last_action)
            self._transitions_2[key][action] += 1
            self._state_totals_2[key] += 1

        # Shift history
        self._prev_action = self._last_action
        self._last_action = action

        return entry

    def infer_style(self, category: str = "communication") -> dict:
        """Infer user style from observations.

        Returns the dominant action for each category.
        """
        self._stats["inferences"] += 1
        if category not in self._style_counters:
            return {"category": category, "dominant": None, "confidence": 0.0}

        counters = self._style_counters[category]
        if not counters:
            return {"category": category, "dominant": None, "confidence": 0.0}

        total = sum(counters.values())
        dominant = max(counters, key=counters.get)
        confidence = counters[dominant] / total if total > 0 else 0.0

        return {
            "category": category,
            "dominant": dominant,
            "confidence": confidence,
            "distribution": dict(counters),
        }

    def predict_next(self, current_action: str, prev_action: str = "",
                     top_k: int = 3) -> list[tuple[str, float]]:
        """Predict the most likely next action.

        Uses 2nd-order Markov chain if prev_action is provided and
        sufficient data exists, otherwise falls back to 1st-order.

        Returns list of (action, probability) sorted by probability.
        """
        # Try 2nd-order first (more context-aware)
        if prev_action:
            key = (prev_action, current_action)
            if key in self._transitions_2:
                total = self._state_totals_2.get(key, 0)
                if total > 0:
                    transitions = self._transitions_2[key]
                    probs = [(a, c / total) for a, c in transitions.items()]
                    probs.sort(key=lambda x: x[1], reverse=True)
                    return probs[:top_k]

        # Fallback to 1st-order
        if current_action not in self._transitions:
            return []

        total = self._state_totals.get(current_action, 0)
        if total == 0:
            return []

        transitions = self._transitions[current_action]
        probs = [(action, count / total) for action, count in transitions.items()]
        probs.sort(key=lambda x: x[1], reverse=True)
        return probs[:top_k]

    def get_transition_probability(self, from_action: str, to_action: str,
                                   prev_action: str = "") -> float:
        """Get P(to_action | from_action) or P(to_action | prev, from).

        Uses 2nd-order if prev_action provided and data exists.
        """
        # Try 2nd-order
        if prev_action:
            key = (prev_action, from_action)
            total = self._state_totals_2.get(key, 0)
            if total > 0:
                return self._transitions_2[key].get(to_action, 0) / total

        # Fallback to 1st-order
        total = self._state_totals.get(from_action, 0)
        if total == 0:
            return 0.0
        return self._transitions[from_action].get(to_action, 0) / total

    def detect_action_loops(self, min_length: int = 2,
                            min_repeats: int = 3) -> list[list[str]]:
        """Detect repeated action sequences using suffix array.

        O(n log n) via suffix array construction, vs O(n²) brute force.
        Finds subsequences that repeat ≥ min_repeats times.
        """
        if len(self._observations) < min_length * min_repeats:
            return []

        actions = [obs["action"] for obs in self._observations]
        return _detect_loops_suffix_array(actions, min_length, min_repeats)

    def get_preferred_style(self) -> dict[str, str]:
        """Get the dominant style for each category."""
        result = {}
        for category in self._style_counters:
            inference = self.infer_style(category)
            if inference["dominant"]:
                result[category] = inference["dominant"]
        return result

    def detect_repeated_questions(self, min_count: int = 3) -> list[str]:
        """Detect knowledge gaps — questions asked repeatedly."""
        question_counts: dict[str, int] = {}
        for obs in self._observations:
            if obs["category"] == "question":
                q = obs["action"]
                question_counts[q] = question_counts.get(q, 0) + 1

        return [q for q, c in question_counts.items() if c >= min_count]

    @property
    def observation_count(self) -> int:
        return len(self._observations)

    @property
    def stats(self) -> dict:
        return dict(self._stats)


def _detect_loops_suffix_array(actions: list[str],
                                min_length: int = 2,
                                min_repeats: int = 3) -> list[list[str]]:
    """Detect repeated subsequences using suffix array.

    Algorithm:
    1. Build suffix array by sorting all suffixes
    2. Scan adjacent suffixes in sorted order for common prefixes
    3. Common prefix length ≥ min_length → repeated subsequence
    4. Count repeats by grouping overlapping matches

    O(n log n) for sorting, O(n) for scanning.
    """
    n = len(actions)
    if n < min_length * min_repeats:
        return []

    # Build suffix array: indices sorted by their suffix
    suffixes = list(range(n))
    suffixes.sort(key=lambda i: actions[i:])

    # Find longest common prefix between adjacent sorted suffixes
    loops = []
    seen: set[tuple[str, ...]] = set()

    for i in range(len(suffixes) - 1):
        s1 = suffixes[i]
        s2 = suffixes[i + 1]

        # Compute LCP
        lcp = 0
        while (s1 + lcp < n and s2 + lcp < n
               and actions[s1 + lcp] == actions[s2 + lcp]):
            lcp += 1

        if lcp >= min_length:
            # Extract the repeated subsequence
            subseq = tuple(actions[s1:s1 + lcp])

            # Count total occurrences (not just adjacent pairs)
            if subseq not in seen:
                # Count by scanning for this subsequence
                count = 0
                for j in range(n - len(subseq) + 1):
                    if tuple(actions[j:j + len(subseq)]) == subseq:
                        count += 1

                if count >= min_repeats:
                    loops.append(list(subseq))
                    seen.add(subseq)

    return loops


