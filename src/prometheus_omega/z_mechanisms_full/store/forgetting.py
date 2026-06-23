"""Weibull forgetting — M7: 5-layer memory with distinct decay parameters.

Each memory layer has different Weibull parameters:
- WORKING: fast decay (λ=30 days, k=0.7) — short-term scratchpad
- EPISODIC: medium decay (λ=90 days, k=0.8) — event memories
- SEMANTIC: slow decay (λ=365 days, k=1.5) — consolidated knowledge

Weibull CDF: F(t) = 1 - exp(-(t/λ)^k)
Retention: R(t) = exp(-(t/λ)^k)
Freshness: f(t) = exp(-age/λ)  (simplified for gravity formula)
"""
from __future__ import annotations

import math

from prometheus_z.schema import MemoryLayer, Node, ZConfig


class WeibullForgetting:
    """M7: Weibull forgetting curve per memory layer."""

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._lambdas = self._config.weibull_lambda
        self._ks = self._config.weibull_k

    def retention(self, node: Node, now: float | None = None) -> float:
        """Compute retention probability for a node.

        R(t) = exp(-(age/λ)^k)

        Returns value in [0, 1]. 1.0 = fully retained, 0.0 = fully forgotten.
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

    def freshness(self, node: Node, now: float | None = None) -> float:
        """Compute freshness for gravity formula.

        freshness = exp(-age_days / λ)

        Simpler than full Weibull — used in memory metabolism gravity formula.
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

    def should_forget(self, node: Node, threshold: float = 0.1,
                      now: float | None = None) -> bool:
        """Check if a node should be forgotten (retention below threshold)."""
        return self.retention(node, now) < threshold

    def decay_utility(self, node: Node, now: float | None = None) -> float:
        """Apply time-based utility decay.

        Utility decays by retention factor. This is the M2 mechanism:
        reference +2 / 30 days -1 / <3 delete (zero LLM).
        """
        ret = self.retention(node, now)
        return node.utility * ret
