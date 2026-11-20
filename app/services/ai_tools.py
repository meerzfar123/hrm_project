# Import json (reads JSON text) and requests (sends web requests)
import json
import requests

# Import our settings file
from app import config
# The first part of the web address of the Gemini service. The model name is added after it
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/"


# Ready-made job text, used when the AI is not available
def fallback_text(title):
    # Give back a dictionary with the three texts
    return {
        "description": (
            "We are looking for a " + title + " to join our team. You will work with colleagues "
            "on real projects, take ownership of your tasks, and help us deliver quality results "
            "for our clients."
        ),
        "requirements": (
            "- Relevant experience for the " + title + " role\n"
            "- Good communication and teamwork\n"
            "- Ability to learn quickly and meet deadlines\n"
            "- Relevant degree or equal practical experience"
        ),
        "benefits": "- Competitive salary\n- Learning and growth\n- Friendly team\n- Medical cover",
    }


# Ready-made screening questions, used when the AI is not available
def fallback_questions(title):
    # Give back a list of five questions
    return [
        "How many years of experience do you have for the " + title + " role?",
        "Which skills from the requirements are your strongest? Give one example of your work.",
        "Why do you want to join our company?",
        "What is your expected monthly salary?",
        "When can you start working with us?",
    ]


# Read the key and the model name from config.py. Give back (key, model). The key is "" if there is none
def get_ai_settings():
    # getattr gives the default value when a line is missing in config.py
    key = getattr(config, "GEMINI_API_KEY", "")
    model = getattr(config, "GEMINI_MODEL", "gemini-flash-latest")

    # A key that still starts with "paste" is only a placeholder, so treat it as no key
    if key.startswith("paste"):
        key = ""

    # Give both back
    return key, model


# Send one prompt to Gemini and give back the answer as Python data (a dictionary or a list)
def ask_gemini(prompt, key, model):
    # Build the full web address for this model
    url = GEMINI_URL + model + ":generateContent"

    # Send the prompt. The key goes in a header, so it never appears in a web address or a log line
    reply = requests.post(
        url,
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        },
        timeout=60,
    )

    # Stop with an error if Gemini answered with a problem code (for example 404 or 429)
    reply.raise_for_status()

    # Take the answer text out of the reply and turn the JSON text into Python data
    text = reply.json()["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)


# Ask Gemini for job text. Give back (data, source). The source is "ai" or "template"
def suggest_job_text(title, department):
    # Read the settings. No key means we use the ready-made text
    key, model = get_ai_settings()
    if key == "":
        return fallback_text(title), "template"

    # The instruction for the AI. It gets only the title and the department, nothing private
    prompt = (
        "Write a job post for the role: " + title + ". Department: " + (department or "not given") + ". "
        "Reply with JSON only, with exactly three keys: description (a short paragraph), "
        "requirements (5 bullet lines starting with '- '), benefits (4 bullet lines starting with '- ')."
    )

    # "try" means: attempt this code, and if anything fails, jump to "except"
    try:
        # Ask Gemini
        data = ask_gemini(prompt, key, model)

        # Keep only the three keys, as text, with a length limit
        result = {}
        for name in ("description", "requirements", "benefits"):
            value = data.get(name, "")

            # If the AI sent a list of lines, join them into one text
            if isinstance(value, list):
                lines = []
                for item in value:
                    lines.append(str(item))
                value = "\n".join(lines)

            result[name] = str(value)[:3000]

        # Tell the caller that this text came from the AI
        return result, "ai"

    # Any problem: print the reason in the terminal and use the ready-made text
    except Exception as error:
        print("AI suggestion failed:", error)
        return fallback_text(title), "template"


# Ask Gemini for screening questions. Give back (list_of_questions, source)
def suggest_questions(title, requirements):
    # Read the settings. No key means we use the ready-made questions
    key, model = get_ai_settings()
    if key == "":
        return fallback_questions(title), "template"

    # The instruction for the AI
    prompt = (
        "Write 6 short screening questions for candidates applying to the job: " + title + ". "
        "Requirements: " + requirements[:1500] + ". "
        "Reply with JSON only: a list of 6 strings."
    )

    # "try" means: attempt this code, and if anything fails, jump to "except"
    try:
        # Ask Gemini
        data = ask_gemini(prompt, key, model)

        # Keep at most 10 questions, each cut to 300 letters, and skip empty ones
        questions = []
        for item in data[:10]:
            item = str(item).strip()[:300]
            if item != "":
                questions.append(item)

        # An empty list is useless, so use the ready-made questions instead
        if len(questions) == 0:
            return fallback_questions(title), "template"

        # Tell the caller that these questions came from the AI
        return questions, "ai"

    # Any problem: print the reason in the terminal and use the ready-made questions
    except Exception as error:
        print("AI questions failed:", error)
        return fallback_questions(title), "template"