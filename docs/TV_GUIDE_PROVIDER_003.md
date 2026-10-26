# First licensed schedule candidate — TVmaze, 2026-10-25

## Source inspection and decision
Inspected TVmaze's official public API documentation, schedule response, licensing section and linked CC BY-SA 4.0 deed:
- https://www.tvmaze.com/api
- https://creativecommons.org/licenses/by-sa/4.0/

The API permits reuse for any purpose subject to attribution and ShareAlike. The derived TVmaze schedule dataset is offered under CC BY-SA 4.0, credits TVmaze, links the license and explains the transformations (`data/TV_GUIDE_LICENSE.md`). No posters, summaries or show artwork are copied by this adapter. These rights concern schedule data; they do not establish playback/rebroadcast rights.

Decision: extend the provider architecture with a bounded TVmaze adapter. Do not treat this as a complete XMLTV replacement. No paid service or API key.

## Directly checked mapping
Compared actual TVmaze network ID, exact network name and country with current iptv-org channel identity metadata. Confirmed existing stream metadata entries for the same channel IDs. Did not verify that a particular stream is currently airing the listed episode.

| TVmaze ID/name | Sully channel ID | Scope |
| --- | --- | --- |
| 40 / CNN / US | CNN.us | US network, not CNN International or Originals |
| 201 / MS NOW / US | MSNOW.us | Current exact network name; no guessing from similar names |
| 467 / BYUtv / US | BYUTV.us | US channel, not Global or Latin America |

Do not copy these mappings to local affiliates, FAST spinoffs, delayed feeds or unrelated similarly named channels. Expand only after identity, schedule timing and coverage inspection.

## Real fetch evidence
Four requests for UTC date offsets -1 through +2, with country US, yielded 40 future/in-progress episode entries across 3 channels after normalization, duplicate/overlap filtering and expiry filtering. Snapshot: `data/tv-guide.json` on development branch. Counts are a dated observation, not a guaranteed minimum.

Each entry uses TVmaze's explicit timezone-bearing airstamp and episode runtime. Missing timezones/runtimes are skipped. No inferred reruns or gap filling. The dataset includes source episode URLs, attribution and license metadata. The UI calls these sourced/partial episode listings and warns that actual stream feeds may differ.

## Validation and limits
Local Python suite: 25 tests passed (original guide 19, 5 TVmaze tests and bounded-retry test). Inline JavaScript syntax passed. Browser verification subsequently passed (see confirmed results below); assertions cover two short shows sharing a half-hour cell and visible TVmaze/license links.

The updater writes a candidate locally and Actions retains it for review. It does not publish data to the live branch or deploy the website. Full-app playback and actual device tests remain outstanding.

## Confirmed integration results
GitHub Actions run https://github.com/mblackketter1976-bit/Sully-tv/actions/runs/40242497404 passed Python, isolated guide checks and complete HTML startup/navigation at 1280px and 390px. The full-page test uses controlled channel metadata and the real fetched guide candidate; it does not decode streams. Screenshots were inspected: source/license links and explicit episode times are visible, with horizontal scrolling contained within the grid. Existing floating navigation can overlap portions of the viewport; no platform-wide navigation redesign was attempted in this change.

Generated the three previously missing app PNG icons from the existing approved banner, using the repository's existing icon workflow crop. Static integrity now passes with zero errors; the existing external CDN dependency remains a warning. This is not an actual Android/iOS installation test.

## Zero-cost refresh and current-data export
A static deployment of the seed snapshot alone would become stale. `guide-source.js` now refreshes the reviewed TVmaze networks directly from the documented CORS-enabled public API when the guide is open and its data are older than one hour. A one-minute active-guide check evaluates expiry; only stale data trigger requests. Four bounded daily requests cover date offsets -1 through +2. The source uses bounded response reading, timeouts and bounded 429/5xx retries. Fresh cache prevents additional requests; a failed or empty refresh preserves the last usable data. Existing freshness rules still hide data older than 36 hours.

The refreshed dataset is cached locally. Opening other rooms does not start guide-source requests. The current dataset, attribution and CC BY-SA metadata can be downloaded through the visible "Download current listings" control. No paid backend, scheduled live-site publishing or new account is needed. The existing updater workflow remains a candidate-generation/check path.

Run https://github.com/mblackketter1976-bit/Sully-tv/actions/runs/40243454864 passed the Python suite, browser-source tests, isolated guide tests and full-page desktop/phone tests. Full-page assertions cover an automatic-source refresh with controlled API responses, four-request bounds, fresh-cache suppression, keeping last-good data after network failure, and downloading the refreshed dataset. Real API fetching was separately verified by the Python candidate fetch. No real-stream decoding, actual Android/iOS installation, or Safari testing is claimed.
