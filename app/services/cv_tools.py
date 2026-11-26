
# This file screens a CV against the actual posted job.
# It checks education, relevant experience, and job-specific requirements.
# It does not use a fixed list of common skills.


# Import os for working with file paths and folders.
import os

# Import re for finding patterns inside CV and job text.
import re

# Import uuid for creating unique uploaded CV names.
import uuid


# Find the main project folder.
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# Create the uploads folder path.
import os
UPLOAD_DIR = "/tmp/uploads" if os.environ.get("VERCEL") else "uploads"

# Allow PDF and DOCX files.
ALLOWED = (".pdf", ".docx")

# Set the maximum CV size to 5 MB.
MAX_BYTES = 5 * 1024 * 1024


# These are normal English words.
# They are NOT skills.
# They are only ignored when comparing requirement phrases.
STOP_WORDS = set((
    "the and for with you your our are will have has can able good strong ability "
    "relevant experience years year work working team skills skill knowledge from "
    "that this such including etc role job must should more than least using use "
    "used well also any all not but their they them its into required requirement "
    "requirements candidate candidates position looking seeking responsible "
    "responsibilities duties preferred preferably minimum maximum of to in on at "
    "a an is be as or by"
).split())


# Check whether a CV file is valid.
def check_file(filename, size):

    # Get the file extension.
    ext = os.path.splitext(filename.lower())[1]

    # Reject unsupported files.
    if ext not in ALLOWED:
        return "Please upload a PDF or Word (.docx) file."

    # Reject empty files.
    if size == 0:
        return "The file is empty."

    # Reject files larger than 5 MB.
    if size > MAX_BYTES:
        return "The file is too big. The limit is 5 MB."

    # Return an empty message when everything is valid.
    return ""


# Save the uploaded CV.
# Connect to the Neon database.
def _connect():
    import psycopg2
    return psycopg2.connect(os.environ["DATABASE_URL"])


# Save the uploaded CV inside the database.
def save_file(filename, data):

    import psycopg2

    # Keep the original extension.
    ext = os.path.splitext(filename.lower())[1]

    # Create a unique file name.
    saved_name = uuid.uuid4().hex + ext

    # Store the file bytes in the cv_files table.
    conn = _connect()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO cv_files (saved_name, content) VALUES (%s, %s)",
                    (saved_name, psycopg2.Binary(data)),
                )
    finally:
        conn.close()

    return saved_name


