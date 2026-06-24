"""Consolidation记忆整合 - 基于Hindsight的自动学习机制

论文核心: 后台异步任务，定期将原始记忆整合为Mental Models

Consolidation流程:
1. 收集相关记忆片段
2. 识别模式和主题
3. 使用LLM生成高阶洞察
4. 更新实体摘要和信念
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import asyncio


class ConsolidationStrategy(Enum):
    """整合策略"""
    TEMPORAL = "temporal"         # 按时间窗口
    ENTITY_CENTRIC = "entity"     # 以实体为中心
    THEMATIC = "thematic"         # 按主题聚合
    HYBRID = "hybrid"             # 混合策略


class ConsolidationStatus(Enum):
    """整合状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ConsolidationTask:
    """整合任务"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy: ConsolidationStrategy = ConsolidationStrategy.HYBRID
    
    # 范围
    entity_id: Optional[str] = None
    time_window_hours: int = 24
    memory_limit: int = 50
    
    # 状态
    status: ConsolidationStatus = ConsolidationStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 结果
    summary: str = ""
    key_insights: List[str] = field(default_factory=list)
    updated_entities: List[str] = field(default_factory=list)
    new_beliefs: List[str] = field(default_factory=list)
    
    # 错误
    error_message: str = ""


@dataclass
class MemoryFragment:
    """记忆片段 - 待整合的原始记忆"""
    fragment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    network_type: str = ""  # world/experiences
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    importance: float = 0.5  # 0-1
    entity_ids: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class ConsolidationEngine:
    """Consolidation引擎 - 自动记忆整合
    
    基于Hindsight的核心机制：
    1. 定期扫描待整合的记忆
    2. 识别模式和主题
    3. 生成高阶洞察
    4. 更新记忆结构
    """
    
    def __init__(self):
        # 任务队列
        self.pending_tasks: List[ConsolidationTask] = []
        self.completed_tasks: List[ConsolidationTask] = []
        
        # 配置
        self.enabled = True
        self.interval_hours = 6
        self.last_run: Optional[datetime] = None
        
        # LLM回调（可选）
        self.llm_callback: Optional[Callable] = None
    
    def set_llm_callback(self, callback: Callable[[str], str]) -> None:
        """设置LLM回调用于生成洞察"""
        self.llm_callback = callback
    
    def create_task(self, strategy: ConsolidationStrategy = ConsolidationStrategy.HYBRID,
                   entity_id: Optional[str] = None,
                   time_window_hours: int = 24) -> ConsolidationTask:
        """创建整合任务"""
        task = ConsolidationTask(
            strategy=strategy,
            entity_id=entity_id,
            time_window_hours=time_window_hours
        )
        self.pending_tasks.append(task)
        return task
    
    async def execute_task(self, task: ConsolidationTask,
                          memory_store) -> ConsolidationTask:
        """执行整合任务
        
        Args:
            task: 整合任务
            memory_store: 外部记忆存储（四网络记忆）
        """
        task.status = ConsolidationStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            # 1. 收集记忆片段
            fragments = self._collect_fragments(task, memory_store)
            
            # 2. 分析模式和主题
            patterns = self._analyze_patterns(fragments)
            
            # 3. 生成洞察（使用LLM或模板）
            if self.llm_callback:
                insights = await self._generate_insights_llm(patterns, task)
            else:
                insights = self._generate_insights_template(patterns, task)
            
            task.key_insights = insights
            
            # 4. 生成摘要
            task.summary = self._generate_summary(fragments, insights)
            
            # 5. 更新实体摘要
            if task.entity_id:
                updated = await self._update_entity_summary(task, memory_store)
                task.updated_entities = updated
            
            # 6. 可能形成新信念
            new_beliefs = await self._form_beliefs(task, memory_store)
            task.new_beliefs = new_beliefs
            
            task.status = ConsolidationStatus.COMPLETED
            
        except Exception as e:
            task.status = ConsolidationStatus.FAILED
            task.error_message = str(e)
        
        task.completed_at = datetime.now()
        self.completed_tasks.append(task)
        
        return task
    
    def _collect_fragments(self, task: ConsolidationTask, 
                          memory_store) -> List[MemoryFragment]:
        """收集待整合的记忆片段"""
        fragments = []
        
        # 按时间窗口收集
        cutoff = datetime.now() - timedelta(hours=task.time_window_hours)
        
        # 从四网络记忆获取
        if hasattr(memory_store, 'world_facts'):
            for fact in memory_store.world_facts.values():
                if fact.created_at >= cutoff:
                    fragments.append(MemoryFragment(
                        content=fact.content,
                        network_type="world",
                        created_at=fact.created_at,
                        importance=fact.confidence,
                        entity_ids=fact.entity_ids,
                        tags=fact.tags
                    ))
        
        if hasattr(memory_store, 'experiences'):
            for fact in memory_store.experiences.values():
                if fact.created_at >= cutoff:
                    fragments.append(MemoryFragment(
                        content=fact.content,
                        network_type="experiences",
                        created_at=fact.created_at,
                        importance=fact.confidence,
                        entity_ids=fact.entity_ids,
                        tags=fact.tags
                    ))
        
        # 限制数量
        fragments.sort(key=lambda x: x.importance, reverse=True)
        return fragments[:task.memory_limit]
    
    def _analyze_patterns(self, fragments: List[MemoryFragment]) -> Dict[str, Any]:
        """分析记忆片段的模式"""
        if not fragments:
            return {"themes": [], "entities": [], "sentiment": "neutral"}
        
        # 统计实体
        entity_counts: Dict[str, int] = {}
        for f in fragments:
            for e in f.entity_ids:
                entity_counts[e] = entity_counts.get(e, 0) + 1
        
        # 统计标签
        tag_counts: Dict[str, int] = {}
        for f in fragments:
            for t in f.tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1
        
        # 识别主题（简单关键词聚类）
        themes = list(tag_counts.keys())[:5]
        
        return {
            "fragment_count": len(fragments),
            "themes": themes,
            "top_entities": sorted(entity_counts.items(), key=lambda x: -x[1])[:5],
            "time_span_hours": (
                (max(f.created_at for f in fragments) - min(f.created_at for f in fragments)).total_seconds() / 3600
                if len(fragments) > 1 else 0
            )
        }
    
    def _generate_insights_template(self, patterns: Dict[str, Any],
                                    task: ConsolidationTask) -> List[str]:
        """使用模板生成洞察"""
        insights = []
        
        # 基于主题的洞察
        if patterns.get("themes"):
            insights.append(f"涉及主题: {', '.join(patterns['themes'][:3])}")
        
        # 基于实体的洞察
        top_entities = patterns.get("top_entities", [])
        if top_entities:
            entities_str = ", ".join([e[0] for e in top_entities[:3]])
            insights.append(f"主要涉及实体: {entities_str}")
        
        # 基于数量的洞察
        count = patterns.get("fragment_count", 0)
        if count > 20:
            insights.append(f"高交互密度: {count}条记忆")
        elif count > 10:
            insights.append(f"中等交互: {count}条记忆")
        
        return insights
    
    async def _generate_insights_llm(self, patterns: Dict[str, Any],
                                     task: ConsolidationTask) -> List[str]:
        """使用LLM生成洞察"""
        if not self.llm_callback:
            return self._generate_insights_template(patterns, task)
        
        # 构造提示
        prompt = f"""分析以下记忆片段的模式，生成3条关键洞察：

