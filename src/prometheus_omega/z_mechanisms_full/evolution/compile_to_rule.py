"""CompileToRule — E11: Deterministic compilation of high-fitness patterns.

When a pattern's fitness > 0.95, it graduates from probabilistic reasoning
to deterministic execution. This is the "compile" step in the evolution pipeline.

Compiled rules:
- Never re-evaluate (saves computation)
- Never drift (deterministic guarantee)
- Can be audited (written as explicit code/config)

P-01: Uses md5 for rule fingerprints, not hash().
"""
from __future__ import annotations

import hashlib

from prometheus_z.schema import Node, NodeType, TrustLevel, ZConfig
from prometheus_z.store.store import MinervaStore


class CompileToRule:
    """E11: Compile high-fitness patterns to deterministic rules."""

    def __init__(self, store: MinervaStore, config: ZConfig | None = None):
        self._store = store
        self._config = config or ZConfig()
        self._compiled_rules: dict[str, dict] = {}

    def compile(self, pattern: Node, fitness: float,
                branch: str = "main") -> Node | None:
        """Compile a pattern to a deterministic rule if fitness > threshold.

        Args:
            pattern: The pattern to compile
            fitness: Current fitness score (0-1)
            branch: Memory branch

        Returns:
            The compiled rule node, or None if fitness too low.
        """
        if fitness < self._config.compile_fitness_threshold:
            return None  # Not ready for compilation

        # Create a deterministic rule node
        rule_fingerprint = hashlib.md5(
            pattern.content.encode()
        ).hexdigest()

        rule = Node(
            content=f"RULE: {pattern.content} (fitness={fitness:.3f})",
            type=NodeType.AVOID_RULE,  # Rules are deterministic
            utility=5.0,  # Max utility for compiled rules
            layer=2,  # SEMANTIC — permanent
            trust=TrustLevel.VERIFIED,
            reinforce_count=pattern.reinforce_count,
            surprise=0.0,  # No surprise — deterministic
            parent_id=pattern.id,
            branch=branch,
            custom_type="compiled_rule",
        )

        rule_id = self._store._system_insert(rule, reason="compile_to_rule")

        # Track in compiled rules registry
        self._compiled_rules[rule_fingerprint] = {
            "rule_id": rule_id,
            "pattern_id": pattern.id,
            "fitness": fitness,
            "content": rule.content,
        }

        return rule

    def is_compiled(self, pattern_id: str) -> bool:
        """Check if a pattern has been compiled to a rule."""
        for rule_info in self._compiled_rules.values():
            if rule_info["pattern_id"] == pattern_id:
                return True
        return False

    def get_rule(self, pattern_id: str) -> dict | None:
        """Get the compiled rule for a pattern."""
        for rule_info in self._compiled_rules.values():
            if rule_info["pattern_id"] == pattern_id:
                return rule_info
        return None

    @property
    def compiled_count(self) -> int:
        return len(self._compiled_rules)

    @property
    def compiled_rules(self) -> dict[str, dict]:
        return dict(self._compiled_rules)
