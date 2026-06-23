"""VariantPool — S10: Maintain diverse solution variants.

Prevents convergence to local optima by maintaining a pool of
diverse solution variants. Each variant has:
- code: the solution
- fitness: measured fitness score
- lineage: where it came from
- age: how long it's been in the pool

Pool management:
- Add new variants from evolution
- Cull low-fitness variants when pool is full
- Select variants for next evolution round (diversity-aware)
"""
from __future__ import annotations

import hashlib
import time

from prometheus_z.schema import ZConfig


class Variant:
    """A single solution variant."""

    __slots__ = ("id", "code", "fitness", "lineage", "age", "added_at")

    def __init__(self, code: str, fitness: float = 0.0,
                 lineage: str = ""):
        self.id = hashlib.md5(code.encode()).hexdigest()[:12]
        self.code = code
        self.fitness = fitness
        self.lineage = lineage
        self.age = 0
        self.added_at = time.time()


class VariantPool:
    """S10: Diverse solution variant pool."""

    def __init__(self, max_size: int = 50, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._max_size = max_size
        self._variants: dict[str, Variant] = {}
        self._stats = {"added": 0, "culled": 0, "selected": 0}

    def add(self, code: str, fitness: float = 0.0,
            lineage: str = "") -> str:
        """Add a variant to the pool. Returns variant ID.

        If pool is full, cull the lowest-fitness variant.
        """
        variant = Variant(code, fitness, lineage)
        vid = variant.id

        if vid in self._variants:
            # Update existing variant's fitness
            self._variants[vid].fitness = max(
                self._variants[vid].fitness, fitness
            )
            return vid

        if len(self._variants) >= self._max_size:
            self._cull()

        self._variants[vid] = variant
        self._stats["added"] += 1
        return vid

    def select(self, n: int = 3, diversity_weight: float = 0.3) -> list[Variant]:
        """Select n variants for next evolution round.

        Selection balances fitness and diversity:
        - score = fitness * (1 - diversity_weight) + diversity * diversity_weight
        - diversity = average distance to other selected variants
        """
        if not self._variants:
            return []

        variants = sorted(self._variants.values(),
                         key=lambda v: v.fitness, reverse=True)
        selected: list[Variant] = [variants[0]]  # Start with best

        while len(selected) < min(n, len(variants)):
            best_score = -1.0
            best_variant = None

            for v in variants:
                if v in selected:
                    continue

                # Diversity: average distance to already-selected
                diversity = self._diversity(v, selected)
                score = (v.fitness * (1 - diversity_weight) +
                        diversity * diversity_weight)

                if score > best_score:
                    best_score = score
                    best_variant = v

            if best_variant:
                selected.append(best_variant)
            else:
                break

        self._stats["selected"] += len(selected)
        return selected

    def _diversity(self, variant: Variant,
                   others: list[Variant]) -> float:
        """Compute diversity of a variant relative to a set of others.

        Uses normalized edit distance approximation.
        """
        if not others:
            return 1.0

        total_dist = 0.0
        for other in others:
            # Simple character-level distance (normalized)
            if variant.code == other.code:
                total_dist += 0.0
            else:
                # Jaccard similarity of character bigrams
                a_bigrams = set(variant.code[i:i+2]
                              for i in range(len(variant.code)-1))
                b_bigrams = set(other.code[i:i+2]
                              for i in range(len(other.code)-1))
                if not a_bigrams and not b_bigrams:
                    total_dist += 0.0
                elif not a_bigrams or not b_bigrams:
                    total_dist += 1.0
                else:
                    jaccard = len(a_bigrams & b_bigrams) / len(a_bigrams | b_bigrams)
                    total_dist += 1.0 - jaccard

        return total_dist / len(others)

    def _cull(self) -> None:
        """Remove the lowest-fitness variant."""
        if not self._variants:
            return
        worst_id = min(self._variants, key=lambda k: self._variants[k].fitness)
        del self._variants[worst_id]
        self._stats["culled"] += 1

    def age_all(self) -> None:
        """Increment age of all variants."""
        for v in self._variants.values():
            v.age += 1

    @property
    def size(self) -> int:
        return len(self._variants)

    @property
    def best_fitness(self) -> float:
        if not self._variants:
            return 0.0
        return max(v.fitness for v in self._variants.values())

    @property
    def average_fitness(self) -> float:
        if not self._variants:
            return 0.0
        return sum(v.fitness for v in self._variants.values()) / len(self._variants)

    @property
    def stats(self) -> dict:
        return dict(self._stats)
