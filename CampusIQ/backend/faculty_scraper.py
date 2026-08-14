import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


# =========================================================
# CONFIGURATION
# =========================================================

FACULTY_URL = "https://www.bitsathy.ac.in/departments/faculty/"

DATA_FILE = "faculty_data.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# =========================================================
# FETCH FACULTY PAGE
# =========================================================

def fetch_faculty_page():

    print("Connecting to BIT faculty website...")

    response = requests.get(
        FACULTY_URL,
        timeout=30,
        headers=HEADERS
    )

    response.raise_for_status()

    return response.text


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# EXTRACT DESIGNATION
# =========================================================

def extract_designation(text):

    text = text.strip()

    # IMPORTANT:
    # Longer designations must come first.

    designations = [

        "Professor & Head",

        "Professor and Head",

        "Associate Professor & Head",

        "Associate Professor and Head",

        "Assistant Professor & Head",

        "Assistant Professor and Head",

        "Assistant Professor Level III",

        "Assistant Professor Level II",

        "Assistant Professor Level I",

        "Associate Professor",

        "Assistant Professor",

        "Professor",

        "Head"
    ]

    for designation in designations:

        if text.lower().endswith(
            designation.lower()
        ):

            return designation

    return ""


# =========================================================
# EXTRACT NAME
# =========================================================

def extract_name(
    text,
    designation
):

    text = text.strip()

    if designation:

        name = text[
            :len(text) - len(designation)
        ].strip()

    else:

        name = text

    return name


# =========================================================
# CHECK FACULTY URL
# =========================================================

def is_faculty_profile_url(url):

    parsed = urlparse(url)

    path = parsed.path.rstrip("/")

    if not path.startswith(
        "/departments/faculty/"
    ):

        return False

    profile_slug = path.split(
        "/departments/faculty/",
        1
    )[1].strip("/")

    if not profile_slug:

        return False

    return True


# =========================================================
# DEPARTMENT FROM URL
# =========================================================

def extract_department_from_url(
    full_url
):

    parsed = urlparse(full_url)

    # Example:
    #
    # https://www.bitsathy.ac.in/
    # departments/faculty/gomathi-r/
    # #artificial-intelligence-and-data-science

    department_slug = (
        parsed.fragment
        .strip()
        .lower()
    )

    if not department_slug:

        return "Unknown Department"


    department_map = {

        "agricultural-engineering":
            "Agricultural Engineering",

        "artificial-intelligence-and-data-science":
            "Artificial Intelligence and Data Science",

        "artificial-intelligence-and-machine-learning":
            "Artificial Intelligence and Machine Learning",

        "biomedical-engineering":
            "Biomedical Engineering",

        "biotechnology":
            "Biotechnology",

        "civil-engineering":
            "Civil Engineering",

        "computer-science-and-business-systems":
            "Computer Science and Business Systems",

        "computer-science-and-design":
            "Computer Science and Design",

        "computer-science-and-engineering":
            "Computer Science and Engineering",

        "computer-technology":
            "Computer Technology",

        "electrical-and-electronics-engineering":
            "Electrical and Electronics Engineering",

        "electronics-and-communication-engineering":
            "Electronics and Communication Engineering",

        "electronics-and-instrumentation-engineering":
            "Electronics and Instrumentation Engineering",

        "fashion-technology":
            "Fashion Technology",

        "food-technology":
            "Food Technology",

        "humanities":
            "Humanities",

        "information-science-and-engineering":
            "Information Science and Engineering",

        "information-technology":
            "Information Technology",

        "mechanical-engineering":
            "Mechanical Engineering",

        "mechatronics-engineering":
            "Mechatronics Engineering",

        "textile-technology":
            "Textile Technology"
    }


    if department_slug in department_map:

        return department_map[
            department_slug
        ]


    # Fallback if a new department
    # appears on the BIT website.

    return department_slug.replace(
        "-",
        " "
    ).title()


# =========================================================
# CHECK HOD
# =========================================================

def check_is_hod(
    designation,
    text
):

    designation_normalized = (
        normalize_text(designation)
    )

    text_normalized = (
        normalize_text(text)
    )

    if "professor & head" in designation_normalized:
        return True

    if "professor and head" in designation_normalized:
        return True

    if "associate professor & head" in designation_normalized:
        return True

    if "associate professor and head" in designation_normalized:
        return True

    if "assistant professor & head" in designation_normalized:
        return True

    if "assistant professor and head" in designation_normalized:
        return True

    if designation_normalized == "head":
        return True

    if "hod" in text_normalized:
        return True

    return False


