# Automation

## Purpose

Describe the intended harness automation pipeline without binding the repository to one vendor runtime.

## Pipeline

request or event -> classification -> doc and skill loading -> planning -> implementation -> evaluation -> risk summary -> promotion -> scoring -> dashboard update

## What is automated now

The following steps run without manual intervention when hooks are wired:

- **Dangerous command guard**: `scripts/hook-pre-bash.sh` intercepts every Bash tool call via Claude Code `PreToolUse` hook (`.claude/settings.json`) and blocks destructive commands before execution.
- **TDD guard**: `scripts/hook-pre-edit.sh` intercepts every Edit/Write tool call via Claude Code `PreToolUse` hook and blocks production edits when no related test changes exist. `scripts/hook-post-edit.sh` remains as a post-edit audit.
- **Codex session preflight**: `.codex/hooks.json` wires a minimal `SessionStart` command that runs `scripts/codex-preflight.sh` to surface guard commands, progress state, repeated-failure warnings, and Claude review routing. It is advisory, not a replacement for tool-level blocking.
- **Adapter sync**: `scripts/sync-adapters.sh` copies canonical skills and runtime adapter templates into `.claude/`, `.agents/`, and `.codex/`; call this explicitly after canonical skill or adapter-template changes.
- **Progress recompute**: `scripts/update-progress.sh` recomputes summary counts from items array; call after changing item statuses.
- **Metrics recompute**: `scripts/update-metrics.sh` recomputes derived retry, blocker, and health signals from canonical state.

## What requires human or agent action

- **Circuit breaker**: `scripts/check-circuit-breaker.sh` must be called with a failure signature before retrying a known-failing approach. When `scripts/dashboard.sh` surfaces a hot cluster, invoke the `learn` skill.
- **Retry logging**: Call `scripts/record-retry.sh` when an approach fails so the circuit breaker can detect accumulation. This also refreshes derived metrics.
- **Promotion**: Call `scripts/record-promotion.sh` when a pattern is ready to be promoted. Invoke the `learn` skill to choose the right destination. This also refreshes derived metrics.
- **Scoring**: Call `scripts/score.sh` to get a readiness snapshot. Update `.ai/EVALS/metrics.json` after real sprint usage.
- **Dashboard**: Call `scripts/dashboard.sh` to surface progress, blocked work, quality metrics, and retry clusters.
- **Review handoff**: Call `scripts/codex-review-brief.sh` when implementation happens in Codex and review happens in Claude.

## Static versus automated

- Static canonical assets: `.ai/PROJECT.md`, `.ai/ARCHITECTURE.md`, `.ai/WORKFLOW.md`, `.ai/GUARDS.md`, `.ai/PROMOTION.md`, runbooks, skills
- Structured mutable assets: `.ai/PLANS/progress.json`, `.ai/EVALS/metrics.json`, `.ai/EVALS/promotion-log.jsonl`, `.ai/EVALS/retry-log.jsonl`
- Hook-automated enforcement: dangerous command guard, TDD guard (wired in `.claude/settings.json`)
- Hook-automated reminders: Codex `SessionStart` guard reminder (wired in `.codex/hooks.json`)
- Generated outputs: `.claude/skills/`, `.agents/skills/`, `.claude/settings.json`, `.agents/README.md`, `.codex/config.toml`, `.codex/hooks.json`, `.codex/README.md`

## Self-reinforcing loop

The harness improves over time through this path:

1. A failure is logged via `scripts/record-retry.sh`.
2. Repeated failures accumulate in `retry-log.jsonl` under the same signature.
3. `scripts/dashboard.sh` detects hot clusters (>=3 occurrences in 24h) and surfaces them.
4. The agent or operator invokes the `learn` skill with the cluster context.
5. `learn` selects the right canonical destination: MEMORY, SKILL, EVAL, or ADR.
6. The pattern is promoted and `scripts/record-promotion.sh` logs the event.
7. Future sessions inherit the compressed knowledge from the canonical artifact.

## Rule

Automation should read and update canonical artifacts. It should not create a parallel hidden state system.
