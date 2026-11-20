import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import getpass, which asks for a password without showing the letters on screen
import getpass

# Import our settings file and our login helper file
from app import config
from app.services import auth_tools
# Read the Gmail of the first HR from config.py and clean it
email = auth_tools.clean_email(config.FIRST_HR_EMAIL)

# Check that it is a valid Gmail address
problem = auth_tools.check_gmail(email)

# If it is not valid, say why and stop
if problem != "":
    print("FIRST_HR_EMAIL in config.py is not valid:", problem)
else:
    # Tell the person which account we are about to create
    print("Creating the first HR account for:", email)

    # Ask for the name and the password twice (the typing stays invisible)
    name = input("Full name: ").strip()
    password = getpass.getpass("Choose a password (at least 8 characters, typing is invisible): ")
    again = getpass.getpass("Type the same password again: ")

    # Check what was typed, one problem at a time
    if name == "":
        print("The name cannot be empty. Nothing was created.")
    elif len(password) < 8:
        print("The password needs at least 8 characters. Nothing was created.")
    elif password != again:
        print("The two passwords are not the same. Nothing was created.")
    else:
        # "try" means: attempt this code, and if something goes wrong, jump to "except"
        try:
            # Save the HR account (or turn an existing account with this Gmail into HR)
            auth_tools.save_first_hr(name, email, password)
            print("First HR account is ready:", email, "(role: hr)")
        # If anything failed, show the reason
        except Exception as error:
            print("FAILED. Reason:", error)