# =========================================================
# EXTRACT FACULTY DATA
# =========================================================

def extract_faculty_data(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    faculty = []

    # -----------------------------------------------------
    # Find every link on the faculty page
    # -----------------------------------------------------

    links = soup.find_all(
        "a",
        href=True
    )

    for link in links:

        # =================================================
        # GET LINK INFORMATION
        # =================================================

        href = link.get(
            "href",
            ""
        ).strip()

        text = link.get_text(
            " ",
            strip=True
        )


        # =================================================
        # IGNORE EMPTY LINKS
        # =================================================

        if not href or not text:

            continue


        # =================================================
        # CREATE FULL URL
        # =================================================

        full_url = urljoin(
            FACULTY_URL,
            href
        )


        # =================================================
        # CHECK WHETHER THIS IS A FACULTY PROFILE
        # =================================================

        if not is_faculty_profile_url(
            full_url
        ):

            continue


        # =================================================
        # EXTRACT DEPARTMENT
        # =================================================

        department = (
            extract_department_from_url(
                full_url
            )
        )


        # =================================================
        # EXTRACT DESIGNATION
        # =================================================

        designation = (
            extract_designation(
                text
            )
        )


        # =================================================
        # EXTRACT NAME
        # =================================================

        name = extract_name(
            text,
            designation
        )


        # =================================================
        # CHECK HOD
        # =================================================

        is_hod = check_is_hod(
            designation,
            text
        )


        # =================================================
        # CREATE FACULTY RECORD
        # =================================================

        faculty.append({

            "name": name,

            "designation": designation,

            "department": department,

            "is_hod": is_hod,

            "profile_url": full_url

        })


    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    unique_faculty = []

    seen_urls = set()

    for person in faculty:

        url = person.get(
            "profile_url",
            ""
        )

        if not url:

            continue

        if url in seen_urls:

            continue

        seen_urls.add(url)

        unique_faculty.append(
            person
        )


    return unique_faculty


# =========================================================
# SAVE FACULTY DATA
# =========================================================

def save_faculty_data(
    data
):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Saved {len(data)} faculty profiles "
        f"to {DATA_FILE}"
    )


# =========================================================
# MAIN FETCH FUNCTION
# =========================================================

def fetch_faculty_data():

    html = fetch_faculty_page()

    data = extract_faculty_data(
        html
    )

    save_faculty_data(
        data
    )

    return data


# =========================================================
# TEST / RUN SCRAPER
# =========================================================

if __name__ == "__main__":

    print()

    print(
        "=" * 60
    )

    print(
        "       CampusIQ Faculty Scraper"
    )

    print(
        "=" * 60
    )

    print()

    try:

        data = fetch_faculty_data()

        print()

        print(
            f"Found {len(data)} faculty profiles."
        )

        print()

        # -------------------------------------------------
        # Show first 20 profiles
        # -------------------------------------------------

        for person in data[:20]:

            print(
                f"Name        : "
                f"{person['name']}"
            )

            print(
                f"Designation : "
                f"{person['designation']}"
            )

            print(
                f"Department  : "
                f"{person['department']}"
            )

            print(
                f"HOD         : "
                f"{person['is_hod']}"
            )

            print(
                f"Profile     : "
                f"{person['profile_url']}"
            )

            print(
                "-" * 60
            )


        # -------------------------------------------------
        # Show AI&DS HOD separately
        # -------------------------------------------------

        print()

        print(
            "=" * 60
        )

        print(
            "AI&DS HOD CHECK"
        )

        print(
            "=" * 60
        )

        for person in data:

            department = normalize_text(
                person["department"]
            )

            if (
                department
                ==
                "artificial intelligence and data science"
                and
                person["is_hod"]
            ):

                print()

                print(
                    "HOD FOUND"
                )

                print(
                    f"Name        : "
                    f"{person['name']}"
                )

                print(
                    f"Designation : "
                    f"{person['designation']}"
                )

                print(
                    f"Department  : "
                    f"{person['department']}"
                )

                print(
                    f"Profile     : "
                    f"{person['profile_url']}"
                )

                print()

                break


    except Exception as error:

        print()

        print(
            "ERROR:"
        )

        print(
            error
        )