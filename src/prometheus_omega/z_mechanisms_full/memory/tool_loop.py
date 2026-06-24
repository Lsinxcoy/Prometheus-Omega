"""工具调用推理循环 - 基于MRAgent的LLM工具调用推理

论文核心概念：Memory is Reconstructed, Not Retrieved
- 不是一次性RAG，而是LLM通过多轮工具调用逐步重建记忆
- 5个核心工具：keyword/topic/personal/temporal/context

本模块实现：
- ToolCallingReasoner: LLM通过工具调用逐步推理
- Tool: 工具定义
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import json


class ToolResultStatus(Enum):
    """工具执行结果状态"""
    SUCCESS = "success"
    PARTIAL = "partial"
    EMPTY = "empty"
    ERROR = "error"


@dataclass
class Tool:
    """工具定义 - OpenAI tool calling格式"""
    name: str
    description: str
    parameters: dict = field(default_factory=dict)
    
    def to_openai_format(self) -> dict:
        """转换为OpenAI工具格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Tool':
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            parameters=data.get("parameters", {})
        )


@dataclass
class ToolResult:
    """工具执行结果"""
    tool_name: str
    status: ToolResultStatus
    data: Any
    message: str = ""
    
    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "status": self.status.value,
            "data": self.data,
            "message": self.message
        }


# 预定义工具：基于MRAgent的5个核心工具
DEFAULT_TOOLS = [
    Tool(
        name="edges_by_tag",
        description="Follow memory graph edges filtered by a {tag, key} pair to retrieve related events under a topic",
        parameters={
            "type": "object",
            "properties": {
                "tag": {"type": "string", "description": "Tag aligned with keyword"},
                "key": {"type": "string", "description": "Key (person/entity/topic)"},
                "note": {"type": "string", "description": "Decision note for next round"}
            },
            "required": ["tag", "key"]
        }
    ),
    Tool(
        name="query_conversation_time",
        description="Return WHEN the conversation containing the event occurred",
        parameters={
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Event ID (e.g., E5)"}
            },
            "required": ["event_id"]
        }
    ),
    Tool(
        name="query_event_keywords",
        description="Return salient keywords for an event",
        parameters={
            "type": "object", 
            "properties": {
                "event_id": {"type": "string", "description": "Event ID"}
            },
            "required": ["event_id"]
        }
    ),
    Tool(
        name="query_event_context",
        description="Return surrounding conversational context of an event",
        parameters={
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Event ID"}
            },
            "required": ["event_id"]
        }
    ),
    Tool(
        name="query_personal_information",
        description="Query personal information about a person",
        parameters={
            "type": "object",
            "properties": {
                "person": {"type": "string", "description": "Person name"},
                "tag": {"type": "string", "description": "Information tag"}
            },
            "required": ["person"]
        }
    )
]


