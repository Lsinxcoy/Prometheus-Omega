"""Disposition用户偏好学习 - 基于Hindsight的人格特质系统

论文核心: 从记忆中学些用户的偏好和行为模式

Disposition Traits:
- 用户沟通风格 (formal/casual)
- 响应偏好 (brief/detailed)
- 交互模式 (questioner/explorer)
- 技术偏好 (technical_level)
- 时间偏好 (time_availability)
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid
import json


class DispositionTrait(Enum):
    """人格特质类型"""
    COMMUNICATION_STYLE = "communication_style"  # 沟通风格
    RESPONSE_PREFERENCE = "response_preference"   # 响应偏好
    INTERACTION_MODE = "interaction_mode"         # 交互模式
    TECHNICAL_LEVEL = "technical_level"           # 技术水平
    TIME_AVAILABILITY = "time_availability"       # 时间可用性
    TOPIC_INTERESTS = "topic_interests"           # 话题兴趣
    RECIPROCAL_PREFERENCE = "reciprocal_preference"  # 互动偏好


class TraitValue(Enum):
    """特质值枚举"""
    # 沟通风格
    FORMAL = "formal"
    CASUAL = "casual"
    MIXED = "mixed"
    
    # 响应偏好
    BRIEF = "brief"
    DETAILED = "detailed"
    ADAPTIVE = "adaptive"
    
    # 交互模式
    QUESTIONER = "questioner"    # 提问者
    EXPLORER = "explorer"        # 探索者
    DIRECT = "direct"            # 直接指令
    COLLABORATIVE = "collaborative"  # 协作
    
    # 技术水平
    EXPERT = "expert"
    INTERMEDIATE = "intermediate"
    NOVICE = "novice"
    UNKNOWN = "unknown"


@dataclass
class TraitObservation:
    """特质观察 - 从交互中提取的证据"""
    observation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trait_type: DispositionTrait = DispositionTrait.COMMUNICATION_STYLE
    
    # 观察内容
    evidence: str = ""
    inferred_value: str = ""
    confidence: float = 0.5  # 0-1
    
    # 来源
    source_interaction_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 元数据
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DispositionTraitProfile:
    """人格特质画像
    
    存储单个特质的多维度信息：
    - 当前值和置信度
    - 观察历史
    - 置信度随时间的变化
    """
    trait_type: DispositionTrait
    current_value: str = ""
    confidence: float = 0.5  # 对当前值的置信度
    
    # 观察统计
    total_observations: int = 0
    observation_history: List[TraitObservation] = field(default_factory=list)
    
    # 值分布 (用于贝叶斯更新)
    value_counts: Dict[str, int] = field(default_factory=dict)
    
    # 时序
    first_observed: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    update_count: int = 0
    
    def add_observation(self, observation: TraitObservation) -> None:
        """添加观察并更新画像"""
        self.total_observations += 1
        self.observation_history.append(observation)
        
        # 更新值计数
        value = observation.inferred_value
        self.value_counts[value] = self.value_counts.get(value, 0) + 1
        
        # 更新当前值（基于多���投票）
        if self.value_counts[value] >= self.value_counts.get(self.current_value, 0):
            self.current_value = value
        
        # 更新置信度
        self._update_confidence()
        
        # 更新时间
        self.last_updated = datetime.now()
        self.update_count += 1
        
        if self.first_observed is None:
            self.first_observed = self.last_updated
        
        # 保持历史在50条以内
        self.observation_history = self.observation_history[-50:]
    
    def _update_confidence(self) -> None:
        """基于观察数量和一致性更新置信度"""
        # 观测越多，置信度越高（有上限）
        count_factor = min(1.0, self.total_observations / 20)
        
        # 一致性因子：多数值占比
        total = sum(self.value_counts.values())
        if total > 0:
            max_count = max(self.value_counts.values())
            consistency_factor = max_count / total
        else:
            consistency_factor = 0.0
        
        # 综合置信度
        self.confidence = (count_factor * 0.6 + consistency_factor * 0.4)
    
    def get_value_distribution(self) -> Dict[str, float]:
        """获取值的分布概率"""
        total = sum(self.value_counts.values())
        if total == 0:
            return {}
        
        return {
            value: count / total 
            for value, count in self.value_counts.items()
        }
    
    def to_dict(self) -> dict:
        return {
            "trait_type": self.trait_type.value,
            "current_value": self.current_value,
            "confidence": round(self.confidence, 3),
            "observations": self.total_observations,
            "value_distribution": self.get_value_distribution(),
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }


class DispositionLearner:
    """Disposition学习器 - 从交互中学习用户偏好
    
    基于Hindsight的核心机制：
    1. 观察提取：从交互中识别特质信号
    2. 信念更新：使用贝叶斯方法更新特质信念
    3. 偏好预测：基于学习到的特质生成个性化响应
    """
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        
        # 所有特质画像
        self.traits: Dict[DispositionTrait, DispositionTraitProfile] = {}
        
        # 初始化默认特质
        for trait_type in DispositionTrait:
            self.traits[trait_type] = DispositionTraitProfile(trait_type=trait_type)
        
        # 观察模式库
        self._observation_patterns = self._init_patterns()
    
    def _init_patterns(self) -> Dict[DispositionTrait, List[dict]]:
        """初始化观察模式库"""
        return {
            DispositionTrait.COMMUNICATION_STYLE: [
                {"keywords": ["请", "麻烦", "感谢"], "value": TraitValue.FORMAL.value, "weight": 0.8},
                {"keywords": ["嘿", "喂", "有啥"], "value": TraitValue.CASUAL.value, "weight": 0.8},
            ],
            DispositionTrait.RESPONSE_PREFERENCE: [
                {"keywords": ["简单", "简短", "一句话"], "value": TraitValue.BRIEF.value, "weight": 0.7},
                {"keywords": ["详细", "完整", "展开"], "value": TraitValue.DETAILED.value, "weight": 0.7},
            ],
            DispositionTrait.INTERACTION_MODE: [
                {"keywords": ["为什么", "怎么", "什么"], "value": TraitValue.QUESTIONER.value, "weight": 0.6},
                {"keywords": ["试试", "探索", "看看"], "value": TraitValue.EXPLORER.value, "weight": 0.6},
                {"keywords": ["直接", "快", "赶紧"], "value": TraitValue.DIRECT.value, "weight": 0.7},
            ],
            DispositionTrait.TECHNICAL_LEVEL: [
                {"keywords": ["api", "sdk", "源码", "架构"], "value": TraitValue.EXPERT.value, "weight": 0.9},
                {"keywords": ["教程", "入门", "基础"], "value": TraitValue.NOVICE.value, "weight": 0.8},
            ]
        }
    
    def observe(self, text: str, interaction_id: str = None) -> List[TraitObservation]:
        """观察交互并提取特质证据
        
        分析用户输入，识别特质信号
        """
        observations = []
        text_lower = text.lower()
        
        # 遍历所有特质模式
        for trait_type, patterns in self._observation_patterns.items():
            for pattern in patterns:
                # 关键词匹配
                matched = any(kw in text_lower for kw in pattern["keywords"])
                
                if matched:
                    observation = TraitObservation(
                        trait_type=trait_type,
                        evidence=f"关键词匹配: {pattern['keywords']}",
                        inferred_value=pattern["value"],
                        confidence=pattern["weight"],
                        source_interaction_id=interaction_id,
                        context={"matched_keywords": pattern["keywords"]}
                    )
                    observations.append(observation)
        
        return observations
    
    def learn(self, observations: List[TraitObservation]) -> None:
        """学习观察结果，更新特质画像
        
        将观察结果整合到特质画像中
        """
        for obs in observations:
            if obs.trait_type in self.traits:
                self.traits[obs.trait_type].add_observation(obs)
    
    def get_trait(self, trait_type: DispositionTrait) -> DispositionTraitProfile:
        """获取特质画像"""
        return self.traits.get(trait_type)
    
    def get_preferences(self, min_confidence: float = 0.3) -> Dict[str, Any]:
        """获取用户偏好摘要
        
        返回所有高于阈值的特质
        """
        preferences = {}
        
        for trait_type, profile in self.traits.items():
            if profile.confidence >= min_confidence and profile.current_value:
                preferences[trait_type.value] = {
                    "value": profile.current_value,
                    "confidence": round(profile.confidence, 3),
                    "observations": profile.total_observations
                }
        
        return preferences
    
    def apply_preferences(self, response_template: str) -> str:
        """应用偏好到响应模板
        
        根据用户偏好调整响应风格
        """
        prefs = self.get_preferences()
        
        # 沟通风格
        comm_style = prefs.get("communication_style", {}).get("value", "mixed")
        
        if comm_style == TraitValue.FORMAL.value:
            response_template = response_template.replace("{greeting}", "您好")
            response_template = response_template.replace("{closing}", "谢谢")
        elif comm_style == TraitValue.CASUAL.value:
            response_template = response_template.replace("{greeting}", "嘿")
            response_template = response_template.replace("{closing}", "回见")
        else:
            response_template = response_template.replace("{greeting}", "你好")
            response_template = response_template.replace("{closing}", "再见")
        
        # 响应偏好
        resp_pref = prefs.get("response_preference", {}).get("value", "adaptive")
        
        if resp_pref == TraitValue.BRIEF.value:
            # 截断为简短版本
            sentences = response_template.split("。")
            response_template = "。".join(sentences[:2]) + "。"
        
        return response_template
    
    def get_profile(self) -> Dict[str, Any]:
        """获取完整画像"""
        return {
            "user_id": self.user_id,
            "traits": {
                trait_type.value: profile.to_dict()
                for trait_type, profile in self.traits.items()
            },
            "summary": self.get_preferences(),
            "overall_confidence": sum(
                p.confidence for p in self.traits.values()
            ) / len(self.traits) if self.traits else 0
        }


def create_disposition_learner(user_id: str = "default") -> DispositionLearner:
    """工厂函数：创建Disposition学习器"""
    return DispositionLearner(user_id=user_id)