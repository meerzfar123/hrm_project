# Import os, a standard library that helps build file paths
import os
import datetime

# Import psycopg2, which we need to catch one database error (a Gmail saved twice)
import psycopg2

# Import quote, which makes text safe to put inside a web address
from urllib.parse import quote

# Import FastAPI, Request (the visitor's request), Form (reads form fields), files and background tasks
from fastapi import APIRouter, FastAPI, Request, Form, File, UploadFile, BackgroundTasks

# Import the responses: redirect to another page, JSON data, and file download
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse

# Import the tool that fills HTML templates with data
from fastapi.templating import Jinja2Templates

# Import the tool that serves static files such as CSS
from fastapi.staticfiles import StaticFiles


# Import our own files
from app import database as db
from app import config
from app.services import auth_tools
from app.services import access_tools
from app.services import email_tools
from app.services import job_tools
from app.services import ai_tools
from app.services import cv_tools
# Import the application configuration values.
import app.config as config
# Find the folder where this file (api.py) lives, so paths work from any terminal folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The full paths of the templates and static folders
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# The name of the login cookie
SESSION_COOKIE = "hrm_session"
# Guest apply: how many apply attempts one IP address may make per hour
APPLY_LIMIT_PER_HOUR = 10
# The green messages of the Access page. The web address carries only a short code, never free text
DONE_MESSAGES = {
    "promoted": "That person already had a verified account, so they are a manager now.",
    "invited": "Invite saved. When this Gmail signs up and types the 6-digit code, the person becomes a manager.",
    "removed": "Manager access removed. The person is a candidate again.",
    "cancelled": "Invite cancelled.",
}

# The green messages of the jobs page (again only a short code travels in the web address)
JOB_MESSAGES = {
    "draft": "Draft saved. You can open it again from the list.",
    "created": "Job created. The managers were notified.",
    "closed": "Job closed successfully. It is no longer visible on the public Careers page.",
    "opened": "Job opened successfully. It is visible again on the public Careers page.",
    "deleted": "Job deleted successfully.",
}

# Create the API object. Think of it as the "front desk" that answers requests
router = APIRouter()

# Tell the front desk where the HTML templates are
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Tell the front desk that any address starting with /static/ is answered from the static folder

# ---------- Helper functions ----------

# Read the company information from the database
# Read the company information from the database
def get_company_info():
    # A safe backup answer, used when the database cannot be read
    default_company = {
        "company_name": "Our Company",
        "about_us": "Company information is not available right now.",
        "mission": "", "address": "", "website": "", "contact_email": "",
        "tagline": "", "vision": "", "services": "", "team": "",
        "phone": "", "facebook": "", "linkedin": "", "instagram": "", "twitter": "",
    }

    keys = ["company_name", "about_us", "mission", "address", "website", "contact_email",
            "tagline", "vision", "services", "team", "phone", "facebook", "linkedin", "instagram", "twitter"]

    try:
        row = db.fetch_one(
            "SELECT company_name, about_us, mission, address, website, contact_email, "
            "tagline, vision, services, team, phone, facebook, linkedin, instagram, twitter "
            "FROM company_info ORDER BY info_id LIMIT 1;"
        )

        # If the table is empty, use the backup answer
        if row is None:
            return default_company

        # Put each column under its name (an empty cell becomes empty text)
        company = dict(default_company)
        for key, value in zip(keys, row):
            company[key] = value or ""
        return company

    except Exception as error:
        print("get_company_info failed:", error)
        return default_company

    # Turn lines like "Title | short text" into a list of dictionaries (at most 12 lines)
def split_items(text):
    items = []
    for line in (text or "").splitlines():
        line = line.strip()
        if line == "":
            continue
        if "|" in line:
            title, detail = line.split("|", 1)
        else:
            title, detail = line, ""
        items.append({"title": title.strip(), "text": detail.strip()})
    return items[:12]


# The IP address of the visitor (used only for the apply rate limit)
def get_client_ip(request):
    if request.client is None:
        return "unknown"
    return request.client.host


# Find who is logged in. Give back a dictionary, or None if nobody is logged in
def get_current_user(request):
    # Read the login token from the cookie
    token = request.cookies.get(SESSION_COOKIE)

    # No cookie means nobody is logged in
    if token is None or token == "":
        return None

    # Look the token up in the database
    return auth_tools.get_user_from_token(token)


# Build a finished HTML page. Every page gets the company information and the current user
def render(request, template_name, data=None, status_code=200):
        # Print the requested URL so we can confirm which page is being opened.
    print("RENDER:", request.url.path, "TEMPLATE:", template_name)
    # Start with an empty dictionary if no data was given
    if data is None:
        data = {}

    # Add the company information for the top bar and footer
    data["company"] = get_company_info()

    # Add the current user, unless the caller already decided it
    if "user" not in data:
        data["user"] = get_current_user(request)

    # Fill the template and give the finished page back
    return templates.TemplateResponse(request, template_name, data, status_code=status_code)


# One shared role check. Give back two things: (user, None) if allowed, or (None, page) if not allowed
def check_role(request, allowed_role):
    # Find who is logged in
    user = get_current_user(request)

    # Nobody is logged in, so send the person to the login page
    if user is None:
        return None, RedirectResponse("/login", status_code=303)

    # Wrong role: build the "Access denied" page with the code 403 ("forbidden")
    if user["role"] != allowed_role:
        denied_page = render(
            request, "message.html",
            {"title": "Access denied", "text": "Your role (" + user["role"] + ") cannot open this screen.", "user": user},
            status_code=403,
        )
        return None, denied_page

    # Right role: give the user back and no problem
    return user, None


# Create a new code, save it, and send it. Give back True if the sending worked
def send_verification_code(email):
    # Make a random 6-digit code
    code = email_tools.make_code()

    # Save its scrambled form in the database
    auth_tools.save_new_code(email, code)

    # Send the email (in terminal mode this prints the code in the uvicorn terminal)
    result = email_tools.send_code_email(email, code)

    # If sending failed, print the reason for us
    if not result["success"]:
        print("Sending the code failed:", result["message"])

    # Tell the caller if it worked
    return result["success"]


# ---------- Public pages ----------
# Show the public homepage at the root URL.
def home_page(request: Request):

    # Use the shared render function.
    # It automatically adds company information and the current user.
    return render(
        request,
        "home.html",
    )
def health_check():
    # Send back a tiny dictionary. FastAPI turns it into JSON text
    return {"status": "ok"}


# Send the company information as JSON (data, not a page)
def company_json():
    # Read the company information and send it back
    return get_company_info()


# ---------- Sign up ----------

# Build the sign up page again with an error message
def signup_error(request, message, name, email):
    # Show the form with the message and the values the person typed (never the password)
    return render(
        request, "signup.html",
        {"error": message, "name": name, "email": email, "user": None},
        status_code=400,
    )


# Show the sign up form.
def signup_page(request: Request):

    # Show the public signup page.
    # A logged-in user can also open this page if needed.
    return render(
        request,
        "signup.html",
        {
            "error": "",
            "name": "",
            "email": "",
        },
    )
# Receive the sign up form

def signup_submit(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    password: str = Form(""),
    password2: str = Form(""),
):
    # Clean what the person typed
    name = name.strip()
    email = auth_tools.clean_email(email)

    # Check the name
    if name == "" or len(name) > 100:
        return signup_error(request, "Please type your name (up to 100 letters).", name, email)

    # Check the Gmail address
    problem = auth_tools.check_gmail(email)
    if problem != "":
        return signup_error(request, problem, name, email)

    # Check the password
    if len(password) < 8 or len(password) > 200:
        return signup_error(request, "The password needs 8 to 200 characters.", name, email)
    if password != password2:
        return signup_error(request, "The two passwords are not the same.", name, email)

    # Look if this Gmail already has an account
    existing = auth_tools.get_user_by_email(email)
    if existing is not None and existing["email_verified"]:
        return signup_error(request, "This Gmail already has an account. Please log in.", name, email)

    # Do not send codes too fast
    if not auth_tools.can_send_code(email):
        return signup_error(request, "A code was just sent. Please wait one minute and try again.", name, email)

    # Create the account, or refresh an account that was never verified
    if existing is None:
        # "try" means: attempt this code, and if the Gmail was saved a moment ago (double click), jump to "except"
        try:
            auth_tools.create_user(name, email, password)
        except psycopg2.errors.UniqueViolation:
            # The Gmail was saved a moment ago, so do not crash
            return signup_error(request, "This Gmail already has an account. Please log in.", name, email)
    else:
        auth_tools.update_pending_user(existing["user_id"], name, password)

    # Send the code. If sending fails, tell the person
    if not send_verification_code(email):
        return signup_error(request, "We could not send the email. Please try again later.", name, email)

    # Go to the page where the code is typed
    return RedirectResponse("/verify?email=" + quote(email), status_code=303)


# ---------- Verify the code ----------

# Build the verify page (with an optional error or info message)
def verify_response(request, email, error, info, status_code=200):
    # dev_mode is True when emails are only shown in the terminal
    return render(
        request, "verify.html",
        {"email": email, "error": error, "info": info, "dev_mode": config.EMAIL_MODE == "terminal", "user": None},
        status_code=status_code,
    )


# Show the verify page
def verify_page(request: Request, email: str = "", sent: str = ""):
    # Clean the email that came in the web address
    email = auth_tools.clean_email(email)

    # If a new code was just requested, show a small message
    info = ""
    if sent == "1":
        info = "If a new code could be sent, it was sent. You can ask again after one minute."

    # Show the page
    return verify_response(request, email, "", info)


# Receive the verify form
def verify_submit(request: Request, email: str = Form(""), code: str = Form("")):
    # Clean what the person typed
    email = auth_tools.clean_email(email)
    code = code.strip()

    # The code must be exactly 6 digits
    if len(code) != 6 or not code.isdigit():
        return verify_response(request, email, "The code has exactly 6 digits.", "", 400)

    # Check the code in the database
    error = auth_tools.check_code(email, code)
    if error != "":
        return verify_response(request, email, error, "", 400)

    # The Gmail is verified, so go to the login page
    return RedirectResponse("/login?verified=1", status_code=303)


# Send a new code
def resend_code(request: Request, email: str = Form("")):
    # Clean the email
    email = auth_tools.clean_email(email)

    # Only send if this Gmail has an unverified account and a code was not just sent
    user = auth_tools.get_user_by_email(email)
    if user is not None and not user["email_verified"] and auth_tools.can_send_code(email):
        send_verification_code(email)

    # Always show the same message, so nobody can learn which Gmails have accounts
    return RedirectResponse("/verify?email=" + quote(email) + "&sent=1", status_code=303)


