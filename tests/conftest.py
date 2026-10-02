import psycopg2
import pytest
from psycopg2 import errors
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from conf import settings
from db import Base

# произвольный ключ для pg_advisory_xact_lock — общий для всех xdist-воркеров
SCHEMA_LOCK_KEY = 232

TEST_DB_NAME = f"{settings.DB_NAME}_test"
CONNECTION_STRING_TEST = (
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{TEST_DB_NAME}"
)


def _ensure_database_exists():
    conn = psycopg2.connect(
        dbname="postgres",
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )
    # CREATE DATABASE нельзя выполнить внутри транзакции
    conn.autocommit = True
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    except (errors.DuplicateDatabase, errors.UniqueViolation):
        # UniqueViolation — гонка двух xdist-воркеров на pg_database
        pass
    finally:
        conn.close()


@pytest.fixture(scope="session")
def db_engine():
    _ensure_database_exists()
    engine = create_engine(CONNECTION_STRING_TEST)
    # параллельные CREATE TABLE из нескольких воркеров падают не только с
    # DuplicateTable, но и с UniqueViolation на pg_type — поэтому не ловим
    # ошибки, а сериализуем create_all блокировкой на время транзакции
    with engine.begin() as conn:
        conn.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": SCHEMA_LOCK_KEY})
        Base.metadata.create_all(conn)
    yield engine
    engine.dispose()


@pytest.fixture
def session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    # commit() внутри кода освобождает SAVEPOINT, а не коммитит внешнюю транзакцию
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()
