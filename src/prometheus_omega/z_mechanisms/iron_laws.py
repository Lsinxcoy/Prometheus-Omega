"""Ω系统 - Z机制适配层

从Z系统复制的真实实现，适配Ω的数据结构。
保留Z的核心逻辑，仅调整类型和依赖。
"""
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Optional
import math


# ═══════════════════════════════════════════
# Ω兼容的Schema定义 (来自Z的schema.py)
# ═══════════════════════════════════════════

class MemoryLayer(IntEnum):
    """三层记忆"""
    WORKING = 0
    EPISODIC = 1
    SEMANTIC = 2


@dataclass
class OmegaNode:
    """Ω兼容的节点结构"""
    content: str
    utility: float = 0.0
    surprise: float = 0.5
    embedding: Optional[list[float]] = None
    layer: MemoryLayer = MemoryLayer.EPISODIC
    created_at: float = field(default_factory=lambda: __import__('time').time())
    accessed_at: float = field(default_factory=lambda: __import__('time').time())


@dataclass
class WriteGateResult:
    """DopamineWriteGate输出 - 检查.allowed而非truthiness"""
    allowed: bool = False
    gate_value: float = 0.0
    reason: str = ""


@dataclass
class EvolutionCheckResult:
    """AntiEvolutionGate输出 - 检查.passed而非truthiness"""
    passed: bool = False
    reason: str = ""
    prerequisites_met: list[str] = field(default_factory=list)
    prerequisites_failed: list[str] = field(default_factory=list)


@dataclass
class OmegaConfig:
    """Ω配置 - 对应Z的ZConfig"""
    write_gate_tau: float = 1.0      # 写入门控阈值提高到1.0（原0.5太低）
    surprise_beta: float = 0.1       # 惊喜奖励
    max_utility: float = 5.0         # 最大效用值
    weibull_lambda: dict = field(default_factory=lambda: {0: 30.0, 1: 90.0, 2: 365.0})
    weibull_k: dict = field(default_factory=lambda: {0: 0.7, 1: 0.8, 2: 1.5})


# ═══════════════════════════════════════════
# DopamineWriteGate - 来自Z系统 store/write_gate.py
# ═══════════════════════════════════════════

class DopamineWriteGate:
    """M12: 多巴胺写入门控 - 乘法门控
    
    公式: gate_value = min(1.0, I(U≥τ) · [U × (S + β)])
    - I(U≥τ): 指示函数 - utility >= threshold时为1，否则为0
    - U: utility分数 (0-5)
    - S: surprise分数 (0-1)
    - β: surprise奖励 (防止门控崩溃)
    - τ: 写入门控
    
    关键: utility=0时，gate_value = 0 × 任何值 = 0 → 绝对拒绝
    """
    
    def __init__(self, config: OmegaConfig | None = None):
        self._config = config or OmegaConfig()
        self._tau = self._config.write_gate_tau
        self._beta = self._config.surprise_beta
        self._max_utility = self._config.max_utility
        self._stats = {"accepted": 0, "rejected": 0, "total_queries": 0}
    
    def should_write(self, node: OmegaNode,
                     existing_embeddings: list[list[float]] | None = None) -> WriteGateResult:
        """判断是否应该写入
        
        返回WriteGateResult - 检查.allowed而非truthiness
        """
        self._stats["total_queries"] += 1
        
        utility = min(node.utility, self._config.max_utility)
        
        # Step 1: 计算surprise
        surprise = node.surprise
        if existing_embeddings and node.embedding:
            surprise = self._compute_surprise(node.embedding, existing_embeddings)
        
        # Step 2: 乘法门控
        indicator = 1.0 if utility >= self._tau else 0.0
        gate_value = indicator * utility * (surprise + self._beta)
        gate_value = min(1.0, gate_value)
        
        # Step 3: 决策
        allowed = indicator > 0 and gate_value > 0
        
        if allowed:
            self._stats["accepted"] += 1
        else:
            self._stats["rejected"] += 1
        
        if indicator == 0.0:
            reason = f"Utility {utility:.2f} below threshold {self._tau:.2f}"
        elif gate_value <= 0:
            reason = f"Gate value {gate_value:.4f} = 0"
        else:
            reason = f"U={utility:.2f} S={surprise:.4f} β={self._beta:.2f} gate={gate_value:.4f}"
        
        return WriteGateResult(
            allowed=allowed,
            gate_value=gate_value,
            reason=reason,
        )
    
    def _compute_surprise(self, embedding: list[float],
                          existing: list[list[float]]) -> float:
        """计算surprise = 1 - max_cosine_similarity"""
        if not existing:
            return 1.0  # 首个同类 = 最大surprise
        
        max_sim = 0.0
        emb_norm = self._norm(embedding)
        if emb_norm == 0:
            return 0.0
        
        for ex in existing:
            ex_norm = self._norm(ex)
            if ex_norm == 0:
                continue
            dot = sum(a * b for a, b in zip(embedding, ex))
            sim = dot / (emb_norm * ex_norm)
            sim = max(-1.0, min(1.0, sim))
            if sim > max_sim:
                max_sim = sim
        
        return max(0.0, 1.0 - max_sim)
    
    @staticmethod
    def _norm(v: list[float]) -> float:
        """L2 norm"""
        return math.sqrt(sum(x * x for x in v))
    
    @property
    def stats(self) -> dict:
        return dict(self._stats)
    
    @property
    def rejection_rate(self) -> float:
        total = self._stats["accepted"] + self._stats["rejected"]
        if total == 0:
            return 0.0
        return self._stats["rejected"] / total


