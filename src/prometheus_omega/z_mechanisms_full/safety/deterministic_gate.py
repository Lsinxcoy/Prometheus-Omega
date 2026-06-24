"""DeterministicGate — S8: Deterministic pre-check before LLM calls.

Prevents unnecessary LLM calls by checking deterministic rules first.
If a rule matches, use the deterministic result (zero LLM cost, zero latency).
Only fall through to LLM if no rule matches.

Rules are compiled from CompileToRule (E11) — patterns with fitness > 0.95.

Pattern formats:
- Simple: "key:value" — exact match
- Wildcard: "key:*" — any value
- Combined: "key1:val1&key2:val2" — ALL conditions must match (AND)
- Negation: "key:!value" — match when value is NOT equal
- Range: "key:1..10" — numeric range (inclusive)
"""
from __future__ import annotations

from prometheus_z.schema import ZConfig


class DeterministicGate:
    """S8: Deterministic rule gate — skip LLM when rules suffice."""

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._rules: dict[str, tuple[str, int]] = {}  # pattern → (action, priority)
        self._stats = {"rule_hits": 0, "llm_fallbacks": 0}

    def register_rule(self, pattern: str, action: str,
                      priority: int = 0) -> None:
        """Register a deterministic rule.

        pattern: condition to match (e.g., "error_type:KeyError")
        action: deterministic response (e.g., "add_key_check")
        priority: higher priority rules are checked first (default 0)
        """
        self._rules[pattern] = (action, priority)

    def check(self, context: dict) -> tuple[bool, str | None]:
        """Check if a deterministic rule matches the context.

        Returns (rule_matched, action_or_none).
        If rule_matched=True, use the action (zero LLM).
        If rule_matched=False, fall through to LLM.

        Rules are checked in priority order (highest first).
        """
        # Sort by priority descending
        sorted_rules = sorted(self._rules.items(),
                             key=lambda x: x[1][1], reverse=True)

        for pattern, (action, _priority) in sorted_rules:
            if self._matches(pattern, context):
                self._stats["rule_hits"] += 1
                return True, action

        self._stats["llm_fallbacks"] += 1
        return False, None

    def check_all(self, context: dict) -> list[tuple[str, str]]:
        """Check all matching rules (not just the first).

        Returns [(pattern, action), ...] for all matching rules,
        sorted by priority descending.
        """
        sorted_rules = sorted(self._rules.items(),
                             key=lambda x: x[1][1], reverse=True)

        matches = []
        for pattern, (action, _priority) in sorted_rules:
            if self._matches(pattern, context):
                matches.append((pattern, action))
        return matches

    def _matches(self, pattern: str, context: dict) -> bool:
        """Check if a pattern matches the context.

        Pattern format supports:
        - Simple: "key:value"
        - Wildcard: "key:*"
        - Combined: "key1:val1&key2:val2" (AND)
        - Negation: "key:!value"
        - Range: "key:1..10"
        """
        # Combined patterns (AND logic)
        if "&" in pattern:
            parts = pattern.split("&")
            return all(self._matches_single(part, context) for part in parts)

        return self._matches_single(pattern, context)

    def _matches_single(self, pattern: str, context: dict) -> bool:
        """Match a single key:value pattern."""
        if ":" not in pattern:
            return pattern in str(context)

        key, value = pattern.split(":", 1)
        if key not in context:
            return False

        actual = str(context[key])

        # Wildcard
        if value == "*":
            return True

        # Negation
        if value.startswith("!"):
            return actual != value[1:]

        # Range (e.g., "1..10")
        if ".." in value:
            try:
                low, high = value.split("..")
                num = float(actual)
                return float(low) <= num <= float(high)
            except (ValueError, TypeError):
                return False

        # Exact match
        return actual == value

    def get_rules(self) -> dict[str, str]:
        """Get all registered rules (pattern → action, priority omitted)."""
        return {p: a for p, (a, _pr) in self._rules.items()}

    def remove_rule(self, pattern: str) -> bool:
        """Remove a rule. Returns True if it existed."""
        if pattern in self._rules:
            del self._rules[pattern]
            return True
        return False

    @property
    def rule_count(self) -> int:
        return len(self._rules)

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    @property
    def hit_rate(self) -> float:
        total = self._stats["rule_hits"] + self._stats["llm_fallbacks"]
        if total == 0:
            return 0.0
        return self._stats["rule_hits"] / total
