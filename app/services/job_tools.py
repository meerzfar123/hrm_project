# Import our database helper file and the date tool
from app import database as db
import datetime


# Make sure the offer fields exist before the HR offer step uses them.
# This is safe to run every time because PostgreSQL uses IF NOT EXISTS.
def ensure_offer_columns():
    # Open a database connection
    connection = db.get_connection()

    # Create a cursor for sending SQL commands
    cursor = connection.cursor()

    try:
        # Add the offer salary column if it does not already exist
        cursor.execute(
            "ALTER TABLE candidates ADD COLUMN IF NOT EXISTS offer_salary NUMERIC(12, 2);"
        )

        # Add the joining date column if it does not already exist
        cursor.execute(
            "ALTER TABLE candidates ADD COLUMN IF NOT EXISTS joining_date DATE;"
        )

        # Save the database changes
        connection.commit()

    finally:
        # Close the cursor
        cursor.close()

        # Close the database connection
        connection.close()


# The longest text allowed in each job field
JOB_LIMITS = {
    "title": 150,
    "department": 100,
    "location": 100,
    "salary_range": 100,
    "description": 4000,
    "requirements": 4000,
    "benefits": 2000,
}


# Create the offer columns if this is an older database
ensure_offer_columns()


# Check the deadline text
# Give back an error message and a cleaned date
def parse_deadline(text):
    # An empty deadline is allowed
    if text == "":
        return "", None

    # Try to read the date
    try:
        day = datetime.date.fromisoformat(text)

    # The text was not a valid date
    except ValueError:
        return "The deadline must be a date like 2026-12-31.", None

    # A deadline in the past is not allowed
    if day < datetime.date.today():
        return "The deadline cannot be in the past.", None

    # Return the date in standard database format
    return "", day.isoformat()


# Check the length of every job field
def check_lengths(form):
    # Check every field one by one
    for field in JOB_LIMITS:

        # If the field is too long, return an error
        if len(form[field]) > JOB_LIMITS[field]:
            return (
                "The field '"
                + field
                + "' is too long (maximum "
                + str(JOB_LIMITS[field])
                + " characters)."
            )

    # Everything is okay
    return ""


# Save a new job
# Give back the new job_id
def create_job(user_id, form, status):
    # Open a database connection
    connection = db.get_connection()

    # Create a cursor for SQL commands
    cursor = connection.cursor()

    # Insert the new job into the jobs table
    cursor.execute(
        "INSERT INTO jobs "
        "(title, department, salary_range, location, description, requirements, benefits, deadline, created_by, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        "RETURNING job_id;",
        (
            form["title"],
            form["department"],
            form["salary_range"],
            form["location"],
            form["description"],
            form["requirements"],
            form["benefits"],
            form["deadline"],
            user_id,
            status,
        ),
    )

    # Read the new job ID
    new_id = cursor.fetchone()[0]

    # Save the new job
    connection.commit()

    # Close the cursor
    cursor.close()

    # Close the connection
    connection.close()

    # Give the new ID back
    return new_id


# Change an existing draft or rejected job
def update_job(job_id, form, status):
    # Update only jobs that are still drafts or rejected
    return db.execute(
        "UPDATE jobs SET "
        "title = %s, "
        "department = %s, "
        "salary_range = %s, "
        "location = %s, "
        "description = %s, "
        "requirements = %s, "
        "benefits = %s, "
        "deadline = %s, "
        "status = %s, "
        "reject_reason = NULL "
        "WHERE job_id = %s "
        "AND status IN ('draft', 'rejected');",
        (
            form["title"],
            form["department"],
            form["salary_range"],
            form["location"],
            form["description"],
            form["requirements"],
            form["benefits"],
            form["deadline"],
            status,
            job_id,
        ),
    )


# Read one job
# Give back a dictionary or None
def get_job(job_id):
    # Read the requested job
    row = db.fetch_one(
        "SELECT job_id, title, department, salary_range, location, description, "
        "requirements, benefits, deadline, created_by, status, reject_reason "
        "FROM jobs WHERE job_id = %s;",
        (job_id,),
    )

    # No job was found
    if row is None:
        return None

    # Convert the database row into an easy dictionary
    return {
        "job_id": row[0],
        "title": row[1],
        "department": row[2] or "",
        "salary_range": row[3] or "",
        "location": row[4] or "",
        "description": row[5] or "",
        "requirements": row[6] or "",
        "benefits": row[7] or "",
        "deadline": str(row[8]) if row[8] else "",
        "created_by": row[9],
        "status": row[10],
        "reject_reason": row[11] or "",
    }


# Give back all jobs, newest first
def list_jobs():
    # Read the main job information
    rows = db.fetch_all(
        "SELECT job_id, title, department, location, status, deadline, created_by "
        "FROM jobs ORDER BY job_id DESC;"
    )

    # Start an empty list
    jobs = []

    # Convert every database row into a dictionary
    for row in rows:
        jobs.append({
            "job_id": row[0],
            "title": row[1],
            "department": row[2] or "",
            "location": row[3] or "",
            "status": row[4],
            "deadline": str(row[5]) if row[5] else "",
            "created_by": row[6],
        })

    # Give the list back
    return jobs


