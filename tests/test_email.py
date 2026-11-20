import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import our email helper file
from app.services import email_tools
# Import our settings file
from app import config
# Make a random 6-digit code
my_code = email_tools.make_code()

# Say where we are sending it (to the same Gmail that sends, which is fine for a test)
print("Sending the code to:", config.EMAIL_SENDER)

# Send the code email and keep the result
result = email_tools.send_code_email(config.EMAIL_SENDER, my_code)

# Print what happened
print(result["message"])

# If it worked, show the code so we can compare it with the email
if result["success"]:
    print("The code in the email should be:", my_code)