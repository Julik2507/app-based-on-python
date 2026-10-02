import logging

from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from db import Order, Profile, Role, User

logger = logging.getLogger(__name__)


class AlreadyExistsError(Exception):
    pass


class DataAccessLayer:
    def __init__(self, session: Session):
        self.session = session

    def _get_user_by_email(self, email: str) -> User:
        stmt = select(User).where(User.email == email)
        try:
            return self.session.scalars(stmt).one()
        except NoResultFound:
            logger.warning("user not found: %s", email)
            raise

    def _get_role_by_name(self, name: str) -> Role:
        stmt = select(Role).where(Role.name == name)
        try:
            return self.session.scalars(stmt).one()
        except NoResultFound:
            logger.warning("role not found: %s", name)
            raise

    def get_user_bio_by_email(self, email: str) -> str:
        user = self._get_user_by_email(email)
        stmt = select(Profile.bio).where(Profile.user_id == user.id)
        try:
            return self.session.scalars(stmt).one()
        except NoResultFound:
            logger.warning("profile not found for user: %s", email)
            raise

    def get_user_orders_amount_total(self, email: str) -> int:
        stmt = (
            select(func.coalesce(func.sum(Order.amount), 0))
            .join(Order.user)
            .where(User.email == email)
        )
        return self.session.scalars(stmt).one()

    def get_user_roles(self, email: str) -> list[str]:
        user = self._get_user_by_email(email)
        stmt = (
            select(Role.name)
            .join(Role.users)
            .where(User.id == user.id)
            .order_by(Role.name)
        )
        return list(self.session.scalars(stmt))

    def place_order(self, email: str, amount: int) -> None:
        if amount <= 0:
            raise ValueError(f"order amount must be positive, got {amount}")
        user = self._get_user_by_email(email)
        self.session.add(Order(user=user, amount=amount))
        self.session.commit()

    def register_user(self, email: str, name: str) -> None:
        exists = self.session.scalars(select(User.id).where(User.email == email)).first()
        if exists is not None:
            logger.warning("user already exists: %s", email)
            raise AlreadyExistsError(f"user with email {email} already exists")
        self.session.add(User(email=email, name=name))
        self.session.commit()

    def rename_user(self, email: str, name: str) -> None:
        user = self._get_user_by_email(email)
        user.name = name
        self.session.commit()

    def create_role(self, name: str) -> None:
        # в таблице roles нет UNIQUE на name — дубликаты отсекаем сами
        exists = self.session.scalars(select(Role.id).where(Role.name == name)).first()
        if exists is not None:
            logger.warning("role already exists: %s", name)
            raise AlreadyExistsError(f"role {name} already exists")
        self.session.add(Role(name=name))
        self.session.commit()

    def assign_role(self, email: str, role_name: str) -> None:
        user = self._get_user_by_email(email)
        role = self._get_role_by_name(role_name)
        if role in user.roles:
            # повторное назначение — no-op, иначе упадём на PK (user_id, role_id)
            logger.info("role %s already assigned to %s", role_name, email)
            return
        user.roles.append(role)
        self.session.commit()
