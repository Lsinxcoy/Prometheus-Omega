"""LotkaVolterra — E8: Ecological dynamics for skill coexistence.

du/dt = r·u·(1 - u/K) + Σ α_ij·u_i·u_j

Where:
- u = skill population (fitness)
- r = intrinsic growth rate
- K = carrying capacity
- α_ij = interaction coefficient (positive=mutualism, negative=competition)

This prevents:
1. Runaway skill growth (carrying capacity)
2. Skill extinction (mutualism support)
3. Oscillation (predator-prey dynamics detection)
"""
from __future__ import annotations

import math

from prometheus_z.schema import ZConfig


class LotkaVolterraEngine:
    """E8: Ecological dynamics for multi-skill coexistence."""

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._populations: dict[str, float] = {}
        self._interactions: dict[tuple[str, str], float] = {}

    def register_skill(self, name: str, initial_fitness: float = 0.5) -> None:
        """Register a skill with its initial population."""
        self._populations[name] = initial_fitness

    def set_interaction(self, skill_a: str, skill_b: str,
                        coefficient: float) -> None:
        """Set interaction coefficient between two skills.

        Positive = mutualism (both benefit)
        Negative = competition (one suffers)
        Zero = neutral
        """
        self._interactions[(skill_a, skill_b)] = coefficient
        self._interactions[(skill_b, skill_a)] = coefficient

    def step(self, dt: float = 0.1) -> dict[str, float]:
        """Evolve all skill populations by one time step.

        Returns updated populations.
        """
        if not self._populations:
            return {}

        K = 1.0  # Carrying capacity (normalized fitness)
        r = 0.1  # Growth rate

        deltas: dict[str, float] = {}
        for skill, u in self._populations.items():
            # Logistic growth: r·u·(1 - u/K)
            growth = r * u * (1 - u / K)

            # Interaction: Σ α_ij · u_i · u_j
            interaction = 0.0
            for (a, b), alpha in self._interactions.items():
                if a == skill and b in self._populations:
                    interaction += alpha * u * self._populations[b]

            deltas[skill] = (growth + interaction) * dt

        # Apply updates
        for skill, delta in deltas.items():
            self._populations[skill] = max(0.0, min(1.0,
                                         self._populations[skill] + delta))

        return dict(self._populations)

    def detect_oscillation(self, history: list[dict[str, float]],
                           window: int = 10) -> bool:
        """Detect predator-prey oscillation in recent history.

        Returns True if oscillation detected (sign of Δ alternates ≥3 times).
        """
        if len(history) < window:
            return False

        recent = history[-window:]
        skills = list(self._populations.keys())
        if not skills:
            return False

        # Check first skill for oscillation
        skill = skills[0]
        values = [h.get(skill, 0.0) for h in recent if skill in h]
        if len(values) < 4:
            return False

        # Count sign changes in differences
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        sign_changes = sum(1 for i in range(len(diffs)-1)
                         if (diffs[i] > 0) != (diffs[i+1] > 0))

        return sign_changes >= 3

    def check_equilibrium(self, epsilon: float = 0.001) -> bool:
        """Check if system is at Nash equilibrium.

        Simple check: all populations stable (Δ < epsilon).
        step() is destructive (modifies _populations), so we snapshot first.
        """
        before = dict(self._populations)
        after = self.step(dt=0.01)
        for skill in before:
            if abs(after.get(skill, 0.0) - before[skill]) > epsilon:
                return False
        return True

    def get_population(self, skill: str) -> float:
        """Get current fitness of a skill."""
        return self._populations.get(skill, 0.0)

    @property
    def populations(self) -> dict[str, float]:
        return dict(self._populations)

    @property
    def interaction_count(self) -> int:
        return len(self._interactions)
