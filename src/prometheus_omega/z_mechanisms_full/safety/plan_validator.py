"""PlanValidator — S9: 3-layer plan validation (single-step + combination + topology).

Before executing any evolution plan, validate it at 3 levels:
1. SINGLE_STEP: Each individual step is valid and safe
2. COMBINATION: Steps together don't conflict or cancel each other
3. TOPOLOGY: The overall plan structure is sound (no dead-ends, no loops)

All validation is zero-LLM — deterministic checks only.
"""
from __future__ import annotations

from prometheus_z.schema import ZConfig


class PlanValidator:
    """S9: 3-layer plan validation."""

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._stats = {"single_step_pass": 0, "single_step_fail": 0,
                       "combination_pass": 0, "combination_fail": 0,
                       "topology_pass": 0, "topology_fail": 0}

    def validate(self, plan: dict) -> dict:
        """Validate a plan at all 3 levels.

        plan must contain:
        - "steps": list of step dicts, each with "action" and "target"
        - "dependencies": list of (step_i, step_j) pairs (step_j depends on step_i)

        Returns dict with "valid" (bool) and "issues" (list of strings).
        """
        steps = plan.get("steps", [])
        dependencies = plan.get("dependencies", [])

        issues = []

        # Layer 1: Single-step validation
        step_issues = self._validate_single_step(steps)
        issues.extend(step_issues)
        if step_issues:
            self._stats["single_step_fail"] += 1
        else:
            self._stats["single_step_pass"] += 1

        # Layer 2: Combination validation
        combo_issues = self._validate_combination(steps)
        issues.extend(combo_issues)
        if combo_issues:
            self._stats["combination_fail"] += 1
        else:
            self._stats["combination_pass"] += 1

        # Layer 3: Topology validation
        topo_issues = self._validate_topology(steps, dependencies)
        issues.extend(topo_issues)
        if topo_issues:
            self._stats["topology_fail"] += 1
        else:
            self._stats["topology_pass"] += 1

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "steps_validated": len(steps),
        }

    def _validate_single_step(self, steps: list[dict]) -> list[str]:
        """Layer 1: Each step must have valid action and target."""
        issues = []
        valid_actions = {"modify", "add", "remove", "rename", "refactor",
                         "optimize", "fix", "test", "document"}

        for i, step in enumerate(steps):
            action = step.get("action", "")
            target = step.get("target", "")

            if not action:
                issues.append(f"Step {i}: missing action")
            elif action not in valid_actions:
                issues.append(f"Step {i}: invalid action '{action}'")

            if not target:
                issues.append(f"Step {i}: missing target")

        return issues

    def _validate_combination(self, steps: list[dict]) -> list[str]:
        """Layer 2: Steps must not conflict."""
        issues = []

        # Check for conflicting targets (same target, opposite actions)
        targets: dict[str, list[tuple[int, str]]] = {}
        for i, step in enumerate(steps):
            target = step.get("target", "")
            action = step.get("action", "")
            if target not in targets:
                targets[target] = []
            targets[target].append((i, action))

        for target, actions in targets.items():
            if len(actions) > 1:
                # Check for add+remove on same target
                action_names = {a for _, a in actions}
                if "add" in action_names and "remove" in action_names:
                    issues.append(f"Target '{target}': add and remove conflict")
                if "modify" in action_names and len(actions) > 1:
                    issues.append(f"Target '{target}': multiple modifications")

        return issues

    def _validate_topology(self, steps: list[dict],
                           dependencies: list[tuple]) -> list[str]:
        """Layer 3: Dependency graph must be a DAG (no cycles)."""
        issues = []

        if not steps:
            issues.append("Plan has no steps")
            return issues

        if not dependencies:
            return issues  # No dependencies = trivially valid DAG

        # Build adjacency list
        n = len(steps)
        adj: dict[int, list[int]] = {i: [] for i in range(n)}
        for dep_i, dep_j in dependencies:
            if dep_i >= n or dep_j >= n:
                issues.append(f"Dependency ({dep_i}, {dep_j}): step index out of range")
                continue
            adj[dep_i].append(dep_j)

        # Detect cycles via DFS
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {i: WHITE for i in range(n)}

        def has_cycle(node: int) -> bool:
            color[node] = GRAY
            for neighbor in adj[node]:
                if color[neighbor] == GRAY:
                    return True  # Back edge = cycle
                if color[neighbor] == WHITE and has_cycle(neighbor):
                    return True
            color[node] = BLACK
            return False

        for node in range(n):
            if color[node] == WHITE:
                if has_cycle(node):
                    issues.append("Dependency cycle detected — plan is not a DAG")
                    break

        # Check for dead-end steps (no dependents and not final step)
        has_dependent = set()
        for dep_i, dep_j in dependencies:
            has_dependent.add(dep_i)
        # Build out-degree map
        out_degree = {i: len(adj[i]) for i in range(n)}
        for i in range(n):
            if i not in has_dependent and i < n - 1 and out_degree[i] == 0:
                # Intermediate step with no dependents and no outgoing edges — dead-end
                issues.append(f"Step {i}: dead-end (no dependents and no outgoing edges)")

        return issues

    @property
    def stats(self) -> dict:
        return dict(self._stats)
