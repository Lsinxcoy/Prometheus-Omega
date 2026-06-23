"""图结构记忆 - 基于MRAgent的图记忆架构

论文核心概念：Memory is Reconstructed, Not Retrieved
- 图结构 episodic memory
- 四层节点：KeyNode, Topic, PersonalEvent, EpisodeEvent
- LLM工具调用推理循环逐步重建记忆

本模块实现：
- GraphMemory: 图结构记忆存储
- GraphTraversal: 图遍历工具
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from collections import defaultdict
import time
import json
from pathlib import Path


@dataclass
class KeyNode:
    """关键词节点 - 连接事件"""
    key_id: str
    text: str = ""
    tag_list: List[str] = field(default_factory=list)
    tag_dict: Dict[str, List[str]] = field(default_factory=dict)
    
    def add_tag(self, tag: str, event_id: str) -> None:
        """添加tag连接"""
        if tag not in self.tag_list:
            self.tag_list.append(tag)
        if tag not in self.tag_dict:
            self.tag_dict[tag] = []
        if event_id not in self.tag_dict[tag]:
            self.tag_dict[tag].append(event_id)
    
    def get_events_by_tag(self, tag: str) -> List[str]:
        """按tag获取事件ID列表"""
        return self.tag_dict.get(tag, [])


@dataclass
class Topic:
    """主题节点 - 聚合事件"""
    topic_id: str
    text: str
    event_list: List[str] = field(default_factory=list)


@dataclass
class PersonalEvent:
    """个人事件 - 跨会话追踪"""
    person: str
    personal_id: str
    text: str
    tag: str
    origin: str  # 来源对话ID
    timestamp: float = field(default_factory=time.time)


@dataclass 
class EpisodeEvent:
    """对话事件 - 原始对话片段"""
    event_id: str
    text: str
    timestamp: float = field(default_factory=time.time)
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "text": self.text,
            "timestamp": self.timestamp,
            "embedding": self.embedding,
            "metadata": self.metadata
        }


class GraphMemory:
    """图结构记忆 - 四层节点架构
    
    基于MRAgent的图记忆设计：
    - KeyNode: 关键词节点
    - Topic: 主题节点  
    - PersonalEvent: 个人事件
    - EpisodeEvent: 对话事件
    
    边关系：
    - Key → Topic (通过tag连接)
    - Topic → EpisodeEvent (事件聚类)
    - Personal → EpisodeEvent (人-事件关系)
    """
    
    def __init__(self):
        # 四层节点
        self.key_nodes: Dict[str, KeyNode] = {}
        self.topics: Dict[str, Topic] = {}
        self.personal_events: Dict[str, PersonalEvent] = {}
        self.episode_events: Dict[str, EpisodeEvent] = {}
        
        # 人-事件索引
        self.person_events: Dict[str, List[str]] = defaultdict(list)
        
        # 时间索引
        self.temporal_index: Dict[str, List[str]] = defaultdict(list)
    
    def add_episode(self, text: str, metadata: dict = None) -> str:
        """添加对话事件"""
        event_id = f"E{len(self.episode_events)}"
        episode = EpisodeEvent(
            event_id=event_id,
            text=text,
            metadata=metadata or {}
        )
        self.episode_events[event_id] = episode
        
        # 时间索引
        conversation_id = metadata.get("conversation_id", "default") if metadata else "default"
        self.temporal_index[conversation_id].append(event_id)
        
        return event_id
    
    def add_key_node(self, key: str, text: str = "") -> KeyNode:
        """添加关键词节点"""
        if key not in self.key_nodes:
            self.key_nodes[key] = KeyNode(key_id=key, text=text or key)
        return self.key_nodes[key]
    
    def link_key_to_episode(self, key: str, event_id: str, tag: str) -> None:
        """建立Key → Episode的边"""
        key_node = self.add_key_node(key)
        key_node.add_tag(tag, event_id)
    
    def add_topic(self, topic_id: str, text: str) -> Topic:
        """添加主题节点"""
        if topic_id not in self.topics:
            self.topics[topic_id] = Topic(topic_id=topic_id, text=text)
        return self.topics[topic_id]
    
    def add_personal_event(self, person: str, text: str, 
                          tag: str, origin: str) -> str:
        """添加个人事件"""
        event_id = f"P{len(self.personal_events)}"
        event = PersonalEvent(
            person=person,
            personal_id=event_id,
            text=text,
            tag=tag,
            origin=origin
        )
        self.personal_events[event_id] = event
        self.person_events[person].append(event_id)
        return event_id
    
    def traverse_by_tag(self, key: str, tag: str) -> List[str]:
        """按tag遍历图 - 获取相关事件"""
        key_node = self.key_nodes.get(key)
        if not key_node:
            return []
        return key_node.get_events_by_tag(tag)
    
    def traverse_by_person(self, person: str) -> List[PersonalEvent]:
        """按人名遍历 - 获取个人事件"""
        event_ids = self.person_events.get(person, [])
        return [self.personal_events[eid] for eid in event_ids if eid in self.personal_events]
    
    def traverse_temporal(self, conversation_id: str) -> List[EpisodeEvent]:
        """时间遍历 - 获取对话中的所有事件"""
        event_ids = self.temporal_index.get(conversation_id, [])
        return [self.episode_events[eid] for eid in event_ids if eid in self.episode_events]
    
    def search_by_embedding(self, query_emb: List[float], 
                           k: int = 5) -> List[tuple[str, float]]:
        """Embedding相似度搜索"""
        if not query_emb:
            return []
        
        # 计算余弦相似度
        def cosine_sim(a, b):
            dot = sum(x*y for x,y in zip(a,b))
            norm_a = sum(x*x for x in a) ** 0.5
            norm_b = sum(x*x for x in b) ** 0.5
            return dot / (norm_a * norm_b + 1e-8)
        
        scores = []
        for eid, event in self.episode_events.items():
            if event.embedding:
                sim = cosine_sim(query_emb, event.embedding)
                scores.append((eid, sim))
        
        # 返回top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]
    
    def get_statistics(self) -> dict:
        """获取记忆统计"""
        return {
            "key_nodes": len(self.key_nodes),
            "topics": len(self.topics),
            "personal_events": len(self.personal_events),
            "episode_events": len(self.episode_events),
            "conversations": len(self.temporal_index)
        }
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "key_nodes": {k: {"key_id": v.key_id, "text": v.text, "tags": v.tag_list} 
                         for k, v in self.key_nodes.items()},
            "topics": {k: {"topic_id": v.topic_id, "text": v.text} 
                      for k, v in self.topics.items()},
            "episode_events": {k: v.to_dict() 
                              for k, v in self.episode_events.items()},
            "personal_events": {k: {"person": v.person, "text": v.text, "tag": v.tag}
                               for k, v in self.personal_events.items()}
        }
    
    def save(self, path: str) -> None:
        """保存到文件"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: str) -> 'GraphMemory':
        """从文件加载"""
        with open(path) as f:
            data = json.load(f)
        
        graph = cls()
        
        # 恢复节点
        for k, v in data.get("key_nodes", {}).items():
            graph.key_nodes[k] = KeyNode(k, v.get("text", ""), v.get("tags", []))
        
        for k, v in data.get("topics", {}).items():
            graph.topics[k] = Topic(k, v.get("text", ""))
        
        for k, v in data.get("episode_events", {}).items():
            graph.episode_events[k] = EpisodeEvent(
                event_id=v["event_id"],
                text=v["text"],
                timestamp=v.get("timestamp", 0),
                embedding=v.get("embedding"),
                metadata=v.get("metadata", {})
            )
        
        for k, v in data.get("personal_events", {}).items():
            pe = PersonalEvent(
                person=v["person"],
                personal_id=k,
                text=v["text"],
                tag=v.get("tag", ""),
                origin=v.get("origin", "")
            )
            graph.personal_events[k] = pe
            graph.person_events[v["person"]].append(k)
        
        return graph