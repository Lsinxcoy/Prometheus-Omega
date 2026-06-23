"""pass@k — E3: Mathematical sampling-based evaluation.

pass@k = 1 - C(n-c, k) / C(n, k)

Where:
- n = total samples
- c = correct samples
- k = number of samples to draw

This is the EXACT formula from Codex paper, not an approximation.
3 raters: Code (deterministic) + Model (LLM) + Human (manual).
"""
from __future__ import annotations

import math

from prometheus_z.schema import ZConfig


def pass_at_k(n: int, c: int, k: int = 1) -> float:
    """E3: Exact pass@k estimation.

    pass@k = 1 - C(n-c, k) / C(n, k)

    Special cases:
    - c = 0: pass@k = 0 (no correct samples)
    - c = n: pass@k = 1 (all correct)
    - k > n-c: pass@k = 1 (can't avoid correct samples)
    """
    if n == 0:
        return 0.0
    if c == 0:
        return 0.0
    if c == n:
        return 1.0
    if k > n - c:
        return 1.0

    # Use log-space to avoid overflow for large n
    # C(n-c, k) / C(n, k) = prod_{i=0}^{k-1} (n-c-i) / (n-i)
    ratio = 1.0
    for i in range(k):
        ratio *= (n - c - i) / (n - i)
    return 1.0 - ratio


class PassKEvaluator:
    """E3: pass@k evaluation with multi-rater scoring."""

    RATER_WEIGHTS = {"code": 0.4, "model": 0.4, "human": 0.2}

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._results: list[dict] = []

    def evaluate(self, solution: str, test_fn=None,
                 n_samples: int = 10, k: int = 1) -> dict:
        """Evaluate a solution using pass@k.

        Args:
            solution: The code/solution to evaluate
            test_fn: Callable that returns True if solution passes
            n_samples: Number of samples to run
            k: pass@k parameter

        Returns:
            Dict with pass_at_k value and rater scores
        """
        if test_fn is None:
            return {"pass_at_k": 0.0, "n": 0, "c": 0, "k": k}

        # Run n samples
        correct = 0
        for _ in range(n_samples):
            try:
                if test_fn(solution):
                    correct += 1
            except Exception:
                pass  # Failed sample

        pk = pass_at_k(n_samples, correct, k)

        result = {
            "pass_at_k": pk,
            "n": n_samples,
            "c": correct,
            "k": k,
            "threshold": self._config.pass_k_threshold,
            "passed": pk >= self._config.pass_k_threshold,
        }

        self._results.append(result)
        return result

    def multi_rater_score(self, code_score: float,
                          model_score: float,
                          human_score: float = 0.0) -> float:
        """Weighted multi-rater score.

        code: deterministic test (weight 0.4)
        model: LLM judgment (weight 0.4)
        human: manual review (weight 0.2)
        """
        w = self.RATER_WEIGHTS
        return (w["code"] * code_score +
                w["model"] * model_score +
                w["human"] * human_score)

    @property
    def results(self) -> list[dict]:
        return list(self._results)