主题: {patterns.get('themes', [])}
实体: {patterns.get('top_entities', [])}
记忆数量: {patterns.get('fragment_count', 0)}

请输出3条洞察，每条不超过20字。
"""
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.llm_callback, prompt
            )
            # 简单解析
            insights = [line.strip() for line in result.split("\n") if line.strip()]
            return insights[:3]
        except Exception:
            return self._generate_insights_template(patterns, task)
    
    def _generate_summary(self, fragments: List[MemoryFragment],
                         insights: List[str]) -> str:
        """生成摘要"""
        if not fragments:
            return "无记忆可整合"
        
        # 简单摘要
        count = len(fragments)
        time_range = f"{fragments[0].created_at.strftime('%m-%d %H:%M')}-{fragments[-1].created_at.strftime('%m-%d %H:%M')}"
        
        summary = f"整合了{count}条记忆 ({time_range})"
        
        if insights:
            summary += f"\n关键洞察: {'; '.join(insights[:2])}"
        
        return summary
    
    async def _update_entity_summary(self, task: ConsolidationTask,
                                     memory_store) -> List[str]:
        """更新实体摘要"""
        if not task.entity_id or not hasattr(memory_store, 'summaries'):
            return []
        
        updated = []
        
        # 获取相关记忆
        fragments = self._collect_fragments(task, memory_store)
        entity_fragments = [f for f in fragments if task.entity_id in f.entity_ids]
        
        if entity_fragments:
            # 更新实体摘要
            facts = [f.content for f in entity_fragments[:10]]
            memory_store.update_entity_summary(
                task.entity_id, 
                task.entity_id,  # name使用entity_id作为默认值
                facts
            )
            updated.append(task.entity_id)
        
        return updated
    
    async def _form_beliefs(self, task: ConsolidationTask,
                          memory_store) -> List[str]:
        """形成新信念"""
        if not hasattr(memory_store, 'beliefs'):
            return []
        
        new_beliefs = []
        
        # 基于洞察生成信念建议
        for insight in task.key_insights:
            # 简单规则：洞察可以转化为信念
            if len(insight) > 5:
                # 检查是否已存在类似信念
                existing = memory_store.get_beliefs(min_strength=0.1)
                similar = any(insight[:20] in b.content for b in existing)
                
                if not similar:
                    belief = memory_store.form_belief(
                        content=insight,
                        source_fact_ids=[task.task_id]
                    )
                    new_beliefs.append(belief.belief_id)
        
        return new_beliefs
    
    def get_task_status(self) -> Dict[str, Any]:
        """获取整合状态"""
        return {
            "enabled": self.enabled,
            "pending_count": len(self.pending_tasks),
            "completed_count": len(self.completed_tasks),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "recent_tasks": [
                {
                    "id": t.task_id,
                    "status": t.status.value,
                    "completed": t.completed_at.isoformat() if t.completed_at else None
                }
                for t in self.completed_tasks[-5:]
            ]
        }
    
    async def run_scheduled(self, memory_store) -> List[ConsolidationTask]:
        """运行计划的整合任务"""
        self.last_run = datetime.now()
        
        # 创建默认任务
        task = self.create_task(
            strategy=ConsolidationStrategy.HYBRID,
            time_window_hours=self.interval_hours
        )
        
        # 执行
        result = await self.execute_task(task, memory_store)
        
        return [result]


def create_consolidation_engine() -> ConsolidationEngine:
    """工厂函数：创建Consolidation引擎"""
    return ConsolidationEngine()