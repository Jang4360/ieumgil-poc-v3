# 부산이음길 실서비스 백엔드 — 확정 구현 기준서

> **작성일:** 2026-04-17  
> **목적:** 실서비스 백엔드 구현에 즉시 착수할 수 있는 단일 기준 문서. 이 문서에 기재된 내용이 구현의 최종 기준이다.  
> **범위:** 백엔드 전용 (프론트엔드 제외).  
> **연관 문서:** `docs/claude_blueprint.md`, `docs/ARD/erd.md`, `docs/API/보행_네트워크_도메인/2026-04-12_경로_API_명세.md`, `docs/API/대중교통_도메인/2026-04-13_대중교통_API_명세.md`

---

## 1. 도메인 열거형 (확정)

### 1-1. DisabilityType

```java
public enum DisabilityType {
    VISUAL,    // 시각장애 (점자블록, 음향신호기 중심)
    MOBILITY   // 보행약자 (휠체어, 고령자, 유아차 포함 상위 개념)
}
```

- API 요청/응답, DB ENUM, Java 코드 전체에서 `VISUAL` / `MOBILITY` 사용.
- GraphHopper 내부 프로필 명칭은 `wheelchair_*` 유지 (MOBILITY가 적용하는 제약 프로필).
- `WHEELCHAIR`는 외부 노출 없음. GH 프로필 내부 명칭에만 사용.

### 1-2. RouteOption

```java
public enum RouteOption {
    SAFE_WALK,           // 안전 도보 (접근성 최우선)
    FAST_WALK,           // 빠른 도보 (시간 최우선, 완화된 접근성)
    ACCESSIBLE_TRANSIT   // 접근성 대중교통 혼합 (오케스트레이션)
}
```

- DB: `favorite_routes.route_option`, `route_logs.route_option` 모두 이 값만 사용.
- DEFAULT: `SAFE_WALK`.

### 1-3. GH 프로필 매핑

| DisabilityType | RouteOption | GH 프로필 |
|---|---|---|
| VISUAL | SAFE_WALK | `visual_safe` |
| VISUAL | FAST_WALK | `visual_fast` |
| MOBILITY | SAFE_WALK | `wheelchair_safe` |
| MOBILITY | FAST_WALK | `wheelchair_fast` |
| VISUAL / MOBILITY | ACCESSIBLE_TRANSIT | 오케스트레이션 (GH 프로필 없음) |

```java
private String resolveProfile(DisabilityType type, RouteOption option) {
    return switch (type) {
        case VISUAL   -> option == RouteOption.SAFE_WALK ? "visual_safe"    : "visual_fast";
        case MOBILITY -> option == RouteOption.SAFE_WALK ? "wheelchair_safe" : "wheelchair_fast";
    };
}
```

---

## 2. 데이터 파이프라인 전체 흐름

### 2-1. 원칙

- OSM PBF: **보행 세그먼트 구조(geometry)만** 추출. 속성 태그 신뢰하지 않음.
- `road_segments` 접근성 속성 컬럼: **공공데이터 ETL로만** 채움.
- ETL 미적용 속성은 `UNKNOWN` 유지.
- 예외: `highway=steps` 같은 OSM 구조적 타입은 참고 가능하나, 공공데이터가 있으면 공공데이터 우선.

### 2-2. 전체 흐름

```
[1] OSM PBF 확보 (부산) — 완료 상태
     ↓
[2] 보행 가능 way 필터 추출
     ↓
[3] anchor node 식별 및 way → road_segments 분해
     ↓
[4] road_nodes / road_segments 적재
    (속성 컬럼 전체 UNKNOWN, geometry + 안정 키만 기록)
     ↓
[5] 공공데이터 수집 → raw staging 적재
     ↓
[6] ETL: 세그먼트-공공데이터 공간 매칭 (segment_attribute_match_result)
     ↓
[7] ETL: road_segments 컬럼 UPDATE
    (avg_slope_percent, width, braille_block, audio_signal, curb_ramp, crossing, stairs, elevator)
     ↓
[8] GraphHopper import job
    (road_segments bulk load → 9개 EV 채우기 → graph artifact 생성)
     ↓
[9] GH 서버: artifact load-only 운영 (4개 프로필 + LM)
     ↓
[10] 대중교통 참조 데이터 적재
    (low_floor_bus_routes, subway_station_elevators)
     ↓
[11] ACCESSIBLE_TRANSIT 오케스트레이션 활성화
```

