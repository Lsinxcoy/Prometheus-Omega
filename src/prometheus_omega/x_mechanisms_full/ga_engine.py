"""Prometheus X — 12-Layer Evolution Engine

Unified mutate→validate→evaluate protocol with UCB1 Bandit selection,
AdaptiveLayer meta-evolution, Island parallel, and 3-direction evolution.
Sources: CIP_Hermes_v2 layers/ + Prometheus V9 UCB1 + V10 speculative + V4 AST.
"""

from __future__ import annotations

import random

from prometheus_x.core.constants import (
    LATERAL_PROBABILITY,
    REVERSE_MIN_AGE,
    REVERSE_PROBABILITY,
)
from prometheus_x.core.schema import EvolutionGenome
from prometheus_x.evolution.layers import (
    EvolutionLayer,
    L0MetaParams,
    L1Strategy,
    L2Skill,
    L3Config,
    L4Code,
    L5MetaEvolution,
    L6Prompt,
    L7Tool,
    L8Memory,
    L9Knowledge,
    L10Collaboration,
    L11Architecture,
)
from prometheus_x.evolution.strategies import (
    ForwardDirection,
    IslandEvolution,
    LateralDirection,
    ReverseDirection,
    UCB1Bandit,
)


class EvolutionEngine:
    """Unified evolution engine combining all mechanisms."""

    def __init__(self, num_islands: int = 4) -> None:
        # All 12 layers
        self.layers: list[EvolutionLayer] = [
            L0MetaParams(), L1Strategy(), L2Skill(), L3Config(),
            L4Code(), L5MetaEvolution(), L6Prompt(), L7Tool(),
            L8Memory(), L9Knowledge(), L10Collaboration(), L11Architecture(),
        ]

        # UCB1 Bandit for layer selection
        self.bandit = UCB1Bandit([l.name for l in self.layers])

        # Island parallel
        self.island = IslandEvolution(self.layers, num_islands=num_islands)

        # 3-direction
        self.forward = ForwardDirection()
        self.lateral = LateralDirection()
        self.reverse = ReverseDirection()

        # Stats
        self.generation = 0
        self.total_mutations = 0
        self.successful_mutations = 0

    def evolve(self, population: list[EvolutionGenome]) -> list[EvolutionGenome]:
        """Run one evolution cycle: bandit selection → mutation → island parallel."""
        self.generation += 1

        # UCB1 selects which layer to focus on
        selected_layer_name = self.bandit.select()
        selected_layer = next(l for l in self.layers if l.name == selected_layer_name)

        # Apply mutations
        for genome in population:
            # Forward (primary)
            result = self.forward.apply(genome, [selected_layer])
            if result.success:
                self.successful_mutations += 1
            self.total_mutations += 1

            # Lateral (exploration)
            if random.random() < LATERAL_PROBABILITY:
                self.lateral.apply(genome, self.layers)

            # Reverse (simplification when stuck)
            if genome.age > REVERSE_MIN_AGE and random.random() < REVERSE_PROBABILITY:
                self.reverse.apply(genome)

            genome.age += 1

        # Update bandit reward
        avg_fitness = sum(g.fitness for g in population) / max(len(population), 1)
        self.bandit.update(selected_layer_name, avg_fitness)

        return population

    def stats(self) -> dict:
        """Return evolution statistics including generation and mutation rates."""
        return {
            "generation": self.generation,
            "total_mutations": self.total_mutations,
            "success_rate": self.successful_mutations / max(self.total_mutations, 1),
            "bandit_stats": {k: v["pulls"] for k, v in self.bandit._stats.items()},
        }
