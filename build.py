#!/usr/bin/env python3
"""Render content/ into _site/. Run: python3 build.py"""
import pathlib
import re
import shutil

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "_site"

# page name -> (template, output path, nav label)
PAGES = {
    "home": ("home.html", "index.html", "Home"),
    "research": ("research.html", "research/index.html", "Research"),
    "teaching": ("teaching.html", "teaching/index.html", "Teaching"),
    "cv": ("cv.html", "cv/index.html", "CV"),
}


def md(text: str) -> str:
    """Markdown -> HTML; unwrap a single paragraph."""
    html = markdown.markdown(text.strip())
    if html.count("<p>") == 1:
        html = html[3:-4]
    return html


def year_of(ref: str) -> str:
    """Year from a journal reference, or from an arXiv identifier (arXiv:YYMM.NNNNN)."""
    m = re.search(r"\b(19|20)\d\d\b", ref or "")
    if m:
        return m.group(0)
    m = re.search(r"arXiv:(\d\d)(\d\d)\.", ref or "")
    return f"20{m.group(1)}" if m else ""


TERM_ORDER = {"Spring": 0, "Summer": 1, "Fall": 2, "Winter": 3}


def term_key(term: str):
    """Sort key for 'Fall 2026' style terms (year, season)."""
    parts = term.split()
    if len(parts) == 2 and parts[1].isdigit():
        return (int(parts[1]), TERM_ORDER.get(parts[0], 9))
    return (int(re.search(r"\d{4}", term).group(0)) if re.search(r"\d{4}", term) else 0, 9)


def group_courses(courses):
    """Courses grouped by institution, then by title, with the list of terms taught (newest first)."""
    by_where = {}
    for c in courses:
        by_where.setdefault(c["where"], {}).setdefault(c["title"], []).append(c["term"])
    out = []
    for where, titles in by_where.items():
        rows = []
        for title, terms in titles.items():
            terms = sorted(terms, key=term_key, reverse=True)
            years = sorted({term_key(t)[0] for t in terms})
            span = str(years[0]) if len(years) == 1 else f"{years[0]}\u2013{years[-1]}"
            rows.append(dict(title=title, terms=terms, span=span, latest=term_key(terms[0])))
        rows.sort(key=lambda r: r["latest"], reverse=True)
        out.append(dict(where=where, rows=rows, latest=max(r["latest"] for r in rows)))
    out.sort(key=lambda g: g["latest"], reverse=True)
    return out


def main() -> None:
    c = ROOT / "content"
    site = yaml.safe_load((c / "site.yml").read_text())
    pubs = yaml.safe_load((c / "publications.yml").read_text())
    teaching = yaml.safe_load((c / "teaching.yml").read_text())
    teaching["grouped"] = group_courses(teaching["current"] + teaching["previous"])
    teaching["grouped_previous"] = group_courses(teaching["previous"])
    research = markdown.markdown((c / "research.md").read_text())
    intro = markdown.markdown((c / "intro.md").read_text())

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=False)
    env.filters["md"] = md
    env.filters["year"] = year_of

    nav = [(name, "/" + out.replace("index.html", ""), label) for name, (_, out, label) in PAGES.items()]
    ctx = dict(site=site, research=research, intro=intro, pubs=pubs, teaching=teaching,
               nav=nav)

    for name, (tpl, out, _) in PAGES.items():
        path = OUT / out
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(env.get_template(tpl).render(page=name, **ctx))
    shutil.copytree(ROOT / "static", OUT / "static", dirs_exist_ok=True)
    print("built", ", ".join(out for _, out, _ in PAGES.values()))


if __name__ == "__main__":
    main()
