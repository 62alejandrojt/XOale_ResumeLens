# Stage 3: classify the normalized skills with finite automata (pyformlang)
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    EpsilonNFA,
    Epsilon,
)

from src.profiles import PROFILES
from src.normalizer import sort_for_profile


def group(profile_name, group_name):
    # skills of one group of a profile
    for name, skills in PROFILES[profile_name]:
        if name == group_name:
            return skills
    return []


def add_group(automaton, origin, symbols, target):
    # one transition for each symbol of the group
    for symbol in symbols:
        automaton.add_transition(origin, symbol, target)


# --- Full Stack Developer: DFA ---
# Language+ Frontend+ Backend+ Database+ (REST_API)? GIT
def build_full_stack():
    p = "FULL_STACK_DEVELOPER"
    dfa = DeterministicFiniteAutomaton()
    dfa.add_start_state("q0")
    dfa.add_final_state("q6")
    add_group(dfa, "q0", group(p, "Language"), "q1")
    add_group(dfa, "q1", group(p, "Language"), "q1")
    add_group(dfa, "q1", group(p, "Frontend"), "q2")
    add_group(dfa, "q2", group(p, "Frontend"), "q2")
    add_group(dfa, "q2", group(p, "Backend"), "q3")
    add_group(dfa, "q3", group(p, "Backend"), "q3")
    add_group(dfa, "q3", group(p, "Database"), "q4")
    add_group(dfa, "q4", group(p, "Database"), "q4")
    dfa.add_transition("q4", "REST_API", "q5")
    dfa.add_transition("q4", "GIT", "q6")
    dfa.add_transition("q5", "GIT", "q6")
    return dfa


# --- Machine Learning Engineer: NFA ---
# PYTHON DataLib+ MLLib+ Concept* Database* GIT
# the automaton guesses which library is the last one of each group
def build_ml_engineer():
    p = "MACHINE_LEARNING_ENGINEER"
    nfa = NondeterministicFiniteAutomaton()
    nfa.add_start_state("q0")
    nfa.add_final_state("q5")
    nfa.add_transition("q0", "PYTHON", "q1")
    add_group(nfa, "q1", group(p, "Data libraries"), "q1")
    add_group(nfa, "q1", group(p, "Data libraries"), "q2")
    add_group(nfa, "q2", group(p, "ML libraries"), "q2")
    add_group(nfa, "q2", group(p, "ML libraries"), "q3")
    add_group(nfa, "q3", group(p, "ML concepts"), "q3")
    add_group(nfa, "q3", group(p, "Database"), "q4")
    add_group(nfa, "q4", group(p, "Database"), "q4")
    nfa.add_transition("q3", "GIT", "q5")
    nfa.add_transition("q4", "GIT", "q5")
    return nfa


# --- DevOps Engineer: epsilon-NFA ---
# (PYTHON)? LINUX Container+ CICD+ Cloud* VersionControl+
# epsilon transitions skip the optional groups
def build_devops():
    p = "DEVOPS_ENGINEER"
    enfa = EpsilonNFA()
    enfa.add_start_state("q0")
    enfa.add_final_state("q6")
    enfa.add_transition("q0", "PYTHON", "q1")
    enfa.add_transition("q0", Epsilon(), "q1")
    enfa.add_transition("q1", "LINUX", "q2")
    add_group(enfa, "q2", group(p, "Containers"), "q3")
    add_group(enfa, "q3", group(p, "Containers"), "q3")
    add_group(enfa, "q3", group(p, "CI/CD"), "q4")
    add_group(enfa, "q4", group(p, "CI/CD"), "q4")
    enfa.add_transition("q4", Epsilon(), "q5")
    add_group(enfa, "q5", group(p, "Cloud"), "q5")
    add_group(enfa, "q5", group(p, "Version control"), "q6")
    add_group(enfa, "q6", group(p, "Version control"), "q6")
    return enfa


# --- Data Analyst: DFA with several final states ---
# SQL (PYTHON DataLib*)? BI+ (DATA_ANALYSIS)? Database*
def build_data_analyst():
    p = "DATA_ANALYST"
    dfa = DeterministicFiniteAutomaton()
    dfa.add_start_state("q0")
    for state in ["q4", "q5", "q6"]:
        dfa.add_final_state(state)
    dfa.add_transition("q0", "SQL", "q1")
    dfa.add_transition("q1", "PYTHON", "q2")
    add_group(dfa, "q2", group(p, "Data libraries"), "q3")
    add_group(dfa, "q3", group(p, "Data libraries"), "q3")
    for state in ["q1", "q2", "q3", "q4"]:
        add_group(dfa, state, group(p, "BI tools"), "q4")
    dfa.add_transition("q4", "DATA_ANALYSIS", "q5")
    add_group(dfa, "q4", group(p, "Database"), "q6")
    add_group(dfa, "q5", group(p, "Database"), "q6")
    add_group(dfa, "q6", group(p, "Database"), "q6")
    return dfa


AUTOMATA = {
    "FULL_STACK_DEVELOPER": build_full_stack(),
    "MACHINE_LEARNING_ENGINEER": build_ml_engineer(),
    "DEVOPS_ENGINEER": build_devops(),
    "DATA_ANALYST": build_data_analyst(),
}


def evaluate(canonical_skills, profile_name):
    # sorted word for the profile and the automaton answer
    word = sort_for_profile(canonical_skills, profile_name)
    accepted = AUTOMATA[profile_name].accepts(word)
    return word, accepted


def classify(canonical_skills):
    # result for the four profiles
    results = {}
    for profile_name in AUTOMATA:
        word, accepted = evaluate(canonical_skills, profile_name)
        results[profile_name] = {
            "sequence": word,
            "result": "ACCEPTED" if accepted else "REJECTED",
        }
    return results


def accepted_profiles(results):
    names = []
    for profile_name in results:
        if results[profile_name]["result"] == "ACCEPTED":
            names.append(profile_name)
    return names


if __name__ == "__main__":
    skills = ["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"]
    for name, info in classify(skills).items():
        print(name, info["sequence"], "->", info["result"])
