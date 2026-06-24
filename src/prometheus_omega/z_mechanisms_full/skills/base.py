"""Skill基础框架 - 参考Hermes Curator机制

基于Hermes Agent橙皮书的Skill系统：
- Skill是意图持久化的核心
- Curator决定"不学什么"
- Skill生命周期：创建→进化→退休
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
import json
from pathlib import Path
import time


@dataclass
class Skill:
    """Skill抽象 - 可复用的行为模式"""
    name: str
    description: str
    trigger_conditions: list[str] = field(default_factory=list)
    actions: list[dict] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    usage_count: int = 0
    success_rate: float = 0.0
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "trigger_conditions": self.trigger_conditions,
            "actions": self.actions,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Skill':
        return cls(**data)
    
    def increment_usage(self) -> None:
        """增加使用计数"""
        self.usage_count += 1
        self.updated_at = time.time()
    
    def update_success(self, success: bool) -> None:
        """更新成功率"""
        if self.usage_count == 0:
            self.success_rate = 1.0 if success else 0.0
        else:
            # 滑动平均
            alpha = 0.1
            self.success_rate = (
                alpha * (1.0 if success else 0.0) + 
                (1 - alpha) * self.success_rate
            )
        self.updated_at = time.time()


class SkillRegistry:
    """Skill注册表 - 管理Skill生命周期
    
    参���Hermes Curator：
    - 自动创建Skill
    - 根据使用反馈进化
    - 决定哪些Skill应该退休
    """
    
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(exist_ok=True)
        self._skills: dict[str, Skill] = {}
        self._load_all()
    
    def _load_all(self) -> None:
        """加载所有Skill"""
        for f in self.skills_dir.glob("*.json"):
            try:
                with open(f) as fp:
                    data = json.load(fp)
                    skill = Skill.from_dict(data)
                    self._skills[skill.name] = skill
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to load skill from {f}: {e}")
    
    def register(self, skill: Skill) -> None:
        """注册或更新Skill"""
        skill.updated_at = time.time()
        self._skills[skill.name] = skill
        self._persist(skill)
    
    def _persist(self, skill: Skill) -> None:
        """持久化Skill"""
        path = self.skills_dir / f"{skill.name}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(skill.to_dict(), f, indent=2, ensure_ascii=False)
    
    def get(self, name: str) -> Optional[Skill]:
        """获取Skill"""
        return self._skills.get(name)
    
    def find_matching(self, context: dict) -> list[Skill]:
        """查找匹配的Skill
        
        基于trigger_conditions匹配
        """
        matches = []
        context_str = str(context).lower()
        
        for skill in self._skills.values():
            for trigger in skill.trigger_conditions:
                if trigger.lower() in context_str:
                    matches.append(skill)
                    break
        
        # 按成功率排序
        matches.sort(key=lambda s: s.success_rate, reverse=True)
        return matches
    
    def record_usage(self, skill_name: str, success: bool) -> None:
        """记录Skill使用 - 用于Curator决策"""
        skill = self._skills.get(skill_name)
        if skill:
            skill.increment_usage()
            skill.update_success(success)
            self._persist(skill)
    
    def list_all(self) -> list[Skill]:
        """列出所有Skill"""
        return list(self._skills.values())
    
    def delete(self, name: str) -> bool:
        """删除Skill"""
        if name in self._skills:
            del self._skills[name]
            path = self.skills_dir / f"{name}.json"
            if path.exists():
                path.unlink()
            return True
        return False
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        if not self._skills:
            return {"total": 0, "avg_success_rate": 0.0}
        
        total = len(self._skills)
        avg_rate = sum(s.success_rate for s in self._skills.values()) / total
        total_usage = sum(s.usage_count for s in self._skills.values())
        
        return {
            "total": total,
            "avg_success_rate": avg_rate,
            "total_usage": total_usage,
            "by_version": self._count_by_version()
        }
    
    def _count_by_version(self) -> dict:
        counts = {}
        for s in self._skills.values():
            v = s.version.split('.')[0]
            counts[v] = counts.get(v, 0) + 1
        return counts


class Curator:
    """Curator引擎 - 决定哪些Skill应该退休
    
    基于Hermes橙皮书的"最该学的是不要学"：
    - 不是所有经验都值得沉淀为Skill
    - 成功率低的Skill应该退休
    - 使用次数少且成功率低于阈值的也应该清理
    """
    
    def __init__(self, registry: SkillRegistry,
                 min_success_rate: float = 0.6,
                 min_usage: int = 5,
                 retirement_check_interval: int = 10):
        self.registry = registry
        self.min_success_rate = min_success_rate
        self.min_usage = min_usage
        self.retirement_check_interval = retirement_check_interval
        self._check_counter = 0
    
    def should_retire(self, skill_name: str) -> tuple[bool, str]:
        """判断Skill是否应该退休"""
        skill = self.registry.get(skill_name)
        if not skill:
            return False, "not_found"
        
        # 使用次数不足
        if skill.usage_count < self.min_usage:
            return False, f"insufficient_usage_{skill.usage_count}"
        
        # 成功率低于阈值
        if skill.success_rate < self.min_success_rate:
            return True, f"low_success_rate_{skill.success_rate:.1%}"
        
        return False, "ok"
    
    def get_retirement_candidates(self) -> list[dict]:
        """获取应该退休的Skill列表"""
        candidates = []
        
        for skill in self.registry.list_all():
            retire, reason = self.should_retire(skill.name)
            if retire:
                candidates.append({
                    "name": skill.name,
                    "reason": reason,
                    "usage_count": skill.usage_count,
                    "success_rate": skill.success_rate
                })
        
        return candidates
    
    def execute_retirement(self) -> list[str]:
        """执行退休操作"""
        self._check_counter += 1
        
        if self._check_counter < self.retirement_check_interval:
            return []
        
        self._check_counter = 0
        candidates = self.get_retirement_candidates()
        retired = []
        
        for candidate in candidates:
            name = candidate["name"]
            if self.registry.delete(name):
                retired.append(name)
        
        return retired
    
    def get_recommendations(self) -> dict:
        """获取优化建议"""
        recommendations = {}
        
        for skill in self.registry.list_all():
            retire, reason = self.should_retire(skill.name)
            
            if retire:
                recommendations[skill.name] = {"action": "retire", "reason": reason}
            elif skill.usage_count > 10 and skill.success_rate > 0.8:
                # 高使用高成功 - 考虑优化
                recommendations[skill.name] = {"action": "optimize", "reason": "high_usage_high_success"}
            elif skill.usage_count > 5 and skill.success_rate < 0.5:
                # 中使用低成功 - 需要改进
                recommendations[skill.name] = {"action": "improve", "reason": "moderate_usage_low_success"}
        
        return recommendations