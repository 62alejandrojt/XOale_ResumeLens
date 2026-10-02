# ResumeLens - Design Overview

## Problem

Resumes describe the same skill in many ways (JS, Javascript, JavaScript).
ResumeLens uses formal language models to extract, normalize and classify
those skills, and to represent the candidate in a small DSL.

ResumeLens does not rank candidates or make hiring decisions. It only checks
if the skills found in a resume satisfy a formally defined profile pattern.

## Modules

| Module | Formal model | Input | Output |
|---|---|---|---|
| `src/extractor.py` | Regular expressions | resume text | dict with raw data and skills |
| `src/normalizer.py` | Finite-state transducers | list of raw skills | list of canonical skills (sorted) |
| `src/classifier.py` | Finite automata | canonical skills | ACCEPTED / REJECTED per profile |
| `src/profile_dsl/` | Context-free grammar (textX) | profile text | validated model |
| `src/visualizer.py` | - | validated model | HTML / Markdown file |
| `src/main.py` | - | resume file | runs the whole pipeline |

## Design documents

- `02_regex.md` - regular expressions
- `03_transducers.md` - transducers (7-tuples and diagrams)
- `04_automata.md` - automata (5-tuples and diagrams)
- `05_grammar.md` - EBNF grammar of the profile language
- `06_tests.md` - test cases and scenarios