# ═══════════════════════════════════════════
# AntiEvolutionGate - 来自Z系统 evolution/anti_evolution_gate.py
# ═══════════════════════════════════════════

class AntiEvolutionGate:
    """Iron Law 2: 进化4前提条件
    
    除非全部4个前提通过，否则拒绝进化:
    1. DEDUP: 这是新见解吗？(不是已尝试过的)
    2. INSIGHT: 它提供真正的新理解吗？
    3. APPLICATION: 它能应用来改进什么吗？
    4. CONSECUTIVE_GAIN: 它会产生连续改进吗？
    
    任何失败 = 静默拒绝
    """
    
    _ATTEMPTED_NODE_TYPE = "_evolution_attempted"
    
    def __init__(self, config: OmegaConfig | None = None, store=None):
        self._config = config or OmegaConfig()
        self._store = store
        self._attempted: set[str] = set()
        self._stats = {
            "dedup_rejected": 0,
            "insight_rejected": 0,
            "application_rejected": 0,
            "consecutive_rejected": 0,
            "passed": 0
        }
    
    def gate_check(self, hypothesis: str,
                   existing_solutions: list[str] | None = None) -> EvolutionCheckResult:
        """检查全部4个前提条件
        
        返回EvolutionCheckResult - 检查.passed而非truthiness
        """
        existing = existing_solutions or []
        
        # Prerequisite 1: DEDUP
        if hypothesis in existing or hypothesis in self._attempted:
            self._stats["dedup_rejected"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"DEDUP: '{hypothesis[:50]}...' already attempted",
                prerequisites_failed=["DEDUP"],
            )
        
        # Prerequisite 2: INSIGHT
        if not self._has_insight(hypothesis):
            self._stats["insight_rejected"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"INSIGHT: doesn't provide new understanding",
                prerequisites_failed=["INSIGHT"],
            )
        
        # Prerequisite 3: APPLICATION
        if not self._has_application(hypothesis):
            self._stats["application_rejected"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"APPLICATION: cannot be applied",
                prerequisites_failed=["APPLICATION"],
            )
        
        # Prerequisite 4: CONSECUTIVE_GAIN
        if not self._has_consecutive_gain(hypothesis):
            self._stats["consecutive_rejected"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"CONSECUTIVE_GAIN: won't compound",
                prerequisites_failed=["CONSECUTIVE_GAIN"],
            )
        
        self._attempted.add(hypothesis)
        self._stats["passed"] += 1
        return EvolutionCheckResult(
            passed=True,
            reason="All 4 prerequisites passed",
            prerequisites_met=["DEDUP", "INSIGHT", "APPLICATION", "CONSECUTIVE_GAIN"],
        )
    
    def _has_insight(self, hypothesis: str) -> bool:
        """检查是否有新见解
        
        简化检测：有具体方案描述就算有insight
        """
        # 要求：有具体词汇（不是模糊词）
        insight_words = {"use", "add", "remove", "change", "improve", "reduce", 
                        "gate", "algorithm", "method", "approach", "with", "and"}
        words = set(hypothesis.lower().split())
        # 至少包含2个有意义的词
        meaningful = words & insight_words
        return len(meaningful) >= 2 or any(c.isdigit() for c in hypothesis)
    
    def _has_application(self, hypothesis: str) -> bool:
        """检查是否能应用
        
        简化：包含动词或动作词就算可应用
        """
        action_words = {"use", "add", "remove", "change", "improve", "reduce",
                       "implement", "apply", "optimize", "enhance", "increase", "decrease",
                       "gate", "to", "for", "by", "with"}
        words = set(hypothesis.lower().split())
        return bool(words & action_words)
    
    def _has_consecutive_gain(self, hypothesis: str) -> bool:
        """检查是否会产生连续收益"""
        # 简化：要求包含递进词
        compounding_words = ["compound", "chain", "stack", "cascade", "amplify", "bootstrap", "recursive"]
        return any(word in hypothesis.lower() for word in compounding_words) or "each" in hypothesis.lower()
    
    @property
    def stats(self) -> dict:
        return dict(self._stats)