# ---------------------------------------------------------
# HR JOB MANAGEMENT
# ---------------------------------------------------------


# Close a published job
# A closed job disappears from the public Careers page
def close_job(job_id, user_id):
    # Change published to closed only when this HR owns the job
    rows = db.execute(
        "UPDATE jobs SET status = 'closed' "
        "WHERE job_id = %s "
        "AND created_by = %s "
        "AND status = 'published';",
        (job_id, user_id),
    )

    # True means one job was successfully closed
    return rows == 1


# Open a previously closed job
# This makes the job visible on the public Careers page again
def open_job(job_id, user_id):
    # Change closed back to published only for the HR who created it
    rows = db.execute(
        "UPDATE jobs SET status = 'published' "
        "WHERE job_id = %s "
        "AND created_by = %s "
        "AND status = 'closed';",
        (job_id, user_id),
    )

    # True means one job was successfully opened
    return rows == 1


# Delete a job safely.
# This allows draft, rejected, and closed jobs to be permanently deleted.
def delete_job(job_id, user_id):

    # First check that this HR owns the job.
    job = db.fetch_one(
        "SELECT status FROM jobs "
        "WHERE job_id = %s AND created_by = %s;",
        (job_id, user_id),
    )

    # If the job does not exist or belongs to another HR, stop here.
    if job is None:
        return "not_found"

    # Get the job status.
    status = job[0]

    # Published jobs must still be closed before they can be deleted.
    if status == "published":
        return "published"

    # Jobs waiting for manager approval cannot be deleted.
    if status == "pending_approval":
        return "pending"

    # Delete answers belonging to candidates of this job.
    db.execute(
        "DELETE FROM candidate_answers "
        "WHERE candidate_id IN "
        "(SELECT candidate_id FROM candidates WHERE job_id = %s);",
        (job_id,),
    )

    # Delete queries belonging to candidates of this job.
    db.execute(
        "DELETE FROM candidate_queries "
        "WHERE candidate_id IN "
        "(SELECT candidate_id FROM candidates WHERE job_id = %s);",
        (job_id,),
    )

    # Delete interviews belonging to candidates of this job.
    db.execute(
        "DELETE FROM interviews "
        "WHERE candidate_id IN "
        "(SELECT candidate_id FROM candidates WHERE job_id = %s);",
        (job_id,),
    )

    # Delete offers belonging to candidates of this job.
    db.execute(
        "DELETE FROM offers "
        "WHERE candidate_id IN "
        "(SELECT candidate_id FROM candidates WHERE job_id = %s);",
        (job_id,),
    )

    # Now delete the candidates belonging to this job.
    db.execute(
        "DELETE FROM candidates "
        "WHERE job_id = %s;",
        (job_id,),
    )

    # Delete the questions belonging to this job.
    db.execute(
        "DELETE FROM job_questions "
        "WHERE job_id = %s;",
        (job_id,),
    )

    # Delete notifications belonging to this job.
    db.execute(
        "DELETE FROM notifications "
        "WHERE job_id = %s;",
        (job_id,),
    )

    # Finally delete the job itself.
    rows = db.execute(
        "DELETE FROM jobs "
        "WHERE job_id = %s "
        "AND created_by = %s;",
        (job_id, user_id),
    )

    # If one job was deleted, report success.
    if rows == 1:
        return "deleted"

    # Something unexpected prevented the deletion.
    return "error"

# Tell every manager that a job waits for approval
def notify_managers(job_id, title):
    # Insert a notification for the manager role
    db.execute(
        "INSERT INTO notifications (to_role, message, job_id) "
        "VALUES ('manager', %s, %s);",
        (
            "New job waiting for your approval: " + title,
            job_id,
        ),
    )


# Give back the questions of a job
def get_questions(job_id):
    # Read the questions in their saved order
    rows = db.fetch_all(
        "SELECT question_text FROM job_questions "
        "WHERE job_id = %s ORDER BY question_id;",
        (job_id,),
    )

    # Start an empty list
    questions = []

    # Add every question text to the list
    for row in rows:
        questions.append(row[0])

    # Give the questions back
    return questions


# Replace all questions of a job
def save_questions(job_id, questions):
    # Open one connection so all question changes happen together
    connection = db.get_connection()

    # Create a cursor
    cursor = connection.cursor()

    # Remove the old questions
    cursor.execute(
        "DELETE FROM job_questions WHERE job_id = %s;",
        (job_id,),
    )

    # Add the new questions
    for text in questions:
        cursor.execute(
            "INSERT INTO job_questions "
            "(job_id, question_text) "
            "VALUES (%s, %s);",
            (job_id, text),
        )

    # Save all changes
    connection.commit()

    # Close the cursor
    cursor.close()

    # Close the connection
    connection.close()


