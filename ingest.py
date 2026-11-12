"""Push a crawl result into the running ARGUS API.

The Python half does the finding and the Java half does the storing and the
version history, which only counts as one system if something walks between
them. This is that walk.

    python3 ingest.py crawl.json --api http://localhost:8080

Documents are keyed by identifier (the source URL), so re-running a crawl
updates rather than duplicates. Connections carry their evidence as rationale:
the two quoted lines and the document each came from.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Dict

import requests


def evidence_rationale(conn: Dict) -> str:
    parts = [f"basis: {conn.get('basis', '')}"]
    for ev in conn.get("evidence", []):
        quote = " ".join((ev.get("quote") or "").split())
        parts.append(f"[{ev.get('title') or ev.get('document')}] {quote} ({ev.get('url')})")
    return "\n".join(parts)


def ingest(crawl: Dict, api: str, timeout: int = 30) -> Dict:
    session = requests.Session()
    stats = {"documents": 0, "document_errors": [], "links": 0, "link_errors": []}

    for rec in crawl.get("records", []):
        payload = {
            "sourceType": "web",
            "identifier": rec["url"],
            "documentType": "pdf" if str(rec.get("url", "")).endswith("/pdf") else "html",
            "url": rec["url"],
            "metadata": json.dumps(
                rec.get("found_by") or {}, default=str
            ),
            "extractedText": (rec.get("text_excerpt") or "")[:20000],
        }
        r = session.post(f"{api}/api/documents", json=payload, timeout=timeout)
        if r.ok:
            stats["documents"] += 1
        else:
            stats["document_errors"].append({"url": rec["url"], "status": r.status_code, "body": r.text[:200]})

    for conn in crawl.get("connections", []):
        payload = {
            "entityA": conn["entity"],
            "entityB": conn.get("entity_type", "entity"),
            "confidence": conn["confidence"],
            "rationale": evidence_rationale(conn),
            "sourceUrl": (conn.get("evidence") or [{}])[0].get("url"),
            "linkType": conn.get("connection_type", "entity_co-occurrence"),
            "metadataEvidence": json.dumps(conn.get("evidence") or [], default=str),
        }
        r = session.post(f"{api}/api/links", json=payload, timeout=timeout)
        if r.ok:
            stats["links"] += 1
        else:
            stats["link_errors"].append({"entity": conn["entity"], "status": r.status_code, "body": r.text[:200]})

    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("crawl_json")
    ap.add_argument("--api", default="http://localhost:8080")
    args = ap.parse_args()

    crawl = json.loads(open(args.crawl_json).read())
    stats = ingest(crawl, args.api)
    print(json.dumps(stats, indent=2))
    return 0 if not (stats["document_errors"] or stats["link_errors"]) else 1


if __name__ == "__main__":
    sys.exit(main())
