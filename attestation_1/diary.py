import logging
from datetime import datetime

import click
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

log = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    text: Mapped[str]


engine = create_engine("sqlite:///diary.db")


def get_session():
    Base.metadata.create_all(engine)
    return Session(engine)


def add_note(session, text):
    if not text.strip():
        raise ValueError("Note text cannot be empty")

    note = Note(text=text)
    session.add(note)
    session.commit()
    return note.id


def list_notes(session):
    statement = select(Note).order_by(Note.id)
    return list(session.scalars(statement))


def delete_note(session, note_id):
    note = session.get(Note, note_id)
    if note is None:
        return False

    session.delete(note)
    session.commit()
    return True


@click.group()
def cli():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler("app.log")],
    )


@cli.command()
@click.argument("text")
def add(text):
    try:
        with get_session() as session:
            try:
                note_id = add_note(session, text)
            except SQLAlchemyError:
                session.rollback()
                raise
    except ValueError as error:
        log.warning("Rejected note: %s", error)
        raise click.ClickException(str(error)) from error
    except SQLAlchemyError as error:
        log.exception("Error while adding note")
        raise click.ClickException("Database error") from error

    log.info("Added note id=%s", note_id)


@cli.command(name="list")
def list_notes_command():
    try:
        with get_session() as session:
            notes = list_notes(session)
    except SQLAlchemyError as error:
        log.exception("Error while listing notes")
        raise click.ClickException("Database error") from error

    for note in notes:
        click.echo(f"{note.id} {note.created_at} {note.text}")
    log.info("Listed %s notes", len(notes))


@cli.command()
@click.argument("note_id", type=click.IntRange(min=1))
def delete(note_id):
    try:
        with get_session() as session:
            try:
                deleted = delete_note(session, note_id)
            except SQLAlchemyError:
                session.rollback()
                raise
    except SQLAlchemyError as error:
        log.exception("Error while deleting note id=%s", note_id)
        raise click.ClickException("Database error") from error

    if not deleted:
        log.warning("Note id=%s not found", note_id)
        raise click.ClickException(f"Note with id {note_id} not found")

    log.info("Deleted note id=%s", note_id)


if __name__ == "__main__":
    cli()