# Send a draft or rejected job to the manager
def submit_job(job_id):
    # Change the job to pending approval
    rows_changed = db.execute(
        "UPDATE jobs SET status = 'pending_approval', reject_reason = NULL "
        "WHERE job_id = %s "
        "AND status IN ('draft', 'rejected');",
        (job_id,),
    )

    # True means the job was sent
    return rows_changed == 1


# Give back jobs waiting for manager approval
def list_pending_jobs():
    # Read pending jobs and the HR name
    rows = db.fetch_all(
        "SELECT j.job_id, j.title, j.department, j.location, u.name "
        "FROM jobs j "
        "LEFT JOIN users u ON j.created_by = u.user_id "
        "WHERE j.status = 'pending_approval' "
        "ORDER BY j.job_id DESC;"
    )

    # Start an empty list
    jobs = []

    # Convert every row into a dictionary
    for row in rows:
        jobs.append({
            "job_id": row[0],
            "title": row[1],
            "department": row[2] or "",
            "location": row[3] or "",
            "created_by_name": row[4] or "",
        })

    # Give the jobs back
    return jobs


# Approve a pending job
def approve_job(job_id, manager_id):
    # Publish the job only while it is pending
    rows = db.execute(
        "UPDATE jobs SET status = 'published', "
        "approved_by = %s, reject_reason = NULL "
        "WHERE job_id = %s AND status = 'pending_approval';",
        (manager_id, job_id),
    )

    # True means approval worked
    return rows == 1


# Reject a pending job
def reject_job(job_id, manager_id, reason):
    # Reject only a job that is still waiting
    rows = db.execute(
        "UPDATE jobs SET status = 'rejected', "
        "approved_by = %s, reject_reason = %s "
        "WHERE job_id = %s AND status = 'pending_approval';",
        (manager_id, reason, job_id),
    )

    # True means rejection worked
    return rows == 1


# Tell HR what the manager decided
def notify_hr(job_id, hr_user_id, message):
    # Insert the notification
    db.execute(
        "INSERT INTO notifications "
        "(to_user_id, message, job_id) "
        "VALUES (%s, %s, %s);",
        (hr_user_id, message, job_id),
    )


# Mark manager notifications as read
def mark_job_notifications_read(job_id):
    # Mark notifications for this job as read
    db.execute(
        "UPDATE notifications SET is_read = TRUE "
        "WHERE job_id = %s AND to_role = 'manager';",
        (job_id,),
    )


# Give back published jobs whose deadline has not passed
def list_published_jobs():
    # Read jobs that candidates are allowed to see
    rows = db.fetch_all(
        "SELECT job_id, title, department, location, salary_range, deadline "
        "FROM jobs "
        "WHERE status = 'published' "
        "AND (deadline IS NULL OR deadline >= CURRENT_DATE) "
        "ORDER BY job_id DESC;"
    )

    # Convert database rows into dictionaries
    return [{
        "job_id": r[0],
        "title": r[1],
        "department": r[2] or "",
        "location": r[3] or "",
        "salary_range": r[4] or "",
        "deadline": str(r[5]) if r[5] else "",
    } for r in rows]


# Check whether a user already applied
def has_applied(user_id, job_id):
    # Search for an existing application
    row = db.fetch_one(
        "SELECT candidate_id FROM candidates "
        "WHERE user_id = %s AND job_id = %s;",
        (user_id, job_id),
    )

    # True means an application already exists
    return row is not None


# Make sure the manual candidate source column exists
def ensure_manual_candidate_columns():
    # Add the source column if the database is older
    db.execute(
        "ALTER TABLE candidates "
        "ADD COLUMN IF NOT EXISTS candidate_source TEXT;"
    )


# Save a candidate entered manually by HR
def create_manual_candidate(
    job_id,
    name,
    email,
    phone,
    experience_years,
    education,
    expected_salary,
    candidate_source,
    cv_text,
    cv_file_path,
    score,
    screening_result,
):
    # Make sure the source column exists
    ensure_manual_candidate_columns()

    # Open a database connection
    connection = db.get_connection()

    # Create a cursor
    cursor = connection.cursor()

    # Insert the HR-sourced candidate
    cursor.execute(
        "INSERT INTO candidates "
        "(user_id, job_id, name, email, phone, cv_text, cv_file_path, "
        "experience_years, education, expected_salary, score, "
        "screening_result, status, candidate_source) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'applied', %s) "
        "RETURNING candidate_id;",
        (
            None,
            job_id,
            name,
            email,
            phone,
            cv_text,
            cv_file_path,
            experience_years,
            education,
            expected_salary,
            score,
            screening_result,
            candidate_source,
        ),
    )

    # Read the new candidate ID
    candidate_id = cursor.fetchone()[0]

    # Save the candidate
    connection.commit()

    # Close the cursor
    cursor.close()

    # Close the connection
    connection.close()

    # Give the candidate ID back
    return candidate_id


