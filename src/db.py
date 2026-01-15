from datetime import UTC, datetime
from tabulate import tabulate

from .auth import pass_hash, jwt
from . import config
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


def check_connectivity():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))





############### TABLES ###############

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


# USERS
def create_users_table():
    users_query = """
        CREATE TABLE IF NOT EXISTS users(
            id              SERIAL PRIMARY KEY,
            email           TEXT UNIQUE NOT NULL,
            password_hash   TEXT NOT NULL,
            created         TIMESTAMP DEFAULT NOW(),
            is_admin        BOOLEAN NOT NULL DEFAULT false
        )
    """
    execute_sql(users_query)

# NOTES
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





############### SCRIPTS ###############

def add_admin_col():
    execute_sql(""" 
        ALTER TABLE users
        ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT false
    """)

def create_admin():
    email = "admin"
    password_hash = pass_hash.hash("admin")
    created = datetime.now(UTC)
    is_admin = True
    execute_sql(
        """
        INSERT INTO users
        (email, password_hash, created, is_admin)
        VALUES
        (:email, :password_hash, :created, :is_admin)
        RETURNING id
        """,
        {"email": email, "password_hash": password_hash, "created": created, "is_admin": is_admin},
    )

def get_admin_permissions():
    rows = execute_sql("SELECT id FROM users WHERE email='admin'")
    admin_id = rows[0]["id"]
    token = jwt.create_access_token(admin_id, 30, 0)
    print("Bearer", token)
    return {
        "user_id": admin_id,
        "access_token": token,
        "token_type": "bearer"
    }




############### TESTS ###############

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
    # test_insertion()
    # check_connectivity()
    # print_table(execute_sql("SELECT * FROM users LIMIT 3"))
    # create_admin()
    get_admin_permissions()
