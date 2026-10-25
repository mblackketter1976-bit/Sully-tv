# BLACKKETTER ENTERTAINMENT — START HERE
Version 1.0 — 2026-10-25

## Trigger word: REFERENCE
When the owner types **reference** at the start of a session, treat it as an instruction to:
1. Read THIS file first.
2. Read [the master vision and engineering charter](BLACKKETTER_ENTERTAINMENT_MASTER_VISION.md).
3. Review the latest relevant repository code, change log, and any project-specific reference documents before making recommendations or changes.
4. Give a concise briefing: vision, rules, verified current state, outstanding problems, and the best next action.
5. Ask only for missing information genuinely needed to proceed. Never claim unseen code, media, or files were reviewed.
6. Carry the philosophy into all subsequent work that session; revisit this file before major architectural decisions.
If repository access is unavailable, say so and request the charter contents; do not pretend to have retrieved it.

## The bigger picture
**Blackketter Entertainment** is the proposed parent entertainment and technology company. The goal is a world-class, independent, vertically integrated entertainment ecosystem: original stories and characters; film and animation production; original creative software; streaming and distribution through Sully TV; publishing and intellectual property; eventually games, audio, and other media.

The aspiration is **Pixar 2.0 and beyond**, not a limited Luna animation tool or a hobby streaming site. Luna is the first flagship character and creative quality test; Sully TV is a core distribution product. All work should serve the broader company vision.

## Founding philosophy — do not dilute
> Create the simplest, most reliable experience possible. Investigate why competing products struggle. Find legal, free alternatives. Challenge assumptions, innovate beyond the obvious, and implement the best solution—not merely the first solution.

Expanded rules:
- **No artificial ceiling** on what we plan to build. Don't exclude future professional-grade capabilities just because they are not needed immediately.
- **Build everything essential for long-term independence.** If a necessary capability has no suitable free option, research how to write our own software. Even when third-party tools are available, plan eventual in-house replacements for critical dependencies.
- **Build to be better, not merely similar.** Study existing professional tools, identify weaknesses, and measure actual improvements.
- **No permanent vendor lock-in.** Favor source ownership, documented interfaces, portable formats, reproducible builds, independent backups, and replaceable components.
- **Zero-cost-first.** Use existing hardware and legal free tools; research costs and return before recommending any purchase. Expand equipment only when affordable and beneficial.
- **Ambition plus proof.** Don't mistake experiments, prototypes, rendered stills, effects, or plans for completed production-quality functionality. Clearly label built / tested / deployed / blocked.
- **Never casually discard working work.** Inspect before editing, preserve existing features, regression-test, version changes, and keep recovery options.
- **Design the complete system; implement and test incrementally.** Staged development is not a ceiling on the vision.
- **Professional quality and usability.** The desired response is WOW, not WTF; do not praise poor output or claim success without evidence.
- **Legal and ethical independence.** Respect copyright, licensing, privacy, content rights and redistribution requirements.
- **Make things last.** Think of restoring a rusty car piece by piece into a blue-ribbon show car; preserve every improvement and document how to rebuild it.

## Owner's intent and expectations
The owner will improve the hardware/workshop over time and wants the assistant to research what equipment will help most, find reasonable prices, and avoid unnecessary purchases. The assistant should take concrete action where tools permit, write code and run tests, explain limitations accurately, and not replace action with repeated roadmaps.

## Mandatory build-or-adopt registry (owner directive, 2026-10-25)
**Default question for every component, feature, service, pipeline, and tool:** "Can we build it, and can we build it better?" Begin with **yes as the ambition**, then investigate **how** and prove the result; never claim an untested improvement is already better.

**Before deciding to adopt an existing system or write our own, SEE the existing system.** Inspect its actual user interface, workflows, output, source code/architecture where accessible, documentation, and real behavior. Use demos, screenshots, repository review, or hands-on tests as available; record what was actually observed versus inferred. Do not make the build-versus-adopt decision from a marketing description or guess.

For each significant candidate, add a row/entry in `docs/BUILD_OR_ADOPT_REGISTRY.md` recording:
1. The capability we need and quality target.
2. The existing system(s), links, and whether we actually inspected the interface, source, demos, or live behavior.
3. What works well, what fails, and why users struggle.
4. Legal rights, license, commercial use, cost, privacy, dependencies and lock-in.
5. Whether we can build it better, and **how** (specific design and measurable acceptance tests).
6. Decision: USE THEIRS / EXTEND THEIRS / BUILD OUR OWN / HYBRID / RESEARCH PENDING, with rationale.
7. Prototype, test evidence, performance/quality comparisons, and next review date or trigger.

**Decision gate:** inspect -> compare -> decide -> prototype -> test -> adopt or build. Prefer the simplest reliable, legal, zero-cost solution that achieves superior user experience and long-term independence. Revisit decisions when new evidence emerges. Preserve working systems during comparisons.

## Known projects
- **Sully TV:** existing GitHub Pages streaming project in repository mblackketter1976-bit/Sully-tv. Preserve channels, Michele's Murder Mystery Channel (one 'l'), Luna's YouTube content, language controls, themes, and cross-device experience. Browser-local DVR does NOT continue after browser closure; true background recording requires a legitimate persistent recording service and suitable rights. Preserve working features while improving.
- **Luna Animation / Sully Creative Engine:** professional full-featured 2D/3D modeling, rigging, simulation, rendering, audio/video and editing platform ambition. Luna is a female French bulldog with vivid blue eyes, bright pure-white base coat, light and dark grey merle patches, erect ears, compact build and a not-overly-jowly face. Approved character artwork exists in prior project context but may not be locally available; don't claim access without verification. A convincing articulated walk cycle with planted/lifted paws, weight transfer and consistent appearance is a first quality gate. Previous camera pan, still-image swelling and crude sketch filters were rejected.
- **Publishing/IP:** Luna on the Streets books and future original characters, series, films, games and merchandising.

## Existing work and truthfulness
The master charter was created on the development branch `sully-phase1-foundation-audit` in `docs/BLACKKETTER_ENTERTAINMENT_MASTER_VISION.md`.
The Sully TV live website was not changed by that charter.
Any prototype rig is only a mechanics demonstration until its appearance and animation pass visual tests.
A prior video shared by the owner is a **safety switch** reminding us of the philosophy. Do not invent its transcript; request or inspect it if its exact contents matter.

## Start-of-day briefing format
**Blackketter Entertainment reference loaded.**
**North star:** [one-sentence summary].
**Rules:** [independence, quality, legal free-first, verify, no ceiling].
**Current verified state:** [only verified information].
**Today's best next move:** [specific, actionable task].
**Blocked or unverified:** [anything we cannot confirm].

## Document discipline
This is the stable entry point. Keep it short enough to reread, update it when the owner revises the philosophy, and link deeper records rather than burying important decisions in chat. Never overwrite history without a commit. Back up the repository independently.

## Current two-project handoff
Read `ACTIVE_PROJECTS.md` for the current verified state and review links. Luna studio implementation/evidence lives on `luna-grounded-motion-benchmark`; Sully TV changes live on `sully-phase1-foundation-audit`. A passing contact fixture is not an approved Luna animation; a partial sourced guide is not a complete broadcast schedule.
