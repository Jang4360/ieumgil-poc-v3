# Current Sprint

## Goal

`docs/confirm_blueprint.md`를 최종 기준으로 삼아 부산이음길 실서비스 백엔드 구현을 바로 시작할 수 있는 워크스트림 계획을 확정한다.

## Request Mode

- Primary mode: spec-driven implementation planning
- Scope baseline: backend, ETL, GraphHopper, routing API, transit orchestration, 운영 준비
- Explicit non-goal for this sprint: `docs/plans/svc_plan_08_frontend_kakao_map.md` 구현

## Source of Truth Order

1. `docs/confirm_blueprint.md`
2. `docs/plans/svc_plan_00_project_setup.md` ~ `docs/plans/svc_plan_07_integrated_api_performance.md`
3. `docs/ARD/erd.md`
4. `docs/PRD/2026-04-14_기능명세서.md`
5. `docs/PRD/2026-04-09_부산이음길_PRD.md`
6. `.ai/ARCHITECTURE.md`, `.ai/WORKFLOW.md`, `.ai/EVALS/exception-checklist.md`

## Structured State

- Narrative plan: this file
- Workstream subplans: `.ai/PLANS/current-sprint/`
- Machine-readable progress: `.ai/PLANS/progress.json`
- Quality state: `.ai/EVALS/metrics.json`

## Current Repository Readiness

- Root 기준 실제 앱 프레임워크는 아직 미구성 상태다. `backend/`, `graphhopper/`, `frontend/`, `docker-compose.yml`, `etl/` 구현 파일이 없다.
- `poc/` 하위에는 기존 Spring Boot POC가 있으나 신규 실서비스 구조와 직접 1:1 대응하지 않는다.
- 따라서 기능 구현 전에 레포/런타임 세팅 워크스트림이 선행되어야 한다.

## Success Criteria

- [ ] 스프린트 인덱스가 구현 순서, 선행 조건, 비범위, 리스크를 명확히 보여준다.
- [ ] 각 워크스트림이 `Success Criteria`, `Implementation Plan`, `Validation Plan`을 포함한다.
- [ ] 백엔드 범위에서 필요한 세팅, 데이터 파이프라인, 라우팅, 대중교통, 운영 준비가 빠짐없이 분해된다.
- [ ] 문서 간 충돌 지점은 계획에 명시적 가정 또는 오픈 이슈로 기록된다.
- [ ] 프레임워크 미구성 상태가 별도 준비 작업으로 반영된다.

## Workstream Index

- [x] [foundation-setup.md](.ai/PLANS/current-sprint/foundation-setup.md) — 신규 서비스 레포 골격, Docker, Spring Boot, Python ETL, GraphHopper 플러그인 기본 세팅
- [!] [pedestrian-network.md](.ai/PLANS/current-sprint/pedestrian-network.md) — OSM 기반 `road_nodes` / `road_segments` 적재와 안정 키 보장
- [ ] [accessibility-etl.md](.ai/PLANS/current-sprint/accessibility-etl.md) — 공공데이터 매칭으로 9개 접근성 속성 채우기와 커버리지 검증
- [ ] [graphhopper-engine.md](.ai/PLANS/current-sprint/graphhopper-engine.md) — EV 9개, 4개 프로필, LM, import 검증
- [ ] [walk-routing-api.md](.ai/PLANS/current-sprint/walk-routing-api.md) — SAFE_WALK / FAST_WALK API, 프로필 매핑, 오류 처리
- [ ] [transit-reference-data.md](.ai/PLANS/current-sprint/transit-reference-data.md) — 저상버스/지하철 엘리베이터 참조 데이터 적재
- [ ] [accessible-transit.md](.ai/PLANS/current-sprint/accessible-transit.md) — ACCESSIBLE_TRANSIT 후보 조합, 필터링, 정렬, 외부 API 연동
- [ ] [operations-readiness.md](.ai/PLANS/current-sprint/operations-readiness.md) — 성능 목표, 캐시, 관측성, blue-green GraphHopper 교체

## Delivery Sequence

1. Foundation setup
2. Pedestrian network pipeline
3. Accessibility ETL
4. GraphHopper engine
5. Walk routing API
6. Transit reference data
7. Accessible transit orchestration
8. Operations readiness

## Think

- [ ] `VISUAL` / `MOBILITY` 도메인 용어를 백엔드 전 계층에서 일관되게 사용한다.
- [ ] `confirm_blueprint.md`의 backend-only 범위를 현재 스프린트 경계로 유지한다.

## Plan

- [ ] 루트 프레임워크 미구성 상태를 별도 선행 작업으로 반영한다.
- [ ] 문서 간 충돌 지점을 구현 전 의사결정 항목으로 기록한다.
- [ ] 각 워크스트림에 실패 경로와 검증 전략을 포함한다.

## Build

- [ ] 세팅부터 운영 준비까지 선행 조건 순서대로 구현한다.
- [ ] 데이터 파이프라인과 API 계약이 `confirm_blueprint.md`와 일치하도록 유지한다.

## Review

- [ ] 각 단계에서 문서 기준 위반, 프로필 불일치, UNKNOWN 처리 오류를 중점 검토한다.

## Test

- [ ] DB 적재, ETL 커버리지, GH 프로필 차이, API 오류 응답, 대중교통 후보 탈락 사유를 검증한다.
- [ ] 문서 변경 후 `scripts/verify.sh`를 실행한다.

## Ship

- [ ] 운영 준비 전까지 frontend, 인증 고도화, LLM UI는 비범위로 유지한다.
- [ ] GraphHopper 아티팩트 교체와 롤백 경로를 문서화한다.

## Reflect

- [ ] 공공데이터 품질과 문서 충돌에서 나온 반복 이슈를 `.ai/MEMORY/` 또는 ADR로 승격할 기준을 정한다.

## Risks and Open Questions

- [ ] `docs/confirm_blueprint.md`가 참조하는 `docs/API/...` 원문이 저장소에 없다. 현재 계획은 `confirm_blueprint.md`와 `svc_plan_04`, `svc_plan_06`의 응답 계약을 기준으로 API를 추론한다.
- [ ] PRD는 local-first와 비로그인 MVP를 강조하지만 `svc_plan_04`, `svc_plan_07`, `erd.md`는 JWT 및 사용자 테이블을 포함한다. MVP 라우팅 API 인증 범위를 구현 전에 확정해야 한다.
- [ ] `erd.md`는 사용자/장소/제보까지 넓은 범위를 포함하지만 `confirm_blueprint.md`는 백엔드 라우팅 중심이다. 현재 스프린트는 라우팅 중심 테이블과 참조 데이터만 우선 구현한다.
- [ ] 공공데이터 원본 파일과 외부 API 키는 저장소에 포함되어 있지 않다. 데이터 확보가 늦어지면 ETL, 오케스트레이션, 운영 검증 일정이 함께 밀린다.
- [!] 현재 호스트의 PostgreSQL 인스턴스에는 PostGIS extension이 설치되어 있지 않고, `ieumgil` role/database를 생성할 권한도 없다. `pedestrian-network` end-to-end 적재 검증은 PostGIS가 포함된 DB가 준비되기 전까지 blocked 상태다.
