from tabulate import tabulate
import config
from sqlalchemy import create_engine, text


settings = config.getSettings()
engine = create_engine(settings.DATABASE_URL, echo=False)


def execute_sql(sql: str, params: dict = {}):
    with engine.begin() as connection:
        result = connection.execute(
            text(sql),
            params
        )
        try:
            # rows = result.fetchall()
            rows = result.mappings().all()
            return rows
        except:
            return None


def print_table(rows, table_name=None):
    if table_name: print(f"\nTable: {table_name}")
    print(tabulate(rows, headers="keys", tablefmt="rounded_outline"))






def create_table_users_newer():
    users_newer_query = """
        CREATE TABLE IF NOT EXISTS users_newer(
            id              SERIAL PRIMARY KEY,
            email           TEXT UNIQUE NOT NULL,
            password_hash   TEXT NOT NULL,
            created         TIMESTAMP DEFAULT NOW()
        )
    """
    execute_sql(users_newer_query)


def create_users_table():
    users_query = """
        CREATE TABLE IF NOT EXISTS users(
            id              SERIAL PRIMARY KEY,
            email           TEXT UNIQUE NOT NULL,
            password_hash   TEXT NOT NULL,
            created         TIMESTAMP DEFAULT NOW()
        )
    """
    execute_sql(users_query)


def create_notes_table():
    notes_query = """
        CREATE TABLE IF NOT EXISTS notes(
            id              SERIAL PRIMARY KEY,
            user_id         INT NOT NULL REFERENCES users(id),
            note            TEXT,
            created         TIMESTAMP DEFAULT NOW()
        )
    """
    execute_sql(notes_query)









def test_insertion():
    create_table_users_newer()
    execute_sql("""
        INSERT INTO users_newer
        (email, password_hash)
        VALUES 
        ('evyats6@gmail.com', 'somepasshash')
    """)
    print_table(execute_sql("""SELECT * FROM users_newer"""))



if __name__ == "__main__":
    pass
    test_insertion()