# 2026-04-19 Ieumgil Accessible Routing Implementation Plan

## Source Documents

- PRD: `docs/PRD/2026-04-09_부산이음길_PRD.md`
- Feature spec: `docs/PRD/2026-04-14_기능명세서.md`
- ERD: `docs/ARD/erd.md`
- Blueprint: `docs/confirm_blueprint.md`
- Existing implementation plan: `docs/plans/`
- Current sprint: `.ai/PLANS/current-sprint.md`

## Problem List

- 기존 `docs/plans`는 `svc_plan_00`~`08`로 분할되어 있지만 각 문서 내부 작업 단위가 여전히 너무 크다. 한 문서 안에 스키마, 코드, 운영, 검증이 한 번에 묶여 있어 build와 review가 병렬로 움직이기 어렵다.
- PRD는 현재 구현을 `local-first`와 비로그인 기본 사용으로 정의하지만, ERD와 `svc_plan_04`, `svc_plan_07`, `svc_plan_08`은 JWT 필수와 계정 기반 저장을 기본 전제로 둔다. 현재 구현 범위의 trust boundary가 문서마다 다르다.
- Blueprint는 백엔드 전용 기준 문서인데 기존 계획은 프론트엔드와 운영 보안 강화 작업을 같은 critical path에 올려두고 있다. 백엔드 MVP 완료 기준과 후속 확장 범위가 섞여 있다.
- `road_segments`가 보행 접근성의 canonical source of truth라는 점은 명확하지만, ETL 실행 이력, raw 데이터 유효성, GraphHopper artifact 버전이 관리되지 않아 "어떤 데이터로 어떤 그래프를 만들었는지"를 추적할 수 없다.
- ETL 계획에는 raw staging, 좌표계 정규화, 데이터셋 스키마 검증, 커버리지 기준 미달 시 중단 규칙이 없다. 실패 원인을 데이터 품질인지 매칭 로직인지 분리하기 어렵다.
- Transit orchestration 계획은 ODsay, BIMS, 저상버스 참조 테이블, 엘리베이터 참조 테이블의 결합 순서를 설명하지만, timeout, rate limit, partial outage, stale reference data에 대한 degraded mode가 불충분하다.
- 완료 기준이 주로 "기동된다", "구현한다", "동작한다" 수준이다. row count, coverage report, fixture pass 수, latency budget, unavailable reason 분포 같은 measurable signal이 필요하다.
- 로그인, 북마크, 자주 가는 길 DB 저장, hazard report, route log 수집은 ERD에 존재하지만 현재 구현 단계에서 실제로 어떤 API와 저장 경로로 이어지는지 계획에 없다. 지금 단계에서 구현하지 않을 기능은 명시적으로 deferred 처리해야 한다.

## Architecture And Data Flow

### Current Delivery Slice

- 현재 delivery slice는 백엔드 접근성 길찾기 MVP에 한정한다.
- 포함 범위: 보행 네트워크 구축, 공공데이터 ETL, GraphHopper import, 도보 라우팅 API, 접근성 대중교통 오케스트레이션, 정적 대중교통 참조 데이터, 운영용 캐시와 관측성.
- 제외 범위: React 프론트엔드, 로그인/회원가입, 계정 연동, 북마크/자주 가는 길 서버 저장, hazard report moderation, route log 수집 저장.
- 비로그인 사용 가능 요구사항에 맞춰 현재 라우팅 API는 anonymous access를 기본으로 두고, 인증은 추후 확장 항목으로 분리한다.

### Source Of Truth And Derived Data

- Raw source of truth:
  - `etl/data/raw/busan.osm.pbf`
  - `etl/data/public/**` 하위 공공데이터 원본
- Normalized relational source of truth:
  - `road_nodes`, `road_segments`
  - `segment_attribute_match_result`
  - `low_floor_bus_routes`
  - `subway_station_elevators`
