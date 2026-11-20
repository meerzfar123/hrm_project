# Import hashlib, a standard library that scrambles text into a fixed fingerprint
import hashlib

# Import secrets, a standard library that makes safe random values
import secrets

# Import our database helper file
from app import database as db
# Import our settings file
from app import config
# How many times a password is scrambled. A bigger number makes guessing slower for attackers
PASSWORD_ROUNDS = 600000

# Every account must use an address that ends like this
GMAIL_ENDING = "@gmail.com"

# How many wrong guesses one 6-digit code allows
MAX_CODE_TRIES = 5


# ---------- Gmail address checks ----------

# Clean an email: remove spaces, use small letters, and remove dots before @gmail.com
def clean_email(email):
    # Remove spaces around the text and make all letters small
    email = email.strip().lower()

    # If it does not end with @gmail.com, give it back as it is (check_gmail will complain later)
    if not email.endswith(GMAIL_ENDING):
        return email

    # Cut off the ending to keep only the name part (the text before @gmail.com)
    name_part = email[: len(email) - len(GMAIL_ENDING)]

    # Gmail ignores dots, so we remove them
    name_part = name_part.replace(".", "")

    # Put the ending back and give the cleaned email back
    return name_part + GMAIL_ENDING


# Check a cleaned email. Give back "" if it is fine, or a message that says what is wrong
def check_gmail(email):
    # It must end with @gmail.com
    if not email.endswith(GMAIL_ENDING):
        return "Please use a Gmail address that ends with @gmail.com."

    # Cut off the ending to keep only the name part
    name_part = email[: len(email) - len(GMAIL_ENDING)]

    # A Gmail name has 6 to 30 characters (dots are not counted)
    if len(name_part) < 6 or len(name_part) > 30:
        return "A Gmail name needs 6 to 30 letters or numbers (dots are not counted)."

    # These are the only characters we allow
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789"

    # Check every character one by one
    for letter in name_part:
        if letter not in allowed:
            return "A Gmail address can only contain letters, numbers and dots."

    # Everything is fine
    return ""


# ---------- Scrambling (hashing) ----------

# Make a random salt (random text mixed into the password before scrambling)
def make_salt():
    # 16 random bytes written as 32 hex letters
    return secrets.token_hex(16)


# Scramble a password with its salt
def hash_password(password, salt_hex):
    # Turn the salt text back into bytes
    salt_bytes = bytes.fromhex(salt_hex)

    # Scramble the password many times (PBKDF2 with SHA-256)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, PASSWORD_ROUNDS)

    # Write the result as text and give it back
    return digest.hex()


# Check if a typed password matches the saved scrambled password
def password_matches(password, salt_hex, saved_hash):
    # Scramble the typed password the same way
    new_hash = hash_password(password, salt_hex)

    # Compare in a safe way (it takes the same time even if the texts differ early)
    return secrets.compare_digest(new_hash, saved_hash)


# Scramble a 6-digit code together with the email
def hash_code(email, code):
    # Join the email and the code into one text
    text = email + ":" + code

    # Scramble it and give it back
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Scramble a login token, so the database never holds the real token
def hash_token(token):
    # Scramble the token and give it back
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ---------- Users ----------

# Find a user by email. Give back a dictionary, or None if there is no such user
def get_user_by_email(email):
    # SELECT reads one row: the person with this Gmail
    row = db.fetch_one(
        "SELECT user_id, name, email, password_hash, salt, role, email_verified FROM users WHERE email = %s;",
        (email,),
    )

    # No row means no such user
    if row is None:
        return None

    # Turn the row into a dictionary with clear names
    return {
        "user_id": row[0],
        "name": row[1],
        "email": row[2],
        "password_hash": row[3],
        "salt": row[4],
        "role": row[5],
        "email_verified": row[6],
    }


# Create a new candidate account (not verified yet)
def create_user(name, email, password):
    # Make a salt and scramble the password
    salt = make_salt()
    hashed = hash_password(password, salt)

    # INSERT adds one new row. Role becomes 'candidate' and email_verified becomes FALSE by default
    db.execute(
        "INSERT INTO users (name, email, password_hash, salt) VALUES (%s, %s, %s, %s);",
        (name, email, hashed, salt),
    )


