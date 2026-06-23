"""BufferingSafetyLayer — D11: HSP90-inspired buffering > correction.

Biology: HSP90 chaperone protein buffers phenotypic variation,
allowing hidden mutations to accumulate without expression.
When stress occurs, buffering releases → variation expressed → selection acts.

Z system analogy:
- Buffering: store potentially useful mutations without applying them
- Stress signal: system under pressure (declining fitness, drift detected)
- Release: apply buffered mutations, enabling rapid adaptation

This prevents premature rejection of "weird" but potentially valuable mutations.
Buffer first, correct later — correction without buffering destroys innovation.
"""
from __future__ import annotations

import time
from collections import deque

from prometheus_z.schema import ZConfig


class BufferingSafetyLayer:
    """D11: HSP90-inspired buffering layer.

    Buffers mutations instead of immediately accepting/rejecting them.
    Only applies them when stress is detected (buffering release).
    """

    def __init__(self, config: ZConfig | None = None, max_buffer_size: int = 200):
        self._config = config or ZConfig()
        self._buffer: deque[dict] = deque(maxlen=max_buffer_size)
        self._applied: deque[dict] = deque(maxlen=max_buffer_size)
        self._rejected: deque[dict] = deque(maxlen=max_buffer_size)
        self._stress_level = 0.0  # 0-1
        self._next_id = 0

    def buffer_mutation(self, mutation: dict) -> str:
        """Buffer a mutation for later evaluation.

        Returns buffer_id for tracking.
        """
        buffer_id = f"buf_{self._next_id}_{time.time():.0f}"
        self._next_id += 1
        entry = {
            "id": buffer_id,
            "mutation": mutation,
            "buffered_at": time.time(),
            "stress_at_buffer": self._stress_level,
        }
        self._buffer.append(entry)
        return buffer_id

    def set_stress(self, level: float) -> list[dict]:
        """Set system stress level (0-1). If stress > threshold, release buffer.

        Returns list of released mutations (applied).
        """
        self._stress_level = max(0.0, min(1.0, level))

        if self._stress_level < self._config.buffer_release_threshold:
            return []  # Not stressed enough to release

        # Release mutations from buffer — sorted by potential value
        released = []
        remaining = []

        for entry in self._buffer:
            mutation = entry["mutation"]
            # Under stress, apply high-potential mutations
            if self._should_release(mutation):
                entry["released_at"] = time.time()
                entry["stress_at_release"] = self._stress_level
                released.append(entry)
                self._applied.append(entry)
            else:
                remaining.append(entry)

        self._buffer = remaining
        return released

    def _should_release(self, mutation: dict) -> bool:
        """Decide whether to release a buffered mutation under stress.

        Heuristic: release mutations with higher estimated value.
        """
        # Estimated value from mutation metadata
        estimated_value = mutation.get("estimated_value", 0.0)
        # Under high stress, lower the bar for release
        threshold = 1.0 - self._stress_level
        return estimated_value >= threshold

    def reject(self, buffer_id: str) -> bool:
        """Manually reject a buffered mutation."""
        for i, entry in enumerate(self._buffer):
            if entry["id"] == buffer_id:
                # deque doesn't support pop(index), so rebuild without the entry
                new_buffer = deque(maxlen=self._buffer.maxlen)
                for j, e in enumerate(self._buffer):
                    if j != i:
                        new_buffer.append(e)
                    else:
                        self._rejected.append(e)
                self._buffer = new_buffer
                return True
        return False

    def get_buffer(self) -> list[dict]:
        """Get all buffered mutations."""
        return list(self._buffer)

    @property
    def buffer_size(self) -> int:
        return len(self._buffer)

    @property
    def stress_level(self) -> float:
        return self._stress_level

    @property
    def stats(self) -> dict:
        return {
            "buffered": len(self._buffer),
            "applied": len(self._applied),
            "rejected": len(self._rejected),
            "stress_level": self._stress_level,
        }
