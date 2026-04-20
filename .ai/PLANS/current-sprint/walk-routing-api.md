# Workstream: Walk Routing API

## Goal

SAFE_WALK와 FAST_WALK를 동일 API 계약으로 제공하고 장애 유형별 GH 프로필 매핑을 고정한다.

## Scope

- `DisabilityType`, `RouteOption` 열거형과 프로필 resolver
- GraphHopper HTTP client와 도보 라우팅 서비스
- `/routes/search` 요청/응답 DTO
- 전역 에러 처리, unavailable reason, 로컬 개발 보안 정책

## Non-goals

- ACCESSIBLE_TRANSIT 후보 조합
- 회원가입/마이페이지 전체 구현

## Source Inputs

- Request: 확정 기준 기반 도보 라우팅 API 계획
- Docs: `docs/confirm_blueprint.md`, `docs/plans/svc_plan_04_walk_routing_api.md`, `docs/ARD/erd.md`
- Code or architecture references: `backend/`, `.ai/EVALS/exception-checklist.md`

## Success Criteria

- [ ] `VISUAL` / `MOBILITY`, `SAFE_WALK` / `FAST_WALK` / `ACCESSIBLE_TRANSIT` 값이 전 계층에서 일치한다.
- [ ] 도보 옵션 두 개가 GH 프로필과 정확히 매핑된다.
- [ ] GH snap 실패, 경로 없음, 타임아웃이 명시적 reason으로 반환된다.
- [ ] 응답 segment에 접근성 detail이 포함된다.

## Implementation Plan

- [ ] 공통 응답 래퍼, 라우팅 DTO, 프로필 resolver, GraphHopper client를 구현한다.
- [ ] `WalkRoutingService`에서 profile별 detail 조회와 segment 변환을 처리한다.
- [ ] `/routes/search`에서 옵션별 병렬 실행 구조를 준비한다.
- [ ] local-first MVP와 JWT 요구사항 충돌을 고려해 local profile 보안 정책을 분리한다.

## Validation Plan

- [ ] enum drift, reason 코드 누락, detail interval 해석 오류를 검토한다.
- [ ] GH 경로 있음/없음, 스냅 불가, 타임아웃 케이스를 API 테스트로 확인한다.
- [ ] 프로필별 동일 요청 결과가 실제로 달라지는지 샘플 좌표로 검증한다.

## Risks and Open Questions

- 인증 요구사항이 불명확해 controller 보안 범위가 다시 바뀔 수 있다.
- GH detail interval을 segment 단위로 나누는 로직이 경계값에서 틀릴 수 있다.
- `docs/API` 원문 부재로 세부 오류 응답 계약은 추가 확인이 필요하다.

## Dependencies

- `graphhopper-engine.md`

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: unavailable reason과 segment detail contract가 고정돼야 상위 옵션 조합을 얹을 수 있다.