- Derived artifacts:
  - GraphHopper graph artifact
  - coverage report
  - ETL run report
  - route search cache entry
- Audit metadata to add in implementation:
  - `etl_runs` or equivalent execution ledger
  - `graph_builds` or equivalent artifact metadata
  - source dataset manifest with file name, hash, CRS, loaded_at

### Request Flow

1. 클라이언트가 `POST /routes/search`로 `disabilityType`, 출발지, 도착지, 원하는 옵션 목록을 전송한다.
2. 백엔드는 요청 좌표 유효성, 부산 영역 제한, 옵션 중복 여부를 검증한다.
3. `SAFE_WALK`, `FAST_WALK`, `ACCESSIBLE_TRANSIT`를 독립 실행 단위로 분리한다.
4. 도보 옵션은 GraphHopper HTTP API에 요청하고, 응답 details를 segment-level DTO로 재구성한다.
5. 대중교통 옵션은 ODsay 후보 조회 후 walk/bus/subway leg로 정규화한다.
6. 대중교통 각 후보에 대해 walk leg는 GH 재탐색, bus leg는 저상버스 검증, subway leg는 엘리베이터 검증을 수행한다.
7. 후보를 accessibility hard filter와 정렬 규칙으로 평가하고 상위 결과를 반환한다.
8. 응답에는 option별 `available`, `reason`, 요약 수치, segment 또는 leg 상세를 포함한다.

### Batch Data Flow

1. OSM PBF를 읽어 walkable way를 필터링하고 anchor node 기준으로 segment를 분해한다.
2. `road_nodes`, `road_segments`를 geometry와 안정 키 중심으로 적재한다.
3. 공공데이터 원본을 raw staging과 normalized geometry로 정규화한다.
4. ETL이 `road_segments`에 slope, width, surface, stairs, braille, audio, curb ramp, elevator, crossing 속성을 채우고 `segment_attribute_match_result`에 근거를 남긴다.
5. coverage report가 속성별 채움률, UNKNOWN 비율, low-confidence 수를 출력한다.
6. GraphHopper import는 특정 `road_segments` snapshot을 읽어 EV를 채우고 graph artifact를 생성한다.
7. backend는 해당 artifact 버전을 바라보는 GH 인스턴스와 통신한다.

### Trust Boundaries

- User input boundary:
  - 비로그인 요청 허용
  - 위도/경도 범위 검증, route option enum 검증, payload size 제한 필요
  - user identifier를 현재 API 계약에서 받지 않는다
- External data boundary:
  - OSM과 공공데이터는 신뢰 가능한 공식 출처이지만 schema drift와 좌표계 오류 가능성이 있다
  - 원본 파일 hash와 CRS 검증 없이는 production import 금지
- Internal service boundary:
  - backend는 GH, Redis, PostgreSQL에만 직접 접근
  - GH health와 actuator 상세 정보는 외부 공개 금지
- External API boundary:
  - ODsay, BIMS는 timeout, rate limit, stale data를 전제로 회복 가능하게 설계
  - 외부 API key는 로그와 응답에 노출 금지
- Operator boundary:
  - ETL 실행, graph rebuild, artifact swap은 운영자 권한의 배치 경로로 한정
  - 사용자 요청이 graph rebuild를 트리거하면 안 된다

### Failure Boundaries And Expected Degraded Mode

- GH snap 실패 또는 경로 없음: 해당 option만 `available: false`와 명시적 reason 반환
- ODsay 실패: `ACCESSIBLE_TRANSIT`만 실패 처리하고 도보 옵션은 계속 반환
- BIMS timeout: 실시간 override 없이 정적 `low_floor_bus_routes` 기준으로만 판정하되 응답 메타데이터에 realtime miss 표시
- 공공데이터 coverage 부족: ETL은 완료로 치지 않고 coverage report와 blocker를 남긴다
- Graph artifact build 실패: 기존 artifact 유지, swap 금지
- Redis 장애: 캐시 없이 계산은 계속되나 latency warning 발생