# ---------- Login and logout ----------

# Show the login page.
def login_page(request: Request, verified: str = ""):

    # Show the green verification message when the user has verified their Gmail.
    info = ""

    # Check whether the verification process just finished successfully.
    if verified == "1":
        info = "Your Gmail is verified. Please log in."

    # Show the public login form.
    return render(
        request,
        "login.html",
        {
            "error": "",
            "info": info,
            "email": "",
        },
    )


# Receive the login form
def login_submit(request: Request, email: str = Form(""), password: str = Form("")):
    # Clean the email
    email = auth_tools.clean_email(email)

    # Find the user
    user = auth_tools.get_user_by_email(email)

    # If there is no such user, scramble anyway, so the answer takes the same time
    if user is None:
        auth_tools.hash_password(password, "00" * 16)
        password_ok = False
    else:
        password_ok = auth_tools.password_matches(password, user["salt"], user["password_hash"])

    # One message for both "no such Gmail" and "wrong password", so nobody learns which Gmails exist
    if not password_ok:
        return render(
            request, "login.html",
            {"error": "Wrong Gmail or password.", "info": "", "email": email, "user": None},
            status_code=400,
        )

    # The password is right, but the Gmail is not verified yet: send a new code
    if not user["email_verified"]:
        if auth_tools.can_send_code(email):
            send_verification_code(email)
        return RedirectResponse("/verify?email=" + quote(email), status_code=303)

    # Create the login ticket and put it in a cookie
    token = auth_tools.make_session(user["user_id"])
    # Send HR users to the HR dashboard.
    if user["role"] == "hr":
        response = RedirectResponse("/hr", status_code=303)
    # Send manager users to the manager screen.
    elif user["role"] == "manager":
        response = RedirectResponse("/manager", status_code=303)

    # Send everyone else to the normal home page.
    else:
     response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,                        # JavaScript cannot read this cookie
        samesite="lax",                       # other websites cannot use it to send forms for you
        secure=config.COOKIE_SECURE,          # True means: only over secure HTTPS
        max_age=config.SESSION_HOURS * 3600,  # how long the browser keeps it, in seconds
    )
    return response


# Log out: delete the ticket and the cookie
def logout(request: Request):
    # Read the token and delete the ticket from the database
    token = request.cookies.get(SESSION_COOKIE)
    if token is not None and token != "":
        auth_tools.delete_session(token)

    # Go to the home page and delete the cookie
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


# ---------- Role-based menu and screens ----------

# Show the menu that matches the role of the logged-in person
def app_menu(request: Request):
    # Find who is logged in
    user = get_current_user(request)

    # Nobody is logged in, so go to the login page
    if user is None:
        return RedirectResponse("/login", status_code=303)

    # Show the menu (the template picks the buttons by role)
    return render(request, "menu.html", {"user": user})


# A shared placeholder screen: only the allowed role may enter
def role_page(request, allowed_role, title, text):
    # Check the role (problem is a ready-made page if the person may not enter)
    user, problem = check_role(request, allowed_role)
    if problem is not None:
        return problem

    # Right role: show the placeholder screen
    return render(request, "message.html", {"title": title, "text": text, "user": user})


 #The candidate screen: shows the welcome, the published jobs and the company information
def candidate_screen(request: Request):
    # Check the role: only a candidate may enter
    user, problem = check_role(request, "candidate")
    if problem is not None:
        return problem

    # Show the candidate page
    return render(request, "candidate.html", {"user": user, "jobs": job_tools.list_published_jobs()})


# The manager screen: jobs waiting for a decision
def manager_screen(request: Request, done: str = ""):
    user, problem = check_role(request, "manager")
    if problem is not None:
        return problem

    messages = {"approved": "Job approved and published.", "rejected": "Job rejected. HR was notified."}
    return render(request, "manager.html",
                  {"user": user, "jobs": job_tools.list_pending_jobs(), "info": messages.get(done, "")})


# Show one pending job to the manager
def manager_job(request: Request, job_id: int = 0, error: str = ""):
    user, problem = check_role(request, "manager")
    if problem is not None:
        return problem

    job = job_tools.get_job(job_id)
    if job is None or job["status"] != "pending_approval":
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job is not waiting for a decision.", "user": user},
                      status_code=404)

    message = "Please write a reason for rejecting." if error == "reason" else ""
    return render(request, "manager_job.html",
                  {"user": user, "job": job, "questions": job_tools.get_questions(job_id), "error": message})


# The manager approves or rejects
def manager_decide(request: Request, job_id: int = Form(0), decision: str = Form(""), reason: str = Form("")):
    user, problem = check_role(request, "manager")
    if problem is not None:
        return problem

    job = job_tools.get_job(job_id)
    if job is None or job["status"] != "pending_approval":
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job is not waiting for a decision.", "user": user},
                      status_code=400)

    if decision == "approve":
        if job_tools.approve_job(job_id, user["user_id"]):
            job_tools.notify_hr(job_id, job["created_by"], "Your job was approved and published: " + job["title"])
            job_tools.mark_job_notifications_read(job_id)
        return RedirectResponse("/manager?done=approved", status_code=303)

    if decision == "reject":
        reason = reason.strip()[:500]
        if reason == "":
            return RedirectResponse("/manager/job?job_id=" + str(job_id) + "&error=reason", status_code=303)
        if job_tools.reject_job(job_id, user["user_id"], reason):
            job_tools.notify_hr(job_id, job["created_by"], "Your job was rejected: " + job["title"] + ". Reason: " + reason)
            job_tools.mark_job_notifications_read(job_id)
        return RedirectResponse("/manager?done=rejected", status_code=303)

    return RedirectResponse("/manager", status_code=303)


# The HR home screen (only HR)
def hr_screen(request: Request):

    # Check the role.
    user, problem = check_role(request, "hr")

    # Stop if the logged-in person is not allowed to open this page.
    if problem is not None:
        return problem

    # Read all selected candidates who have scheduled interviews.
    scheduled_interviews = job_tools.list_selected_interviews()

    # Show the HR home page with the existing user and interview data.
    return render(
        request,
        "hr.html",
        {
            "user": user,
            "scheduled_interviews": scheduled_interviews,
        },
    )


# Show the poster of a published job (only a candidate)
def candidate_poster(request: Request, job_id: int = 0):
    user, problem = check_role(request, "candidate")
    if problem is not None:
        return problem

    job = job_tools.get_job(job_id)
    if job is None or job["status"] != "published":
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job is not open.", "user": user}, status_code=404)

    return render(request, "job_poster.html", {
        "user": user, "job": job, "back_url": "/candidate", "back_text": "Back to jobs",
        "apply_url": "/candidate/job?job_id=" + str(job_id),
    })


# ---------- HR: applications ----------



def hr_application_status(request: Request, background_tasks: BackgroundTasks, candidate_id: int = Form(0), status: str = Form("")):
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    app_row = job_tools.get_application(candidate_id)
    job = job_tools.get_job(app_row["job_id"]) if app_row is not None else None
    if app_row is None or job is None or job["created_by"] != user["user_id"]:
        return render(request, "message.html",
                      {"title": "Not available", "text": "This application was not found.", "user": user}, status_code=404)

    if status in ("applied", "shortlisted", "rejected"):
        job_tools.set_application_status(candidate_id, status)

        # Tell the candidate, only when the status really changed
        if status != app_row["status"]:
            company_name = get_company_info()["company_name"]
            if status == "shortlisted":
                background_tasks.add_task(email_tools.send_shortlist_email,
                                          app_row["email"], app_row["name"], job["title"], company_name)
            if status == "rejected":
                background_tasks.add_task(email_tools.send_reject_email,
                                          app_row["email"], app_row["name"], job["title"], company_name)

    return RedirectResponse("/hr/application?candidate_id=" + str(candidate_id) + "&done=1", status_code=303)


# Save the feedback and the rating of an interview (only HR who made the job)
def hr_feedback_save(request: Request, candidate_id: int = Form(0), feedback: str = Form(""), rating: str = Form("")):
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    app_row = job_tools.get_application(candidate_id)
    job = job_tools.get_job(app_row["job_id"]) if app_row is not None else None
    if app_row is None or job is None or job["created_by"] != user["user_id"]:
        return render(request, "message.html",
                      {"title": "Not available", "text": "This application was not found.", "user": user}, status_code=404)

    back = "/hr/application?candidate_id=" + str(candidate_id) + "&done="

    # The interview must exist first
    if job_tools.get_interview(candidate_id) is None:
        return RedirectResponse(back + "nointerview", status_code=303)

    # The rating is a number from 1 to 5
    rating = rating.strip()
    if not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
        return RedirectResponse(back + "badrating", status_code=303)

    job_tools.save_feedback(candidate_id, feedback.strip()[:2000], int(rating))
    return RedirectResponse(back + "feedback", status_code=303)

# Save the HR's final decision for a shortlisted candidate.
def hr_final_decision(
    request: Request,
    background_tasks: BackgroundTasks,
    candidate_id: int = Form(0),
    decision: str = Form(""),
):
    # Check that the logged-in person is an HR user.
    user, problem = check_role(request, "hr")

    # Stop immediately if the user is not allowed to use this page.
    if problem is not None:
        return problem

    # Get the candidate application.
    app_row = job_tools.get_application(candidate_id)

    # Get the job connected to this application.
    job = job_tools.get_job(app_row["job_id"]) if app_row is not None else None

    # Make sure this HR created the job.
    if app_row is None or job is None or job["created_by"] != user["user_id"]:
        return render(
            request,
            "message.html",
            {
                "title": "Not available",
                "text": "This application was not found.",
                "user": user,
            },
            status_code=404,
        )

    # Only shortlisted candidates can receive a final HR decision.
    if app_row["status"] != "shortlisted":
        return RedirectResponse(
            "/hr/application?candidate_id="
            + str(candidate_id)
            + "&done=notshort",
            status_code=303,
        )

    # Only allow the two decisions defined by this step.
    if decision not in ("selected", "rejected"):
        return RedirectResponse(
            "/hr/application?candidate_id="
            + str(candidate_id),
            status_code=303,
        )

    # Save the HR decision by changing the candidate status.
    job_tools.set_application_status(candidate_id, decision)

    # If HR rejected the candidate, send the existing rejection email.
    if decision == "rejected":
        background_tasks.add_task(
            email_tools.send_reject_email,
            app_row["email"],
            app_row["name"],
            job["title"],
            get_company_info()["company_name"],
        )

    # Return to the candidate page with a success message.
    if decision == "selected":
        return RedirectResponse(
            "/hr/application?candidate_id="
            + str(candidate_id)
            + "&done=selected",
            status_code=303,
        )

    return RedirectResponse(
        "/hr/application?candidate_id="
        + str(candidate_id)
        + "&done=finalrejected",
        status_code=303,
    )
