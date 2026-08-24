from workers.inference.trend_spike import is_trend_spike, topic_velocity


def test_spike_requires_velocity_and_sample_size() -> None:
    assert is_trend_spike(velocity=3.0, sample_size=51) is True
    assert is_trend_spike(velocity=3.0, sample_size=50) is False
    assert is_trend_spike(velocity=2.5, sample_size=51) is False
    assert is_trend_spike(velocity=2.51, sample_size=51) is True


def test_velocity_uses_previous_window() -> None:
    assert topic_velocity(current_count=26, previous_count=10) == 2.6
    assert topic_velocity(current_count=5, previous_count=0) == 5.0