## Execution Units

### ENG-00 Scope Freeze And Canonical Contract

- Goal: 현재 delivery slice를 백엔드 접근성 길찾기 MVP로 고정하고, local-first 요구사항과 충돌하는 인증/저장 범위를 분리한다.
- Inputs and dependencies: PRD, 기능명세서, Blueprint, ERD, 기존 `docs/plans`
- Files or surfaces likely to change: `.ai/PLANS/current-sprint.md`, 본 문서, 필요 시 `docs/plans` 참조 문구
- Build steps:
  - backend MVP 포함/제외 범위를 문서로 고정한다.
  - `anonymous route search`, `deferred auth`, `deferred persistence`를 명시한다.
  - frontend와 account feature를 backend critical path에서 제거한다.
- Review focus: PRD local-first와 blueprint backend-only가 실제 계획에 반영됐는지
- QA or validation path: 문서 상호 검토, `scripts/check-plan-readiness.sh`
- Done criteria:
  - 현재 구현 범위 문서에서 JWT 필수가 더 이상 기본 전제가 아니다.
  - build/review/qa가 backend MVP 범위를 한 문장으로 동일하게 설명할 수 있다.

### DATA-01 Schema Baseline And Run Metadata

- Goal: DDL을 blueprint 기준으로 정리하고 ETL/graph build 추적에 필요한 metadata schema를 추가한다.
- Inputs and dependencies: Blueprint section 3~5, ERD, `svc_plan_01`, `svc_plan_05`
- Files or surfaces likely to change: `postgresql/init/01_schema.sql`, DB migration files
- Build steps:
  - enum과 컬럼명을 blueprint와 일치시킨다.
  - `road_segments`와 참조 테이블을 우선 배치한다.
  - `etl_runs`, `graph_builds`, source manifest 테이블 또는 동등한 ledger를 추가한다.
  - out-of-scope 도메인 테이블은 `deferred` 또는 별도 migration group으로 분리한다.
- Review focus: source of truth 구분, enum 일치성, 운영 추적 가능성
- QA or validation path: blank DB apply, schema diff review
- Done criteria:
  - blank database에 DDL이 한 번에 적용된다.
  - blueprint의 `road_segments` 9개 EV 컬럼과 enum 값이 모두 일치한다.
  - ETL run과 graph build를 식별할 ledger가 존재한다.

### DATA-02 OSM Loader Determinism

- Goal: walkable way 필터, anchor split, bulk insert가 멱등적으로 동작하도록 고정한다.
- Inputs and dependencies: `busan.osm.pbf`, `svc_plan_01`, DATA-01
- Files or surfaces likely to change: `etl/build_network.py`, loader tests, loader README
- Build steps:
  - walkable filter, exclude rule, anchor identification을 코드와 fixture로 고정한다.
  - way split 결과에 대해 stable key를 생성한다.
  - rerun 시 duplicate insert가 0건인지 확인한다.
  - loader summary report에 nodes/segments row count를 출력한다.
- Review focus: anchor rule 누락 여부, geometry 생성 정확성, rerun safety
- QA or validation path: small OSM fixture test, real PBF dry run report
- Done criteria:
  - fixture 기준 segment count가 기대값과 정확히 일치한다.
  - 동일 입력으로 2회 실행 시 신규 insert 수가 0이다.
  - real run summary에 총 node 수, segment 수, filtered way 수가 기록된다.

### DATA-03 Raw Dataset Manifest And Normalization

- Goal: 공공데이터 원본을 무조건 바로 ETL에 쓰지 않고 staging과 정규화 단계를 명시한다.
- Inputs and dependencies: `etl/data/public/**`, `svc_plan_02`, DATA-01
- Files or surfaces likely to change: `etl/normalize_public_data.py`, manifest schema, loader docs
- Build steps:
  - 파일 존재 여부, hash, CRS, geometry validity, 필수 컬럼을 검사한다.
  - shapefile/geojson/csv 입력을 normalized GeoPackage 또는 GeoJSON으로 변환한다.
  - dataset별 source manifest를 저장한다.
  - validation failure 시 ETL 본 실행을 중단한다.
