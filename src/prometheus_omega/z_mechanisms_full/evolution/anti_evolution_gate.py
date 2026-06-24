"""AntiEvolutionGate — Iron Law 2: 4 prerequisites for evolution.

Evolution is denied unless ALL 4 prerequisites pass:
1. DEDUP: Is this a novel insight? (not already attempted)
2. INSIGHT: Does it provide genuine new understanding?
3. APPLICATION: Can it be applied to improve something?
4. CONSECUTIVE_GAIN: Will it produce consecutive improvement?

Any failure = silent rejection (no half-measures).
"""
from __future__ import annotations

from prometheus_z.schema import EvolutionCheckResult, ZConfig


class AntiEvolutionGate:
    """Iron Law 2: 4 prerequisites for evolution.

    Prevents:
    - Duplicate evolution attempts
    - Evolution without understanding
    - Evolution without application
    - Evolution that doesn't compound
    """

    # Persist attempted hypotheses to a special node type
    _ATTEMPTED_NODE_TYPE = "_evolution_attempted"

    def __init__(self, config: ZConfig | None = None,
                 store: 'MinervaStore | None' = None):
        self._config = config or ZConfig()
        self._store = store
        self._attempted: set[str] = set()
        self._stats = {"dedup_rejected": 0, "insight_rejected": 0,
                       "application_rejected": 0, "consecutive_rejected": 0,
                       "passed": 0}

    def _load_attempted(self) -> None:
        """Load previously attempted hypotheses from store (persistence)."""
        if self._store is None:
            return
        try:
            nodes = self._store.get_all_nodes("main", limit=100000)
            for n in nodes:
                if n.custom_type == self._ATTEMPTED_NODE_TYPE:
                    self._attempted.add(n.content)
        except Exception:
            pass  # Store not available yet

    def _persist_attempted(self, hypothesis: str) -> None:
        """Persist an attempted hypothesis to store."""
        if self._store is None:
            return
        try:
            from prometheus_z.schema import Node, NodeType
            node = Node(
                content=hypothesis,
                type=NodeType.CONCEPT,
                utility=0.0,  # System node, no dopamine value
                custom_type=self._ATTEMPTED_NODE_TYPE,
            )
            self._store._system_insert(node, reason="anti_evolution_gate")
        except Exception:
            pass  # Best-effort persistence

    def gate_check(self, hypothesis: str,
              existing_solutions: list[str] | None = None) -> EvolutionCheckResult:
        """Check all 4 prerequisites. Returns EvolutionCheckResult.

        Alias: check() for backward compatibility.

        P-27: Check .passed, NOT truthiness.
        """
        # Lazy-load persisted hypotheses on first check
        if self._store and not self._attempted:
            self._load_attempted()

        existing = existing_solutions or []

        # Prerequisite 1: DEDUP — novel insight?
        if hypothesis in existing or hypothesis in self._attempted:
            self._stats["dedup_rejected"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"DEDUP: '{hypothesis}' already attempted",
            )

        # Prerequisite 2: INSIGHT — provides new understanding?
        if not self._has_insight(hypothesis):
            self._stats["insight_rejected"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"INSIGHT: '{hypothesis}' doesn't provide new understanding",
            )

        # Prerequisite 3: APPLICATION — can be applied?
        if not self._has_application(hypothesis):
            self._stats["application_rejected"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"APPLICATION: '{hypothesis}' cannot be applied",
            )

        # Prerequisite 4: CONSECUTIVE_GAIN — compounds?
        if not self._has_consecutive_gain(hypothesis):
            self._stats["consecutive_rejected"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"CONSECUTIVE_GAIN: '{hypothesis}' won't compound",
            )

        self._attempted.add(hypothesis)
        self._persist_attempted(hypothesis)
        self._stats["passed"] += 1
        return EvolutionCheckResult(
            passed=True,
            reason="All 4 prerequisites passed",
        )

    def _has_insight(self, hypothesis: str) -> bool:
        """Prerequisite 2: Does the hypothesis provide genuine insight?

        Heuristic: must contain at least one specific technical term
        (not just vague statements like "improve things").
        """
        # Vague phrases that lack insight
        vague = {"improve", "better", "fix", "optimize", "enhance", "things", "stuff"}
        words = set(hypothesis.lower().split())

        # Must have at least one specific (non-vague) word
        specific = words - vague
        return len(specific) > 0

    def _has_application(self, hypothesis: str) -> bool:
        """Prerequisite 3: Can the hypothesis be applied?

        Heuristic: must describe a concrete change, not just an observation.
        """
        # Must have at least 3 words (not trivial)
        return len(hypothesis.split()) >= 3

    def _has_consecutive_gain(self, hypothesis: str) -> bool:
        """Prerequisite 4: Will the hypothesis compound?

        Heuristic: must not be a one-off fix. Must describe a pattern
        that can repeat and improve over time.
        """
        # One-off indicators
        one_off = {"once", "temporary", "one-time", "quick fix", "workaround"}
        hypothesis_lower = hypothesis.lower()
        for phrase in one_off:
            if phrase in hypothesis_lower:
                return False
        return True

    def reset(self) -> None:
        """Reset attempted hypotheses (for new evolution cycle)."""
        self._attempted.clear()

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    @property
    def rejection_rate(self) -> float:
        total = sum(self._stats.values())
        if total == 0:
            return 0.0
        rejections = total - self._stats["passed"]
        return rejections / total

    # Backward compatibility alias
    check = gate_check
