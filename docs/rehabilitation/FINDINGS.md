# ARGUS rehabilitation findings and plan

Inspection date: 2026-11-12. Upstream baseline: `30b5f605e9b5a1c18c753491d37d24c76c3f40bc`.
Historical reference: Google Drive folder `data crawler`. No target requests, continuous crawl, biometric comparison, or infrastructure probes were run. Findings below are source observations unless explicitly described as test results.

## Scope and preservation

The upstream tree contains 72 files: 71 text files and one reference photograph. All text files were retrieved for static inspection; the photograph is inventoried and left untouched, not used for identification. The Drive root has 67 source/configuration/documentation files besides the photograph and logs, plus generated-code, editor, upgrade-history and crawler-state directories. Source text was compared with newline normalization; binary build products are not treated as source truth. Drive remains read-only. Private logs/state and private-only historical source are not copied into this public repository.

`INVENTORY.json` records file-level source inventory, Python definitions/imports, and historical comparison. This is a whole-tree static assessment, not a claim that every feature has passed runtime validation. Historical generated binaries and upgrade tooling are catalogued separately from application functionality.

## Architecture and entry points

| Area | Actual implementation | Main concerns |
|---|---|---|
| `trawler.py` | MemoryWebTrawler, HTML traversal, Ollama and proximity fallback | Alternate crawler, own networking and scoring |
| `trawler_enhanced.py` | Images/PDF metadata, local assets, GPS links | Optional dependencies omitted from current requirements; unvalidated attribution |
| `trawler_enhanced_v2.py` | Thread pool, TTL caches, assets, model calls | `query_ollama` passes an integer context hash into the prompt path instead of source text; shared mutable edges; arbitrary confidence |
| `trawler_public_records.py` | Search frontier, HTML/PDF retrieval, regex entities, cross-document links | Best candidate for supported pipeline; URL, provenance, scope and dedup defects |
| `trawler_irgc_monica_witt.py` | Wrapper filtering public-record output using its own target lists | Duplicated dictionaries, 0.95 keyword confidence, truncated-text filtering |
| `trawler_24_7_continuous.py` | Async loop plus five CrewAI roles, state counters, alerts | Active probing, DeepFace, simulated observations, Windows-only imports, stub backend sync |
| `import os.py` | Independent graph/cache/PGP pipeline | Another incompatible graph and persistence path; additional undeclared dependencies |
| `analysis_engine*.py` | Fuzzy matching, distance clustering, graphs/timelines | Heuristic scores are not identity probabilities; rounded coordinates called geohashes |
| `metadata_extractor.py` | Local image EXIF and PDF metadata | Wrong GPS tag dictionary, null/error handling, eager optional imports |
| `search_sources.py` | GovInfo, SEC, CourtListener, unavailable-source placeholders | Credentials embedded in exported fetch URL; no credential-safe error output |
| `ingest.py` | POST documents and links to Spring API | No request exception isolation; truncated evidence; incompatible edge identity |
| Java `ArgusApplication` | Scans all three package families | Deliberate broad scanning supports historical packages; do not flatten blindly |
| `CrawlerController` | Documents, links, GPS clusters, summary APIs | Document insert is not upsert; pair-only edge collapse; top-entities endpoint is stub |
| `IntelligenceController` | Separate findings/admiralty/Envers and PDF export | Disconnected from ordinary document ingestion; client-supplied data hash; export returns signature as PDF |
| PGP filter/services | Optional detached body signature | Missing configured key silently disables gate; replay/path binding absent |
| Examples and setup tools | Multiple executable demos, Ollama diagnostics/model download | Not tests; can cause live traffic; must not run as verification |

## Historical comparison

Most root Python/configuration/manual files are text-equivalent to Drive (ignoring newline/terminal whitespace). Current public-record crawler adds real search-source integration, byte-preserving PDF handling, larger PDF text extraction, names, evidence quotes and court-source checks. Preserve these improvements. New `search_sources.py`, `ingest.py`, application entry point/resources and five Python tests form the newer integration layer.

Historical `IntelligenceLinkEnhanced.java` and its repository correspond to the current `com.crawler` model/repository; earlier unenhanced classes and `IntelligenceLinkController.java` are a superseded API generation, not proof that every old endpoint should be restored. The two finding/link domains remain separate. Current requirements shrank to requests/BeautifulSoup/pypdf while retained modules still import Pillow, PyPDF2, fuzzywuzzy, cachetools, psutil, CrewAI, DeepFace, NetworkX, pyvis and PGPy. The historical requirements also do not cover every late addition.

## Prioritized defects

### P0: Passive scope and evidence integrity

