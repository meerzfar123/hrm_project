import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import requests, the library that sends requests to an API
import requests

# The address where our API is running (the same one you used in Chrome)
API_URL = "http://localhost:8000"

# Send a GET request to the main address and keep the reply
reply = requests.get(API_URL + "/")

# Print the status code (200 means success)
print("Status code:", reply.status_code)

# Print the answer as a Python dictionary
print("Answer:", reply.json())