# Create an offer for a selected candidate.

# Get all selected candidates who have a scheduled interview.
def get_hr_interviews():

    # Create the SQL query to get candidate, job and interview information.
    query = """
        SELECT
            c.candidate_id,
            c.name,
            j.title,
            i.interview_date,
            i.instructions
        FROM candidates c
        JOIN interviews i
            ON i.candidate_id = c.candidate_id
        JOIN jobs j
            ON j.job_id = c.job_id
        WHERE c.status = 'selected'
        ORDER BY i.interview_date
    """

    # Open the database connection using your existing database function.
    conn = db.get_connection()

    # Create a cursor so Python can execute the SQL query.
    cur = conn.cursor()

    # Run the SQL query.
    cur.execute(query)

    # Get all rows returned by PostgreSQL.
    rows = cur.fetchall()

    # Close the cursor after reading the data.
    cur.close()

    # Close the database connection.
    conn.close()

    # Create an empty list for the interview records.
    interviews = []

    # Go through every database row.
    for row in rows:

        # Add one interview record to the list.
        interviews.append({
            "candidate": row[1],
            "job": row[2],
            "interview_datetime": row[3],
            "description": row[4]
        })

    # Return all interview records to the HR page.
    return interviews

# Show the HR Interviews page.
def hr_interviews_page(request: Request):

    # Check that the logged-in user is an HR user.
    user, problem = check_role(request, "hr")

    # Stop if the logged-in person is not allowed to open this page.
    if problem is not None:
        return problem

    # Get the same selected candidates and scheduled interviews
    # that are already being used on the HR home page.
    scheduled_interviews = job_tools.list_selected_interviews()

    # Show the HR Interviews page with the existing interview data.
    return render(
        request,
        "hr_interviews.html",
        {
            "user": user,
            "scheduled_interviews": scheduled_interviews,
        },
    )

def hr_offer_save(
    request: Request,
    candidate_id: int = Form(0),
    offer_salary: str = Form(""),
    joining_date: str = Form(""),
):
    # Check that the logged-in person is an HR user.
    user, problem = check_role(request, "hr")

    # Stop immediately if the user is not allowed to use this page.
    if problem is not None:
        return problem

    # Get the candidate application.
    app_row = job_tools.get_application(candidate_id)

    # Get the job connected to this application.
    job = job_tools.get_job(app_row["job_id"]) if app_row is not None else None

    # Make sure this HR created the job.
    if app_row is None or job is None or job["created_by"] != user["user_id"]:
        return render(
            request,
            "message.html",
            {
                "title": "Not available",
                "text": "This application was not found.",
                "user": user,
            },
            status_code=404,
        )

    # Only a selected candidate can receive an offer.
    if app_row["status"] != "selected":
        return RedirectResponse(
            "/hr/application?candidate_id="
            + str(candidate_id),
            status_code=303,
        )

    # Clean the salary entered by HR.
    offer_salary = offer_salary.strip()

    # Make sure salary was entered.
    if offer_salary == "":
        return RedirectResponse(
            "/hr/application?candidate_id="
            + str(candidate_id)
            + "&done=badoffer",
            status_code=303,
        )

    # Save the offer salary and joining date.
    job_tools.save_offer(candidate_id, offer_salary, joining_date)

    # Return to the candidate profile with a success message.
    return RedirectResponse(
        "/hr/application?candidate_id="
        + str(candidate_id)
        + "&done=offersaved",
        status_code=303,
    )

# Send the saved offer letter to the selected candidate.
def hr_offer_send(
    request: Request,
    background_tasks: BackgroundTasks,
    candidate_id: int = Form(0),
):
    # Check that the logged-in user is an HR user.
    user, problem = check_role(request, "hr")

    # Stop if the user is not allowed to use this function.
    if problem is not None:
        return problem

    # Get the candidate application from the database.
    app_row = job_tools.get_application(candidate_id)

    # Get the job connected to this candidate.
    job = job_tools.get_job(
        app_row["job_id"]
    ) if app_row is not None else None

    # Make sure this candidate belongs to a job created by this HR user.
    if (
        app_row is None
        or job is None
        or job["created_by"] != user["user_id"]
    ):
        return render(
            request,
            "message.html",
            {
                "title": "Not available",
                "text": "This application was not found.",
                "user": user,
            },
            status_code=404,
        )

    # Only a candidate with a saved pending offer can receive the offer letter.
    if app_row["status"] != "offer_pending":
        return RedirectResponse(
            "/hr/application?candidate_id="
            + str(candidate_id),
            status_code=303,
        )

    # Create a secure token for this candidate's offer.
    offer_token = job_tools.create_offer_token(candidate_id)

    # Stop if the token could not be created.
    if offer_token == "":
        return render(
            request,
            "message.html",
            {
                "title": "Offer not available",
                "text": "The pending offer could not be found.",
                "user": user,
            },
            status_code=404,
        )

    # Build the public offer link using the live website URL.
    offer_url = (
    config.APP_BASE_URL.rstrip("/")
    + "/offer/response/"
    + offer_token
    )

    # Get the company name used in the candidate email.
    company_name = get_company_info()["company_name"]

    # Get the saved offer details.
    offer = job_tools.get_offer(candidate_id)

    # Make sure the saved offer exists.
    if offer is None:
        return render(
            request,
            "message.html",
            {
                "title": "Offer not available",
                "text": "The saved offer could not be found.",
                "user": user,
            },
            status_code=404,
        )

    # Send the offer email in the background.
    background_tasks.add_task(
        email_tools.send_offer_email,
        app_row["email"],
        app_row["name"],
        job["title"],
        offer["salary"],
        offer["joining_date"],
        company_name,
        offer_url,
    )

    # Return to the candidate profile with a success message.
    return RedirectResponse(
        "/hr/application?candidate_id="
        + str(candidate_id)
        + "&done=offersent",
        status_code=303,
    )
# Download the CV (only HR who made the job)


# Show the candidate's offer page using the secure offer token.
def offer_response_page(
    request: Request,
    offer_token: str = "",
):
    # Find the offer connected to this secure token.
    offer = job_tools.get_offer_by_token(offer_token)

    # Stop if the token is missing or invalid.
    if offer is None:
        return render(
            request,
            "message.html",
            {
                "title": "Offer not available",
                "text": "This offer link is invalid or no longer available.",
                "user": get_current_user(request),
            },
            status_code=404,
        )

    # Get the company information for the offer page.
    company = get_company_info()

    # Show the candidate's offer page.
    return render(
        request,
        "offer_response.html",
        {
            "offer": offer,
            "token": offer_token,
            "company": company,
            "user": get_current_user(request),
        },
    )

# Accept the offer using the secure offer token.
def offer_accept(
    request: Request,
    offer_token: str = Form(""),
):
    # Save the candidate's acceptance in the database.
    saved = job_tools.respond_to_offer(
        offer_token,
        "accepted",
    )

    # Stop if the offer link is invalid or was already answered.
    if not saved:
        return render(
            request,
            "message.html",
            {
                "title": "Offer not available",
                "text": "This offer is invalid or has already been answered.",
                "user": get_current_user(request),
            },
            status_code=404,
        )

    # Show a simple success message after acceptance.
    return render(
        request,
        "message.html",
        {
            "title": "Offer Accepted",
            "text": "Thank you. You have accepted the job offer.",
            "user": get_current_user(request),
        },
    )


# Reject the offer using the secure offer token.
def offer_reject(
    request: Request,
    offer_token: str = Form(""),
):
    # Save the candidate's rejection in the database.
    saved = job_tools.respond_to_offer(
        offer_token,
        "rejected",
    )

    # Stop if the offer link is invalid or was already answered.
    if not saved:
        return render(
            request,
            "message.html",
            {
                "title": "Offer not available",
                "text": "This offer is invalid or has already been answered.",
                "user": get_current_user(request),
            },
            status_code=404,
        )

    # Show a simple message after rejection.
    return render(
        request,
        "message.html",
        {
            "title": "Offer Rejected",
            "text": "Your offer response has been recorded.",
            "user": get_current_user(request),
        },
    )


def hr_cv_download(request: Request, candidate_id: int = 0):
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    app_row = job_tools.get_application(candidate_id)
    job = job_tools.get_job(app_row["job_id"]) if app_row is not None else None
    if app_row is None or job is None or job["created_by"] != user["user_id"] or app_row["cv_file_path"] == "":
        return render(request, "message.html",
                      {"title": "Not available", "text": "No CV was found.", "user": user}, status_code=404)

    # Use only the file name, so nobody can reach other folders
    saved_name = os.path.basename(app_row["cv_file_path"])
    path = os.path.join(cv_tools.UPLOAD_DIR, saved_name)
    if not os.path.isfile(path):
        return render(request, "message.html",
                      {"title": "Not available", "text": "The CV file is missing.", "user": user}, status_code=404)

    ext = os.path.splitext(saved_name)[1]
    return FileResponse(path, filename="CV-" + app_row["name"].replace(" ", "_") + ext)


# ---------- HR: jobs ----------

# Show the list of jobs (only HR)
def hr_jobs_page(request: Request, done: str = ""):
    # Check the role
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # Pick the green message that belongs to the short code in the web address (empty if unknown)
    info = JOB_MESSAGES.get(done, "")

    # Show the list of all jobs
    return render(request, "hr_jobs.html", {"user": user, "jobs": job_tools.list_jobs(), "info": info})


# Show the empty form, or the form of an existing job (only HR)
def hr_job_edit(request: Request, job_id: int = 0):
    # Check the role
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # An empty form for a new job
    form = {"job_id": 0, "title": "", "department": "", "location": "", "salary_range": "",
            "description": "", "requirements": "", "benefits": "", "deadline": "", "reject_reason": ""}

    # An existing job: only the HR who made it, and only a draft or a rejected job
    if job_id != 0:
        job = job_tools.get_job(job_id)
        if job is None or job["created_by"] != user["user_id"] or job["status"] not in ("draft", "rejected"):
            return render(
                request, "message.html",
                {"title": "Not available", "text": "This job cannot be edited.", "user": user},
                status_code=404,
            )

        # Fill the form with the saved job
        form = job

    # Show the form
    return render(request, "job_form.html", {"user": user, "form": form, "error": ""})


