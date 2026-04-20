# Workstream: Operations Readiness

## Goal

통합 라우팅 API를 운영 가능한 수준의 성능, 관측성, 배포 교체 전략으로 마무리한다.

## Scope

- 응답 성능 목표와 option별 timeout
- Redis 캐시, 구조화 로그, Actuator, health
- GraphHopper blue-green artifact 교체
- 운영용 Docker Compose와 배포 체크리스트 정리

## Non-goals

- 모바일 앱 배포
- CI/CD 전체 자동화 구축

## Source Inputs

- Request: 구현 이후 운영까지 이어지는 실행 계획
- Docs: `docs/plans/svc_plan_07_integrated_api_performance.md`, `docs/confirm_blueprint.md`
- Code or architecture references: `docker-compose.yml`, `scripts/`, `.ai/RUNBOOKS/`

## Success Criteria

- [ ] SAFE_WALK / FAST_WALK / ACCESSIBLE_TRANSIT의 timeout과 목표 P95가 코드와 문서에 반영된다.
- [ ] 주요 실패가 로그, health, metric으로 드러난다.
- [ ] GraphHopper artifact 교체와 롤백 경로가 문서화된다.
- [ ] 운영용 Compose와 필수 환경변수 정책이 정리된다.

## Implementation Plan

- [ ] 옵션별 timeout, executor, 캐시 정책을 서비스 코드에 반영한다.
- [ ] Actuator, 구조화 로그, 실패 reason metric을 추가한다.
- [ ] GraphHopper current/next artifact 디렉토리와 교체 스크립트를 준비한다.
- [ ] 배포 전후 체크리스트와 운영 런북을 정리한다.

## Validation Plan

- [ ] 타임아웃 취소 처리, 캐시 stale 데이터, health 과다 노출을 중점 검토한다.
- [ ] 캐시 hit/miss, GH 교체, 외부 API 실패 시 degraded 응답을 점검한다.
- [ ] 문서 변경 후 `scripts/verify.sh`를 실행한다.

## Risks and Open Questions

- 실제 성능 검증 전에는 timeout과 스레드풀 크기가 추정치일 뿐이다.
- GraphHopper artifact blue-green 전략은 디스크 용량과 운영 절차 지원이 필요하다.
- JWT 운영 정책이 확정되지 않으면 actuator와 보호 엔드포인트 범위가 달라질 수 있다.

## Dependencies

- `accessible-transit.md`

## Handoff

- Build skill: `deliver-change`
- Validation skill: `validate-change`
- Ship readiness note: 성능, 관측성, 교체 절차가 없으면 서비스 준비 완료로 간주하지 않는다.
