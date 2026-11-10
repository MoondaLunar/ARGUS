"""
Where ARGUS looks, and what it is allowed to claim about each place.

Every source here answers two questions honestly:
  available() -> (bool, reason). False means "cannot search this from the
  current process", with the reason spelled out (Cloudflare challenge, missing
  token). Nothing is papered over as an empty result.
  search(term) -> list of SourceHit. Each hit keeps the query that produced it,
  so a record can always say how it was found.

Endpoints verified live on 2026-11-10 from this sandbox:
  govinfo /search?offsetMark=*   200, JSON, federal court and agency collections
  govinfo package PDF            200, application/pdf, 10 pages
  efts.sec.gov/LATEST/search-index 200, JSON full-text search
  courtlistener api/rest/v4      401 without a token (token required)
  www.fbi.gov/search?q=          403 Cloudflare interstitial ("Just a moment...")
  www.justice.gov/search?keys=   403, returns a JS shell, results not in the HTML
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

import requests


@dataclass
class SourceHit:
    source: str
    query: str
    title: str
    url: str
    doc_id: str
    court: Optional[str] = None
    date: Optional[str] = None
    collection: Optional[str] = None
    extra: Dict = field(default_factory=dict)

    def as_dict(self) -> Dict:
        return asdict(self)


class SearchSource:
    name = "base"
    #: how the user turns this source on, when it is not on by default
    requires: Optional[str] = None

    def available(self) -> Tuple[bool, str]:
        return True, "ok"

    def search(self, term: str, limit: int = 10) -> List[SourceHit]:
        raise NotImplementedError


class GovInfoSource(SearchSource):
    """Federal court opinions/orders and agency documents via api.govinfo.gov.

    DEMO_KEY works for a handful of requests per hour. Register a key at
    api.data.gov and set ARGUS_GOVINFO_KEY for real use.
    """

    name = "govinfo"
    API = "https://api.govinfo.gov/search"

    def __init__(self, api_key: Optional[str] = None, collection: str = "USCOURTS", timeout: int = 30):
        self.api_key = api_key or os.environ.get("ARGUS_GOVINFO_KEY") or "DEMO_KEY"
        self.collection = collection
        self.timeout = timeout

    def available(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "no govinfo key"
        return True, "ok"

    def search(self, term: str, limit: int = 10) -> List[SourceHit]:
        body = {
            "query": f'collection:{self.collection} "{term}"',
            "pageSize": limit,
            "offsetMark": "*",
        }
        r = requests.post(self.API, params={"api_key": self.api_key}, json=body, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        hits = []
        for item in data.get("results", []):
            pdf = (item.get("download") or {}).get("pdfLink")
            fetch_url = None
            if pdf:
                sep = "&" if "?" in pdf else "?"
                fetch_url = f"{pdf}{sep}api_key={self.api_key}"
            hits.append(
                SourceHit(
                    source=self.name,
                    query=term,
                    title=item.get("title") or item.get("packageId", ""),
                    url=pdf or item.get("resultLink") or "",
                    doc_id=item.get("packageId", ""),
                    court=(item.get("governmentAuthor") or [None])[0],
                    date=item.get("dateIssued"),
                    collection=item.get("collectionCode") or self.collection,
                    extra={"fetch_url": fetch_url} if fetch_url else {},
                )
            )
        return hits


class SecEdgarSource(SearchSource):
    """SEC EDGAR full-text search. No key; send a real User-Agent."""

    name = "sec_edgar"
    API = "https://efts.sec.gov/LATEST/search-index"

    def __init__(self, user_agent: Optional[str] = None, timeout: int = 30):
        self.ua = user_agent or os.environ.get("ARGUS_USER_AGENT") or "ARGUS osint tool (contact: set ARGUS_USER_AGENT)"
        self.timeout = timeout

    def search(self, term: str, limit: int = 10) -> List[SourceHit]:
        r = requests.get(
            self.API,
            params={"q": f'"{term}"'},
            headers={"User-Agent": self.ua, "Accept": "application/json"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        hits = []
        for h in r.json().get("hits", {}).get("hits", [])[:limit]:
            src = h.get("_source", {})
            cik = (src.get("ciks") or [""])[0].lstrip("0") or ""
            adsh = src.get("adsh", "").replace("-", "")
            filename = h.get("_id", "").split(":", 1)[-1] if ":" in h.get("_id", "") else src.get("file_id", "")
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh}/{filename}" if cik and adsh and filename else ""
            hits.append(
                SourceHit(
                    source=self.name,
                    query=term,
                    title=" ".join(src.get("display_names", []) or [src.get("file_type", "")]),
                    url=url,
                    doc_id=h.get("_id", ""),
                    date=src.get("file_date"),
                    collection="EDGAR",
                )
            )
        return hits


class CourtListenerSource(SearchSource):
    """Dockets and opinions. A free account token is required (401 without)."""

    name = "courtlistener"
    API = "https://www.courtlistener.com/api/rest/v4/search/"

    def __init__(self, token: Optional[str] = None, timeout: int = 30):
        self.token = token or os.environ.get("ARGUS_COURTLISTENER_TOKEN")
        self.timeout = timeout

    def available(self) -> Tuple[bool, str]:
        if not self.token:
            return False, "needs ARGUS_COURTLISTENER_TOKEN (free account, api/rest/v4 returns 401 without it)"
        return True, "ok"

    def search(self, term: str, limit: int = 10) -> List[SourceHit]:
        r = requests.get(
            self.API,
            params={"q": f'"{term}"', "type": "o"},
            headers={"Authorization": f"Token {self.token}", "Accept": "application/json"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        hits = []
        for item in r.json().get("results", [])[:limit]:
            hits.append(
                SourceHit(
                    source=self.name,
                    query=term,
                    title=item.get("caseName") or item.get("docketNumber") or item.get("absolute_url", ""),
                    url="https://www.courtlistener.com" + (item.get("absolute_url") or ""),
                    doc_id=str(item.get("id", "")),
                    court=item.get("court"),
                    date=item.get("dateFiled"),
                    collection="COURTLISTENER",
                )
            )
        return hits


class BrowserGatedSource(SearchSource):
    """A real place ARGUS cannot query headlessly. It says so instead of
    returning an empty list that reads like 'nothing was found'."""

    def __init__(self, name: str, url_template: str, reason: str):
        self.name = name
        self.url_template = url_template
        self.reason = reason
        self.requires = "a browser session"

    def available(self) -> Tuple[bool, str]:
        return False, self.reason

    def search(self, term: str, limit: int = 10) -> List[SourceHit]:
        return []

    def open_url(self, term: str) -> str:
        return self.url_template.format(term=requests.utils.quote(term))


def default_sources() -> List[SearchSource]:
    return [
        GovInfoSource(),
        SecEdgarSource(),
        CourtListenerSource(),
        BrowserGatedSource(
            "fbi.gov",
            "https://www.fbi.gov/search?q={term}",
            "Cloudflare JS challenge (403 'Just a moment...'); open in a browser or wire a browser session",
        ),
        BrowserGatedSource(
            "justice.gov",
            "https://www.justice.gov/search?keys={term}",
            "search page is client-rendered; the HTML shell carries no results",
        ),
    ]


def search_all(terms: List[str], sources: Optional[List[SearchSource]] = None, limit: int = 10) -> Dict:
    """Run every available source for every term and report what each one did."""
    sources = sources if sources is not None else default_sources()
    report = {"terms": terms, "sources": [], "hits": [], "unavailable": [], "errors": []}
    for src in sources:
        ok, reason = src.available()
        entry = {"source": src.name, "available": ok, "reason": reason, "requires": src.requires}
        if getattr(src, "url_template", None):
            entry["browser_url_template"] = src.url_template
        report["sources"].append(entry)
        if not ok:
            report["unavailable"].append({"source": src.name, "reason": reason})
            continue
        for term in terms:
            try:
                hits = src.search(term, limit=limit)
                report["hits"].extend(h.as_dict() for h in hits)
            except Exception as exc:  # a source failing is data, not silence
                report["errors"].append({"source": src.name, "term": term, "error": f"{type(exc).__name__}: {exc}"})
    return report


if __name__ == "__main__":
    import sys

    terms = sys.argv[1:] or ["Monica Witt"]
    print(json.dumps(search_all(terms, limit=3), indent=2))
