# Stage 4: candidate profile language defined with textX
import os

from textx import metamodel_from_file, TextXError

GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "candidate.tx")
METAMODEL = metamodel_from_file(GRAMMAR_PATH)


class ProfileError(Exception):
    pass


def quote(text):
    # strings in the DSL use double quotes
    return '"' + str(text).replace('"', "'") + '"'


def build_profile_text(data, skills, results):
    # data from stage 1, skills from stage 2, results from stage 3
    lines = ["candidate " + quote(data["name"]) + " {"]

    lines.append("    contact {")
    lines.append("        email: " + data["email"])
    if data.get("phone"):
        lines.append("        phone: " + data["phone"])
    if data.get("location"):
        lines.append("        location: " + quote(data["location"]))
    lines.append("    }")

    if data.get("summary"):
        lines.append("    summary: " + quote(data["summary"]))

    if data.get("experience"):
        lines.append("    experience {")
        for job in data["experience"]:
            lines.append("        job " + quote(job["role"]) + " at " + quote(job["company"])
                         + " years: " + str(job["years"]))
        lines.append("    }")

    if data.get("education"):
        lines.append("    education {")
        for record in data["education"]:
            lines.append("        degree " + quote(record["degree"]) + " at "
                         + quote(record["institution"]))
        lines.append("    }")

    lines.append("    skills {")
    if skills:
        lines.append("        " + " ".join(skills))
    lines.append("    }")

    lines.append("    evaluation {")
    for profile_name in results:
        lines.append("        profile " + profile_name + ": " + results[profile_name]["result"])
    lines.append("    }")

    lines.append("}")
    return "\n".join(lines) + "\n"


def check_rules(model):
    # rules that a context-free grammar cannot express
    if len(set(model.skills.names)) != len(model.skills.names):
        raise ProfileError("repeated skill in skills block")
    seen = []
    for result in model.evaluation.results:
        if result.profile in seen:
            raise ProfileError("profile evaluated twice: " + result.profile)
        seen.append(result.profile)


def parse_profile(text):
    # returns the model or raises ProfileError
    try:
        model = METAMODEL.model_from_str(text)
    except TextXError as error:
        raise ProfileError("line " + str(error.line) + ", col " + str(error.col)
                           + ": " + error.message)
    check_rules(model)
    return model


def validate_profile(text):
    # (True, "") if valid, (False, reason) if not
    try:
        parse_profile(text)
        return True, ""
    except ProfileError as error:
        return False, str(error)


def accepted_profiles(model):
    names = []
    for result in model.evaluation.results:
        if result.status == "ACCEPTED":
            names.append(result.profile)
    return names


if __name__ == "__main__":
    path = "tests/profiles/wednesday_addams.cand"
    with open(path, "r", encoding="utf-8") as file:
        model = parse_profile(file.read())
    print("valid profile:", model.name)
    print("skills:", model.skills.names)
    print("accepted:", accepted_profiles(model))
