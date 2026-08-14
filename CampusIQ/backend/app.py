from flask import Flask, request, jsonify
from flask_cors import CORS

import json
import os
import re
import unicodedata
from difflib import SequenceMatcher


# =========================================================
# OPTIONAL FACULTY SCRAPER
# =========================================================

try:
    from faculty_scraper import fetch_faculty_data
except Exception:
    fetch_faculty_data = None


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

CORS(app)


# =========================================================
# OFFICIAL BIT URLS
# =========================================================

OFFICIAL_BIT_URL = "https://www.bitsathy.ac.in/"

FACULTY_URL = (
    "https://www.bitsathy.ac.in/departments/faculty/"
)

SPECIAL_LABS_URL = (
    "https://www.bitsathy.ac.in/special-labs/"
)

PLACEMENT_URL = (
    "https://www.bitsathy.ac.in/placement/"
)

ACHIEVEMENT_URL = (
    "https://www.bitsathy.ac.in/achievement/"
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

FACULTY_DATA_FILE = os.path.join(
    BASE_DIR,
    "faculty_data.json"
)

COLLEGE_DATA_FILE = os.path.join(
    BASE_DIR,
    "college_data.json"
)


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(value):

    if value is None:
        return ""

    value = unicodedata.normalize(
        "NFKC",
        str(value)
    )

    value = value.replace(
        "\xa0",
        " "
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def normalize(value):

    value = clean_text(value).lower()

    value = value.replace(
        "&",
        " and "
    )

    value = re.sub(
        r"[-_/]+",
        " ",
        value
    )

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def compact(value):

    return normalize(
        value
    ).replace(
        " ",
        ""
    )


# =========================================================
# LOAD JSON SAFELY
# =========================================================

def load_json_file(
    filename,
    default=None
):

    if default is None:
        default = []

    if not os.path.exists(filename):

        print(
            f"WARNING: {os.path.basename(filename)} "
            f"not found."
        )

        return default

    try:

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data

    except Exception as error:

        print(
            f"ERROR reading {filename}:",
            error
        )

        return default


# =========================================================
# FACULTY DATA CLEANING
# =========================================================

def clean_faculty_data(data):

    cleaned = []

    seen = set()

    if not isinstance(data, list):
        return cleaned

    for item in data:

        if not isinstance(item, dict):
            continue

        name = clean_text(
            item.get("name")
        )

        designation = clean_text(
            item.get("designation")
        )

        department = clean_text(
            item.get("department")
        )

        profile_url = clean_text(
            item.get("profile_url")
        )

        if not name:
            continue

        if not profile_url:
            continue

        clean_url = (
            profile_url
            .split("#")[0]
            .rstrip("/")
        )

        if clean_url in seen:
            continue

        seen.add(clean_url)

        cleaned.append({

            "name": name,

            "designation":
                designation,

            "department":
                department,

            "is_hod":
                bool(
                    item.get(
                        "is_hod",
                        False
                    )
                ),

            "profile_url":
                clean_url

        })

    return cleaned


# =========================================================
# LOAD FACULTY DATA
# =========================================================

def load_faculty_data():

    print(
        "Loading BIT faculty data..."
    )

    # -----------------------------------------------------
    # FIRST USE faculty_data.json
    # -----------------------------------------------------

    if os.path.exists(
        FACULTY_DATA_FILE
    ):

        data = load_json_file(
            FACULTY_DATA_FILE
        )

        cleaned = clean_faculty_data(
            data
        )

        if cleaned:

            print(
                f"Loaded {len(cleaned)} faculty "
                f"profiles from faculty_data.json"
            )

            return cleaned

    # -----------------------------------------------------
    # FALLBACK SCRAPER
    # -----------------------------------------------------

    if fetch_faculty_data:

        try:

            print(
                "faculty_data.json unavailable."
            )

            print(
                "Connecting to official BIT "
                "faculty website..."
            )

            data = fetch_faculty_data()

            cleaned = clean_faculty_data(
                data
            )

            print(
                f"Scraped {len(cleaned)} faculty profiles."
            )

            return cleaned

        except Exception as error:

            print(
                "Faculty scraper failed:",
                error
            )

    return []


# =========================================================
# LOAD FACULTY
# =========================================================

FACULTY_DATA = load_faculty_data()


# =========================================================
# COLLEGE DATA
# =========================================================

def normalize_college_record(item):

    if not isinstance(item, dict):
        return None

    category = clean_text(
        item.get("category")
        or item.get("type")
        or item.get("section")
        or ""
    )

    title = clean_text(
        item.get("title")
        or item.get("name")
        or item.get("heading")
        or ""
    )

    url = clean_text(
        item.get("url")
        or item.get("source_url")
        or item.get("link")
        or ""
    )

    content = clean_text(
        item.get("content")
        or item.get("text")
        or item.get("description")
        or item.get("body")
        or ""
    )

    # Some scraped files may use "data"
    # instead of "content".

    if not content:

        raw_data = item.get("data")

        if isinstance(raw_data, str):
            content = clean_text(raw_data)

        elif isinstance(raw_data, list):

            content = clean_text(
                " ".join(
                    str(x)
                    for x in raw_data
                )
            )

        elif isinstance(raw_data, dict):

            content = clean_text(
                " ".join(
                    str(v)
                    for v in raw_data.values()
                )
            )

    if not (
        category
        or title
        or url
        or content
    ):
        return None

    return {

        "category":
            category,

        "title":
            title,

        "url":
            url,

        "content":
            content

    }


def load_college_data():

    print(
        "Loading BIT college data..."
    )

    if not os.path.exists(
        COLLEGE_DATA_FILE
    ):

        print(
            "WARNING: college_data.json not found."
        )

        return []

    data = load_json_file(
        COLLEGE_DATA_FILE
    )

    records = []

    # -----------------------------------------------------
    # Normal list format
    # -----------------------------------------------------

    if isinstance(data, list):

        for item in data:

            record = normalize_college_record(
                item
            )

            if record:
                records.append(record)

    # -----------------------------------------------------
    # Dictionary format
    # -----------------------------------------------------

    elif isinstance(data, dict):

        # If actual records are inside "data"
        if isinstance(
            data.get("data"),
            list
        ):

            for item in data["data"]:

                record = normalize_college_record(
                    item
                )

                if record:
                    records.append(record)

        else:

            record = normalize_college_record(
                data
            )

            if record:
                records.append(record)

    print(
        f"Loaded {len(records)} college information records "
        f"from college_data.json"
    )

    return records


# =========================================================
# LOAD COLLEGE DATA
# =========================================================

COLLEGE_DATA = load_college_data()


# =========================================================
# DEPARTMENT ALIASES
# =========================================================

DEPARTMENT_ALIASES = {

    "artificial intelligence and data science": [
        "ai&ds",
        "ai ds",
        "aids",
        "ai and ds",
        "artificial intelligence data science",
        "artificial intelligence and data science"
    ],

    "artificial intelligence and machine learning": [
        "ai&ml",
        "ai ml",
        "aiml",
        "ai and ml",
        "artificial intelligence machine learning",
        "artificial intelligence and machine learning"
    ],

    "computer technology": [
        "ct",
        "computer tech",
        "computer technology"
    ],

    "computer science and engineering": [
        "cse",
        "computer science",
        "computer science and engineering"
    ],

    "electronics and communication engineering": [
        "ece",
        "electronics communication",
        "electronics and communication engineering"
    ],

    "electronics and instrumentation engineering": [
        "eie",
        "electronics instrumentation",
        "electronics and instrumentation engineering"
    ],

    "electrical and electronics engineering": [
        "eee",
        "electrical electronics",
        "electrical and electronics engineering"
    ],

    "mechanical engineering": [
        "mech",
        "mechanical engineering"
    ],

    "civil engineering": [
        "civil",
        "civil engineering"
    ],

    "information technology": [
        "it",
        "information technology"
    ],

    "agricultural engineering": [
        "agri",
        "agricultural engineering"
    ],

    "biotechnology": [
        "biotech",
        "biotechnology"
    ],

    "food technology": [
        "food tech",
        "food technology"
    ],

    "fashion technology": [
        "fashion",
        "fashion technology"
    ],

    "textile technology": [
        "textile",
        "textile technology"
    ]

}


# =========================================================
# INTENT WORDS
# =========================================================

INTENT_WORDS = {

    "who",
    "is",
    "the",
    "of",
    "and",
    "for",
    "in",
    "at",
    "from",
    "give",
    "tell",
    "me",
    "about",
    "find",
    "show",
    "search",
    "details",
    "detail",
    "information",
    "info",
    "faculty",
    "staff",
    "member",
    "members",
    "department",
    "dept",
    "please",
    "what",
    "which",
    "their",
    "there",
    "are",
    "any",
    "list",
    "all",
    "my",
    "college",
    "campus",
    "prof",
    "dr"
}


# =========================================================
# COLLEGE INTENT DETECTION
# =========================================================

SPECIAL_LAB_WORDS = [
    "special lab",
    "special labs",
    "special laboratory",
    "special laboratories",
    "speciallab",
    "speciallabs"
]


PLACEMENT_WORDS = [
    "placement",
    "placements",
    "campus placement",
    "campus placements",
    "recruitment",
    "recruiters",
    "recruiter",
    "placement cell",
    "training and placement",
    "tnp"
]


ACHIEVEMENT_WORDS = [
    "achievement",
    "achievements",
    "award",
    "awards",
    "recognition",
    "recognitions",
    "accomplishment",
    "accomplishments"
]


COLLEGE_GENERAL_WORDS = [
    "college",
    "campus",
    "bitsathy",
    "bannari amman",
    "institute",
    "admission",
    "admissions",
    "hostel",
    "library",
    "transport",
    "canteen",
    "scholarship",
    "course",
    "courses",
    "academic",
    "academics",
    "examination",
    "exams",
    "exam",
    "fees",
    "fee",
    "laboratory",
    "laboratories",
    "lab",
    "facilities"
]


def contains_phrase(
    question,
    phrases
):

    q = normalize(
        question
    )

    for phrase in phrases:

        p = normalize(
            phrase
        )

        if p in q:
            return True

    return False


def detect_college_intent(question):

    q = normalize(
        question
    )

    # -----------------------------------------------------
    # SPECIAL LABS HAVE HIGHEST PRIORITY
    # -----------------------------------------------------

    if contains_phrase(
        q,
        SPECIAL_LAB_WORDS
    ):

        return "special_labs"


    # -----------------------------------------------------
    # PLACEMENT
    # -----------------------------------------------------

    if contains_phrase(
        q,
        PLACEMENT_WORDS
    ):

        return "placement"


    # -----------------------------------------------------
    # ACHIEVEMENTS
    # -----------------------------------------------------

    if contains_phrase(
        q,
        ACHIEVEMENT_WORDS
    ):

        return "achievement"


    # -----------------------------------------------------
    # GENERAL COLLEGE
    # -----------------------------------------------------

    if contains_phrase(
        q,
        COLLEGE_GENERAL_WORDS
    ):

        return "general"


    return None


# =========================================================
# DETECT COLLEGE CATEGORY
# =========================================================

def record_category_matches(
    record,
    intent
):

    category = normalize(
        record.get(
            "category",
            ""
        )
    )

    title = normalize(
        record.get(
            "title",
            ""
        )
    )

    url = normalize(
        record.get(
            "url",
            ""
        )
    )

    if intent == "special_labs":

        return (
            "special lab" in category
            or
            "special lab" in title
            or
            "/special-labs" in url
        )


    if intent == "placement":

        return (
            "placement" in category
            or
            "placement" in title
            or
            "/placement" in url
        )


    if intent == "achievement":

        return (
            "achievement" in category
            or
            "achievement" in title
            or
            "award" in title
            or
            "recognition" in title
            or
            "/achievement" in url
        )


    return True


# =========================================================
# REMOVE SCRAPING GARBAGE
# =========================================================

def clean_college_content(
    content
):

    content = clean_text(
        content
    )

    if not content:
        return ""

    # Remove repeated image/file IDs such as:
    #
    # P1017835 P1018015 DSC_1474 IMG_8721
    #
    # These appeared in your screenshot and are
    # not useful to the user.

    content = re.sub(

        r"\b(?:P\d{5,}|IMG[_-]?\d{3,}|DSC[_-]?\d{3,})\b",

        " ",

        content,

        flags=re.IGNORECASE

    )

    # Remove excessive spaces.

    content = re.sub(
        r"\s+",
        " ",
        content
    )

    return content.strip()


# =========================================================
# SCORE COLLEGE RECORD
# =========================================================

def score_college_record(
    question,
    record,
    intent
):

    q = normalize(
        question
    )

    title = normalize(
        record.get(
            "title",
            ""
        )
    )

    category = normalize(
        record.get(
            "category",
            ""
        )
    )

    content = normalize(
        record.get(
            "content",
            ""
        )
    )

    url = normalize(
        record.get(
            "url",
            ""
        )
    )

    score = 0


    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    if intent == "special_labs":

        if "special lab" in category:
            score += 100

        if "special lab" in title:
            score += 100

        if "special-labs" in url:
            score += 80


    elif intent == "placement":

        if "placement" in category:
            score += 100

        if "placement" in title:
            score += 100

        if "placement" in url:
            score += 80


    elif intent == "achievement":

        if "achievement" in category:
            score += 100

        if "achievement" in title:
            score += 100

        if "award" in title:
            score += 60

        if "recognition" in title:
            score += 60


    # -----------------------------------------------------
    # QUESTION WORD MATCHING
    # -----------------------------------------------------

    question_words = [

        word

        for word in q.split()

        if len(word) >= 3

        and word not in INTENT_WORDS

    ]


    # -----------------------------------------------------
    # TITLE MATCH
    # -----------------------------------------------------

    for word in question_words:

        if word in title:

            score += 35


    # -----------------------------------------------------
    # CATEGORY MATCH
    # -----------------------------------------------------

    for word in question_words:

        if word in category:

            score += 25


    # -----------------------------------------------------
    # CONTENT MATCH
    # -----------------------------------------------------

    for word in question_words:

        if word in content:

            score += 5


    # -----------------------------------------------------
    # URL MATCH
    # -----------------------------------------------------

    for word in question_words:

        if word in url:

            score += 15


    return score


# =========================================================
# FIND COLLEGE INFORMATION
# =========================================================

def find_college_records(
    question,
    intent
):

    if not COLLEGE_DATA:
        return []


    candidates = []


    for record in COLLEGE_DATA:

        if not record_category_matches(
            record,
            intent
        ):
            continue


        score = score_college_record(
            question,
            record,
            intent
        )


        if score > 0:

            candidates.append(
                (
                    score,
                    record
                )
            )


    candidates.sort(

        key=lambda item: (
            -item[0],
            item[1].get(
                "title",
                ""
            )
        )

    )


    return [

        record

        for score, record
        in candidates

    ]


# =========================================================
# FORMAT COLLEGE RECORD
# =========================================================

def format_college_record(
    record
):

    title = clean_text(
        record.get(
            "title"
        )
    )

    category = clean_text(
        record.get(
            "category"
        )
    )

    url = clean_text(
        record.get(
            "url"
        )
    )

    content = clean_college_content(
        record.get(
            "content"
        )
    )


    result = ""


    if title:

        result += (
            f"{title}\n"
        )


    if category:

        result += (
            f"Category: {category}\n"
        )


    if content:

        result += (
            f"\n{content}\n"
        )


    if url:

        result += (
            f"\nSource page: {url}"
        )


    return result.strip()


# =========================================================
# ANSWER COLLEGE QUESTION
# =========================================================

def answer_college_question(
    question,
    intent
):

    records = find_college_records(
        question,
        intent
    )


    if not records:

        if intent == "special_labs":

            return jsonify({

                "success":
                    True,

                "answer":
                    "I could not find specific Special Labs "
                    "information matching your question in "
                    "the currently loaded official BIT college data.\n\n"
                    f"Please refer to the official BIT Special Labs page:\n"
                    f"{SPECIAL_LABS_URL}",

                "source":
                    "Official BIT Special Labs Website",

                "source_url":
                    SPECIAL_LABS_URL

            })


        if intent == "placement":

            return jsonify({

                "success":
                    True,

                "answer":
                    "I could not find specific Placement "
                    "information matching your question in "
                    "the currently loaded official BIT college data.\n\n"
                    f"Please refer to the official BIT Placement page:\n"
                    f"{PLACEMENT_URL}",

                "source":
                    "Official BIT Placement Website",

                "source_url":
                    PLACEMENT_URL

            })


        if intent == "achievement":

            return jsonify({

                "success":
                    True,

                "answer":
                    "I could not find specific Achievement "
                    "information matching your question in "
                    "the currently loaded official BIT college data.\n\n"
                    f"Please refer to the official BIT Achievement page:\n"
                    f"{ACHIEVEMENT_URL}",

                "source":
                    "Official BIT Achievement Website",

                "source_url":
                    ACHIEVEMENT_URL

            })


        return None


    # -----------------------------------------------------
    # SPECIAL LABS
    # -----------------------------------------------------

    if intent == "special_labs":

        # If a specific lab was requested,
        # return the strongest matching records.

        best_records = records[:10]


        answer_parts = []


        for record in best_records:

            formatted = format_college_record(
                record
            )

            if formatted:
                answer_parts.append(
                    formatted
                )


        return jsonify({

            "success":
                True,

            "answer":
                "According to the official BIT Special Labs data:\n\n"
                +
                "\n\n".join(
                    answer_parts
                ),

            "source":
                "Official BIT Special Labs Website",

            "source_url":
                SPECIAL_LABS_URL

        })


    # -----------------------------------------------------
    # PLACEMENT
    # -----------------------------------------------------

    if intent == "placement":

        best_records = records[:10]

        answer_parts = []


        for record in best_records:

            formatted = format_college_record(
                record
            )

            if formatted:
                answer_parts.append(
                    formatted
                )


        return jsonify({

            "success":
                True,

            "answer":
                "According to the official BIT Placement data:\n\n"
                +
                "\n\n".join(
                    answer_parts
                ),

            "source":
                "Official BIT Placement Website",

            "source_url":
                PLACEMENT_URL

        })


    # -----------------------------------------------------
    # ACHIEVEMENTS
    # -----------------------------------------------------

    if intent == "achievement":

        best_records = records[:10]

        answer_parts = []


        for record in best_records:

            formatted = format_college_record(
                record
            )

            if formatted:
                answer_parts.append(
                    formatted
                )


        return jsonify({

            "success":
                True,

            "answer":
                "According to the official BIT Achievement data:\n\n"
                +
                "\n\n".join(
                    answer_parts
                ),

            "source":
                "Official BIT Achievement Website",

            "source_url":
                ACHIEVEMENT_URL

        })


    return None


# =========================================================
# DETECT DEPARTMENT
# =========================================================

def detect_department(
    question
):

    q_norm = normalize(
        question
    )

    q_compact = compact(
        question
    )


    actual_departments = sorted(

        {
            clean_text(
                faculty.get(
                    "department"
                )
            )

            for faculty
            in FACULTY_DATA

            if faculty.get(
                "department"
            )

        },

        key=len,

        reverse=True

    )


    # -----------------------------------------------------
    # EXACT DEPARTMENT FROM DATA
    # -----------------------------------------------------

    for department in actual_departments:

        normalized_department = normalize(
            department
        )

        if (
            normalized_department
            in q_norm
        ):

            return department

        if (
            compact(department)
            in q_compact
        ):

            return department


    # -----------------------------------------------------
    # ALIASES
    # -----------------------------------------------------

    for canonical, aliases in DEPARTMENT_ALIASES.items():

        for alias in aliases:

            alias_normalized = normalize(
                alias
            )


            if len(alias_normalized) <= 3:

                pattern = (

                    r"(?<![a-z0-9])"
                    +
                    re.escape(
                        alias_normalized
                    )
                    +
                    r"(?![a-z0-9])"

                )

                found = re.search(
                    pattern,
                    q_norm
                )

            else:

                found = (

                    alias_normalized
                    in q_norm

                    or

                    compact(
                        alias_normalized
                    )
                    in q_compact

                )


            if found:

                for department in actual_departments:

                    if (
                        normalize(
                            department
                        )
                        ==
                        normalize(
                            canonical
                        )
                    ):

                        return department


    return None


# =========================================================
# DETECT DESIGNATION
# =========================================================

def detect_designation(
    question
):

    q = normalize(
        question
    )


    if re.search(
        r"\b(hod|head of department|department head|head)\b",
        q
    ):

        return "head"


    if (
        "assistant professor"
        in q
        or
        "assistant prof"
        in q
    ):

        return "assistant professor"


    if (
        "associate professor"
        in q
        or
        "associate prof"
        in q
    ):

        return "associate professor"


    if re.search(
        r"\bprofessor\b",
        q
    ):

        return "professor"


    if re.search(
        r"\bprof\b",
        q
    ):

        return "professor"


    return None


# =========================================================
# CHECK HOD
# =========================================================

def is_head(
    faculty
):

    if faculty.get(
        "is_hod"
    ) is True:

        return True


    designation = normalize(
        faculty.get(
            "designation"
        )
    )


    return bool(
        re.search(
            r"\bhead\b",
            designation
        )
    )


# =========================================================
# DESIGNATION MATCH
# =========================================================

def designation_matches(
    faculty,
    requested
):

    if not requested:
        return True


    designation = normalize(
        faculty.get(
            "designation"
        )
    )


    if requested == "head":

        return is_head(
            faculty
        )


    if requested == "assistant professor":

        return designation.startswith(
            "assistant professor"
        )


    if requested == "associate professor":

        return designation.startswith(
            "associate professor"
        )


    if requested == "professor":

        return designation == "professor"


    return False


# =========================================================
# TOKENIZE FACULTY NAME QUERY
# =========================================================

def tokenize_name_query(
    question
):

    q = normalize(
        question
    )


    for canonical in DEPARTMENT_ALIASES:

        q = q.replace(
            normalize(canonical),
            " "
        )


    designation_phrases = [

        "assistant professor",
        "associate professor",
        "head of department",
        "department head",
        "professor"

    ]


    for phrase in designation_phrases:

        q = q.replace(
            phrase,
            " "
        )


    words = q.split()


    result = []


    for word in words:

        if word in INTENT_WORDS:
            continue

        if len(word) < 2:
            continue

        result.append(
            word
        )


    return result


# =========================================================
# FIND FACULTY BY NAME
# =========================================================

def find_faculty_by_name(
    question,
    candidates=None
):

    pool = (

        candidates
        if candidates is not None
        else FACULTY_DATA

    )


    q_norm = normalize(
        question
    )

    q_compact = compact(
        question
    )

    q_tokens = tokenize_name_query(
        question
    )


    scored = []


    for faculty in pool:

        name = clean_text(
            faculty.get(
                "name"
            )
        )


        name_normalized = normalize(
            name
        )

        name_compact = compact(
            name
        )

        name_tokens = (
            name_normalized.split()
        )


        score = 0


        # Exact full name

        if (
            name_normalized
            and
            name_normalized in q_norm
        ):

            score = 100


        # Compact name

        if (
            name_compact
            and
            name_compact in q_compact
        ):

            score = max(
                score,
                98
            )


        # Token match

        overlap = sum(

            1

            for token
            in q_tokens

            if token in name_tokens

        )


        if overlap:

            score = max(

                score,

                50
                +
                min(
                    overlap,
                    4
                )
                * 12

            )


        # Fuzzy match

        if q_tokens:

            query_name = " ".join(
                q_tokens
            )


            ratio = SequenceMatcher(

                None,

                query_name,

                name_normalized

            ).ratio()


            if ratio >= 0.65:

                score = max(

                    score,

                    int(
                        ratio * 70
                    )

                )


        if score > 0:

            scored.append(
                (
                    score,
                    faculty
                )
            )


    scored.sort(

        key=lambda item: (
            -item[0],
            item[1].get(
                "name",
                ""
            )
        )

    )


    return [

        item[1]

        for item
        in scored

    ]


# =========================================================
# FORMAT FACULTY
# =========================================================

def format_faculty(
    faculty,
    number=None
):

    prefix = (

        f"{number}. "

        if number is not None
        else ""

    )


    hod = (

        "Yes"
        if is_head(faculty)
        else
        "No"

    )


    return (

        f"{prefix}"
        f"{faculty.get('name', 'Unknown')}\n"

        f"Designation: "
        f"{faculty.get('designation') or 'Not listed'}\n"

        f"Department: "
        f"{faculty.get('department') or 'Not listed'}\n"

        f"HOD: {hod}\n"

        f"Profile: "
        f"{faculty.get('profile_url', '')}"

    )


# =========================================================
# ANSWER FACULTY QUESTION
# =========================================================

def answer_faculty_question(
    question
):

    department = detect_department(
        question
    )

    designation = detect_designation(
        question
    )


    # -----------------------------------------------------
    # DEPARTMENT + HOD
    # -----------------------------------------------------

    if (
        department
        and
        designation == "head"
    ):

        matches = [

            faculty

            for faculty
            in FACULTY_DATA

            if normalize(
                faculty.get(
                    "department"
                )
            )
            ==
            normalize(
                department
            )

            and
            is_head(
                faculty
            )

        ]


        if matches:

            return (

                "The HOD of "
                f"{department} is:\n\n"

                +
                format_faculty(
                    matches[0]
                ),

                FACULTY_URL

            )


        return (

            f"I could not find an HOD listed for "
            f"{department} in the current official "
            f"BIT faculty data.",

            FACULTY_URL

        )


    # -----------------------------------------------------
    # DEPARTMENT + DESIGNATION
    # -----------------------------------------------------

    if (
        department
        and
        designation
    ):

        matches = [

            faculty

            for faculty
            in FACULTY_DATA

            if normalize(
                faculty.get(
                    "department"
                )
            )
            ==
            normalize(
                department
            )

            and
            designation_matches(
                faculty,
                designation
            )

        ]


        if matches:

            if designation == "assistant professor":

                label = "Assistant Professors"

            elif designation == "associate professor":

                label = "Associate Professors"

            elif designation == "professor":

                label = "Professors"

            else:

                label = "Heads"


            blocks = [

                format_faculty(
                    faculty,
                    index + 1
                )

                for index, faculty
                in enumerate(
                    matches
                )

            ]


            return (

                f"{label} in "
                f"{department} "
                f"({len(matches)}):\n\n"

                +

                "\n\n".join(
                    blocks
                ),

                FACULTY_URL

            )


    # -----------------------------------------------------
    # DEPARTMENT ONLY
    # -----------------------------------------------------

    if department:

        matches = [

            faculty

            for faculty
            in FACULTY_DATA

            if normalize(
                faculty.get(
                    "department"
                )
            )
            ==
            normalize(
                department
            )

        ]


        if matches:

            blocks = [

                format_faculty(
                    faculty,
                    index + 1
                )

                for index, faculty
                in enumerate(
                    matches
                )

            ]


            return (

                f"Faculty of "
                f"{department} "
                f"({len(matches)}):\n\n"

                +

                "\n\n".join(
                    blocks
                ),

                FACULTY_URL

            )


    # -----------------------------------------------------
    # FACULTY NAME
    # -----------------------------------------------------

    name_matches = find_faculty_by_name(
        question
    )


    if name_matches:

        best = name_matches[0]


        exact_name = (

            normalize(
                best["name"]
            )
            in
            normalize(
                question
            )

        )


        exact_compact = (

            compact(
                best["name"]
            )
            in
            compact(
                question
            )

        )


        if (
            exact_name
            or
            exact_compact
        ):

            return (

                "Faculty information:\n\n"
                +
                format_faculty(
                    best
                ),

                best.get(
                    "profile_url",
                    FACULTY_URL
                )

            )


        top_matches = name_matches[:5]


        return (

            "I found these possible faculty matches:\n\n"
            +

            "\n\n".join(

                format_faculty(
                    faculty,
                    index + 1
                )

                for index, faculty
                in enumerate(
                    top_matches
                )

            )

            +

            "\n\nPlease enter the faculty member's "
            "full name for an exact result.",

            FACULTY_URL

        )


    # -----------------------------------------------------
    # HEAD WITHOUT DEPARTMENT
    # -----------------------------------------------------

    if designation == "head":

        matches = [

            faculty

            for faculty
            in FACULTY_DATA

            if is_head(
                faculty
            )

        ]


        if matches:

            return (

                "Faculty matching the requested "
                f"HOD/Head designation "
                f"({len(matches)}):\n\n"

                +

                "\n\n".join(

                    format_faculty(
                        faculty,
                        index + 1
                    )

                    for index, faculty
                    in enumerate(
                        matches
                    )

                ),

                FACULTY_URL

            )


    return (

        "I could not identify a specific faculty "
        "member, department, or designation.\n\n"

        "Try:\n"

        "• Who is the HOD of Artificial Intelligence and Data Science?\n"
        "• Faculty in Computer Technology\n"
        "• Assistant Professors in Computer Technology\n"
        "• Tell me about Dr Gomathi R\n"
        "• What is the designation of Dr Uvaraja V C?",

        FACULTY_URL

    )


# =========================================================
# MAIN ASK API
# =========================================================

@app.route(
    "/api/ask",
    methods=["POST"]
)
def ask_question():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success":
                False,

            "answer":
                "Please provide a question."

        }), 400


    question = clean_text(
        data.get(
            "question",
            ""
        )
    )


    if not question:

        return jsonify({

            "success":
                False,

            "answer":
                "Please enter a question."

        }), 400


    # =====================================================
    # VERY IMPORTANT:
    #
    # COLLEGE INTENT IS CHECKED FIRST.
    #
    # This prevents:
    #
    # "Biotechnology special lab"
    #
    # from becoming:
    #
    # "Biotechnology faculty"
    # =====================================================

    college_intent = detect_college_intent(
        question
    )


    if college_intent in [

        "special_labs",
        "placement",
        "achievement"

    ]:

        result = answer_college_question(

            question,

            college_intent

        )

        if result is not None:

            return result


    # =====================================================
    # FACULTY QUESTION
    # =====================================================

    faculty_answer, faculty_source = (
        answer_faculty_question(
            question
        )
    )


    # -----------------------------------------------------
    # Determine whether faculty answer is meaningful.
    # -----------------------------------------------------

    faculty_related = (

        detect_department(
            question
        )

        or

        detect_designation(
            question
        )

        or

        len(
            find_faculty_by_name(
                question
            )
        ) > 0

    )


    if faculty_related:

        return jsonify({

            "success":
                True,

            "answer":
                faculty_answer,

            "source":
                "Official BIT Faculty Website",

            "source_url":
                faculty_source

        })


    # =====================================================
    # GENERAL COLLEGE QUESTION
    # =====================================================

    if college_intent == "general":

        # Search college data generically.

        records = find_college_records(

            question,

            "general"

        )


        if records:

            answer_parts = []


            for record in records[:5]:

                formatted = format_college_record(
                    record
                )

                if formatted:

                    answer_parts.append(
                        formatted
                    )


            return jsonify({

                "success":
                    True,

                "answer":
                    "According to the official BIT college data:\n\n"
                    +
                    "\n\n".join(
                        answer_parts
                    ),

                "source":
                    "Official BIT College Website",

                "source_url":
                    OFFICIAL_BIT_URL

            })


    # =====================================================
    # NO MATCH
    # =====================================================

    return jsonify({

        "success":
            True,

        "answer":
            "I'm CampusIQ, the official BIT information "
            "assistant.\n\n"

            "I can answer questions about:\n"

            "• Faculty and faculty details\n"
            "• Departments\n"
            "• HODs\n"
            "• Faculty designations\n"
            "• Special Labs\n"
            "• Placements\n"
            "• Achievements\n"
            "• College information\n\n"

            "Please ask a specific question related to "
            "Bannari Amman Institute of Technology.",

        "source":
            "CampusIQ — Official BIT Data",

        "source_url":
            OFFICIAL_BIT_URL

    })