- Review focus: schema drift 대응, CRS 통일, raw/normalized 분리
- QA or validation path: corrupt file fixture, CRS mismatch fixture, manifest snapshot review
- Done criteria:
  - 모든 입력 데이터셋에 file hash, CRS, feature count가 기록된다.
  - CRS mismatch는 자동 변환되거나 실패로 중단된다.
  - 필수 컬럼 누락 데이터셋은 ETL 본 실행 전에 실패한다.

### DATA-04 Slope ETL

- Goal: `avg_slope_percent`를 DEM 기반으로 채우고 이상치와 미계산 구간을 분리한다.
- Inputs and dependencies: DEM, normalized road segments, DATA-02, DATA-03
- Files or surfaces likely to change: `etl/etl_slope.py`, ETL tests, coverage report schema
- Build steps:
  - DEM sampling 로직을 고정한다.
  - short segment, no-data cell, outlier slope를 처리한다.
  - slope update와 match audit를 분리 기록한다.
  - coverage report에 `avg_slope_percent` non-null 비율을 출력한다.
- Review focus: CRS 변환, DEM no-data 처리, 절댓값 정책 일관성
- QA or validation path: synthetic slope fixture, sample district run report
- Done criteria:
  - synthetic fixture에서 계산 오차가 허용 범위 내에 있다.
  - no-data 구간은 `NULL` 유지와 audit reason이 기록된다.
  - real run coverage report에 slope non-null 비율이 수치로 남는다.

### DATA-05 Polygon And Line Attribute ETL

- Goal: width, surface, crossing처럼 면/선 기반 속성 매칭을 작은 단위로 분리한다.
- Inputs and dependencies: normalized width/surface/crossing datasets, DATA-02, DATA-03
- Files or surfaces likely to change: `etl/etl_width.py`, `etl/etl_surface.py`, `etl/etl_crossing.py`
- Build steps:
  - dataset별 공간 조인 규칙과 distance threshold를 코드 상수로 고정한다.
  - `width_meter`와 `width_state` 변환 규칙을 분리한다.
  - low-confidence, no-match, conflict match를 audit로 남긴다.
  - dataset별 update row count를 출력한다.
- Review focus: threshold 근거, state derivation, overwrite precedence
- QA or validation path: geometry overlap fixture, conflict fixture, SQL spot checks
- Done criteria:
  - 각 ETL이 update row count와 no-match count를 출력한다.
  - 동일 segment에 복수 후보가 있을 때 우선순위 규칙이 테스트로 고정된다.
  - `width_state`, `surface_state`, `crossing_state`가 UNKNOWN 외 값으로 채워진 비율이 report에 기록된다.

### DATA-06 Point Feature ETL And Coverage Gate

- Goal: stairs, braille, audio, curb ramp, elevator 매칭과 coverage gate를 한 번에 끝내지 말고 audit 가능하게 만든다.
- Inputs and dependencies: point datasets, DATA-02, DATA-03
- Files or surfaces likely to change: `etl/etl_point_features.py`, `etl/coverage_report.py`, ETL SQL
- Build steps:
  - attribute별 endpoint/buffer 규칙을 분리 구현한다.
  - `segment_attribute_match_result`에 source dataset, confidence, distance를 남긴다.
  - coverage report에서 attribute별 `YES/NO/UNKNOWN` 분포와 low-confidence count를 출력한다.
  - coverage gate 기준 미달 시 graph build를 막는다.
- Review focus: NO와 UNKNOWN 구분, endpoint 기준의 false positive 방지
- QA or validation path: point-near-endpoint fixture, false-positive fixture, coverage report review
- Done criteria:
  - attribute별 coverage report가 파일 또는 테이블로 남는다.
  - `NO`는 dataset coverage 근거가 있는 경우에만 기록된다.
  - coverage gate 미달 시 exit code non-zero로 실패한다.