# Receive the job form (only HR)
def hr_job_save(
    request: Request,
    job_id: int = Form(0),
    title: str = Form(""),
    department: str = Form(""),
    location: str = Form(""),
    salary_range: str = Form(""),
    description: str = Form(""),
    requirements: str = Form(""),
    benefits: str = Form(""),
    deadline: str = Form(""),
    action: str = Form("draft"),
):
    # Check the role first: nothing below runs for a candidate, a manager or a visitor
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # Clean what HR typed (remove spaces around the text)
    form = {
        "job_id": job_id, "title": title.strip(), "department": department.strip(), "location": location.strip(),
        "salary_range": salary_range.strip(), "description": description.strip(),
        "requirements": requirements.strip(), "benefits": benefits.strip(), "deadline": deadline.strip(),
        "reject_reason": "",
    }

    # Check the title and the length of every text
    error = ""
    if form["title"] == "":
        error = "The job title cannot be empty."
    else:
        error = job_tools.check_lengths(form)

    # Check the deadline (if it is wrong, the typed text stays in the box so HR can fix it)
    if error == "":
        error, deadline_value = job_tools.parse_deadline(form["deadline"])
        if error == "":
            form["deadline"] = deadline_value or ""

    # To open the review page, the description and the requirements must be filled
    if error == "" and action == "create":
        if form["description"] == "" or form["requirements"] == "":
            error = "To review the job, please fill in the description and the requirements. Or save it as a draft."

    # If something is wrong, show the form again with the same text
    if error != "":
        return render(request, "job_form.html", {"user": user, "form": form, "error": error}, status_code=400)

    # An empty deadline is saved as nothing
    if form["deadline"] == "":
        form["deadline"] = None

    # The job is always saved as a draft here. Sending it to the manager happens on the review page
    status = "draft"

    if job_id == 0:
        # A new job
        job_id = job_tools.create_job(user["user_id"], form, status)
    else:
        # An existing job: only the HR who made it may change it
        job = job_tools.get_job(job_id)
        if job is None or job["created_by"] != user["user_id"]:
            return render(
                request, "message.html",
                {"title": "Not available", "text": "This job cannot be changed.", "user": user},
                status_code=404,
            )

        # update_job changes only a draft or rejected job; 0 changed rows means it was already sent
        if job_tools.update_job(job_id, form, status) == 0:
            return render(
                request, "message.html",
                {"title": "Not available", "text": "This job can no longer be changed.", "user": user},
                status_code=400,
            )

    # "Save and review" opens the review page
    if action == "create":
        return RedirectResponse("/hr/jobs/review?job_id=" + str(job_id), status_code=303)

    # A plain draft goes back to the list with a green message
    return RedirectResponse("/hr/jobs?done=draft", status_code=303)


# Close a published job (only the HR who created it).
def hr_job_close(request: Request, job_id: int = Form(0)):
    # Check that the logged-in person is HR.
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # Ask job_tools to change the job from published to closed.
    changed = job_tools.close_job(job_id, user["user_id"])

    # If no row changed, the job was not found, was not owned by this HR, or was not published.
    if changed == 0:
        return render(
            request,
            "message.html",
            {
                "title": "Cannot close job",
                "text": "This job cannot be closed.",
                "user": user,
            },
            status_code=400,
        )

    # Return to the Jobs page with a success message.
    return RedirectResponse("/hr/jobs?done=closed", status_code=303)


# Reopen a closed job (only the HR who created it).
def hr_job_open(request: Request, job_id: int = Form(0)):
    # Check that the logged-in person is HR.
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # Ask job_tools to change the job from closed to published.
    changed = job_tools.open_job(job_id, user["user_id"])

    # If no row changed, the job was not found, was not owned by this HR, or was not closed.
    if changed == 0:
        return render(
            request,
            "message.html",
            {
                "title": "Cannot open job",
                "text": "This job cannot be opened.",
                "user": user,
            },
            status_code=400,
        )

    # Return to the Jobs page with a success message.
    return RedirectResponse("/hr/jobs?done=opened", status_code=303)


# Delete a job that is allowed to be deleted (only the HR who created it).
def hr_job_delete(request: Request, job_id: int = Form(0)):
    # Check that the logged-in person is HR.
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # Ask job_tools to delete the job and its questions.
    result = job_tools.delete_job(job_id, user["user_id"])

    # The job was not found or belongs to another HR.
    if result == "not_found":
        return render(
            request,
            "message.html",
            {
                "title": "Not available",
                "text": "This job was not found or does not belong to you.",
                "user": user,
            },
            status_code=404,
        )

    # A published job must be closed before it can be deleted.
    if result == "published":
        return render(
            request,
            "message.html",
            {
                "title": "Cannot delete",
                "text": "A published job cannot be deleted. Close the job first.",
                "user": user,
            },
            status_code=400,
        )

    # A job waiting for manager approval must not be deleted.
    if result == "pending":
        return render(
            request,
            "message.html",
            {
                "title": "Cannot delete",
                "text": "This job is waiting for manager approval.",
                "user": user,
            },
            status_code=400,
        )

    # A successful delete returns to the Jobs page.
    return RedirectResponse("/hr/jobs?done=deleted", status_code=303)


# ---------- HR: company information ----------

# Show the edit form (only HR)
def hr_company_page(request: Request, saved: str = ""):
    # Check the role
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # A green message after a successful save
    info = ""
    if saved == "1":
        info = "Company information saved."

    # Fill the form with what is saved now
    return render(
        request, "company_form.html",
        {"error": "", "info": info, "form": get_company_info(), "user": user},
    )


# Receive the edit form (only HR)
def hr_company_submit(
    request: Request,
    company_name: str = Form(""),
    about_us: str = Form(""),
    mission: str = Form(""),
    address: str = Form(""),
    website: str = Form(""),
    contact_email: str = Form(""),
    tagline: str = Form(""),
    vision: str = Form(""),
    services: str = Form(""),
    team: str = Form(""),
    phone: str = Form(""),
    facebook: str = Form(""),
    linkedin: str = Form(""),
    instagram: str = Form(""),
    twitter: str = Form(""),
):
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    form = {
        "company_name": company_name.strip(), "about_us": about_us.strip(), "mission": mission.strip(),
        "address": address.strip(), "website": website.strip(), "contact_email": contact_email.strip(),
        "tagline": tagline.strip(), "vision": vision.strip(), "services": services.strip(), "team": team.strip(),
        "phone": phone.strip(), "facebook": facebook.strip(), "linkedin": linkedin.strip(),
        "instagram": instagram.strip(), "twitter": twitter.strip(),
    }

    error = ""
    if form["company_name"] == "":
        error = "The company name cannot be empty."
    elif len(form["company_name"]) > 100:
        error = "The company name can have up to 100 letters."
    elif len(form["about_us"]) > 2000 or len(form["mission"]) > 1000 or len(form["vision"]) > 1000:
        error = "The About us, Mission or Vision text is too long."
    elif len(form["services"]) > 2000 or len(form["team"]) > 2000:
        error = "The Services or Team text is too long (up to 2000 letters)."
    elif len(form["tagline"]) > 200:
        error = "The tagline can have up to 200 letters."
    elif len(form["address"]) > 300 or len(form["website"]) > 200 or len(form["contact_email"]) > 200:
        error = "The address, website or contact email is too long."
    elif len(form["phone"]) > 50:
        error = "The phone number is too long."
    elif form["website"] != "" and not (form["website"].startswith("https://") or form["website"].startswith("http://")):
        error = "The website must start with https:// or http://"
    elif form["contact_email"] != "" and ("@" not in form["contact_email"] or " " in form["contact_email"]):
        error = "The contact email does not look right."
    else:
        # Every social link must be empty or start with https:// or http://
        for name in ("facebook", "linkedin", "instagram", "twitter"):
            value = form[name]
            if len(value) > 200:
                error = "The " + name + " link is too long."
            elif value != "" and not (value.startswith("https://") or value.startswith("http://")):
                error = "The " + name + " link must start with https:// or http://"
            if error != "":
                break

    if error != "":
        return render(
            request, "company_form.html",
            {"error": error, "info": "", "form": form, "user": user},
            status_code=400,
        )

    values = (form["company_name"], form["about_us"], form["mission"], form["address"], form["website"],
              form["contact_email"], form["tagline"], form["vision"], form["services"], form["team"],
              form["phone"], form["facebook"], form["linkedin"], form["instagram"], form["twitter"],
              user["user_id"])

    rows_changed = db.execute(
        "UPDATE company_info SET company_name = %s, about_us = %s, mission = %s, address = %s, website = %s, "
        "contact_email = %s, tagline = %s, vision = %s, services = %s, team = %s, phone = %s, facebook = %s, "
        "linkedin = %s, instagram = %s, twitter = %s, updated_by = %s "
        "WHERE info_id = (SELECT info_id FROM company_info ORDER BY info_id LIMIT 1);",
        values,
    )

    if rows_changed == 0:
        db.execute(
            "INSERT INTO company_info (company_name, about_us, mission, address, website, contact_email, "
            "tagline, vision, services, team, phone, facebook, linkedin, instagram, twitter, updated_by) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
            values,
        )

    return RedirectResponse("/hr/company?saved=1", status_code=303)


# Give back AI suggestions as JSON (only HR)
def hr_job_suggest(request: Request, title: str = Form(""), department: str = Form("")):
    user, problem = check_role(request, "hr")
    if problem is not None:
        return JSONResponse({"error": "Not allowed"}, status_code=403)

    title = title.strip()[:150]
    if title == "":
        return JSONResponse({"error": "Type a job title first."}, status_code=400)

    data, source = ai_tools.suggest_job_text(title, department.strip()[:100])
    data["source"] = source
    return JSONResponse(data)


# Show the auto poster of a job (only HR who made it)
def hr_job_poster(request: Request, job_id: int = 0):
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    job = job_tools.get_job(job_id)
    if job is None or job["created_by"] != user["user_id"]:
        return render(
            request, "message.html",
            {"title": "Not available", "text": "This job was not found.", "user": user},
            status_code=404,
        )

    return render(request, "job_poster.html", {"user": user, "job": job})


