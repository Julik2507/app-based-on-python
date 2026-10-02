import pytest

from practice import geometry


def test_circle_circumference_with_patched_pi(monkeypatch):
    monkeypatch.setattr(geometry, "calculate_pi", lambda: 3.14)

    assert geometry.circle_circumference(2) == pytest.approx(12.56)


def test_circle_circumference_zero_radius(monkeypatch):
    monkeypatch.setattr(geometry, "calculate_pi", lambda: 3.14)

    assert geometry.circle_circumference(0) == 0
