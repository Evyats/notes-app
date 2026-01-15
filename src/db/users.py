from . import db_engine


def get_user_by_email(email: str):
    return db_engine.execute_sql(
        """
        SELECT id, password_hash
        FROM users
        WHERE email=:email
        """,
        {"email": email},
    )


def create_user(email: str, password_hash: str, created):
    return db_engine.execute_sql(
        """
        INSERT INTO users
        (email, password_hash, created)
        VALUES
        (:email, :password_hash, :created)
        RETURNING id
        """,
        {"email": email, "password_hash": password_hash, "created": created},
    )


def list_users(offset: int, limit: int):
    return db_engine.execute_sql(
        """
        SELECT u.id, u.email, u.created, COUNT(n.note) AS notes_count
        FROM users u
        LEFT JOIN notes n ON u.id=n.user_id
        GROUP BY u.id
        ORDER BY u.created DESC
        OFFSET :offset
        LIMIT :limit
        """,
        {"offset": offset, "limit": limit},
    )


def get_user(user_id: int):
    return db_engine.execute_sql(
        """
        SELECT u.id, u.email, u.created, u.is_admin, COUNT(n.note) AS notes_count
        FROM users u
        LEFT JOIN notes n ON u.id=n.user_id
        WHERE u.id=:user_id
        GROUP BY u.id
        """,
        {"user_id": user_id},
    )


def delete_user_notes(user_id: int):
    return db_engine.execute_sql(
        """
        DELETE FROM notes
        WHERE user_id=:user_id
        RETURNING *
        """,
        {"user_id": user_id},
    )


def delete_user(user_id: int):
    return db_engine.execute_sql(
        """
        DELETE FROM users
        WHERE id=:user_id
        RETURNING *
        """,
        {"user_id": user_id},
    )


def user_exists(user_id: int) -> bool:
    rows = db_engine.execute_sql(
        """
        SELECT id FROM users WHERE id=:user_id
        """,
        {"user_id": user_id},
    )
    return len(rows) > 0