### GH-01 Encoded Values And Import Plugin

- Goal: GraphHopper import가 `road_segments` 9개 속성을 정확히 EV로 적재하도록 고정한다.
- Inputs and dependencies: DATA-01~06, Blueprint section 5~7, `svc_plan_03`
- Files or surfaces likely to change: `graphhopper/` plugin code, `config.yaml`, custom model files
- Build steps:
  - 9개 EV 정의와 enum/decimal mapping을 구현한다.
  - DB bulk load와 in-memory lookup을 구현한다.
  - per-edge DB query를 금지한다.
  - profile별 custom model rule을 blueprint와 일치시킨다.
- Review focus: enum cardinality, import path, performance footgun 여부
- QA or validation path: import unit tests, EV mapping sample assertions
- Done criteria:
  - import 중 per-edge query가 발생하지 않는다.
  - profile config가 `visual_safe`, `visual_fast`, `wheelchair_safe`, `wheelchair_fast` 4개로 고정된다.
  - sample edges에서 EV 값이 DB와 일치한다.

### GH-02 Graph Build Versioning And Profile Verification

- Goal: graph build를 재현 가능하게 만들고 profile 분기 검증을 release gate로 둔다.
- Inputs and dependencies: GH-01, DATA-06
- Files or surfaces likely to change: graph build scripts, `scripts/swap_graph.sh`, verification scripts
- Build steps:
  - graph build가 참조한 ETL run id와 source hash를 기록한다.
  - 신규 artifact health 확인 전까지 swap을 금지한다.
  - profile 차이, stairs 회피, slope 회피 검증 스크립트를 만든다.
  - import 실패 시 이전 artifact를 유지한다.
- Review focus: build reproducibility, blue-green swap safety, verification realism
- QA or validation path: `tests/verify_gh_profiles.py`, health check, canary query set
- Done criteria:
  - artifact metadata에 build timestamp와 source identifiers가 기록된다.
  - verification script가 최소 3개 시나리오를 pass한다.
  - 신규 artifact health check 실패 시 active artifact가 바뀌지 않는다.

### API-01 Anonymous Walk Routing Contract

- Goal: 도보 경로 API를 anonymous-friendly하게 구현하고 요청/응답 계약을 고정한다.
- Inputs and dependencies: Blueprint API 계약, GH-02
- Files or surfaces likely to change: `backend/src/main/java/.../routing/**`, API docs, tests
- Build steps:
  - `RouteSearchRequest` validation을 구현한다.
  - disability type과 route option을 GH profile로 매핑한다.
  - GH error를 `ORIGIN_NOT_SNAPPABLE`, `NO_ACCESSIBLE_ROUTE` 등 명시적 reason으로 변환한다.
  - actuator와 internal health 노출 범위를 분리한다.
- Review focus: request validation, unavailable reason 정확성, auth boundary
- QA or validation path: controller tests, GH mock integration tests
- Done criteria:
  - anonymous 요청으로 SAFE_WALK와 FAST_WALK를 호출할 수 있다.
  - 잘못된 좌표, 중복 option, 빈 option 처리 규칙이 테스트로 고정된다.
  - 도보 옵션 실패 시 다른 option 결과는 유지된다.

### API-02 ODsay And BIMS Client Hardening

- Goal: 외부 API 연동을 구현하되 fixture와 timeout 정책을 먼저 고정한다.
- Inputs and dependencies: API-01, `svc_plan_06`, `svc_plan_07`
- Files or surfaces likely to change: `backend/.../client/OdsayClient.java`, `BimsClient.java`, fixture files
- Build steps:
  - ODsay response parser와 BIMS response parser를 구현한다.
  - 최초 성공 응답을 fixture로 저장해 contract test를 만든다.
  - timeout, retry 없음 또는 제한적 retry, rate limit handling을 명시한다.
  - API key 미설정 시 startup failure와 local test override를 분리한다.