# Load the CV bytes from the database (None if not found).
def load_file(saved_name):

    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT content FROM cv_files WHERE saved_name = %s",
                (saved_name,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return None
    return bytes(row[0])


# Read text from the saved CV.
def read_text(saved_name):

    import io

    data = load_file(saved_name)
    if data is None:
        return ""

    try:

        # Read PDF files.
        if saved_name.lower().endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")
            return "\n".join(pages)[:50000]

        # Read DOCX files.
        if saved_name.lower().endswith(".docx"):
            import docx
            document = docx.Document(io.BytesIO(data))
            paragraphs = []
            for paragraph in document.paragraphs:
                paragraphs.append(paragraph.text)
            return "\n".join(paragraphs)[:50000]

    except Exception as error:
        raise

    return ""
# Read text from the saved CV.
def read_text(saved_name):

    # Create the full CV path.
    path = os.path.join(UPLOAD_DIR, saved_name)

    try:

        # Read PDF files.
        if saved_name.lower().endswith(".pdf"):

            # Import the PDF reader.
            from pypdf import PdfReader

            # Open the PDF.
            reader = PdfReader(path)

            # Create an empty page list.
            pages = []

            # Read every page.
            for page in reader.pages:

                # Extract text from the page.
                page_text = page.extract_text() or ""

                # Add the page text.
                pages.append(page_text)

            # Return the combined text.
            return "\n".join(pages)[:50000]

        # Read DOCX files.
        if saved_name.lower().endswith(".docx"):

            # Import the Word reader.
            import docx

            # Open the Word document.
            document = docx.Document(path)

            # Create an empty paragraph list.
            paragraphs = []

            # Read every paragraph.
            for paragraph in document.paragraphs:

                # Add paragraph text.
                paragraphs.append(paragraph.text)

            # Return the combined text.
            return "\n".join(paragraphs)[:50000]

    # Catch file-reading errors.
    except Exception as error:

        # Print the error for debugging.
        print("Reading the CV failed:", error)

    # Return empty text when the file cannot be read.
    return ""


# Clean text before comparison.
def clean_text(text):

    # Convert None into empty text.
    if text is None:
        return ""

    # Convert the value to lowercase.
    text = str(text).lower()

    # Make different dash characters consistent.
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Replace multiple spaces with one space.
    text = re.sub(r"\s+", " ", text)

    # Return cleaned text.
    return text.strip()


# Check whether a phrase exists in text.
def contains_phrase(text, phrase):

    # Clean the main text.
    text = clean_text(text)

    # Clean the phrase.
    phrase = clean_text(phrase)

    # Empty phrases cannot match.
    if phrase == "":
        return False

    # Search the phrase as a complete word/phrase.
    pattern = (
        r"(?<![a-z0-9+#])"
        + re.escape(phrase)
        + r"(?![a-z0-9+#])"
    )

    # Return True when found.
    return re.search(pattern, text) is not None


# Clean a requirement phrase.
def clean_requirement_phrase(phrase):

    # Clean spaces and lowercase.
    phrase = clean_text(phrase)

    # Remove bullet symbols.
    phrase = phrase.strip("-•*")

    # Remove punctuation at the edges.
    phrase = phrase.strip(".,:;()[]")

    # Return the cleaned phrase.
    return phrase.strip()


# Check whether a phrase contains useful information.
def is_useful_requirement(phrase):

    # Clean the phrase.
    phrase = clean_requirement_phrase(phrase)

    # Ignore empty text.
    if phrase == "":
        return False

    # Split into words.
    words = phrase.split()

    # Ignore a single common word.
    if len(words) == 1 and words[0] in STOP_WORDS:
        return False

    # Ignore numbers only.
    if re.fullmatch(r"[\d\s+.-]+", phrase):
        return False

    # Ignore extremely long paragraphs.
    if len(words) > 12:
        return False

    # Return True when useful.
    return True


# Extract phrases from the actual job posting.
def extract_job_requirement_phrases(job):

    # Read the job title.
    title = str(job.get("title", ""))

    # Read the requirements.
    requirements = str(job.get("requirements", ""))

    # Read the description.
    description = str(job.get("description", ""))

    # Start with the requirements.
    source_text = requirements

    # Add the description.
    if description.strip() != "":
        source_text += " " + description

    # Add the title.
    if title.strip() != "":
        source_text += " " + title

    # Replace common separators.
    source_text = source_text.replace("\n", "|")
    source_text = source_text.replace("•", "|")
    source_text = source_text.replace(";", "|")

    # Split into smaller pieces.
    pieces = re.split(
        r"\||\.\s+|,\s+",
        source_text
    )

    # Create an empty result list.
    found = []

    # Process every piece.
    for piece in pieces:

        # Clean the piece.
        phrase = clean_requirement_phrase(piece)

        # Keep useful pieces only.
        if is_useful_requirement(phrase):

            # Avoid duplicate phrases.
            if phrase not in found:

                # Add the actual job phrase.
                found.append(phrase)

    # Return the job phrases.
    return found


# Extract education requirements from the actual job.
def extract_job_education(job):

    # Read the job requirements.
    requirements = str(job.get("requirements", ""))

    # Read the job description.
    description = str(job.get("description", ""))

    # Combine both fields.
    job_text = requirements + " " + description

    # Create an empty education list.
    education = []

    # Look for education wording.
    patterns = [
        r"(?:bachelor|master|doctorate|phd|diploma|degree)[^.,;|\n]{0,80}",
        r"\b(?:bs|ms|bsc|msc|bba|mba|bcs|mcs)\b[^.,;|\n]{0,60}",
    ]

    # Check every pattern.
    for pattern in patterns:

        # Find education phrases.
        matches = re.findall(
            pattern,
            job_text,
            flags=re.IGNORECASE
        )

        # Process every match.
        for match in matches:

            # Clean the education phrase.
            phrase = clean_requirement_phrase(match)

            # Keep useful phrases.
            if is_useful_requirement(phrase):

                # Avoid duplicates.
                if phrase not in education:

                    # Add the education requirement.
                    education.append(phrase)

    # Return education requirements.
    return education


# Extract education information from the CV.
def extract_cv_education(cv_text):

    # Create an empty education list.
    education = []

    # Use the actual CV text.
    patterns = [
        r"(?:bachelor|master|doctorate|phd|diploma|degree)[^.,;|\n]{0,100}",
        r"\b(?:bs|ms|bsc|msc|bba|mba|bcs|mcs)\b[^.,;|\n]{0,80}",
    ]

    # Check every pattern.
    for pattern in patterns:

        # Find education entries.
        matches = re.findall(
            pattern,
            cv_text,
            flags=re.IGNORECASE
        )

        # Process every match.
        for match in matches:

            # Clean the result.
            phrase = clean_requirement_phrase(match)

            # Keep useful results.
            if is_useful_requirement(phrase):

                # Avoid duplicates.
                if phrase not in education:

                    # Add CV education.
                    education.append(phrase)

    # Return education information.
    return education


# Calculate education matching.
def calculate_education_match(job, cv_text):

    # Extract education required by the job.
    job_education = extract_job_education(job)

    # Extract education from the CV.
    cv_education = extract_cv_education(cv_text)

    # If the job does not mention education,
    # do not punish the candidate.
    if len(job_education) == 0:
        return 100, job_education, cv_education, []

    # Create lists for matches and missing education.
    matched = []
    missing = []

    # Check every job education requirement.
    for required in job_education:

        # Check exact match first.
        if contains_phrase(
            " ".join(cv_education),
            required
        ):

            # Store the match.
            matched.append(required)

        else:

            # Break the requirement into useful words.
            words = []

            # Check every word.
            for word in required.split():

                # Ignore normal language words.
                if word not in STOP_WORDS and len(word) > 2:

                    # Store useful word.
                    words.append(word)

            # Count matching words.
            matches = 0

            # Check each useful word.
            for word in words:

                # Search the CV.
                if contains_phrase(cv_text, word):

                    # Count the match.
                    matches += 1

            # Calculate similarity.
            if len(words) > 0:
                ratio = matches / len(words)
            else:
                ratio = 0

            # Accept a related education match.
            if ratio >= 0.50:
                matched.append(required + " (related)")
            else:
                missing.append(required)

    # Calculate education percentage.
    score = int(round(
        len(matched) / len(job_education) * 100
    ))

    # Return the result.
    return score, matched, cv_education, missing


# Extract experience years from the CV.
def extract_cv_experience_years(cv_text):

    # Clean the CV.
    text = clean_text(cv_text)

    # IMPORTANT:
    # These patterns require "experience" or a work-related phrase.
    # This prevents "23 years old" from becoming 23 years of experience.
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+of\s+(?:professional\s+)?experience",
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience",
        r"(?:professional|work)\s+experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?",
    ]

    # Create an empty list.
    years_found = []

    # Check every pattern.
    for pattern in patterns:

        # Find experience values.
        matches = re.findall(pattern, text)

        # Add every value.
        for value in matches:

            # Convert the value into a number.
            years_found.append(float(value))

    # Return zero when nothing is found.
    if len(years_found) == 0:
        return 0

    # Return the largest valid value.
    return max(years_found)


