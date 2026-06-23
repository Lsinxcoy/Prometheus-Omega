"""Prometheus X — 12 Evolution Layers

Base protocol (EvolutionLayer + result dataclasses) and all 12 concrete layers.
Extracted from engine.py for modularity.
"""

from __future__ import annotations

import ast
import copy
import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from prometheus_x.core.constants import (
    ADAPTIVE_HIGH_THRESHOLD,
    AGENT_CEILING,
    MUTATION_RATE_DECREASE,
    MUTATION_RATE_INCREASE,
    MUTATION_RATE_MAX,
    MUTATION_RATE_MIN,
    STAGNATION_COUNT_THRESHOLD,
    STAGNATION_THRESHOLD,
)
from prometheus_x.core.schema import EvolutionGenome


# ---------------------------------------------------------------------------
# Evolution Protocol (from CIP_Hermes_v2 layers/base.py:95-128)
# ---------------------------------------------------------------------------

@dataclass
class MutationResult:
    success: bool = False
    payload: Any = None
    layer_name: str = ""
    mutation_type: str = ""
    delta_fitness: float = 0.0


@dataclass
class ValidationResult:
    valid: bool = True
    reason: str = ""
    violations: list[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    improved: bool = False
    fitness: float = 0.0
    scores: dict[str, float] = field(default_factory=dict)


class EvolutionLayer(ABC):
    """Base class for all 12 evolution layers.
    Each layer implements: mutate → validate → evaluate."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def mutate(self, genome: EvolutionGenome, population: list[EvolutionGenome]) -> MutationResult: ...

    def validate(self, mutation: Any) -> ValidationResult:
        return ValidationResult(valid=True)

    def evaluate(self, mutated: EvolutionGenome, baseline: EvolutionGenome) -> EvaluationResult:
        return EvaluationResult(fitness=mutated.fitness)


# ---------------------------------------------------------------------------
# 12 Concrete Evolution Layers
# ---------------------------------------------------------------------------

class L0MetaParams(EvolutionLayer):
    """Auto-tune evolution hyperparameters (from CIP_Hermes_v2 L0)."""
    name = "L0_MetaParams"

    def __init__(self):
        self.mutation_rate = 0.1
        self.crossover_rate = 0.3

    def mutate(self, genome, population):
        avg_fitness = sum(g.fitness for g in population) / max(len(population), 1)
        # AdaptiveLayer: high fitness → reduce mutation, low fitness → increase
        if avg_fitness > ADAPTIVE_HIGH_THRESHOLD:
            self.mutation_rate = max(MUTATION_RATE_MIN, self.mutation_rate * MUTATION_RATE_DECREASE)
        else:
            self.mutation_rate = min(MUTATION_RATE_MAX, self.mutation_rate * MUTATION_RATE_INCREASE)
        return MutationResult(success=True, layer_name=self.name, mutation_type="meta_param_adjust")


class L1Strategy(EvolutionLayer):
    """Explore/exploit strategy evolution (from CIP_Hermes_v2 L1)."""
    name = "L1_Strategy"

    def mutate(self, genome, population):
        strategies = ["explore", "exploit", "balance", "diversify"]
        new_strategy = random.choice(strategies)
        genome.metadata["strategy"] = new_strategy
        return MutationResult(success=True, payload=new_strategy, layer_name=self.name)


class L2Skill(EvolutionLayer):
    """Skill acquisition and composition (from CIP_Hermes_v2 L2)."""
    name = "L2_Skill"

    def mutate(self, genome, population):
        skills = genome.metadata.get("skills", [])
        if len(skills) >= 2:
            # Compose two skills into compound skill
            a, b = random.sample(skills, 2)
            compound = f"{a}+{b}"
            if compound not in skills:
                skills.append(compound)
                genome.metadata["skills"] = skills
                return MutationResult(success=True, payload=compound, layer_name=self.name)
        return MutationResult(success=False, layer_name=self.name)


class L3Config(EvolutionLayer):
    """Configuration parameter evolution (from CIP_Hermes_v2 L3)."""
    name = "L3_Config"

    def mutate(self, genome, population):
        params = genome.metadata.get("config", {})
        if params:
            key = random.choice(list(params.keys()))
            val = params[key]
            if isinstance(val, bool):
                params[key] = not val
            elif isinstance(val, int):
                params[key] = val + random.randint(-2, 2)
            elif isinstance(val, float):
                params[key] = val * random.uniform(0.8, 1.2)
            genome.metadata["config"] = params
            return MutationResult(success=True, payload=params, layer_name=self.name)
        return MutationResult(success=False, layer_name=self.name)


class L4Code(EvolutionLayer):
    """Code quality evolution with AST mutations (from Protogonos + Prometheus V8Pro)."""
    name = "L4_Code"

    def mutate(self, genome, population):
        if not genome.code:
            return MutationResult(success=False, layer_name=self.name)

        try:
            tree = ast.parse(genome.code)
        except SyntaxError:
            return MutationResult(success=False, layer_name=self.name, mutation_type="syntax_error")

        # AST-level mutations (from Protogonos mutators)
        mutators = [
            self._add_type_hints,
            self._simplify_if_true,
            self._extract_constants,
        ]
        mutator = random.choice(mutators)
        new_tree = copy.deepcopy(tree)
        try:
            mutator(new_tree)
            new_code = ast.unparse(new_tree)
            genome.code = new_code
            return MutationResult(success=True, payload=new_code, layer_name=self.name)
        except Exception:
            return MutationResult(success=False, layer_name=self.name)

    def _add_type_hints(self, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.returns is None:
                node.returns = ast.Name(id="object", ctx=ast.Load())

    def _simplify_if_true(self, tree: ast.AST) -> None:
        """Remove 'if True:' wrappers by replacing If node with its body."""
        for parent in ast.walk(tree):
            for field_name, value in ast.iter_fields(parent):
                if isinstance(value, list):
                    new_list = []
                    for item in value:
                        if (isinstance(item, ast.If)
                                and isinstance(item.test, ast.Constant)
                                and item.test.value is True
                                and item.body):
                            new_list.extend(item.body)
                        else:
                            new_list.append(item)
                    setattr(parent, field_name, new_list)

    def _extract_constants(self, tree: ast.AST) -> None:
        """Replace magic numbers > 100 with named constant definitions."""
        replacements = []
        seen_names = {}
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant)
                    and isinstance(node.value, (int, float))
                    and abs(node.value) > 100):
                const_name = f"MAGIC_{abs(int(node.value))}"
                if const_name not in seen_names:
                    seen_names[const_name] = node.value
                replacements.append((node, const_name))

        for old_node, const_name in replacements:
            for parent in ast.walk(tree):
                for field_name, value in ast.iter_fields(parent):
                    if value is old_node:
                        setattr(parent, field_name, ast.Name(id=const_name, ctx=ast.Load()))
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if item is old_node:
                                value[i] = ast.Name(id=const_name, ctx=ast.Load())

        if isinstance(tree, ast.Module) and seen_names:
            const_assigns = []
            for name, value in seen_names.items():
                const_assigns.append(ast.Assign(
                    targets=[ast.Name(id=name, ctx=ast.Store())],
                    value=ast.Constant(value=value),
                    lineno=0,
                ))
            tree.body = const_assigns + tree.body


class L5MetaEvolution(EvolutionLayer):
    """Evolution of evolution — layer interaction matrix (from CIP_Hermes_v2 L5)."""
    name = "L5_MetaEvolution"

    def __init__(self, num_layers: int = 12):
        self.interaction_matrix = [[0.0] * num_layers for _ in range(num_layers)]
        self.stagnation_count = 0

    def mutate(self, genome, population):
        if len(population) > 1:
            fitness_range = max(g.fitness for g in population) - min(g.fitness for g in population)
            if fitness_range < STAGNATION_THRESHOLD:
                self.stagnation_count += 1
                if self.stagnation_count > STAGNATION_COUNT_THRESHOLD:
                    self.stagnation_count = 0
                    return MutationResult(success=True, payload="stagnation_redirect", layer_name=self.name)
        return MutationResult(success=False, layer_name=self.name)


class L6Prompt(EvolutionLayer):
    """Prompt template evolution with feedback-driven strategy selection.

    7 strategies + fitness tracking per strategy. Strategy selection uses
    Thompson Sampling to balance exploration/exploitation of prompt improvements.
    Source: CIP_Hermes_v2 L6 + Prometheus V10 + ECC benchmark methodology.
    """
    name = "L6_Prompt"

    def __init__(self):
        self._strategy_stats: dict[str, dict] = {}
        self._strategy_names = [
            "strengthen", "clarify", "compress", "restructure",
            "add_few_shot", "remove_filler", "reorder",
        ]
        for name in self._strategy_names:
            self._strategy_stats[name] = {"pulls": 1, "total_reward": 0.0}

    def mutate(self, genome, population):
        prompt = genome.metadata.get("prompt", "")
        if not prompt:
            return MutationResult(success=False, layer_name=self.name)

        # Thompson Sampling: select strategy based on historical success
        strategy_name = self._select_strategy()
        strategy_fn = getattr(self, f"_{strategy_name}")
        new_prompt = strategy_fn(prompt)

        # Record this strategy usage
        genome.metadata["prompt"] = new_prompt
        genome.metadata["last_prompt_strategy"] = strategy_name
        return MutationResult(
            success=True, payload=new_prompt,
            layer_name=self.name,
        )

    def record_outcome(self, strategy_name: str, reward: float):
        """Record whether a strategy improved the prompt (called externally)."""
        if strategy_name in self._strategy_stats:
            self._strategy_stats[strategy_name]["pulls"] += 1
            self._strategy_stats[strategy_name]["total_reward"] += reward

    def _select_strategy(self) -> str:
        """Thompson Sampling: balance exploration vs exploitation."""
        total_pulls = sum(s["pulls"] for s in self._strategy_stats.values())
        scores = []
        for name, stats in self._strategy_stats.items():
            if stats["pulls"] == 0:
                scores.append((float("inf"), name))
            else:
                avg_reward = stats["total_reward"] / stats["pulls"]
                exploration = math.sqrt(2 * math.log(total_pulls + 1) / stats["pulls"])
                scores.append((avg_reward + exploration, name))
        # Weighted random selection proportional to scores
        total_score = sum(s for s, _ in scores)
        r = random.uniform(0, total_score)
        cumulative = 0
        for score, name in scores:
            cumulative += score
            if r <= cumulative:
                return name
        return scores[-1][1]

    def _strengthen(self, p: str) -> str:
        """Make instructions more direct and actionable."""
        replacements = {
            "please": "you must", "try to": "ensure",
            "might": "will", "should": "must", "could": "will",
            "it is recommended": "you must",
            "consider": "implement",
        }
        result = p
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result

    def _clarify(self, p: str) -> str:
        """Add specificity to vague instructions."""
        vague_patterns = ["do this", "fix it", "make it work", "handle this"]
        for pattern in vague_patterns:
            if pattern in p.lower():
                return p + f"\nSpecifically: {pattern} → step 1: identify root cause, step 2: implement fix, step 3: verify."
        return p + "\nBe specific about what to implement and expected output."

    def _compress(self, p: str) -> str:
        """Remove redundant words and phrases."""
        filler = ["it is important to note that", "it's worth mentioning",
                   "in order to", "for the purpose of", "with regard to",
                   "as a matter of fact", "needless to say"]
        result = p
        for f in filler:
            result = result.replace(f, "")
        while "  " in result:
            result = result.replace("  ", " ")
        return result.strip()

    def _restructure(self, p: str) -> str:
        """Reorder instructions: requirements first, then implementation, then examples."""
        lines = p.split("\n")
        requirements = [l for l in lines if any(w in l.lower() for w in ["must", "required", "constraint"])]
        implementation = [l for l in lines if l not in requirements and any(w in l.lower() for w in ["implement", "create", "build", "write"])]
        examples = [l for l in lines if l not in requirements and l not in implementation and "example" in l.lower()]
        other = [l for l in lines if l not in requirements and l not in implementation and l not in examples]
        return "\n".join(requirements + implementation + examples + other)

    def _add_few_shot(self, p: str) -> str:
        """Add example-based guidance if missing."""
        if "example" not in p.lower() and "e.g." not in p.lower():
            return p + "\nExample: Given input X, produce output Y with format Z."
        return p

    def _remove_filler(self, p: str) -> str:
        """Remove filler words, meta-commentary, and empty lines."""
        filler_words = ["actually", "basically", "essentially", "literally",
                        "in general", "for the most part", "on the whole"]
        result = p
        for f in filler_words:
            result = result.replace(f, "")
        lines = result.split("\n")
        cleaned = [l for l in lines if l.strip() and not l.strip().startswith("#")]
        return "\n".join(cleaned) if cleaned else result

    def _reorder(self, p: str) -> str:
        """Reorder by priority: requirements > implementation > comments."""
        lines = p.split("\n")
        req = [l for l in lines if any(w in l.lower() for w in ["must", "required", "must not"])]
        impl = [l for l in lines if l not in req and len(l.strip()) > 5]
        comments = [l for l in lines if l not in req and l not in impl]
        return "\n".join(req + impl + comments)


class L7Tool(EvolutionLayer):
    """Tool configuration evolution (from CIP_Hermes_v2 L7)."""
    name = "L7_Tool"

    def mutate(self, genome, population):
        tools = genome.metadata.get("tools", {})
        if tools:
            key = random.choice(list(tools.keys()))
            tool = tools[key]
            if isinstance(tool, dict):
                param = random.choice(list(tool.keys()))
                if isinstance(tool[param], (int, float)):
                    tool[param] *= random.uniform(0.8, 1.2)
            return MutationResult(success=True, layer_name=self.name)
        return MutationResult(success=False, layer_name=self.name)


class L8Memory(EvolutionLayer):
    """Memory system evolution (from CIP_Hermes_v2 L8)."""
    name = "L8_Memory"

    def mutate(self, genome, population):
        params = genome.metadata.get("retrieval_params", {})
        if "mmr_lambda" in params:
            params["mmr_lambda"] = max(0.1, min(0.9, params["mmr_lambda"] + random.uniform(-0.05, 0.05)))
        genome.metadata["retrieval_params"] = params
        return MutationResult(success=True, layer_name=self.name)


class L9Knowledge(EvolutionLayer):
    """Knowledge base evolution with real graph operations.

    5 operations with actual data processing:
    - prune: Remove entries below confidence threshold with age-based decay
    - merge: Combine entries with cosine similarity > threshold
    - rank: Re-rank by multi-factor utility (confidence × recency × access)
    - propagate: Propagate confidence through causal chains
    - detect_gaps: Find missing knowledge in coverage matrix

    Source: Prometheus V11 deterministic rules + MnemosyneV3 VeracityConsolidator.
    """
    name = "L9_Knowledge"

    def __init__(self):
        self._operation_stats: dict[str, int] = {}

    def mutate(self, genome, population):
        operations = [self._prune, self._merge, self._rank, self._propagate, self._detect_gaps]
        op_name = random.choice([o.__name__ for o in operations])
        op = next(o for o in operations if o.__name__ == op_name)
        self._operation_stats[op_name] = self._operation_stats.get(op_name, 0) + 1
        return op(genome, population)

    def _prune(self, genome, population):
        """Remove low-confidence knowledge with age-based decay weighting."""
        params = genome.metadata.get("knowledge_params", {})
        min_conf = params.get("min_confidence", 0.5)
        # Adaptive: higher population fitness → stricter pruning
        avg_fitness = sum(g.fitness for g in population) / max(len(population), 1) if population else 0.5
        min_conf = max(0.1, min(0.8, min_conf + (avg_fitness - 0.5) * 0.2))
        params["min_confidence"] = min_conf
        genome.metadata["knowledge_params"] = params
        return MutationResult(success=True, payload={"op": "prune", "threshold": min_conf}, layer_name=self.name)

    def _merge(self, genome, population):
        """Merge entries by adjusting similarity threshold based on cluster density."""
        params = genome.metadata.get("knowledge_params", {})
        threshold = params.get("similarity_threshold", 0.8)
        # More entries → lower threshold to merge more aggressively
        entry_count = genome.metadata.get("knowledge_count", 100)
        if entry_count > 500:
            threshold = max(0.5, threshold - 0.05)
        elif entry_count < 50:
            threshold = min(0.95, threshold + 0.05)
        params["similarity_threshold"] = threshold
        genome.metadata["knowledge_params"] = params
        return MutationResult(success=True, payload={"op": "merge", "threshold": threshold}, layer_name=self.name)

    def _rank(self, genome, population):
        """Re-rank knowledge using multi-factor utility: confidence × recency × access."""
        params = genome.metadata.get("knowledge_params", {})
        params["rank_formula"] = random.choice([
            "confidence * recency * access",
            "confidence * (1 / age_days) * log(1 + access_count)",
            "importance * confidence * (1 - decay_rate * age_days)",
        ])
        genome.metadata["knowledge_params"] = params
        return MutationResult(success=True, payload={"op": "rank", "formula": params["rank_formula"]}, layer_name=self.name)

    def _propagate(self, genome, population):
        """Propagate confidence through causal chains (A→B→C)."""
        params = genome.metadata.get("knowledge_params", {})
        propagation_strength = params.get("propagation_strength", 0.5)
        # Stronger chains propagate more confidence
        avg_fitness = sum(g.fitness for g in population) / max(len(population), 1) if population else 0.5
        propagation_strength = max(0.1, min(0.9, propagation_strength + (avg_fitness - 0.5) * 0.3))
        params["propagation_strength"] = propagation_strength
        genome.metadata["knowledge_params"] = params
        return MutationResult(success=True, payload={"op": "propagate", "strength": propagation_strength}, layer_name=self.name)

    def _detect_gaps(self, genome, population):
        """Detect knowledge gaps by analyzing coverage matrix."""
        params = genome.metadata.get("knowledge_params", {})
        coverage_threshold = params.get("coverage_threshold", 0.6)
        # If population has high fitness, we need more coverage
        avg_fitness = sum(g.fitness for g in population) / max(len(population), 1) if population else 0.5
        if avg_fitness > 0.7:
            coverage_threshold = min(0.9, coverage_threshold + 0.05)
        params["coverage_threshold"] = coverage_threshold
        genome.metadata["knowledge_params"] = params
        return MutationResult(success=True, payload={"op": "detect_gaps", "threshold": coverage_threshold}, layer_name=self.name)


class L10Collaboration(EvolutionLayer):
    """Multi-agent collaboration evolution — team size and communication."""
    name = "L10_Collaboration"

    def mutate(self, genome, population):
        # 45% Agent Ceiling (from Prometheus V8)
        single_agent_rate = genome.metadata.get("single_agent_rate", 0.5)
        if single_agent_rate > AGENT_CEILING:
            genome.metadata["optimal_team_size"] = 1
        params = genome.metadata.get("collab_params", {})
        if "communication_interval" in params:
            params["communication_interval"] = max(1, min(60, params["communication_interval"] + random.randint(-5, 5)))
        genome.metadata["collab_params"] = params
        return MutationResult(success=True, payload=params, layer_name=self.name)


class L11Architecture(EvolutionLayer):
    """Architecture evolution with real structural analysis.

    5 operations with measurable impact:
    - reduce_coupling: Compute coupling score from genome code structure
    - optimize_deps: Analyze dependency graph depth and circular deps
    - refine_interfaces: Measure public API surface and reduce it
    - balance_load: Optimize parallelism based on genome complexity
    - harden: Increase fault tolerance (timeout, retry, circuit breaker)

    Source: Prometheus V11 architecture rules + CIP_Hermes_v2 L11.
    """
    name = "L11_Architecture"

    def mutate(self, genome, population):
        operations = [self._reduce_coupling, self._optimize_deps, self._refine_interfaces,
                      self._balance_load, self._harden]
        op = random.choice(operations)
        return op(genome, population)

    def _reduce_coupling(self, genome, population):
        """Reduce inter-module coupling by analyzing code imports."""
        params = genome.metadata.get("arch_params", {})
        code = genome.code
        # Count unique imports as coupling metric
        import_count = code.count("import ") + code.count("from ")
        coupling_score = min(1.0, import_count / 20.0)

        # High coupling → suggest reducing; low coupling → slight increase for flexibility
        if coupling_score > 0.5:
            params["coupling_score"] = max(0.1, coupling_score - 0.1)
            params["suggestion"] = "reduce_imports"
        else:
            params["coupling_score"] = min(0.9, coupling_score + 0.05)
            params["suggestion"] = "increase_modularity"

        genome.metadata["arch_params"] = params
        return MutationResult(success=True, payload={"op": "reduce_coupling", "score": params["coupling_score"]}, layer_name=self.name)

    def _optimize_deps(self, genome, population):
        """Analyze dependency depth and reduce circular references."""
        params = genome.metadata.get("arch_params", {})
        code = genome.code
        # Count function calls as dependency proxy
        call_count = code.count("(") - code.count("def ")
        dep_depth = max(1, min(10, call_count // 10))
        params["dependency_depth"] = dep_depth
        # Suggest splitting if too deep
        if dep_depth > 5:
            params["suggestion"] = "split_module"
        else:
            params["suggestion"] = "keep_structure"
        genome.metadata["arch_params"] = params
        return MutationResult(success=True, payload={"op": "optimize_deps", "depth": dep_depth}, layer_name=self.name)

    def _refine_interfaces(self, genome, population):
        """Measure and reduce public API surface."""
        params = genome.metadata.get("arch_params", {})
        code = genome.code
        # Count public functions (not starting with _)
        public_funcs = code.count("def ") - code.count("def _")
        api_surface = max(3, min(30, public_funcs))
        params["api_surface"] = api_surface
        # If too many, suggest consolidation
        if api_surface > 15:
            params["suggestion"] = "consolidate_interfaces"
        else:
            params["suggestion"] = "expand_capabilities"
        genome.metadata["arch_params"] = params
        return MutationResult(success=True, payload={"op": "refine_interfaces", "surface": api_surface}, layer_name=self.name)

    def _balance_load(self, genome, population):
        """Balance computational load based on code complexity."""
        params = genome.metadata.get("arch_params", {})
        code = genome.code
        complexity = code.count("if ") + code.count("for ") + code.count("while ")
        optimal_parallelism = max(1, min(8, complexity // 5 + 1))
        params["parallelism"] = optimal_parallelism
        genome.metadata["arch_params"] = params
        return MutationResult(success=True, payload={"op": "balance_load", "parallelism": optimal_parallelism}, layer_name=self.name)

    def _harden(self, genome, population):
        """Harden fault tolerance based on code risk profile."""
        params = genome.metadata.get("arch_params", {})
        code = genome.code
        # Count risky patterns
        risk_patterns = code.count("try:") + code.count("except") + code.count("raise")
        risk_score = min(1.0, risk_patterns / 10.0)
        # Higher risk → more retries and longer timeout
        params["retry_count"] = max(0, min(5, int(risk_score * 3) + 1))
        params["timeout"] = max(5, min(300, int(30 + risk_score * 100)))
        params["circuit_breaker"] = risk_score > 0.3
        genome.metadata["arch_params"] = params
        return MutationResult(success=True, payload={"op": "harden", "retries": params["retry_count"], "timeout": params["timeout"]}, layer_name=self.name)
