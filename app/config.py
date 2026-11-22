# Import os so Python can read values from the .env file.
import os

# Load the .env file when the project starts.
from dotenv import load_dotenv

# Read all values from the .env file.
load_dotenv()


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