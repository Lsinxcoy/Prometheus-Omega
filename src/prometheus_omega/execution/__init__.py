# 基础导入
from __future__ import annotations
import sys, os, re, json, time, datetime
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto


"""Execution - 执行层 (DAG+Parallel+Retryable+Monitored)"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import uuid, time


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DAGNode:
    """DAG节点"""
    node_id: str
    task: Any
    depends_on: List[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    
    def is_ready(self) -> bool:
        return self.status == NodeStatus.PENDING
    
    def is_completed(self) -> bool:
        return self.status == NodeStatus.COMPLETED
    
    def is_failed(self) -> bool:
        return self.status == NodeStatus.FAILED
    
    def mark_running(self):
        self.status = NodeStatus.RUNNING
    
    def mark_completed(self, result: Any):
        self.status = NodeStatus.COMPLETED
        self.result = result
    
    def mark_failed(self, error: Any):
        self.status = NodeStatus.FAILED
        self.result = error
    
    def get_info(self) -> Dict:
        return {
            'node_id': self.node_id,
            'status': self.status.value,
            'depends_on': self.depends_on,
            'has_result': self.result is not None,
        }


class DAGExecutor:
    """DAG执行器"""
    
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
    
    def add_node(self, node_id: str, task: Any, deps: List[str] = None):
        self.nodes[node_id] = DAGNode(node_id, task, deps or [])
    
    def execute(self) -> Dict[str, Any]:
        results = {}
        executed = set()
        
        while len(executed) < len(self.nodes):
            for node_id, node in self.nodes.items():
                if node_id in executed:
                    continue
                
                deps_done = all(d in executed for d in node.depends_on)
                if deps_done:
                    node.status = NodeStatus.RUNNING
                    node.result = {"node": node_id, "executed": True}
                    node.status = NodeStatus.COMPLETED
                    results[node_id] = node.result
                    executed.add(node_id)
        
        return results


class ParallelDAG:
    """并行DAG执行"""
    
    def __init__(self, max_parallel: int = 4):
        self.max_parallel = max_parallel
        self.execution_log: List[Dict] = []
        self._max_log = 200
    
    def execute_parallel(self, nodes: List[DAGNode]) -> List[Any]:
        results = []
        levels = self._compute_levels(nodes)
        
        for level_nodes in levels:
            batch = level_nodes[:self.max_parallel]
            for node in batch:
                try:
                    if callable(node.task):
                        node.result = node.task()
                    else:
                        node.result = {"node": node.node_id, "executed": True}
                    node.status = NodeStatus.COMPLETED
                    results.append(node.result)
                    self.execution_log.append({'node_id': node.node_id, 'status': 'completed', 'timestamp': time.time()})
                except Exception as e:
                    node.status = NodeStatus.FAILED
                    node.result = {'error': str(e)}
                    results.append(node.result)
            
            if len(self.execution_log) > self._max_log:
                self.execution_log = self.execution_log[-self._max_log:]
        
        return results
    
    def _compute_levels(self, nodes: List[DAGNode]) -> List[List[DAGNode]]:
        levels = []
        executed = set()
        
        while len(executed) < len(nodes):
            current_level = []
            for node in nodes:
                if node.node_id in executed:
                    continue
                deps_done = all(d in executed for d in node.depends_on)
                if deps_done:
                    current_level.append(node)
            
            if not current_level:
                break
            
            levels.append(current_level)
            for node in current_level:
                executed.add(node.node_id)
        
        return levels
    
    def get_statistics(self) -> Dict:
        if not self.execution_log:
            return {'total': 0, 'completed': 0, 'failed': 0}
        
        completed = sum(1 for l in self.execution_log if l['status'] == 'completed')
        failed = sum(1 for l in self.execution_log if l['status'] == 'failed')
        
        return {'total': len(self.execution_log), 'completed': completed, 'failed': failed}


class RetryableDAG:
    """可重试DAG"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_log: List[Dict] = []
    
    def execute_with_retry(self, node: DAGNode) -> Any:
        last_error = None
        for attempt in range(self.max_retries):
            try:
                if callable(node.task):
                    result = node.task()
                else:
                    result = {"node": node.node_id, "executed": True}
                self.retry_log.append({'node_id': node.node_id, 'attempt': attempt+1, 'success': True, 'timestamp': time.time()})
                return result
            except Exception as e:
                last_error = e
                self.retry_log.append({'node_id': node.node_id, 'attempt': attempt+1, 'success': False, 'error': str(e), 'timestamp': time.time()})
        raise last_error
    
    def get_retry_count(self, node_id: str) -> int:
        return sum(1 for l in self.retry_log if l['node_id'] == node_id and not l['success'])


class MonitoredDAG:
    """可监控DAG"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self._history_size = 500
    
    def record(self, node_id: str, metric: str, value: Any):
        if node_id not in self.metrics:
            self.metrics[node_id] = {'records': []}
        
        record = {'metric': metric, 'value': value, 'timestamp': time.time()}
        self.metrics[node_id]['records'].append(record)
        
        if len(self.metrics[node_id]['records']) > self._history_size:
            self.metrics[node_id]['records'] = self.metrics[node_id]['records'][-self._history_size:]
    
    def get_node_metrics(self, node_id: str) -> Dict:
        if node_id not in self.metrics:
            return {}
        
        records = self.metrics[node_id].get('records', [])
        numeric = {r['metric']: r['value'] for r in records if isinstance(r['value'], (int, float))}
        
        if not numeric:
            return {'records': len(records)}
        
        return {'count': len(records), 'min': min(numeric.values()), 'max': max(numeric.values()), 'avg': sum(numeric.values()) / len(numeric)}
    
    def get_all_metrics(self) -> Dict[str, Dict]:
        return {nid: self.get_node_metrics(nid) for nid in self.metrics}
    
    def clear_metrics(self):
        self.metrics = {}


# 工厂
def create_dag_executor() -> DAGExecutor:
    return DAGExecutor()

def create_parallel_dag(max_parallel: int = 4) -> ParallelDAG:
    return ParallelDAG(max_parallel=max_parallel)

def create_retryable_dag(max_retries: int = 3) -> RetryableDAG:
    return RetryableDAG(max_retries=max_retries)

def create_monitored_dag() -> MonitoredDAG:
    return MonitoredDAG()


# ===== 来自XYZ系统 =====
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

