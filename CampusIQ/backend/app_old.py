from flask import Flask, request, jsonify
from flask_cors import CORS

import json
import os
import re
import unicodedata
from difflib import SequenceMatcher


# =========================================================
# OPTIONAL SCRAPER
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

FACULTY_URL = "https://www.bitsathy.ac.in/departments/faculty/"


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "faculty_data.json"
)
COLLEGE_DATA_FILE = os.path.join(
    BASE_DIR,
    "college_data.json"
)

OFFICIAL_FACULTY_URL = (
    "https://www.bitsathy.ac.in/departments/faculty/"
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

    value = clean_text(
        value
    ).lower()

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
# LOAD FACULTY DATA
# =========================================================

def clean_faculty_data(data):

    cleaned = []

    seen = set()


    for item in data:

        if not isinstance(
            item,
            dict
        ):
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


        if not name or not profile_url:

            continue


        # Remove URL fragments
        # such as #artificial-intelligence-and-data-science

        clean_url = (
            profile_url
            .split("#")[0]
            .rstrip("/")
        )


        if clean_url in seen:

            continue


        seen.add(
            clean_url
        )


        cleaned.append({

            "name":
                name,

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


def load_faculty_data():

    print(
        "Loading BIT faculty data..."
    )


    # -----------------------------------------------------
    # FIRST: USE EXISTING JSON
    # -----------------------------------------------------

    if os.path.exists(
        DATA_FILE
    ):

        try:

            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )


            if (
                isinstance(data, list)
                and len(data) > 0
            ):

                cleaned = clean_faculty_data(
                    data
                )

                print(
                    f"Loaded {len(cleaned)} faculty profiles from faculty_data.json"
                )

                return cleaned


        except Exception as error:

            print(
                "Could not read faculty_data.json:",
                error
            )


    # -----------------------------------------------------
    # FALLBACK: SCRAPER
    # -----------------------------------------------------

    if fetch_faculty_data:

        try:

            print(
                "faculty_data.json not available."
            )

            print(
                "Connecting to BIT faculty website..."
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
                "Could not scrape faculty data:",
                error
            )


    return []


# =========================================================
# LOAD DATA
# =========================================================

FACULTY_DATA = load_faculty_data()
# =========================================================
# LOAD COLLEGE WEBSITE DATA
# =========================================================

def load_college_data():

    print(
        "Loading BIT college website data..."
    )

    if not os.path.exists(COLLEGE_DATA_FILE):

        print(
            "college_data.json not found."
        )

        return []

    try:

        with open(
            COLLEGE_DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        # -------------------------------------------------
        # Support either:
        # [
        #   {...},
        #   {...}
        # ]
        #
        # OR:
        #
        # {
        #   "pages": [...]
        # }
        # -------------------------------------------------

        if isinstance(data, dict):

            if isinstance(
                data.get("pages"),
                list
            ):

                data = data["pages"]

            elif isinstance(
                data.get("data"),
                list
            ):

                data = data["data"]

            else:

                data = [data]


        if not isinstance(data, list):

            print(
                "Invalid college_data.json format."
            )

            return []


        cleaned = []

        seen_urls = set()


        for item in data:

            if not isinstance(
                item,
                dict
            ):

                continue


            category = clean_text(
                item.get(
                    "category",
                    ""
                )
            )

            title = clean_text(
                item.get(
                    "title",
                    ""
                )
            )

            url = clean_text(
                item.get(
                    "url",
                    item.get(
                        "source_url",
                        item.get(
                            "link",
                            ""
                        )
                    )
                )
            )


            # Different scraper versions may
            # use different names for page text.

            content = clean_text(

                item.get(
                    "content",
                    item.get(
                        "text",
                        item.get(
                            "body",
                            item.get(
                                "description",
                                ""
                            )
                        )
                    )
                )

            )


            if not title and not content:

                continue


            # Remove URL fragment

            if url:

                url = (
                    url
                    .split("#")[0]
                    .rstrip("/")
                )


            # Avoid duplicate pages

            if url:

                if url in seen_urls:

                    continue

                seen_urls.add(url)


            cleaned.append({

                "category":
                    category,

                "title":
                    title,

                "url":
                    url,

                "content":
                    content

            })


        print(
            f"Loaded {len(cleaned)} BIT college website pages "
            f"from college_data.json"
        )


        return cleaned


    except Exception as error:

        print(
            "Could not read college_data.json:",
            error
        )

        return []


# =========================================================
# LOAD COLLEGE DATA
# =========================================================

COLLEGE_DATA = load_college_data()
# =========================================================
# COLLEGE WEBSITE SEARCH
# =========================================================

def search_college_data(
    question,
    limit=5
):

    q_norm = normalize(
        question
    )

    q_tokens = [

        token

        for token
        in q_norm.split()

        if len(token) >= 3

        and token not in INTENT_WORDS

    ]


    if not q_tokens:

        return []


    scored = []


    for page in COLLEGE_DATA:

        category = normalize(
            page.get(
                "category",
                ""
            )
        )

        title = normalize(
            page.get(
                "title",
                ""
            )
        )

        content = normalize(
            page.get(
                "content",
                ""
            )
        )


        combined = (
            category
            + " "
            + title
            + " "
            + content
        )


        score = 0


        # -------------------------------------------------
        # TOKEN MATCHING
        # -------------------------------------------------

        for token in q_tokens:

            if token in title:

                score += 12

            elif token in category:

                score += 10

            elif token in content:

                score += 3


        # -------------------------------------------------
        # EXACT PHRASE MATCH
        # -------------------------------------------------

        if q_norm in title:

            score += 40

        elif q_norm in category:

            score += 30

        elif q_norm in content:

            score += 20


        # -------------------------------------------------
        # CATEGORY BOOSTS
        # -------------------------------------------------

        if (
            "placement" in q_norm
            and
            "placement" in category
        ):

            score += 30


        if (
            "achievement" in q_norm
            and
            "achievement" in category
        ):

            score += 30


        if (
            "special lab" in q_norm
            or
            "special labs" in q_norm
            or
            "laboratory" in q_norm
            or
            "lab" in q_norm
        ):

            if "special lab" in category:

                score += 30


        if score > 0:

            scored.append(
                (
                    score,
                    page
                )
            )


    scored.sort(

        key=lambda item: (
            -item[0],
            item[1].get(
                "title",
                ""
            )
        )

    )


    return [

        item[1]

        for item
        in scored[:limit]

    ]
    # =========================================================
# FORMAT COLLEGE WEBSITE RESULT
# =========================================================

def format_college_result(
    page,
    max_content=1800
):

    category = page.get(
        "category",
        ""
    )

    title = page.get(
        "title",
        ""
    )

    url = page.get(
        "url",
        ""
    )

    content = clean_text(
        page.get(
            "content",
            ""
        )
    )


    # Prevent extremely large answers

    if len(content) > max_content:

        content = (
            content[:max_content]
            + "..."
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

    else:

        result += (
            "\nThe official BIT website has a page "
            "for this topic, but detailed page content "
            "is not available in the current dataset.\n"
        )


    if url:

        result += (
            f"\nOfficial Source: {url}"
        )


    return result


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
# DETECT DEPARTMENT
# =========================================================

def detect_department(question):

    q_norm = normalize(
        question
    )

    q_compact = compact(
        question
    )


    # -----------------------------------------------------
    # FIRST: CHECK ACTUAL DEPARTMENTS FROM DATA
    # -----------------------------------------------------

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


    for department in actual_departments:

        department_normalized = normalize(
            department
        )


        if (
            department_normalized
            in q_norm
        ):

            return department


        if (
            compact(department)
            in q_compact
        ):

            return department


    # -----------------------------------------------------
    # CHECK ALIASES
    # -----------------------------------------------------

    for canonical, aliases in DEPARTMENT_ALIASES.items():

        for alias in aliases:

            alias_normalized = normalize(
                alias
            )


            # Short aliases such as
            # IT / ECE / CSE / EEE
            # need word boundaries.

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

                # Return exact department
                # spelling from the JSON.

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


                return canonical.title()


    return None


# =========================================================
# DETECT DESIGNATION
# =========================================================

def detect_designation(question):

    q = normalize(
        question
    )


    # HEAD MUST BE CHECKED FIRST

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


    if (
        re.search(
            r"\bprofessor\b",
            q
        )
        or
        re.search(
            r"\bprof\b",
            q
        )
    ):

        return "professor"


    return None


# =========================================================
# CHECK HOD
# =========================================================

def is_head(faculty):

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

        # IMPORTANT:
        #
        # This means ONLY:
        # Professor
        #
        # NOT:
        # Assistant Professor
        # Associate Professor

        return designation == "professor"


    return False


# =========================================================
# EXTRACT NAME WORDS
# =========================================================

def tokenize_name_query(question):

    q = normalize(
        question
    )


    # Remove department phrases first.

    department_phrases = [

        "artificial intelligence and data science",

        "artificial intelligence data science",

        "artificial intelligence and machine learning",

        "artificial intelligence machine learning",

        "computer technology",

        "computer science and engineering",

        "electronics and communication engineering",

        "electronics and instrumentation engineering",

        "electrical and electronics engineering",

        "agricultural engineering",

        "information technology"

    ]


    for phrase in department_phrases:

        q = q.replace(
            phrase,
            " "
        )


    # Remove designation phrases.

    designation_phrases = [

        "assistant professor",

        "associate professor",

        "head of department",

        "department head"

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


        # -------------------------------------------------
        # EXACT FULL NAME
        # -------------------------------------------------

        if (
            name_normalized
            and
            name_normalized
            in q_norm
        ):

            score = 100


        # -------------------------------------------------
        # COMPACT FULL NAME
        # -------------------------------------------------

        if (
            name_compact
            and
            name_compact
            in q_compact
        ):

            score = max(
                score,
                98
            )


        # -------------------------------------------------
        # TOKEN MATCH
        # -------------------------------------------------

        overlap = sum(

            1

            for token
            in q_tokens

            if token
            in name_tokens

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


        # -------------------------------------------------
        # FUZZY MATCH
        # -------------------------------------------------

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
            item[1]["name"]
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

    if number is not None:

        prefix = (
            f"{number}. "
        )

    else:

        prefix = ""


    hod = (
        "Yes"
        if is_head(faculty)
        else
        "No"
    )


    return (

        f"{prefix}"
        f"{faculty['name']}\n"

        f"Designation: "
        f"{faculty.get('designation') or 'Not listed'}\n"

        f"Department: "
        f"{faculty.get('department') or 'Not listed'}\n"

        f"HOD: {hod}\n"

        f"Profile: "
        f"{faculty['profile_url']}"

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


    # =====================================================
    # CASE 1
    # DEPARTMENT + HOD
    # =====================================================

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

            answer = (

                f"The HOD of "
                f"{department} is:\n\n"

                +
                format_faculty(
                    matches[0]
                )

            )


            return (
                answer,
                "Official BIT Faculty Website"
            )


        return (

            f"I could not find an HOD listed "
            f"for {department} in the currently "
            f"loaded official BIT faculty data.",

            "Official BIT Faculty Website"

        )


    # =====================================================
    # CASE 2
    # DEPARTMENT + DESIGNATION
    # =====================================================

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

            if (
                designation
                ==
                "assistant professor"
            ):

                label = (
                    "Assistant Professors"
                )


            elif (
                designation
                ==
                "associate professor"
            ):

                label = (
                    "Associate Professors"
                )


            else:

                label = (
                    "Professors"
                )


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

                "Official BIT Faculty Website"

            )


        return (

            f"I could not find any "
            f"{designation} listed under "
            f"{department} in the currently "
            f"loaded official BIT faculty data.",

            "Official BIT Faculty Website"

        )


    # =====================================================
    # CASE 3
    # DEPARTMENT ONLY
    # =====================================================

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

                "Official BIT Faculty Website"

            )


    # =====================================================
    # CASE 4
    # FACULTY NAME
    # =====================================================

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

                "Official BIT Faculty Website"

            )


        # Show possible matches only
        # when the search is ambiguous.

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

            "Official BIT Faculty Website"

        )


    # =====================================================
    # CASE 5
    # HEAD WITHOUT DEPARTMENT
    # =====================================================

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

                f"Faculty matching the requested "
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

                "Official BIT Faculty Website"

            )


    # =====================================================
    # NOTHING FOUND
    # =====================================================

    return (

        "I could not identify a specific "
        "faculty member, department, or "
        "designation from your question.\n\n"

        "Try examples such as:\n"

        "• Who is the HOD of Artificial Intelligence and Data Science?\n"

        "• Who is the HOD of Artificial Intelligence and Machine Learning?\n"

        "• Faculty in Computer Technology\n"

        "• Assistant Professors in Computer Technology\n"

        "• Tell me about Dr Gomathi R\n"

        "• What is the designation of Dr Gomathi R?",

        "CampusIQ — Official BIT Faculty Dataset"

    )


# =========================================================
# HOME API
# =========================================================

@app.route("/api/ask", methods=["POST"])
def ask_question():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "answer": "Please provide a question."
        }), 400

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "success": False,
            "answer": "Please enter a question."
        }), 400

    q = question.lower().strip()

    # =========================================================
    # COLLEGE KEYWORDS
    # =========================================================

    college_keywords = [
        "college",
        "campus",
        "bitsathy",
        "bannari",
        "faculty",
        "professor",
        "assistant professor",
        "associate professor",
        "head",
        "hod",
        "head of department",
        "department",
        "academic",
        "attendance",
        "exam",
        "examination",
        "fee",
        "fees",
        "hostel",
        "placement",
        "library",
        "course",
        "courses",
        "admission",
        "admissions",
        "student",
        "students",
        "staff",
        "timetable",
        "regulation",
        "regulations",
        "scholarship",
        "transport",
        "bus",
        "canteen",
        "laboratory",
        "laboratory",
        "lab",
        "designation",
        "faculty member",
        "teaching staff"
    ]

    # =========================================================
    # FIND FACULTY MATCHES BY NAME
    #
    # IMPORTANT:
    # This happens BEFORE checking whether the question
    # contains the word "faculty".
    #
    # Therefore:
    # "What is the designation of Dr Uvaraja V C?"
    # will correctly identify Dr Uvaraja V C.
    # =========================================================

    faculty_matches = []

    for faculty in FACULTY_DATA:

        name = faculty.get("name", "").strip()

        if not name:
            continue

        name_lower = name.lower()

        # Exact complete name
        if name_lower in q:

            faculty_matches.append(faculty)

            continue

        # Remove titles for flexible searching
        clean_name = name_lower

        for title in [
            "dr.",
            "dr ",
            "prof.",
            "prof ",
            "mr.",
            "mr ",
            "mrs.",
            "mrs ",
            "ms.",
            "ms "
        ]:

            clean_name = clean_name.replace(
                title,
                ""
            ).strip()

        if clean_name and clean_name in q:

            faculty_matches.append(faculty)

            continue

        # Word-based matching
        name_words = [
            word.strip(".,")
            for word in clean_name.split()
            if len(word.strip(".,")) >= 3
        ]

        if len(name_words) >= 2:

            matched_words = sum(
                1
                for word in name_words
                if word in q
            )

            # Require at least two meaningful name words
            if matched_words >= 2:

                faculty_matches.append(faculty)

    # =========================================================
    # REMOVE DUPLICATES
    # =========================================================

    unique_faculty = []

    seen_urls = set()

    for faculty in faculty_matches:

        url = faculty.get(
            "profile_url",
            ""
        )

        if url not in seen_urls:

            seen_urls.add(url)

            unique_faculty.append(
                faculty
            )

    faculty_matches = unique_faculty

    # =========================================================
    # FACULTY NAME QUESTION
    #
    # If a faculty member's name was found,
    # always answer from the official scraped data.
    # =========================================================

    if faculty_matches:

        # If multiple faculty members match,
        # show them clearly.
        if len(faculty_matches) > 1:

            answer_parts = []

            for index, faculty in enumerate(
                faculty_matches[:10],
                start=1
            ):

                name = faculty.get(
                    "name",
                    "Unknown"
                )

                designation = faculty.get(
                    "designation",
                    "Not available"
                )

                department = faculty.get(
                    "department",
                    "Not available"
                )

                is_hod = faculty.get(
                    "is_hod",
                    False
                )

                profile_url = faculty.get(
                    "profile_url",
                    ""
                )

                answer_parts.append(

                    f"{index}. {name}\n"
                    f"Designation: {designation}\n"
                    f"Department: {department}\n"
                    f"HOD: {'Yes' if is_hod else 'No'}\n"
                    f"Profile: {profile_url}"

                )

            return jsonify({

                "success": True,

                "answer":
                    "I found the following matching faculty members "
                    "from the official BIT faculty data:\n\n"
                    +
                    "\n\n".join(answer_parts),

                "source":
                    "Official BIT Faculty Website",

                "source_url":
                    FACULTY_URL

            })

        # =====================================================
        # EXACT / SINGLE FACULTY
        # =====================================================

        faculty = faculty_matches[0]

        name = faculty.get(
            "name",
            "Unknown"
        )

        designation = faculty.get(
            "designation",
            ""
        )

        department = faculty.get(
            "department",
            ""
        )

        is_hod = faculty.get(
            "is_hod",
            False
        )

        profile_url = faculty.get(
            "profile_url",
            ""
        )

        # =====================================================
        # DESIGNATION QUESTION
        # =====================================================

        if (
            "designation" in q
            or "position" in q
            or "role" in q
            or "post" in q
        ):

            answer = (
                f"The designation of {name} is "
                f"{designation}."
            )

        # =====================================================
        # DEPARTMENT QUESTION
        # =====================================================

        elif (
            "which department" in q
            or "what department" in q
            or "department does" in q
            or "department of" in q
            or "belongs to which department" in q
        ):

            answer = (
                f"{name} belongs to the "
                f"{department} department."
            )

        # =====================================================
        # HOD QUESTION
        # =====================================================

        elif (
            "hod" in q
            or "head of department" in q
            or "head of the department" in q
            or "is he the head" in q
            or "is she the head" in q
            or "is an hod" in q
            or "is a hod" in q
        ):

            if is_hod:

                answer = (
                    f"Yes. {name} is the Head of the "
                    f"{department} department."
                )

            else:

                answer = (
                    f"No. {name} is not listed as the "
                    f"Head of the {department} department "
                    f"in the current official BIT faculty data."
                )

        # =====================================================
        # PROFILE / DETAILS QUESTION
        # =====================================================

        else:

            answer = (

                f"Here are the official faculty details "
                f"for {name}:\n\n"

                f"Name: {name}\n"
                f"Designation: {designation}\n"
                f"Department: {department}\n"
                f"HOD: {'Yes' if is_hod else 'No'}\n"
                f"Profile: {profile_url}"

            )

        return jsonify({

            "success": True,

            "answer": answer,

            "source":
                "Official BIT Faculty Website",

            "source_url":
                profile_url

        })

    # =========================================================
    # HOD SEARCH
    # =========================================================

    hod_words = [
        "hod",
        "head of department",
        "head of the department",
        "who is the head",
        "who's the head"
    ]

    is_hod_question = any(
        word in q
        for word in hod_words
    )

    if is_hod_question:

        # -----------------------------------------------------
        # Find department mentioned in question
        # -----------------------------------------------------

        department_matches = []

        for faculty in FACULTY_DATA:

            department = faculty.get(
                "department",
                ""
            ).strip()

            if not department:
                continue

            if department.lower() in q:

                department_matches.append(
                    department
                )

        # Remove duplicates while preserving order
        department_matches = list(
            dict.fromkeys(
                department_matches
            )
        )

        # -----------------------------------------------------
        # If department found, find its HOD
        # -----------------------------------------------------

        if department_matches:

            department = department_matches[0]

            hods = [

                faculty
                for faculty in FACULTY_DATA

                if faculty.get(
                    "department",
                    ""
                ).lower() == department.lower()

                and faculty.get(
                    "is_hod",
                    False
                )

            ]

            if hods:

                answer_parts = []

                for hod in hods:

                    answer_parts.append(

                        f"{hod.get('name', 'Unknown')}\n"
                        f"Designation: "
                        f"{hod.get('designation', 'Not available')}\n"
                        f"Department: {department}\n"
                        f"Profile: "
                        f"{hod.get('profile_url', '')}"

                    )

                return jsonify({

                    "success": True,

                    "answer":
                        f"The HOD of {department} is:\n\n"
                        +
                        "\n\n".join(
                            answer_parts
                        ),

                    "source":
                        "Official BIT Faculty Website",

                    "source_url":
                        FACULTY_URL

                })

        # -----------------------------------------------------
        # If no specific department, list HODs
        # -----------------------------------------------------

        all_hods = [

            faculty
            for faculty in FACULTY_DATA

            if faculty.get(
                "is_hod",
                False
            )

        ]

        if all_hods:

            answer_parts = []

            for index, hod in enumerate(
                all_hods[:20],
                start=1
            ):

                answer_parts.append(

                    f"{index}. {hod.get('name', 'Unknown')}\n"
                    f"Designation: "
                    f"{hod.get('designation', 'Not available')}\n"
                    f"Department: "
                    f"{hod.get('department', 'Not available')}\n"
                    f"Profile: "
                    f"{hod.get('profile_url', '')}"

                )

            return jsonify({

                "success": True,

                "answer":
                    "Here are the Heads of Departments "
                    "found in the official BIT faculty data:\n\n"
                    +
                    "\n\n".join(answer_parts),

                "source":
                    "Official BIT Faculty Website",

                "source_url":
                    FACULTY_URL

            })

    # =========================================================
    # DEPARTMENT SEARCH
    # =========================================================

    matched_department = None

    # Prefer longest department name first
    # to avoid partial matching problems.

    departments = sorted(

        set(
            faculty.get(
                "department",
                ""
            ).strip()

            for faculty in FACULTY_DATA

            if faculty.get(
                "department",
                ""
            ).strip()
        ),

        key=len,

        reverse=True
    )

    for department in departments:

        if department.lower() in q:

            matched_department = department

            break

    if matched_department:

        department_faculty = [

            faculty

            for faculty in FACULTY_DATA

            if faculty.get(
                "department",
                ""
            ).lower()
            ==
            matched_department.lower()

        ]

        # -----------------------------------------------------
        # Department faculty result
        # -----------------------------------------------------

        if department_faculty:

            answer_parts = []

            for index, faculty in enumerate(
                department_faculty,
                start=1
            ):

                answer_parts.append(

                    f"{index}. {faculty.get('name', 'Unknown')}\n"
                    f"Designation: "
                    f"{faculty.get('designation', 'Not available')}\n"
                    f"HOD: "
                    f"{'Yes' if faculty.get('is_hod', False) else 'No'}\n"
                    f"Profile: "
                    f"{faculty.get('profile_url', '')}"

                )

            return jsonify({

                "success": True,

                "answer":
                    f"Faculty members in "
                    f"{matched_department}:\n\n"
                    +
                    "\n\n".join(answer_parts),

                "source":
                    "Official BIT Faculty Website",

                "source_url":
                    FACULTY_URL

            })

    # =========================================================
    # DESIGNATION SEARCH
    # =========================================================

    designation_terms = [
        "professor",
        "associate professor",
        "assistant professor",
        "head",
        "designation"
    ]

    if any(
        term in q
        for term in designation_terms
    ):

        # Search faculty whose designation occurs
        # in the question.

        designation_matches = []

        for faculty in FACULTY_DATA:

            designation = faculty.get(
                "designation",
                ""
            ).lower()

            if not designation:
                continue

            if designation in q:

                designation_matches.append(
                    faculty
                )

        if designation_matches:

            answer_parts = []

            for index, faculty in enumerate(
                designation_matches[:30],
                start=1
            ):

                answer_parts.append(

                    f"{index}. {faculty.get('name', 'Unknown')}\n"
                    f"Designation: "
                    f"{faculty.get('designation', 'Not available')}\n"
                    f"Department: "
                    f"{faculty.get('department', 'Not available')}\n"
                    f"HOD: "
                    f"{'Yes' if faculty.get('is_hod', False) else 'No'}\n"
                    f"Profile: "
                    f"{faculty.get('profile_url', '')}"

                )

            return jsonify({

                "success": True,

                "answer":
                    "Faculty matching the requested designation:\n\n"
                    +
                    "\n\n".join(answer_parts),

                "source":
                    "Official BIT Faculty Website",

                "source_url":
                    FACULTY_URL

            })

    # =========================================================
    # COLLEGE QUESTION CHECK
    # =========================================================

    is_college_question = any(
        keyword in q
        for keyword in college_keywords
    )

    if not is_college_question:

        return jsonify({

            "success": True,

            "answer":
                "I'm CampusIQ, your college information assistant. "
                "I can answer questions related to Bannari Amman "
                "Institute of Technology, including faculty, "
                "departments, academics, examinations, fees, "
                "hostel, placements and other campus information.",

            "source":
                "CampusIQ — College Information Assistant"

        })

    # =========================================================
    # GENERAL COLLEGE QUESTION
    # =========================================================

    return jsonify({

        "success": True,

        "answer":
            "Your question is related to Bannari Amman Institute "
            "of Technology, but the required official information "
            "is not currently available in the connected CampusIQ "
            "knowledge base.",

        "source":
            "CampusIQ — Official BIT Faculty Dataset",

        "source_url":
            FACULTY_URL

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


    # Department filter

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


    # Designation filter

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


    # Name search

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
# CAMPUSIQ ASK API
# =========================================================

# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print()

    print(
        "=" * 55
    )

    print(
        "        CampusIQ Backend"
    )

    print(
        "=" * 55
    )

    print(
        f"Loaded faculty profiles: "
        f"{len(FACULTY_DATA)}"
    )

    print(
        "Server: http://127.0.0.1:5000"
    )

    print(
        "Faculty API: "
        "http://127.0.0.1:5000/api/faculty"
    )

    print(
        "Ask API: "
        "http://127.0.0.1:5000/api/ask"
    )

    print(
        "=" * 55
    )

    print()


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )