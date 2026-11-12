# Historical capabilities and migration boundary

The original crawler generations are preserved in place and in Git history. Their imports now fail explicitly before optional dependencies, agent construction or network execution. This is an intentional quarantine, not a claim that their functionality has been replaced. Remove no data or state files.

| Retained capability | Supported path / migration requirement |
|---|---|
| HTML/PDF public-record search and retrieval | `trawler_public_records.py`, offline by default |
| Historical vocabulary | `research/vocabulary-original.json`; source locations preserved |
| Active research terms | `research/search-profile.json` through `research_config.py` |
| Local EXIF/PDF metadata | `metadata_extractor.py`, optional dependencies |
| Fuzzy matching, timelines, graphs and distance utilities | `analysis_engine*.py`; exploratory output, never identity verification |
| Specialized case reports | Historical `trawler_irgc_monica_witt.py`; migrate to evidence-based filters before re-enabling |
| Cached/threaded model analysis | Historical enhanced crawlers; migrate with explicit context, candidate schemas and concurrency tests |
| Graph checkpoint/cache/PGP pipeline | Historical `import os.py`; migrate with schema/version compatibility tests |
| Continuous scheduler and alerts | Preserved, disabled; requires separate user approval and repaired durable state |
| Infrastructure probes and biometric identification | Preserved as historical source only; excluded from this platform |
| Random/fixed simulated intelligence and linguistic identity claims | Historical only; must never enter evidence storage |

No verified alias is populated merely because a historical file calls it known. The initial active profile contains two literal research name queries with an explicit unverified/contextual label. All other historical vocabulary stays inactive. Exclusions are not positive queries and do not silently discard a document that contains relevant evidence.
