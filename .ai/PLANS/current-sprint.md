# Current Sprint

## Goal

Adopt the template into a real repository while preserving the end-to-end loop.

## Source Documents

- Narrative plan: this file
- Active implementation plan: `.ai/PLANS/2026-04-19_ieumgil-accessible-routing-implementation-plan.md`
- Machine-readable progress: `.ai/PLANS/progress.json`
- Quality and readiness metrics: `.ai/EVALS/metrics.json`
- Reusable planning template: `.ai/PLANS/implementation-plan-template.md`

## Problem List

- The template still contains project-agnostic placeholders that a real repository must close.
- Codex and Claude host behavior must stay thin while `.ai/` remains canonical.
- A real project needs execution-ready planning artifacts, not just narrative task lists.

## Architecture And Data Flow

- Canonical methodology and skills live under `.ai/`.
- `scripts/sync-adapters.sh` generates `.claude/skills/`, `.agents/skills/`, and runtime adapter files.
- Guard, scoring, promotion, and dashboard scripts read canonical `.ai/` artifacts.
- Codex and Claude consume generated adapters plus root guidance files.

## Execution Units

### HARNESS-1 Customize project identity

- Inputs: `.ai/PROJECT.md`, README, public repo metadata
- Build steps: replace template identity and project wedge placeholders
- Review focus: identity consistency across docs
- QA path: `scripts/verify.sh`
- Done criteria: default identity placeholders are removed

### HARNESS-2 Customize smoke and runbooks

- Inputs: `.ai/RUNBOOKS/`, `scripts/smoke.sh`
- Build steps: replace TODO command slots with project-specific commands
- Review focus: command realism and operator clarity
- QA path: `scripts/smoke.sh`, runbook spot-check
- Done criteria: setup, release, rollback, and smoke commands are executable or intentionally stubbed with rationale

### HARNESS-3 Wire host-specific guard behavior

- Inputs: `.ai/ADAPTERS/`, guard scripts, runtime needs
- Build steps: connect only the necessary host-specific hooks and preflight paths
- Review focus: safety, determinism, and minimalism
- QA path: `scripts/pipeline-check.sh`, hook simulations
- Done criteria: chosen host guard flow is documented and tested

### HARNESS-4 Record real metrics

- Inputs: `.ai/EVALS/metrics.json`, first real project runs
- Build steps: replace template null metrics with observed values and update score interpretation
- Review focus: metric meaning and signal quality
- QA path: `scripts/dashboard.sh`, `scripts/score.sh`
- Done criteria: quality metrics reflect real usage rather than template defaults

### HARNESS-5 Capture first durable learnings

- Inputs: retry log, promotion log, early project failures
- Build steps: promote at least one recurring pattern into MEMORY, SKILL, EVAL, or ADR
- Review focus: whether the promoted lesson is durable and specific
- QA path: `scripts/dashboard.sh`, artifact inspection
- Done criteria: the harness improved itself with at least one real project learning

## Test And Validation Matrix

- Structure validation: `scripts/verify.sh`
- Adapter sync validation: `scripts/sync-adapters.sh`
- Pipeline validation: `scripts/pipeline-check.sh`
- Guard validation: dangerous command, TDD guard, and circuit breaker script checks
- Runtime validation: Codex preflight and Claude review handoff scripts
- Smoke validation: `scripts/smoke.sh` after project commands are customized

## Risk Register

- Risk: teams may treat generated adapters as editable sources.
  Mitigation now: keep `.ai/ADAPTERS/` explicit and verify sync.
  Open remainder: real project adoption discipline still depends on usage.
- Risk: host runtimes may differ in hook capability.
  Mitigation now: keep actual enforcement in scripts and instructions, use runtime hooks only as thin adapters.
  Open remainder: stronger runtime integration depends on stable host support.
- Risk: planning may stop at analysis without producing execution-ready artifacts.
  Mitigation now: strengthen `plan-eng-review`, add template, add readiness check.
  Open remainder: real project teams must actually run the readiness check.

## Review Handoff

- Reviewers should inspect whether canonical versus generated boundaries are preserved.
- Reviewers should confirm the execution units, done criteria, and risk handling match the requested workflow.
- Review should challenge any plan artifact that only lists gaps instead of converting them into work, tests, or explicit blockers.

## QA Handoff

- QA should verify the guard scripts, dashboard visibility, and score outputs against the documented workflow.
- QA should fail the stage if project-specific smoke and runbook commands remain placeholders without rationale.
- QA should confirm that planning artifacts are actionable enough for build, review, and release.

## Open Questions

- Which host runtime features are stable enough to justify stronger automatic enforcement?
- Which additional machine-readable plan fields are worth formalizing after real project adoption?
