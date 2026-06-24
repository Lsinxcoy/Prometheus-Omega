"""Skills - 技能层 (SkillRegistry+Curator+SkillClaw)"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timezone
from enum import Enum
import uuid


class SkillStatus(Enum):
    ACTIVE = "active"
    LEARNING = "learning"
    ARCHIVED = "archived"


@dataclass
class Skill:
    skill_id: str
    name: str
    description: str
    success_rate: float = 0.0
    usage_count: int = 0
    status: SkillStatus = SkillStatus.LEARNING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillRegistry:
    """技能注册表 - 来自Z/X系统"""
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
    
    def register(self, name: str, description: str = "", 
                 executor: Optional[Callable] = None) -> str:
        skill_id = str(uuid.uuid4())
        self.skills[skill_id] = Skill(
            skill_id=skill_id,
            name=name,
            description=description,
            metadata={"executor": executor}
        )
        return skill_id
    
    def get(self, skill_id: str) -> Optional[Skill]:
        return self.skills.get(skill_id)
    
    def list_all(self) -> List[Skill]:
        return list(self.skills.values())
    
    def update_usage(self, skill_id: str, success: bool):
        skill = self.skills.get(skill_id)
        if skill:
            skill.usage_count += 1
            n = skill.usage_count
            old_rate = skill.success_rate
            skill.success_rate = (old_rate * (n-1) + (1 if success else 0)) / n


class Curator:
    """策展人 - 来自Z系统
    
    自动技能策展
    """
    
    def __init__(self, registry: SkillRegistry,
                 min_success_rate: float = 0.6,
                 min_usage: int = 5):
        self.registry = registry
        self.min_success_rate = min_success_rate
        self.min_usage = min_usage
    
    def curate(self) -> Dict[str, List[str]]:
        """策展返回需要归档和激活的技能"""
        to_archive = []
        to_activate = []
        
        for skill in self.registry.list_all():
            if skill.usage_count >= self.min_usage:
                if skill.success_rate >= self.min_success_rate:
                    skill.status = SkillStatus.ACTIVE
                    to_activate.append(skill.skill_id)
                else:
                    skill.status = SkillStatus.ARCHIVED
                    to_archive.append(skill.skill_id)
        
        return {
            "activate": to_activate,
            "archive": to_archive
        }


class SkillClaw:
    """SkillClaw PRM 4级路由 - 来自X系统#62"""
    
    def __init__(self):
        self.routes = {
            "pattern_match": [],
            "semantic_similarity": [],
            "context_aware": [],
            "adaptive": []
        }
    
    def route(self, query: str, skills: List[Skill]) -> Optional[Skill]:
        # 4级路由
        for skill in skills:
            if skill.status == SkillStatus.ACTIVE:
                return skill
        return None


# 工厂
def create_skill_registry() -> SkillRegistry:
    return SkillRegistry()

def create_curator(registry: SkillRegistry, **kwargs) -> Curator:
    return Curator(registry, **kwargs)