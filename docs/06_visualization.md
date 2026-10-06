# Stage 5 - Visualization and Main Program

Files: `src/visualizer.py` and `src/main.py`

## Visualization

The visualization is generated **only from a valid candidate profile**. The
input is the textX model returned by `parse_profile` (Stage 4), not the raw
data of the previous stages. If the profile is rejected by the grammar, no
visualization is produced.

| Function | Input | Output |
|---|---|---|
| `to_html(model)` | valid `CandidateProfile` model | HTML document (string) |
| `to_markdown(model)` | valid `CandidateProfile` model | Markdown document (string) |
| `save(text, path)` | text and file path | file on disk |

The HTML follows the structure of the example given in the statement:

1. Header with the candidate name.
2. Personal information (email, phone, location).
3. Profile summary (if present).
4. Experience and education (if present).
5. Normalized technical skills (output of the transducers).
6. Qualification evaluation: one box per profile with `ACCEPTED` (green)
   or `REJECTED` (gray), the output of the automata.

Text values are escaped (`&`, `<`, `>`, `"`) so that a name like `Ana <Perez>`
does not break the HTML.

## Main program (console interface)

`src/main.py` connects the five stages:

```
resume.txt
   │  Stage 1  extract_from_file      (regular expressions)
   ▼
raw data + raw skills
   │  Stage 2  normalize              (finite-state transducers)
   ▼
canonical skills
   │  Stage 3  classify               (DFA / NFA / ε-NFA)
   ▼
ACCEPTED / REJECTED per profile
   │  Stage 4  build_profile_text + parse_profile   (textX grammar)
   ▼
valid candidate profile
   │  Stage 5  to_html / to_markdown
   ▼
output/<name>.html, output/<name>.md, output/<name>.cand
```

Run it from the root folder of the repository:

```
python -m src.main
```

Menu options:

| Option | What it does |
|---|---|
| 1. Process a resume | runs the whole pipeline for one `.txt` file and prints the result of each stage |
| 2. Process all sample resumes | runs the pipeline for every file in `tests/resumes/` |
| 3. Validate a candidate profile | validates a `.cand` file written by hand; if it is valid, it also generates the HTML/Markdown |
| 4. Exit | ends the program |

Example of option 1:

```
[1] Extraction
    name: Wednesday Addams | email: wednesday.addams@example.com
    raw skills: JS, React.js, NodeJS, Postgres, Git, REST APIs
[2] Normalization
    canonical skills: JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT, REST_API
[3] Classification
    FULL_STACK_DEVELOPER        ACCEPTED ['JAVASCRIPT', 'REACT', 'NODE_JS', 'POSTGRESQL', 'REST_API', 'GIT']
    MACHINE_LEARNING_ENGINEER   REJECTED ['POSTGRESQL', 'GIT']
    DEVOPS_ENGINEER             REJECTED ['GIT']
    DATA_ANALYST                REJECTED ['POSTGRESQL']
[4] Profile language: valid
[5] Output: output/wednesday_addams.html / .md / .cand
```

The `output/` folder is created when the program runs and is ignored by Git.

Errors handled: file not found, invalid menu option and invalid profile
(the error message of textX with line and column is shown).
