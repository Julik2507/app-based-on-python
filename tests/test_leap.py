import pytest

from practice.leap import is_leap_year


@pytest.mark.parametrize("year, expected", [
    (2024, True),   # делится на 4
    (2023, False),  # не делится на 4
    (1900, False),  # делится на 100, но не на 400
    (2100, False),
    (2000, True),   # делится на 400
    (1600, True),
    (4, True),
    (1, False),
])
def test_is_leap_year(year, expected):
    assert is_leap_year(year) is expected
