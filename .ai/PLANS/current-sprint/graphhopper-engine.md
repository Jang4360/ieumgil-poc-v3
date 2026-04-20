# Workstream: GraphHopper Engine

## Goal

`road_segments` 속성을 GraphHopper EV 9개로 로드하고 4개 프로필의 차별화된 경로를 생성한다.

## Scope

- `gh-plugin/` 커스텀 앱 진입점과 ImportRegistry 구성
- EV 9개 정의와 bulk load 매핑
- `config.yaml`, custom model 4개, LM 설정
- 컨테이너 빌드와 프로필 차이 검증

## Non-goals

- 백엔드 HTTP API 응답 포맷 구현
- 대중교통 오케스트레이션 구현

## Source Inputs

- Request: 라우팅 엔진 구현 순서 수립
- Docs: `docs/confirm_blueprint.md`, `docs/plans/svc_plan_03_graphhopper_import.md`
- Code or architecture references: `graphhopper/`, `gh-plugin/`, `poc/`

## Success Criteria

- [ ] EV 9개 이름, 타입, 값 집합이 `confirm_blueprint.md`와 일치한다.
- [ ] DB bulk load 후 per-edge DB query 없이 import가 완료된다.
- [ ] `visual_safe`, `visual_fast`, `wheelchair_safe`, `wheelchair_fast`가 서로 다른 정책을 반영한다.
- [ ] LM 기반 성능 최적화와 import 검증 시나리오가 문서화된다.

## Implementation Plan

- [ ] GraphHopper 9.1용 커스텀 앱 진입점, managed lifecycle, EV registry를 구현한다.
- [ ] `road_segments`에서 `source_way_id + segment_ordinal` 기준으로 EV를 매핑한다.
- [ ] custom model 4개에 HARD EXCLUDE와 UNKNOWN penalty 규칙을 반영한다.
- [ ] 프로필 차이, 계단 회피, 경사도 필터용 검증 스크립트를 작성한다.

## Validation Plan

- [ ] ordinal mismatch, UNKNOWN default 남용, LM 설정 누락을 집중 검토한다.
- [ ] 프로필별 경로 차이와 불가 구간 배제가 실제로 발생하는지 검증한다.
- [ ] GH health와 import 완료 로그를 확인한다.

## Risks and Open Questions

- `segment_ordinal` 기반 매핑이 OSM import 순서와 어긋나면 잘못된 EV가 들어갈 수 있다.
- 전체 segment bulk load가 메모리 사용량을 초과할 수 있다.
- JSON/YAML 파일 형식이 문서 간 혼재되어 있어 실제 GraphHopper 설정 형식을 하나로 정해야 한다.

## Dependencies

- `accessibility-etl.md`

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: 이 단계 검증이 끝나기 전에는 도보 API를 연결하지 않는다.
