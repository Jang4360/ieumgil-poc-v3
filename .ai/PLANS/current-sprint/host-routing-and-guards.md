# Workstream: Host Routing and Guards

## Goal

Make planning, implementation, validation, and retry handling behave consistently across AI hosts while keeping guard behavior explicit.

## Scope

- Review host-neutral workflow rules.
- Confirm guard and handoff expectations match actual usage.
- Tighten planning and validation entrypoints where needed.

## Non-goals

- Vendor-specific deep hook integrations not supported by the current runtime.
- Replacing human judgment with hidden automation.

## Source Inputs

- Request: improve harness behavior across planning, implementation, and validation stages
- Docs: `AGENTS.md`, `CLAUDE.md`, `.ai/AUTOMATION.md`, `.ai/GUARDS.md`
- Code or architecture references: `scripts/record-retry.sh`, `scripts/review-brief.sh`, `scripts/dashboard.sh`

## Success Criteria

- [ ] Host instructions do not hard-code stage ownership to a single AI host.
- [ ] Retry handling and escalation into `learn` are explicit in the workflow.
- [ ] Cross-host validation routing is documented and works through canonical skills.

## Implementation Plan

- [ ] Review host instruction surfaces for vendor-specific assumptions.
- [ ] Tighten workflow or skill wording where escalation is too manual.
- [ ] Keep cross-host handoff optional rather than the default path.

## Validation Plan

- [ ] Check that `deliver-change` and `validate-change` describe the intended behavior clearly.
- [ ] Check that dashboard or preflight surfaces the most important next action.

## Risks and Open Questions

- Some runtimes may still lack hooks strong enough for full enforcement.
- Over-automation could hide too much planning intent from the operator.

## Dependencies

- Depends on canonical skills and scripts staying in sync.

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: host-specific surfaces must stay subordinate to canonical `.ai/` policy
