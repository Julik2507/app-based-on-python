from datetime import datetime, timedelta

from freezegun import freeze_time

from practice.subscription import is_subscription_active

EXPIRES_AT = datetime(2026, 1, 1, 12, 0, 0)


@freeze_time("2026-01-01 11:59:59")
def test_active_before_expiration():
    assert is_subscription_active(EXPIRES_AT)


@freeze_time("2026-01-01 12:00:01")
def test_inactive_after_expiration():
    assert not is_subscription_active(EXPIRES_AT)


@freeze_time("2026-01-01 12:00:00")
def test_inactive_exactly_at_expiration():
    assert not is_subscription_active(EXPIRES_AT)


def test_becomes_inactive_as_time_ticks():
    with freeze_time("2026-01-01 11:59:00") as frozen:
        assert is_subscription_active(EXPIRES_AT)

        frozen.tick(delta=timedelta(seconds=59))  # 11:59:59
        assert is_subscription_active(EXPIRES_AT)

        frozen.tick(delta=timedelta(seconds=1))  # 12:00:00
        assert not is_subscription_active(EXPIRES_AT)


def test_becomes_inactive_after_move_to():
    with freeze_time("2025-06-01") as frozen:
        assert is_subscription_active(EXPIRES_AT)

        frozen.move_to("2026-02-01")

        assert not is_subscription_active(EXPIRES_AT)