# Save a normal candidate application
def create_application(user, job_id, form, cv_file, score, result, answers):
    # Open a database connection
    connection = db.get_connection()

    # Create a cursor
    cursor = connection.cursor()

    # Save the application
    cursor.execute(
        "INSERT INTO candidates "
        "(user_id, job_id, name, email, phone, cv_text, cv_file_path, "
        "experience_years, education, expected_salary, score, "
        "screening_result, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'applied') "
        "RETURNING candidate_id;",
        (
            user.get("user_id"),
            job_id,
            user["name"],
            user["email"],
            user.get("phone", ""),
            form["cv_text"],
            cv_file,
            form["experience_years"],
            form["education"],
            form["expected_salary"],
            score,
            result,
        ),
    )

    # Read the new candidate ID
    candidate_id = cursor.fetchone()[0]

    # Save every questionnaire answer
    for question_id, text in answers:
        cursor.execute(
            "INSERT INTO candidate_answers "
            "(candidate_id, question_id, answer_text) "
            "VALUES (%s, %s, %s);",
            (candidate_id, question_id, text),
        )

    # Save everything
    connection.commit()

    # Close the cursor
    cursor.close()

    # Close the connection
    connection.close()

    # Give back the candidate ID
    return candidate_id


# Give back job questions with their IDs
def get_questions_with_ids(job_id):
    # Read question IDs and text
    rows = db.fetch_all(
        "SELECT question_id, question_text "
        "FROM job_questions "
        "WHERE job_id = %s "
        "ORDER BY question_id;",
        (job_id,),
    )

    # Convert rows to tuples
    return [(r[0], r[1]) for r in rows]


# The applications of one candidate
#def list_my_applications(user_id):
#    # Read the candidate's applications
#    rows = db.fetch_all(
#        "SELECT c.candidate_id, j.title, c.status, i.interview_date "
#        "FROM candidates c "
#        "JOIN jobs j ON c.job_id = j.job_id "
#        "LEFT JOIN interviews i ON i.candidate_id = c.candidate_id "
#        "WHERE c.user_id = %s "
#        "ORDER BY c.candidate_id DESC;",
#        (user_id,),
#   )
#
#    # Convert rows to dictionaries
#    return [{
#        "candidate_id": r[0],
#        "title": r[1],
#        "status": r[2],
#        "interview": str(r[3])[:16] if r[3] else "",
#    } for r in rows]


# Read one application
# Read one application.
def get_application(candidate_id):
    # Read the candidate details from the database.
    # candidate_source is included so the HR profile can show where the candidate came from.
    r = db.fetch_one(
        "SELECT candidate_id, job_id, name, email, experience_years, education, "
        "expected_salary, score, screening_result, status, cv_file_path, phone, "
        "user_id, candidate_source "
        "FROM candidates WHERE candidate_id = %s;",
        (candidate_id,),
    )

    # Return nothing if the candidate does not exist.
    if r is None:
        return None

    # Return the candidate information as a simple dictionary.
    return {
        "candidate_id": r[0],
        "job_id": r[1],
        "name": r[2],
        "email": r[3],
        "experience_years": r[4],
        "education": r[5] or "",
        "expected_salary": r[6],
        "score": r[7] or 0,
        "screening_result": r[8] or "",
        "status": r[9],
        "cv_file_path": r[10] or "",
        "phone": r[11] or "",
        "is_guest": r[12] is None,

        # Show the candidate source.
        # Public applicants have an empty source, so we label them clearly.
        "candidate_source": r[13] or "Public Application",
    }

# Read the answers of one application
def get_answers(candidate_id):
    # Read question and answer together
    rows = db.fetch_all(
        "SELECT q.question_text, a.answer_text "
        "FROM candidate_answers a "
        "JOIN job_questions q ON a.question_id = q.question_id "
        "WHERE a.candidate_id = %s "
        "ORDER BY q.question_id;",
        (candidate_id,),
    )

    # Return question/answer pairs
    return [(r[0], r[1] or "") for r in rows]


# Change the status of an application
def set_application_status(candidate_id, status):
    # Update the candidate status
    return db.execute(
        "UPDATE candidates SET status = %s "
        "WHERE candidate_id = %s;",
        (status, candidate_id),
    ) == 1


# Save interview feedback and rating
def save_feedback(candidate_id, feedback, rating):
    # Update the interview record
    return db.execute(
        "UPDATE interviews SET feedback = %s, rating = %s "
        "WHERE candidate_id = %s;",
        (feedback, rating, candidate_id),
    ) == 1


# Save an interview date and instructions
def schedule_interview(candidate_id, when_text, instructions):
    # Check whether an interview already exists
    existing = db.fetch_one(
        "SELECT interview_id FROM interviews "
        "WHERE candidate_id = %s;",
        (candidate_id,),
    )

    # Create a new interview if none exists
    if existing is None:
        db.execute(
            "INSERT INTO interviews "
            "(candidate_id, interview_date, instructions) "
            "VALUES (%s, %s, %s);",
            (candidate_id, when_text, instructions),
        )

    # Otherwise update the existing interview
    else:
        db.execute(
            "UPDATE interviews SET interview_date = %s, instructions = %s "
            "WHERE interview_id = %s;",
            (when_text, instructions, existing[0]),
        )


