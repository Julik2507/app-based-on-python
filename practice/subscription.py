from datetime import datetime


def is_subscription_active(expires_at: datetime) -> bool:
    return datetime.now() < expires_at
