import os
from dotenv import load_dotenv

# Find the folder where this config.py file is located.
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Load the .env file that is inside the app folder.
load_dotenv(os.path.join(APP_DIR, ".env"))


# Read the PostgreSQL host from the environment.
DB_HOST = os.getenv("DB_HOST", "localhost")

# Read the PostgreSQL port from the environment.
DB_PORT = os.getenv("DB_PORT", "5432")

# Read the database name from the environment.
DB_NAME = os.getenv("DB_NAME", "hrm_db")

# Read the PostgreSQL username from the environment.
DB_USER = os.getenv("DB_USER", "postgres")

# Read the PostgreSQL password from the environment.
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


# Read the Gemini API key from the environment.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Keep the Gemini model name in one place.
GEMINI_MODEL = "gemini-flash-latest"


# Read the Gmail sender address from the environment.
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")

# Read the Gmail App Password from the environment.
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")

# Read the first HR email address from the environment.
FIRST_HR_EMAIL = os.getenv("FIRST_HR_EMAIL", "")


# Read the email mode from the environment.
EMAIL_MODE = os.getenv("EMAIL_MODE", "gmail")


# Read the cookie security setting from the environment.
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False").lower() == "true"


# Read the session duration from the environment.
SESSION_HOURS = int(os.getenv("SESSION_HOURS", "8"))

# The live website URL used when creating public links.
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")