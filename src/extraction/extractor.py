import re
from typing import Dict, Optional

from bs4 import BeautifulSoup


SECTION_HEADINGS = [
    "responsibilities",
    "requirements",
    "qualifications",
    "about",
    "description",
]


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract(html: str) -> Dict[str, Optional[str]]:
    """Legacy extractor returning title/text/sections."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    body_text = clean_text(soup.get_text(" "))

    sections: Dict[str, Optional[str]] = {}
    for heading in soup.find_all(re.compile("^h[1-6]$")):
        key = heading.get_text().strip().lower()
        if any(h in key for h in SECTION_HEADINGS):
            content_parts = []
            sib = heading.find_next_sibling()
            while sib and sib.name not in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                content_parts.append(sib.get_text(" "))
                sib = sib.find_next_sibling()
            sections[key] = clean_text(" ".join(content_parts)) if content_parts else None

    return {"title": title, "text": body_text, "sections": sections}


def extract_sections(html: str) -> Dict[str, Optional[str]]:
    """Structured extraction used by the pipeline."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    title = None
    if soup.title and soup.title.string:
        title = clean_text(soup.title.string)
    if not title:
        h1 = soup.find("h1")
        if h1 and h1.get_text():
            title = clean_text(h1.get_text())

    company = None
    company_meta = soup.find("meta", attrs={"property": "og:site_name"})
    if company_meta and company_meta.get("content"):
        company = clean_text(company_meta["content"])
    if not company:
        company_el = soup.find(class_=re.compile("company|employer", re.I))
        if company_el:
            company = clean_text(company_el.get_text())

    location = None
    location_el = soup.find(class_=re.compile("location", re.I))
    if location_el and location_el.get_text():
        location = clean_text(location_el.get_text())

    body_text = clean_text(soup.get_text(" "))

    # Description: prefer a main content area
    description = None
    main = soup.find("main") or soup.find("article")
    if main:
        description = clean_text(main.get_text(" "))
    else:
        description = body_text

    # Summary: first 400 chars of description
    summary = description[:400] + "…" if description and len(description) > 400 else description

    return {
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "summary": summary,
    }
