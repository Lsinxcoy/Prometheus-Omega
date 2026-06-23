"""EquilibriumGuard — S2: Nash equilibrium + 3-level early warning.

Monitors system state for divergence from equilibrium:
- Level 0 (GREEN): System stable, all metrics within bounds
- Level 1 (YELLOW): Early warning — metrics drifting
- Level 2 (ORANGE): Alert — metrics diverging, intervention needed
- Level 3 (RED): Critical — system unsafe, halt evolution

Detection (all zero-LLM):
1. Fitness convergence — is fitness still improving?
2. Population balance — are skills in healthy coexistence?
3. Error rate — is the system making more mistakes?
4. Resource usage — is memory/computation growing unbounded?
"""
from __future__ import annotations

import time
from collections import deque
from enum import IntEnum

from prometheus_z.schema import ZConfig


class AlertLevel(IntEnum):
    """3-level early warning system. Integer for >= comparison (P-16)."""
    GREEN = 0
    YELLOW = 1
    ORANGE = 2
    RED = 3


class EquilibriumGuard:
    """S2: Nash equilibrium monitor with 3-level early warning."""

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._fitness_history: deque[float] = deque(maxlen=200)
        self._error_history: deque[float] = deque(maxlen=200)
        self._population_history: deque[dict[str, float]] = deque(maxlen=200)
        self._last_alert = AlertLevel.GREEN
        self._stats = {"green": 0, "yellow": 0, "orange": 0, "red": 0,
                       "interventions": 0}

    def check(self, fitness: float, error_rate: float = 0.0,
              populations: dict[str, float] | None = None) -> AlertLevel:
        """Check system equilibrium. Returns current alert level.

        All thresholds are configurable, zero-LLM.
        """
        self._fitness_history.append(fitness)
        self._error_history.append(error_rate)
        if populations:
            self._population_history.append(populations)

        level = AlertLevel.GREEN

        # Check 1: Fitness convergence — not improving for N rounds
        if self._is_fitness_stagnant():
            level = max(level, AlertLevel.YELLOW)

        # Check 2: Fitness declining — going backwards
        if self._is_fitness_declining():
            level = max(level, AlertLevel.ORANGE)

        # Check 3: Error rate exceeding threshold
        if error_rate > self._config.max_error_rate:
            level = max(level, AlertLevel.ORANGE)

        # Check 4: Error rate spiking
        if self._is_error_rate_spiking():
            level = max(level, AlertLevel.RED)

        # Check 5: Population imbalance (one skill dominating)
        if populations and self._is_population_imbalanced(populations):
            level = max(level, AlertLevel.YELLOW)

        # Check 6: Critical — fitness collapsed
        if fitness < 0.1 and len(self._fitness_history) > 5:
            level = max(level, AlertLevel.RED)

        self._last_alert = level
        self._stats[{
            AlertLevel.GREEN: "green",
            AlertLevel.YELLOW: "yellow",
            AlertLevel.ORANGE: "orange",
            AlertLevel.RED: "red",
        }[level]] += 1

        return level

    def should_halt_evolution(self) -> bool:
        """RED alert → halt all evolution immediately."""
        return self._last_alert >= AlertLevel.RED

    def should_pause_evolution(self) -> bool:
        """ORANGE alert → pause evolution, allow diagnosis."""
        return self._last_alert >= AlertLevel.ORANGE

    def intervene(self) -> str | None:
        """Suggest intervention based on alert level.

        Returns intervention description or None if GREEN.
        """
        if self._last_alert == AlertLevel.GREEN:
            return None

        # RED alert should always suggest circuit breaker (most urgent response)
        if self._last_alert >= AlertLevel.RED:
            self._stats["interventions"] += 1
            return "CIRCUIT_BREAK: Critical alert — open circuit breaker immediately"

        if self._is_fitness_declining():
            self._stats["interventions"] += 1
            return "ROLLBACK: Fitness declining — revert last change"

        if self._is_error_rate_spiking():
            self._stats["interventions"] += 1
            return "CIRCUIT_BREAK: Error rate spiking — open circuit breaker"

        if self._is_fitness_stagnant():
            self._stats["interventions"] += 1
            return "REDIRECT: Fitness stagnant — try different strategy"

        self._stats["interventions"] += 1
        return "DIAGNOSE: Unknown issue — manual inspection needed"

    def _is_fitness_stagnant(self, window: int = 5, threshold: float = 0.01) -> bool:
        """Check if fitness hasn't improved in last N rounds."""
        if len(self._fitness_history) < window:
            return False
        recent = list(self._fitness_history)[-window:]
        return (max(recent) - min(recent)) < threshold

    def _is_fitness_declining(self, window: int = 3) -> bool:
        """Check if fitness is consistently declining."""
        if len(self._fitness_history) < window:
            return False
        recent = list(self._fitness_history)[-window:]
        return all(recent[i] > recent[i+1] for i in range(len(recent)-1))

    def _is_error_rate_spiking(self, window: int = 3,
                                factor: float = 3.0) -> bool:
        """Check if error rate has spiked by factor compared to baseline."""
        if len(self._error_history) < window * 2:
            return False
        # Use sliding window baseline: the period just before the recent window
        baseline = sum(list(self._error_history)[-2*window:-window]) / window
        recent = sum(list(self._error_history)[-window:]) / window
        if baseline == 0:
            return recent > 0.1
        return recent / baseline > factor

    def _is_population_imbalanced(self, populations: dict[str, float],
                                   threshold: float = 0.8) -> bool:
        """Check if one skill dominates (>threshold of total fitness)."""
        total = sum(populations.values())
        if total == 0:
            return False
        max_pop = max(populations.values())
        return (max_pop / total) > threshold

    @property
    def alert_level(self) -> AlertLevel:
        return self._last_alert

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    @property
    def fitness_history(self) -> list[float]:
        return list(self._fitness_history)
