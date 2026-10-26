# Sully Guide Engine — Implementation 001

## Delivered on development branch
- `scripts/sully_epg_engine.py`: standalone, Python-standard-library XMLTV parser and channel mapping engine.
- `tests/test_sully_epg_engine.py`: six synthetic/offline tests.
- Does not download external sources, alter live channel data, publish schedules, or require subscriptions.

## Example invocation
`python scripts/sully_epg_engine.py input.xml mapping.json approved-provider-id output.json`

Mapping format: `{"xmltv-channel-id": "sully-channel-id"}`. These must be verified mappings, not guessed. Input source must have independently reviewed permissions for intended use.

## Safety and quality behavior
- Refuses DTD and entity declarations; bounded input (5 MB) and programme count (20,000).
- Requires explicit timezone offsets; normalizes times to UTC.
- Ignores unmapped channels, missing titles, invalid dates, and nonpositive durations.
- Deduplicates entries, sorts chronologically, preserves source provenance.
- Refuses to write an empty schedule.

## Limitations and next gates
- Code committed but NOT executed in GitHub Actions or tested in production at time of writing.
- Not yet a streaming/bounded-memory parser; limits are deliberately conservative for small licensed feeds.
- No HTTP fetching, multi-provider priority, rights registry, coverage threshold, atomic output, or live UI integration yet.
- Add fixture-based CI, then evaluate authorized provider data and verified channel mappings.
- Production use requires further adversarial XML handling and real-provider tests.
