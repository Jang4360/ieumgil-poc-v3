# Workstream: Project Identity

## Goal

Replace template identity and framing with real project context so later planning and implementation do not target a generic repository.

## Scope

- Update project identity artifacts with real product context.
- Align top-level plan language with the actual project wedge and users.

## Non-goals

- Final product roadmap definition.
- Deep architecture design beyond the current project identity pass.

## Source Inputs

- Request: adopt the harness template into a real repository
- Docs: `.ai/PROJECT.md`, `.ai/ARCHITECTURE.md`, `.ai/WORKFLOW.md`
- Code or architecture references: `README.md`, `AGENTS.md`, `CLAUDE.md`

## Success Criteria

- [ ] `.ai/PROJECT.md` no longer uses the default template identity.
- [ ] The top-level sprint goal reflects the real project instead of generic template adoption.
- [ ] README and host instructions do not contradict the real project framing.

## Implementation Plan

- [ ] Replace the template project name and outcome with real project context.
- [ ] Align any user-facing intro docs with the same product wedge.
- [ ] Update sprint framing if the new project context changes current priorities.

## Validation Plan

- [ ] Review for consistency across project docs and host instructions.
- [ ] Confirm downstream planning can refer to a concrete product and user.

## Risks and Open Questions

- The real primary user and wedge may still be underspecified.
- Project framing may change after the first actual feature plan.

## Dependencies

- The team needs a minimally credible statement of user, wedge, and non-goals.

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: identity docs must be internally consistent before later sprint work depends on them
