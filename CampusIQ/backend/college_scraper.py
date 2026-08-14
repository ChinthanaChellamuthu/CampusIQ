import json
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# =========================================================
# CAMPUSIQ COLLEGE WEBSITE SCRAPER
# Official BIT Website
# =========================================================

BASE_URL = "https://www.bitsathy.ac.in/"

START_URLS = [
    "https://www.bitsathy.ac.in/",
    "https://www.bitsathy.ac.in/special-labs/",
    "https://www.bitsathy.ac.in/placement/",
    "https://www.bitsathy.ac.in/achievement/",
]

OUTPUT_FILE = "college_data.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

TIMEOUT = 20

MAX_PAGES = 150


# =========================================================
# SESSION
# =========================================================

session = requests.Session()
session.headers.update(HEADERS)


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(text):

    if not text:
        return ""

    # Decode HTML whitespace
    text = text.replace("\xa0", " ")

    # Remove repeated whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# GET CATEGORY FROM URL
# =========================================================

def get_category(url):

    path = urlparse(url).path.lower()

    if path.startswith("/special-labs"):
        return "Special Labs"

    if path.startswith("/placement"):
        return "Placement"

    if (
        path.startswith("/achievement")
        or path.startswith("/achievements")
    ):
        return "Achievements"

    if path == "/" or path == "":
        return "General BIT Information"

    return "BIT Website"


# =========================================================
# CHECK WHETHER URL BELONGS TO BIT
# =========================================================

def is_valid_bit_url(url):

    parsed = urlparse(url)

    if parsed.netloc not in [
        "www.bitsathy.ac.in",
        "bitsathy.ac.in"
    ]:
        return False

    return True


# =========================================================
# CHECK WHETHER WE SHOULD CRAWL URL
# =========================================================

def should_crawl(url):

    if not is_valid_bit_url(url):
        return False

    path = urlparse(url).path.lower()

    allowed_paths = [
        "/",
        "/special-labs",
        "/special-labs/",
        "/placement",
        "/placement/",
        "/achievement",
        "/achievement/",
        "/achievements",
        "/achievements/",
    ]

    # Direct allowed pages
    if path in allowed_paths:
        return True

    # Special lab pages
    if path.startswith("/special-labs/"):
        return True

    # Achievement pages
    if path.startswith("/achievement/"):
        return True

    if path.startswith("/achievements/"):
        return True

    # Placement pages
    if path.startswith("/placement/"):
        return True

    return False


# =========================================================
# NORMALIZE URL
# =========================================================

def normalize_url(url):

    parsed = urlparse(url)

    # Remove fragments
    normalized = (
        parsed.scheme
        + "://"
        + parsed.netloc
        + parsed.path
    )

    # Remove trailing slash except homepage
    if normalized.endswith("/") and parsed.path != "/":
        normalized = normalized.rstrip("/")

    return normalized


# =========================================================
# FETCH PAGE
# =========================================================

def fetch_page(url):

    try:

        print("Fetching:", url)

        response = session.get(
            url,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.text

    except Exception as error:

        print(
            "Failed:",
            url,
            "->",
            error
        )

        return None


# =========================================================
# EXTRACT PAGE
# =========================================================

def extract_page_data(html, url):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # Remove unwanted elements
    for element in soup([
        "script",
        "style",
        "noscript",
        "svg"
    ]):

        element.decompose()

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    title = ""

    if soup.title:

        title = clean_text(
            soup.title.get_text(" ")
        )

    # -----------------------------------------------------
    # MAIN CONTENT
    # -----------------------------------------------------

    main = (
        soup.find("main")
        or soup.find(
            "article"
        )
        or soup.body
    )

    if not main:

        return None

    text = clean_text(
        main.get_text(
            " ",
            strip=True
        )
    )

    # Avoid useless tiny pages
    if len(text) < 80:

        return None

    # Limit extremely large pages
    if len(text) > 15000:

        text = text[:15000]

    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    category = get_category(url)

    # -----------------------------------------------------
    # PAGE DATA
    # -----------------------------------------------------

    return {

        "title": title,

        "category": category,

        "url": url,

        "content": text

    }


# =========================================================
# EXTRACT LINKS
# =========================================================

def extract_links(html, current_url):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    links = set()

    for anchor in soup.find_all(
        "a",
        href=True
    ):

        href = anchor.get(
            "href"
        ).strip()

        if not href:
            continue

        # Ignore special links
        if href.startswith(
            (
                "#",
                "mailto:",
                "tel:",
                "javascript:"
            )
        ):
            continue

        full_url = urljoin(
            current_url,
            href
        )

        full_url = normalize_url(
            full_url
        )

        if should_crawl(full_url):

            links.add(full_url)

    return links


# =========================================================
# SCRAPE WEBSITE
# =========================================================

def scrape_college_website():

    print()
    print("=" * 60)
    print("       CampusIQ College Website Scraper")
    print("=" * 60)
    print()

    queue = []

    for url in START_URLS:

        queue.append(
            normalize_url(url)
        )

    visited = set()

    pages = []

    while queue and len(visited) < MAX_PAGES:

        url = queue.pop(0)

        if url in visited:
            continue

        visited.add(url)

        html = fetch_page(url)

        if not html:
            continue

        # -------------------------------------------------
        # Extract current page
        # -------------------------------------------------

        page_data = extract_page_data(
            html,
            url
        )

        if page_data:

            pages.append(
                page_data
            )

            print(
                "Saved:",
                page_data["category"],
                "|",
                page_data["title"]
            )

        # -------------------------------------------------
        # Find additional pages
        # -------------------------------------------------

        links = extract_links(
            html,
            url
        )

        for link in links:

            if link not in visited:

                if link not in queue:

                    queue.append(link)

        time.sleep(0.2)

    # =====================================================
    # SAVE JSON
    # =====================================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            pages,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print(
        f"Saved {len(pages)} college pages "
        f"to {OUTPUT_FILE}"
    )
    print("=" * 60)

    return pages


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    data = scrape_college_website()

    print()
    print(
        f"Found {len(data)} useful BIT website pages."
    )

    print()

    for page in data[:20]:

        print(
            "Category    :",
            page["category"]
        )

        print(
            "Title       :",
            page["title"]
        )

        print(
            "URL         :",
            page["url"]
        )

        print("-" * 60)