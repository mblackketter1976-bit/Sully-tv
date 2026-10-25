# TV Guide reliability handoff — 2026-10-25

## Built
- Replaced the obsolete `guides.json` URL guessing path with an explicit provider registry (`data/guide-sources.json`) and the existing Sully XMLTV engine.
- Registry order selects provider priority. Reject overlapping duplicate listings, expired programmes, unreviewed reuse rights, insecure URLs, oversized downloads and oversized gzip expansion.
- Preserve the prior guide when providers fail, return no usable listings, or none are approved. Publish candidate JSON by atomic replacement. Preserve attribution in `sources`.
- Updater workflow retains a review artifact; it does not commit data or deploy the website.
- Guide hides stale and implausibly future-generated schedules, requires programme source identifiers, and finds programmes starting between half-hour boundaries. Language, station search and playback remain separate from schedule availability.

## Verified locally
- 19 Python tests passed, including the original 11 and updater integration/failure tests.
- All inline JavaScript passed `node --check`.
- Running the updater against the empty registry preserved the existing guide without a network request.

## Verified in GitHub Actions
- Run https://github.com/mblackketter1976-bit/Sully-tv/actions/runs/40241221857 passed both Python and guide-browser jobs on commit `971697dd688b6632019d7402a2e8bf61b611b96e`. Browser assertions passed at 1280px and 390px; screenshots retained as workflow artifacts for seven days. Local browser download failure was bypassed by running the same test in CI.

## Verification limits
- `tests/guide-browser.cjs` exercises the real guide function in an isolated DOM with explicitly synthetic channels and programmes at 1280px and 390px. Passing checks cover rendering, filters, watch dispatch, navigation, and stale data; it does not verify the full application, actual streaming, devices, remote controls or real schedule accuracy.
- No authorized live schedule provider has been verified. Registry is deliberately empty. A playable channel directory is available; a populated live programme guide is not ready.
- Half-hour cells are a coarse listing view. Two short programmes sharing a cell are not both represented. An exact timeline is a separate UI change.
- Existing static integrity check reports missing `sully-icon-192.png` and `sully-icon-512.png` on this branch. Those predate these changes; icon workflow exists separately.
- No production deployment, merge, channel removal, or DVR change.

## Adding a provider
Add an object to `providers` with `id`, `name`, `enabled`, HTTPS `url`, explicit XMLTV-to-Sully `channelMap`, and `rights`. Rights must include `publicRedistribution: true`, `commercialUse: true`, `evidenceUrl`, `reviewedAt`, and required `attribution`. These are review records, not proof on their own: inspect actual provider terms and sample data before enabling. Never use real rights claims for test fixtures.

Next: verify a permitted source with actual channel overlap, then review a separate full-app preview before seeking production approval. Draft review: https://github.com/mblackketter1976-bit/Sully-tv/pull/1 .
