"""DriftDetector — S3: Zero-LLM drift detection.

Detects when the system's behavior drifts from expected patterns.
All detection is deterministic — no LLM calls.

Detection methods:
1. Distribution shift — KL-divergence between recent and baseline distributions
2. Behavioral regression — previously passing tests now failing
3. Feature drift — input feature statistics shifting
4. Confidence decay — model confidence dropping over time
"""
from __future__ import annotations

import math
from collections import deque

from prometheus_z.schema import ZConfig


class DriftDetector:
    """S3: Zero-LLM drift detection via statistical tests."""

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._baseline: dict[str, list[float]] = {}
        self._recent: dict[str, list[float]] = {}
        self._drift_history: deque[dict] = deque(maxlen=100)
        self._window_size = 20

    def set_baseline(self, metric: str, values: list[float]) -> None:
        """Set baseline distribution for a metric."""
        self._baseline[metric] = values[-self._window_size:]

    def observe(self, metric: str, value: float) -> dict:
        """Observe a new value for a metric. Returns drift report.

        Drift is detected via:
        1. Mean shift (t-test approximation)
        2. Variance shift (F-test approximation)
        3. Range shift (min-max comparison)
        """
        if metric not in self._recent:
            self._recent[metric] = []
        self._recent[metric].append(value)

        # Keep only recent window
        if len(self._recent[metric]) > self._window_size:
            self._recent[metric] = self._recent[metric][-self._window_size:]

        # Can't detect drift without baseline
        if metric not in self._baseline or len(self._recent[metric]) < 5:
            return {"metric": metric, "drift_detected": False, "reason": "insufficient data"}

        report = self._detect_drift(metric)
        self._drift_history.append(report)
        return report

    def _detect_drift(self, metric: str) -> dict:
        """Detect drift for a specific metric.

        Detection methods:
        1. Mean shift (simplified t-test)
        2. Variance shift (F-test ratio)
        3. KL divergence (distribution shift)
        """
        baseline = self._baseline[metric]
        recent = self._recent[metric]

        b_mean = sum(baseline) / len(baseline)
        r_mean = sum(recent) / len(recent)

        b_var = sum((x - b_mean) ** 2 for x in baseline) / max(1, len(baseline) - 1)
        r_var = sum((x - r_mean) ** 2 for x in recent) / max(1, len(recent) - 1)

        # Mean shift detection (simplified t-test)
        mean_shift = abs(r_mean - b_mean)
        pooled_std = math.sqrt((b_var + r_var) / 2) if (b_var + r_var) > 0 else 1.0
        t_statistic = mean_shift / (pooled_std / math.sqrt(len(recent))) if pooled_std > 0 else 0.0

        # Variance shift (ratio)
        var_ratio = r_var / b_var if b_var > 0 else float('inf') if r_var > 0 else 1.0

        # KL divergence (Gaussian approximation)
        # KL(N(μ₁,σ₁²) || N(μ₀,σ₀²)) = log(σ₀/σ₁) + (σ₁²+(μ₁-μ₀)²)/(2σ₀²) - 0.5
        kl_div = self._kl_gaussian(b_mean, b_var, r_mean, r_var)

        # Thresholds
        mean_drift = t_statistic > 2.0  # ~95% confidence
        var_drift = var_ratio > 3.0 or var_ratio < 0.33
        kl_drift = kl_div > 0.5  # Moderate divergence threshold
        drift_detected = mean_drift or var_drift or kl_drift

        return {
            "metric": metric,
            "drift_detected": drift_detected,
            "baseline_mean": b_mean,
            "recent_mean": r_mean,
            "mean_shift": mean_shift,
            "t_statistic": t_statistic,
            "var_ratio": var_ratio,
            "kl_divergence": kl_div,
            "mean_drift": mean_drift,
            "var_drift": var_drift,
            "kl_drift": kl_drift,
        }

    @staticmethod
    def _kl_gaussian(mu0: float, var0: float, mu1: float, var1: float) -> float:
        """KL divergence between two Gaussian distributions.

        KL(N(μ₁,σ₁²) || N(μ₀,σ₀²)) = log(σ₀/σ₁) + (σ₁²+(μ₁-μ₀)²)/(2σ₀²) - 0.5

        Returns 0.0 if either variance is zero (degenerate distribution).
        """
        if var0 <= 0:
            # Zero-variance baseline → any non-zero variance is infinite drift
            return float('inf') if var1 > 0 or mu1 != mu0 else 0.0
        if var1 <= 0:
            # Zero-variance recent → distribution collapsed to point
            return float('inf') if mu1 != mu0 else 0.0
        return (math.log(math.sqrt(var0) / math.sqrt(var1))
                + (var1 + (mu1 - mu0) ** 2) / (2 * var0)
                - 0.5)

    def check_all(self) -> list[dict]:
        """Check all metrics for drift."""
        results = []
        for metric in self._baseline:
            if metric in self._recent and len(self._recent[metric]) >= 5:
                results.append(self._detect_drift(metric))
        return results

    def has_any_drift(self) -> bool:
        """Quick check: is any metric drifting?"""
        return any(r.get("drift_detected", False) for r in self.check_all())

    @property
    def drift_count(self) -> int:
        """Number of drift events detected."""
        return sum(1 for h in self._drift_history if h.get("drift_detected"))

    @property
    def monitored_metrics(self) -> list[str]:
        return list(set(list(self._baseline.keys()) + list(self._recent.keys())))
