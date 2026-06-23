"""Bandit — E5+E6: Thompson Sampling + UCB1 dual-armed bandit.

E5: Thompson Sampling for hyperparameter tuning (Beta distribution).
E6: UCB1 for strategy direction selection (Forward/Lateral/Reverse).

Both are explore-exploit balances:
- Thompson: Bayesian — sample from posterior, choose best sample
- UCB1: Frequentist — upper confidence bound = mean + sqrt(2*ln(t)/n)
"""
from __future__ import annotations

import math
import random

from prometheus_z.schema import ZConfig


class ThompsonBandit:
    """E5: Thompson Sampling bandit for hyperparameter tuning.

    Each arm represents a configuration option.
    Uses Beta(α, β) posterior — α = successes, β = failures.
    """

    def __init__(self, arms: list[str], config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._arms = arms
        self._alpha: dict[str, float] = {a: 1.0 for a in arms}
        self._beta: dict[str, float] = {a: 1.0 for a in arms}
        self._counts: dict[str, int] = {a: 0 for a in arms}
        self._total = 0

    def select(self) -> str:
        """Select an arm using Thompson Sampling.

        Sample from Beta(α, β) for each arm, choose the one with highest sample.
        """
        samples = {}
        for arm in self._arms:
            samples[arm] = random.betavariate(
                self._alpha[arm], self._beta[arm]
            )
        best = max(samples, key=samples.get)
        return best

    def update(self, arm: str, reward: float) -> None:
        """Update the posterior for the selected arm.

        reward ∈ [0, 1]: 0 = total failure, 1 = total success.
        """
        if arm not in self._arms:
            return
        self._alpha[arm] += reward
        self._beta[arm] += (1 - reward)
        self._counts[arm] += 1
        self._total += 1

    def get_best(self) -> str:
        """Get the arm with highest expected reward."""
        expected = {a: self._alpha[a] / (self._alpha[a] + self._beta[a])
                    for a in self._arms}
        return max(expected, key=expected.get)

    def get_distribution(self) -> dict[str, float]:
        """Get expected reward for each arm."""
        return {a: self._alpha[a] / (self._alpha[a] + self._beta[a])
                for a in self._arms}


class UCB1Bandit:
    """E6: UCB1 bandit for strategy direction selection.

    Arms: "forward", "lateral", "reverse"
    UCB1 = mean_reward + sqrt(2 * ln(total_count) / arm_count)
    """

    DIRECTIONS = ["forward", "lateral", "reverse"]

    def __init__(self, arms: list[str] | None = None,
                 config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._arms = arms or self.DIRECTIONS
        self._rewards: dict[str, list[float]] = {a: [] for a in self._arms}
        self._total = 0

    def select(self) -> str:
        """Select an arm using UCB1.

        For untried arms, priority exploration (infinite UCB1 when count=0).
        """
        # Try each arm at least once
        for arm in self._arms:
            if len(self._rewards[arm]) == 0:
                return arm

        # UCB1 formula
        ucb_values = {}
        for arm in self._arms:
            n = len(self._rewards[arm])
            mean = sum(self._rewards[arm]) / n
            ucb = mean + math.sqrt(2 * math.log(self._total) / n)
            ucb_values[arm] = ucb

        return max(ucb_values, key=ucb_values.get)

    def update(self, arm: str, reward: float) -> None:
        """Update reward for the selected arm."""
        if arm not in self._arms:
            return
        self._rewards[arm].append(reward)
        self._total += 1

    def get_best_direction(self) -> str:
        """Get the direction with highest average reward."""
        averages = {}
        for arm in self._arms:
            if self._rewards[arm]:
                averages[arm] = sum(self._rewards[arm]) / len(self._rewards[arm])
            else:
                averages[arm] = 0.0
        return max(averages, key=averages.get)

    def get_stats(self) -> dict[str, dict]:
        """Get stats for each arm."""
        stats = {}
        for arm in self._arms:
            rewards = self._rewards[arm]
            stats[arm] = {
                "count": len(rewards),
                "mean": sum(rewards) / len(rewards) if rewards else 0.0,
            }
        return stats
