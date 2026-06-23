"""Prometheus Z Skills System - 意图持久化

基于Hermes Agent橙皮书的Skill系统：
- Skill是意图持久化的核心
- Curator决定"不学什么"
- Skill生命周期：创建→进化→退休
"""

from prometheus_z.skills.base import (
    Skill,
    SkillRegistry,
    Curator
)

__all__ = [
    "Skill",
    "SkillRegistry", 
    "Curator"
]

__version__ = "1.0.0"