# Show the questionnaire of a job (only the HR who made it)
def hr_questions_page(request: Request, job_id: int = 0, saved: str = "", made: str = ""):
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    job = job_tools.get_job(job_id)
    if job is None or job["created_by"] != user["user_id"]:
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job was not found.", "user": user}, status_code=404)

    info = ""
    if saved == "1":
        info = "Questions saved."

    # "made" means new suggestions were just created and are not saved yet
    questions = job_tools.get_questions(job_id)
    if made != "":
        suggested, source = ai_tools.suggest_questions(job["title"], job["requirements"])
        questions = suggested
        info = ("AI questions added." if source == "ai" else "Ready-made questions added (AI not available).") + " Please edit them, then click Save."

    return render(request, "job_questions.html",
                  {"user": user, "job": job, "questions": questions, "info": info, "error": ""})


# Save the questionnaire (only the HR who made the job)
def hr_questions_save(request: Request, job_id: int = Form(0), questions: list[str] = Form([])):
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    job = job_tools.get_job(job_id)
    if job is None or job["created_by"] != user["user_id"]:
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job was not found.", "user": user}, status_code=404)

    # Only a draft or rejected job can change its questions
    if job["status"] not in ("draft", "rejected"):
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job was already sent, so its questions are locked.", "user": user},
                      status_code=400)

    # Clean the questions: remove empty ones, cut long ones, keep at most 15
    cleaned = []
    for text in questions:
        text = text.strip()[:300]
        if text != "":
            cleaned.append(text)
    cleaned = cleaned[:15]

    job_tools.save_questions(job_id, cleaned)
    return RedirectResponse("/hr/jobs/questions?job_id=" + str(job_id) + "&saved=1", status_code=303)


# Show the review page of a job (only the HR who made it)
def hr_job_review(request: Request, job_id: int = 0, error: str = ""):
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    job = job_tools.get_job(job_id)
    if job is None or job["created_by"] != user["user_id"] or job["status"] not in ("draft", "rejected"):
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job cannot be reviewed.", "user": user}, status_code=404)

    message = ""
    if error == "noq":
        message = "Please add at least one question before sending the job to the manager."
    if error == "nodesc":
        message = "Please fill in the description and the requirements first."

    return render(request, "job_review.html",
                  {"user": user, "job": job, "questions": job_tools.get_questions(job_id), "error": message})


# Send the reviewed job to the managers (only the HR who made it)
def hr_job_send(request: Request, job_id: int = Form(0)):
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    job = job_tools.get_job(job_id)
    if job is None or job["created_by"] != user["user_id"]:
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job was not found.", "user": user}, status_code=404)

    if job["description"] == "" or job["requirements"] == "":
        return RedirectResponse("/hr/jobs/review?job_id=" + str(job_id) + "&error=nodesc", status_code=303)

    if len(job_tools.get_questions(job_id)) == 0:
        return RedirectResponse("/hr/jobs/review?job_id=" + str(job_id) + "&error=noq", status_code=303)

    if not job_tools.submit_job(job_id):
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job was already sent.", "user": user}, status_code=400)

    job_tools.notify_managers(job_id, job["title"])
    return RedirectResponse("/hr/jobs?done=created", status_code=303)


# ---------- Candidate: view a job and apply ----------

# Show one published job with the apply form (only a candidate)
def candidate_job(request: Request, job_id: int = 0, error: str = ""):
    user, problem = check_role(request, "candidate")
    if problem is not None:
        return problem

    job = job_tools.get_job(job_id)
    if job is None or job["status"] != "published":
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job is not open.", "user": user}, status_code=404)

    form = {"experience_years": "", "education": "", "expected_salary": ""}
    return render(request, "candidate_job.html", {
        "user": user, "job": job, "questions": job_tools.get_questions_with_ids(job_id),
        "applied": job_tools.has_applied(user["user_id"], job_id), "error": error, "form": form,
    })


# Receive the application (only a candidate)
async def candidate_apply(request: Request, background_tasks: BackgroundTasks):
    user, problem = check_role(request, "candidate")
    if problem is not None:
        return problem

    # Read the form (it contains a file, so we read it by hand)
    data = await request.form()
    job_id_text = str(data.get("job_id", "0"))
    job_id = int(job_id_text) if job_id_text.isdigit() else 0

    job = job_tools.get_job(job_id)
    if job is None or job["status"] != "published":
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job is not open.", "user": user}, status_code=404)

    questions = job_tools.get_questions_with_ids(job_id)
    form = {
        "experience_years": str(data.get("experience_years", "")).strip(),
        "education": str(data.get("education", "")).strip()[:200],
        "expected_salary": str(data.get("expected_salary", "")).strip(),
        "cv_text": "",
    }

    def show_error(message):
        return render(request, "candidate_job.html", {
            "user": user, "job": job, "questions": questions,
            "applied": False, "error": message, "form": form,
        }, status_code=400)

    # One application per job
    if job_tools.has_applied(user["user_id"], job_id):
        return show_error("You already applied to this job.")

    # Deadline
    if job["deadline"] != "" and job["deadline"] < str(datetime.date.today()):
        return show_error("The deadline of this job has passed.")

    # Numbers
    if not form["experience_years"].isdigit() or int(form["experience_years"]) > 60:
        return show_error("Years of experience must be a number from 0 to 60.")
    if not form["expected_salary"].isdigit() or int(form["expected_salary"]) > 100000000:
        return show_error("Expected salary must be a number.")
    if form["education"] == "":
        return show_error("Please type your education.")
    experience_years = int(form["experience_years"])
    form["experience_years"] = experience_years
    form["expected_salary"] = int(form["expected_salary"])

    # The answers
    answers = []
    for question_id, text in questions:
        answer = str(data.get("answer_" + str(question_id), "")).strip()[:1000]
        if answer == "":
            return show_error("Please answer every question.")
        answers.append((question_id, answer))

    # The CV file
    cv = data.get("cv")
    if cv is None or not hasattr(cv, "filename") or cv.filename == "":
        return show_error("Please upload your CV.")
    content = await cv.read()
    file_problem = cv_tools.check_file(cv.filename, len(content))
    if file_problem != "":
        return show_error(file_problem)

    # Save the file, read it, and score it
    saved_name = cv_tools.save_file(cv.filename, content)
    cv_text = cv_tools.read_text(saved_name)
    form["cv_text"] = cv_text[:20000]
    score, result = cv_tools.score_cv(cv_text, job, experience_years)

    job_tools.create_application(user, job_id, form, saved_name, score, result, answers)

    # Send the "you have applied" email after the page is answered (a slow or failed email changes nothing)
    background_tasks.add_task(
        email_tools.send_application_email,
        user["email"], user["name"], job["title"], get_company_info()["company_name"],
    )
    return RedirectResponse("/candidate/applications?done=1", status_code=303)


# Show the HR manual candidate form.
def hr_manual_candidate_page(request: Request, job_id: int = 0, done: str = "", error: str = ""):
    # Check that the logged-in person is an HR user.
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # Get only the jobs created by this HR.
    jobs = [j for j in job_tools.list_jobs() if j["created_by"] == user["user_id"]]

    # If a job was supplied, make sure this HR owns it.
    if job_id != 0:
        selected_job = job_tools.get_job(job_id)
        if selected_job is None or selected_job["created_by"] != user["user_id"]:
            return render(request, "message.html",
                          {"title": "Not available", "text": "This job was not found.", "user": user},
                          status_code=404)

    # Show the form and any success or error message.
    return render(request, "hr_manual_candidate.html", {
        "user": user,
        "jobs": jobs,
        "selected_job_id": job_id,
        "info": {"saved": "Candidate added successfully."}.get(done, ""),
        "error": {
            "missing": "Please fill in all required candidate information.",
            "badjob": "Please select a valid job.",
            "jobnotpublished": "This job is waiting for manager approval. Candidates can only be added after the job is published.",
            "badnumbers": "Experience and expected salary must be valid numbers.",
            "badsource": "Please enter the source website or referral source.",
            "badcv": "The CV file could not be accepted.",
        }.get(error, ""),
    })


# Save a candidate manually entered by HR.
async def hr_manual_candidate_save(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    job_id: int = Form(0),
    experience_years: str = Form(""),
    education: str = Form(""),
    expected_salary: str = Form(""),
    candidate_source: str = Form(""),
    source_other: str = Form(""),
    cv: UploadFile | None = File(None),
):
    # Check that the logged-in person is an HR user.
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # Clean the text values before saving them.
    name = name.strip()[:150]
    email = email.strip()[:200]
    phone = phone.strip()[:50]
    education = education.strip()[:250]
    candidate_source = candidate_source.strip()[:50]
    source_other = source_other.strip()[:100]

    # A job is optional, so NULL is used when HR leaves the job empty.
    database_job_id = None

    # Only check ownership when HR actually selected a job.
    if job_id != 0:
        selected_job = job_tools.get_job(job_id)

        # Make sure the selected job belongs to this HR.
        # Make sure the selected job belongs to the current HR.
        if selected_job is None or selected_job["created_by"] != user["user_id"]:
         return RedirectResponse("/hr/candidate/add?error=badjob", status_code=303)

          # Only approved and published jobs can receive HR-sourced candidates.
        if selected_job["status"] != "published":
          return RedirectResponse(
        "/hr/candidate/add?error=jobnotpublished",
        status_code=303,
    )

        # Save the real job ID for the database.
        database_job_id = job_id

    # Experience is optional. Blank means zero for the existing database field.
    experience_number = 0

    # Convert experience only when HR entered it.
    if experience_years.strip() != "":
        try:
            experience_number = int(experience_years.strip())
        except ValueError:
            return RedirectResponse("/hr/candidate/add?error=badnumbers", status_code=303)

        # Check the allowed experience range.
        if experience_number < 0 or experience_number > 60:
            return RedirectResponse("/hr/candidate/add?error=badnumbers", status_code=303)

    # Expected salary is optional. Blank means zero for the existing database field.
    salary_number = 0

    # Convert salary only when HR entered it.
    if expected_salary.strip() != "":
        try:
            salary_number = int(expected_salary.strip())
        except ValueError:
            return RedirectResponse("/hr/candidate/add?error=badnumbers", status_code=303)

        # Check the allowed salary range.
        if salary_number < 0 or salary_number > 100000000:
            return RedirectResponse("/hr/candidate/add?error=badnumbers", status_code=303)

    # If HR selected Other and typed another source, use that text.
    if candidate_source == "Other" and source_other != "":
        candidate_source = source_other

    # A CV is optional for an HR-sourced candidate.
    cv_file_path = ""
    cv_text = ""
    score = 0
    screening_result = "Manual HR candidate - CV not provided."

    # If HR uploaded a CV, use the existing CV screening system.
    if cv is not None and cv.filename:
        content = await cv.read()
        file_problem = cv_tools.check_file(cv.filename, len(content))
        if file_problem != "":
            return RedirectResponse("/hr/candidate/add?error=badcv", status_code=303)

        # Save the CV and extract its text.
        cv_file_path = cv_tools.save_file(cv.filename, content)
        cv_text = cv_tools.read_text(cv_file_path)[:20000]

        # Score the CV only when a job was selected.
        if selected_job is not None:
            score, screening_result = cv_tools.score_cv(
                cv_text, selected_job, experience_number
            )
        else:
            screening_result = "Manual HR candidate - CV provided; no job selected."

    # Save the HR-sourced candidate in the existing candidates table.
    # Blank job selection is passed as NULL instead of invalid job ID 0.
    job_tools.create_manual_candidate(
        database_job_id,
        name,
        email,
        phone,
        experience_number,
        education,
        salary_number,
        candidate_source,
        cv_text,
        cv_file_path,
        score,
        screening_result,
    )

    # Return to the Add Candidate page with a success message.
    return RedirectResponse("/hr/candidate/add?done=saved", status_code=303)



