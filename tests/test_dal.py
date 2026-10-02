import logging

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound

from dal import AlreadyExistsError, DataAccessLayer
from db import Order, Profile, Role, User

EMAIL = "alice@example.com"
MISSING_EMAIL = "nobody@example.com"


@pytest.fixture
def dal(session):
    return DataAccessLayer(session)


@pytest.fixture
def user(session):
    u = User(name="Alice", email=EMAIL)
    session.add(u)
    session.flush()
    return u


@pytest.fixture
def role(session):
    r = Role(name="admin")
    session.add(r)
    session.flush()
    return r


# get_user_bio_by_email

def test_get_user_bio(dal, session, user):
    session.add(Profile(user=user, bio="Hello"))
    session.flush()

    assert dal.get_user_bio_by_email(EMAIL) == "Hello"


def test_get_user_bio_user_not_found(dal, caplog):
    with caplog.at_level(logging.WARNING, logger="dal"):
        with pytest.raises(NoResultFound):
            dal.get_user_bio_by_email(MISSING_EMAIL)

    assert f"user not found: {MISSING_EMAIL}" in caplog.text


def test_get_user_bio_no_profile(dal, user, caplog):
    with caplog.at_level(logging.WARNING, logger="dal"):
        with pytest.raises(NoResultFound):
            dal.get_user_bio_by_email(EMAIL)

    assert f"profile not found for user: {EMAIL}" in caplog.text


# get_user_orders_amount_total

def test_orders_total(dal, session, user):
    session.add_all([Order(user=user, amount=100), Order(user=user, amount=50)])
    session.flush()

    assert dal.get_user_orders_amount_total(EMAIL) == 150


def test_orders_total_no_orders(dal, user):
    assert dal.get_user_orders_amount_total(EMAIL) == 0


def test_orders_total_ignores_other_users(dal, session, user):
    other = User(name="Bob", email="bob@example.com")
    session.add_all([Order(user=user, amount=10), Order(user=other, amount=999)])
    session.flush()

    assert dal.get_user_orders_amount_total(EMAIL) == 10


def test_orders_total_unknown_user_is_zero(dal):
    # агрегат без GROUP BY всегда возвращает одну строку — исключения нет
    assert dal.get_user_orders_amount_total(MISSING_EMAIL) == 0


# get_user_roles

def test_get_user_roles(dal, session, user):
    user.roles.extend([Role(name="editor"), Role(name="admin")])
    session.flush()

    assert dal.get_user_roles(EMAIL) == ["admin", "editor"]


def test_get_user_roles_empty(dal, user):
    assert dal.get_user_roles(EMAIL) == []


def test_get_user_roles_user_not_found(dal):
    with pytest.raises(NoResultFound):
        dal.get_user_roles(MISSING_EMAIL)


# place_order

def test_place_order(dal, session, user):
    dal.place_order(EMAIL, 200)

    orders = session.scalars(select(Order).where(Order.user_id == user.id)).all()
    assert [o.amount for o in orders] == [200]


def test_place_order_user_not_found(dal, session, caplog):
    with caplog.at_level(logging.WARNING, logger="dal"):
        with pytest.raises(NoResultFound):
            dal.place_order(MISSING_EMAIL, 200)

    assert f"user not found: {MISSING_EMAIL}" in caplog.text
    assert session.scalar(select(func.count()).select_from(Order)) == 0


@pytest.mark.parametrize("amount", [0, -10])
def test_place_order_non_positive_amount(dal, user, amount):
    with pytest.raises(ValueError):
        dal.place_order(EMAIL, amount)


# register_user

def test_register_user(dal, session):
    dal.register_user(EMAIL, "Alice")

    created = session.scalars(select(User).where(User.email == EMAIL)).one()
    assert created.name == "Alice"


def test_register_user_duplicate_email(dal, session, user, caplog):
    with caplog.at_level(logging.WARNING, logger="dal"):
        with pytest.raises(AlreadyExistsError):
            dal.register_user(EMAIL, "Another Alice")

    assert f"user already exists: {EMAIL}" in caplog.text
    assert session.scalar(select(func.count()).select_from(User)) == 1


# rename_user

def test_rename_user(dal, session, user):
    dal.rename_user(EMAIL, "Alicia")

    session.expire_all()
    assert session.get(User, user.id).name == "Alicia"


def test_rename_user_not_found(dal):
    with pytest.raises(NoResultFound):
        dal.rename_user(MISSING_EMAIL, "Ghost")


# create_role

def test_create_role(dal, session):
    dal.create_role("admin")

    assert session.scalars(select(Role.name)).all() == ["admin"]


def test_create_role_duplicate(dal, session, role, caplog):
    with caplog.at_level(logging.WARNING, logger="dal"):
        with pytest.raises(AlreadyExistsError):
            dal.create_role("admin")

    assert "role already exists: admin" in caplog.text
    assert session.scalar(select(func.count()).select_from(Role)) == 1


# assign_role

def test_assign_role(dal, user, role):
    dal.assign_role(EMAIL, "admin")

    assert dal.get_user_roles(EMAIL) == ["admin"]


def test_assign_role_already_assigned_is_noop(dal, user, role):
    dal.assign_role(EMAIL, "admin")
    dal.assign_role(EMAIL, "admin")

    assert dal.get_user_roles(EMAIL) == ["admin"]


def test_assign_role_user_not_found(dal, role):
    with pytest.raises(NoResultFound):
        dal.assign_role(MISSING_EMAIL, "admin")


def test_assign_role_role_not_found(dal, user, caplog):
    with caplog.at_level(logging.WARNING, logger="dal"):
        with pytest.raises(NoResultFound):
            dal.assign_role(EMAIL, "superuser")

    assert "role not found: superuser" in caplog.text


# изоляция: данные предыдущих тестов откатились

def test_isolation_db_is_empty(session):
    assert session.scalar(select(func.count()).select_from(User)) == 0
    assert session.scalar(select(func.count()).select_from(Role)) == 0
