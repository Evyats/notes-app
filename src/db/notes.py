from . import db_engine



def list_all_notes(offset: int, limit: int):
    return db_engine.execute_sql(
        """
        SELECT id, user_id, created, name FROM notes
        ORDER BY created DESC
        OFFSET :offset
        LIMIT :limit
        """,
        {"offset": offset, "limit": limit},
    )


def list_notes(user_id: int):
    return db_engine.execute_sql(
        """
        SELECT id, created, name FROM notes WHERE user_id=:user_id
        """,
        {"user_id": user_id},
    )


def create_note(user_id: int, name: str, note: str, created):
    return db_engine.execute_sql(
        """
        INSERT INTO notes
        (user_id, note, created, name)
        VALUES
        (:user_id, :note, :created, :name)
        RETURNING id, user_id, created
        """,
        {"user_id": user_id, "note": note, "created": created, "name": name},
    )


def get_note(user_id: int, note_id: int):
    return db_engine.execute_sql(
        """
        SELECT id, note, created, name
        FROM notes
        WHERE user_id=:user_id AND id=:note_id
        """,
        {"user_id": user_id, "note_id": note_id},
    )


def delete_note(note_id: int):
    return db_engine.execute_sql(
        """
        DELETE FROM notes
        WHERE id=:note_id
        RETURNING *
        """,
        {"note_id": note_id},
    )


def update_note(note_id: int, note: str):
    return db_engine.execute_sql(
        """
        UPDATE notes
        SET note=:note
        WHERE id=:note_id
        RETURNING *
        """,
        {"note_id": note_id, "note": note},
    )