# Show the applications page and read the result message from the URL.
def hr_applications(request: Request, job_id: int = 0, view: str = "", done: str = ""):

    # Check that the logged-in user is an HR user.
    user, problem = check_role(request, "hr")

    # Stop if the user is not allowed to access this page.
    if problem is not None:
        return problem

    # Get the job from the database.
    job = job_tools.get_job(job_id)

    # Check that the job exists and belongs to this HR user.
    if job is None or job["created_by"] != user["user_id"]:
        return render(
            request,
            "message.html",
            {
                "title": "Not available",
                "text": "This job was not found.",
                "user": user,
            },
            status_code=404,
        )

    # Check that the selected application view is valid.
    if view not in ("applied", "shortlisted", "rejected", "selected", "offer_pending", "offer_rejected", "hired", ):
        view = ""

    # Messages shown after an interview selection action.
    messages = {
        "sent": "Interview invitations sent successfully.",
        "noselect": "Please select at least one shortlisted candidate.",
        "baddate": "Please pick a valid date and time.",
        "pastdate": "The interview time cannot be in the past.",
    }

    # Get all applications for the selected job.
    applications = job_tools.list_applications(job_id, view)

    # Get the shortlisted candidates in interview-ranking order.
    ranked_candidates = job_tools.list_ranked_candidates(job_id)

    # Show the applications page and send all required data to the HTML page.
    return render(
        request,
        "hr_applications.html",
        {
            "user": user,
            "job": job,
            "view": view,
            "applications": applications,
            "counts": job_tools.count_applications(job_id),
            "ranked_candidates": ranked_candidates,
            "info": messages.get(done, ""),
        },
    )

# The HR dashboard page.
def hr_dashboard_page(request: Request):

    # Make sure the logged-in user is an HR user.
    user, problem = check_role(request, "hr")

    # Stop if the user is not allowed to open this page.
    if problem is not None:
        return problem

    # Read the dashboard data from the database.
    dashboard = job_tools.hr_dashboard(user["user_id"])

    # Open the HR dashboard and send the jobs and summary counts.
    return render(
        request,
        "hr_dashboard.html",
        {
            "user": user,
            "jobs": dashboard["jobs"],
            "counts": dashboard["counts"],
        },
    )


# Show one application (only HR who made the job)
def hr_application(request: Request, candidate_id: int = 0, done: str = ""):
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    app_row = job_tools.get_application(candidate_id)
    job = job_tools.get_job(app_row["job_id"]) if app_row is not None else None
    if app_row is None or job is None or job["created_by"] != user["user_id"]:
        return render(request, "message.html",
                      {"title": "Not available", "text": "This application was not found.", "user": user}, status_code=404)

    messages = {
        "1": "Status updated.",
        "interview": "Interview saved. The candidate was emailed.",
        "sent": "Interview invitations sent successfully.",
        "noselect": "Please select at least one shortlisted candidate.",
        "notshort": "Shortlist the candidate first.",
        "baddate": "Please pick a valid date and time.",
        "pastdate": "The interview time cannot be in the past.",
        "feedback": "Feedback and rating saved.",
        "nointerview": "Schedule the interview first.",
        "badrating": "The rating must be a number from 1 to 5.",
        "replied": "Your reply was saved. The candidate can see it.",
        "badreply": "Please write a reply first.",
        "selected": "Candidate selected. The next step is to make an offer.",
        "offersaved": "Offer saved successfully. The candidate is now waiting for the offer step.",
        "badoffer": "Please enter the offered salary.",
        "finalrejected": "Candidate rejected after the final HR decision.",
    }
    return render(request, "hr_application.html", {
        "user": user, "app": app_row, "job": job,
        "answers": job_tools.get_answers(candidate_id), "info": messages.get(done, ""),
        "interview": job_tools.get_interview(candidate_id),
        "queries": job_tools.list_queries(candidate_id),
        "offer": job_tools.get_offer(candidate_id) if app_row["status"] in ("selected", "offer_pending", "hired") else None,
    })

# Schedule an interview with the current Schedule Interview form.
# This keeps the existing database and email functions unchanged.
def hr_interview_save(
    request: Request,
    background_tasks: BackgroundTasks,
    candidate_id: int = Form(0),
    interview_date: str = Form(""),
    interview_time: str = Form(""),
    interview_type: str = Form(""),
    interview_notes: str = Form(""),
):
    # Check that the logged-in user is an HR user.
    user, problem = check_role(request, "hr")

    # Stop if the user is not allowed to use this function.
    if problem is not None:
        return problem

    # Get the candidate application from the database.
    app_row = job_tools.get_application(candidate_id)

    # Get the job connected to this candidate.
    job = job_tools.get_job(
        app_row["job_id"]
    ) if app_row is not None else None

    # Make sure the application belongs to this HR user.
    if (
        app_row is None
        or job is None
        or job["created_by"] != user["user_id"]
    ):
        return render(
            request,
            "message.html",
            {
                "title": "Not available",
                "text": "This application was not found.",
                "user": user,
            },
            status_code=404,
        )

    # Build the return address for the candidate profile.
    back = (
        "/hr/application?candidate_id="
        + str(candidate_id)
        + "&done="
    )

    # Only shortlisted candidates can have an interview scheduled.
    if app_row["status"] != "shortlisted":
        return RedirectResponse(
            back + "notshort",
            status_code=303,
        )

    # Check that the HR entered both a date and a time.
    if interview_date.strip() == "" or interview_time.strip() == "":
        return RedirectResponse(
            back + "baddate",
            status_code=303,
        )

    # Combine the separate date and time fields from the form.
    when = (
        interview_date.strip()
        + " "
        + interview_time.strip()
    )

    # Convert the combined date and time into a Python datetime.
    try:
        moment = datetime.datetime.strptime(
            when,
            "%Y-%m-%d %H:%M",
        )
    except ValueError:
        return RedirectResponse(
            back + "baddate",
            status_code=303,
        )

    # Do not allow an interview time in the past.
    if moment < datetime.datetime.now():
        return RedirectResponse(
            back + "pastdate",
            status_code=303,
        )

    # Clean the interview type.
    interview_type = interview_type.strip()

    # Clean the interview notes and keep the existing 1500-character limit.
    interview_notes = interview_notes.strip()[:1500]

    # Start the instructions with the selected interview type.
    instructions = "Interview type: " + interview_type

    # Add interview notes if HR entered any.
    if interview_notes != "":
        instructions += (
            "\n\nInterview notes:\n"
            + interview_notes
        )

    # Save or update the interview using the existing function.
    job_tools.schedule_interview(
        candidate_id,
        moment.strftime("%Y-%m-%d %H:%M:00"),
        instructions,
    )

    # Send the existing interview email using the existing email function.
    background_tasks.add_task(
        email_tools.send_interview_email,
        app_row["email"],
        app_row["name"],
        job["title"],
        moment.strftime("%d %B %Y at %H:%M"),
        get_company_info()["company_name"],
        instructions,
    )

    # Return to the candidate profile with the existing success message.
    return RedirectResponse(
        back + "interview",
        status_code=303,
    )# HR selects shortlisted candidates, schedules their interview, and sends the existing interview email.
def hr_interview_select(
    request: Request,
    background_tasks: BackgroundTasks,
    selected_candidates: list[int] = Form([]),
    when: str = Form(""),
    instructions: str = Form(""),
):
    # Make sure the logged-in user is an HR user.
    user, problem = check_role(request, "hr")

    # Stop if the user is not allowed to use this function.
    if problem is not None:
        return problem

    # Stop if HR did not select any candidate.
    if not selected_candidates:
        return RedirectResponse(
            "/hr/applications?view=shortlisted&done=noselect",
            status_code=303,
        )

    # Clean the interview instructions before saving them.
    instructions = instructions.strip()[:1500]

    # Check that the HR entered an interview date and time.
    try:
        moment = datetime.datetime.strptime(
            when.strip(),
            "%Y-%m-%dT%H:%M",
        )
    except ValueError:
        return RedirectResponse(
            "/hr/applications?view=shortlisted&done=baddate",
            status_code=303,
        )

    # Stop HR from scheduling an interview in the past.
    if moment < datetime.datetime.now():
        return RedirectResponse(
            "/hr/applications?view=shortlisted&done=pastdate",
            status_code=303,
        )

    # Keep track of the job used for the selected candidates.
    job_id = 0

    # Process each selected candidate one by one.
    for candidate_id in selected_candidates:

        # Get the candidate application from the database.
        app_row = job_tools.get_application(candidate_id)

        # Get the job connected to this application.
        job = job_tools.get_job(
            app_row["job_id"]
        ) if app_row is not None else None

        # Skip candidates that are not valid or do not belong to this HR user.
        if (
            app_row is None
            or job is None
            or job["created_by"] != user["user_id"]
            or app_row["status"] != "shortlisted"
        ):
            continue

        # Remember the job ID for the return page.
        job_id = job["job_id"]

        # Save or update the interview using the existing function.
        job_tools.schedule_interview(
            candidate_id,
            moment.strftime("%Y-%m-%d %H:%M:00"),
            instructions,
        )

        # Send the existing interview email with the real date and time.
        background_tasks.add_task(
            email_tools.send_interview_email,
            app_row["email"],
            app_row["name"],
            job["title"],
            moment.strftime("%d %B %Y at %H:%M"),
            get_company_info()["company_name"],
            instructions,
        )

    # Return HR to the shortlisted candidates page.
    return RedirectResponse(
        "/hr/applications?job_id="
        + str(job_id)
        + "&view=shortlisted&done=sent",
        status_code=303,
    )
