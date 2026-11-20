# Import psycopg2, the library that talks to PostgreSQL
import psycopg2

# Import our own settings file (config.py), which holds the host, name, user and password
from app import config
# This small function opens a connection to the database and gives it back
def get_connection():
    # Open the connection using the settings from config.py
    connection = psycopg2.connect(
        host=config.DB_HOST,          # where the database is
        port=config.DB_PORT,          # which door to knock on
        dbname=config.DB_NAME,        # which database to open
        user=config.DB_USER,          # who is logging in
        password=config.DB_PASSWORD,  # the secret password
    )

    # Hand the open connection back to whoever called this function
    return connection


# NEW: run a SELECT and give back ALL rows (a list of rows)
def fetch_all(sql, params=()):
    # Open a connection and a cursor (the "pen" that sends SQL)
    connection = get_connection()
    cursor = connection.cursor()

    # Send the SQL, with the values filled into the %s spots safely
    cursor.execute(sql, params)

    # Take all rows of the answer
    rows = cursor.fetchall()

    # Close the cursor and the connection
    cursor.close()
    connection.close()

    # Give the rows back
    return rows


# NEW: run a SELECT and give back only the FIRST row (or None if there is no row)
def fetch_one(sql, params=()):
    # Open a connection and a cursor
    connection = get_connection()
    cursor = connection.cursor()

    # Send the SQL with the values
    cursor.execute(sql, params)

    # Take the first row of the answer
    row = cursor.fetchone()

    # Close the cursor and the connection
    cursor.close()
    connection.close()

    # Give the row back
    return row


# NEW: run an INSERT, UPDATE or DELETE and save the change for good
def execute(sql, params=()):
    # Open a connection and a cursor
    connection = get_connection()
    cursor = connection.cursor()

    # Send the SQL with the values
    cursor.execute(sql, params)

    # Count how many rows were changed
    rows_changed = cursor.rowcount

    # Save the change for good (without commit PostgreSQL throws it away)
    connection.commit()

    # Close the cursor and the connection
    cursor.close()
    connection.close()

    # Give back how many rows were changed
    return rows_changed