# Change the name and password of an account that is still not verified
def update_pending_user(user_id, name, password):
    # Make a new salt and scramble the new password
    salt = make_salt()
    hashed = hash_password(password, salt)

    # UPDATE changes values, only for this user and only while the Gmail is not verified
    db.execute(
        "UPDATE users SET name = %s, password_hash = %s, salt = %s WHERE user_id = %s AND email_verified = FALSE;",
        (name, hashed, salt, user_id),
    )


# Create the first HR account, or turn an existing account into HR (used by create_first_hr.py)
def save_first_hr(name, email, password):
    # Make a salt and scramble the password
    salt = make_salt()
    hashed = hash_password(password, salt)

    # INSERT adds the person. If this Gmail already exists (ON CONFLICT), update that row instead
    db.execute(
        "INSERT INTO users (name, email, password_hash, salt, role, email_verified) "
        "VALUES (%s, %s, %s, %s, 'hr', TRUE) "
        "ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name, password_hash = EXCLUDED.password_hash, "
        "salt = EXCLUDED.salt, role = 'hr', email_verified = TRUE;",
        (name, email, hashed, salt),
    )


# ---------- Verification codes ----------

# Can we send a new code now? We refuse if a code was already made in the last minute
def can_send_code(email):
    # A code lives 10 minutes, so "expires in more than 9 minutes" means "made in the last minute"
    row = db.fetch_one(
        "SELECT code_id FROM email_codes WHERE email = %s AND purpose = 'signup' AND used = FALSE "
        "AND expires_at > NOW() + INTERVAL '9 minutes' LIMIT 1;",
        (email,),
    )

    # If no such row exists, we may send a new code
    return row is None


# Save a new code (scrambled). Older codes of this Gmail are switched off first
def save_new_code(email, code):
    # UPDATE switches off all older codes of this Gmail
    db.execute(
        "UPDATE email_codes SET used = TRUE WHERE email = %s AND purpose = 'signup' AND used = FALSE;",
        (email,),
    )

    # INSERT saves the new code (only its scrambled form) that expires in 10 minutes
    db.execute(
        "INSERT INTO email_codes (email, code_hash, purpose, expires_at) "
        "VALUES (%s, %s, 'signup', NOW() + INTERVAL '10 minutes');",
        (email, hash_code(email, code)),
    )


# Mark the Gmail as verified and give manager access if HR invited this Gmail (all or nothing)
def finish_verification(email):
    # Open one connection, so all changes below are saved together or not at all
    connection = db.get_connection()
    cursor = connection.cursor()

    # Switch off all codes of this Gmail
    cursor.execute("UPDATE email_codes SET used = TRUE WHERE email = %s AND purpose = 'signup';", (email,))

    # Mark the account as verified
    cursor.execute("UPDATE users SET email_verified = TRUE WHERE email = %s;", (email,))

    # Look for a manager invite that HR made for this Gmail (Step 7 creates invites)
    cursor.execute(
        "SELECT invite_id FROM role_invites WHERE email = %s AND role = 'manager' AND status = 'pending' "
        "ORDER BY invite_id DESC LIMIT 1;",
        (email,),
    )
    invite = cursor.fetchone()

    # If there is an invite, make this person a manager and close the invite
    if invite is not None:
        cursor.execute("UPDATE users SET role = 'manager' WHERE email = %s AND role = 'candidate';", (email,))
        cursor.execute("UPDATE role_invites SET status = 'accepted' WHERE invite_id = %s;", (invite[0],))

    # Save all changes for good
    connection.commit()

    # Close the cursor and the connection
    cursor.close()
    connection.close()


# Check the code the person typed. Give back "" if it is right, or a message if not
def check_code(email, code):
    # Read the newest active code of this Gmail
    row = db.fetch_one(
        "SELECT code_id, code_hash, wrong_tries FROM email_codes WHERE email = %s AND purpose = 'signup' "
        "AND used = FALSE AND expires_at > NOW() ORDER BY code_id DESC LIMIT 1;",
        (email,),
    )

    # No row means there is no active code (it expired or was never sent)
    if row is None:
        return "There is no active code for this Gmail. Please ask for a new code."

    # Give the three values clear names
    code_id = row[0]
    saved_hash = row[1]
    wrong_tries = row[2]

    # Too many wrong guesses already
    if wrong_tries >= MAX_CODE_TRIES:
        return "Too many wrong tries. Please ask for a new code."

    # If the typed code does not match, count one more wrong try
    if not secrets.compare_digest(hash_code(email, code), saved_hash):
        db.execute("UPDATE email_codes SET wrong_tries = wrong_tries + 1 WHERE code_id = %s;", (code_id,))
        tries_left = MAX_CODE_TRIES - wrong_tries - 1
        return "Wrong code. You have " + str(tries_left) + " tries left."

    # The code is right, so verify the account
    finish_verification(email)
    return ""


