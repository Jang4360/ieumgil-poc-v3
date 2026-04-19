# Architecture

## Canonical layers

- `.ai/` is the methodology and project-operations layer.
- `.ai/SKILLS/` is the canonical workflow layer.
- `.ai/ADAPTERS/` is the canonical runtime-adapter template layer.
- `.ai/PLANS/progress.json` is the canonical structured progress layer.
- `.ai/EVALS/metrics.json` plus promotion and retry logs are the canonical measurable state layer.
- `.ai/GUARDS.md`, `.ai/PROMOTION.md`, and `.ai/AUTOMATION.md` define harness control behavior.
- `.claude/skills/` is the Claude adapter layer generated from canonical skills.
- `.agents/skills/` is the Codex adapter layer generated from canonical skills.
- `.codex/` holds repo-local Codex configuration placeholders.
- `scripts/` holds deterministic repository helpers for sync, verification, smoke checks, guards, scoring, dashboard views, and bootstrap.

## Design intent

This template keeps one source of truth and three generated compatibility surfaces. It does not split the repository into a syncable core and a separate scaffold. The repository itself is the scaffold.

## Data flow

1. A request or event is classified against the current sprint and workflow.
2. Humans or agents update canonical docs and canonical skills under `.ai/`.
3. Planning and implementation update narrative plan artifacts plus `.ai/PLANS/progress.json`.
4. Evaluation and release update `.ai/EVALS/metrics.json` and related logs.
5. Promotion decisions update `.ai/MEMORY/`, `.ai/SKILLS/`, `.ai/EVALS/`, or `.ai/DECISIONS/`.
6. `scripts/sync-adapters.sh` copies canonical skills and adapter templates into `.claude/`, `.agents/`, and `.codex/`.
7. Claude uses `.claude/skills/` with `CLAUDE.md` and generated `.claude/settings.json`.
8. Codex uses `.agents/skills/`, `AGENTS.md`, and generated `.codex/` placeholders.
9. `scripts/dashboard.sh` turns canonical progress, metrics, and promotion state into a visible status summary.

## Change policy

- Change canonical skill behavior only under `.ai/SKILLS/`.
- Change host instructions in `AGENTS.md` and `CLAUDE.md`.
- Add new deterministic scripts only when markdown instructions are not enough.
