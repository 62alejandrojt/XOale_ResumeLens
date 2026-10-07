# Test Design

All tests use Python's `unittest` and are in the `tests/` folder.

```
python -m unittest discover tests -v
```

| File | Stage | Number of tests |
|---|---|---|
| `test_extractor.py` | 1 - Regular expressions | 18 |
| `test_normalizer.py` | 2 - Transducers | 20 |
| `test_classifier.py` | 3 - Automata | 26 |
| `test_profile_language.py` | 4 - Grammar (textX) | 17 |
| `test_visualizer.py` | 5 - Visualization | 8 |
| `test_main.py` | Main program | 3 |
| `test_scenarios.py` | Whole pipeline | 15 |
| **Total** | | **107** |

## Scenarios (test data)

Each scenario is a resume in `tests/resumes/` or a profile in `tests/profiles/`.
They were chosen to cover one accepted case per profile, a case with two
profiles, a case with no profile and the invalid profiles of the grammar.

| ID | File | Situation it represents | Expected result |
|---|---|---|---|
| S1 | `wednesday_addams.txt` | Example of the statement. Short names: JS, React.js, NodeJS, Postgres | FULL_STACK_DEVELOPER |
| S2 | `mary_jane_watson.txt` | Example of the statement. ML libraries and concepts in the summary | MACHINE_LEARNING_ENGINEER |
| S3 | `bruce_wayne.txt` | Abbreviations (K8s, CI/CD), "5+ years", two jobs, a job of "1 year" | DEVOPS_ENGINEER |
| S4 | `lisa_simpson.txt` | No phone, concept "data analysis" only in the summary | DATA_ANALYST |
| S5 | `hermione_granger.txt` | Mixed spelling (sklearn, Py Torch, PowerBI), two degrees | MACHINE_LEARNING_ENGINEER and DATA_ANALYST |
| S6 | `homer_simpson.txt` | Skills that do not form any pattern, no education | no profile (valid profile with 4 REJECTED) |
| P1 | `wednesday_addams.cand` | Profile written by hand that follows the grammar | valid |
| P2 | `invalid_email.cand` | Email without domain | rejected (lexical) |
| P3 | `missing_evaluation.cand` | Required block missing | rejected (syntax) |

## Stage 1 - Extraction (`test_extractor.py`)

Setup: the text of S1 is stored in the constant `WEDNESDAY`.

| Class | Test | Input | Expected |
|---|---|---|---|
| TestContactData | test_name | S1 text | `Wednesday Addams` |
| | test_email | S1 text | `wednesday.addams@example.com` |
| | test_phone | S1 text | `+57 300 123 4567` |
| | test_location | S1 text | `Nevermore Academy, Jericho` |
| | test_years | S1 text | `3` |
| | test_invalid_email | `wednesday.addams@` | no match |
| | test_short_phone | `call 12345` | no match |
| TestSections | test_experience | S1 text | role, company and 3 years |
| | test_education | S1 text | degree and institution |
| | test_summary | S1 text | summary in one line |
| | test_no_sections | text without sections | empty lists |
| TestSkills | test_example_from_statement | S1 text | `JS, React.js, NodeJS, Postgres, Git` |
| | test_js_not_inside_react | `React.js and Node.js` | no language found |
| | test_java_vs_javascript | `Java, JavaScript` | both, separated |
| | test_spaced_variants | `Tensor Flow, Py Torch, scikit learn` | the three are found |
| | test_sql_not_inside_postgresql | `PostgreSQL` | only database, not SQL |
| | test_no_repeated_skills | `Git, Git, Git` | `Git` once |
| | test_concepts | `machine learning models` | `machine learning` |

## Stage 2 - Normalization (`test_normalizer.py`)

| Class | Test | Input | Expected |
|---|---|---|---|
| TestTokenize | test_dot | `React.js` | `react`, `js` |
| | test_dash_and_space | `Scikit-learn`, `scikit learn` | `scikit`, `learn` |
| | test_slash | `CI/CD` | `ci`, `cd` |
| | test_keeps_plus_and_hash | `C++`, `C#` | one token each |
| TestNormalizeSkill | test_javascript | JS, Javascript, JavaScript, Java Script | `JAVASCRIPT` |
| | test_java_is_not_javascript | `Java` | `JAVA` (nondeterministic path) |
| | test_react | React, React.js, ReactJS | `REACT` |
| | test_node | NodeJS, Node.js, node | `NODE_JS` |
| | test_postgres | Postgres, PostgreSQL | `POSTGRESQL` |
| | test_scikit | sklearn, scikit learn, Scikit-learn | `SCIKIT_LEARN` |
| | test_spaced_names | Tensor Flow, Py Torch | `TENSORFLOW`, `PYTORCH` |
| | test_rest | REST API, REST APIs, RESTful API | `REST_API` |
| | test_concept | machine learning, predictive models | `MACHINE_LEARNING` |
| | test_unknown | `Cobol`, `react native app`, empty | `None` |
| | test_incomplete_variant | `Tensor` | `None` (ends in non-final state) |
| TestNormalizeList | test_repeated_variants | `JS, Javascript, Cobol` | `[JAVASCRIPT]`, unknown `[Cobol]` |
| TestSortForProfile | test_example_from_statement | `Git, NodeJS, JS, Postgres, React.js` | `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT` |
| | test_order_does_not_matter | same skills in two orders | same sorted word |
| | test_drops_other_skills | `DOCKER, PYTHON` for Full Stack | empty word |
| TestWithExtractor | test_mary_jane | S2 file | sorted ML word, no unknown skills |

