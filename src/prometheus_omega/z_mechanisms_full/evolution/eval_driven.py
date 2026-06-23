"""EvalDrivenEngine — E2: 7-step evaluation-driven evolution.

Steps:
1. GRILL — 4 questions about what to improve
2. DEFINE_EVAL — define how to measure improvement
3. WRITE_PLAN — write a concrete change plan
4. EXECUTE — execute the plan
5. GRADE — grade the result against the eval
6. APPLY — if grade > threshold, apply the change
7. COMPILE — if fitness > 0.95, compile to deterministic rule

Iron Law 2 (AntiEvolutionGate) enforces prerequisites before step 1.
Iron Law 3 (VerificationIronLaw) enforces 5-step verification in step 5.
"""
from __future__ import annotations

import time

from prometheus_z.schema import (
    EvolutionCheckResult, EvolutionOutcome, ZConfig,
)
from prometheus_z.evolution.anti_evolution_gate import AntiEvolutionGate
from prometheus_z.evaluation.iron_law import VerificationIronLaw


class EvalDrivenEngine:
    """E2: 7-step evaluation-driven evolution pipeline."""

    def __init__(self, config: ZConfig | None = None,
                 store: 'MinervaStore | None' = None):
        self._config = config or ZConfig()
        self._gate = AntiEvolutionGate(self._config, store=store)
        self._iron_law = VerificationIronLaw(self._config)
        self._history: list[dict] = []

    def evolve(self, context: dict) -> EvolutionOutcome:
        """Run 7-step evolution pipeline.

        context must contain:
        - "weakness": what to improve (str)
        - "current_code": the code to evolve (str)
        - "eval_fn": callable that returns fitness score (0-1)
        - "apply_fn": callable that applies the change (optional)
        """
        weakness = context.get("weakness", "")
        current_code = context.get("current_code", "")
        eval_fn = context.get("eval_fn")
        apply_fn = context.get("apply_fn")

        if not weakness or not eval_fn:
            return EvolutionOutcome(applied=False, reason="Missing weakness or eval_fn")

        # ── Iron Law 2: AntiEvolutionGate ──
        gate_result = self._gate.check(
            hypothesis=weakness,
            existing_solutions=self._get_existing_solutions(),
        )
        if not gate_result.passed:
            return EvolutionOutcome(
                applied=False,
                reason=f"AntiEvolutionGate denied: {gate_result.reason}",
            )

        # ── Step 1: GRILL ──
        grill_answers = self._grill(weakness, current_code)

        # ── Step 2: DEFINE_EVAL ──
        eval_definition = self._define_eval(weakness, grill_answers)

        # ── Step 3: WRITE_PLAN ──
        plan = self._write_plan(weakness, grill_answers, eval_definition)

        # ── Step 4: EXECUTE ──
        fitness_before = eval_fn(current_code)
        modified_code = self._execute_plan(current_code, plan)

        # ── Step 5: GRADE (Iron Law 3: VerificationIronLaw) ──
        fitness_after = eval_fn(modified_code)

        # Determine direction from eval definition
        direction = eval_definition.get("direction", "maximize")

        # Verify improvement
        verification = self._iron_law.verify(
            claim=f"Change improves {weakness}",
            evidence={"before": fitness_before, "after": fitness_after},
            threshold=self._config.pass_k_threshold,
            direction=direction,
        )
        if not verification.passed:
            return EvolutionOutcome(
                applied=False,
                reason=f"VerificationIronLaw denied: {verification.reason}",
                fitness_before=fitness_before,
                fitness_after=fitness_after,
            )

        # ── Step 6: APPLY ──
        direction = context.get("direction", "maximize")
        if direction == "minimize":
            should_apply = fitness_after < fitness_before
        else:
            should_apply = fitness_after > fitness_before

        if should_apply:
            if apply_fn:
                apply_fn(modified_code)

            # ── Step 7: COMPILE ──
            compiled = fitness_after > self._config.compile_fitness_threshold

            outcome = EvolutionOutcome(
                applied=True,
                reason=f"Improved {weakness}: {fitness_before:.3f} → {fitness_after:.3f}",
                fitness_before=fitness_before,
                fitness_after=fitness_after,
                compilation=compiled,
            )

            self._history.append({
                "weakness": weakness,
                "fitness_before": fitness_before,
                "fitness_after": fitness_after,
                "applied": True,
                "compiled": compiled,
                "timestamp": time.time(),
            })

            return outcome

        return EvolutionOutcome(
            applied=False,
            reason=f"No improvement: {fitness_before:.3f} → {fitness_after:.3f}",
            fitness_before=fitness_before,
            fitness_after=fitness_after,
        )

    def _grill(self, weakness: str, code: str) -> dict:
        """Step 1: 4 questions about what to improve.

        Analyzes the weakness string and code to produce structured insights.
        Zero-LLM: uses heuristic analysis, not model calls.
        """
        # Parse weakness into components
        parts = weakness.lower().split()
        
        # Identify category from keywords
        categories = {
            "search": "retrieval_quality",
            "accuracy": "precision",
            "speed": "performance",
            "memory": "memory_efficiency",
            "consolidation": "knowledge_quality",
            "retention": "memory_retention",
            "utilization": "resource_efficiency",
            "relevance": "result_quality",
        }
        category = "general"
        for keyword, cat in categories.items():
            if keyword in parts:
                category = cat
                break

        # Analyze code structure for evidence
        code_lines = code.splitlines() if code else []
        code_size = len(code_lines)
        has_loops = any('for ' in l or 'while ' in l for l in code_lines)
        has_error_handling = any('try:' in l or 'except' in l for l in code_lines)
        has_caching = any('cache' in l.lower() for l in code_lines)

        # Build structured GRILL answers
        evidence_parts = []
        if code_size > 50:
            evidence_parts.append(f"code is {code_size} lines (large)")
        if not has_error_handling:
            evidence_parts.append("no error handling detected")
        if not has_caching:
            evidence_parts.append("no caching detected")
        evidence = "; ".join(evidence_parts) if evidence_parts else "observed in current behavior"

        # Generate improvement target
        improvement_map = {
            "retrieval_quality": "increase search recall and precision",
            "precision": "reduce false positive rate",
            "performance": "reduce latency of hot path",
            "memory_efficiency": "improve knowledge consolidation ratio",
            "knowledge_quality": "increase semantic node proportion",
            "memory_retention": "improve episodic-to-semantic promotion rate",
            "resource_efficiency": "increase recall/remember ratio",
            "result_quality": "improve ranking relevance score",
            "general": f"improve {weakness}",
        }

        # Suggest simplest change based on analysis
        change_map = {
            "retrieval_quality": "add hybrid search weight tuning",
            "precision": "add result filtering threshold",
            "performance": "add caching for frequent queries",
            "memory_efficiency": "add consolidation trigger threshold",
            "knowledge_quality": "add gravity-based promotion",
            "memory_retention": "adjust Weibull decay parameters",
            "resource_efficiency": "add prefetch for common patterns",
            "result_quality": "add MMR diversity filtering",
            "general": f"address {weakness} directly",
        }

        return {
            "weakness": weakness,
            "category": category,
            "evidence": evidence,
            "improvement_target": improvement_map.get(category, f"improve {weakness}"),
            "simplest_change": change_map.get(category, f"address {weakness} directly"),
        }

    def _define_eval(self, weakness: str, grill: dict) -> dict:
        """Step 2: Define how to measure improvement.

        Maps weakness category to concrete evaluation metrics.
        """
        category = grill.get("category", "general")

        metric_map = {
            "retrieval_quality": {"metric": "recall@k", "direction": "maximize", "threshold": 0.8},
            "precision": {"metric": "precision@k", "direction": "maximize", "threshold": 0.9},
            "performance": {"metric": "latency_p95_ms", "direction": "minimize", "threshold": 100},
            "memory_efficiency": {"metric": "consolidation_ratio", "direction": "maximize", "threshold": 0.6},
            "knowledge_quality": {"metric": "semantic_node_ratio", "direction": "maximize", "threshold": 0.3},
            "memory_retention": {"metric": "promotion_rate", "direction": "maximize", "threshold": 0.2},
            "resource_efficiency": {"metric": "recall_remember_ratio", "direction": "maximize", "threshold": 0.5},
            "result_quality": {"metric": "mmr_diversity_score", "direction": "maximize", "threshold": 0.4},
            "general": {"metric": weakness, "direction": "maximize", "threshold": self._config.pass_k_threshold},
        }

        result = metric_map.get(category, metric_map["general"]).copy()
        result["weakness"] = weakness
        result["category"] = category
        return result

    def _write_plan(self, weakness: str, grill: dict, eval_def: dict) -> dict:
        """Step 3: Write a concrete change plan.

        Maps GRILL insights + eval definition to a structured mutation plan.
        """
        category = grill.get("category", "general")
        improvement = grill.get("improvement_target", "")
        simplest = grill.get("simplest_change", "")
        metric = eval_def.get("metric", weakness)

        # Map category to AST mutation strategy
        strategy_map = {
            "retrieval_quality": "log_add",       # Add logging to track retrieval
            "precision": "assert_add",            # Add assertions for precision
            "performance": "type_annotate",        # Type hints enable optimization
            "memory_efficiency": "error_handle",   # Add error handling for robustness
            "knowledge_quality": "doc_add",         # Add documentation for clarity
            "memory_retention": "log_add",          # Add logging for retention tracking
            "resource_efficiency": "type_annotate", # Type hints for efficiency
            "result_quality": "assert_add",         # Add assertions for quality
            "general": "log_add",
        }

        strategy = strategy_map.get(category, "log_add")

        return {
            "target": weakness,
            "category": category,
            "change_type": "ast_mutation",
            "strategy": strategy,
            "description": simplest,
            "improvement_target": improvement,
            "metric": metric,
            "threshold": eval_def.get("threshold", 0.5),
        }

    def _execute_plan(self, code: str, plan: dict) -> str:
        """Step 4: Execute the plan via AST mutation.

        Uses ASTMutation for syntax-safe code modification.
        Falls back to returning code unchanged if mutation fails.
        """
        if not code:
            return code

        strategy = plan.get("strategy", "log_add")

        try:
            from prometheus_z.evolution.ast_mutation import ASTMutation
            mutator = ASTMutation(self._config)
            result = mutator.mutate(code, strategy)
            if result is not None:
                return result
        except Exception:
            pass

        # Fallback: return code unchanged (mutation not applicable)
        return code

    def _get_existing_solutions(self) -> list[str]:
        """Get list of existing attempted solutions for dedup check."""
        return [h["weakness"] for h in self._history]

    @property
    def history(self) -> list[dict]:
        return list(self._history)

    @property
    def success_rate(self) -> float:
        if not self._history:
            return 0.0
        applied = sum(1 for h in self._history if h.get("applied"))
        return applied / len(self._history)
