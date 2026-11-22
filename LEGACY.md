# Historical capabilities and migration boundary

Original source, vocabulary, data references and Git history are preserved. No collected data has been deleted. Historical documentation is retained for comparison; its operational commands and feature claims are not current instructions.

| Capability | Current disposition |
|---|---|
| HTML/PDF public-record retrieval and source discovery | Supported pipeline in `trawler_public_records.py`; network disabled by default; fixture-tested |
| Original research vocabulary | Archived with source locations in `research/vocabulary-original.json` |
| Active queries and verified identifiers | Central `research_config.py`; no unsourced verified alias; hypotheses/exclusions inactive |
| Local EXIF/PDF metadata | `metadata_extractor.py`; GPS decoding/null/PDF fixes tested; metadata is not proof of presence |
| Distance, timelines, metadata patterns, graph helpers | `analysis_engine*.py` retained; selected distance/pattern regressions pass; exhaustive graph/timeline validation pending |
| Specialized case view | `trawler_irgc_monica_witt.py` restored over the supported pipeline; full-text literal query matches only; all records retained |
| Original crawler parsers and model cache | Three crawler generations importable; their sessions reject every network request; full-context cache bug fixed; model behavior/concurrency unvalidated |
| Standalone graph/checkpoint/cache/PGP pipeline | `import os.py` retained but blocked before dependency loading; migration and state compatibility unresolved |
| Continuous scheduler, agents, alerts and state | Source retained; `trawler_24_7_continuous.py` blocked before dependency loading; no scheduler activation |
| Infrastructure probes and biometric identification | Historical source only, outside supported scope; not enabled by live retrieval opt-in |
| Random/fixed simulated observations and linguistic identity claims | Historical-only; excluded from supported evidence pipeline |
| Backend document/link records and separate findings | Both preserved; not falsely presented as one integrated domain; separate findings export does not include ordinary crawler records |

The legacy block is not a replacement claim. Restoration of a capability requires evidence schemas, fixture tests, passive scope review, and explicit documentation. Continuous scheduling and live target requests additionally require the user's approval. Importable legacy helpers remain exploratory: network blocking does not make their original heuristics reliable.
