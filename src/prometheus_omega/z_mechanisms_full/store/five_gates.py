"""FiveGates — P20: Write → Read → Modify → Consolidate → Execute.

6 independent systems converged on this architecture (SAGE+MemGate+SkillAdaptor+Nautilus+AURA-Mem+TRACE).
Each gate is a cascading failure circuit breaker — one gate fails → short-circuit return.

P-27: check_gate() returns GateCheckResult — check .passed, NOT truthiness.
"""
from __future__ import annotations

from prometheus_z.schema import (
    GateCheckResult, Node, TrustLevel, WriteGateResult, ZConfig,
)
from prometheus_z.store.write_gate import DopamineWriteGate


class FiveGates:
    """Five cascading gates: Write → Read → Modify → Consolidate → Execute.

    Each gate is a circuit breaker. If any gate FAILS, subsequent gates
    are not checked (short-circuit). This prevents partial-state corruption.
    """

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._write_gate = DopamineWriteGate(self._config)

    @property
    def write_gate(self) -> DopamineWriteGate:
        """Access the underlying DopamineWriteGate."""
        return self._write_gate

    # ── Gate 1: Write ──

    def write_gate_check(self, node: Node,
                         existing_embeddings: list[list[float]] | None = None) -> GateCheckResult:
        """Gate 1: Write — DopamineWriteGate multiplicative check."""
        result = self._write_gate.should_write(node, existing_embeddings)
        return GateCheckResult(
            passed=result.allowed,
            reason=result.reason,
            gate_name="write",
            details={"gate_value": result.gate_value},
        )

    # ── Gate 2: Read ──

    def read_gate_check(self, node: Node) -> GateCheckResult:
        """Gate 2: Read — node must exist and not be soft-deleted (tx_to=0)."""
        if not node.id:
            return GateCheckResult(passed=False, reason="Node has no ID", gate_name="read")
        if node.tx_to != 0:
            return GateCheckResult(
                passed=False, reason="Node is soft-deleted (tx_to != 0)", gate_name="read"
            )
        return GateCheckResult(passed=True, reason="Node is readable", gate_name="read")

    # ── Gate 3: Modify ──

    def modify_gate_check(self, node: Node,
                          modifier_agent: str = "") -> GateCheckResult:
        """Gate 3: Modify — node must have sufficient trust for modification.

        PENDING nodes can be modified by their creator only.
        HIGH_SIGNAL and VERIFIED can be modified by anyone.
        """
        if node.trust >= TrustLevel.HIGH_SIGNAL:
            return GateCheckResult(
                passed=True, reason=f"Trust level {node.trust.name} allows modification",
                gate_name="modify",
            )
        # PENDING: only creator can modify
        if node.trust == TrustLevel.PENDING:
            if modifier_agent and modifier_agent == node.creator_agent:
                return GateCheckResult(
                    passed=True,
                    reason=f"PENDING node modifiable by creator '{modifier_agent}'",
                    gate_name="modify",
                )
            return GateCheckResult(
                passed=False,
                reason=f"PENDING node not modifiable by '{modifier_agent}' (creator: '{node.creator_agent}')",
                gate_name="modify",
            )
        return GateCheckResult(
            passed=False,
            reason=f"Trust level {node.trust.name} too low for modification",
            gate_name="modify",
        )

    # ── Gate 4: Consolidate ──

    def consolidate_gate_check(self, nodes: list[Node]) -> GateCheckResult:
        """Gate 4: Consolidate — source nodes must exist and not be already consolidated."""
        if not nodes:
            return GateCheckResult(
                passed=False, reason="No nodes to consolidate", gate_name="consolidate"
            )
        already_consolidated = [n for n in nodes if n.is_consolidated]
        if already_consolidated:
            return GateCheckResult(
                passed=False,
                reason=f"{len(already_consolidated)} nodes already consolidated",
                gate_name="consolidate",
            )
        return GateCheckResult(
            passed=True, reason=f"{len(nodes)} nodes ready for consolidation",
            gate_name="consolidate",
        )

    # ── Gate 5: Execute ──

    def execute_gate_check(self, node: Node) -> GateCheckResult:
        """Gate 5: Execute — node must be VERIFIED trust for execution."""
        if node.trust >= 2:  # VERIFIED
            return GateCheckResult(
                passed=True, reason="VERIFIED node can be executed",
                gate_name="execute",
            )
        return GateCheckResult(
            passed=False,
            reason=f"Trust level {node.trust} insufficient for execution (need VERIFIED)",
            gate_name="execute",
        )

    # ── Full cascade ──

    def check_all(self, node: Node,
                  existing_embeddings: list[list[float]] | None = None) -> GateCheckResult:
        """Run all 5 gates in cascade. First failure → short-circuit.

        This is the primary entry point for the write pipeline.
        """
        # Gate 1: Write
        result = self.write_gate_check(node, existing_embeddings)
        if not result.passed:
            return result

        # Gate 2: Read (verify node is in valid state)
        result = self.read_gate_check(node)
        if not result.passed:
            return result

        # Gate 3: Modify
        result = self.modify_gate_check(node)
        if not result.passed:
            return result

        # Gate 4: Consolidate (single-node check)
        result = self.consolidate_gate_check([node])
        if not result.passed:
            return result

        # Gate 5: Execute
        result = self.execute_gate_check(node)
        if not result.passed:
            return result

        return GateCheckResult(passed=True, reason="All 5 gates passed", gate_name="all")
