# Workstream: Accessible Transit

## Goal

ODsay 후보를 분해해 접근 가능한 대중교통 경로만 남기는 ACCESSIBLE_TRANSIT 오케스트레이션을 구현한다.

## Scope

- ODsay 응답 파싱 DTO와 실 API client
- walk/bus/subway leg 분해와 실제 정류장·역 좌표 사용
- MOBILITY용 저상버스/엘리베이터 하드 필터
- 후보 병렬 평가, 정렬, 탈락 사유 응답

## Non-goals

- 프론트엔드 지도 시각화
- 두리발, LLM UI, 커뮤니티 기능

## Source Inputs

- Request: 확정 기준 기반 ACCESSIBLE_TRANSIT 구현 계획
- Docs: `docs/confirm_blueprint.md`, `docs/plans/svc_plan_06_accessible_transit_orchestration.md`
- Code or architecture references: `backend/`, `low_floor_bus_routes`, `subway_station_elevators`, `.ai/EVALS/exception-checklist.md`

## Success Criteria

- [ ] ODsay 후보가 실제 정류장/역 좌표 기반으로 walk leg를 재계산한다.
- [ ] MOBILITY 후보는 저상버스/엘리베이터 조건을 만족하지 않으면 즉시 탈락한다.
- [ ] 후보 결과는 `NO_ACCESSIBLE_TRANSIT`, `TRANSIT_API_UNAVAILABLE` 등 명시적 reason을 반환한다.
- [ ] 정렬 기준이 총 이동시간, 총 도보거리, 환승 횟수 순으로 고정된다.

## Implementation Plan

- [ ] ODsay client와 DTO를 구현하고 실 API 응답을 fixture로 고정한다.
- [ ] leg assembler에서 walk/bus/subway를 분리하고 walk leg는 GH safe profile로 재계산한다.
- [ ] BIMS 실시간 조회, 저상버스 static catalog, 지하철 엘리베이터 조회를 후보 평가에 통합한다.
- [ ] 옵션 병렬 처리와 타임아웃, 후보 탈락 사유 기록을 구현한다.

## Validation Plan

- [ ] 보간 좌표 사용, 순차 처리, synthetic fallback 재도입을 금지 항목으로 검토한다.
- [ ] VISUAL과 MOBILITY 각각에서 허용/탈락 조합을 통합 테스트로 검증한다.
- [ ] 외부 API timeout, 빈 후보, 부분 후보 탈락 시 사용자 응답이 일관적인지 확인한다.

## Risks and Open Questions

- ODsay/BIMS 실 API 키가 없으면 실제 통합 검증이 불가능하다.
- 역 ID와 정류장 ID 정규화가 맞지 않으면 후보 검증이 틀어질 수 있다.
- 외부 API 응답 지연이 옵션 병렬 처리 전체를 끌어내릴 수 있다.

## Dependencies

- `walk-routing-api.md`
- `transit-reference-data.md`

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: 실제 외부 API와 고정 fixture 둘 다 검증돼야 운영 준비로 넘어갈 수 있다.
