"""DAG执行器 - 基于2604.11378论文的Structured Graph Harness

论文核心概念：
- Agent Loop三弱点：隐式依赖、无界恢复、可变历史
- 调度理论视角：Agent Loop = 单就绪单元调度器
- SGH提议：
  - 执行计划在版本内不可变
  - 规划/执行/恢复分离三层
  - 恢复遵循严格升级协议

本模块实现：
- DAGExecutor: 将Agent Loop转换为显式DAG执行
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import time
import uuid


class NodeType(Enum):
    """节点类型 - 三层分离"""
    PLAN = "plan"      # 规划节点
    EXECUTE = "execute" # 执行节点
    RECOVER = "recover" # 恢复节点


@dataclass
class DAGNode:
    """DAG节点"""
    node_id: str
    node_type: NodeType
    action: Callable
    level: int = 0  # 用于恢复升级���议
    metadata: dict = field(default_factory=dict)
    state: str = "pending"
    result: Any = None
    error: str = ""
    
    def can_recover_from(self, failed_node: 'DAGNode') -> bool:
        """恢复遵循严格升级协议 - 高level可恢复低level"""
        if self.node_type != NodeType.RECOVER:
            return False
        return self.level > failed_node.level


class DAGExecutor:
    """DAG执行器 - 显式DAG执行替代Agent Loop
    
    核心改进：
    1. 执行计划在版本内不可变
    2. 规划/执行/恢复分离三层
    3. 恢复遵循严格升级协议
    """
    
    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self.nodes: Dict[str, DAGNode] = {}
        self.edges: List[tuple[str, str]] = []
        self._execution_order: List[str] = []
        self._execution_id = str(uuid.uuid4())[:8]
    
    def add_node(self, node_id: str, node_type: NodeType, 
                 action: Callable, level: int = 0,
                 metadata: dict = None) -> None:
        """添加节点"""
        self.nodes[node_id] = DAGNode(
            node_id=node_id,
            node_type=node_type,
            action=action,
            level=level,
            metadata=metadata or {}
        )
    
    def add_edge(self, from_id: str, to_id: str) -> None:
        """添加边 - 执行依赖"""
        if from_id in self.nodes and to_id in self.nodes:
            self.edges.append((from_id, to_id))
    
    def _topological_sort(self) -> List[str]:
        """拓扑排序 - 确定执行顺序"""
        # 计算入度
        in_degree = {node_id: 0 for node_id in self.nodes}
        for from_id, to_id in self.edges:
            in_degree[to_id] += 1
        
        # 从入度为0的节点开始（只选PLAN类型）
        queue = [n for n in self.nodes if in_degree[n] == 0 and 
                 self.nodes[n].node_type == NodeType.PLAN]
        result = []
        
        while queue:
            # 按节点类型优先级：PLAN > EXECUTE > RECOVER
            queue.sort(key=lambda n: self.nodes[n].node_type.value)
            node_id = queue.pop(0)
            result.append(node_id)
            
            # 更新邻居
            for from_id, to_id in self.edges:
                if from_id == node_id:
                    in_degree[to_id] -= 1
                    if in_degree[to_id] == 0:
                        queue.append(to_id)
        
        return result
    
    def execute(self, initial_context: dict) -> dict:
        """DAG执行 - 三层严格顺序"""
        self._execution_order = self._topological_sort()
        
        # 分离三层节点
        plan_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.PLAN]
        execute_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.EXECUTE]
        recover_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.RECOVER]
        
        # 严格顺序：PLAN → EXECUTE → RECOVER
        context = dict(initial_context)
        context["_execution"] = {
            "execution_id": self._execution_id,
            "version": self.version,
            "steps": []
        }
        
        results = {}
        failed_node = None
        
        # Phase 1: PLAN
        for node in sorted(plan_nodes, key=lambda n: n.node_id):
            context = self._execute_node(node, context)
            results[node.node_id] = node.result
            
            if node.state == "failed":
                failed_node = node
                break
        
        # Phase 2: EXECUTE
        if not failed_node:
            for node in sorted(execute_nodes, key=lambda n: n.node_id):
                context = self._execute_node(node, context)
                results[node.node_id] = node.result
                
                if node.state == "failed":
                    failed_node = node
                    break
        
        # Phase 3: RECOVER (仅当有失败)
        if failed_node:
            # 按level排序，选择最小满足条件的
            eligible_recover = [
                n for n in recover_nodes 
                if n.can_recover_from(failed_node)
            ]
            eligible_recover.sort(key=lambda n: n.level)
            
            for node in eligible_recover:
                # 传递失败信息
                context["_failure"] = {
                    "failed_node": failed_node.node_id,
                    "error": failed_node.error
                }
                context = self._execute_node(node, context)
                results[node.node_id] = node.result
        
        return {
            "context": context,
            "results": results,
            "execution_order": self._execution_order,
            "failed": failed_node.node_id if failed_node else None,
            "execution_id": self._execution_id
        }
    
    def _execute_node(self, node: DAGNode, context: dict) -> dict:
        """执行单个节点"""
        node.state = "running"
        node.result = None
        node.error = ""
        
        try:
            # 执行动作
            result = node.action(context)
            node.result = result
            node.state = "completed"
            
            # 更新上下文
            context[node.node_id] = result
            context["_execution"]["steps"].append({
                "node_id": node.node_id,
                "type": node.node_type.value,
                "state": "completed"
            })
            
        except Exception as e:
            node.state = "failed"
            node.error = str(e)
            context["_execution"]["steps"].append({
                "node_id": node.node_id,
                "type": node.node_type.value,
                "state": "failed",
                "error": str(e)
            })
        
        return context
    
    def get_execution_plan(self) -> dict:
        """获取执行计划"""
        return {
            "version": self.version,
            "nodes": [
                {
                    "id": n.node_id,
                    "type": n.node_type.value,
                    "level": n.level
                }
                for n in self.nodes.values()
            ],
            "edges": [{"from": f, "to": t} for f, t in self.edges],
            "execution_order": self._execution_order
        }
    
    def can_execute(self) -> tuple[bool, str]:
        """检查是否可以执行"""
        # 检查是否有PLAN节点
        plan_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.PLAN]
        if not plan_nodes:
            return False, "no_plan_nodes"
        
        # 检查是否有EXECUTE节点
        exec_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.EXECUTE]
        if not exec_nodes:
            return False, "no_execute_nodes"
        
        # 检查是否有循环依赖
        try:
            self._topological_sort()
        except Exception as e:
            return False, f"cycle_detected: {e}"
        
        return True, "ok"


def create_planning_execution_dag(plan_fn: Callable, execute_fn: Callable,
                                   recovery_fns: Dict[int, Callable] = None) -> DAGExecutor:
    """创建标准的三层DAG"""
    
    dag = DAGExecutor(version="1.0.0")
    
    # PLAN节点
    dag.add_node("plan", NodeType.PLAN, plan_fn, level=0)
    
    # EXECUTE节点
    dag.add_node("execute", NodeType.EXECUTE, execute_fn, level=0)
    
    # RECOVER节点（可选）
    if recovery_fns:
        for level, fn in recovery_fns.items():
            dag.add_node(f"recover_level_{level}", NodeType.RECOVER, fn, level=level)
    
    # 边
    dag.add_edge("plan", "execute")
    
    # 添加恢复边
    if recovery_fns:
        for level in recovery_fns:
            dag.add_edge("execute", f"recover_level_{level}")
    
    return dag


class ParallelDAGExecutor(DAGExecutor):
    """并行DAG执行器 - 支持并行执行独立节点"""
    
    def __init__(self, version: str = "1.0.0", max_parallel: int = 4):
        super().__init__(version)
        self.max_parallel = max_parallel
        self._parallel_groups: List[List[str]] = []
    
    def _compute_parallel_groups(self) -> List[List[str]]:
        """计算可并行执行的节点组"""
        # 简化：按层级分组
        in_degree = {node_id: 0 for node_id in self.nodes}
        for from_id, to_id in self.edges:
            in_degree[to_id] += 1
        
        groups = []
        remaining = set(self.nodes.keys())
        
        while remaining:
            # 找出入度为0的节点
            ready = [n for n in remaining if in_degree[n] == 0]
            if not ready:
                break
            
            groups.append(ready)
            
            # 移除已处理的节点
            for node_id in ready:
                remaining.remove(node_id)
                for from_id, to_id in self.edges:
                    if from_id == node_id:
                        in_degree[to_id] -= 1
        
        return groups
    
    def execute_parallel(self, initial_context: dict) -> dict:
        """并行执行"""
        self._parallel_groups = self._compute_parallel_groups()
        
        context = dict(initial_context)
        context["_execution"] = {
            "execution_id": self._execution_id,
            "version": self.version,
            "steps": [],
            "parallel": True
        }
        
        results = {}
        
        for group in self._parallel_groups:
            # 并行执行组内节点
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(group)) as executor:
                futures = {}
                for node_id in group:
                    node = self.nodes[node_id]
                    future = executor.submit(node.action, context)
                    futures[future] = node_id
                
                for future in concurrent.futures.as_completed(futures):
                    node_id = futures[future]
                    node = self.nodes[node_id]
                    try:
                        node.result = future.result()
                        node.state = "completed"
                    except Exception as e:
                        node.state = "failed"
                        node.error = str(e)
                    
                    results[node_id] = node.result
                    context[node_id] = node.result
        
        return {
            "context": context,
            "results": results,
            "parallel_groups": self._parallel_groups,
            "execution_id": self._execution_id
        }


class RetryableDAGExecutor(DAGExecutor):
    """可重试的DAG执行器"""
    
    def __init__(self, version: str = "1.0.0", max_retries: int = 3):
        super().__init__(version)
        self.max_retries = max_retries
        self._retry_counts: Dict[str, int] = {}
    
    def execute_with_retry(self, initial_context: dict) -> dict:
        """执行并重试失败的节点"""
        self._retry_counts = {node_id: 0 for node_id in self.nodes}
        
        for attempt in range(self.max_retries):
            result = self.execute(initial_context)
            
            # 检查是否有失败
            if not result["failed"]:
                result["attempts"] = attempt + 1
                return result
            
            # 重试失败的节点
            failed_id = result["failed"]
            self._retry_counts[failed_id] += 1
            
            # 重置节点状态
            self.nodes[failed_id].state = "pending"
            self.nodes[failed_id].error = ""
        
        result["attempts"] = self.max_retries
        result["final_failure"] = True
        return result
    
    def get_retry_stats(self) -> dict:
        """获取重试统计"""
        return dict(self._retry_counts)


class MonitoredDAGExecutor(DAGExecutor):
    """可监控的DAG执行器 - 带指标收集"""
    
    def __init__(self, version: str = "1.0.0"):
        super().__init__(version)
        self._metrics = {
            "node_executions": {},
            "total_duration": 0.0,
            "failed_count": 0,
            "success_count": 0
        }
    
    def _execute_node(self, node: DAGNode, context: dict) -> dict:
        """执行节点并收集指标"""
        start_time = time.time()
        
        result = super()._execute_node(node, context)
        
        duration = time.time() - start_time
        
        # 更新指标
        if node.node_id not in self._metrics["node_executions"]:
            self._metrics["node_executions"][node.node_id] = {
                "count": 0,
                "total_duration": 0.0,
                "failures": 0
            }
        
        m = self._metrics["node_executions"][node.node_id]
        m["count"] += 1
        m["total_duration"] += duration
        
        if node.state == "failed":
            m["failures"] += 1
            self._metrics["failed_count"] += 1
        else:
            self._metrics["success_count"] += 1
        
        self._metrics["total_duration"] += duration
        
        return result
    
    def get_metrics(self) -> dict:
        """获取执行指标"""
        return {
            **self._metrics,
            "avg_node_duration": {
                k: v["total_duration"] / max(v["count"], 1)
                for k, v in self._metrics["node_executions"].items()
            }
        }
    
    def reset_metrics(self) -> None:
        """重置指标"""
        self._metrics = {
            "node_executions": {},
            "total_duration": 0.0,
            "failed_count": 0,
            "success_count": 0
        }