- Review focus: parser robustness, secret handling, fallback policy
- QA or validation path: fixture contract tests, sandbox integration run
- Done criteria:
  - ODsay/BIMS parser가 stored fixture contract test를 pass한다.
  - timeout과 4xx/5xx에 대한 unavailable reason 매핑이 문서화되고 테스트된다.
  - API key가 로그와 예외 메시지에 출력되지 않는다.

### API-03 Accessible Transit Candidate Evaluation

- Goal: transit 후보 조립, walk leg 재계산, accessibility hard filter를 분리된 단계로 구현한다.
- Inputs and dependencies: API-02, GH-02, `low_floor_bus_routes`, `subway_station_elevators`
- Files or surfaces likely to change: `AccessibleTransitService`, `TransitLegAssembler`, repositories, tests
- Build steps:
  - ODsay subPath를 walk/bus/subway leg로 정규화한다.
  - walk leg는 실제 좌표로 GH 재탐색한다.
  - mobility 후보에 한해 low-floor/elevator hard filter를 적용한다.
  - 후보 탈락 사유를 candidate-level metadata로 남긴다.
- Review focus: 실제 좌표 사용 여부, station/stop id 처리, candidate elimination correctness
- QA or validation path: synthetic transit fixture, repository-backed integration test
- Done criteria:
  - walk leg에 선형 보간 좌표를 사용하지 않는다.
  - candidate 탈락 사유가 `LOW_FLOOR_UNAVAILABLE`, `ELEVATOR_UNAVAILABLE`, `TRANSIT_WALK_UNROUTABLE` 등으로 식별 가능하다.
  - mobility와 visual의 후보 필터 차이가 fixture 테스트로 재현된다.

### API-04 Search Orchestration, Cache, And Telemetry

- Goal: option 병렬 처리, 캐시 키, latency budget, 구조화 로그를 명시해 운영 가능한 응답 경로를 만든다.
- Inputs and dependencies: API-01~03, Redis, `svc_plan_07`
- Files or surfaces likely to change: `RouteSearchService`, cache config, actuator/metrics config
- Build steps:
  - option별 timeout budget을 분리한다.
  - cache key를 `disabilityType + option + rounded coordinates + reference version`으로 고정한다.
  - `available=false` 비율과 latency를 메트릭으로 남긴다.
  - Redis 장애 시 no-cache 계산으로 degrade한다.
- Review focus: thread pool 크기, cache invalidation 기준, partial failure handling
- QA or validation path: concurrency test, cache hit/miss test, benchmark run
- Done criteria:
  - SAFE_WALK/FAST_WALK P95 <= 3000ms, ACCESSIBLE_TRANSIT P95 <= 10000ms를 local benchmark로 확인한다.
  - cache hit와 miss가 로그/메트릭에서 구분된다.
  - 한 option timeout이 다른 option 결과를 막지 않는다.

### OPS-01 Review, QA, And Release Gate Packaging

- Goal: build, review, QA가 그대로 사용할 수 있는 handoff artifact와 smoke path를 만든다.
- Inputs and dependencies: DATA-01~06, GH-01~02, API-01~04
- Files or surfaces likely to change: `.ai/PLANS/current-sprint.md`, smoke checklist, verification scripts
- Build steps:
  - review checklist와 QA 시나리오를 artifact에 연결한다.
  - local compose 기반 smoke flow를 정의한다.
  - graph build, backend boot, route query, transit query를 release gate로 묶는다.
  - out-of-scope 항목은 release gate에서 제외한다고 명시한다.
