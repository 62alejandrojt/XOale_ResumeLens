# Profile definitions shared by the normalizer and the classifier
# Each profile is a list of (group name, canonical skills) in canonical order

PROFILES = {
    "FULL_STACK_DEVELOPER": [
        ("Language", ["JAVASCRIPT", "TYPESCRIPT"]),
        ("Frontend", ["REACT", "ANGULAR", "VUE"]),
        ("Backend", ["NODE_JS", "EXPRESS", "DJANGO", "FLASK", "SPRING_BOOT"]),
        ("Database", ["POSTGRESQL", "MYSQL", "SQLITE", "MONGODB", "REDIS", "SQL", "NOSQL"]),
        ("API", ["REST_API"]),
        ("Version control", ["GIT"]),
    ],
    "MACHINE_LEARNING_ENGINEER": [
        ("Language", ["PYTHON"]),
        ("Data libraries", ["PANDAS", "NUMPY"]),
        ("ML libraries", ["SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS"]),
        ("ML concepts", ["MACHINE_LEARNING", "DEEP_LEARNING"]),
        ("Database", ["SQL", "POSTGRESQL", "MYSQL", "SQLITE", "MONGODB"]),
        ("Version control", ["GIT"]),
    ],
    # software engineering profile chosen by the team
    "DEVOPS_ENGINEER": [
        ("Scripting", ["PYTHON"]),
        ("Operating system", ["LINUX"]),
        ("Containers", ["DOCKER", "KUBERNETES"]),
        ("CI/CD", ["CI_CD", "JENKINS"]),
        ("Cloud", ["AWS", "AZURE"]),
        ("Version control", ["GIT", "GITHUB", "GITLAB"]),
    ],
    # AI / data profile chosen by the team
    "DATA_ANALYST": [
        ("Query language", ["SQL"]),
        ("Programming", ["PYTHON"]),
        ("Data libraries", ["PANDAS", "NUMPY"]),
        ("BI tools", ["EXCEL", "POWER_BI", "TABLEAU"]),
        ("Analysis", ["DATA_ANALYSIS"]),
        ("Database", ["POSTGRESQL", "MYSQL", "SQLITE"]),
    ],
}


def profile_order(profile_name):
    # flat list with the canonical order of a profile
    order = []
    for group in PROFILES[profile_name]:
        order.extend(group[1])
    return order
