from sqlalchemy import Index, select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import selectinload

from db import SessionLocal, User, Order

TARGET_ID = 15
ORIGINAL_NAME = "Alice"

# 4th task
name = "Alice2"
email = "alice2@gmail.com"

user = User(name=name, email=email)
order = Order(amount=100, user=user)

stmt = select(User).where(User.id == 16)
stmt2 = select(Order).options(selectinload(Order.user))

with SessionLocal() as session:
    user = session.execute(stmt).scalar_one()
    session.execute(stmt2)
    session.commit()

# question #8: SELECT ... FOR UPDATE доказывает Read Committed по умолчанию
with SessionLocal() as session_a, SessionLocal() as session_b:
    user_a = session_a.get(User, TARGET_ID)
    print(f"[A] первый session.get(): name = {user_a.name!r}")

    user_b = session_b.get(User, TARGET_ID)
    user_b.name = f"{ORIGINAL_NAME}_updated_by_B"
    session_b.commit()

    cached_user_a = session_a.get(User, TARGET_ID)
    print(f"[A] повторный get() без expire: name = {cached_user_a.name!r}  <- из identity map, SQL не отправлялся")

    session_a.expire(user_a)
    fresh_name = session_a.get(User, TARGET_ID).name
    print(f"[A] после expire()+get(): name = {fresh_name!r}  <- новый SELECT внутри ТОЙ ЖЕ транзакции A")

    session_a.commit()

with SessionLocal() as session:
    u = session.get(User, TARGET_ID)
    u.name = ORIGINAL_NAME
    session.commit()

# question #9: SELECT ... FOR UPDATE блокирует выбранные строки
with SessionLocal() as session_a:
    locked_user = session_a.execute(
        select(User).where(User.id == TARGET_ID).with_for_update()
    ).scalar_one()

    with SessionLocal() as session_b:
        # lock_timeout — на уровне сессии/транзакции B, чтобы SELECT FOR UPDATE
        # не ждал блокировку бесконечно, а упал через 1s (ошибка 55P03)
        session_b.execute(text("SET lock_timeout = '1s'"))
        try:
            session_b.execute(
                select(User).where(User.id == TARGET_ID).with_for_update()
            ).scalar_one()
            print("[B] лока не было")
        except OperationalError as e:
            session_b.rollback()

    session_a.commit()

# question #10: индекс меняет план запроса и ускоряет поиск
N = 200_000
TARGET_NAME = f"user_{N // 2}"

# bulk-инсерт оставляем как raw SQL: generate_series на стороне Postgres,
# ORM-инсерт 200k строк по одной был бы на порядки медленнее
name_index = Index("ix_users_name", User.name)

with SessionLocal() as session:
    session.execute(text(
        "INSERT INTO users (name, email) "
        "SELECT 'user_' || i, 'user_' || i || '@test.com' FROM generate_series(1, :n) i "
        "ON CONFLICT (email) DO NOTHING"
    ), {"n": N})
    session.commit()

    stmt = select(User).where(User.name == TARGET_NAME)
    compiled = stmt.compile(bind=session.bind, compile_kwargs={"literal_binds": True})

    print("--- ДО индекса (ожидаем Seq Scan) ---")
    for row in session.execute(text(f"EXPLAIN ANALYZE {compiled}")):
        print(row[0])

    name_index.create(session.bind, checkfirst=True)

    print("--- ПОСЛЕ индекса (ожидаем Index Scan, меньше actual time) ---")
    for row in session.execute(text(f"EXPLAIN ANALYZE {compiled}")):
        print(row[0])

    name_index.drop(session.bind, checkfirst=True)

k