- Review focus: gate가 현실적인지, 아직 없는 의존성에 묶이지 않았는지
- QA or validation path: `scripts/verify.sh`, local smoke checklist, readiness check
- Done criteria:
  - reviewer가 우선 볼 파일과 QA가 수행할 시나리오가 문서에 명시된다.
  - smoke path가 data pipeline부터 route query까지 끊김 없이 정의된다.
  - frontend/login 미구현이 release blocker로 취급되지 않는다.

## Test And Validation Matrix

- Unit or module tests:
  - OSM walkable filter와 anchor split fixture 테스트
  - slope 계산 fixture 테스트
  - width/surface/crossing state derivation 테스트
  - ODsay/BIMS parser fixture contract 테스트
  - route option/profile resolver 테스트
- Contract tests:
  - `POST /routes/search` request validation과 error schema 테스트
  - ODsay/BIMS stored fixture replay 테스트
  - GH details to `SegmentDto` mapping 테스트
- Integration or ETL checks:
  - blank DB schema apply
  - sample district PBF load
  - normalized public dataset validation
  - attribute ETL 후 coverage report 생성
  - graph build 후 profile verification script 실행
- Security checks:
  - anonymous route search만 허용되고 actuator 상세는 외부에 노출되지 않는지 확인
  - API key가 config dump, 예외, 로그에 노출되지 않는지 확인
  - 좌표 입력 범위와 payload size 제한 테스트
- QA scenarios:
  - 시각장애 safe/fast 경로가 서로 다른 penalty를 반영하는지
  - mobility safe 경로가 stairs와 narrow width를 회피하는지
  - transit 후보가 저상버스/엘리베이터 부재로 탈락하는지
  - ODsay 실패 시 walk 결과만 남는지
  - Redis down 상태에서도 검색이 수행되는지
- Benchmark or latency checks:
  - SAFE_WALK / FAST_WALK P95 <= 3000ms
  - ACCESSIBLE_TRANSIT P95 <= 10000ms, cache hit <= 300ms
  - graph build time과 artifact size 기록
- Release gating checks:
  - `scripts/check-plan-readiness.sh` 통과
  - `scripts/verify.sh` 통과
  - schema apply, ETL coverage report, graph health, walk query, transit query smoke 통과

## Risk Register

- Risk statement: PRD local-first와 JWT 기반 설계가 다시 섞이면 구현과 QA 범위가 무한정 커진다.
  Why it matters: 인증 서버가 없는 상태에서 backend MVP가 기동조차 안 되는 설계가 된다.
  What can be mitigated now: anonymous route search를 current slice 기본값으로 고정한다.
  What remains open: 계정 연동을 도입할 시점과 저장 데이터 동기화 정책은 추후 결정이 필요하다.
  Owner or next action: planning owner가 후속 auth expansion plan을 별도 문서로 분리

- Risk statement: 공공데이터 coverage가 낮으면 4개 GH 프로필 차이가 충분히 드러나지 않을 수 있다.
  Why it matters: 서비스 핵심 차별점인 장애 유형별 경로 분기가 약해진다.
  What can be mitigated now: coverage report와 gate를 추가하고 low-confidence 비율을 추적한다.
  What remains open: 실제 부산 데이터셋 커버리지가 목표치에 미달할 경우 대체 데이터 확보가 필요하다.
  Owner or next action: data pipeline owner가 첫 실측 coverage report 제출

- Risk statement: ODsay/BIMS 외부 API 지연이나 rate limit이 ACCESSIBLE_TRANSIT 안정성을 무너뜨릴 수 있다.
  Why it matters: transit option만 자주 실패하면 사용자 신뢰를 잃는다.
  What can be mitigated now: strict timeout, explicit unavailable reason, fixture contract test, cache를 적용한다.
  What remains open: production traffic 기준 rate limit과 quota 정책은 실제 키 발급 후 확인이 필요하다.
  Owner or next action: backend owner가 sandbox 호출 결과와 quota 문서 수집