# Extract required experience years from the job.
def extract_job_experience_years(job):

    # Read job requirements.
    requirements = str(job.get("requirements", ""))

    # Read job description.
    description = str(job.get("description", ""))

    # Combine job text.
    job_text = clean_text(
        requirements + " " + description
    )

    # Experience requirement patterns.
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+of\s+experience",
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+experience",
        r"minimum\s+of\s+(\d+(?:\.\d+)?)\s*years?",
        r"at\s+least\s+(\d+(?:\.\d+)?)\s*years?",
    ]

    # Create an empty list.
    years_found = []

    # Check every pattern.
    for pattern in patterns:

        # Find matches.
        matches = re.findall(pattern, job_text)

        # Store every value.
        for value in matches:
            years_found.append(float(value))

    # Return zero when no requirement exists.
    if len(years_found) == 0:
        return 0

    # Return the highest requirement found.
    return max(years_found)


# Extract job-related experience phrases.
def extract_job_experience_terms(job):

    # Read requirements.
    requirements = str(job.get("requirements", ""))

    # Read description.
    description = str(job.get("description", ""))

    # Combine job text.
    source_text = requirements + " " + description

    # Replace common separators.
    source_text = source_text.replace("\n", "|")
    source_text = source_text.replace("•", "|")
    source_text = source_text.replace(";", "|")

    # Split into pieces.
    pieces = re.split(
        r"\||\.\s+|,\s+",
        source_text
    )

    # Create an empty list.
    terms = []

    # Process every piece.
    for piece in pieces:

        # Clean the phrase.
        phrase = clean_requirement_phrase(piece)

        # Skip empty text.
        if phrase == "":
            continue

        # Skip phrases that only specify years.
        if re.fullmatch(
            r"(minimum|at least)?\s*\d+(?:\.\d+)?\s*\+?\s*years?",
            phrase
        ):
            continue

        # Count useful words.
        useful_words = []

        # Check each word.
        for word in phrase.split():

            # Ignore common language.
            if word not in STOP_WORDS and len(word) > 2:

                # Add useful word.
                useful_words.append(word)

        # Skip phrases with no useful words.
        if len(useful_words) == 0:
            continue

        # Keep normal-sized phrases.
        if len(useful_words) <= 12:

            # Avoid duplicates.
            if phrase not in terms:

                # Add the phrase.
                terms.append(phrase)

    # Return job experience terms.
    return terms


