import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from attestation_1.diary import Base, add_note, delete_note, list_notes


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_add_note(session):
    note_id = add_note(session, "Первая заметка")

    notes = list_notes(session)

    assert notes[0].id == note_id
    assert notes[0].text == "Первая заметка"


def test_list_notes_returns_notes_in_addition_order(session):
    add_note(session, "Первая")
    add_note(session, "Вторая")

    notes = list_notes(session)

    assert [note.text for note in notes] == ["Первая", "Вторая"]


def test_delete_note_removes_existing_note(session):
    note_id = add_note(session, "удалить меня")

    assert delete_note(session, note_id) is True
    assert list_notes(session) == []


def test_list_notes_returns_empty_list(session):
    assert list_notes(session) == []


def test_delete_note_returns_false_for_missing_note(session):
    assert delete_note(session, 1) is False


def test_add_note_rejects_blank_text(session):
    with pytest.raises(ValueError, match="Note text cannot be empty"):
        add_note(session, "   ")

    assert list_notes(session) == []
