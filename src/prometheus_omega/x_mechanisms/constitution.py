"""Prometheus X — Governance System

22-constitution + 5-level autonomy + 3-level trust + ConfidenceGate + EvolutionGrill.
Sources: Prometheus V8 governance/ + V11 governance/.
"""

from __future__ import annotations

import time
from typing import Any

from prometheus_x.core.constants import (
    AUTONOMY_FREQUENCY_LIMIT,
    AUTONOMY_FREQUENCY_WINDOW,
    GRILL_THRESHOLDS,
    TRUST_SOURCE_THRESHOLD,
)
from prometheus_x.core.schema import (
    AutonomyLevel,
    ConfidenceAction,
    MemoryEntry,
    TrustLevel,
)


# ---------------------------------------------------------------------------
# 22 Constitutional Principles (from Prometheus V11 V11_DESIGN.md)
# ---------------------------------------------------------------------------

CONSTITUTION_PRINCIPLES: list[dict] = [
    {"id": "P2", "rule": "More memory can be worse", "source": "LongMINT"},
    {"id": "P3", "rule": "Write is a decision, not storage", "source": "D-MEM"},
    {"id": "P4", "rule": "Buffering > Error Correction", "source": "HSP90"},
    {"id": "P5", "rule": "Deterministic detection > LLM detection", "source": "impeccable"},
    {"id": "P7", "rule": "Zero-LLM lifecycle", "source": "Nautilus"},
    {"id": "P10", "rule": "Compile >> Online", "source": "general"},
    {"id": "P11", "rule": "Eval-Driven Evolution", "source": "ECC"},
    {"id": "P12", "rule": "Evidence Before Claims", "source": "superpowers"},
    {"id": "P14", "rule": "Constraints ≤ 7 + escape valve", "source": "CEF/CET"},
    {"id": "P20", "rule": "Five-gate chain", "source": "SAGE+MemGate"},
    {"id": "P22", "rule": "Trust must be earned, not assumed", "source": "general"},
    {"id": "P25", "rule": "Overconfidence is a system risk", "source": "CCSIL"},
    {"id": "P28", "rule": "Memory consolidation requires verification", "source": "general"},
    {"id": "P30", "rule": "Evolution must never regress", "source": "EDRE"},
    {"id": "P33", "rule": "Autonomy must have escape valves", "source": "general"},
    {"id": "P35", "rule": "Multi-source validation required", "source": "general"},
    {"id": "P38", "rule": "Deterministic rules preferred over learned", "source": "general"},
    {"id": "P40", "rule": "Code quality is non-negotiable", "source": "general"},
    {"id": "P42", "rule": "Every evolution must be auditable", "source": "general"},
    {"id": "P45", "rule": "Budget constraints are hard limits", "source": "general"},
    {"id": "P50", "rule": "Simplicity over complexity", "source": "general"},
    {"id": "P55", "rule": "Fail-safe, not fail-open", "source": "general"},
]


# ---------------------------------------------------------------------------
# Autonomy Levels (from Prometheus V8 autonomy.py)
# ---------------------------------------------------------------------------

AUTONOMY_RULES: dict[str, AutonomyLevel] = {
    "read_memory": AutonomyLevel.L0_FULL_AUTO,
    "write_memory": AutonomyLevel.L1_SEMI_AUTO,
    "delete_memory": AutonomyLevel.L2_CONFIRM,
    "evolve_code": AutonomyLevel.L2_CONFIRM,
    "modify_config": AutonomyLevel.L3_APPROVAL,
    "access_external_api": AutonomyLevel.L3_APPROVAL,
    "execute_arbitrary_code": AutonomyLevel.L4_FORBIDDEN,
    "modify_governance": AutonomyLevel.L4_FORBIDDEN,
    "self_replicate": AutonomyLevel.L4_FORBIDDEN,
}


class AutonomyManager:
    """5-level autonomy with frequency limiting and time windows."""

    def __init__(self) -> None:
        self._action_counts: dict[str, list[float]] = {}
        self._cooldowns: dict[str, float] = {}

    def check(self, action: str, current_level: AutonomyLevel) -> tuple[bool, str]:
        """Check if the current autonomy level permits the given action."""
        required = AUTONOMY_RULES.get(action, AutonomyLevel.L3_APPROVAL)

        if current_level.value < required.value:
            return False, f"Autonomy {current_level.name} insufficient for {action} (requires {required.name})"

        # Frequency limiting
        now = time.time()
        if action not in self._action_counts:
            self._action_counts[action] = []
        self._action_counts[action] = [t for t in self._action_counts[action] if now - t < AUTONOMY_FREQUENCY_WINDOW]
        if len(self._action_counts[action]) >= AUTONOMY_FREQUENCY_LIMIT:
            return False, f"Frequency limit exceeded for {action} (10/hour)"

        self._action_counts[action].append(now)
        return True, "approved"


