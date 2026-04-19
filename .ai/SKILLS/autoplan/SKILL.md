---
name: autoplan
description: Run a full planning pass by consolidating problem framing, product scope review, engineering review, and design review into one reusable sprint artifact.
---

# autoplan

## purpose

Produce a complete plan packet without skipping the Think or Plan stages.

## when to use

- When a new task needs a full reviewed plan
- When the team wants one command-shaped planning entrypoint
- When downstream build and QA need structured artifacts immediately

## inputs

- Raw task request
- `.ai/PROJECT.md`
- `.ai/ARCHITECTURE.md`
- `.ai/WORKFLOW.md`

## procedure

1. Run the intent of `office-hours`.
2. Run the intent of `plan-ceo-review`.
3. Run the intent of `plan-eng-review`.
4. Run the intent of `plan-design-review` when the work is user-facing.
5. Consolidate the approved result in `.ai/PLANS/current-sprint.md` or a linked plan artifact under `.ai/PLANS/`.
6. Run `scripts/check-plan-readiness.sh` and close plan gaps that do not require external confirmation.

## outputs

- Single reviewed sprint plan
- Explicit scope, architecture, risk, and UX expectations
- Ready-to-build artifact with review and QA handoff sections

## escalation rules

- Escalate if the request is too ambiguous to survive a combined planning pass.
- Escalate if the plan reveals unresolved product ownership or technical feasibility questions.

## handoff rules

- Hand off to `implement-feature`, `fix-bug`, or another build skill with the consolidated plan as the brief.
