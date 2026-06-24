"""Loop状态持久化 - State Management"""
import json
import time
from pathlib import Path
from typing import Any, Optional


class LoopStateStore:
    """Loop状态持久化 - 防止状态腐烂
    
    基于Loop Engineering的STATE.md模式：
    - 每次运行开头读状态
    - 每次运行结尾写结果
    - 定期剪枝过期条目
    """
    
    def __init__(self, state_dir: str = "loop_state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
    
    def _get_state_path(self, loop_id: str) -> Path:
        """获取状态文件路径"""
        return self.state_dir / f"{loop_id}.json"
    
    def save(self, loop_id: str, state: dict) -> None:
        """保存Loop状态"""
        path = self._get_state_path(loop_id)
        
        # 加载现有状态
        existing = self.load(loop_id) or {"loop_id": loop_id, "history": []}
        
        # 合并状态
        existing.update(state)
        existing["last_updated"] = time.time()
        
        with open(path, 'w') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
    
    def load(self, loop_id: str) -> Optional[dict]:
        """加载Loop状态"""
        path = self._get_state_path(loop_id)
        if not path.exists():
            return None
        
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def prune(self, loop_id: str, max_entries: int = 100,
              max_age_days: int = 30) -> dict:
        """剪枝过期状态
        
        基于Loop Engineering的State Rot防护：
        - 删除过期条目
        - 删除已解决/已合并的条目
        """
        state = self.load(loop_id)
        if not state:
            return {"pruned": 0, "remaining": 0}
        
        current_time = time.time()
        max_age_seconds = max_age_days * 86400
        
        original_count = len(state.get("history", []))
        
        # 剪枝过期的历史记录
        if "history" in state:
            pruned_history = []
            for entry in state["history"]:
                entry_time = entry.get("timestamp", 0)
                age_days = (current_time - entry_time) / 86400
                
                # 保留：近期或未完成的
                if age_days < max_age_days or not entry.get("completed", False):
                    pruned_history.append(entry)
            
            state["history"] = pruned_history[-max_entries:]
        
        # 保存剪枝后的状态
        self.save(loop_id, state)
        
        return {
            "pruned": original_count - len(state.get("history", [])),
            "remaining": len(state.get("history", []))
        }
    
    def append_history(self, loop_id: str, entry: dict) -> None:
        """追加历史记录"""
        state = self.load(loop_id)
        if not state:
            state = {"loop_id": loop_id, "history": []}
        
        if "history" not in state:
            state["history"] = []
        
        entry["timestamp"] = time.time()
        state["history"].append(entry)
        
        # 限制历史大小
        max_history = 100
        if len(state["history"]) > max_history:
            state["history"] = state["history"][-max_history:]
        
        self.save(loop_id, state)
    
    def get_history(self, loop_id: str, limit: int = 10) -> list[dict]:
        """获取历史记录"""
        state = self.load(loop_id)
        if not state:
            return []
        
        history = state.get("history", [])
        return history[-limit:]
    
    def clear(self, loop_id: str) -> None:
        """清除状态"""
        path = self._get_state_path(loop_id)
        if path.exists():
            path.unlink()
    
    def list_loops(self) -> list[str]:
        """列出所有Loop"""
        return [p.stem for p in self.state_dir.glob("*.json")]


class LoopStateManager:
    """Loop状态管理器 - 跨Loop协调
    
    基于Loop Engineering的多Loop协调原则：
    - 分离状态文件
    - 聚合Token预算
    - 碰撞检测
    """
    
    def __init__(self, state_dir: str = "loop_state"):
        self.store = LoopStateStore(state_dir)
        self._active_loops: dict[str, dict] = {}
    
    def begin_loop(self, loop_id: str, metadata: dict = None) -> dict:
        """开始Loop执行"""
        # 检查是否已有活跃实例
        if loop_id in self._active_loops:
            return {
                "status": "conflict",
                "message": f"Loop {loop_id} already active",
                "existing": self._active_loops[loop_id]
            }
        
        # 加载历史状态
        historical = self.store.get_history(loop_id, limit=5)
        
        # 注册活跃Loop
        self._active_loops[loop_id] = {
            "started_at": time.time(),
            "metadata": metadata or {},
            "historical_runs": len(historical)
        }
        
        return {
            "status": "started",
            "loop_id": loop_id,
            "historical_runs": len(historical),
            "can_proceed": True
        }
    
    def end_loop(self, loop_id: str, result: dict) -> None:
        """结束Loop执行"""
        if loop_id in self._active_loops:
            del self._active_loops[loop_id]
        
        # 追加到历史
        self.store.append_history(loop_id, result)
    
    def get_active_loops(self) -> list[dict]:
        """获取活跃的Loops"""
        return [
            {"loop_id": k, **v}
            for k, v in self._active_loops.items()
        ]
    
    def check_collision(self, loop_id: str, resource: str) -> bool:
        """检查资源碰撞"""
        for active_id, info in self._active_loops.items():
            if active_id != loop_id:
                if info.get("metadata", {}).get("resource") == resource:
                    return True
        return False