# ═══════════════════════════════════════════
# VerificationIronLaw - 来自Z系统 evaluation/iron_law.py
# ═══════════════════════════════════════════

class VerificationIronLaw:
    """Iron Law 3: 5步验证门控
    
    步骤（强制，无跳过）:
    1. IDENTIFY — 声称是什么？
    2. RUN — 执行测试/实验
    3. READ — 收集输出
    4. VERIFY — 对比输出与预期（不用should/probably/seems）
    5. APPLY — 如果验证通过，应用变更
    
    拒绝词汇: "should", "probably", "seems", "likely", "might"
    只有硬证据通过
    """
    
    FUZZY_WORDS = {"should", "probably", "seems", "likely", "might",
                   "maybe", "perhaps", "possibly", "approximately",
                   "roughly", "guess", "assume", "presumably"}
    
    def __init__(self, config: OmegaConfig | None = None):
        self._config = config or OmegaConfig()
        self._stats = {
            "verified": 0,
            "rejected_fuzzy": 0,
            "rejected_no_evidence": 0,
            "rejected_no_improvement": 0
        }
    
    def verify(self, claim: str, evidence: dict,
               threshold: float = 0.9,
               direction: str = "maximize") -> EvolutionCheckResult:
        """5步验证
        
        Args:
            claim: 声称的内容
            evidence: 包含"before"和"after"数值的字典
            threshold: 接受的最小改进比例 (0.0-1.0)
            direction: "maximize"或"minimize"
        
        返回:
            EvolutionCheckResult - 检查.passed而非truthiness
        """
        # Step 1: IDENTIFY
        if not claim:
            return EvolutionCheckResult(passed=False, reason="No claim identified")
        
        # Step 1b: 检查模糊词
        if self._contains_fuzzy_words(claim):
            self._stats["rejected_fuzzy"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"FUZZY: Claim contains unverified language",
            )
        
        # Step 2-3: 检查证据
        if not evidence:
            self._stats["rejected_no_evidence"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason="NO_EVIDENCE: No evidence provided",
            )
        
        before = evidence.get("before", 0.0)
        after = evidence.get("after", 0.0)
        
        if before is None or after is None:
            self._stats["rejected_no_evidence"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason="NO_EVIDENCE: Missing 'before' or 'after'",
            )
        
        # Step 4: VERIFY
        if direction == "maximize":
            improved = after > before
            improvement = after - before
        else:
            improved = after < before
            improvement = before - after
        
        if not improved:
            self._stats["rejected_no_improvement"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"NO_IMPROVEMENT: {before:.3f} → {after:.3f}",
            )
        
        # 相对改进检查
        baseline = abs(before) if abs(before) > 1e-9 else 1.0
        relative_improvement = improvement / baseline
        if relative_improvement < (1 - threshold):
            self._stats["rejected_no_improvement"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"INSUFFICIENT: {relative_improvement:.3f} < {(1-threshold):.3f}",
            )
        
        # Step 5: APPLY
        self._stats["verified"] += 1
        return EvolutionCheckResult(
            passed=True,
            reason=f"VERIFIED: {before:.3f} → {after:.3f} (Δ={improvement:.3f})",
        )
    
    def verify_claim_text(self, claim_text: str) -> EvolutionCheckResult:
        """检查文本是否使用模糊语言"""
        if self._contains_fuzzy_words(claim_text):
            fuzzy = self._find_fuzzy_words(claim_text)
            self._stats["rejected_fuzzy"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"FUZZY: Found unverified words: {fuzzy}",
            )
        return EvolutionCheckResult(passed=True, reason="No fuzzy words detected")
    
    def _contains_fuzzy_words(self, text: str) -> bool:
        words = set(text.lower().split())
        return bool(words & self.FUZZY_WORDS)
    
    def _find_fuzzy_words(self, text: str) -> list[str]:
        words = set(text.lower().split())
        return sorted(words & self.FUZZY_WORDS)
    
    @property
    def stats(self) -> dict:
        return dict(self._stats)