### 2-3. OSM way 필터 기준

**포함 (하나라도 해당):**
```
highway IN {footway, path, pedestrian, living_street, residential,
            service, unclassified, crossing, steps, elevator}
OR foot IN {yes, designated}
OR sidewalk IN {left, right, both, yes}
```

**제외:**
```
foot == no
OR access == private
OR highway IN {motorway, trunk}
```

### 2-4. anchor node 식별

- way의 시작/끝 node
- 2개 이상의 보행 가능 way에 공통으로 등장하는 node (교차점)
- `crossing` 태그 node
- `barrier` 태그 node

### 2-5. 안정 키

```sql
UNIQUE (source_way_id, source_osm_from_node_id, source_osm_to_node_id)
```

`segment_ordinal`은 보조 검증용.

---

## 3. road_segments 스키마 (확정)

| 컬럼명 | 타입 | NULL | DEFAULT | 설명 |
|---|---|---|---|---|
| `edge_id` | BIGSERIAL | NOT NULL | — | PK |
| `from_node_id` | BIGINT | NOT NULL | — | FK → road_nodes.vertexId |
| `to_node_id` | BIGINT | NOT NULL | — | FK → road_nodes.vertexId |
| `geom` | GEOMETRY(LINESTRING, 4326) | NOT NULL | — | 선형 좌표 |
| `length_meter` | NUMERIC(10,2) | NOT NULL | — | 구간 길이 |
| `source_way_id` | BIGINT | NOT NULL | — | OSM way ID |
| `source_osm_from_node_id` | BIGINT | NOT NULL | — | OSM from node ID |
| `source_osm_to_node_id` | BIGINT | NOT NULL | — | OSM to node ID |
| `segment_ordinal` | INT | NOT NULL | — | 보조 검증 순번 |
| `walk_access` | VARCHAR(30) | NOT NULL | `UNKNOWN` | 보행 가능 여부 |
| `avg_slope_percent` | NUMERIC(6,2) | NULL | — | 경사도 절댓값(양수). GH DecimalEV로 등록 |
| `width_meter` | NUMERIC(6,2) | NULL | — | 보행 폭 |
| `braille_block_state` | ENUM | NOT NULL | `UNKNOWN` | YES/NO/UNKNOWN |
| `audio_signal_state` | ENUM | NOT NULL | `UNKNOWN` | YES/NO/UNKNOWN |
| `curb_ramp_state` | ENUM | NOT NULL | `UNKNOWN` | YES/NO/UNKNOWN |
| `width_state` | ENUM | NOT NULL | `UNKNOWN` | ADEQUATE_150/ADEQUATE_120/NARROW/UNKNOWN |
| `surface_state` | ENUM | NOT NULL | `UNKNOWN` | PAVED/GRAVEL/UNPAVED/OTHER/UNKNOWN |
| `stairs_state` | ENUM | NOT NULL | `UNKNOWN` | YES/NO/UNKNOWN |
| `elevator_state` | ENUM | NOT NULL | `UNKNOWN` | YES/NO/UNKNOWN |
| `crossing_state` | ENUM | NOT NULL | `UNKNOWN` | TRAFFIC_SIGNALS/UNCONTROLLED/UNMARKED/NO/UNKNOWN |

**삭제 확정:** `slope_grade`, `slope_state_visual_safe`, `slope_state_visual_fast`, `slope_state_wheelchair_safe`, `slope_state_wheelchair_fast` — 사용하지 않음.  
`avg_slope_percent` 하나를 GH DecimalEncodedValue로 직접 등록해 custom model에서 `avg_slope_percent > N` 으로 비교.

**경사도 부호:** 절댓값(양수)만 저장. 보행 네트워크는 양방향이며 급경사 내리막도 동일 위험.

---

## 4. 공공데이터 → road_segments 속성 매핑

