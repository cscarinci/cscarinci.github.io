# cscarinci.github.io

Personal homepage. `content/` holds the data, `build.py` renders it into `_site/`, GitHub Actions deploys on every push to `main`.

| File | Contents |
|---|---|
| `content/site.yml` | Name, affiliation, contact, profile links, positions, education, grants, events, memberships, current projects; optional `photo`, `cv_pdf` and `goatcounter` |
| `content/intro.md` | Home page introduction |
| `content/research.md` | Research statement |
| `content/publications.yml` | Preprints and articles, newest first |
| `content/teaching.yml` | Current and previous courses, mentoring |

The project `text` field accepts Markdown and inline HTML; quote any value that contains `: `.

## Local preview

```
pip install -r requirements.txt
python build.py
python -m http.server -d _site 8000
```

## GitHub Pages

Repository `cscarinci/cscarinci.github.io`, branch `main`. Settings > Pages > Source: GitHub Actions.
