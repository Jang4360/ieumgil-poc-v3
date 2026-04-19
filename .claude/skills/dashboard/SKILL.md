---
name: dashboard
description: Summarize current progress, risk, promotion activity, and harness health from canonical structured artifacts.
---

# dashboard

## purpose

Make repository progress and harness quality state visible without relying on chat memory.

## when to use

- When you need an immediate status view of work, risk, and harness health
- Before ship or retro
- When deciding what to do next

## inputs

- `.ai/PLANS/progress.json`
- `.ai/EVALS/metrics.json`
- `.ai/EVALS/promotion-log.jsonl`
- `.ai/PLANS/current-sprint.md`

## procedure

1. Read the structured progress and metric artifacts.
2. Summarize totals, in-progress work, blocked work, quality signals, and recent promotions.
3. Surface the most important remaining risks and next actions.
4. If the dashboard reveals stale state, update the canonical artifacts before relying on the summary.

## outputs

- Current progress summary
- Risk summary
- Harness health summary
- Recommended next actions

## escalation rules

- Escalate if progress or metrics artifacts are stale or contradictory.
- Escalate if the dashboard exposes blockers with no owner or next step.

## handoff rules

- Hand off to the next stage skill based on the top unresolved risk or next planned item.
