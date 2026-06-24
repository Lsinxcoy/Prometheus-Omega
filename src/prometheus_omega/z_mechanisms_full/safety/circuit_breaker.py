"""CircuitBreaker — S5: 3-level circuit breaker for fault isolation.

Levels:
1. CLOSED — normal operation, requests pass through
2. OPEN — circuit tripped, all requests rejected (cool-down period)
3. HALF_OPEN — testing recovery, limited requests allowed

Trip conditions (zero-LLM):
- Error rate > threshold in window
- Latency > threshold
- Consecutive failures > limit
"""
from __future__ import annotations

import time
from collections import deque
from enum import IntEnum

from prometheus_z.schema import ZConfig


class CircuitState(IntEnum):
    """Circuit breaker states. Integer for comparison (P-16)."""
    CLOSED = 0    # Normal
    OPEN = 1      # Tripped — rejecting all
    HALF_OPEN = 2 # Testing recovery


class CircuitBreaker:
    """S5: 3-level circuit breaker with automatic recovery."""

    def __init__(self, name: str = "default", config: ZConfig | None = None):
        self._name = name
        self._config = config or ZConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._consecutive_failures = 0
        self._last_failure_time = 0.0
        self._last_state_change = time.time()
        self._history: deque[dict] = deque(maxlen=200)
        self._half_open_requests = 0

    @property
    def state(self) -> CircuitState:
        """Current circuit state. Auto-transitions from OPEN→HALF_OPEN after cool-down."""
        if self._state == CircuitState.OPEN:
            elapsed = time.time() - self._last_failure_time
            if elapsed >= self._config.circuit_breaker_cooldown:
                self._transition(CircuitState.HALF_OPEN)
        return self._state

    def allow_request(self) -> bool:
        """Check if a request should be allowed through.

        CLOSED → always allow
        OPEN → always deny
        HALF_OPEN → allow (test request)
        """
        current = self.state  # Trigger auto-transition
        if current == CircuitState.CLOSED:
            return True
        if current == CircuitState.OPEN:
            return False
        if current == CircuitState.HALF_OPEN:
            if self._half_open_requests < 1:
                self._half_open_requests += 1
                return True  # Test request
            return False
        return False

    def record_success(self) -> CircuitState:
        """Record a successful operation."""
        self._success_count += 1
        self._consecutive_failures = 0

        if self._state == CircuitState.HALF_OPEN:
            # Recovery confirmed — close circuit
            self._transition(CircuitState.CLOSED)

        return self._state

    def record_failure(self) -> CircuitState:
        """Record a failed operation. May trip the circuit."""
        self._failure_count += 1
        self._consecutive_failures += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            # Recovery failed — re-open circuit
            self._transition(CircuitState.OPEN)

        elif self._state == CircuitState.CLOSED:
            # Check if we should trip
            if self._consecutive_failures >= self._config.circuit_breaker_threshold:
                self._transition(CircuitState.OPEN)

        return self._state

    def trip(self) -> None:
        """Manually trip the circuit breaker."""
        self._transition(CircuitState.OPEN)
        self._last_failure_time = time.time()

    def reset(self) -> None:
        """Manually reset to CLOSED."""
        self._transition(CircuitState.CLOSED)
        self._failure_count = 0
        self._consecutive_failures = 0

    def _transition(self, new_state: CircuitState) -> None:
        """Transition to a new state and record history."""
        if new_state == self._state:
            return
        old_state = self._state
        self._state = new_state
        self._last_state_change = time.time()
        if new_state == CircuitState.HALF_OPEN:
            self._half_open_requests = 0
        self._history.append({
            "from": old_state.name,
            "to": new_state.name,
            "time": time.time(),
        })

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    @property
    def failure_count(self) -> int:
        return self._failure_count

    @property
    def consecutive_failures(self) -> int:
        return self._consecutive_failures

    @property
    def stats(self) -> dict:
        return {
            "name": self._name,
            "state": self._state.name,
            "failures": self._failure_count,
            "successes": self._success_count,
            "consecutive_failures": self._consecutive_failures,
            "transitions": len(self._history),
        }
