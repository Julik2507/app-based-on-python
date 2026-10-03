
import logging

from pytest import Session

from db import Role
from sqlalchemy import select, func
from sqlalchemy.exc import NoResultFound
from db.py import User, Order

logger = logging.getLogger(__name__)


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

    def get_user_bio_by_email(self, email: str) -> str:
        try:
            user = self._get_user_by_email(email)
            return user.profile.bio
        except NoResultFound:
            logger.warning("user not found: %s", email)
            raise

    def get_user_orders_amount_total(self, email: str) -> int:
        try: 
            stmt = (
                select(func.coalesce(func.sum(Order.amount), 0))
                .join(Order.user)
                .where(User.email == email)
            )
            return self.session.scalars(stmt).one()
        except NoResultFound:
            logger.warning("user not found: %s", email)
            raise

    def get_user_roles(self, email: str) -> list[str]:
        try:
            user = self._get_user_by_email(email)
            return [role.name for role in user.roles]
        except NoResultFound:
            logger.warning("user not found: %s", email)
            raise

    def place_order(self, email: str, amount: int) -> None:
        try:
            user = self._get_user_by_email(email)
            order = Order(amount=amount, user=user)
            self.session.add(order)
        except NoResultFound:
            logger.warning("user not found: %s", email)
            raise

    def register_user(self, email: str, name: str) -> None:
        try:
            user = User(name=name, email=email)
            self.session.add(user)
        except Exception as e:
            logger.error("Error registering user: %s", e)
            raise
    def rename_user(self, email: str, name: str) -> None:
        try:
            user = self._get_user_by_email(email)
            user.name = name
        except NoResultFound:
            logger.warning("user not found: %s", email)
            raise

    def create_role(self, name: str) -> None:
        try:
            role = Role(name=name)
            self.session.add(role)
        except Exception as e:
            logger.error("Error creating role: %s", e)
            raise

    def assign_role(self, email: str, role_name: str) -> None:
        try:
            user = self._get_user_by_email(email)
            stmt = select(Role).where(Role.name == role_name)
            role = self.session.scalars(stmt).one()
            user.roles.append(role)
        except NoResultFound:
            logger.warning("user or role not found: %s", email)
            raise