| 속성 컬럼 | 공공데이터셋 | 매칭 방법 | 신뢰 거리 |
|---|---|---|---|
| `avg_slope_percent` | 수치표고모델(DEM) 5m 격자 / 국토지리정보원 | geometry 따라 DEM 샘플링 후 경사도 계산 | — |
| `width_meter` / `width_state` | 보도 폭원 GIS / 부산광역시·국가공간정보포털 | 공간 overlap 매칭 | 15m |
| `surface_state` | 도로포장 현황 / 부산광역시 | 공간 매칭 | 15m |
| `stairs_state` | 계단 위치 현황 / 부산광역시·한국장애인개발원 | POINT 근접 | 15m |
| `braille_block_state` | 점자블록 설치 현황 / 부산광역시·한국장애인개발원 | segment buffer 내 POINT 존재 여부 | 10m |
| `audio_signal_state` | 음향신호기 위치 / 부산광역시·도로교통공단 | segment endpoint 근처 POINT | 15m |
| `curb_ramp_state` | 교통약자 편의시설 경사로 / 부산광역시·한국장애인개발원 | segment endpoint 근처 POINT | 15m |
| `crossing_state` | 횡단보도 GIS / 경찰청·부산광역시 | segment endpoint 공간 매칭 | 15m |
| `elevator_state` | 승강기 위치 DB / 한국승강기안전공단 | segment endpoint 근처 POINT | 15m |

**매칭 신뢰도 기준:**

| 거리 | 처리 |
|---|---|
| ≤ 15m | 반영 (HIGH) |
| 15m ~ 30m | 반영 + segment_attribute_match_result에 LOW_CONFIDENCE 기록 (MEDIUM) |
| 30m ~ 50m | 매칭 무시, UNKNOWN 유지 (LOW) |
| > 50m 또는 데이터 없음 | UNKNOWN (NONE) |

---

## 5. GraphHopper 커스텀 EV 9개 (확정)

| EV 이름 | GH 타입 | 값 | DB 컬럼 |
|---|---|---|---|
| `braille_block_state` | EnumEncodedValue(3) | YES/NO/UNKNOWN | `braille_block_state` |
| `audio_signal_state` | EnumEncodedValue(3) | YES/NO/UNKNOWN | `audio_signal_state` |
| `curb_ramp_state` | EnumEncodedValue(3) | YES/NO/UNKNOWN | `curb_ramp_state` |
| `width_state` | EnumEncodedValue(4) | ADEQUATE_150/ADEQUATE_120/NARROW/UNKNOWN | `width_state` |
| `surface_state` | EnumEncodedValue(5) | PAVED/GRAVEL/UNPAVED/OTHER/UNKNOWN | `surface_state` |
| `stairs_state` | EnumEncodedValue(3) | YES/NO/UNKNOWN | `stairs_state` |
| `elevator_state` | EnumEncodedValue(3) | YES/NO/UNKNOWN | `elevator_state` |
| `crossing_state` | EnumEncodedValue(5) | TRAFFIC_SIGNALS/UNCONTROLLED/UNMARKED/NO/UNKNOWN | `crossing_state` |
| `avg_slope_percent` | DecimalEncodedValue(0.0~30.0) | 절댓값 | `avg_slope_percent` |

### GH Import 전략

```
road_segments 전체 bulk load → Map<wayId, List<Segment>> 메모리 구성
→ OsmTagParser edge 처리 시:
   1. edge의 OSM way ID → candidates 조회
   2. segment_ordinal로 disambiguation
   3. 매칭 segment의 EV 값 기록
→ per-edge DB query 금지 (bulk load만 허용)
```

---

## 6. GraphHopper 프로필 설정 (확정)

```yaml
profiles:
  - name: visual_safe
    custom_model_files: [visual_safe.yaml]
    turn_costs: false
  - name: visual_fast
    custom_model_files: [visual_fast.yaml]
    turn_costs: false
  - name: wheelchair_safe
    custom_model_files: [wheelchair_safe.yaml]
    turn_costs: false
  - name: wheelchair_fast
    custom_model_files: [wheelchair_fast.yaml]
    turn_costs: false

profiles_ch: []   # CH 사용 안 함. custom model 런타임 적용 불가

profiles_lm:
  - profile: visual_safe
    preparations: [{k: 16}]
  - profile: visual_fast
    preparations: [{k: 16}]
  - profile: wheelchair_safe
    preparations: [{k: 16}]
  - profile: wheelchair_fast
    preparations: [{k: 16}]
```

**LM 선택 이유:** CH는 쿼리 시 custom model 가중치 변경 불가. LM은 사전 계산 랜드마크 기반 A* 가속으로 부산 규모 도보 네트워크에서 성능 충분하며, custom model 런타임 적용 가능.

