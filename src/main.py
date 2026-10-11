# ResumeLens: runs the whole pipeline from the console
import os
import re

from src.extractor import extract_from_file
from src.normalizer import normalize
from src.classifier import classify, accepted_profiles
from src.profile_language import build_profile_text, parse_profile, ProfileError
from src.visualizer import to_html, to_markdown, save

OUTPUT_DIR = "output"
SAMPLES_DIR = "tests/resumes"


def file_name(candidate_name):
    # "Wednesday Addams" -> "wednesday_addams"
    name = re.sub(r"[^a-z0-9]+", "_", candidate_name.lower()).strip("_")
    return name if name else "candidate"


def write_outputs(model, profile_text):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base = os.path.join(OUTPUT_DIR, file_name(model.name))
    save(profile_text, base + ".cand")
    save(to_html(model), base + ".html")
    save(to_markdown(model), base + ".md")
    return base


def process_resume(path, verbose=True):
    # stage 1
    data = extract_from_file(path)
    # stage 2
    skills, unknown = normalize(data["all_skills"])
    # stage 3
    results = classify(skills)
    # stage 4
    profile_text = build_profile_text(data, skills, results)
    model = parse_profile(profile_text)
    # stage 5
    base = write_outputs(model, profile_text)

    if verbose:
        print("\n[1] Extraction")
        print("    name:", data["name"], "| email:", data["email"])
        print("    raw skills:", ", ".join(data["all_skills"]))
        print("[2] Normalization")
        print("    canonical skills:", ", ".join(skills))
        if unknown:
            print("    not recognized:", ", ".join(unknown))
        print("[3] Classification")
        for name in results:
            print("    " + name.ljust(27), results[name]["result"], results[name]["sequence"])
        print("[4] Profile language: valid")
        print("[5] Output: " + base + ".html / .md / .cand")
    return accepted_profiles(results)


def process_samples():
    for name in sorted(os.listdir(SAMPLES_DIR)):
        if name.endswith(".txt"):
            path = os.path.join(SAMPLES_DIR, name)
            try:
                accepted = process_resume(path, verbose=False)
                print(name.ljust(28), "->", ", ".join(accepted) if accepted else "no profile")
            except ProfileError as error:
                print(name.ljust(28), "-> invalid profile:", error)


def validate_file(path):
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()
    try:
        model = parse_profile(text)
    except ProfileError as error:
        print("REJECTED:", error)
        return
    base = write_outputs(model, text)
    print("VALID profile. Output: " + base + ".html / .md")


def menu():
    while True:
        print("\n===== ResumeLens =====")
        print("1. Process a resume (.txt)")
        print("2. Process all sample resumes")
        print("3. Validate a candidate profile (.cand)")
        print("4. Exit")
        option = input("Option: ").strip()
        try:
            if option == "1":
                path = input("Resume path (e.g. tests/resumes/wednesday_addams.txt): ").strip()
                process_resume(path)
            elif option == "2":
                process_samples()
            elif option == "3":
                path = input("Profile path (e.g. tests/profiles/invalid_email.cand): ").strip()
                validate_file(path)
            elif option == "4":
                print("Bye.")
                break
            else:
                print("Invalid option.")
        except FileNotFoundError:
            print("File not found.")
        except ProfileError as error:
            print("The generated profile is not valid:", error)


if __name__ == "__main__":
    menu()
