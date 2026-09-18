import psycopg
from db import User, connection_string

#insert
# with psycopg.connect(connection_string) as conn:
#     with conn.cursor() as cursor:
#         cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ("John Pork", "john.pork@example.com"))
#         cursor.execute("SELECT * FROM users WHERE name = %s", ("John Pork",))
#         result = cursor.fetchall()

# print(result)  # (1,)

# select
# with psycopg.connect(connection_string) as conn:
#     with conn.cursor() as cursor:
#         cursor.execute("SELECT * FROM users")
#         result = cursor.fetchall()

# print(result)  # (1,)

# #update
# with psycopg.connect(connection_string) as conn:
#     with conn.cursor() as cursor:
#         cursor.execute("UPDATE users SET name = %s WHERE email = %s", ("John Pork The Second", "j1ohn.pork@example.com"))
#         result = cursor.rowcount

# print(result)  # 1

#delete
# with psycopg.connect(connection_string) as conn:
#     with conn.cursor() as cursor:
#         cursor.execute("DELETE FROM users WHERE email = %s", ("j11ohn.pork@example.com",))
#         result = cursor.rowcount

# print(result)  # 1

# #SQL Alchemy

from sqlalchemy import insert, delete, update, select
from sqlalchemy.orm import selectinload
from db import User, Order
from db import SessionLocal, User
# stmt = delete(user_table).where(user_table.c.id == 5)

# stmt = User.insert().values((name="Alice", email="alice@gmail.com"),)

# stmt = insert(User).values(name=name, email=email)
# email = "alice2_updated@gmail.com"
# stmt2 = update(User).where(User.name=="Alice2").values(email=email)

# stmt3 = delete(User).where(User.name=="Alice2")
# # stmt = insert(User).values(name=name, email=email)

# with SessionLocal() as session:
#     session.execute(stmt)
#     session.commit()



#orm
name = "Alice2"
email = "alice2@gmail.com"


user=User(name=name, email=email)

order=Order(amount=100, user=user)

stmt = select(User).where(User.id==16)
stmt2 = select(Order).options(selectinload(Order.user))

with SessionLocal() as session:
    user = session.execute(stmt).scalar_one()
    # user.name = "Alice2_updated"
    # session.add(user)
    # session.delete(user)
    session.execute(stmt2)


    session.commit()
