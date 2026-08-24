"""Trend-spike rule from the source: velocity > 2.5 AND sample size > 50."""

from __future__ import annotations


def is_trend_spike(*, velocity: float, sample_size: int) -> bool:
    return velocity > 2.5 and sample_size > 50


def topic_velocity(*, current_count: int, previous_count: int) -> float:
    """IMPLEMENTATION formula — source did not define velocity algebra.

    velocity = current_window_count / max(previous_window_count, 1)
    """
    if current_count < 0 or previous_count < 0:
        raise ValueError("counts must be >= 0")
    return current_count / max(previous_count, 1)


def topic_acceleration(*, current_velocity: float, previous_velocity: float) -> float:
    """IMPLEMENTATION: difference of successive velocity values."""
    return current_velocity - previous_velocity
