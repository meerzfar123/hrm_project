import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import our AI helper file
from app.services import ai_tools
# Ask for a job text and keep the answer and its source
data, source = ai_tools.suggest_job_text("Accountant", "Finance")

# "ai" means Gemini answered. "template" means the ready-made text was used
print("Source:", source)

# Show the first 150 letters of the description
print(data["description"][:150])