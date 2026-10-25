# Blackketter Entertainment — Build or Adopt Registry
Owner directive: **Can we build it, and can we build it better? Start from YES; prove the HOW.**

## Required process
1. **SEE IT:** inspect the competing/existing system's actual UI, demo, workflows, behavior, documentation, and source/architecture when available. Mark unobserved claims as unverified.
2. **UNDERSTAND IT:** identify strengths, pain points, costs, licensing, dependencies, and causes of failure.
3. **CHALLENGE IT:** sketch a simpler/better design with measurable quality criteria.
4. **DECIDE:** USE / EXTEND / BUILD / HYBRID / RESEARCH PENDING.
5. **PROVE IT:** test prototypes against the existing system; retain the option to revise.

No blind adoption; no reflexive rewrite. Do not call our product better without evidence.

## Entry template
- **ID / Capability / Owner / Date:**
- **Existing systems and links:**
- **Observed directly (UI, demo, code, tests):**
- **Not yet observed:**
- **What they do well:**
- **Where they struggle and why:**
- **Licensing, rights, cost, privacy, lock-in:**
- **Can we build it? How would ours be better?:**
- **Measurable comparison / acceptance criteria:**
- **Decision and rationale:**
- **Implementation status and test evidence:**
- **Next review trigger:**

## Registry entries

### BA-001 — TV schedule guide engine — 2026-10-25
- **Existing systems:** iptv-org/api (https://github.com/iptv-org/api); iptv-org/epg (https://github.com/iptv-org/epg); XMLTV (https://github.com/XMLTV/xmltv); EPGTalk (https://github.com/acidjesuz/EPGTalk).
- **Observed directly:** our existing workflow behavior through GitHub Actions logs; 180,678 guide records, 15,503 matched live channel IDs, 0 populated `sources` records. Our own source script and workflow inspected. The new offline engine files are committed but not yet executed.
- **Not yet observed:** competitor UIs or working EPG feeds hands-on; comparative tests; production redistribution rights; actual licensed feed channel coverage.
- **Strengths:** existing ecosystem has guide schemas, collection utilities and channel metadata.
- **Struggles:** our integration incorrectly assumed that metadata supplies XMLTV URLs; missing-source handling yielded empty schedules.
- **Legal/cost/lock-in:** tools can be open-source while schedule data rights remain restricted; verify permissions before any production feed use. No paid dependencies.
- **Build it / improve it:** independent small XMLTV parser, explicit verified channel mapping, source provenance, provider adapters, graceful no-guide state, offline tests.
- **Acceptance criteria:** synthetic tests pass; no fabricated listings; channel playback unaffected; source licensing verified; real matched-channel coverage measured; fallback behavior tested.
- **Decision:** HYBRID — build our own normalization and reliability layer; adopt legally authorized data sources and standards where appropriate.
- **Status:** source and six offline tests committed; six tests executed locally on a matching copy and passed on 2026-10-25; GitHub Actions CI result not yet confirmed; no live deployment.
- **Next review:** after test execution and first verified authorized provider evaluation.

### BA-002 — Sully TV streaming interface — 2026-10-25
- **Existing systems:** Netflix and Roku, among others.
- **Observed directly:** Sully TV's own GitHub project and user screenshots; no verified hands-on competitor UI review in this registry yet.
- **Not yet observed:** structured Netflix/Roku feature walkthrough and quantified comparison.
- **Decision:** RESEARCH PENDING. Capture actual UI and user journeys before adopting design patterns or rewriting major components.
- **Next review:** before next major navigation or architecture redesign.