# =========================================================
# FACULTY SEARCH API
# =========================================================

@app.route(
    "/api/faculty",
    methods=["GET"]
)
def faculty_search():

    query = clean_text(
        request.args.get(
            "q",
            ""
        )
    )


    if not query:

        return jsonify({

            "success":
                True,

            "count":
                len(FACULTY_DATA),

            "results":
                FACULTY_DATA

        })


    department = detect_department(
        query
    )

    designation = detect_designation(
        query
    )


    results = FACULTY_DATA


    # -----------------------------------------------------
    # Department filter
    # -----------------------------------------------------

    if department:

        results = [

            faculty

            for faculty
            in results

            if normalize(
                faculty.get(
                    "department"
                )
            )
            ==
            normalize(
                department
            )

        ]


    # -----------------------------------------------------
    # Designation filter
    # -----------------------------------------------------

    if designation:

        results = [

            faculty

            for faculty
            in results

            if designation_matches(
                faculty,
                designation
            )

        ]


    # -----------------------------------------------------
    # Name search
    # -----------------------------------------------------

    name_results = find_faculty_by_name(

        query,

        results

    )


    if name_results:

        results = name_results


    return jsonify({

        "success":
            True,

        "query":
            query,

        "count":
            len(results),

        "results":
            results

    })


