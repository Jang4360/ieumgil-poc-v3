# Workstream: Commands and Runbooks

## Goal

Replace template placeholders for smoke, release, and rollback with real project commands and operating steps.

## Scope

- Configure `scripts/smoke.sh`.
- Update release and rollback runbooks.
- Align related setup instructions if needed.

## Non-goals

- Full CI pipeline design.
- Production deployment automation beyond documented commands.

## Source Inputs

- Request: make the harness operational in a real repository
- Docs: `.ai/RUNBOOKS/local-setup.md`, `.ai/RUNBOOKS/release.md`, `.ai/RUNBOOKS/rollback.md`, `README.md`
- Code or architecture references: `scripts/smoke.sh`

## Success Criteria

- [ ] `scripts/smoke.sh` runs a real project-specific smoke command.
- [ ] Release runbook no longer contains `TODO(project)` placeholders.
- [ ] Rollback runbook no longer contains `TODO(project)` placeholders.

## Implementation Plan

- [ ] Choose the minimum high-signal smoke command for the project.
- [ ] Document the real release command sequence.
- [ ] Document the real rollback command sequence.

## Validation Plan

- [ ] Review whether the commands are actionable and realistic.
- [ ] Run `scripts/smoke.sh` once the smoke command is configured.

## Risks and Open Questions

- The project may not yet have a stable smoke command.
- Release or rollback authority may live outside the repository.

## Dependencies

- Requires the project stack and command entrypoints to be known.

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: smoke, release, and rollback commands must be defined before calling the harness operational