## Stage 3 - Classification (`test_classifier.py`)

| Class | Test | Input word | Expected |
|---|---|---|---|
| TestAutomatonType | test_full_stack_is_dfa | A1 | `is_deterministic()` True |
| | test_ml_is_nfa | A2 | False |
| | test_devops_is_not_deterministic | A3 (ε-NFA) | False |
| | test_data_analyst_is_dfa | A4 | True |
| TestFullStack | test_statement_example | `JAVASCRIPT REACT NODE_JS POSTGRESQL GIT` | accepted |
| | test_with_rest_api | `... MYSQL REST_API GIT` | accepted |
| | test_several_per_group | two items in several groups | accepted |
| | test_missing_backend | no backend | rejected |
| | test_missing_git | no GIT | rejected |
| | test_empty | ε (empty word) | rejected |
| TestMLEngineer | test_statement_example | `PYTHON PANDAS TENSORFLOW POSTGRESQL GIT` | accepted |
| | test_with_concepts | `... PYTORCH DEEP_LEARNING GIT` | accepted |
| | test_missing_ml_library | no ML library | rejected |
| | test_missing_python | no PYTHON | rejected |
| TestDevOps | test_full_word | all groups | accepted |
| | test_epsilon_skips_optional | `LINUX DOCKER CI_CD GITHUB` | accepted (ε skips Python and cloud) |
| | test_missing_containers | no container tool | rejected |
| TestDataAnalyst | test_only_sql_and_bi | `SQL POWER_BI` | accepted (final state q4) |
| | test_full_word | all groups | accepted (final state q6) |
| | test_missing_bi_tool | no BI tool | rejected |
| | test_missing_sql | no SQL | rejected |
| TestClassify | test_order_from_resume_does_not_matter | skills in reverse order | sorted word, accepted |
| | test_wednesday_pipeline | S1 | only Full Stack |
| | test_mary_jane_pipeline | S2 | only ML Engineer |
| | test_two_profiles | ML + BI skills | ML Engineer and Data Analyst |
| | test_no_profile | `PHP` | no profile |

## Stage 4 - Profile language (`test_profile_language.py`)

Setup: `MINIMAL` is the smallest valid profile (contact, skills, evaluation).

| Class | Test | Input | Expected |
|---|---|---|---|
| TestValidProfiles | test_hand_written_file | P1 | valid, fields read from the model |
| | test_minimal_profile | MINIMAL | valid, optional blocks are `None` |
| | test_several_jobs | two `job` lines | 2 jobs |
| | test_empty_skills_block | `skills { }` | valid |
| TestLexicalErrors | test_bad_email | P2 | rejected, "Expected Email" |
| | test_lowercase_skill | `sql` | rejected |
| | test_unknown_status | `MAYBE` | rejected |
| | test_years_not_number | `years: two` | rejected |
| TestSyntaxErrors | test_missing_evaluation | P3 | rejected, "Expected 'evaluation'" |
| | test_missing_brace | no closing `}` | rejected |
| | test_wrong_block_order | skills before contact | rejected |
| | test_unknown_profile | `CHEF` | rejected |
| TestExtraRules | test_repeated_skill | `SQL SQL` | `ProfileError` |
| | test_repeated_profile | same profile twice | rejected, "twice" |
| TestGeneratedProfiles | test_wednesday | S1 through stages 1-4 | valid, Full Stack accepted |
| | test_mary_jane | S2 through stages 1-4 | valid, ML accepted |
| | test_quotes_in_text | name with `"` | quotes replaced, valid |

## Stage 5 - Visualization and main (`test_visualizer.py`, `test_main.py`)

| Class | Test | Input | Expected |
|---|---|---|---|
| TestHtml | test_is_html_document | P1 model | starts with `<!DOCTYPE html>` |
| | test_personal_data | P1 model | name and email in the HTML |
| | test_skills | P1 model | one `skill` span per skill |
| | test_evaluation | P1 model | 1 accepted, 3 rejected |
| | test_optional_parts_missing | MINIMAL | no experience/education sections |
| | test_escape | name `Ana <Perez>` | `Ana &lt;Perez&gt;` |
| TestMarkdown | test_content | P1 model | title, skills and result table |
| | test_titles | `DEVOPS_ENGINEER` | `DevOps Engineer` |
| TestMain | test_file_name | `Mary-Jane  Watson!` | `mary_jane_watson` |
| | test_full_pipeline | S1 file | files `.html`, `.md`, `.cand` created |
| | test_missing_file | file that does not exist | `FileNotFoundError` |

## Whole pipeline (`test_scenarios.py`)

| Class | Scenario | What is checked |
|---|---|---|
| TestScenario1FullStack | S1 | accepted profiles = Full Stack |
| TestScenario2MLEngineer | S2 | accepted profiles = ML Engineer |
| TestScenario3DevOps | S3 | K8s → KUBERNETES, CI/CD → CI_CD, "5+ years" → 5, two jobs, DevOps accepted |
| TestScenario4DataAnalyst | S4 | no phone in the profile, DATA_ANALYSIS from the summary, Data Analyst accepted |
| TestScenario5TwoProfiles | S5 | sklearn, Py Torch, PowerBI normalized, two degrees, two profiles accepted |
| TestScenario6NoProfile | S6 | skills `PHP, JAVA, EXCEL`, no education, valid profile with 4 REJECTED |
