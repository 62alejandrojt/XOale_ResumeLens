# ResumeLens

ResumeLens is a resume screening tool based on formal languages.
It reads plain text resumes and checks if the candidate skills match
a professional profile.

This project is the Integrative Task 1 of *Computación y Estructuras Discretas III* (ICESI, 2026-2).

## Pipeline

1. **Extraction** - regular expressions (`re`) find contact data, experience and skills.
2. **Normalization** - finite-state transducers (`pyformlang`) map skill variants to one canonical name (JS -> JAVASCRIPT).
3. **Classification** - finite automata (`pyformlang`) check the skills against four profiles.
4. **Profile language** - a context-free grammar (`textX`) defines and validates the candidate profile.
5. **Visualization** - a valid profile is exported to HTML / Markdown.

## Profiles

- Full Stack Developer
- Machine Learning Engineer
- DevOps Engineer *(software engineering profile chosen by the team)*
- Data Analyst *(AI / data profile chosen by the team)*

| Profile | Automaton | Pattern |
|---|---|---|
| Full Stack Developer | DFA | `Language+ Frontend+ Backend+ Database+ (REST_API)? GIT` |
| Machine Learning Engineer | NFA | `PYTHON DataLib+ MLLib+ Concept* Database* GIT` |
| DevOps Engineer | ε-NFA | `(PYTHON)? LINUX Container+ CICD+ Cloud* VC+` |
| Data Analyst | DFA | `SQL (PYTHON DataLib*)? BI+ (DATA_ANALYSIS)? Database*` |

## Project structure

```
docs/     design documents (Markdown)
src/      Python source code
tests/    unit tests, sample resumes (tests/resumes/) and profiles (tests/profiles/)
```

Generated HTML / Markdown profiles are saved in `output/`, which is created
when the program runs and is not part of the repository.

## Requirements

- Python 3.10+
- pyformlang
- textX

```
pip install -r requirements.txt
```

## How to run

Run all commands from the root folder of the repository.

**Main program (console menu):**

```
python -m src.main
```

| Option | Description |
|---|---|
| 1 | Process one resume, e.g. `tests/resumes/wednesday_addams.txt` |
| 2 | Process all sample resumes in `tests/resumes/` |
| 3 | Validate a candidate profile written by hand, e.g. `tests/profiles/invalid_email.cand` |
| 4 | Exit |

The results are saved in `output/<candidate>.html`, `.md` and `.cand`.
Open the `.html` file in a browser to see the candidate profile.

**Each stage alone:**

```
python -m src.extractor
python -m src.normalizer
python -m src.classifier
python -m src.profile_language
python -m src.visualizer
```

**Unit tests:**

```
python -m unittest discover tests -v
```

## Resume format

Resumes are plain `.txt` files:

```
Full Name
Email: name@example.com
Phone: +57 300 123 4567
Location: City

Summary:
N years of experience ...

Experience:
- Role at Company (N years)

Education:
- Degree, Institution

Technical Skills:
skill, skill, skill
```

Only the name and email are required. Skills are searched in the whole text.

## Design documents

| Document | Content |
|---|---|
| [01_overview.md](docs/01_overview.md) | problem and modules |
| [02_regex.md](docs/02_regex.md) | regular expressions |
| [03_transducers.md](docs/03_transducers.md) | transducers (7-tuples and diagrams) |
| [04_automata.md](docs/04_automata.md) | automata (5-tuples and diagrams) |
| [05_grammar.md](docs/05_grammar.md) | EBNF grammar of the profile language |
| [06_visualization.md](docs/06_visualization.md) | HTML / Markdown output and main program |
| [07_tests.md](docs/07_tests.md) | test cases and scenarios |

## Team

- Brayan Alejandro Jimenez Timana - A00430989

## IDE

Visual Studio Code