# Show the HR Selected Candidates page.
def hr_selected_candidates_page(request: Request):

    # Check that the logged-in person is an HR user.
    user, problem = check_role(request, "hr")

    # Stop if the logged-in person is not allowed to open this page.
    if problem is not None:
        return problem

    # Get all candidates whose status is hired.
    hired_candidates = job_tools.list_hired_candidates()

    # Show the Selected Candidates page.
    return render(
        request,
        "hr_selected_candidates.html",
        {
            "user": user,
            "hired_candidates": hired_candidates,
        },
    )


# The candidate's own applications, with the shortlisted section on top
def candidate_applications(request: Request, done: str = ""):
    user, problem = check_role(request, "candidate")
    if problem is not None:
        return problem

    infos = {"1": "Your application was sent.", "asked": "Your question was sent to HR."}
    errors = {"emptyq": "Please write your question first.",
              "toomany": "You already have 3 questions waiting for an answer. Please wait for HR to reply."}
    return render(request, "candidate_applications.html", {
        "user": user, "applications": job_tools.list_my_applications(user["user_id"]),
        "shortlisted": job_tools.list_my_shortlisted(user["user_id"]),
        "info": infos.get(done, ""), "error": errors.get(done, ""),
    })

# Candidate accepts an offer
def candidate_accept_offer(request: Request, candidate_id: int = Form(0)):
    user, problem = check_role(request, "candidate")
    if problem is not None:
        return problem

    app_row = job_tools.get_application(candidate_id)

    if (
        app_row is None
        or not job_tools.owns_application(user["user_id"], candidate_id)
        or app_row["status"] != "offer_pending"
    ):
        return render(
            request,
            "message.html",
            {
                "title": "Not available",
                "text": "This offer is not available.",
                "user": user,
            },
            status_code=404,
        )

    job_tools.accept_offer(candidate_id)

    return RedirectResponse(
        "/candidate/applications?done=offeraccepted",
        status_code=303,
    )


# Candidate rejects an offer
def candidate_reject_offer(request: Request, candidate_id: int = Form(0)):
    user, problem = check_role(request, "candidate")
    if problem is not None:
        return problem

    app_row = job_tools.get_application(candidate_id)

    if (
        app_row is None
        or not job_tools.owns_application(user["user_id"], candidate_id)
        or app_row["status"] != "offer_pending"
    ):
        return render(
            request,
            "message.html",
            {
                "title": "Not available",
                "text": "This offer is not available.",
                "user": user,
            },
            status_code=404,
        )

    job_tools.reject_offer(candidate_id)

    return RedirectResponse(
        "/candidate/applications?done=offerrejected",
        status_code=303,
    )


# ---------- Public careers pages (no login needed) ----------

# The public list of open jobs
def careers_page(request: Request):
    jobs = job_tools.list_published_jobs()
    return render(request, "careers.html", {
        "jobs": jobs,
        "departments": sorted({j["department"] for j in jobs if j["department"]}),
    })
# One public job: details only, and an Apply button
def careers_job(request: Request, job_id: int = 0):
    job = job_tools.get_job(job_id)
    if job is None or job["status"] != "published":
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job is not open.", "user": get_current_user(request)},
                      status_code=404)
    return render(request, "careers_job.html", {"job": job, "questions": job_tools.get_questions(job_id)})


# The public poster of a published job
def careers_poster(request: Request, job_id: int = 0):
    job = job_tools.get_job(job_id)
    if job is None or job["status"] != "published":
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job is not open.", "user": get_current_user(request)},
                      status_code=404)
    return render(request, "job_poster.html", {
        "job": job, "back_url": "/careers", "back_text": "Back to open positions",
        "apply_url": "/apply?job_id=" + str(job_id),
    })


# The Apply button: a candidate with an account goes to the normal form, everyone else to the guest form
def apply_entry(request: Request, job_id: int = 0):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse("/careers/apply?job_id=" + str(job_id), status_code=303)
    if user["role"] == "candidate":
        return RedirectResponse("/candidate/job?job_id=" + str(job_id), status_code=303)
    return render(request, "message.html",
                  {"title": "Candidates only", "text": "Only candidate accounts can apply for jobs.", "user": user},
                  status_code=403)

# Show the guest apply form (no login needed)
def careers_apply_page(request: Request, job_id: int = 0):
    job = job_tools.get_job(job_id)
    if job is None or job["status"] != "published" or (job["deadline"] != "" and job["deadline"] < str(datetime.date.today())):
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job is not open.", "user": get_current_user(request)},
                      status_code=404)

    form = {"name": "", "email": "", "phone": "", "experience_years": "", "education": "", "expected_salary": ""}
    return render(request, "careers_apply.html", {
        "job": job, "questions": job_tools.get_questions_with_ids(job_id), "form": form, "error": "",
    })


# Receive the guest application (no login needed)
async def careers_apply_submit(request: Request, background_tasks: BackgroundTasks):
    data = await request.form()
    job_id_text = str(data.get("job_id", "0"))
    job_id = int(job_id_text) if job_id_text.isdigit() else 0

    job = job_tools.get_job(job_id)
    if job is None or job["status"] != "published":
        return render(request, "message.html",
                      {"title": "Not available", "text": "This job is not open.", "user": get_current_user(request)},
                      status_code=404)

    questions = job_tools.get_questions_with_ids(job_id)
    form = {
        "name": str(data.get("name", "")).strip()[:100],
        "email": auth_tools.clean_email(str(data.get("email", ""))),
        "phone": str(data.get("phone", "")).strip()[:30],
        "experience_years": str(data.get("experience_years", "")).strip(),
        "education": str(data.get("education", "")).strip()[:200],
        "expected_salary": str(data.get("expected_salary", "")).strip(),
        "cv_text": "",
    }

    # Show the form again with an error (the typed text stays)
    def show_error(message):
        return render(request, "careers_apply.html", {
            "job": job, "questions": questions, "form": form, "error": message,
        }, status_code=400)

    # Rate limit: too many attempts from one IP address
    ip = get_client_ip(request)
    if job_tools.count_recent_attempts(ip) >= APPLY_LIMIT_PER_HOUR:
        return show_error("Too many applications from this connection. Please try again in an hour.")
    job_tools.log_apply_attempt(ip)

    # Deadline
    if job["deadline"] != "" and job["deadline"] < str(datetime.date.today()):
        return show_error("The deadline of this job has passed.")

    # Name, Gmail and phone
    if form["name"] == "":
        return show_error("Please type your name.")
    email_problem = auth_tools.check_gmail(form["email"])
    if email_problem != "":
        return show_error(email_problem)
    phone_digits = form["phone"].replace("+", "").replace(" ", "").replace("-", "")
    if not phone_digits.isdigit() or len(phone_digits) < 7 or len(phone_digits) > 15:
        return show_error("Please type a valid phone number (7 to 15 digits).")

    # One application per Gmail per job
    if job_tools.has_applied_email(form["email"], job_id):
        return show_error("This Gmail already applied to this job.")

    # Numbers and education
    if not form["experience_years"].isdigit() or int(form["experience_years"]) > 60:
        return show_error("Years of experience must be a number from 0 to 60.")
    if not form["expected_salary"].isdigit() or int(form["expected_salary"]) > 100000000:
        return show_error("Expected salary must be a number.")
    if form["education"] == "":
        return show_error("Please type your education.")
    experience_years = int(form["experience_years"])

    # The answers
    answers = []
    for question_id, text in questions:
        answer = str(data.get("answer_" + str(question_id), "")).strip()[:1000]
        if answer == "":
            return show_error("Please answer every question.")
        answers.append((question_id, answer))

    # The CV file
    cv = data.get("cv")
    if cv is None or not hasattr(cv, "filename") or cv.filename == "":
        return show_error("Please upload your CV.")
    content = await cv.read()
    file_problem = cv_tools.check_file(cv.filename, len(content))
    if file_problem != "":
        return show_error(file_problem)

    # Save the file, read it, and score it (same tools as the normal apply)
    saved_name = cv_tools.save_file(cv.filename, content)
    cv_text = cv_tools.read_text(saved_name)
    form["cv_text"] = cv_text[:20000]
    form["experience_years"] = experience_years
    form["expected_salary"] = int(form["expected_salary"])
    score, result = cv_tools.score_cv(cv_text, job, experience_years)

    # A guest has no account, so user_id is None
    guest = {"user_id": None, "name": form["name"], "email": form["email"], "phone": form["phone"]}
    try:
        job_tools.create_application(guest, job_id, form, saved_name, score, result, answers)
    except psycopg2.errors.UniqueViolation:
        # A double click saved it a moment ago
        return show_error("This Gmail already applied to this job.")

    # Send the "you have applied" email after the page is answered
    background_tasks.add_task(
        email_tools.send_application_email,
        form["email"], form["name"], job["title"], get_company_info()["company_name"],
    )
    return RedirectResponse("/careers/applied", status_code=303)


# The "thank you" page after a guest applied
def careers_applied(request: Request):
    return render(request, "message.html", {
        "title": "Application sent",
        "text": "Thank you! We received your application and sent a confirmation to your Gmail. HR will contact you by email.",
        "user": get_current_user(request),
    })

# ---------- HR: manager access ----------

# Build the Access page with the current managers and pending invites
def access_response(request, user, error="", info="", status_code=200):
    # Read both lists from the database and fill access.html
    return render(
        request, "access.html",
        {
            "user": user,
            "managers": access_tools.list_managers(),
            "invites": access_tools.list_pending_invites(),
            "error": error,
            "info": info,
        },
        status_code=status_code,
    )


# Show the Access page (only HR)
def access_page(request: Request, done: str = ""):
    # Check the role
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # Pick the green message that belongs to the short code in the web address (empty if unknown)
    info = DONE_MESSAGES.get(done, "")

    # Show the page
    return access_response(request, user, "", info)


