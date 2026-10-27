"""Lab 7 tests for the real Lab 5 SQLite functions and Flask API.

Each test uses a new temporary working directory and database. Fixture records
are inserted with SQL so setup does not depend on the functions under test.
"""
from pathlib import Path
import runpy
import sqlite3

import pytest
from flask import Flask

import database
from app import app


USER_FIELDS = ("name", "email", "phone", "address", "country")
SAMPLE_USERS = [
    {
        "user_id": 1,
        "name": "Joseph Awaida",
        "email": "joseph@example.com",
        "phone": "70123456",
        "address": "Beirut",
        "country": "Lebanon",
    },
    {
        "user_id": 2,
        "name": "Test User",
        "email": "test@example.com",
        "phone": "70000000",
        "address": "Tripoli",
        "country": "Lebanon",
    },
]
NEW_USER = {
    "name": "New User",
    "email": "new@example.com",
    "phone": "71111111",
    "address": "Byblos",
    "country": "Lebanon",
}
UPDATED_USER = {
    "user_id": 1,
    "name": "Joseph Awaida",
    "email": "joseph.updated@example.com",
    "phone": "70987654",
    "address": "Beirut, Lebanon",
    "country": "Lebanon",
}


@pytest.fixture(autouse=True)
def isolated_directory(tmp_path, monkeypatch):
    """Keep the original database and every other test's data untouched."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def empty_database(isolated_directory):
    database.create_db_table()
    return isolated_directory / "database.db"


@pytest.fixture
def populated_database(empty_database):
    """Load known fixture data independently of insert_user()."""
    with sqlite3.connect(empty_database) as connection:
        connection.execute("DELETE FROM users")
        connection.executemany(
            "INSERT INTO users "
            "(user_id, name, email, phone, address, country) "
            "VALUES (:user_id, :name, :email, :phone, :address, :country)",
            SAMPLE_USERS,
        )
    return empty_database


@pytest.fixture
def client(populated_database, monkeypatch):
    monkeypatch.setitem(app.config, "TESTING", True)
    with app.test_client() as test_client:
        yield test_client


def read_rows(path):
    """Verify persisted data directly, without using a function under test."""
    with sqlite3.connect(path) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(
            "SELECT * FROM users ORDER BY user_id"
        )]


def test_database_created_on_first_app_run(isolated_directory, monkeypatch):
    """Exercise __main__ startup without opening a server or network port."""
    db_path = isolated_directory / "database.db"
    assert not db_path.exists()
    server_calls = []
    monkeypatch.setattr(
        Flask, "run", lambda self, *args, **kwargs: server_calls.append(True)
    )
    runpy.run_path(str(Path(database.__file__).with_name("app.py")),
                   run_name="__main__")
    assert server_calls == [True]
    assert db_path.is_file()
    with sqlite3.connect(db_path) as connection:
        columns = [row[1] for row in connection.execute("PRAGMA table_info(users)")]
    assert columns == ["user_id", *USER_FIELDS]
    # The original Lab 5 startup creates an empty table; no seed users exist.
    assert read_rows(db_path) == []


def test_insert_user(populated_database):
    before = read_rows(populated_database)
    inserted = database.insert_user(dict(NEW_USER))
    assert isinstance(inserted["user_id"], int)
    assert inserted["user_id"] not in {user["user_id"] for user in before}
    assert inserted == {"user_id": inserted["user_id"], **NEW_USER}
    assert read_rows(populated_database) == [*before, inserted]


def test_get_users(populated_database):
    actual = database.get_users()
    assert sorted(actual, key=lambda user: user["user_id"]) == SAMPLE_USERS
    assert read_rows(populated_database) == SAMPLE_USERS


def test_get_user_by_id(populated_database):
    assert database.get_user_by_id(1) == SAMPLE_USERS[0]
    assert database.get_user_by_id(2) == SAMPLE_USERS[1]
    assert read_rows(populated_database) == SAMPLE_USERS


def test_update_user(populated_database):
    assert database.update_user(dict(UPDATED_USER)) == UPDATED_USER
    assert read_rows(populated_database) == [UPDATED_USER, SAMPLE_USERS[1]]


def test_delete_user(populated_database):
    assert database.delete_user(1) == {"status": "User deleted successfully"}
    assert read_rows(populated_database) == [SAMPLE_USERS[1]]


def test_api_get_user(client, populated_database):
    response = client.get("/api/users/1")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == SAMPLE_USERS[0]
    assert read_rows(populated_database) == SAMPLE_USERS


def test_api_add_user(client, populated_database):
    response = client.post("/api/users/add", json=dict(NEW_USER))
    assert response.status_code == 200  # Actual Lab 5 API contract.
    assert response.is_json
    inserted = response.get_json()
    assert isinstance(inserted["user_id"], int)
    assert inserted["user_id"] not in {user["user_id"] for user in SAMPLE_USERS}
    assert inserted == {"user_id": inserted["user_id"], **NEW_USER}
    assert read_rows(populated_database) == [*SAMPLE_USERS, inserted]
    fetched = client.get(f"/api/users/{inserted['user_id']}")
    assert fetched.status_code == 200
    assert fetched.get_json() == inserted


def test_api_update_user(client, populated_database):
    response = client.put("/api/users/update", json=dict(UPDATED_USER))
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == UPDATED_USER
    assert read_rows(populated_database) == [UPDATED_USER, SAMPLE_USERS[1]]
    fetched = client.get("/api/users/1")
    assert fetched.status_code == 200
    assert fetched.get_json() == UPDATED_USER


def test_api_delete_user(client, populated_database):
    response = client.delete("/api/users/delete/1")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {"status": "User deleted successfully"}
    assert read_rows(populated_database) == [SAMPLE_USERS[1]]
    fetched = client.get("/api/users/1")
    assert fetched.status_code == 200
    assert fetched.get_json() == {}  # Lab 5 returns {} for missing users.


def test_api_get_all_users(client, populated_database):
    response = client.get("/api/users")
    assert response.status_code == 200
    assert response.is_json
    assert sorted(response.get_json(), key=lambda user: user["user_id"]) == SAMPLE_USERS
    assert read_rows(populated_database) == SAMPLE_USERS


def test_get_user_by_id_missing(populated_database):
    assert database.get_user_by_id(9999) == {}
    assert read_rows(populated_database) == SAMPLE_USERS


def test_get_users_empty(empty_database):
    assert database.get_users() == []