# ---------------------------------------------------------------------------
# Trust Manager (from Prometheus V8 trust.py)
# ---------------------------------------------------------------------------

class TrustManager:
    """3-level trust: PENDING → HIGH_SIGNAL → VERIFIED."""

    def __init__(self) -> None:
        self._trust: dict[str, TrustLevel] = {}
        self._sources: dict[str, set[str]] = {}
        self._usage: dict[str, list[float]] = {}

    def get_trust(self, memory_id: str) -> TrustLevel:
        """Return the current trust level for a memory."""
        return self._trust.get(memory_id, TrustLevel.PENDING)

    def record_source(self, memory_id: str, source: str) -> TrustLevel:
        """Record an independent source and upgrade trust if threshold met."""
        if memory_id not in self._sources:
            self._sources[memory_id] = set()
        self._sources[memory_id].add(source)

        # Upgrade: 2+ independent sources → HIGH_SIGNAL
        if len(self._sources[memory_id]) >= TRUST_SOURCE_THRESHOLD:
            self._trust[memory_id] = TrustLevel.HIGH_SIGNAL
        return self.get_trust(memory_id)

    def record_usage(self, memory_id: str, success: bool) -> TrustLevel:
        """Record a successful usage to upgrade trust to VERIFIED."""
        if memory_id not in self._usage:
            self._usage[memory_id] = []
        self._usage[memory_id].append(time.time())

        # Upgrade: actual successful usage → VERIFIED
        if success and len(self._usage[memory_id]) >= 1:
            self._trust[memory_id] = TrustLevel.VERIFIED
        return self.get_trust(memory_id)

    def decay(self, max_age_days: int = 30) -> list[str]:
        """Decay trust for unused memories."""
        now = time.time()
        decayed = []
        for mid, level in list(self._trust.items()):
            if level == TrustLevel.VERIFIED:
                last_use = max(self._usage.get(mid, [0]))
                if (now - last_use) / 86400 > max_age_days:
                    self._trust[mid] = TrustLevel.HIGH_SIGNAL
                    decayed.append(mid)
        return decayed


# ---------------------------------------------------------------------------
# ConfidenceGate (from Prometheus V8 confidence_gate.py)
# ---------------------------------------------------------------------------

VERIFIABLE_CATEGORIES = {"code", "config", "prompt", "tool"}
NON_VERIFIABLE_CATEGORIES = {"strategy", "creative", "philosophy", "governance"}


class ConfidenceGate:
    """CCSIL-inspired confidence gate: overconfidence = system risk."""

    def evaluate(self, entry: MemoryEntry) -> ConfidenceAction:
        """Evaluate whether to proceed, ask, defer, or reject based on confidence."""
        category = entry.category.value

        if category in NON_VERIFIABLE_CATEGORIES:
            if entry.confidence < 0.9:
                return ConfidenceAction.DEFER

        if entry.confidence >= 0.8:
            return ConfidenceAction.PROCEED
        elif entry.confidence >= 0.5:
            return ConfidenceAction.ASK
        else:
            return ConfidenceAction.DEFER


# ---------------------------------------------------------------------------
# EvolutionGrill (from Prometheus V11 grill.py)
# ---------------------------------------------------------------------------

MANDATORY_QUESTIONS = [
    "Is this evolution truly necessary?",
    "Is there a simpler solution?",
    "What could this break?",
    "What is the rollback plan?",
    "Is the eval definition clear?",
    "What is the expected fitness delta?",
    "Does this align with EvolutionKnobs?",
]