# Give back the interview of a candidate
def get_interview(candidate_id):
    # Read the interview
    r = db.fetch_one(
        "SELECT interview_id, interview_date, feedback, rating, instructions "
        "FROM interviews WHERE candidate_id = %s;",
        (candidate_id,),
    )

    # No interview exists
    if r is None:
        return None

    # Return the interview information
    return {
        "interview_id": r[0],
        "date": str(r[1])[:16],
        "date_input": str(r[1])[:16].replace(" ", "T"),
        "feedback": r[2] or "",
        "rating": r[3],
        "instructions": r[4] or "",
    }

# Get all shortlisted candidates who already have a scheduled interview.
def list_selected_interviews():

    # Read the candidate, job and existing interview information.
    rows = db.fetch_all(
        "SELECT c.name, j.title, i.interview_date, i.instructions "
        "FROM candidates c "
        "JOIN jobs j ON c.job_id = j.job_id "
        "JOIN interviews i ON i.candidate_id = c.candidate_id "
        "WHERE c.status = 'shortlisted' "
        "AND i.interview_date IS NOT NULL "
        "ORDER BY i.interview_date;"
    )

    # Start an empty list for the Interviews box.
    result = []

    # Go through every shortlisted candidate with a scheduled interview.
    for r in rows:

        # Format the interview date and time for the HR screen.
        if r[2] is not None:
            interview_datetime = r[2].strftime("%d %b %Y • %I:%M %p")
        else:
            interview_datetime = ""

        # Add this candidate's information to the result list.
        result.append({
            "candidate": r[0],
            "job": r[1],
            "interview_datetime": interview_datetime,
            "description": r[3] or "",
        })

    # Give the complete interview list back to the HR page.
    return result


# The applications of one job
def list_applications(job_id, status=""):
    # Start the SQL query.
    # We also read candidate_source so HR can see where the candidate came from.
    sql = (
        "SELECT c.candidate_id, c.name, c.email, c.experience_years, "
        "c.score, c.status, i.interview_date, c.candidate_source "
        "FROM candidates c "
        "LEFT JOIN interviews i ON i.candidate_id = c.candidate_id "
        "WHERE c.job_id = %s"
    )

    # Start the query parameters with the selected job ID.
    params = [job_id]

    # Add a status filter when HR selects a specific tab.
    if status != "":
        sql += " AND c.status = %s"
        params.append(status)

    # Keep the strongest CV scores at the top.
    sql += " ORDER BY c.score DESC NULLS LAST, c.candidate_id;"

    # Run the SQL query.
    rows = db.fetch_all(sql, tuple(params))

    # Convert database rows into simple dictionaries for the HTML page.
    return [{
        "candidate_id": r[0],
        "name": r[1],
        "email": r[2],
        "experience_years": r[3],
        "score": r[4] if r[4] is not None else 0,
        "status": r[5],
        "interview": str(r[6])[:16] if r[6] else "",

        # Public applicants have no candidate_source.
        # HR-sourced candidates have values such as LinkedIn or Referral.
        "candidate_source": r[7] or "Public Application",
    } for r in rows]
def count_applications(job_id):
    # Read the count of each status
    rows = db.fetch_all(
        "SELECT status, COUNT(*) "
        "FROM candidates "
        "WHERE job_id = %s "
        "GROUP BY status;",
        (job_id,),
    )

    # Start the counters
    counts = {
        "applied": 0,
        "shortlisted": 0,
        "rejected": 0,
        "selected": 0,
        "offer_pending": 0,
        "offer_rejected": 0,
        "hired": 0,
    }

    # Put database counts into the dictionary
    for status, number in rows:
        counts[status] = number

    # Calculate the total
    counts["all"] = sum(counts.values())

    # Give counts back
    return counts


# Check whether an application belongs to a user
def owns_application(user_id, candidate_id):
    # Search for this user/candidate combination
    row = db.fetch_one(
        "SELECT 1 FROM candidates "
        "WHERE candidate_id = %s AND user_id = %s;",
        (candidate_id, user_id),
    )

    # True means this application belongs to the user
    return row is not None


# Add a candidate question
def add_query(candidate_id, question):
    # Save the candidate's question
    db.execute(
        "INSERT INTO candidate_queries (candidate_id, question) "
        "VALUES (%s, %s);",
        (candidate_id, question),
    )


# Count unanswered questions
def count_open_queries(candidate_id):
    # Count questions without a reply
    row = db.fetch_one(
        "SELECT COUNT(*) FROM candidate_queries "
        "WHERE candidate_id = %s AND reply IS NULL;",
        (candidate_id,),
    )

    # Give the count back
    return row[0]


