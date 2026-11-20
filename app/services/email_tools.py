# Import smtplib, a standard Python library that sends email (nothing to install)
import smtplib

# Import secrets, a standard library that makes safe random numbers
import secrets

# Import EmailMessage, a standard tool that builds an email (From, To, Subject, text)
from email.message import EmailMessage
from app import database as db
# Import our settings file (config.py) to read the Gmail address, the app password and the mode
from app import config
# This function makes a random 6-digit code, for example "042917"
def make_code():
    # Pick a safe random number from 0 up to 999999
    number = secrets.randbelow(1000000)

    # Turn the number into text and add zeros in front until it has 6 digits
    code = str(number).zfill(6)

    # Give the code back to whoever asked for it
    return code


# This function sends one email (through Gmail, or just shows it on screen in terminal mode)
def send_email(to_address, subject, body):
    # TERMINAL MODE: show the email on the screen and stop here. No internet is needed
    if config.EMAIL_MODE == "terminal":
        # Print a line of equal signs so the email is easy to see in the terminal
        print("=" * 50)

        # Warn that nothing was really sent
        print("DEV MODE: this email is NOT really sent")

        # Show who it would go to, the subject and the text (the 6-digit code is inside)
        print("To:", to_address)
        print("Subject:", subject)
        print(body)

        # Print another line to close the box
        print("=" * 50)

        # Tell the caller it "worked" so the rest of the program can continue
        return {"success": True, "message": "DEV MODE: email shown in the terminal, not sent."}

    # GMAIL MODE: send a real email. "try" means: attempt this code, and if it fails, jump to "except"
    try:
        # Build the email like filling in a letter
        message = EmailMessage()

        # Who sends the email
        message["From"] = config.EMAIL_SENDER

        # Who receives the email
        message["To"] = to_address

        # The subject line
        message["Subject"] = subject

        # The text inside the email
        message.set_content(body)

        # Open a secure (SSL) connection to Gmail on port 465, wait at most 20 seconds
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20)

        # Log in with the Gmail address and the app password
        server.login(config.EMAIL_SENDER, config.EMAIL_APP_PASSWORD)

        # Send the email
        server.send_message(message)

        # Close the connection politely
        server.quit()

        # Tell the caller it worked
        return {"success": True, "message": "Email sent to " + to_address}

    # This runs when Gmail refuses the login (wrong Gmail or wrong app password)
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": "Gmail refused the login. Check EMAIL_SENDER and EMAIL_APP_PASSWORD in config.py.",
        }

    # This runs for any other problem (no internet, blocked port, wrong address)
    except Exception as error:
        return {"success": False, "message": str(error)}


# This function sends the verification code email
def send_code_email(to_address, code):
    # The subject line of the email
    subject = "Your HRM verification code"

    # The text of the email, with the code inside
    body = (
        "Your verification code is: " + code + "\n\n"
        "It expires in 10 minutes. If you did not ask for it, please ignore this email."
    )

    # Send it with the function above and give back the result
    return send_email(to_address, subject, body)
# This function sends the "you have applied" email to a candidate
def send_application_email(to_address, name, job_title, company_name):
    # The subject line of the email
    subject = "We received your application for " + job_title

    # The text of the email
    body = (
        "Hello " + name + ",\n\n"
        "Thank you for applying for the position of " + job_title + " at " + company_name + ".\n"
        "We have received your application. Our HR team will review it and contact you "
        "if you are shortlisted.\n\n"
        "You can follow the status of your application any time on our careers website, "
        "under My applications.\n\n"
        "Best regards,\n"
        + company_name + " HR team"
    )

    # Send it with the function above and give back the result
    return send_email(to_address, subject, body)
# One shared helper: the greeting and the signature of every candidate email
def candidate_mail(to_address, name, subject, middle, company_name):
    body = "Hello " + name + ",\n\n" + middle + "\n\nBest regards,\n" + company_name + " HR team"
    return send_email(to_address, subject, body)


# The candidate was shortlisted
def send_shortlist_email(to_address, name, job_title, company_name):
    middle = ("Good news! After reviewing your application for " + job_title + ", you have been shortlisted.\n"
              "We will contact you soon with the interview details.")
    return candidate_mail(to_address, name, "You are shortlisted for " + job_title, middle, company_name)


# The candidate was not selected
def send_reject_email(to_address, name, job_title, company_name):
    middle = ("Thank you for your interest in " + job_title + ". After careful review, we will not move forward "
              "with your application at this time.\nWe wish you success and welcome you to apply again in the future.")
    return candidate_mail(to_address, name, "Update on your application for " + job_title, middle, company_name)


# Save the feedback and rating after the interview. Give back True if it worked
def save_feedback(candidate_id, feedback, rating):
    return db.execute(
        "UPDATE interviews SET feedback = %s, rating = %s WHERE candidate_id = %s;",
        (feedback, rating, candidate_id),
    ) == 1
# An interview was scheduled (the email also carries the special instructions)
def send_interview_email(to_address, name, job_title, when_text, company_name, instructions=""):
    middle = "Your interview for " + job_title + " is scheduled for: " + when_text + "."
    if instructions != "":
        middle += "\n\nSpecial instructions:\n" + instructions
    middle += ("\n\nIf you have any question before the interview, please ask it on our careers website, "
               "under My applications.")
    return candidate_mail(to_address, name, "Interview scheduled for " + job_title, middle, company_name)



# Send the offer letter link to the candidate.
def send_offer_email(
    to_address,
    name,
    job_title,
    salary,
    joining_date,
    company_name,
    offer_url,
):
    # Create the middle part of the candidate email.
    middle = (
        "Congratulations!\n\n"
        "We are pleased to offer you the position of "
        + job_title
        + " at "
        + company_name
        + ".\n\n"
        "Offered Salary: "
        + str(salary)
        + "\n"
        "Joining Date: "
        + str(joining_date)
        + "\n\n"
        "Please review your complete offer letter using the link below:\n\n"
        + offer_url
        + "\n\n"
        "Please use the offer page to accept or reject this offer."
    )

    # Send the offer email through the existing candidate email helper.
    return candidate_mail(
        to_address,
        name,
        "Job Offer - " + job_title,
        middle,
        company_name,
    )
# Sends the password reset code email
def send_reset_code_email(to_address, code):
    subject = "Reset your HRM password"
    body = (
        "Your password reset code is: " + code + "\n\n"
        "It expires in 10 minutes. If you did not ask for it, please ignore this email "
        "and your password will stay the same."
    )
    return send_email(to_address, subject, body)