---

## 7. 6개 라우팅 정책 (Custom Model 확정)

### UNKNOWN 처리 원칙

- **HARD EXCLUDE:** 확인된 불가 상태만 (예: `stairs_state == YES` + 휠체어)
- **HEAVY PENALTY:** UNKNOWN 상태에 적용 (`multiply_by: 0.3~0.6`)
  - 이유: 공공데이터 커버리지가 완전하지 않아 UNKNOWN 전면 제외 시 경로 자체가 생성되지 않는 케이스 다수 발생

### 7-1. visual_safe

| 조건 | 처리 |
|---|---|
| `avg_slope_percent > 8` | HARD EXCLUDE |
| `braille_block_state == NO` | HARD EXCLUDE |
| `crossing_state != NO && audio_signal_state == NO` | HARD EXCLUDE |
| `stairs_state == YES` | PENALTY × 0.2 |
| `braille_block_state == UNKNOWN` | PENALTY × 0.5 |
| `audio_signal_state == UNKNOWN` (crossing 구간) | PENALTY × 0.6 |
| `avg_slope_percent > 5` | PENALTY × 0.7 |

### 7-2. visual_fast

| 조건 | 처리 |
|---|---|
| `avg_slope_percent > 8` | HARD EXCLUDE |
| `crossing_state != NO && audio_signal_state == NO` | HARD EXCLUDE |
| `braille_block_state == NO` | PENALTY × 0.4 |
| `stairs_state == YES` | PENALTY × 0.3 |
| `avg_slope_percent > 5` | PENALTY × 0.5 |
| `braille_block_state == UNKNOWN` | PENALTY × 0.7 |

### 7-3. wheelchair_safe

| 조건 | 처리 |
|---|---|
| `stairs_state == YES` | HARD EXCLUDE |
| `surface_state IN {GRAVEL, UNPAVED}` | HARD EXCLUDE |
| `width_state == NARROW` | HARD EXCLUDE |
| `avg_slope_percent > 3` | HARD EXCLUDE |
| `crossing_state != NO && curb_ramp_state == NO` | HARD EXCLUDE |
| `width_state == UNKNOWN` | PENALTY × 0.5 |
| `curb_ramp_state == UNKNOWN` (crossing 구간) | PENALTY × 0.4 |
| `stairs_state == UNKNOWN` | PENALTY × 0.4 |

### 7-4. wheelchair_fast

| 조건 | 처리 |
|---|---|
| `stairs_state == YES` | HARD EXCLUDE |
| `surface_state IN {GRAVEL, UNPAVED}` | HARD EXCLUDE |
| `width_state == NARROW` | HARD EXCLUDE |
| `avg_slope_percent > 5` | HARD EXCLUDE |
| `avg_slope_percent > 3` | PENALTY × 0.5 |
| `width_state == UNKNOWN` | PENALTY × 0.6 |
| `stairs_state == UNKNOWN` | PENALTY × 0.5 |

### 7-5. VISUAL + ACCESSIBLE_TRANSIT

- walk leg: `visual_safe` 프로필로 GH 재계산
- bus/subway leg: 별도 접근성 검증 없음 (시각장애인 시내버스 독립 이용 가능)
- 출발지→버스정류장, 버스정류장→목적지 모든 walk leg를 `visual_safe`로 재계산

### 7-6. MOBILITY + ACCESSIBLE_TRANSIT

- walk leg: `wheelchair_safe` 프로필로 GH 재계산
- 버스 leg 필수: `low_floor_bus_routes.hasLowFloor == true`. 미확인/false → 후보 탈락
- 지하철 leg 필수: 승차역 AND 하차역 모두 `isOperating == true`인 엘리베이터 레코드 존재. 없으면 탈락
- 환승역: 환승 동선 엘리베이터도 검증 (`subway_station_elevators`에서 `entranceNo` 구분)

---

## 8. ACCESSIBLE_TRANSIT 오케스트레이션 흐름