# List candidate questions
def list_queries(candidate_id):
    # Read the questions and replies
    rows = db.fetch_all(
        "SELECT query_id, question, reply, asked_at, replied_at "
        "FROM candidate_queries "
        "WHERE candidate_id = %s "
        "ORDER BY query_id;",
        (candidate_id,),
    )

    # Convert rows into dictionaries
    return [{
        "query_id": r[0],
        "question": r[1],
        "reply": r[2] or "",
        "asked": str(r[3])[:16],
        "replied": str(r[4])[:16] if r[4] else "",
    } for r in rows]


# Reply to a candidate question
def reply_query(query_id, candidate_id, reply):
    # Update only the requested candidate's question
    return db.execute(
        "UPDATE candidate_queries "
        "SET reply = %s, replied_at = NOW() "
        "WHERE query_id = %s AND candidate_id = %s;",
        (reply, query_id, candidate_id),
    ) == 1


# Shortlisted applications of a candidate
def list_my_shortlisted(user_id):
    # Read shortlisted applications
    rows = db.fetch_all(
        "SELECT c.candidate_id, j.title, i.interview_date, i.instructions "
        "FROM candidates c "
        "JOIN jobs j ON c.job_id = j.job_id "
        "LEFT JOIN interviews i ON i.candidate_id = c.candidate_id "
        "WHERE c.user_id = %s AND c.status = 'shortlisted' "
        "ORDER BY c.candidate_id DESC;",
        (user_id,),
    )

    # Start the result list
    result = []

    # Add each shortlisted application
    for r in rows:
        result.append({
            "candidate_id": r[0],
            "title": r[1],
            "interview": str(r[2])[:16] if r[2] else "",
            "instructions": r[3] or "",
            "queries": list_queries(r[0]),
        })

    # Give the result back
    return result

# The HR dashboard data.
def hr_dashboard(user_id):

    # Read all jobs created by this HR.
    jobs = db.fetch_all(
        "SELECT j.job_id, j.title, j.status, "
        "(SELECT COUNT(*) FROM candidates c WHERE c.job_id = j.job_id), "
        "(SELECT COUNT(*) FROM candidates c "
        "WHERE c.job_id = j.job_id AND c.status = 'shortlisted'), "
        "(SELECT COUNT(*) FROM candidate_queries q "
        "JOIN candidates c ON q.candidate_id = c.candidate_id "
        "WHERE c.job_id = j.job_id AND q.reply IS NULL) "
        "FROM jobs j "
        "WHERE j.created_by = %s "
        "ORDER BY j.job_id DESC;",
        (user_id,),
    )

    # Count all active published jobs for the top dashboard card.
    active_jobs_row = db.fetch_one(
        "SELECT COUNT(*) FROM jobs "
        "WHERE created_by = %s AND status = 'published';",
        (user_id,),
    )

    # Count every candidate/application belonging to this HR's jobs.
    applications_row = db.fetch_one(
        "SELECT COUNT(*) "
        "FROM candidates c "
        "JOIN jobs j ON c.job_id = j.job_id "
        "WHERE j.created_by = %s;",
        (user_id,),
    )

    # Count all shortlisted candidates belonging to this HR's jobs.
    shortlisted_row = db.fetch_one(
        "SELECT COUNT(*) "
        "FROM candidates c "
        "JOIN jobs j ON c.job_id = j.job_id "
        "WHERE j.created_by = %s "
        "AND c.status = 'shortlisted';",
        (user_id,),
    )

    # Count candidates who have an interview record.
    interviews_row = db.fetch_one(
        "SELECT COUNT(*) "
        "FROM interviews i "
        "JOIN candidates c ON i.candidate_id = c.candidate_id "
        "JOIN jobs j ON c.job_id = j.job_id "
        "WHERE j.created_by = %s;",
        (user_id,),
    )

    # Read the overall dashboard numbers.
    dashboard_counts = {
        "active_jobs": active_jobs_row[0] if active_jobs_row else 0,
        "applications": applications_row[0] if applications_row else 0,
        "shortlisted": shortlisted_row[0] if shortlisted_row else 0,
        "interviews": interviews_row[0] if interviews_row else 0,
    }

    # Read shortlisted candidates for the recruitment pipeline.
    shortlisted = db.fetch_all(
        "SELECT c.job_id, c.candidate_id, c.name, c.email, "
        "c.score, i.interview_date "
        "FROM candidates c "
        "JOIN jobs j ON c.job_id = j.job_id "
        "LEFT JOIN interviews i ON i.candidate_id = c.candidate_id "
        "WHERE j.created_by = %s "
        "AND c.status = 'shortlisted' "
        "ORDER BY i.interview_date NULLS LAST, "
        "c.score DESC NULLS LAST;",
        (user_id,),
    )

    # Create a dictionary to group shortlisted candidates by job.
    by_job = {}

    # Go through every shortlisted candidate.
    for r in shortlisted:

        # Create an empty list for this job if needed.
        if r[0] not in by_job:
            by_job[r[0]] = []

        # Add this candidate to the correct job.
        by_job[r[0]].append({
            "candidate_id": r[1],
            "name": r[2],
            "email": r[3],
            "score": r[4] or 0,
            "interview": str(r[5])[:16] if r[5] else "",
        })

    # Start the dashboard job list.
    result = []

    # Go through every job.
    for r in jobs:

        # Hide empty non-published jobs from the dashboard.
        if r[3] == 0 and r[2] != "published":
            continue

        # Add this job to the dashboard.
        result.append({
            "job_id": r[0],
            "title": r[1],
            "status": r[2],
            "total": r[3],
            "shortlisted": r[4],
            "open_queries": r[5],
            "shortlist": by_job.get(r[0], []),
        })

    # Return both the job data and the overall dashboard counts.
    return {
        "jobs": result,
        "counts": dashboard_counts,
    }
