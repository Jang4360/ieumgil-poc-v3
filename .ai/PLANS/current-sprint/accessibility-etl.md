# Workstream: Accessibility ETL

## Goal

공공데이터를 `road_segments`에 매칭해 9개 접근성 속성을 채우고 UNKNOWN 정책을 안정화한다.

## Scope

- DEM 기반 `avg_slope_percent` 계산
- 폭원, 포장, 계단, 점자블록, 음향신호기, 연석경사로, 횡단보도, 엘리베이터 매칭
- `segment_attribute_match_result` 기록
- 커버리지 리포트와 품질 확인 쿼리

## Non-goals

- GraphHopper EV 등록
- API 레이어 구현

## Source Inputs

- Request: 백엔드 구현 선행용 ETL 계획
- Docs: `docs/confirm_blueprint.md`, `docs/plans/svc_plan_02_public_data_etl.md`, `docs/ARD/erd.md`
- Code or architecture references: `etl/`, `.ai/EVALS/exception-checklist.md`

## Success Criteria

- [ ] `road_segments`의 9개 속성이 문서 기준 타입과 값 범위를 따른다.
- [ ] 거리 기반 신뢰도 규칙과 UNKNOWN 유지 정책이 구현에 반영된다.
- [ ] 매칭 결과가 `segment_attribute_match_result`에 남아 사후 분석이 가능하다.
- [ ] 경사도 분포와 속성 커버리지를 확인할 리포트가 존재한다.

## Implementation Plan

- [ ] DEM, SHP, GeoJSON 입력 포맷을 표준화하고 좌표계를 통일한다.
- [ ] 속성별 ETL 스크립트를 공통 DB 유틸과 배치 처리 방식으로 구현한다.
- [ ] HIGH/MEDIUM/LOW/NONE 신뢰도와 UNKNOWN 유지 규칙을 일관되게 적용한다.
- [ ] 커버리지 리포트와 샘플 검증 SQL을 만든다.

## Validation Plan

- [ ] 잘못된 CRS, 거리 계산 오류, UNKNOWN을 NO로 오판하는 로직을 우선 점검한다.
- [ ] 속성별 null/unknown 비율과 샘플 구간 지도 검증을 수행한다.
- [ ] ETL 재실행 시 업데이트 결과가 일관되는지 확인한다.

## Risks and Open Questions

- 공공데이터 파일 확보와 정제 수준이 일정의 핵심 리스크다.
- 데이터셋별 컬럼명이 예시와 다를 가능성이 높다.
- ETL 속도가 느리면 전체 개발 루프가 과도하게 길어진다.

## Dependencies

- `pedestrian-network.md`

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: EV와 custom model 검증 전까지 slope와 width 계열 값은 최소한 유효 범위로 채워져야 한다.