```
POST /routes/search (ACCESSIBLE_TRANSIT)
  ↓
ODsay 후보 6~10개 조회 (출발→목적지)
  ↓
각 후보: WALK / BUS / SUBWAY leg 분해
  ↓
[병렬 처리]
  ├── WALK leg → GH wheelchair_safe (또는 visual_safe) 재계산
  │     └── MOBILITY: 지하철 승/하차역은 가장 가까운 엘리베이터 좌표로 endpoint 대체
  ├── BUS leg → low_floor_bus_routes 정적 검증
  │     └── MOBILITY only: hasLowFloor == false → 즉시 탈락
  │     └── BIMS 실시간 도착 API lowplate1/lowplate2 로 trip 단위 override
  └── SUBWAY leg → subway_station_elevators 엘리베이터 검증
        └── MOBILITY only: isOperating 레코드 없는 역 → 즉시 탈락
  ↓
하드 필터 (접근성 미충족 후보 전체 탈락)
  ↓
정렬: 총 이동시간 ASC → 총 도보거리 ASC → 환승 횟수 ASC
  ↓
상위 1~3개 반환
후보 없음 → available: false, reason: "NO_ACCESSIBLE_TRANSIT"
```

### 허용 조합 (최대 transit leg 2개, 환승 1회)

| 조합 | VISUAL | MOBILITY |
|---|---|---|
| BUS 직행 | O | O (저상버스 필수) |
| SUBWAY 직행 | O | O (엘리베이터 필수) |
| BUS+BUS | O | O (모든 버스 저상 필수) |
| BUS+SUBWAY | O | O |
| SUBWAY+BUS | O | O |
| SUBWAY+SUBWAY | O | O (모든 역 엘리베이터 필수) |

### ACCESSIBLE_TRANSIT fallback 정책

- 후보 없어도 다른 옵션(SAFE_WALK/FAST_WALK)으로 자동 전환하지 않음.
- `available: false, reason: "NO_ACCESSIBLE_TRANSIT"` 명시 반환.
- 세 옵션은 항상 병렬 실행이므로 SAFE_WALK/FAST_WALK 결과는 별도 필드에 이미 포함.

---

## 9. 대중교통 참조 DB 테이블 (확정)

### 9-1. low_floor_bus_routes

```sql
CREATE TABLE low_floor_bus_routes (
    route_id       VARCHAR(20) PRIMARY KEY,  -- 부산 BIMS 노선 ID
    route_no       VARCHAR(20) NOT NULL,      -- 버스 번호 (예: "86")
    has_low_floor  BOOLEAN     NOT NULL DEFAULT false
);
```

- 초기 적재: 부산시 저상버스 도입 현황 공공데이터
- 갱신 주기: 월 1회 이상
- BIMS 실시간 API `lowplate1/lowplate2` → trip 단위 override 가능

### 9-2. subway_station_elevators

```sql
CREATE TABLE subway_station_elevators (
    elevator_id   BIGSERIAL     PRIMARY KEY,
    station_id    VARCHAR(20)   NOT NULL,       -- 부산교통공사 역 ID
    station_name  VARCHAR(100)  NOT NULL,
    line_name     VARCHAR(50)   NOT NULL,
    entrance_no   VARCHAR(10)   NULL,            -- 출입구 번호 (환승 동선 구분)
    point         GEOMETRY(POINT, 4326) NOT NULL, -- 엘리베이터 실제 위치
    is_operating  BOOLEAN       NOT NULL DEFAULT true
);

CREATE INDEX idx_subway_elev_station ON subway_station_elevators(station_id);
```

- 엘리베이터 1개 = 레코드 1개
- 초기 적재: 한국승강기안전공단 + 부산교통공사 역 시설 현황
- WALK leg endpoint 대체 시: `station_id` 조회 → ODsay walk leg 종점과 가장 가까운 엘리베이터 선택

---

## 10. API 계약 (확정)

### 10-1. POST /routes/search

```json
// Request
{
  "disabilityType": "VISUAL | MOBILITY",
  "startPoint": { "lat": 35.1795, "lng": 129.0756 },
  "endPoint":   { "lat": 35.2198, "lng": 129.2153 },
  "routeOptions": ["SAFE_WALK", "FAST_WALK", "ACCESSIBLE_TRANSIT"]
}
// routeOptions 생략 시 세 가지 모두 반환
```

