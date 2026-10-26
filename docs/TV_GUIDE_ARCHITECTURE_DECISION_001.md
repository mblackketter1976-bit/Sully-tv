# Sully TV Guide Engine — Architecture Decision 001
Date: 2026-10-25
Status: DECISION / RESEARCH; no live deployment; no external listing rights assumed.

## Why the current workflow failed
GitHub Actions diagnostic run #7 showed 180,678 iptv-org guide records, 15,503 matching a live channel ID, and ZERO records with populated `sources`. Our script incorrectly treated `guides.json` as a guaranteed registry of downloadable XMLTV feeds. Raising the HTTP metadata cap removed the first error but did not create actual listings.

## Findings from upstream projects
- iptv-org/api documents `guides.json` with optional `sources`, but availability is not guaranteed. Source: https://github.com/iptv-org/api
- iptv-org/epg publishes open-source EPG collection tools and a list of community guides: https://github.com/iptv-org/epg and https://github.com/iptv-org/epg/blob/master/GUIDES.md. Open-source tool licensing is NOT equivalent to permission to redistribute all collected TV schedule data.
- EPGTalk publishes compressed regional and FreeTV XMLTV guides: https://github.com/acidjesuz/EPGTalk . Its free availability and legal-use notice are NOT an explicit blanket redistribution/commercial license; obtain suitable rights before copying, rehosting, bundling or using data in a public monetized product.
- XMLTV utilities are GPL-2.0 software: https://github.com/XMLTV/xmltv ; respect licensing if integrating their code.

## Architecture choice
Keep Sully TV independent of a single feed. Build a small provider-adapter pipeline:
1. **Source registry**: explicit reviewed providers, endpoint, source provenance, license/terms, last checked, size cap, priority, geographic coverage and channel-ID mapping. No guessed URLs.
2. **Fetch adapter**: HTTPS only, timeouts, bounded compressed and decompressed sizes, retry/backoff, conditional requests, no secrets in logs.
3. **Normalize**: map XMLTV channel IDs to verified Sully TV channel IDs; reject unknown or implausible times; preserve attribution and source identity; do not fabricate programs.
4. **Validate**: fresh listings, positive matched channel count, sensible future horizon, duplicate suppression, malformed XML rejection, source coverage report.
5. **Publish**: atomic update ONLY when validated and permitted by provider rights. Preserve last known valid data and mark stale when appropriate.
6. **UI**: distinguish 'Verified schedule', 'Guide unavailable', and 'Stale schedule'; never display made-up titles. Channel playback must remain independent.
7. **Fallback**: second authorized source where available; otherwise explicit no-data state. Do not silently switch to an unlicensed feed.

## Next implementation gate
Before selecting a feed for Sully TV production:
- Verify whether its terms authorize commercial/public reuse and redistribution.
- Probe a small sample of its XMLTV structure, time coverage, download limits and channel-ID overlap.
- Write offline fixture-based tests with tiny synthetic XMLTV examples; run in GitHub Actions on the development branch without publishing.
- Measure matched channel coverage and error handling.
- Only then connect a provider and request owner approval for deployment.

## Constraints
No recurring payments; minimize downloads and bandwidth; do not scrape sites in violation of terms; no dependence on one provider; no regressions to existing playback and DVR.

## Alternatives evaluated
| Option | Benefits | Caveats | Decision |
| --- | --- | --- | --- |
| iptv-org guides.json sources | Already integrated; matching channel IDs | All `sources` empty in observed run | Stop relying on it as sole EPG URL registry |
| iptv-org/epg tools/community guides | Open-source utilities; many sources | Data rights, source uptime, and scraping terms differ | Investigate permitted feed subset |
| EPGTalk XMLTV files | Existing compressed feeds; free access | Public/commercial redistribution rights not established; matching untested | Research only, not production-integrated |
| Own authorized broadcaster feeds | Potentially best provenance and rights | Uneven availability and varying formats | Preferred where licensing permits |
| Paid guide provider | May have clearer licensing | Conflicts with zero-cost requirement | Do not adopt |

## Verified vs unverified
Verified: GitHub Actions diagnostic counts from run #7; documentation and published project descriptions.
Unverified: feed licensing for Sully TV, actual channel overlap, program correctness, availability of specific endpoints in our runtime.