class ToolCallingReasoner:
    """LLM通过工具调用逐步推理 - 不是一次性RAG
    
    核心流程：
    1. LLM决定使用哪个工具
    2. 执行工具获取结果
    3. 将结果注入上下文
    4. 检查是否足够回答问题
    5. 重复直到得出答案或达到最大轮次
    """
    
    def __init__(self, memory_graph, tools: List[Tool] = None,
                 max_turns: int = 5):
        self.memory = memory_graph
        self.tools = tools or DEFAULT_TOOLS
        self.max_turns = max_turns
        
        # 工具名到函数的映射 - 由外部注入
        self._tool_handlers: Dict[str, Callable] = {}
        
        # 注册默认处理器
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """注册默认工具处理器"""
        self.register_handler("edges_by_tag", self._handle_edges_by_tag)
        self.register_handler("query_conversation_time", self._handle_conversation_time)
        self.register_handler("query_event_keywords", self._handle_event_keywords)
        self.register_handler("query_event_context", self._handle_event_context)
        self.register_handler("query_personal_information", self._handle_personal_info)
    
    def register_handler(self, tool_name: str, handler: Callable) -> None:
        """注册工具处理器"""
        self._tool_handlers[tool_name] = handler
    
    def execute_tool(self, tool_name: str, args: dict) -> ToolResult:
        """执行工具"""
        handler = self._tool_handlers.get(tool_name)
        
        if not handler:
            return ToolResult(
                tool_name=tool_name,
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Unknown tool: {tool_name}"
            )
        
        try:
            result = handler(args)
            return ToolResult(
                tool_name=tool_name,
                status=ToolResultStatus.SUCCESS,
                data=result,
                message="OK"
            )
        except Exception as e:
            return ToolResult(
                tool_name=tool_name,
                status=ToolResultStatus.ERROR,
                data=None,
                message=str(e)
            )
    
    # 默认处理器实现
    def _handle_edges_by_tag(self, args: dict) -> dict:
        """edges_by_tag处理器"""
        key = args.get("key", "")
        tag = args.get("tag", "")
        
        event_ids = self.memory.traverse_by_tag(key, tag)
        
        if not event_ids:
            return {"events": [], "message": "No events found"}
        
        # 获取事件文本
        events = []
        for eid in event_ids[:10]:  # 限制数量
            event = self.memory.episode_events.get(eid)
            if event:
                events.append({
                    "event_id": eid,
                    "text": event.text,
                    "timestamp": event.timestamp
                })
        
        return {"events": events, "count": len(events)}
    
    def _handle_conversation_time(self, args: dict) -> dict:
        """query_conversation_time处理器"""
        event_id = args.get("event_id", "")
        
        # 查找事件所属的对话
        for conv_id, events in self.memory.temporal_index.items():
            if event_id in events:
                return {"conversation_id": conv_id, "event_id": event_id}
        
        return {"message": "Event not found in any conversation"}
    
    def _handle_event_keywords(self, args: dict) -> dict:
        """query_event_keywords处理器"""
        event_id = args.get("event_id", "")
        event = self.memory.episode_events.get(event_id)
        
        if not event:
            return {"keywords": [], "message": "Event not found"}
        
        # 简单实现：从文本提取关键词（实际应该用NLP）
        words = event.text.split()
        keywords = [{"key": w, "tags": ["auto"]} for w in words[:5]]
        
        return {"keywords": keywords}
    
    def _handle_event_context(self, args: dict) -> dict:
        """query_event_context处理器"""
        event_id = args.get("event_id", "")
        
        # 找到事件所属的对话
        for conv_id, events in self.memory.temporal_index.items():
            if event_id in events:
                idx = events.index(event_id)
                context_events = []
                
                # 获取前后各2个事件
                start = max(0, idx - 2)
                end = min(len(events), idx + 3)
                
                for eid in events[start:end]:
                    event = self.memory.episode_events.get(eid)
                    if event:
                        context_events.append({
                            "event_id": eid,
                            "text": event.text,
                            "is_target": eid == event_id
                        })
                
                return {"context": context_events, "conversation": conv_id}
        
        return {"context": [], "message": "Event not found"}
    
    def _handle_personal_info(self, args: dict) -> dict:
        """query_personal_information处理器"""
        person = args.get("person", "")
        tag = args.get("tag", None)
        
        events = self.memory.traverse_by_person(person)
        
        if not events:
            return {"information": [], "message": f"No info about {person}"}
        
        # 按tag过滤
        if tag:
            events = [e for e in events if e.tag == tag]
        
        info = [{"text": e.text, "tag": e.tag, "origin": e.origin} for e in events[:10]]
        
        return {"information": info, "count": len(info)}
    
    def reason(self, question: str, llm_decide_fn: Callable) -> dict:
        """推理循环
        
        Args:
            question: 问题
            llm_decide_fn: LLM决策函数，签名为 (context, tools) -> {tool_name, args, is_answer, answer}
            
        Returns:
            {answer, evidence, turns, tool_calls}
        """
        context = {
            "question": question,
            "evidence": [],
            "tool_calls": []
        }
        
        for turn in range(self.max_turns):
            # LLM决定下一步
            decision = llm_decide_fn(context, self.tools)
            
            # 检查是否直接回答
            if decision.get("is_answer"):
                return {
                    "answer": decision.get("answer", ""),
                    "evidence": context["evidence"],
                    "turns": turn + 1,
                    "tool_calls": context["tool_calls"]
                }
            
            # 执行工具调用
            tool_name = decision.get("tool_name")
            tool_args = decision.get("args", {})
            
            if not tool_name:
                # 无法决定，结束
                break
            
            result = self.execute_tool(tool_name, tool_args)
            
            # 记录工具调用
            context["tool_calls"].append({
                "turn": turn,
                "tool": tool_name,
                "args": tool_args,
                "result": result.to_dict()
            })
            
            # 添加到证据
            context["evidence"].append(result.to_dict())
        
        # 达到最大轮次
        return {
            "answer": "max_turns_exceeded",
            "evidence": context["evidence"],
            "turns": self.max_turns,
            "tool_calls": context["tool_calls"]
        }
    
    def get_tools_for_llm(self) -> List[dict]:
        """获取LLM可用的工具格式"""
        return [tool.to_openai_format() for tool in self.tools]