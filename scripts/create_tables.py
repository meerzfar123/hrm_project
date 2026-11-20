import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import our helper file so we can use get_connection()
from app import database as db
# The names of all tables, in the order we delete them (tables that point to others go first)
drop_order = [
    "offers", "interviews", "candidate_answers", "notifications", "candidates",
    "job_questions", "jobs", "company_info", "sessions", "role_invites",
    "email_codes", "users",
]

# TABLE 1: users (one row per person who has an account)
create_users = """
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'candidate' CHECK (role IN ('candidate', 'hr', 'manager')),
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
"""

# TABLE 2: email_codes (the 6-digit codes we send to Gmail)
create_email_codes = """
CREATE TABLE email_codes (
    code_id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    purpose TEXT NOT NULL DEFAULT 'signup',
    expires_at TIMESTAMP NOT NULL,
    wrong_tries INTEGER NOT NULL DEFAULT 0,
    used BOOLEAN NOT NULL DEFAULT FALSE
);
"""

# TABLE 3: role_invites (HR invites a Gmail to become a manager)
create_role_invites = """
CREATE TABLE role_invites (
    invite_id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'manager',
    invited_by INTEGER REFERENCES users(user_id),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'removed')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
"""

# TABLE 4: sessions (one row for each logged-in person, the "login ticket")
create_sessions = """
CREATE TABLE sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
"""

# TABLE 5: company_info (the company details shown to candidates, only one row)
create_company_info = """
CREATE TABLE company_info (
    info_id SERIAL PRIMARY KEY,
    company_name TEXT,
    about_us TEXT,
    mission TEXT,
    address TEXT,
    website TEXT,
    contact_email TEXT,
    updated_by INTEGER REFERENCES users(user_id)
);
"""

# TABLE 6: jobs (one row per job vacancy)
create_jobs = """
CREATE TABLE jobs (
    job_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    department TEXT,
    salary_range TEXT,
    location TEXT,
    description TEXT,
    requirements TEXT,
    benefits TEXT,
    deadline DATE,
    poster_path TEXT,
    created_by INTEGER REFERENCES users(user_id),
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_approval', 'rejected', 'published')),
    reject_reason TEXT,
    approved_by INTEGER REFERENCES users(user_id)
);
"""

# TABLE 7: job_questions (the questionnaire of each job)
create_job_questions = """
CREATE TABLE job_questions (
    question_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    question_text TEXT NOT NULL
);
"""

# TABLE 8: candidates (one row per application)
create_candidates = """
CREATE TABLE candidates (
    candidate_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    job_id INTEGER REFERENCES jobs(job_id),
    name TEXT NOT NULL,
    email TEXT,
    cv_text TEXT,
    cv_file_path TEXT,
    experience_years INTEGER,
    education TEXT,
    expected_salary INTEGER,
    score INTEGER,
    screening_result TEXT,
    status TEXT NOT NULL DEFAULT 'applied'
);
"""

# TABLE 9: candidate_answers (the answers a candidate gave to the questionnaire)
create_candidate_answers = """
CREATE TABLE candidate_answers (
    answer_id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES job_questions(question_id),
    answer_text TEXT
);
"""

# TABLE 10: notifications (messages shown on the screens, for example "new job to approve")
create_notifications = """
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    to_role TEXT,
    to_user_id INTEGER REFERENCES users(user_id),
    message TEXT NOT NULL,
    job_id INTEGER REFERENCES jobs(job_id) ON DELETE CASCADE,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
"""

# TABLE 11: interviews (same idea as before)
create_interviews = """
CREATE TABLE interviews (
    interview_id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(candidate_id),
    interview_date TIMESTAMP,
    feedback TEXT,
    rating INTEGER
);
"""

# TABLE 12: offers (same idea as before)
create_offers = """
CREATE TABLE offers (
    offer_id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(candidate_id),
    offer_status TEXT NOT NULL DEFAULT 'pending' CHECK (offer_status IN ('pending', 'accepted', 'rejected'))
);
"""

# A starter row for the company information, so the page is not empty. HR edits it later
insert_company = """
INSERT INTO company_info (company_name, about_us, mission, address, website, contact_email)
VALUES ('Our Company', 'Write a short description of your company here.', 'Write your mission here.',
        'Your address', 'www.example.com', 'hr@example.com');
"""

# The create commands in the right order: parents first, because children point to them
create_list = [
    create_users, create_email_codes, create_role_invites, create_sessions,
    create_company_info, create_jobs, create_job_questions, create_candidates,
    create_candidate_answers, create_notifications, create_interviews, create_offers,
]

# Ask for a safe confirmation, because this file deletes ALL data in hrm_db
answer = input("This DELETES all tables and data in hrm_db and builds new ones. Type YES to continue: ")

# If the person did not type exactly YES, stop and change nothing
if answer != "YES":
    print("Cancelled. Nothing was changed.")
else:
    # "try" means: attempt this code, and if something goes wrong, jump to "except"
    try:
        # Open a connection to hrm_db and create a cursor (the "pen" that sends SQL)
        connection = db.get_connection()
        cursor = connection.cursor()

        # Delete the old tables one by one (the names come from our own list above, so this is safe)
        for table_name in drop_order:
            cursor.execute("DROP TABLE IF EXISTS " + table_name + " CASCADE;")

        # Create the 12 new tables one by one
        for sql in create_list:
            cursor.execute(sql)

        # Add the starter company row
        cursor.execute(insert_company)

        # Save everything for good. If anything failed before this line, nothing is saved
        connection.commit()

        # Ask PostgreSQL for the list of all tables, to prove the new ones exist
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
        rows = cursor.fetchall()

        # Print the table names, one per line
        print("Tables now in hrm_db:")
        for row in rows:
            print(" -", row[0])

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        # Tell us that everything worked
        print("Done. The database is ready for Step 4.")

    # If anything above failed, the code jumps here and "error" holds the reason
    except Exception as error:
        print("Changing the database FAILED. Nothing was changed.")
        print("Reason:", error)