class EvolutionGrill:
    """Relentless questioning with escalating standards.

    Enhanced with bidirectional clarification (from mattpocock/skills grill-me).
    Now supports: AI asks human → human answers → AI追问 → consensus.
    """

    def __init__(self) -> None:
        self._rounds = 0
        self._thresholds = GRILL_THRESHOLDS
        self._ai_questions: list[str] = []  # AI-generated questions for human
        self._human_answers: list[str] = []

    def grill(self, proposal: dict[str, str]) -> tuple[bool, list[str]]:
        """Multi-round interrogation. Each round raises the bar."""
        self._rounds += 1
        threshold = self._thresholds[min(self._rounds - 1, len(self._thresholds) - 1)]

        answers = []
        score = 0

        for q in MANDATORY_QUESTIONS:
            answer = proposal.get(q, "")
            if self._is_quality_answer(answer):
                score += 1
            answers.append(f"Q: {q}\nA: {answer or '[unanswered]'}")

        passed = score / len(MANDATORY_QUESTIONS) >= threshold
        if passed:
            self._rounds = 0  # Reset on success
        return passed, answers

    def ask_human(self, proposal: dict[str, str]) -> list[str]:
        """AI generates clarifying questions for the human (bidirectional grill).

        Source: mattpocock/skills grill-me — AI asks questions to eliminate ambiguity.
        """
        questions = []
        # Detect vagueness in proposal
        for key, value in proposal.items():
            if isinstance(value, str):
                if len(value) < 20:
                    questions.append(f"Can you clarify '{key}'? Current: '{value[:50]}'")
                if any(word in value.lower() for word in ["maybe", "probably", "not sure"]):
                    questions.append(f"('{key}' seems uncertain. What's the definitive answer?)")

        # Detect missing critical fields
        critical = ["task", "success_criteria", "rollback_plan"]
        for field_name in critical:
            if field_name not in proposal or not proposal.get(field_name):
                questions.append(f"Missing '{field_name}' — what is it?")

        self._ai_questions = questions
        return questions

    def receive_human_answer(self, answers: dict[str, str]) -> None:
        """Receive human answers to AI questions."""
        self._human_answers = [f"{k}: {v}" for k, v in answers.items()]

    def _is_quality_answer(self, answer: str) -> bool:
        """Multi-heuristic quality check, not just length."""
        if not answer or len(answer.strip()) < 5:
            return False

        quality_signals = 0

        if len(answer) > 30:
            quality_signals += 1

        if any(c.isdigit() for c in answer):
            quality_signals += 1

        tech_words = {"because", "therefore", "however", "specifically",
                      "algorithm", "function", "variable", "implementation",
                      "trade-off", "consider", "alternative", "approach"}
        if any(w in answer.lower() for w in tech_words):
            quality_signals += 1

        action_words = {"implement", "use", "add", "remove", "replace",
                        "optimize", "refactor", "test", "measure", "verify"}
        if any(w in answer.lower() for w in action_words):
            quality_signals += 1

        return quality_signals >= 2

    def reset(self) -> None:
        """Reset the grill round counter."""
        self._rounds = 0


# ---------------------------------------------------------------------------
# DriftDetector (from Prometheus V11 drift_detector.py)
# ---------------------------------------------------------------------------

class DriftDetector:
    """4-dimension drift detection: policy, behavior, performance, distribution."""

    def __init__(self) -> None:
        self._baselines: dict[str, float] = {}
        self._current: dict[str, float] = {}

    def update(self, dimension: str, value: float) -> None:
        """Update the current value for a drift dimension."""
        self._current[dimension] = value

    def set_baseline(self, dimension: str, value: float) -> None:
        """Set the baseline value for a drift dimension."""
        self._baselines[dimension] = value

    def detect(self, threshold: float = 0.2) -> dict[str, bool]:
        """Detect drift across all dimensions against their baselines."""
        drifts = {}
        for dim, baseline in self._baselines.items():
            current = self._current.get(dim, baseline)
            if baseline > 0:
                drift = abs(current - baseline) / baseline
                drifts[dim] = drift > threshold
            else:
                drifts[dim] = False
        return drifts


# ---------------------------------------------------------------------------
# Unified Governance Manager
# ---------------------------------------------------------------------------

class GovernanceManager:
    """Unified governance: constitution + autonomy + trust + confidence + grill + drift."""

    def __init__(self) -> None:
        self.principles = CONSTITUTION_PRINCIPLES
        self.autonomy = AutonomyManager()
        self.trust = TrustManager()
        self.confidence_gate = ConfidenceGate()
        self.grill = EvolutionGrill()
        self.drift = DriftDetector()

    def audit(self, entry: MemoryEntry, action: str) -> dict[str, Any]:
        """Full governance audit for a proposed action."""
        # Trust check
        trust = self.trust.get_trust(entry.id)

        # Autonomy check
        autonomy_ok, autonomy_msg = self.autonomy.check(action, entry.autonomy_level)

        # Confidence gate
        confidence_action = self.confidence_gate.evaluate(entry)

        # Constitution check
        principle_violations = []
        if entry.confidence < 0.3:
            principle_violations.append("P12: Evidence Before Claims")
        if entry.importance < 0.1:
            principle_violations.append("P3: Write is a decision, not storage")

        allowed = autonomy_ok and confidence_action == ConfidenceAction.PROCEED and not principle_violations

        return {
            "allowed": allowed,
            "trust": trust.value,
            "autonomy": autonomy_msg,
            "confidence": confidence_action.value,
            "violations": principle_violations,
        }
