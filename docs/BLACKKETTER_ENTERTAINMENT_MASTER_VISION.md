# Blackketter Entertainment — Master Vision and Engineering Charter
Version: 0.1 (founding charter, 2026-10-25)
Status: Vision and proposed architecture; not a claim of completed software.
Owner's direction: Build a world-class, independent entertainment and technology company, with Sully TV as one part of the ecosystem.

## North star
Blackketter Entertainment aims to create, produce, publish, and distribute original entertainment using technology it controls. Luna is an early flagship character and production; Sully TV is the streaming and distribution product. The creative toolchain is intended to grow into a comprehensive professional-grade platform, not remain a Luna-specific utility.

## Non-negotiable working philosophy
- Create the simplest, most reliable experience possible.
- Investigate why competitors struggle; study the best techniques and challenge assumptions.
- Find legally free alternatives first. When a needed tool is unavailable for free, investigate building it ourselves.
- No artificial ceiling on the eventual product scope: design for modeling, rigging, 2D/3D animation, physics, compositing, rendering, audio, editing, AI assistance, games, and future capabilities.
- Favor independence and ownership: avoid irreplaceable vendors, proprietary lock-in, and recurring costs.
- Build and verify in stages. Never represent prototypes as finished, untested features as tested, or plans as implementations.
- Preserve working features, source history, original assets, and backups. Do not rebuild from scratch without evidence.
- Aim to surpass competing experiences through measurable quality, reliability, usability, and performance—not slogans.
- Respect copyright, content licenses, trademarks, privacy, and open-source license obligations.
- Spend only when the benefit is demonstrable and affordable; compare real options before purchasing.
- Every release should be something the Blackketter name can stand behind.

## Proposed ecosystem (not established legal subsidiaries)
1. Blackketter Studios — films, animation, series and original productions.
2. Sully Creative Engine / Animation Studio — modeling, rigging, motion, simulation, rendering, compositing, audio/video and extensible authoring tools.
3. Sully TV — discovery, legal streaming, playback, accessibility, distribution and optional personal recording where lawful and technically viable.
4. Publishing and intellectual property — Luna books, characters, stories and merchandise.
5. Future interactive and audio divisions — games, immersive experiences, music and voice production.

## Architecture principles
- Modular components with documented interfaces and interchangeable implementations.
- Open, portable project and media formats; documented migrations and exports.
- Local-first where practical; transparent network and compute requirements.
- Versioned code, assets, build environments, specifications, test fixtures and releases.
- Separate backups from Git version control, including large video, images and project files.
- Security, permissions and legal distribution requirements are design inputs, not afterthoughts.
- Quality gates for visual fidelity, actual motion, accessibility, stability, performance and cross-device operation.

## Current known projects and limitations
### Sully TV
- Existing GitHub Pages/static website in this repository; preserve working channels and features.
- Browser MediaRecorder/IndexedDB recordings are not server-side DVR and cannot reliably continue after the page/browser closes.
- Any persistent DVR must be engineered around actual always-on compute/storage and content permissions; do not claim static hosting alone can do it.
- Guide styling and DVR feasibility work on the development branch must be regression-tested before deployment.

### Luna animation
- Approved Luna appearance: bright pure-white base with light/dark grey merle patches, vivid blue eyes, compact French bulldog proportions.
- Previous camera-pan, image swelling and sketch-filter tests are not acceptable character animation.
- A believable, articulated, consistent walk with actual paw lifts/plants and weight transfer is an early measurable animation quality gate.
- A mechanical rig demonstration is not proof of final art quality.
- Existing desktop hardware and free toolchain are starting resources, not a permanent design ceiling.

## Work order
**Stage 0 — Audit:** inventory repositories, programs, assets, licenses, computer resources, and working/broken functionality. Record evidence.
**Stage 1 — Workshop:** organize repositories, versioning, backup/export practices, issue tracking, reproducible builds, automated smoke tests, and documentation.
**Stage 2 — Architecture:** design a complete expandable engine and media-platform roadmap with interfaces, milestones, and fallback strategies.
**Stage 3 — Proof:** deliver a short, genuinely articulated Luna animation with approved visual fidelity; independently validate Sully TV playback and guide regressions.
**Stage 4 — Expand:** implement broader modeling, rigging, rendering, editing, and distribution features behind tested interfaces; release incrementally.
**Stage 5 — Scale:** only after demonstrable product value, research hardware upgrades, partnerships, commercialization, and legal entity/IP questions.

## Decision and change log
- 2026-10-25: Parent vision named **Blackketter Entertainment**.
- 2026-10-25: Explicit requirement: no artificial ceiling; build complete capabilities for future use, not just immediate needs.
- 2026-10-25: Explicit requirement: reduce permanent dependence on third-party tools and services; build in-house alternatives where feasible.
- 2026-10-25: User's reference video is intended as a safety switch to recover philosophy if conversational context is lost. Its contents have not been independently transcribed or validated here.
- 2026-10-25: Charter created on a development branch; no live site changes implied.

## Rules for the assistant
Before changing software, consult this charter, inspect existing code and assets, and identify a measurable acceptance test. Clearly distinguish built, tested, planned, and blocked work. Never claim a commit is deployed without verifying deployment. Preserve the user's exact Luna design constraints. Update this charter and the decision log when the vision changes.

## Next audit deliverables
- Repository inventory and branch/release map.
- Asset register, licenses and backup status.
- Feature inventory: working / untested / broken / proposed.
- Modular system architecture with dependency map.
- Prioritized test matrix and zero-cost resource plan.
