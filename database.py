#!/usr/bin/python
import sqlite3


def connect_to_db():
    conn = sqlite3.connect("database.db")
    return conn


def create_db_table():
    conn = None

    try:
        conn = connect_to_db()

        conn.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            );
        """)

        conn.commit()
        print("User table created successfully")

    except:
        print("User table creation failed - Maybe table already exists")

    finally:
        if conn:
            conn.close()


def insert_user(user):
    inserted_user = {}
    conn = None

    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute(
            """INSERT INTO users
            (name, email, phone, address, country)
            VALUES (?, ?, ?, ?, ?)""",
            (
                user["name"],
                user["email"],
                user["phone"],
                user["address"],
                user["country"],
            ),
        )

        conn.commit()

        inserted_user = get_user_by_id(cur.lastrowid)

    except Exception as e:
        if conn:
            conn.rollback()
        print("Insert error:", e)

    finally:
        if conn:
            conn.close()

    return inserted_user


def get_users():
    users = []
    conn = None

    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()

        for row in rows:
            user = {
                "user_id": row["user_id"],
                "name": row["name"],
                "email": row["email"],
                "phone": row["phone"],
                "address": row["address"],
                "country": row["country"],
            }

            users.append(user)

    except Exception as e:
        print("Get users error:", e)
        users = []

    finally:
        if conn:
            conn.close()

    return users


def get_user_by_id(user_id):
    user = {}
    conn = None

    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,),
        )

        row = cur.fetchone()

        if row:
            user = {
                "user_id": row["user_id"],
                "name": row["name"],
                "email": row["email"],
                "phone": row["phone"],
                "address": row["address"],
                "country": row["country"],
            }

    except Exception as e:
        print("Get user error:", e)
        user = {}

    finally:
        if conn:
            conn.close()

    return user


def update_user(user):
    updated_user = {}
    conn = None

    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute(
            """UPDATE users
            SET name = ?, email = ?, phone = ?, address = ?, country = ?
            WHERE user_id = ?""",
            (
                user["name"],
                user["email"],
                user["phone"],
                user["address"],
                user["country"],
                user["user_id"],
            ),
        )

        conn.commit()

        updated_user = get_user_by_id(user["user_id"])

    except Exception as e:
        if conn:
            conn.rollback()
        print("Update error:", e)

    finally:
        if conn:
            conn.close()

    return updated_user


def delete_user(user_id):
    message = {}
    conn = None

    try:
        conn = connect_to_db()

        conn.execute(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,),
        )

        conn.commit()

        message["status"] = "User deleted successfully"

    except Exception as e:
        if conn:
            conn.rollback()

        message["status"] = "Cannot delete user"
        print("Delete error:", e)

    finally:
        if conn:
            conn.close()

    return message