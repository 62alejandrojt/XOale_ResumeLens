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
- *(software engineering profile - TBD)*
- *(AI / data profile - TBD)*

## Project structure

```
docs/          design documents (Markdown)
src/           Python source code
tests/         unit tests
data/resumes/  sample resumes (.txt)
output/        generated HTML / Markdown files
```

## Requirements

- Python 3.10+
- pyformlang
- textX

```
pip install -r requirements.txt
```

## How to run

*(will be added when the main script is ready)*

## Team

- Alejandro - *(code / group)*
- *(member 2)*
- *(member 3)*

## IDE

Visual Studio Code