# Calculate experience matching.
def calculate_experience_match(
    job,
    cv_text,
    experience_years
):

    # Extract experience directly from the CV.
    cv_years = extract_cv_experience_years(cv_text)

    # Use the existing supplied experience value only
    # when the CV does not contain a clear value.
    if cv_years == 0 and experience_years is not None:

        # Try to convert the existing value.
        try:
            cv_years = float(experience_years)

        # Ignore invalid values.
        except:
            cv_years = 0

    # Extract required years from the job.
    required_years = extract_job_experience_years(job)

    # Extract job-specific experience terms.
    job_terms = extract_job_experience_terms(job)

    # Create an empty match list.
    matched_terms = []

    # Check each job term.
    for term in job_terms:

        # Check exact phrase.
        if contains_phrase(cv_text, term):

            # Store exact match.
            matched_terms.append(term)

        else:

            # Break the phrase into useful words.
            words = []

            # Check every word.
            for word in term.split():

                # Ignore general words.
                if word not in STOP_WORDS and len(word) > 2:

                    # Add useful word.
                    words.append(word)

            # Count matching words.
            matches = 0

            # Check each useful word.
            for word in words:

                # Search CV.
                if contains_phrase(cv_text, word):

                    # Count the match.
                    matches += 1

            # Calculate similarity.
            if len(words) > 0:
                similarity = matches / len(words)
            else:
                similarity = 0

            # Accept related experience.
            if similarity >= 0.60:

                # Store related match.
                matched_terms.append(
                    term + " (related)"
                )

    # Calculate relevance.
    if len(job_terms) > 0:
        relevance = (
            len(matched_terms)
            / len(job_terms)
        )
    else:
        relevance = 1

    # Calculate the experience-years score.
    if required_years == 0:

        # No experience-year requirement.
        year_score = 100

    elif cv_years >= required_years:

        # Candidate meets the requirement.
        year_score = 100

    elif cv_years > 0:

        # Candidate has some experience.
        year_score = int(round(
            cv_years / required_years * 100
        ))

    else:

        # No experience found.
        year_score = 0

    # Give 60% weight to experience years.
    year_points = year_score * 0.60

    # Give 40% weight to job relevance.
    relevance_points = relevance * 100 * 0.40

    # Calculate the final experience score.
    score = int(round(
        year_points + relevance_points
    ))

    # Keep the score inside 0-100.
    score = min(max(score, 0), 100)

    # Return the experience information.
    return (
        score,
        cv_years,
        required_years,
        matched_terms,
        job_terms,
    )


