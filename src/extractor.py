# Stage 1: extract resume information with regular expressions
import re

# --- Contact and personal data ---

# first line with two or more capitalized words
NAME_RE = re.compile(r"^[ \t]*([A-Z][a-zA-Z'-]+(?:[ \t]+[A-Z][a-zA-Z'-]+)+)[ \t]*$", re.MULTILINE)

# user@domain.ext
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# optional country code + 3-3-4 digits (space, dot or dash between groups)
PHONE_RE = re.compile(r"(?:\+\d{1,3}[ .-]?)?\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}")

# text after "Location:"
LOCATION_RE = re.compile(r"^Location:[ \t]*(.+)$", re.MULTILINE | re.IGNORECASE)

# "3 years of experience", "5+ years of experience"
YEARS_RE = re.compile(r"(\d+)\+?\s+years?\s+of\s+experience", re.IGNORECASE)

# --- Sections ---

# "- Role at Company (N years)"
EXPERIENCE_ITEM_RE = re.compile(
    r"^-[ \t]*(?P<role>.+?)[ \t]+at[ \t]+(?P<company>.+?)[ \t]*\((?P<years>\d+)[ \t]+years?\)[ \t]*$",
    re.MULTILINE | re.IGNORECASE)

# "- Degree, Institution"
EDUCATION_ITEM_RE = re.compile(r"^-[ \t]*(?P<degree>[^,\n]+),[ \t]*(?P<institution>.+)$", re.MULTILINE)

# --- Skills by category ---
# (?<![\w.]) and (?![\w]) work like word limits, so "JS" is not taken from "React.js"
SKILL_PATTERNS = {
    "languages": r"java\s?script|type\s?script|python|java|c\+\+|c#|php|sql|js|ts",
    "frameworks": r"react(?:\.?js)?|angular(?:\.?js)?|vue(?:\.?js)?|node(?:\.?js)?"
                  r"|express(?:\.?js)?|django|flask|spring\s?boot",
    "libraries": r"pandas|numpy|scikit[\s-]?learn|sklearn|tensor\s?flow|py\s?torch|keras",
    "databases": r"postgre(?:s|sql)|mysql|sqlite|mongo\s?db|redis|no\s?sql",
    "tools": r"github|gitlab|git|docker|kubernetes|k8s|linux|jenkins|aws|azure"
             r"|ci\s?/\s?cd|rest(?:ful)?\s?apis?|excel|power\s?bi|tableau",
    "concepts": r"machine[\s-]learning|deep[\s-]learning|predictive\s+models?|data\s+analysis",
}


def build_skill_regex(alternatives):
    # wraps the alternatives with the word limits
    return re.compile(r"(?<![\w.])(?:" + alternatives + r")(?![\w+#])", re.IGNORECASE)


SKILL_RES = {}
for category in SKILL_PATTERNS:
    SKILL_RES[category] = build_skill_regex(SKILL_PATTERNS[category])


def get_section(text, title):
    # returns the lines below "Title:" until a blank line
    pattern = r"^" + title + r":[ \t]*\n((?:[ \t]*\S.*\n?)+)"
    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


def first_match(regex, text):
    match = regex.search(text)
    if match is None:
        return None
    if match.groups():
        return match.group(1).strip()
    return match.group(0).strip()


def find_skills(text):
    # raw skills, written as in the resume, without repeated values
    skills = {}
    for category in SKILL_RES:
        found = []
        for match in SKILL_RES[category].finditer(text):
            word = match.group(0)
            if word not in found:
                found.append(word)
        skills[category] = found
    return skills


def extract(text):
    data = {}
    data["name"] = first_match(NAME_RE, text)
    data["email"] = first_match(EMAIL_RE, text)
    data["phone"] = first_match(PHONE_RE, text)
    data["location"] = first_match(LOCATION_RE, text)

    # summary lines joined in one sentence
    summary = get_section(text, "Summary")
    data["summary"] = " ".join(summary.split()) if summary else None

    years = first_match(YEARS_RE, text)
    data["years_experience"] = int(years) if years else 0

    data["experience"] = []
    for m in EXPERIENCE_ITEM_RE.finditer(get_section(text, "Experience")):
        data["experience"].append({
            "role": m.group("role"),
            "company": m.group("company"),
            "years": int(m.group("years")),
        })

    data["education"] = []
    for m in EDUCATION_ITEM_RE.finditer(get_section(text, "Education")):
        data["education"].append({
            "degree": m.group("degree").strip(),
            "institution": m.group("institution").strip(),
        })

    data["skills"] = find_skills(text)

    # flat list, this is the input for the transducers
    data["all_skills"] = []
    for category in data["skills"]:
        data["all_skills"].extend(data["skills"][category])
    return data


def extract_from_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return extract(file.read())


def save_extraction(data, path):
    # simple "key: value" text file
    with open(path, "w", encoding="utf-8") as file:
        for key in data:
            file.write(key + ": " + str(data[key]) + "\n")


if __name__ == "__main__":
    result = extract_from_file("tests/resumes/wednesday_addams.txt")
    for key in result:
        print(key, "->", result[key])
