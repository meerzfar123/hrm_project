import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import psycopg2, the library that talks to PostgreSQL
import psycopg2

# Import our own settings file (config.py)
from app import config
# "try" means: attempt this code, and if something goes wrong, jump to "except"
try:
    # Open a connection to the database using the settings from config.py
    connection = psycopg2.connect(
        host=config.DB_HOST,          # where the database is
        port=config.DB_PORT,          # which door to knock on
        dbname=config.DB_NAME,        # which database to open
        user=config.DB_USER,          # who is logging in
        password=config.DB_PASSWORD,  # the secret password
    )

    # Create a cursor, which is like a pen that writes SQL commands for us
    cursor = connection.cursor()

    # Ask PostgreSQL for its version (this SQL command only reads, it changes nothing)
    cursor.execute("SELECT version();")

    # Take the first (and only) row of the answer
    result = cursor.fetchone()

    # Print a success message
    print("Connection OK!")

    # Print the version text, which is the first item in the row
    print("PostgreSQL version:", result[0])

    # Close the cursor because we are finished with it
    cursor.close()

    # Close the connection so it does not stay open
    connection.close()

# If anything above failed, the code jumps here and "error" holds the reason
except Exception as error:
    # Tell us it failed
    print("Connection FAILED.")

    # Show the reason, which helps us fix the problem
    print("Reason:", error)