# Check whether a Gmail already applied
def has_applied_email(email, job_id):
    # Search by email and job
    row = db.fetch_one(
        "SELECT candidate_id FROM candidates "
        "WHERE LOWER(email) = LOWER(%s) AND job_id = %s;",
        (email, job_id),
    )

    # True means an application exists
    return row is not None


# Count recent application attempts from one IP
def count_recent_attempts(ip_address, minutes=60):
    # Count attempts during the requested time
    row = db.fetch_one(
        "SELECT COUNT(*) FROM apply_attempts "
        "WHERE ip_address = %s "
        "AND created_at > NOW() - make_interval(mins => %s);",
        (ip_address, minutes),
    )

    # Give the count back
    return row[0]


# Save one application attempt
def log_apply_attempt(ip_address):
    # Remove very old attempts
    db.execute(
        "DELETE FROM apply_attempts "
        "WHERE created_at < NOW() - INTERVAL '1 day';"
    )

    # Save the new attempt
    db.execute(
        "INSERT INTO apply_attempts (ip_address) VALUES (%s);",
        (ip_address,),
    )

# Give shortlisted candidates in ranking order and save the ranking in PostgreSQL.
def list_ranked_candidates(job_id):

    # First remove the old ranking for this job.
    # This prevents duplicate ranking rows every time the HR page is opened.
    db.execute(
        """
        DELETE FROM candidate_rankings
        WHERE job_id = %s;
        """,
        (job_id,),
    )

    # Read shortlisted candidates and their interview information.
    rows = db.fetch_all(
        """
        SELECT
            c.candidate_id,
            c.name,
            c.email,
            c.score,
            c.status,
            i.rating,
            i.feedback,
            i.interview_date
        FROM candidates c
        LEFT JOIN interviews i
            ON i.candidate_id = c.candidate_id
        WHERE c.job_id = %s
          AND c.status = 'shortlisted'
        ORDER BY
            i.rating DESC NULLS LAST,
            c.score DESC NULLS LAST,
            c.candidate_id ASC;
        """,
        (job_id,),
    )

    # Start an empty ranking list for the HR screen.
    ranked = []

    # Start ranking at number one.
    rank = 1

    # Go through every shortlisted candidate in ranking order.
    for row in rows:

        # Save this candidate's current ranking in PostgreSQL.
        db.execute(
            """
            INSERT INTO candidate_rankings
                (candidate_id, job_id, rank_position)
            VALUES (%s, %s, %s);
            """,
            (row[0], job_id, rank),
        )

        # Add the candidate information to the HR ranking screen.
        ranked.append({
            "rank": rank,
            "candidate_id": row[0],
            "name": row[1],
            "email": row[2],
            "score": row[3] if row[3] is not None else 0,
            "status": row[4],
            "rating": row[5],
            "feedback": row[6] or "",
            "interview": str(row[7])[:16] if row[7] else "",
        })

        # Move to the next ranking number.
        rank += 1

 # Save the offer salary, joining date, and offer status.
def save_offer(candidate_id, offer_salary, joining_date):

    # Update the candidate's offer information in the candidates table.
    candidate_updated = db.execute(
        """
        UPDATE candidates
        SET offer_salary = %s,
            joining_date = %s,
            status = 'offer_pending'
        WHERE candidate_id = %s;
        """,
        (offer_salary, joining_date, candidate_id),
    )

    # Stop if the candidate could not be updated.
    if candidate_updated != 1:
        return False

    # Check whether an offer record already exists for this candidate.
    existing_offer = db.fetch_one(
        """
        SELECT offer_id
        FROM offers
        WHERE candidate_id = %s;
        """,
        (candidate_id,),
    )

    # Create a new offer record if this candidate has no offer yet.
    if existing_offer is None:

        # Save all offer information into the offers table.
        db.execute(
            """
            INSERT INTO offers
                (candidate_id, offer_status, offered_salary, joining_date)
            VALUES (%s, %s, %s, %s);
            """,
            (
                candidate_id,
                "pending",
                offer_salary,
                joining_date,
            ),
        )

    # Update the existing offer record if one already exists.
    else:

        # Update the status, salary, and joining date in the offers table.
        db.execute(
            """
            UPDATE offers
            SET offer_status = %s,
                offered_salary = %s,
                joining_date = %s
            WHERE candidate_id = %s;
            """,
            (
                "pending",
                offer_salary,
                joining_date,
                candidate_id,
            ),
        )

    # Tell the calling function that the offer was saved successfully.
    return True