# HR gives manager access to a Gmail (only HR)
def access_invite(request: Request, email: str = Form("")):
    # Check the role first: nothing below runs for a candidate, a manager or a visitor
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # Clean the Gmail and check that it is a valid Gmail address
    email = auth_tools.clean_email(email)
    email_problem = auth_tools.check_gmail(email)
    if email_problem != "":
        return access_response(request, user, email_problem, "", 400)

    # Give the access (or save the pending invite)
    result = access_tools.invite_manager(user["user_id"], email)

    # If it did not work, show why
    if not result["ok"]:
        return access_response(request, user, result["message"], "", 400)

    # It worked: reload the page with a green message code
    return RedirectResponse("/hr/access?done=" + result["code"], status_code=303)


# HR removes manager access (only HR)
def access_remove(request: Request, user_id: int = Form(0)):
    # Check the role first
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # Remove the access
    removed = access_tools.remove_manager(user_id)

    # If this person is not a manager, say so
    if not removed:
        return access_response(request, user, "That person is not a manager.", "", 400)

    # It worked: reload the page with a green message code
    return RedirectResponse("/hr/access?done=removed", status_code=303)


# HR cancels a pending invite (only HR)
def access_cancel(request: Request, invite_id: int = Form(0)):
    # Check the role first
    user, problem = check_role(request, "hr")
    if problem is not None:
        return problem

    # Cancel the invite
    cancelled = access_tools.cancel_invite(invite_id)

    # If there was no such pending invite, say so
    if not cancelled:
        return access_response(request, user, "That invite does not exist or is not pending.", "", 400)

    # It worked: reload the page with a green message code
    return RedirectResponse("/hr/access?done=cancelled", status_code=303)

# ---------- Forgot password ----------

# Send a reset code (same steps as send_verification_code, but for 'reset')
def send_reset_code(email):
    code = email_tools.make_code()                    # use the same module name as in send_verification_code
    auth_tools.save_new_reset_code(email, code)
    email_tools.send_reset_code_email(email, code)


# Build the reset page
def reset_response(request, email, error, info, status_code=200):
    return render(
        request, "reset_password.html",
        {"email": email, "error": error, "info": info, "dev_mode": config.EMAIL_MODE == "terminal", "user": None},
        status_code=status_code,
    )


# GET /forgot-password
def forgot_page(request: Request):
    return render(request, "forgot_password.html", {"error": "", "info": "", "email": "", "user": None})


# POST /forgot-password
def forgot_submit(request: Request, email: str = Form("")):
    email = auth_tools.clean_email(email)

    # Send only if this Gmail has an account and a code was not just sent
    user = auth_tools.get_user_by_email(email)
    if user is not None and auth_tools.can_send_reset_code(email):
        send_reset_code(email)

    # Always the same answer, so nobody can learn which Gmails have accounts
    return RedirectResponse("/reset-password?email=" + quote(email) + "&sent=1", status_code=303)


# GET /reset-password
def reset_page(request: Request, email: str = "", sent: str = ""):
    email = auth_tools.clean_email(email)
    info = ""
    if sent == "1":
        info = "If this Gmail has an account, a code was sent. You can ask again after one minute."
    return reset_response(request, email, "", info)


# POST /reset-password
def reset_submit(request: Request, email: str = Form(""), code: str = Form(""),
                 password: str = Form(""), password2: str = Form("")):
    email = auth_tools.clean_email(email)
    code = code.strip()

    if len(code) != 6 or not code.isdigit():
        return reset_response(request, email, "The code has exactly 6 digits.", "", 400)

    if len(password) < 8:
        return reset_response(request, email, "The password needs at least 8 characters.", "", 400)

    if password != password2:
        return reset_response(request, email, "The two passwords are not the same.", "", 400)

    error = auth_tools.check_reset_code(email, code)
    if error != "":
        return reset_response(request, email, error, "", 400)

    auth_tools.finish_password_reset(email, password)
    return RedirectResponse("/login?reset=1", status_code=303)
# ---------- Connect each address to its function (no decorators) ----------
router.add_api_route("/", home_page, methods=["GET"])
router.add_api_route("/health", health_check, methods=["GET"])
router.add_api_route("/api/company", company_json, methods=["GET"])
router.add_api_route("/signup", signup_page, methods=["GET"])
router.add_api_route("/signup", signup_submit, methods=["POST"])
router.add_api_route("/verify", verify_page, methods=["GET"])
router.add_api_route("/verify", verify_submit, methods=["POST"])
router.add_api_route("/resend", resend_code, methods=["POST"])
router.add_api_route("/login", login_page, methods=["GET"])
router.add_api_route("/login", login_submit, methods=["POST"])
router.add_api_route("/logout", logout, methods=["POST"])
router.add_api_route("/app", app_menu, methods=["GET"])
#router.add_api_route("/candidate", candidate_screen, methods=["GET"])
router.add_api_route("/manager", manager_screen, methods=["GET"])
router.add_api_route("/hr", hr_screen, methods=["GET"])
router.add_api_route("/hr/access", access_page, methods=["GET"])
router.add_api_route("/hr/access/invite", access_invite, methods=["POST"])
router.add_api_route("/hr/access/remove", access_remove, methods=["POST"])
router.add_api_route("/hr/access/cancel", access_cancel, methods=["POST"])
router.add_api_route("/hr/company", hr_company_page, methods=["GET"])
router.add_api_route("/hr/company", hr_company_submit, methods=["POST"])
router.add_api_route("/hr/jobs", hr_jobs_page, methods=["GET"])
router.add_api_route("/hr/jobs/edit", hr_job_edit, methods=["GET"])
router.add_api_route("/hr/jobs/save", hr_job_save, methods=["POST"])
router.add_api_route("/hr/jobs/suggest", hr_job_suggest, methods=["POST"])
router.add_api_route("/hr/jobs/poster", hr_job_poster, methods=["GET"])
router.add_api_route("/hr/jobs/questions", hr_questions_page, methods=["GET"])
router.add_api_route("/hr/jobs/questions/save", hr_questions_save, methods=["POST"])
router.add_api_route("/hr/jobs/review", hr_job_review, methods=["GET"])
router.add_api_route("/hr/jobs/send", hr_job_send, methods=["POST"])
# Route for closing a published job.
router.add_api_route("/hr/jobs/close", hr_job_close, methods=["POST"])
# Route for reopening a closed job.
router.add_api_route("/hr/jobs/open", hr_job_open, methods=["POST"])
# Route for deleting an allowed job.
router.add_api_route("/hr/jobs/delete", hr_job_delete, methods=["POST"])
router.add_api_route("/manager/job", manager_job, methods=["GET"])
router.add_api_route("/manager/decide", manager_decide, methods=["POST"])
router.add_api_route("/candidate/job", candidate_job, methods=["GET"])
router.add_api_route("/candidate/apply", candidate_apply, methods=["POST"])
router.add_api_route("/candidate/applications", candidate_applications, methods=["GET"])

# Show the HR Add Candidate page.
router.add_api_route("/hr/candidate/add", hr_manual_candidate_page, methods=["GET"])

# Save an HR-sourced candidate.
router.add_api_route("/hr/candidate/add", hr_manual_candidate_save, methods=["POST"])
router.add_api_route("/hr/applications", hr_applications, methods=["GET"])
router.add_api_route("/hr/application", hr_application, methods=["GET"])
router.add_api_route("/hr/application/status", hr_application_status, methods=["POST"])
router.add_api_route("/hr/application/cv", hr_cv_download, methods=["GET"])
router.add_api_route("/candidate/poster", candidate_poster, methods=["GET"])
router.add_api_route("/hr/interview/save", hr_interview_save, methods=["POST"])
# Allow HR to select shortlisted candidates for interview invitations.
router.add_api_route(
    "/hr/interview/select",
    hr_interview_select,
    methods=["POST"],
)
router.add_api_route("/hr/feedback/save", hr_feedback_save, methods=["POST"])
# Route used by HR to make the final decision.
router.add_api_route("/hr/final-decision", hr_final_decision, methods=["POST"])
router.add_api_route("/hr/offer/save", hr_offer_save, methods=["POST"])
router.add_api_route("/hr/dashboard", hr_dashboard_page, methods=["GET"])
router.add_api_route("/careers", careers_page, methods=["GET"])
router.add_api_route("/careers/job", careers_job, methods=["GET"])
router.add_api_route("/careers/poster", careers_poster, methods=["GET"])
router.add_api_route("/apply", apply_entry, methods=["GET"])
router.add_api_route("/careers/apply", careers_apply_page, methods=["GET"])
router.add_api_route("/careers/apply", careers_apply_submit, methods=["POST"])
router.add_api_route("/careers/applied", careers_applied, methods=["GET"])
router.add_api_route(
    "/candidate/offer/accept",
    candidate_accept_offer,
    methods=["POST"],
)

router.add_api_route(
    "/candidate/offer/reject",
    candidate_reject_offer,
    methods=["POST"],
)

# Send the saved offer letter to the candidate.
router.add_api_route(
    "/hr/offer/send",
    hr_offer_send,
    methods=["POST"],
)

# Save the offer when HR submits the offer form.
router.add_api_route("/hr/offer/save", hr_offer_save, methods=["POST"])

# Send the saved offer letter to the candidate.
router.add_api_route(
    "/hr/offer/send",
    hr_offer_send,
    methods=["POST"],
)

# Open the candidate's offer page using the secure token.
router.add_api_route(
    "/offer/response/{offer_token}",
    offer_response_page,
    methods=["GET"],
)

# Accept the candidate's offer.
router.add_api_route(
    "/offer/accept",
    offer_accept,
    methods=["POST"],
)

# Reject the candidate's offer.
router.add_api_route(
    "/offer/reject",
    offer_reject,
    methods=["POST"],
)

router.add_api_route(
    "/hr/interviews",
    hr_interviews_page,
    methods=["GET"]
)

# Open the HR home page.
router.add_api_route("/hr", hr_screen, methods=["GET"])

# Open the separate HR Interviews page.
router.add_api_route("/hr/interviews", hr_interviews_page, methods=["GET"])
# Open the separate HR Selected Candidates page.
router.add_api_route(
    "/hr/selected-candidates",
    hr_selected_candidates_page,
    methods=["GET"],
)

router.add_api_route("/forgot-password", forgot_page, methods=["GET"])
router.add_api_route("/forgot-password", forgot_submit, methods=["POST"])
router.add_api_route("/reset-password", reset_page, methods=["GET"])
router.add_api_route("/reset-password", reset_submit, methods=["POST"])