"""DeterministicRuleEngine — D12: 44 deterministic rules for zero-LLM decisions.

These rules replace LLM calls for well-known patterns.
Every rule is a (condition, action) pair with zero ambiguity.

Categories:
1. Error handling rules (1-10)
2. Memory lifecycle rules (11-20)
3. Evolution gate rules (21-30)
4. Search optimization rules (31-40)
5. Safety override rules (41-44)

All rules are zero-LLM — no model calls needed.
"""
from __future__ import annotations

from prometheus_z.schema import ZConfig


class DeterministicRuleEngine:
    """D12: 44 deterministic rules for common decisions.

    Zero-LLM by design — every rule maps condition → action deterministically.
    """

    # All 44 rules as (id, condition_key, condition_value, action)
    RULES = [
        # Error handling (1-10)
        (1, "error_type", "KeyError", "add_key_check"),
        (2, "error_type", "IndexError", "add_bounds_check"),
        (3, "error_type", "TypeError", "add_type_validation"),
        (4, "error_type", "ValueError", "add_value_validation"),
        (5, "error_type", "AttributeError", "add_attribute_check"),
        (6, "error_type", "ImportError", "add_import_fallback"),
        (7, "error_type", "FileNotFoundError", "add_file_check"),
        (8, "error_type", "PermissionError", "add_permission_check"),
        (9, "error_type", "TimeoutError", "add_timeout_retry"),
        (10, "error_type", "ConnectionError", "add_connection_retry"),
        # Memory lifecycle (11-20)
        (11, "memory_age", "old", "schedule_consolidation"),
        (12, "memory_age", "stale", "schedule_forgetting"),
        (13, "memory_utility", "zero", "mark_for_deletion"),
        (14, "memory_utility", "high", "promote_to_semantic"),
        (15, "memory_access", "frequent", "increase_reinforcement"),
        (16, "memory_access", "rare", "decrease_reinforcement"),
        (17, "memory_duplicate", "yes", "merge_duplicates"),
        (18, "memory_contradiction", "yes", "flag_for_review"),
        (19, "memory_orphan", "yes", "connect_to_nearest"),
        (20, "memory_stale", "yes", "apply_forgetting_curve"),
        # Evolution gate (21-30)
        (21, "evolution_duplicate", "yes", "reject_dedup"),
        (22, "evolution_insight", "none", "reject_no_insight"),
        (23, "evolution_application", "none", "reject_no_application"),
        (24, "evolution_consecutive", "none", "reject_no_consecutive"),
        (25, "evolution_fitness", "declining", "rollback"),
        (26, "evolution_fitness", "stagnant", "redirect"),
        (27, "evolution_compiled", "yes", "skip_reevaluation"),
        (28, "evolution_phase", "exploration", "allow_diverse"),
        (29, "evolution_phase", "exploitation", "allow_refinement"),
        (30, "evolution_phase", "cooldown", "pause"),
        # Search optimization (31-40)
        (31, "search_result", "empty", "expand_query"),
        (32, "search_result", "too_many", "narrow_query"),
        (33, "search_result", "irrelevant", "adjust_weights"),
        (34, "search_type", "exact", "use_fts5"),
        (35, "search_type", "semantic", "use_vector"),
        (36, "search_type", "hybrid", "use_rrf"),
        (37, "search_scope", "local", "use_cache"),
        (38, "search_scope", "global", "use_full_index"),
        (39, "search_freshness", "recent", "filter_by_time"),
        (40, "search_freshness", "any", "no_time_filter"),
        # Safety override (41-44)
        (41, "safety_alert", "red", "halt_evolution"),
        (42, "safety_alert", "orange", "pause_evolution"),
        (43, "safety_alert", "yellow", "log_warning"),
        (44, "safety_override", "emergency", "reset_to_last_stable"),
    ]

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._rule_map: dict[tuple[str, str], str] = {}
        self._stats = {"hits": 0, "misses": 0}
        self._build_rule_map()

    def _build_rule_map(self) -> None:
        """Build lookup map from rules."""
        for rule_id, condition_key, condition_value, action in self.RULES:
            self._rule_map[(condition_key, condition_value)] = action

    def evaluate(self, context: dict) -> str | None:
        """Evaluate context against all rules.

        Returns the action of the first matching rule, or None.
        Zero-LLM guaranteed.
        """
        for (key, value), action in self._rule_map.items():
            if key in context and str(context[key]) == value:
                self._stats["hits"] += 1
                return action

        self._stats["misses"] += 1
        return None

    def evaluate_all(self, context: dict) -> list[str]:
        """Evaluate context against all rules, return all matching actions."""
        actions = []
        for (key, value), action in self._rule_map.items():
            if key in context and str(context[key]) == value:
                actions.append(action)
        self._stats["hits"] += len(actions)
        if not actions:
            self._stats["misses"] += 1
        return actions

    def get_rule(self, rule_id: int) -> tuple | None:
        """Get a specific rule by ID."""
        for r in self.RULES:
            if r[0] == rule_id:
                return r
        return None

    def get_rules_by_category(self, category: str) -> list[tuple]:
        """Get rules by category name."""
        ranges = {
            "error_handling": (1, 10),
            "memory_lifecycle": (11, 20),
            "evolution_gate": (21, 30),
            "search_optimization": (31, 40),
            "safety_override": (41, 44),
        }
        if category not in ranges:
            return []
        lo, hi = ranges[category]
        return [r for r in self.RULES if lo <= r[0] <= hi]

    @property
    def rule_count(self) -> int:
        return len(self.RULES)

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    @property
    def hit_rate(self) -> float:
        total = self._stats["hits"] + self._stats["misses"]
        if total == 0:
            return 0.0
        return self._stats["hits"] / total