# Get the offer details of one candidate.
def get_offer(candidate_id):

    # Read the saved offer from the offers table.
    row = db.fetch_one(
        """
        SELECT offered_salary, joining_date, offer_status
        FROM offers
        WHERE candidate_id = %s
        ORDER BY offer_id DESC
        LIMIT 1;
        """,
        (candidate_id,),
    )

    # No offer found.
    if row is None:
        return None

    # Return the offer information in the same format
    # that the existing HR template already expects.
    return {
        "salary": row[0],
        "joining_date": str(row[1]) if row[1] else "",
        "status": row[2],
    }
    # No candidate found
    if row is None:
        return None

    # Return offer information
    return {
        "salary": row[0],
        "joining_date": str(row[1]) if row[1] else "",
        "status": row[2],
    }

# Create a secure token for the candidate's offer link.
def create_offer_token(candidate_id):

    # Import secrets because it creates a strong random token.
    import secrets

    # Create a long random token that is difficult to guess.
    token = secrets.token_urlsafe(32)

    # Save the token in the existing offers table.
    updated = db.execute(
        """
        UPDATE offers
        SET offer_token = %s
        WHERE candidate_id = %s
          AND offer_status = 'pending';
        """,
        (token, candidate_id),
    )

    # If one offer was updated, return the token.
    if updated == 1:
        return token

    # Return an empty value if no pending offer was found.
    return ""

# Get an offer using its secure token.
def get_offer_by_token(offer_token):

    # Read the offer and candidate information from the database.
    row = db.fetch_one(
        """
        SELECT
            o.offer_id,
            o.candidate_id,
            o.offer_status,
            o.offered_salary,
            o.joining_date,
            c.name,
            c.email,
            c.status,
            j.title
        FROM offers o
        JOIN candidates c
            ON c.candidate_id = o.candidate_id
        JOIN jobs j
            ON j.job_id = c.job_id
        WHERE o.offer_token = %s;
        """,
        (offer_token,),
    )

    # Return nothing if this token does not exist.
    if row is None:
        return None

    # Return the offer information in a simple dictionary.
    return {
        "offer_id": row[0],
        "candidate_id": row[1],
        "offer_status": row[2],
        "salary": row[3],
        "joining_date": str(row[4]) if row[4] else "",
        "name": row[5],
        "email": row[6],
        "candidate_status": row[7],
        "job_title": row[8],
    }

# Save the candidate's response to the offer.
def respond_to_offer(offer_token, response):

    # Only allow the two valid candidate responses.
    if response not in ("accepted", "rejected"):
        return False

    # Find the pending offer using its secure token.
    row = db.fetch_one(
        """
        SELECT candidate_id
        FROM offers
        WHERE offer_token = %s
          AND offer_status = 'pending';
        """,
        (offer_token,),
    )

    # Stop if the token is invalid or the offer is no longer pending.
    if row is None:
        return False

    # Get the candidate ID from the database result.
    candidate_id = row[0]

    # Save the candidate's response and response time.
    updated = db.execute(
        """
        UPDATE offers
        SET offer_status = %s,
            responded_at = CURRENT_TIMESTAMP
        WHERE offer_token = %s
          AND offer_status = 'pending';
        """,
        (response, offer_token),
    )

    # If the offer was updated successfully, update the candidate status too.
    if updated == 1:

        # Mark the candidate as hired when the offer is accepted.
        if response == "accepted":
            db.execute(
                """
                UPDATE candidates
                SET status = 'hired'
                WHERE candidate_id = %s;
                """,
                (candidate_id,),
            )

        # Mark the candidate as offer rejected when the offer is rejected.
        if response == "rejected":
            db.execute(
                """
                UPDATE candidates
                SET status = 'offer_rejected'
                WHERE candidate_id = %s;
                """,
                (candidate_id,),
            )

        # Tell the calling function that the response was saved.
        return True

    # Tell the calling function that nothing was changed.
    return False

# Get all candidates whose final status is hired.
def list_hired_candidates():

    # Read the hired candidate and job information from the database.
    rows = db.fetch_all(
        "SELECT c.name, j.title, c.email, c.phone, "
        "c.offer_salary, c.joining_date "
        "FROM candidates c "
        "JOIN jobs j ON c.job_id = j.job_id "
        "WHERE c.status = 'hired' "
        "ORDER BY c.joining_date;"
    )

    # Start an empty list for the Selected Candidates page.
    result = []

    # Go through every hired candidate.
    for r in rows:

        # Format the joining date if one exists.
        if r[5] is not None:
            joining_date = r[5].strftime("%d %b %Y")
        else:
            joining_date = ""

        # Add the candidate information to the result list.
        result.append({
            "candidate": r[0],
            "job": r[1],
            "email": r[2] or "",
            "phone": r[3] or "",
            "offer_salary": r[4] or "",
            "joining_date": joining_date,
        })

    # Return the complete hired candidate list.
    return result