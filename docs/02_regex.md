# Stage 1 - Information Extraction with Regular Expressions

Module: `src/extractor.py`

## Purpose

This stage finds text that may represent candidate data or qualifications.
It does **not** decide if two skills are equivalent (that is Stage 2) and it
does **not** decide if the candidate fits a profile (that is Stage 3).

## Expected resume format

The resumes are plain `.txt` files with some simple sections:

```
<Full Name>
Email: ...
Phone: ...
Location: ...

Summary:
...

Experience:
- <Role> at <Company> (<N> years)

Education:
- <Degree>, <Institution>

Technical Skills:
skill, skill, skill
```

Skills are searched in the **whole text**, not only in the skills section,
because a resume can mention a technology in the experience or summary.

## Regular expressions

Notation: `Σ` is the set of keyboard characters. `[A-Z]` is one uppercase
letter, `\d` one digit, `x?` means optional, `x+` one or more, `x*` zero or more.

### 1. Name

```
^[ \t]*([A-Z][a-zA-Z'-]+(?:[ \t]+[A-Z][a-zA-Z'-]+)+)[ \t]*$
```

Language: lines formed by **two or more words** that start with an uppercase
letter, separated by spaces, and nothing else on the line.
Accepts: `Wednesday Addams`, `Mary Jane Watson`.
Rejects: `Email: x@y.com` (has `:`), `wednesday addams` (lowercase).
Only the first match is used.

### 2. Email

```
[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}
```

Language: `local @ domain . extension`, where the extension has at least
two letters.
Accepts: `wednesday.addams@example.com`. Rejects: `wednesday.addams@`.

### 3. Phone

```
(?:\+\d{1,3}[ .-]?)?\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}
```

Language: an optional country code (`+57`), then groups of 3, 3 and 4 digits
separated by an optional space, dot or dash. The separator is the character
class `[ .-]`, so adding the dot only makes the language bigger; it is still regular.
Accepts: `+57 300 123 4567`, `315 987 6543`, `(315)987-6543`, `300.123.4567`. Rejects: `12345`.

### 4. Location

```
^Location:[ \t]*(.+)$
```

Language: lines that start with `Location:`. Group 1 is the rest of the line.

### 5. Years of experience

```
(\d+)\+?\s+years?\s+of\s+experience
```

Language: a number, an optional `+`, the word `year` or `years`, then
`of experience`. Accepts: `3 years of experience`, `5+ years of experience`,
`1 year of experience`.

### 6. Sections

```
^<Title>:[ \t]*\n((?:[ \t]*\S.*\n?)+)
```

Language: the header line `Title:` followed by one or more **non-empty** lines.
The block ends at the first blank line. Used for `Experience` and `Education`.

### 7. Experience item

```
^-[ \t]*(?P<role>.+?)[ \t]+at[ \t]+(?P<company>.+?)[ \t]*\((?P<years>\d+)[ \t]+years?\)[ \t]*$
```

Language: lines like `- Role at Company (N years)`. Named groups keep the
role, the company and the number of years.

### 8. Education item

```
^-[ \t]*(?P<degree>[^,\n]+),[ \t]*(?P<institution>.+)$
```

Language: lines like `- Degree, Institution`. The first comma splits both parts.

### 9. Skills by category

All skill expressions use the same frame:

```
(?<![\w.])( alternatives )(?![\w+#])
```

- `(?<![\w.])` : the skill cannot come right after a letter, digit or dot.
- `(?![\w+#])` : the skill cannot be followed by a letter, digit, `+` or `#`.

This works like a word limit. Thanks to it `JS` is **not** found inside
`React.js` or `NodeJS`, `SQL` is not found inside `PostgreSQL`, and `Java` is
not found inside `JavaScript`. All skill regexes are case insensitive.

| Category | Alternatives (union of words) | Example matches |
|---|---|---|
| languages | `java\s?script \| type\s?script \| python \| java \| c\+\+ \| c# \| php \| sql \| js \| ts` | JS, Javascript, Java Script, SQL |
| frameworks | `react(\.?js)? \| angular(\.?js)? \| vue(\.?js)? \| node(\.?js)? \| express(\.?js)? \| django \| flask \| spring\s?boot` | React.js, ReactJS, NodeJS, Node.js |
| libraries | `pandas \| numpy \| scikit[\s-]?learn \| sklearn \| tensor\s?flow \| py\s?torch \| keras` | Scikit-learn, scikit learn, Tensor Flow |
| databases | `postgre(s\|sql) \| mysql \| sqlite \| mongo\s?db \| redis \| no\s?sql` | Postgres, PostgreSQL, MongoDB |
| tools | `github \| gitlab \| git \| docker \| kubernetes \| k8s \| linux \| jenkins \| aws \| azure \| ci\s?/\s?cd \| rest(ful)?\s?apis? \| excel \| power\s?bi \| tableau` | Git, REST APIs, CI/CD, Power BI |
| concepts | `machine[\s-]learning \| deep[\s-]learning \| predictive\s+models? \| data\s+analysis` | machine learning, predictive models |

Each category is a **union** of simple regular expressions, so each one is
still a regular language. Optional parts (`\.?js`, `\s?`) let the same regex
accept several spellings. Choosing one canonical name is done in Stage 2.

## Output (data structure)

`extract(text)` returns a dictionary:

```python
{
  "name": "Wednesday Addams",
  "email": "wednesday.addams@example.com",
  "phone": "+57 300 123 4567",
  "location": "Nevermore Academy, Jericho",
  "years_experience": 3,
  "experience": [{"role": "Web Application Developer",
                  "company": "Nevermore Academy Projects", "years": 3}],
  "education": [{"degree": "B.Sc. in Computer Science",
                 "institution": "Nevermore Academy"}],
  "skills": {"languages": ["JS"], "frameworks": ["React.js", "NodeJS"], ...},
  "all_skills": ["JS", "React.js", "NodeJS", "Postgres", "Git", "REST APIs"]
}
```

`all_skills` keeps the skills **as written** in the resume. This list is the
input of Stage 2 (normalization). `save_extraction(data, path)` can also save
the result in a text file.

## Limitations

- Resumes must follow the simple format above for name, experience and education.
- A common word can be confused with a skill (for example `node` in "a graph node").
- Skills not listed in the patterns are ignored.
