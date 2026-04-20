# Workstream: Foundation Setup

## Goal

실서비스 구현이 가능한 루트 레포 골격과 실행 환경을 만든다.

## Scope

- `docker-compose.yml`, `.env.example`, `.gitignore`, `runtime/` 구조 정의
- `backend/` Spring Boot 3.3 + Java 21 기본 프로젝트 생성
- `graphhopper/` 컨테이너 및 `gh-plugin/` 모듈 골격 생성
- `etl/` Python 가상환경 의존성과 공통 DB 유틸 구성

## Non-goals

- 도메인별 비즈니스 로직 구현
- 프론트엔드 앱 구현

## Source Inputs

- Request: `confirm_blueprint.md`, `docs/plans/`, `erd.md` 기반 구현 계획 작성
- Docs: `docs/confirm_blueprint.md`, `docs/plans/svc_plan_00_project_setup.md`, `docs/ARD/erd.md`
- Code or architecture references: `.ai/ARCHITECTURE.md`, `.ai/WORKFLOW.md`, `poc/`

## Success Criteria

- [x] 루트에 backend, graphhopper, gh-plugin, etl, postgresql 초기 구조가 생성된다.
- [x] Docker Compose만으로 PostgreSQL, Redis, GraphHopper, backend를 올릴 수 있는 설정이 준비된다.
- [x] 환경변수 이름이 `svc_plan_00` 표준 키와 일치한다.
- [x] 후속 워크스트림이 사용할 기본 의존성, 디렉토리, 실행 진입점이 정해진다.

## Implementation Plan

- [x] `svc_plan_00` 기준 디렉토리 구조와 필수 파일 목록을 루트에 만든다.
- [x] Spring Boot, GraphHopper, Python ETL 기본 의존성과 빌드 파일을 구성한다.
- [x] `.env.example`와 `.gitignore`를 외부 API 키, PBF, 공공데이터 파일 기준으로 정리한다.
- [x] `poc/`에서 재사용 가능한 클래스·설정 후보를 식별하되 신규 구조에 맞게 별도 모듈로 이관한다.

## Validation Plan

- [!] `docker compose config` 수준의 정적 검토가 가능해야 한다.
- [x] backend, gh-plugin, etl의 빌드 진입점이 문서와 일치하는지 확인한다.
- [x] 누락된 환경변수나 버전 충돌이 없는지 검토한다.

## Risks and Open Questions

- 루트 프레임워크가 비어 있어 초기 세팅 누락 시 후속 워크스트림이 모두 막힌다.
- GraphHopper 9.1과 Java 21, Spring Boot 3.3 조합 검증이 필요하다.
- JWT 설정은 문서 충돌이 있어 MVP 범위 확정 전까지 local profile 우선으로 설계해야 할 수 있다.

## Validation Status

- Status: ready for next workstream with accepted gaps
- Build evidence:
  - `backend/./gradlew test`
  - `backend/./gradlew bootJar`
  - `gh-plugin/mvn -q test`
  - `gh-plugin/mvn -q -DskipTests package`
  - `python3 -m compileall etl`
  - `python3 etl/*.py --help`
- Tested exception paths:
  - Local profile requests are permitted by a dedicated `SecurityFilterChain` test.
  - ETL entrypoints fail with explicit "foundation setup only" messages instead of silent placeholders.
  - Runtime directories and ignored data paths are present so missing PBF/public data does not produce accidental commits.
- Accepted risks:
  - Docker CLI is unavailable in this host, so `docker compose config` was not executed here.
  - `graphhopper/config.yaml`, custom models, and `gh-plugin` are scaffolds only; real EV/import wiring belongs to `graphhopper-engine.md`.
  - Non-local JWT startup behavior is intentionally deferred until the routing API workstream fixes the final auth boundary.

## Dependencies

- 선행 의존성 없음

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: 루트 실행 골격이 없으면 나머지 워크스트림은 착수하지 않는다.
