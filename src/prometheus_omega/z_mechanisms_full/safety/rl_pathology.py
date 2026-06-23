"""RLPathology — S7: RL pathology detection (zero-LLM).

Detects common reinforcement learning pathologies:
1. Reward hacking — agent gaming the reward function
2. Distribution collapse — all actions converging to one
3. Catastrophic forgetting — old skills degrading
4. Exploration collapse — no new strategies tried
5. Oscillation — alternating between strategies without convergence
6. Policy degeneration — policy becoming deterministic too early
"""
from __future__ import annotations

import math
from collections import deque

from prometheus_z.schema import ZConfig

class RLPathologyDetector:
    """S7: Detect RL pathologies in evolution dynamics."""

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._reward_history: deque[float] = deque(maxlen=500)
        self._action_distribution: dict[str, int] = {}
        self._skill_history: dict[str, deque[float]] = {}
        self._exploration_history: deque[float] = deque(maxlen=500)
        self._pathologies: deque[dict] = deque(maxlen=100)

    def observe(self, reward: float, action: str = "",
                skills: dict[str, float] | None = None,
                exploration_rate: float = 1.0) -> list[dict]:
        """Observe a step and check for pathologies.

        Returns list of detected pathologies (empty if healthy).
        """
        self._reward_history.append(reward)
        if action:
            self._action_distribution[action] = self._action_distribution.get(action, 0) + 1
        if skills:
            for skill, fitness in skills.items():
                if skill not in self._skill_history:
                    self._skill_history[skill] = deque(maxlen=500)
                self._skill_history[skill].append(fitness)
        self._exploration_history.append(exploration_rate)

        detected = []
        if self._check_reward_hacking():
            detected.append({"pathology": "reward_hacking",
                           "description": "Reward increasing without real improvement"})
        if self._check_distribution_collapse():
            detected.append({"pathology": "distribution_collapse",
                           "description": "Actions converging to single strategy"})
        if self._check_catastrophic_forgetting():
            detected.append({"pathology": "catastrophic_forgetting",
                           "description": "Previously strong skills degrading"})
        if self._check_exploration_collapse():
            detected.append({"pathology": "exploration_collapse",
                           "description": "No new strategies being tried"})
        if self._check_oscillation():
            detected.append({"pathology": "oscillation",
                           "description": "Alternating strategies without convergence"})
        if self._check_policy_degeneration():
            detected.append({"pathology": "policy_degeneration",
                           "description": "Policy collapsed to near-deterministic"})

        self._pathologies.extend(detected)
        return detected

    def _check_reward_hacking(self, window: int = 10) -> bool:
        """Reward going up but skills not improving."""
        if len(self._reward_history) < window * 2:
            return False
        rh = list(self._reward_history)
        recent_reward = sum(rh[-window:]) / window
        old_reward = sum(rh[-2*window:-window]) / window
        # Reward increasing but no skill improvement
        if recent_reward > old_reward * 1.2:
            for skill, history in self._skill_history.items():
                if len(history) >= window:
                    hl = list(history)
                    recent_skill = sum(hl[-window:]) / window
                    old_skill = sum(hl[-2*window:-window]) / window if len(hl) >= 2*window else recent_skill
                    if recent_skill < old_skill * 0.9:
                        return True
        return False

    def _check_distribution_collapse(self, threshold: float = 0.8) -> bool:
        """One action dominates > threshold of all actions."""
        total = sum(self._action_distribution.values())
        if total < 10:
            return False
        max_count = max(self._action_distribution.values())
        return (max_count / total) > threshold

    def _check_catastrophic_forgetting(self, threshold: float = 0.5) -> bool:
            """Previously strong skill (fitness > 0.7) now below threshold."""
            for skill, history in self._skill_history.items():
                if len(history) >= 10:
                    hl = list(history)
                    peak = max(hl[:len(hl)//2])  # First half peak
                    recent = min(hl[-5:])  # Recent minimum
                    if peak > 0.7 and recent < threshold:
                        return True
            return False

    def _check_exploration_collapse(self, threshold: float = 0.05) -> bool:
        """Exploration rate dropped below threshold."""
        if len(self._exploration_history) < 10:
            return False
        recent = sum(list(self._exploration_history)[-5:]) / 5
        return recent < threshold

    def _check_oscillation(self, window: int = 10) -> bool:
        """Reward oscillating without convergence."""
        if len(self._reward_history) < window:
            return False
        recent = list(self._reward_history)[-window:]
        diffs = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
        sign_changes = sum(1 for i in range(len(diffs)-1)
                         if (diffs[i] > 0) != (diffs[i+1] > 0))
        # More than 60% sign changes = oscillation
        return sign_changes > len(diffs) * 0.6

    def _check_policy_degeneration(self, threshold: float = 0.95) -> bool:
        """Policy becoming deterministic too early — entropy too low.

        Measures action distribution entropy. If near-zero (highly concentrated),
        the policy has collapsed to deterministic behavior prematurely.
        """
        total = sum(self._action_distribution.values())
        if total < 20:  # Need enough observations
            return False
        n_actions = len(self._action_distribution)
        if n_actions <= 1:
            return True  # Only one action = fully degenerate
        # Compute Shannon entropy
        entropy = 0.0
        for count in self._action_distribution.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        # Maximum entropy = log2(n_actions)
        max_entropy = math.log2(n_actions)
        if max_entropy == 0:
            return False
        # Normalized entropy: 1 = uniform, 0 = deterministic
        normalized = entropy / max_entropy
        return normalized < (1 - threshold)  # Below 5% of max = degenerate

    @property
    def pathology_count(self) -> int:
        return len(self._pathologies)

    @property
    def pathologies(self) -> list[dict]:
        return list(self._pathologies)

    @property
    def is_healthy(self) -> bool:
        """No pathologies detected in recent observations.

        Checks whether the last N observations detected any pathologies,
        not whether the entire history is empty (which would always return True).
        """
        if not self._pathologies:
            return True
        # Check if the most recent observation detected anything
        # (pathologies list grows over time; only recent ones matter)
        recent_pathologies = list(self._pathologies)[-5:]
        return len([p for p in recent_pathologies if p]) == 0
