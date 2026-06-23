"""VerificationIronLaw — Iron Law 3: 5-step verification gate.

Steps (mandatory, no skipping):
1. IDENTIFY — what is the claim?
2. RUN — execute the test/experiment
3. READ — collect the output
4. VERIFY — compare output against expected (no should/probably/seems)
5. APPLY — if verified, apply the change

Rejected words: "should", "probably", "seems", "likely", "might"
Only hard evidence passes.
"""
from __future__ import annotations

import re

from prometheus_z.schema import EvolutionCheckResult, ZConfig


class VerificationIronLaw:
    """Iron Law 3: 5-step verification gate.

    Rejects fuzzy claims. Only concrete evidence passes.
    """

    # Words that indicate fuzzy/unverified claims
    FUZZY_WORDS = {"should", "probably", "seems", "likely", "might",
                   "maybe", "perhaps", "possibly", "approximately",
                   "roughly", "guess", "assume", "presumably"}

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._stats = {"verified": 0, "rejected_fuzzy": 0,
                       "rejected_no_evidence": 0, "rejected_no_improvement": 0}

    def verify(self, claim: str, evidence: dict,
               threshold: float = 0.9,
               direction: str = "maximize") -> EvolutionCheckResult:
        """Run 5-step verification.

        Args:
            claim: What is being claimed (e.g., "improves search accuracy")
            evidence: Dict with "before" and "after" numeric values
            threshold: Minimum improvement ratio to accept (0.0-1.0)
            direction: "maximize" (higher=better) or "minimize" (lower=better)

        Returns:
            EvolutionCheckResult — check .passed, NOT truthiness.
        """
        # Step 1: IDENTIFY — what is the claim?
        if not claim:
            return EvolutionCheckResult(passed=False, reason="No claim identified")

        # Step 1b: Check for fuzzy words
        if self._contains_fuzzy_words(claim):
            self._stats["rejected_fuzzy"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"FUZZY: Claim contains unverified language: '{claim}'",
            )

        # Step 2-3: RUN + READ — check evidence exists
        if not evidence:
            self._stats["rejected_no_evidence"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason="NO_EVIDENCE: No evidence provided",
            )

        before = evidence.get("before", 0.0)
        after = evidence.get("after", 0.0)

        if before is None or after is None:
            self._stats["rejected_no_evidence"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason="NO_EVIDENCE: Missing 'before' or 'after' in evidence",
            )

        # Step 4: VERIFY — is the improvement real and significant?
        if direction == "maximize":
            improved = after > before
            improvement = after - before
        else:  # "minimize"
            improved = after < before
            improvement = before - after  # Positive = good for minimize

        if not improved:
            self._stats["rejected_no_improvement"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"NO_IMPROVEMENT: {before:.3f} → {after:.3f} "
                       f"(direction={direction})",
            )

        # Relative improvement check
        baseline = abs(before) if abs(before) > 1e-9 else 1.0
        relative_improvement = improvement / baseline
        if relative_improvement < (1 - threshold):
            self._stats["rejected_no_improvement"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"INSUFFICIENT: relative improvement {relative_improvement:.3f} "
                       f"< threshold {(1-threshold):.3f}",
            )

        # Step 5: APPLY — verification passed
        self._stats["verified"] += 1
        return EvolutionCheckResult(
            passed=True,
            reason=f"VERIFIED: {before:.3f} → {after:.3f} "
                   f"(Δ={improvement:.3f}, direction={direction})",
        )

    def verify_claim_text(self, claim_text: str) -> EvolutionCheckResult:
        """Check if a text claim uses fuzzy language.

        Useful for verifying LLM outputs before trusting them.
        """
        if self._contains_fuzzy_words(claim_text):
            fuzzy = self._find_fuzzy_words(claim_text)
            self._stats["rejected_fuzzy"] += 1
            return EvolutionCheckResult(
                passed=False,
                reason=f"FUZZY: Found unverified words: {fuzzy}",
            )
        return EvolutionCheckResult(passed=True, reason="No fuzzy words detected")

    def _contains_fuzzy_words(self, text: str) -> bool:
        """Check if text contains any fuzzy words."""
        words = set(text.lower().split())
        return bool(words & self.FUZZY_WORDS)

    def _find_fuzzy_words(self, text: str) -> list[str]:
        """Find all fuzzy words in text."""
        words = set(text.lower().split())
        return sorted(words & self.FUZZY_WORDS)

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    @property
    def fuzzy_rejection_rate(self) -> float:
        total = sum(self._stats.values())
        if total == 0:
            return 0.0
        return self._stats["rejected_fuzzy"] / total