```json
// Response
{
  "success": true,
  "data": {
    "disabilityType": "MOBILITY",
    "startPoint": { "lat": 35.1795, "lng": 129.0756 },
    "endPoint":   { "lat": 35.2198, "lng": 129.2153 },
    "options": [
      {
        "option": "SAFE_WALK",
        "available": true,
        "profile": "wheelchair_safe",
        "summary": {
          "totalDistanceMeter": 3200,
          "estimatedTimeMinute": 45,
          "riskLevel": "LOW"
        },
        "segments": [
          {
            "sequence": 1,
            "geometry": "LINESTRING(...)",
            "distanceMeter": 120,
            "stairsState": "NO",
            "brailleBlockState": "YES",
            "audioSignalState": "YES",
            "curbRampState": "YES",
            "crossingState": "TRAFFIC_SIGNALS",
            "surfaceState": "PAVED",
            "widthState": "ADEQUATE_150",
            "avgSlopePercent": 2.1,
            "guidanceMessage": "전방 횡단보도를 건넌 뒤 직진하세요."
          }
        ]
      },
      {
        "option": "FAST_WALK",
        "available": true,
        "profile": "wheelchair_fast",
        "summary": { "totalDistanceMeter": 2800, "estimatedTimeMinute": 35 },
        "segments": [...]
      },
      {
        "option": "ACCESSIBLE_TRANSIT",
        "available": true,
        "candidates": [
          {
            "rank": 1,
            "combinationType": "BUS_SUBWAY",
            "lowFloorConfirmed": true,
            "elevatorAccessConfirmed": true,
            "summary": {
              "totalDistanceMeter": 6420,
              "estimatedTimeMinute": 31,
              "transferCount": 1,
              "walkDistanceMeter": 520,
              "walkProfile": "wheelchair_safe"
            },
            "legs": [
              {
                "type": "WALK",
                "sequence": 1,
                "distanceMeter": 180,
                "durationMinute": 3,
                "geometry": "LINESTRING(...)"
              },
              {
                "type": "BUS",
                "sequence": 2,
                "routeNo": "1001",
                "isLowFloor": true,
                "boardStop": "반송시장",
                "alightStop": "센텀시티",
                "arrivalMinute": 5
              },
              {
                "type": "SUBWAY",
                "sequence": 3,
                "lineName": "동해선",
                "boardStation": "벡스코",
                "alightStation": "오시리아",
                "elevatorAccess": true
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 10-2. 에러 케이스

| 상황 | available | reason |
|---|---|---|
| GH 경로 없음 | false | `NO_ACCESSIBLE_ROUTE` |
| GH snap 실패 | false | `ORIGIN_NOT_SNAPPABLE` |
| ODsay API 실패 | false | `TRANSIT_API_UNAVAILABLE` |
| 접근성 후보 전체 탈락 | false | `NO_ACCESSIBLE_TRANSIT` |
| 도보보다 느린 후보만 존재 | false | `TRANSIT_SLOWER_THAN_WALK` |

### 10-3. POST /public-transit/accessible-route-candidates

- 기존 API 명세 유지.
- `disabilityType`: `VISUAL` | `MOBILITY` (기존 명세와 동일).

---

## 11. 기존 API 명세 대비 변경 사항

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Request `disabilityType` | 없음 | 추가 (필수) |
| Request `routeOptions` 값 | `SAFE`, `SHORTEST` | `SAFE_WALK`, `FAST_WALK`, `ACCESSIBLE_TRANSIT` |
| Response 구간 속성 | boolean (`hasStairs` 등) | enum 상태값 (`stairsState: "YES/NO/UNKNOWN"`) |
| Response 경사도 | `slopeGrade` (삭제) | `avgSlopePercent` (numeric) |
| Response 구조 | 단일 경로 | 세 옵션 병렬 (`options` 배열) |

---

## 12. 구현 단계 계획 (svc_plan 목록)

| 계획 파일 | 내용 |
|---|---|
| `svc_plan_01` | OSM → 보행 네트워크 파이프라인 (road_nodes/road_segments) |
| `svc_plan_02` | 공공데이터 ETL (DEM 경사도, 보도폭, 접근성 시설 매칭) |
| `svc_plan_03` | GraphHopper import + 4 프로필 + LM 준비 |
| `svc_plan_04` | 도보 라우팅 API (SAFE_WALK + FAST_WALK) |
| `svc_plan_05` | 대중교통 참조 데이터 적재 (저상버스, 지하철 엘리베이터) |
| `svc_plan_06` | ACCESSIBLE_TRANSIT 오케스트레이션 |
| `svc_plan_07` | 통합 API + 성능 최적화 |