# Extract requirements directly from the posted job.
#
# There is NO fixed skill list.
def extract_job_skills(job):

    # Read the job title.
    title = str(job.get("title", ""))

    # Read the job requirements.
    requirements = str(job.get("requirements", ""))

    # Read the job description.
    description = str(job.get("description", ""))

    # Start with the requirements.
    source_text = requirements

    # Add the description.
    if description.strip() != "":
        source_text += " " + description

    # Add the title.
    if title.strip() != "":
        source_text += " " + title

    # Replace common separators.
    source_text = source_text.replace("\n", "|")
    source_text = source_text.replace("•", "|")
    source_text = source_text.replace(";", "|")

    # Split the job text.
    pieces = re.split(
        r"\||\.\s+|,\s+",
        source_text
    )

    # Create an empty requirement list.
    skills = []

    # Process every job phrase.
    for piece in pieces:

        # Clean the phrase.
        phrase = clean_requirement_phrase(piece)

        # Ignore empty phrases.
        if phrase == "":
            continue

        # Ignore phrases that only contain experience years.
        if re.search(
            r"\b\d+(?:\.\d+)?\s*\+?\s*years?\b",
            phrase
        ):
            continue

        # Count useful words.
        useful_words = []

        # Check each word.
        for word in phrase.split():

            # Ignore general words.
            if word not in STOP_WORDS and len(word) > 2:

                # Store useful word.
                useful_words.append(word)

        # Ignore phrases without useful words.
        if len(useful_words) == 0:
            continue

        # Ignore very long sentences.
        if len(useful_words) <= 12:

            # Avoid duplicates.
            if phrase not in skills:

                # Add actual job requirement.
                skills.append(phrase)

    # Return job-specific requirements.
    return skills


# Find how strongly a job requirement appears in a CV.
def find_requirement_match(
    requirement,
    cv_text
):

    # Clean the requirement.
    requirement = clean_text(requirement)

    # Clean the CV.
    cv_text = clean_text(cv_text)

    # Check the complete phrase first.
    if contains_phrase(
        cv_text,
        requirement
    ):
        return "exact"

    # Create an empty useful-word list.
    words = []

    # Check every word.
    for word in requirement.split():

        # Ignore normal language words.
        if word not in STOP_WORDS and len(word) > 2:

            # Store useful word.
            words.append(word)

    # Count matching words.
    matched_words = 0

    # Check every useful word.
    for word in words:

        # Search the CV.
        if contains_phrase(
            cv_text,
            word
        ):

            # Count the match.
            matched_words += 1

    # Calculate similarity.
    if len(words) > 0:
        similarity = (
            matched_words / len(words)
        )
    else:
        similarity = 0

    # Accept a related match when enough words match.
    if similarity >= 0.60:
        return "related"

    # Otherwise the requirement is missing.
    return "missing"


# Calculate the job-specific requirement score.
def calculate_skill_score(
    job_skills,
    cv_text
):

    # Start the score at zero.
    score = 0

    # Create exact match list.
    exact_matches = []

    # Create related match list.
    related_matches = []

    # Create missing list.
    missing_skills = []

    # If no job requirements were found,
    # do not punish the candidate.
    if len(job_skills) == 0:

        # Return a full score.
        return (
            100,
            exact_matches,
            related_matches,
            missing_skills,
        )

    # Check every job requirement.
    for requirement in job_skills:

        # Find the match type.
        match_type = find_requirement_match(
            requirement,
            cv_text
        )

        # Give full credit to exact matches.
        if match_type == "exact":

            # Add one full point.
            score += 1

            # Store the requirement.
            exact_matches.append(
                requirement
            )

        # Give half credit to related matches.
        elif match_type == "related":

            # Add half a point.
            score += 0.5

            # Store the requirement.
            related_matches.append(
                requirement
            )

        # Store missing requirements.
        else:

            # Add the requirement to missing.
            missing_skills.append(
                requirement
            )

    # Calculate percentage.
    percentage = (
        score / len(job_skills)
    ) * 100

    # Return the result.
    return (
        round(percentage, 1),
        exact_matches,
        related_matches,
        missing_skills,
    )


