import re
from typing import List

from bs4 import BeautifulSoup


JOB_LINK_PATTERNS = [
    re.compile(r"/careers/.*job", re.IGNORECASE),
    re.compile(r"/jobs/", re.IGNORECASE),
    re.compile(r"/positions/", re.IGNORECASE),
]


def discover_job_links(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(p.search(href) for p in JOB_LINK_PATTERNS):
            links.append(_resolve(base_url, href))
    return list(dict.fromkeys(links))


def _resolve(base: str, href: str) -> str:
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/"):
        return base.rstrip("/") + href
    return base.rstrip("/") + "/" + href
