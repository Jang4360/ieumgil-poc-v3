# Workstream: Metrics and Learning

## Goal

Make success, failure, and repeated patterns visible enough that the harness can improve instead of repeating the same mistakes.

## Scope

- Clarify success criteria in planning artifacts.
- Keep metrics and learning promotion paths aligned with real usage.
- Ensure dashboard views reflect plan progress and failure patterns credibly.

## Non-goals

- Full analytics system design.
- Long-term performance benchmarking strategy beyond the current harness needs.

## Source Inputs

- Request: make planning and validation precise enough that implementation follows the right direction
- Docs: `.ai/EVALS/metrics.json`, `.ai/PROMOTION.md`, `.ai/EVALS/failure-patterns.md`, `.ai/PLANS/current-sprint.md`
- Code or architecture references: `scripts/update-metrics.sh`, `scripts/dashboard.sh`

## Success Criteria

- [ ] Top-level and per-workstream plans contain explicit success criteria.
- [ ] Dashboard progress is readable from plan checklists instead of only from machine state.
- [ ] Repeated failures can be promoted into durable learnings without ambiguity.

## Implementation Plan

- [ ] Add explicit success-criteria requirements to planning templates and planning skills.
- [ ] Keep dashboard behavior tied to plan checklist state and failure logs.
- [ ] Make learning promotion paths explicit in workflow documents.

## Validation Plan

- [ ] Review whether a future implementer could tell when work is done from the plan alone.
- [ ] Check that the dashboard exposes enough signal to choose the next action.

## Risks and Open Questions

- Metrics may still be too sparse until the real project starts using the harness.
- Overly rigid metrics can distort how teams mark progress.

## Dependencies

- Depends on the planning structure and dashboard structure staying aligned.

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: success criteria and failure visibility must be credible before trusting the harness dashboard
