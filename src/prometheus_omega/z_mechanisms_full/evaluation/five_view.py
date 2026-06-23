"""五视图评估器 - 基于2606.17546 SEAGym论文

论文核心洞察：
- 频繁更新可能无法提升held-out性能
- 有效中间快照可能崩溃
- 源多样性和模型后端影响harness可靠性

五视图：训练/验证/测试/重放/成本
"""
from dataclasses import dataclass, field
from typing import Optional, Any
import time
import copy
import json
from pathlib import Path


@dataclass
class Snapshot:
    """基因组快照"""
    genome_id: str
    genome_data: dict
    timestamp: float
    train_score: float = 0.0
    validation_score: float = 0.0
    test_score: float = 0.0
    cost: float = 0.0
    metadata: dict = field(default_factory=dict)


class FiveViewEvaluator:
    """五视图评估器 - SEAGym风格的自进化评估"""
    
    def __init__(self, snapshot_dir: str = "snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(exist_ok=True)
        
        self.snapshots: list[Snapshot] = []
        self._current_snapshot_id = 0
    
    def snapshot(self, genome, scores: dict) -> Snapshot:
        """创建快照
        
        Args:
            genome: 基因组对象
            scores: 分数字典 {train, validation, test, cost}
            
        Returns:
            Snapshot对象
        """
        self._current_snapshot_id += 1
        snapshot_id = f"snap_{self._current_snapshot_id}"
        
        snapshot = Snapshot(
            genome_id=snapshot_id,
            genome_data=self._serialize_genome(genome),
            timestamp=time.time(),
            train_score=scores.get("train", 0.0),
            validation_score=scores.get("validation", 0.0),
            test_score=scores.get("test", 0.0),
            cost=scores.get("cost", 0.0),
            metadata=scores.get("metadata", {})
        )
        
        self.snapshots.append(snapshot)
        self._save_snapshot(snapshot)
        
        return snapshot
    
    def _serialize_genome(self, genome) -> dict:
        """序列化基因组"""
        if hasattr(genome, "__dict__"):
            return {"type": type(genome).__name__, "data": vars(genome)}
        return {"type": "unknown", "data": str(genome)}
    
    def _save_snapshot(self, snapshot: Snapshot) -> None:
        """保存快照到磁盘"""
        path = self.snapshot_dir / f"{snapshot.genome_id}.json"
        with open(path, 'w') as f:
            json.dump({
                "genome_id": snapshot.genome_id,
                "genome_data": snapshot.genome_data,
                "timestamp": snapshot.timestamp,
                "train_score": snapshot.train_score,
                "validation_score": snapshot.validation_score,
                "test_score": snapshot.test_score,
                "cost": snapshot.cost,
                "metadata": snapshot.metadata
            }, f, indent=2)
    
    def detect_overfitting(self) -> bool:
        """检测过拟合：validation下降但test上升
        
        Returns:
            True if overfitting detected
        """
        if len(self.snapshots) < 3:
            return False
        
        recent = self.snapshots[-1]
        prev = self.snapshots[-3]
        
        # 检查：validation下降，test上升
        validation_dropped = recent.validation_score < prev.validation_score
        test_improved = recent.test_score > prev.test_score
        
        return validation_dropped and test_improved
    
    def detect_collapse(self) -> bool:
        """检测崩溃：有效快照之后性能崩溃
        
        Returns:
            True if collapse detected
        """
        if len(self.snapshots) < 5:
            return False
        
        # 找到validation最高的快照
        best_idx = max(range(len(self.snapshots)), 
                      key=lambda i: self.snapshots[i].validation_score)
        
        # 检查之后是否崩溃
        if best_idx < len(self.snapshots) - 2:
            best_score = self.snapshots[best_idx].validation_score
            recent_score = self.snapshots[-1].validation_score
            
            # 崩溃：性能下降超过30%
            if recent_score < best_score * 0.7:
                return True
        
        return False
    
    def select_best_snapshot(self) -> Optional[Snapshot]:
        """选择最佳快照（平衡performance + 稳定性）
        
        策略：选择validation较高且不是最近的
        """
        if not self.snapshots:
            return None
        
        # 过滤出validation分数大于0的
        valid_snapshots = [s for s in self.snapshots if s.validation_score > 0]
        
        if not valid_snapshots:
            return self.snapshots[0]
        
        # 选择validation最高的
        best = max(valid_snapshots, key=lambda s: s.validation_score)
        
        # 如果最近的快照不是最佳，可能有过拟合风险
        if best != self.snapshots[-1] and self.detect_overfitting():
            # 返回最佳而非最近的
            return best
        
        return best
    
    def get_five_view_report(self) -> dict:
        """获取五视图报告
        
        Returns:
            包含5个视图的完整报告
        """
        if not self.snapshots:
            return {"status": "no_snapshots"}
        
        latest = self.snapshots[-1]
        
        return {
            "train": {
                "latest": latest.train_score,
                "history": [s.train_score for s in self.snapshots[-10:]]
            },
            "validation": {
                "latest": latest.validation_score,
                "history": [s.validation_score for s in self.snapshots[-10:]]
            },
            "test": {
                "latest": latest.test_score,
                "history": [s.test_score for s in self.snapshots[-10:]]
            },
            "replay": {
                "best": max(s.validation_score for s in self.snapshots) if self.snapshots else 0,
                "recent": self.snapshots[-1].validation_score if self.snapshots else 0
            },
            "cost": {
                "latest": latest.cost,
                "total": sum(s.cost for s in self.snapshots)
            },
            "diagnostics": {
                "overfitting_detected": self.detect_overfitting(),
                "collapse_detected": self.detect_collapse()
            }
        }
    
    def get_summary(self) -> dict:
        """获取评估摘要"""
        return {
            "total_snapshots": len(self.snapshots),
            "latest_train": self.snapshots[-1].train_score if self.snapshots else 0,
            "latest_validation": self.snapshots[-1].validation_score if self.snapshots else 0,
            "latest_test": self.snapshots[-1].test_score if self.snapshots else 0,
            "overfitting": self.detect_overfitting(),
            "collapse": self.detect_collapse()
        }