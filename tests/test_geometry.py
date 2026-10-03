import pytest

from practice import geometry

def fake_calculate_pi():
    return 3.14

def test_circle_circumference_with_patched_pi(monkeypatch):
    monkeypatch.setattr(geometry, "calculate_pi", fake_calculate_pi)

    assert geometry.circle_circumference(2) == pytest.approx(12.56)

###

