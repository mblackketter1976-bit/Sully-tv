# Sully TV — active action plan

Updated 2026-10-30. Luna cartoon production is paused at the owner's request.

## Direction
Improve the existing GitHub Pages app. Preserve channels, themes, Kids TV,
language controls, favorites, Luna content and Michele's Murder Mystery Channel.
Use legal free tools and hosting. Verify behavior before scaling. A listed URL
is not proof of playable media. Official provider guides may describe paid access;
never label them as free live streams.

## Stage 1: Sports & Local release
Bring the focused feature from draft PR #5 onto current main; do not merge the
entire older foundation branch over newer live code/data. Cover Sacramento
(Kings, River Cats, Republic FC, Athletics) and Bay Area (Warriors, Giants,
49ers, Sharks). Offer official schedule and broadcast-guide links, region/team
filtering, saved choices, clear external-link labels and visible keyboard focus.
No subscription, paid API, scraped schedule or invented live-game availability.

Acceptance: all four regional teams; single-team filtering; incompatible team
reset on region change; selection retained after navigation; HTTPS official
links with safe new-tab behavior; 44px targets; no horizontal page overflow;
existing navigation/theme/back/home checks at 320, 390, 768 and 1920 pixels.

## Following stages
1. Repair the fresh-program-guide pipeline. Current main has an empty guide.
   Inspect the existing guide work on sully-phase1-foundation-audit, license
   attribution and workflow failures before adopting it. Display only fresh,
   sourced programs, including honest empty/failure states.
2. Audit live playback and legal catalog discovery. Confirm actual media
   playback, not just HTTP status; handle failed sources and stale entries.
3. Expand verified legal catalog coverage and real-device testing. Android,
   iPhone and TV hardware checks remain necessary; browser emulation alone
   does not verify them.

## Verification boundaries
Browser preview confirmed team filtering, region reset, saved preference after
Home/Guide navigation and keyboard focus. Inline script syntax checked locally.
The navigation CI includes Sports & Local assertions at four widths.
Official sources inspected: Republic FC broadcast page; MiLB streaming page;
49ers ways-to-watch; Giants watch guide; Sharks broadcast page; NBA Tap to Watch.
NBC pages were search-indexed but direct retrieval returned 403: neither a
working player nor current free access is verified there. Sports links lead to
information pages; no full-game media playback has been verified.

## Existing master reference
The broader charter remains in docs/REFERENCE_START_HERE.md on branch
sully-phase1-foundation-audit. This file records the current STV work on main
without importing unfinished Luna/guide work from that branch.

## Release evidence — 2026-10-30
Sports & Local merged as PR #6. GitHub Pages deployment succeeded. Navigation
and sports assertions passed at 320, 390, 768 and 1920px, across three themes.

Library discovery repair: failed workflow 41153744853 showed a NameError for
missing genres_for. Added conservative source-text tags, corrected license
whitespace/title-extension matching and JSON newline output. Fixture tests cover
readable output, attribution/license handling, rejecting unsupported licenses,
existing entry preservation, deduplication on repeat runs and upstream failure.
These tests do not establish media playback or third-party rights clearance.

The repaired discovery workflow completed successfully and found 60 new entries
(239 catalog records total). Those 60 records are pending-playback and excluded
by the existing verified-only UI filters. Both Commons importers now use that
state for new entries; source metadata dates are separate from playback checks.
Existing pre-release records are preserved; their playback audit remains open.
