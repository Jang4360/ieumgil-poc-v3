# Workstream: Pedestrian Network

## Goal

부산 OSM PBF를 보행 세그먼트로 분해해 `road_nodes`와 `road_segments`를 안정적으로 적재한다.

## Scope

- PostGIS DDL 작성
- walkable way 필터, anchor node 식별, segment 분해 로직 구현
- bulk insert, 멱등성, 안정 키 보장
- `segment_attribute_match_result` 추적 테이블 생성

## Non-goals

- 공공데이터 속성 채우기
- GraphHopper 프로필 로직 구현

## Source Inputs

- Request: 확정 기준 문서 기반 보행 네트워크 구현 계획
- Docs: `docs/confirm_blueprint.md`, `docs/plans/svc_plan_01_pedestrian_network_pipeline.md`, `docs/ARD/erd.md`
- Code or architecture references: `etl/`, `postgresql/init/`

## Success Criteria

- [x] `road_nodes`, `road_segments`, `segment_attribute_match_result` 스키마가 확정 기준과 일치한다.
- [x] OSM way 필터와 anchor 분해 기준이 문서에 적힌 포함/제외 규칙을 그대로 반영한다.
- [x] `UNIQUE (source_way_id, source_osm_from_node_id, source_osm_to_node_id)`가 중복 적재를 막는다.
- [!] 한 번의 전체 적재 후 GraphHopper import가 참조할 수 있는 기초 데이터가 생성된다.

## Implementation Plan

- [x] `svc_plan_01` DDL을 `confirm_blueprint.md` 스키마로 정렬해 migration 또는 init SQL로 옮긴다.
- [x] PyOsmium 기반 2-pass 파이프라인으로 walkable way 수집, anchor 계산, segment 분해를 구현한다.
- [x] road node와 segment를 batch insert하고 재실행 시 중복이 생기지 않도록 처리한다.
- [x] 적재 결과를 검증할 SQL과 샘플 통계를 같이 남긴다.

## Validation Plan

- [x] 중복 적재, 누락 anchor, 비정상 짧은 segment, 잘못된 geometry를 리뷰 포인트로 본다.
- [!] 적재 후 row count, 중복 키, geometry null 여부를 SQL로 검증한다.
- [!] 재실행 시 동일 결과가 나오는지 멱등성을 확인한다.

## Risks and Open Questions

- anchor 계산이 과도하면 segment가 지나치게 잘게 쪼개지고, 부족하면 교차점 정확도가 떨어진다.
- `highway=steps`, `elevator` 같은 구조 태그를 어디까지 초기 반영할지 구현 세부 기준이 필요하다.
- 대용량 부산 PBF 처리에서 메모리 사용량이 높아질 수 있다.

## Validation Status

- Status: blocked by database environment
- Build evidence:
  - `python3 -m unittest discover -s etl/tests -v`
  - `python3 -m compileall etl`
  - `python3 etl/build_network.py --help`
  - `python3 etl/build_network.py --pbf /tmp/does-not-exist.osm.pbf`
  - `./scripts/verify.sh`
  - `python3 -m venv etl/.venv && etl/.venv/bin/pip install -r etl/requirements.txt`
- Environment evidence:
  - `etl/data/raw/busan.osm.pbf` exists and was used as the intended runtime input.
  - ETL dependency imports succeeded in `etl/.venv`.
  - PostgreSQL port `5432` is open and accessible.
  - Accessible databases (`postgres`, `poc`, `devinterview`) all reported `postgis = false`.
  - `create extension if not exists postgis` failed because `postgis.control` is not installed on the host PostgreSQL.
  - `.env` targets `ieumgil` role/database, but the current `postgres` login lacks privilege to create that role.
- Tested exception paths:
  - Missing PBF exits with an explicit error instead of silent failure.
  - Missing ETL dependencies were reproduced, then resolved by creating `etl/.venv` and installing `requirements.txt`.
  - Segment splitting, anchor detection, and walkable-way filtering are covered by unit tests.
- Remaining validation work:
  - Prepare a PostgreSQL instance with PostGIS installed.
  - Provide or bootstrap a writable `ieumgil` role/database, or explicitly override ETL connection env vars to a writable PostGIS database.
  - Re-run `python etl/build_network.py --pbf etl/data/raw/busan.osm.pbf --truncate`.
  - Execute SQL checks for row counts, duplicate keys, null geometry, and rerun idempotency.
- Accepted risks:
  - End-to-end load behavior is still unproven because the current host lacks a writable PostGIS database.
  - `build_network.py` has no progress logging yet, so large PBF runs are opaque while parsing.

## Dependencies

- `foundation-setup.md`

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: 이 단계가 끝나야 ETL과 GraphHopper import가 의미 있게 진행된다.
