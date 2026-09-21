from sqlalchemy.dialects.postgresql import insert as pg_insert
import csv
import logging
from sqlalchemy import literal_column
from sqlalchemy.dialects.postgresql import insert as pg_insert
from db import SessionLocal, User

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ],
)

created = 0
updated = 0
skipped = 0

with SessionLocal() as session:
    try:
        with open("./users.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:

                name = row["name"].strip()
                email = row["email"].strip().lower()

                if "@" not in email:
                    log.error("invalid email in row %s: %r", row, email)
                    skipped += 1
                    continue

                stmt = (
                    pg_insert(User)
                    .values(name=name, email=email)
                    .on_conflict_do_update(
                        index_elements=["email"],
                        set_={"name": name},
                    )
                    .returning(User.id, literal_column("(xmax = 0)").label("inserted"))
                )
                user_id, inserted = session.execute(stmt).one()
                if inserted:
                    created += 1
                else:
                    updated += 1
                    log.warning(
                        "user with email %s already existed (id=%s), name updated to %r",
                        email, user_id, name,
                    )
        session.commit()
    except FileNotFoundError:
        log.exception("users.csv not found")
    except Exception:
        log.exception("error while reading users.csv")
        session.rollback()

log.info("created: %d, updated: %d, skipped: %d", created, updated, skipped)
