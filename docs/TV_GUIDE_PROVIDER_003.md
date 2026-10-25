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
Local Python suite: 25 tests passed (original guide 19, 5 TVmaze tests and bounded-retry test). Inline JavaScript syntax passed. Browser verification for this revision remains pending until Actions completes; new assertions cover two short shows sharing a half-hour cell and visible TVmaze/license links.

The updater writes a candidate locally and Actions retains it for review. It does not publish data to the live branch or deploy the website. Full-app playback and actual device tests remain outstanding.
