# AI Harness Template

This repository is a vendor-neutral starter for AI-assisted software delivery. It is the scaffold itself, not a migration layer, plugin marketplace, or prompt dump.

The template treats `.ai/` as the canonical source of truth for project context, workflow, memory, evaluation, guards, promotion logic, progress state, reusable skills, and runtime adapter templates. Claude- and Codex-specific directories are generated adapters so teams can keep one methodology while supporting multiple hosts.

## Who this is for

- Teams starting a new repository and wanting AI workflow structure on day one.
- Individual builders who want more than ad hoc prompts.
- Maintainers who want planning, review, QA, release, and learning loops captured in versioned files.

## What makes this different from a simple prompt repo

- The workflow is stage-based: Think -> Plan -> Build -> Review -> Test -> Ship -> Reflect.
- Skills are tied to durable artifacts under `.ai/`, not one-off chat output.
- Planning feeds build and QA. Review and QA feed release. Retro feeds memory and evals.
- Guard checks, scoring inputs, and dashboard outputs are repository artifacts rather than hidden chat behavior.
- Adapter directories are generated from one canonical skill set plus canonical adapter templates instead of hand-maintained copies.

## Repository shape

- `.ai/` is canonical.
- `.ai/SKILLS/` contains the reusable methodology skills.
- `.ai/ADAPTERS/` contains canonical runtime adapter templates.
- `.ai/PLANS/progress.json` is the structured progress source.
- `.ai/EVALS/metrics.json` is the structured quality and readiness source.
- `.ai/GUARDS.md`, `.ai/PROMOTION.md`, and `.ai/AUTOMATION.md` describe harness safeguards and automation intent.
- `.claude/skills/` is the Claude-compatible adapter output.
- `.agents/skills/` is the Codex-compatible adapter output.
- `.codex/` contains safe repo-local Codex placeholders.
- `scripts/sync-adapters.sh` rebuilds skills and runtime adapter files from `.ai/`.
- `scripts/verify.sh` checks structure, skill contract sections, and adapter sync.
- `scripts/dashboard.sh` renders a repository-state summary from structured artifacts.
- `scripts/codex-preflight.sh` prints the Codex session-start summary for guards, progress, and review routing.
- `scripts/codex-review-brief.sh` prints a Claude-ready review handoff from the current Codex workspace state.
- `scripts/check-plan-readiness.sh` checks whether a planning artifact is executable enough for build, review, and QA handoff.
- `scripts/check-tdd-guard.sh`, `scripts/check-dangerous-command.sh`, and `scripts/check-circuit-breaker.sh` provide harness guard entrypoints.
- `scripts/update-metrics.sh` recomputes derived quality signals from canonical state.
- `scripts/pipeline-check.sh` runs the default local verification pipeline.

## Quick start

1. Clone the repository and create a new git remote for your project.
2. Read `.ai/PROJECT.md`, `.ai/ARCHITECTURE.md`, and `.ai/WORKFLOW.md`.
3. Run `scripts/bootstrap-template.sh "Your Project Name"` to set a first-pass project identity.
4. Customize project-specific commands in `scripts/smoke.sh`, `.ai/RUNBOOKS/local-setup.md`, `.ai/RUNBOOKS/release.md`, `.ai/RUNBOOKS/rollback.md`, and `.ai/ADAPTERS/codex/hooks.json`.
5. Edit or add canonical skills under `.ai/SKILLS/`.
6. Update `.ai/PLANS/progress.json` and `.ai/EVALS/metrics.json` so progress and quality are externally visible.
7. Run `scripts/sync-adapters.sh`.
8. Run `scripts/check-plan-readiness.sh` after plan refinement work.
9. Run `scripts/verify.sh`.
10. Run `scripts/dashboard.sh`.

## Using it with Codex

- Codex reads `AGENTS.md` for repository instructions.
- Codex discovers repo skills from `.agents/skills/`.
- Canonical changes should still be made under `.ai/SKILLS/`, then synced.
- Repo-local Codex adapter templates live in `.ai/ADAPTERS/codex/` and generate `.codex/config.toml` plus `.codex/hooks.json`.
- The generated Codex hook is intentionally minimal: it runs a session-start preflight that points implementation work back to the guard scripts, dashboard state, and Claude review path.
- Primary enforcement for Codex remains `AGENTS.md`, `.agents/skills/`, and the guard scripts themselves.
- `.codex/*` placeholders are generated from `.ai/ADAPTERS/codex/`.

## Using it with Claude Code

- Claude Code reads `CLAUDE.md` for project instructions.
- Claude discovers skills from `.claude/skills/`.
- Claude memory discipline is mirrored in `.ai/MEMORY/` so the methodology stays repo-native.
- Canonical changes still belong in `.ai/SKILLS/`, then sync regenerates the Claude adapter.
- Claude-facing workflows should still use the canonical progress, metrics, and promotion artifacts under `.ai/`.
- `.claude/settings.json` is generated from `.ai/ADAPTERS/claude/settings.json`.

## Skill authoring contract

Every canonical skill directory contains `SKILL.md` and may optionally include `notes.md` or deterministic helpers under `scripts/`.

Every `SKILL.md` in this template includes:

- `name`
- `description`
- `purpose`
- `when to use`
- `inputs`
- `procedure`
- `outputs`
- `escalation rules`
- `handoff rules`

## Methodology extension

Extend the methodology by changing the canonical sources first:

1. Update `.ai/WORKFLOW.md` if the stage contract changes.
2. Update `.ai/EVALS/` if done criteria or score logic changes.
3. Update `.ai/MEMORY/` or `.ai/DECISIONS/` if the change should persist across sprints.
4. Update or add canonical skills under `.ai/SKILLS/`.
5. Run `scripts/sync-adapters.sh` and `scripts/verify.sh`.

## Generated versus canonical

- Canonical: everything under `.ai/`
- Generated: `.claude/skills/` and `.agents/skills/`
- Generated runtime adapters: `.codex/config.toml` and `.codex/hooks.json`

Treat generated adapters as rebuildable views over the canonical skill set.
