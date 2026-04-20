# Workstream: Transit Reference Data

## Goal

ACCESSIBLE_TRANSIT 검증에 필요한 저상버스와 지하철 엘리베이터 참조 데이터를 적재한다.

## Scope

- `low_floor_bus_routes` 적재 스크립트
- `subway_station_elevators` 적재 스크립트
- JPA entity/repository 또는 조회 계층 정의
- 갱신 주기와 우선 수집 범위 정리

## Non-goals

- ODsay 후보 조합 로직
- 실시간 버스 도착 정보 조회 로직

## Source Inputs

- Request: 대중교통 참조 테이블까지 포함한 구현 계획
- Docs: `docs/confirm_blueprint.md`, `docs/plans/svc_plan_05_transit_reference_data.md`, `docs/ARD/erd.md`
- Code or architecture references: `etl/`, `backend/`

## Success Criteria

- [ ] 두 참조 테이블 스키마와 적재 스크립트가 문서 기준과 일치한다.
- [ ] 저상버스 카탈로그는 upsert 가능해야 한다.
- [ ] 지하철 엘리베이터는 역 ID와 위치 기준 조회가 가능해야 한다.
- [ ] 환승역 우선 수집 범위가 계획에 반영된다.

## Implementation Plan

- [ ] CSV/GeoJSON 적재 스크립트를 ETL 모듈에 추가한다.
- [ ] Spring 조회 계층에서 route ID, route no, station ID, 운영 여부 기준 조회 메서드를 제공한다.
- [ ] 월간 재적재와 운영 중 override 지점을 문서화한다.
- [ ] 데이터 원본 확보 상태를 체크리스트로 남긴다.

## Validation Plan

- [ ] 잘못된 키 매핑, 중복 upsert, 좌표 SRID 오류를 우선 검토한다.
- [ ] 테이블 row count와 환승역 샘플 조회 결과를 검증한다.
- [ ] 엘리베이터 운영 여부 필터가 정상 동작하는지 확인한다.

## Risks and Open Questions

- 실제 부산 데이터셋의 컬럼 체계가 예시와 다를 수 있다.
- 환승 동선 엘리베이터 데이터가 공공데이터만으로 충분하지 않을 수 있다.
- route ID 표준이 BIMS, ODsay, CSV마다 다르면 조인 전략이 추가로 필요하다.

## Dependencies

- `pedestrian-network.md`

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: ACCESSIBLE_TRANSIT 하드 필터를 구현하기 전에 참조 데이터 적재 경로가 먼저 안정화돼야 한다.
