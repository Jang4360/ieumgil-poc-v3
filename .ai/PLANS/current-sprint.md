# Current Sprint

## Goal

템플릿을 실제 저장소에 적용하면서 엔드투엔드 워크플로를 유지한다.

## Request Mode

- Primary mode: command-driven repository improvement
- Secondary inputs: canonical `.ai/` docs
- Default docs rule: if `docs/` exists, planning should read relevant specs there first and then fall back to `.ai/`, code, and runbooks

## Structured state

- Narrative plan: this file
- Machine-readable progress: `.ai/PLANS/progress.json`
- Quality and readiness metrics: `.ai/EVALS/metrics.json`
- Workstream subplans: `.ai/PLANS/current-sprint/`

## Checklist Status Rule

- `[ ]` not started
- `[~]` in progress
- `[x]` completed successfully
- `[!]` failed, blocked, or requires strategy change

## Planning Inputs

- User request or command
- Relevant files under `docs/` when they exist
- `.ai/PROJECT.md`
- `.ai/ARCHITECTURE.md`
- `.ai/WORKFLOW.md`
- Existing backlog, roadmap, ADRs, incidents, and runbooks when relevant

## Success Criteria

- [ ] 상위 스프린트 문서는 목표, 성공 기준, 작업 분해, 리스크를 분명히 보여준다.
- [ ] 의미 있는 작업 단위마다 별도 세부 계획 파일이 존재한다.
- [ ] 각 세부 계획 파일은 구현과 검증 스킬이 바로 사용할 수 있는 성공 기준과 검증 계획을 담고 있다.
- [ ] 계획은 `docs/` 명세가 있으면 이를 우선 입력으로 삼고, 없으면 요청과 코드 구조를 기준으로 작업을 분해한다.

## Workstream Index

- [ ] [project-identity.md](.ai/PLANS/current-sprint/project-identity.md) — 템플릿 기본값을 실제 프로젝트 정체성으로 교체
- [ ] [commands-and-runbooks.md](.ai/PLANS/current-sprint/commands-and-runbooks.md) — smoke·release·rollback 명령을 실제 프로젝트 기준으로 정의
- [ ] [host-routing-and-guards.md](.ai/PLANS/current-sprint/host-routing-and-guards.md) — 호스트별 가드·훅 라우팅 확인 및 설정
- [ ] [metrics-and-learning.md](.ai/PLANS/current-sprint/metrics-and-learning.md) — 실사용 메트릭 수집 후 첫 번째 패턴 canonical 승격

## Think

- [ ] 제품의 핵심 가치와 대상 사용자를 명확히 한다.
- [ ] 범용으로 유지할 것과 프로젝트 전용으로 바꿀 것을 구분한다.

## Plan

- [ ] 프로젝트 전용 smoke, release, rollback 명령을 정의한다.
- [ ] 지금 바로 필요한 ADR, memory, eval 규칙을 결정한다.

## Build

- [ ] 실제 프로젝트 기준으로 문서, 런북, 명령을 조정한다.
- [ ] 기본 워크플로가 맞지 않는 부분만 canonical skill을 수정한다.

## Review

- [ ] 선택한 워크플로가 실제 팀의 개발 흐름과 맞는지 검토한다.

## Test

- [ ] 구조 변경 후 `scripts/verify.sh`를 실행한다.
- [ ] 프로젝트 전용 smoke 명령을 연결한 뒤 `scripts/smoke.sh`를 실행한다.

## Ship

- [ ] release/rollback 런북이 더 이상 템플릿 placeholder가 아닌지 확인한다.

## Reflect

- [ ] 템플릿에서 유용했던 점, 과했던 점, 부족했던 점을 기록한다.

## Risks and Open Questions

- [ ] 실제 프로젝트의 `docs/` 구조가 아직 없어서 명세 기반 분해 규칙은 아직 실사용으로 검증되지 않았다.
- [ ] 세부 계획 파일을 어떻게 작업 단위로 자를지에 대한 기본 규칙은 강화됐지만, 실제 도메인 예시가 더 필요할 수 있다.
