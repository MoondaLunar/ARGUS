# Rehabilitation validation and remaining work

Updated 2026-11-21 (America/New_York). Findings reference upstream `30b5f605e9b5a1c18c753491d37d24c76c3f40bc`. Draft PRs are stacked in review order; none is merged.

## Completed validation

| Area | Evidence |
|---|---|
| Python | 44 tests pass through `scripts/test_offline.py`; real DNS/socket connections blocked in the test process |
| Java | 8 tests pass: repeat/concurrent document upserts, preserved enrichment, distinct link evidence, score correction, validation, Envers prior revisions, no hash credibility upgrade, missing-key gate, exact PDF/signature ZIP packaging (some tests cover multiple assertions) |
| Data preservation | Tests use synthetic records and disposable H2 only; no existing user database or Drive file modified |
| Scope | No live target requests, continuous scheduling, infrastructure probes or biometric comparisons performed |
| Vocabulary | Regression checks retain literal dictionary members and enforce inactive hypotheses/exclusions; no identifier asserted as verified without reviewed source metadata |
| Local utilities | GPS tag mapping/altitude, absent/corrupt metadata, blank PDF, image dimensions, distance and dictionary-valued GPS patterns tested |
| Candidate semantics | No fuzzy identity merge, no document-count confidence increase, court-qualified docket matches, mirrored-text suppression, full-text case view |
| Error/provenance handling | Redirect scope, byte bound, private DNS rejection, malformed URLs, explicit fetch/source errors, credential redaction and request isolation tested with fixtures |

Java ran on the available JDK 21 using source/target 17. The runtime lacks the release-signature archive needed for `--release 17`; this is not a native JDK 17 compatibility certification. Mockito uses its subclass mock maker because this runtime cannot attach an inline Java agent. Export signing was mocked and the exact supplied PDF bytes were checked, not real-key cryptographic verification.

## Inspection coverage

All 71 upstream text files were retrieved for static review and inventory, including Python, Java, configuration, setup scripts, examples and manuals. The reference photograph was inventoried and not used for identification. The relevant Drive root source/configuration/manual files were downloaded and compared. Generated outputs, private logs and state directories were catalogued; their contents and binary behavior were not exhaustively audited. Private historical files were not republished.

Inventory byte sizes and SHA-256 values refer to the normalized local text snapshots used for inspection, not exact raw Git blob bytes or Drive-provider integrity attestations. The immutable upstream commit and paths identify the source version. Historical comparison ignores newline/terminal whitespace. Vocabulary snapshot hashes have the same normalized-text limitation; source occurrences identify the original research context.

## Remaining acceptance gates, in priority order

1. **Database rollout:** reviewed additive migration, backup/restore rehearsal, PostgreSQL integration and multi-process contention tests. Do not run inherited `ddl-auto=update` against existing data as a migration plan. Existing nullable evidence keys need an explicit non-destructive backfill design.
2. **Evidence domain integration:** ordinary document/link records and the separate findings/admiralty/export domain remain distinct. Add an explicit, reviewed mapping before claiming end-to-end signed exports of crawler evidence. Durable raw-response storage and replayable extraction remain to implement.
3. **Live source adapters:** obtain approval for exact sources, queries and bounds before testing. Search adapters still have separate HTTP implementations; consolidate them with bounded transport, credential handling and source-specific rate limits before operational use. GovInfo download credentials and SEC contact headers require explicit configuration. Browser-gated sources remain unavailable; no browser bypass attempted.
4. **Transport hardening:** preflight DNS checks are not socket-level pinning, especially through proxies. Add an explicit egress policy/pinned connector and encoded-path tests before exposing arbitrary retrieval input. No production security certification is claimed.
5. **Authentication/export:** verify actual signing and signature verification using disposable keys; address replay and method/path binding. Loopback without a configured key is not authenticated. Review authorization before binding beyond loopback.
6. **Dependencies and portability:** native JDK 17 CI, PostgreSQL tests, reproducible dependency constraints/locks and dependency advisory review remain outstanding. No package-security audit claim is made. Source adapter availability tables in older docs are historical observations, not current verified service status.
7. **Retained capability migration:** standalone graph/checkpoint pipeline, model concurrency, timelines/graphs, alerts and durable scheduler recovery need separate fixtures and contracts. The top-entities endpoint remains a stub. No unexplained deletion substitutes for this work.
8. **Research classification:** review inactive archived terms by source context. Conservative placement in speculative/unreviewed vocabulary is not an assertion that the term itself is false. Populate verified identifiers only from reviewed public-source quotations; no target sources were contacted for verification here.

The draft changes repair concrete defects and establish a tested passive foundation. They do not certify the complete historical platform as production-ready. Follow-up work above should remain small reviewable PRs with explicit preservation and acceptance criteria.
