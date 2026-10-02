# Stage 2: normalize skills with finite-state transducers (pyformlang)
import re

from pyformlang.fst import FST

from src.profiles import profile_order

# Rules for each transducer: canonical output -> list of input variants
# Each variant is written as tokens separated by spaces
RULES = {
    "languages": {
        "JAVASCRIPT": ["javascript", "js", "java script"],
        "TYPESCRIPT": ["typescript", "ts", "type script"],
        "PYTHON": ["python"],
        "JAVA": ["java"],
        "CPP": ["c++", "cpp"],
        "CSHARP": ["c#"],
        "PHP": ["php"],
        "SQL": ["sql"],
    },
    "frameworks": {
        "REACT": ["react", "reactjs", "react js"],
        "ANGULAR": ["angular", "angularjs", "angular js"],
        "VUE": ["vue", "vuejs", "vue js"],
        "NODE_JS": ["node", "nodejs", "node js"],
        "EXPRESS": ["express", "expressjs", "express js"],
        "DJANGO": ["django"],
        "FLASK": ["flask"],
        "SPRING_BOOT": ["springboot", "spring boot"],
    },
    "libraries": {
        "PANDAS": ["pandas"],
        "NUMPY": ["numpy"],
        "SCIKIT_LEARN": ["sklearn", "scikitlearn", "scikit learn"],
        "TENSORFLOW": ["tensorflow", "tensor flow"],
        "PYTORCH": ["pytorch", "py torch"],
        "KERAS": ["keras"],
    },
    "databases": {
        "POSTGRESQL": ["postgres", "postgresql"],
        "MYSQL": ["mysql"],
        "SQLITE": ["sqlite"],
        "MONGODB": ["mongodb", "mongo db"],
        "REDIS": ["redis"],
        "NOSQL": ["nosql", "no sql"],
    },
    "tools": {
        "GIT": ["git"],
        "GITHUB": ["github"],
        "GITLAB": ["gitlab"],
        "DOCKER": ["docker"],
        "KUBERNETES": ["kubernetes", "k8s"],
        "LINUX": ["linux"],
        "JENKINS": ["jenkins"],
        "AWS": ["aws"],
        "AZURE": ["azure"],
        "CI_CD": ["ci cd"],
        "REST_API": ["rest api", "rest apis", "restful api", "restful apis"],
        "EXCEL": ["excel"],
        "POWER_BI": ["powerbi", "power bi"],
        "TABLEAU": ["tableau"],
    },
    "concepts": {
        "MACHINE_LEARNING": ["machine learning", "predictive model", "predictive models"],
        "DEEP_LEARNING": ["deep learning"],
        "DATA_ANALYSIS": ["data analysis"],
    },
}

START = "q0"
FINAL = "qf"


def tokenize(raw_skill):
    # "React.js" -> ["react", "js"], "Scikit-learn" -> ["scikit", "learn"]
    tokens = re.split(r"[\s.\-_/]+", raw_skill.lower())
    return [t for t in tokens if t != ""]


def build_transducer(rules):
    # one start state, one final state, middle states named by the prefix read
    fst = FST()
    fst.add_start_state(START)
    fst.add_final_state(FINAL)
    for canonical in rules:
        for variant in rules[canonical]:
            tokens = variant.split(" ")
            current = START
            # all tokens but the last one write nothing (epsilon)
            for i in range(len(tokens) - 1):
                next_state = "q_" + "_".join(tokens[:i + 1])
                fst.add_transition(current, tokens[i], next_state, [])
                current = next_state
            # the last token writes the canonical name
            fst.add_transition(current, tokens[-1], FINAL, [canonical])
    return fst


TRANSDUCERS = {}
for name in RULES:
    TRANSDUCERS[name] = build_transducer(RULES[name])


def normalize_skill(raw_skill):
    # tries every transducer, returns the canonical name or None
    tokens = tokenize(raw_skill)
    if not tokens:
        return None
    for name in TRANSDUCERS:
        outputs = list(TRANSDUCERS[name].translate(tokens))
        if outputs:
            return outputs[0][0]
    return None


def normalize(raw_skills):
    # returns (canonical skills without repeats, skills not recognized)
    canonical = []
    unknown = []
    for raw in raw_skills:
        result = normalize_skill(raw)
        if result is None:
            unknown.append(raw)
        elif result not in canonical:
            canonical.append(result)
    return canonical, unknown


def sort_for_profile(canonical_skills, profile_name):
    # keeps only the skills of the profile, in the profile order
    ordered = []
    for skill in profile_order(profile_name):
        if skill in canonical_skills:
            ordered.append(skill)
    return ordered


def to_mermaid(fst):
    # text for a Mermaid diagram (used in the docs)
    lines = ["stateDiagram-v2", "    [*] --> " + START]
    for (state, symbol), targets in fst.transitions.items():
        for target, output in targets:
            out = output[0] if output else "ε"
            # "#" is a special char in Mermaid
            label = str(symbol).replace("#", "#35;")
            lines.append("    " + str(state) + " --> " + str(target) + " : " + label + " / " + out)
    lines.append("    " + FINAL + " --> [*]")
    return "\n".join(lines)


if __name__ == "__main__":
    raw = ["Git", "NodeJS", "JS", "Postgres", "React.js"]
    skills, unknown = normalize(raw)
    print("input:     ", raw)
    print("normalized:", skills)
    print("full stack:", sort_for_profile(skills, "FULL_STACK_DEVELOPER"))
