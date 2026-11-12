"""Historical network pipelines are preserved but not executable."""

def blocked(module):
    raise RuntimeError(
        f'{module} is retained for historical review, but its legacy runtime is disabled. '
        'Use trawler_public_records.PublicRecordsCrawler with offline fixtures. '
        'Active probes, biometric identification and continuous crawling are not supported. '
        'See docs/rehabilitation/FINDINGS.md and LEGACY.md.'
    )