# =========================================================
# COLLEGE SEARCH API
# =========================================================

@app.route(
    "/api/college",
    methods=["GET"]
)
def college_search():

    query = clean_text(
        request.args.get(
            "q",
            ""
        )
    )


    if not query:

        return jsonify({

            "success":
                True,

            "count":
                len(COLLEGE_DATA),

            "results":
                COLLEGE_DATA

        })


    intent = detect_college_intent(
        query
    )


    if intent is None:

        intent = "general"


    results = find_college_records(

        query,

        intent

    )


    return jsonify({

        "success":
            True,

        "query":
            query,

        "intent":
            intent,

        "count":
            len(results),

        "results":
            results

    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "success":
            True,

        "message":
            "CampusIQ backend is running.",

        "faculty_records":
            len(FACULTY_DATA),

        "college_records":
            len(COLLEGE_DATA),

        "official_sources": [

            OFFICIAL_BIT_URL,

            FACULTY_URL,

            SPECIAL_LABS_URL,

            PLACEMENT_URL,

            ACHIEVEMENT_URL

        ]

    })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print()

    print(
        "=" * 60
    )

    print(
        "                 CampusIQ Backend"
    )

    print(
        "=" * 60
    )

    print(
        f"Faculty profiles : {len(FACULTY_DATA)}"
    )

    print(
        f"College records  : {len(COLLEGE_DATA)}"
    )

    print()

    print(
        "Server:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()

    print(
        "Faculty API:"
    )

    print(
        "http://127.0.0.1:5000/api/faculty"
    )

    print()

    print(
        "College API:"
    )

    print(
        "http://127.0.0.1:5000/api/college"
    )

    print()

    print(
        "Ask API:"
    )

    print(
        "http://127.0.0.1:5000/api/ask"
    )

    print()

    print(
        "Health:"
    )

    print(
        "http://127.0.0.1:5000/api/health"
    )

    print()

    print(
        "Official BIT Sources:"
    )

    print(
        OFFICIAL_BIT_URL
    )

    print(
        FACULTY_URL
    )

    print(
        SPECIAL_LABS_URL
    )

    print(
        PLACEMENT_URL
    )

    print(
        ACHIEVEMENT_URL
    )

    print()

    print(
        "=" * 60
    )

    print()


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )