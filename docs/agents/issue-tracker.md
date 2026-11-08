# Issue tracker: Local Markdown

This repo has no git remote. Issues, specs and the planning map live as markdown files.

## Two layouts

- **Wayfinder (planning, already exists)**: `docs/wayfinder/`
  - Map: `docs/wayfinder/map.md`
  - Child tickets: `docs/wayfinder/tickets/NN-slug.md`, numbered from `01`. The header block holds `title`, `label` (`wayfinder:<type>`), `status` (`open`/`closed`), `blocked_by` (list of ticket file names without `.md`), `assignee` (the claim).
  - A ticket is resolved by appending a `## Resolution` section, setting `status: closed`, then adding a one-line pointer to the map's Decisions so far.
  - Research findings: `docs/wayfinder/research/NN-slug.md`.
  - Do not renumber or rename these files.
- **Build issues (new work)**: `.scratch/<feature-slug>/`
  - The spec for a feature is `.scratch/<feature-slug>/spec.md`. The overall project spec is `docs/spec.md`.
  - Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file.
  - Triage state is a `Status:` line near the top of each issue file (see `triage-labels.md`).
  - Comments and conversation history append to the bottom under a `## Comments` heading.

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed). For wayfinder, add a ticket file under `docs/wayfinder/tickets/` with the next number.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/wayfinder`. The map already exists, so new decision tickets go in the wayfinder layout above.

- **Map**: `docs/wayfinder/map.md` (Destination / Notes / Decisions so far / Open tickets / Not yet specified / Out of scope).
- **Child ticket**: `docs/wayfinder/tickets/NN-slug.md` with the question in the body.
- **Blocking**: the `blocked_by` header list. A ticket is unblocked when every file it lists has `status: closed`.
- **Frontier**: tickets with `status: open`, an empty `assignee`, and no open blocker; first by number wins.
- **Claim**: set `assignee` and save before any work.
- **Resolve**: append `## Resolution`, set `status: closed`, add a pointer to the map's Decisions so far.
