# ARGUS

A public-records correlation tool. It searches real legal and corporate
endpoints for a name, pulls the documents down, extracts them, and links the
ones that share a specific identifier. Every link carries the exact lines that
produced it, in both documents, with URLs.

It does not decide whether a match matters. It produces evidence a person (or
an agent at a federal desk) can check line by line.

## Run it

```bash
mvn package                      # jar with all dependencies
java -jar target/argus-1.0.0.jar # http://localhost:8080
```

The Java half stores records and links, plus Hibernate Envers history so a
confidence that changes over repeated crawls stays auditable.

Requires Java 17. Default store is a file-backed H2 database at `./data/argus`;
set `ARGUS_DB_URL` / `ARGUS_DB_USER` / `ARGUS_DB_PASSWORD` for Postgres.

## The Python half

```bash
pip install -r requirements.txt
export ARGUS_GOVINFO_KEY=...        # free at api.data.gov; DEMO_KEY is rate-limited to uselessness
# or keep the key in a local .env (already gitignored) and: set -a; . ./.env; set +a
export ARGUS_COURTLISTENER_TOKEN=...  # optional, free account

python3 trawler_public_records.py > crawl.json
python3 ingest.py crawl.json --api http://localhost:8080
```

`search_sources.py` is the source registry. Each source reports whether it can
actually be queried and why not, so "unavailable" never looks like "nothing
found":

| source | state |
| --- | --- |
| api.govinfo.gov (USCOURTS, agencies) | works, needs a key (DEMO_KEY gets 429 quickly) |
| efts.sec.gov full-text (EDGAR) | works, no key, needs a real contact User-Agent |
| courtlistener api/rest/v4 | 401 without a free account token |
| fbi.gov/search | 403 Cloudflare challenge, browser required |
| justice.gov/search | client-rendered, HTML carries no results, browser required |

## What a connection looks like

```json
{
  "entity": "Monica Witt",
  "entity_type": "PERSON",
  "confidence": 0.9,
  "basis": "person match, exact string match, base 0.9, 2 documents",
  "evidence": [
    {"url": "https://.../pdf", "matched_text": "Monica Witt",
     "quote": "The defendant Monica Witt, a former Air Force ..."},
    {"url": "https://.../pdf", "matched_text": "Monica Witt",
     "quote": "Monica Witt was charged in a superseding indictment ..."}
  ]
}
```

Confidence is derived, not fixed: exact string match scores higher than a near
duplicate, near duplicates are grouped only at 92% similarity with a matching
surname, and each extra document adds a small corroboration bump.

Two kinds of match are refused outright:

- identifiers too thin to identify anything ("Case Number 3"),
- a docket number shared across two different courts (two cases, not one).

## Tests

```bash
python3 -m unittest discover -s tests -v
```