# Create a SHORT screening message.
#
# This function is the important fix for the massive result.
# It does not print entire CV or job paragraphs.
def create_screening_result(
    final_score,
    education_score,
    experience_score,
    skill_score,
    missing_skills
):

    # Decide the overall label.
    if final_score >= 85:
        label = "Excellent Match"

    elif final_score >= 70:
        label = "Strong Match"

    elif final_score >= 55:
        label = "Good Match"

    elif final_score >= 40:
        label = "Partial Match"

    else:
        label = "Low Match"

    # Start a short result.
    result = label + "."

    # Add the three category scores.
    result += (
        " Education: "
        + str(education_score)
        + "%."
    )

    result += (
        " Experience: "
        + str(experience_score)
        + "%."
    )

    result += (
        " Skills: "
        + str(skill_score)
        + "%."
    )

    # Show only the number of missing requirements.
    if len(missing_skills) > 0:

        # Add the count only.
        result += (
            " Missing job requirements: "
            + str(len(missing_skills))
            + "."
        )

    else:

        # Tell HR that no job requirements were missing.
        result += " Missing job requirements: 0."

    # Return the short result.
    return result


# Main CV screening function.
#
# IMPORTANT:
# The function name and arguments are unchanged.
def score_cv(
    cv_text,
    job,
    experience_years
):

    # Stop if the CV could not be read.
    if cv_text.strip() == "":

        # Return a simple failure message.
        return (
            0,
            "The CV text could not be read. HR should open the file manually."
        )

    # Calculate education.
    (
        education_score,
        education_matches,
        candidate_education,
        education_missing
    ) = calculate_education_match(
        job,
        cv_text
    )

    # Calculate experience.
    (
        experience_score,
        cv_years,
        required_years,
        experience_matches,
        experience_requirements
    ) = calculate_experience_match(
        job,
        cv_text,
        experience_years
    )

    # Extract job-specific requirements.
    job_skills = extract_job_skills(job)

    # Compare the CV with those requirements.
    (
        skill_score,
        exact_skills,
        related_skills,
        missing_skills
    ) = calculate_skill_score(
        job_skills,
        cv_text
    )

    # Education has 30% weight.
    education_points = (
        education_score * 0.30
    )

    # Experience has 30% weight.
    experience_points = (
        experience_score * 0.30
    )

    # Job-specific requirements have 40% weight.
    skill_points = (
        skill_score * 0.40
    )

    # Calculate the final score.
    final_score = int(round(
        education_points
        + experience_points
        + skill_points
    ))

    # Keep the score between 0 and 100.
    final_score = min(
        max(final_score, 0),
        100
    )

    # Create the short HR-friendly result.
    result = create_screening_result(
        final_score,
        education_score,
        experience_score,
        skill_score,
        missing_skills
    )

    # Return exactly two values.
    # Existing HRM code can continue using:
    # score, result = score_cv(...)
    return final_score, result


# Test the screening file directly.
if __name__ == "__main__":

    # Create a sample job.
    # These requirements are intentionally written in the job.
    # There is no predefined skills list.
    test_job = {
        "title": "Admin Assistant",

        "requirements": (
            "Relevant degree or equal practical experience. "
            "Good communication and teamwork. "
            "Minimum 2 years of administrative experience. "
            "Ability to learn quickly and meet deadlines."
        ),

        "description": (
            "We are looking for an admin to join our team."
        ),
    }

    # Create a sample CV.
    test_cv = """
    EDUCATION

    BS Business Administration

    EXPERIENCE

    Admin Assistant with 3 years of experience.
    Worked with office administration.
    Good communication and teamwork.
    Managed daily office tasks.

    SKILLS

    Communication
    Teamwork
    Office Administration
    """

    # Run the screening.
    score, result = score_cv(
        test_cv,
        test_job,
        0
    )

    # Print the score.
    print("SCORE:", score)

    # Print the short result.
    print("RESULT:", result)