1. `trawler_24_7_continuous.py:perform_infrastructure_probe`, `calculate_tls_fingerprint`, `check_dns_canaries`, and `perform_facial_biometric_check` violate the requested scope. The agent tool list exposes these operations. Preserve source for historical inspection but make the legacy runtime unavailable pending modular migration; no approval flag should enable biometric/probe tools.
2. `analyze_ip_geospatial_footprint`, `analyze_environmental_leakage`, `monitor_ghost_accounts`, `analyze_breach_patterns` include fixed/random/simulated claims. Those outputs cannot be evidence. `_sync_to_immutable_backend` is `pass`; state persistence saves counters rather than a full restartable frontier and evidence store.
3. `irgc_monica_witt_config.get_all_search_terms` flattens `noise_exclusions` into positive terms. Four dictionary locations disagree: main config, continuous config, continuous fallback lists, specialized wrapper. Context, speculation and identifiers are mixed. “Known” labels in these files are not source verification.
4. `PublicRecordsCrawler._canonical_name` groups similar people; `_connection_confidence` boosts repeated documents. Neither linguistic similarity nor URL diversity proves identity or independent corroboration. `CorroborationService` upgrades equal hashes at different URLs, even to “Confirmed”; matching copies are not independent sources.
5. URL relevance uses substring membership, including path/query/userinfo; exclusion `ad` rejects innocent paths. Seeds and search results bypass that filter, and redirects are unchecked. Bound network access before every request, including credential-bearing download paths.

### P1: Pipeline correctness

6. `fetch_document` does HEAD then unbounded GET, follows redirects implicitly, drops errors, and trusts a misleading Content-Length. Restrict types, stream with byte limits, validate redirects, and record status/failure separately from an empty result.
7. HTML is parsed as markup text rather than visible document text. PDF extraction failures and disabled PDF processing are not represented reliably. Document IDs use process-randomized `hash(text)` modulo one million; use versioned SHA-256 identities.
8. Provenance only keeps one search hit per URL; API key is included in `extra.fetch_url`; timestamps, raw/content digests and final retrieval URL are absent. Preserve all discovery routes without storing credentials.
9. Docket correlation compares `source`, which may be the same generic publisher for distinct courts. Unknown court must not establish case equivalence. Duplicate entities/documents and mirrored content need separate treatment.
10. `ingest.py` sends `entityB=entity_type`, losing document-pair identity. Backend upserts all links by entityA/entityB and only replaces with a higher confidence. Separate evidence pairs/types and allow corrected lower scores while retaining audit revisions.
11. `saveDocument` always inserts despite unique identifier. Re-ingestion conflicts rather than updates. Preserve enrichment and all previous versions; do not wipe metadata fields absent from a new request. Concurrency must be tested explicitly.
12. `PgpSignatureFilter` permits everything when configured key is missing. Default service does not explicitly bind loopback. Postgres is advertised but JDBC driver is absent; LONGTEXT column definitions are not portable. No Java tests exist.
13. Evidence export generates PDF then returns only detached signature bytes with application/pdf. Export both exact PDF and its signature; keep signing secrets out of source. Envers is revision history, not cryptographically immutable storage.

### P2: Retained capabilities requiring follow-up validation

14. Metadata GPS decoding uses EXIF_TAGS instead of GPSTAGS; missing extraction result is passed to `asdict({})`. Fix locally with fixtures; document GPS as metadata, never proof a person was present.
15. Optimized model cache sends a hash instead of context; proximity outputs and metadata-derived entity links need candidate-only semantics. Preserve graph, caching, timelines and local metadata capabilities while isolating legacy network execution.
16. Config values advertised in manuals are often not consumed; top-entities API returns an empty list. Manuals overstate deployment readiness, immutable audit, “verified” identity and operational predictions. Mark historical manuals as such and make supported behavior explicit.
17. No CI, Java tests, migrations, dependency lock, or network-blocking regression harness in baseline. Existing five tests cover some correlations, including an expectation that near names merge. Initial baseline attempt failed before collection because the runtime lacked requests; this is an environment failure, not an assertion failure.

## Review sequence and acceptance gates

1. **Findings and inventory**: commit this report before code changes. No runtime modifications.
2. **Vocabulary and passive controls**: archive original vocabulary with source paths/categories; central active profile; no unsourced verified identifiers; exclusions never positive queries; quarantine legacy execution with explicit explanations and preservation map. Tests: complete vocabulary retention, category boundaries, no legacy execution.
3. **Public-record retrieval and provenance**: approved host allowlist, explicit live opt-in (not exercised here), bounded GET/redirect handling, credential-safe transport, stable records, HTML/PDF parsing, complete provenance and errors. Tests use injected sessions/sources and synthetic documents only.
4. **Correlation and ingestion**: exact mention candidates, no identity claims or corroboration boosts, court-qualified docket matches, duplicate suppression, preserved evidence, request/error isolation and deterministic evidence identity.
5. **Backend persistence and audit**: transactional upsert with repeat/concurrent tests, schema portability, fail-closed configured PGP gate, loopback default, correct PDF/signature packaging, no automatic credibility upgrades. Do not run against an existing user database. Test only disposable databases.
6. **Retained utilities and documentation**: local metadata fixes and meaningful regressions; isolate speculative/legacy scoring; update supported instructions, dependency split and validation results. Publish small draft PRs and keep all unmerged.

Live endpoint compatibility is intentionally unverified. No claim that legacy models, DeepFace, probes, continuous monitoring, PostgreSQL migration, signing with the user's keys, or production deployment has been validated. Before any approved future live run, review exact sources, queries, page/byte limits and credentials separately. Database schema rollout requires a backup and migration review; this work must not mutate existing data.