# ---------- Login sessions (tickets) ----------

# Create a login ticket for a user and give back the real token (it goes into the cookie)
def make_session(user_id):
    # Make a long random token
    token = secrets.token_urlsafe(32)

    # INSERT saves only the scrambled token, together with the user number
    db.execute("INSERT INTO sessions (token, user_id) VALUES (%s, %s);", (hash_token(token), user_id))

    # Give the real token back
    return token


# Find the logged-in user for a token. Give back a dictionary, or None
def get_user_from_token(token):
    # JOIN matches each ticket with its user. We accept only tickets younger than SESSION_HOURS
    row = db.fetch_one(
        "SELECT u.user_id, u.name, u.email, u.role FROM sessions s JOIN users u ON s.user_id = u.user_id "
        "WHERE s.token = %s AND s.created_at > NOW() - make_interval(hours => %s) AND u.email_verified = TRUE;",
        (hash_token(token), config.SESSION_HOURS),
    )

    # No row means the ticket is wrong or too old
    if row is None:
        return None

    # Turn the row into a dictionary with clear names
    return {"user_id": row[0], "name": row[1], "email": row[2], "role": row[3]}


# Delete a login ticket (logout)
def delete_session(token):
    # DELETE removes the ticket row
    db.execute("DELETE FROM sessions WHERE token = %s;", (hash_token(token),))

# ---------- Forgot password ----------

# Can we send a new reset code now? We refuse if one was already made in the last minute
def can_send_reset_code(email):
    row = db.fetch_one(
        "SELECT code_id FROM email_codes WHERE email = %s AND purpose = 'reset' AND used = FALSE "
        "AND expires_at > NOW() + INTERVAL '9 minutes' LIMIT 1;",
        (email,),
    )
    return row is None


# Save a new reset code (scrambled). Older reset codes of this Gmail are switched off first
def save_new_reset_code(email, code):
    db.execute(
        "UPDATE email_codes SET used = TRUE WHERE email = %s AND purpose = 'reset' AND used = FALSE;",
        (email,),
    )
    db.execute(
        "INSERT INTO email_codes (email, code_hash, purpose, expires_at) "
        "VALUES (%s, %s, 'reset', NOW() + INTERVAL '10 minutes');",
        (email, hash_code(email, code)),
    )


# Check the reset code. Give back "" if it is right, or a message if not (does NOT use up the code)
def check_reset_code(email, code):
    row = db.fetch_one(
        "SELECT code_id, code_hash, wrong_tries FROM email_codes WHERE email = %s AND purpose = 'reset' "
        "AND used = FALSE AND expires_at > NOW() ORDER BY code_id DESC LIMIT 1;",
        (email,),
    )
    if row is None:
        return "There is no active code for this Gmail. Please ask for a new code."

    code_id = row[0]
    saved_hash = row[1]
    wrong_tries = row[2]

    if wrong_tries >= MAX_CODE_TRIES:
        return "Too many wrong tries. Please ask for a new code."

    if not secrets.compare_digest(hash_code(email, code), saved_hash):
        db.execute("UPDATE email_codes SET wrong_tries = wrong_tries + 1 WHERE code_id = %s;", (code_id,))
        tries_left = MAX_CODE_TRIES - wrong_tries - 1
        return "Wrong code. You have " + str(tries_left) + " tries left."

    return ""


# Save the new password, switch off the reset codes, and log the user out everywhere (all or nothing)
def finish_password_reset(email, password):
    salt = make_salt()
    hashed = hash_password(password, salt)

    connection = db.get_connection()
    cursor = connection.cursor()

    cursor.execute("UPDATE email_codes SET used = TRUE WHERE email = %s AND purpose = 'reset';", (email,))
    cursor.execute(
        "UPDATE users SET password_hash = %s, salt = %s WHERE email = %s;",
        (hashed, salt, email),
    )
    # Old login tickets stop working, so anyone who had the old password is logged out
    cursor.execute(
        "DELETE FROM sessions WHERE user_id = (SELECT user_id FROM users WHERE email = %s);",
        (email,),
    )

    connection.commit()
    cursor.close()
    connection.close()