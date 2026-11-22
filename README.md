# ARGUS

ARGUS is a passive public-record research platform under rehabilitation. The supported Python pipeline extracts document text, records source provenance, and proposes cross-document mention matches for human review. A match, linguistic similarity, GPS tag, or numerical score does not verify identity, affiliation, location of a person, or wrongdoing.

Start with [the findings and prioritized plan](docs/rehabilitation/FINDINGS.md), [validation and remaining work](docs/rehabilitation/VALIDATION.md), and [the preservation map](LEGACY.md). Other setup guides, examples, and manuals describe historical implementations and may contain unsupported claims or network-enabled commands.

## Supported offline workflow

Use Python 3.11+ and a virtual environment:

```bash
python -m venv .venv
# Activate the virtual environment for your shell.
python -m pip install -r requirements-utilities.txt
python scripts/test_offline.py
```

The test runner blocks real DNS and socket connections. Tests use synthetic documents and injected source/HTTP responses. The optional utilities requirements include local image metadata and legacy analysis imports; `requirements.txt` is sufficient for the supported public-record pipeline alone.

```bash
python trawler_public_records.py > offline-report.json
python ingest.py offline-report.json
```

The first command reports network-disabled sources, not live search results. Ingestion previews payloads by default. Explicit `--send` writes only to a loopback API. No scheduler is started. Live source testing requires a separately approved source/query/limit plan; no live compatibility claim is made here.

## Research vocabulary

`research/vocabulary-original.json` preserves the original literal vocabulary and source occurrences. `research/search-profile.json` separately classifies verified identifiers, contextual research terms, speculative hypotheses, and exclusions. Only two contextual name queries are initially active. Verified identifiers remain empty pending source review; historical alias labels are not verification. Hypotheses and exclusions cannot become active queries through the configuration loader.

The specialized case view uses this same profile, examines retained full text, and preserves all collected records alongside the filtered view. Its historical declarations do not drive matching.

## Evidence and correlation

Records retain requested/final URLs, discovery routes, retrieval timestamp, raw-byte SHA-256, extracted-text SHA-256, MIME type, bounded extracted text, and explicit failures. Retrieval uses approved HTTPS hosts, validates redirects, and bounds streamed response size. Raw response bytes are not yet durably archived. DNS checks are preflight checks, not connection pinning.

Exact normalized mentions produce candidate links carrying both document identifiers and quotations. Similar names are separate review candidates. Dockets require a known matching court. Mirrored text does not become independent corroboration, and document count does not increase confidence. Scores describe extraction heuristics, not calibrated identity probabilities.

Ingestion preserves pair-specific evidence keys and redacts structured credentials in legacy provenance. Original input files are not modified. The Java service updates documents by identifier, retains absent enrichment, and records changes through Hibernate Envers. Envers provides database revision history, not immutable or cryptographically tamper-proof storage. The separate findings API remains a separate domain; its signed export does not automatically export crawler document/link records.

## Backend validation

Use a full JDK 17 and Maven:

```bash
mvn test
mvn package
```

Tests use disposable in-memory H2 databases. Before starting the application against existing data, back up the database and review schema migration: the inherited configuration uses Hibernate `ddl-auto=update`. No existing user database was opened during rehabilitation. PostgreSQL has a runtime driver, but migration and integration tests remain outstanding.

The service binds `127.0.0.1` by default. Its optional PGP gate fails closed if a configured key is missing. Without a configured key, loopback API access is unauthenticated. Export requires signing-key configuration and returns a ZIP containing the exact PDF and detached signature; real-key signing has not been exercised in this work.

Continuous monitoring, infrastructure probes, biometric identification, and the standalone legacy graph runtime remain disabled. Local metadata, distance analysis, timeline/graph helpers, and legacy parsers remain available for offline research; their heuristic outputs are exploratory. See the preservation map before using older modules.