# ═══════════════════════════════════════════
# WeibullForgetting - 来自Z系统 store/forgetting.py
# ═══════════════════════════════════════════

class WeibullForgetting:
    """M7: Weibull遗忘曲线 - 每层记忆有不同的衰减参数
    
    每层记忆有不同的Weibull参数:
    - WORKING: 快��衰减 (λ=30天, k=0.7) — 短期暂存
    - EPISODIC: 中等衰减 (λ=90天, k=0.8) — 事件记忆
    - SEMANTIC: 慢速衰减 (λ=365天, k=1.5) — 巩固知识
    
    Weibull CDF: F(t) = 1 - exp(-(t/λ)^k)
    保留率: R(t) = exp(-(t/λ)^k)
    """
    
    def __init__(self, config: OmegaConfig | None = None):
        self._config = config or OmegaConfig()
        self._lambdas = self._config.weibull_lambda
        self._ks = self._config.weibull_k
    
    def retention(self, node: OmegaNode, now: float | None = None) -> float:
        """计算节点的保留概率
        
        R(t) = exp(-(age/λ)^k)
        返回 [0, 1]。1.0 = 完全保留，0.0 = 完全遗忘
        """
        if now is None:
            import time
            now = time.time()
        
        age_days = max(0, (now - node.created_at) / 86400)
        layer = int(node.layer)
        lam = self._lambdas.get(layer, 90.0)
        k = self._ks.get(layer, 0.8)
        
        if lam <= 0:
            return 0.0
        
        x = age_days / lam
        if x <= 0:
            return 1.0
        
        return math.exp(-(x ** k))
    
    def freshness(self, node: OmegaNode, now: float | None = None) -> float:
        """计算新鲜度用于重力公式
        
        freshness = exp(-age_days / λ)
        """
        if now is None:
            import time
            now = time.time()
        
        age_days = max(0, (now - node.accessed_at) / 86400)
        layer = int(node.layer)
        lam = self._lambdas.get(layer, 90.0)
        
        if lam <= 0:
            return 0.0
        
        return math.exp(-age_days / lam)
    
    def should_forget(self, node: OmegaNode, threshold: float = 0.1,
                      now: float | None = None) -> bool:
        """检查是否应该遗忘（保留率低于阈值）"""
        return self.retention(node, now) < threshold
    
    def decay_utility(self, node: OmegaNode, now: float | None = None) -> float:
        """应用基于时间的utility衰减"""
        ret = self.retention(node, now)
        return node.utility * ret


__all__ = [
    "DopamineWriteGate",
    "AntiEvolutionGate",
    "VerificationIronLaw",
    "WeibullForgetting",
    "OmegaNode",
    "OmegaConfig",
    "WriteGateResult",
    "EvolutionCheckResult",
]