- Risk statement: graph build와 active artifact의 연결이 추적되지 않으면 잘못된 데이터로 운영할 수 있다.
  Why it matters: route anomaly 발생 시 원인 추적과 rollback이 어려워진다.
  What can be mitigated now: `graph_builds` metadata와 blue-green swap 검증을 추가한다.
  What remains open: 장기 보관 정책과 artifact retention 수는 운영 환경에서 확정해야 한다.
  Owner or next action: ops owner가 swap 절차와 retention 정책 초안 작성

- Risk statement: ERD에 있는 사용자/제보/로그 테이블을 current slice에 암묵적으로 끌어오면 일정이 붕괴한다.
  Why it matters: 핵심 라우팅 기능이 완성되기 전에 주변 기능이 critical path를 점유한다.
  What can be mitigated now: deferred scope를 문서에 명시하고 release gate에서 제외한다.
  What remains open: hazard report와 route log의 수집/보관 정책은 별도 데이터 거버넌스 검토가 필요하다.
  Owner or next action: product/engineering이 후속 phase 문서 작성

## Review Handoff

- What reviewers should inspect first:
  - scope freeze가 PRD/blueprint와 충돌 없이 정리됐는지
  - `road_segments`와 graph artifact 사이에 추적 가능한 metadata가 추가됐는지
  - transit candidate 평가가 실제 좌표와 명시적 탈락 사유를 사용하도록 설계됐는지
- What changed versus the previous plan:
  - stage 문서 중심 계획을 execution unit 중심 계획으로 재구성했다.
  - frontend와 JWT 필수 조건을 backend MVP critical path에서 제거했다.
  - ETL/graph build에 run metadata, coverage gate, artifact versioning을 추가했다.
  - 테스트 전략을 fixture, contract, integration, benchmark로 분리했다.
- What is intentionally deferred:
  - 로그인/회원가입
  - 북마크/자주 가는 길 서버 저장
  - hazard report 백엔드 저장/관리자 워크플로
  - frontend 구현

## QA Handoff

- Primary user flows:
  - anonymous user가 SAFE_WALK, FAST_WALK를 조회한다.
  - mobility user가 ACCESSIBLE_TRANSIT를 조회하고 저상버스/엘리베이터 조건으로 후보가 필터링된다.
  - visual user가 ACCESSIBLE_TRANSIT를 조회하고 mobility보다 완화된 필터를 받는다.
- Degraded mode or failure scenarios:
  - GH snap 실패
  - ODsay timeout
  - BIMS timeout
  - Redis down
  - coverage gate 미달
- Required fixtures or environments:
  - small OSM fixture
  - sample public dataset fixture with CRS mismatch case
  - stored ODsay/BIMS success and failure fixtures
  - local docker compose stack with PostgreSQL, Redis, GH, backend
- Expected pass or fail signals:
  - pass: option별 `available/reason`이 명시적이고 partial failure가 전체 실패로 번지지 않는다.
  - pass: profile verification과 benchmark threshold가 기준 이내다.
  - fail: JWT 없이는 route search가 불가능한 상태
  - fail: graph build provenance가 남지 않는 상태
  - fail: coverage report 없이 ETL 완료로 처리하는 상태

## Open Questions

- 부산 공공데이터셋별 실제 coverage 메타데이터가 존재하는가, 아니면 UNKNOWN/NO 판정을 별도 현장 규칙으로 보강해야 하는가.
- ACCESSIBLE_TRANSIT에 대해 PRD의 "경로 탐색 응답 3초 이내"를 그대로 적용할 것인가, 아니면 도보와 대중교통 옵션의 latency budget을 분리할 것인가.
- BIMS 실시간 API의 저상버스 필드가 route-level이 아니라 trip-level로 안정적으로 식별 가능한가.
- 지하철 엘리베이터 데이터에서 환승 동선을 판정할 만큼 entrance/exit 정보가 일관되게 제공되는가.
- 향후 로그인 도입 시 anonymous local-first 데이터와 서버 저장 데이터를 어떤 기준으로 병합할 것인가.
