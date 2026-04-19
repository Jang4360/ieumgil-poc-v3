# svc_plan_05: 대중교통 참조 데이터 적재

> **작성일:** 2026-04-18 (POC 분석 반영 업데이트)  
> **목적:** ACCESSIBLE_TRANSIT 오케스트레이션에 필요한 두 정적 테이블 적재  
> **선행 조건:** svc_plan_01 완료 (DB 스키마 준비)  
> **후행 단계:** svc_plan_06 (ACCESSIBLE_TRANSIT 오케스트레이션)

---

## 1. POC 대비 변경 사항

POC에 `low_floor_bus_routes`, `subway_station_elevators` 테이블이 없었다.
`BusanBimsTransitClient`는 stub이었고 `lowFloorExpected` 값은 항상 true를 반환:

```java
// POC StubBusanBimsTransitClient.java
boolean lowFloorExpected = routeNo != null && !routeNo.isBlank();  // 항상 true
```

신규 레포에서는 실제 저상버스 카탈로그와 엘리베이터 위치를 DB에 적재해 검증한다.

---

## 2. 테이블 스키마

svc_plan_01의 DDL에 포함됨:

```sql
CREATE TABLE low_floor_bus_routes (
    route_id       VARCHAR(20) PRIMARY KEY,
    route_no       VARCHAR(20) NOT NULL,
    has_low_floor  BOOLEAN     NOT NULL DEFAULT false
);

CREATE TABLE subway_station_elevators (
    elevator_id   BIGSERIAL              PRIMARY KEY,
    station_id    VARCHAR(20)            NOT NULL,
    station_name  VARCHAR(100)           NOT NULL,
    line_name     VARCHAR(50)            NOT NULL,
    entrance_no   VARCHAR(10),
    point         GEOMETRY(POINT, 4326)  NOT NULL,
    is_operating  BOOLEAN                NOT NULL DEFAULT true
);
CREATE INDEX idx_subway_elev_station ON subway_station_elevators(station_id);
CREATE INDEX idx_subway_elev_point   ON subway_station_elevators USING GIST(point);
```

---

## 3. low_floor_bus_routes 적재

### 3-1. 데이터 출처 (우선순위)

| 순위 | 출처 | 방법 |
|---|---|---|
| 1 | 부산광역시 저상버스 도입 현황 (공공데이터포털) | CSV 다운로드 |
| 2 | BIMS API `getBusRouteList` | API 조회 후 저상 여부 파싱 |

### 3-2. 적재 스크립트

```python
# etl/load_low_floor_routes.py
import csv
import psycopg2
from psycopg2.extras import execute_values

def load_from_csv(conn, csv_path: str):
    """
    CSV 컬럼 예시: 노선ID, 노선번호, 저상버스여부(Y/N)
    실제 컬럼명은 공공데이터 파일에 맞게 조정
    """
    rows = []
    with open(csv_path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            route_id = row.get('노선ID') or row.get('routeId') or row.get('ROUTE_ID')
            route_no = row.get('노선번호') or row.get('routeNo') or row.get('ROUTE_NO')
            raw_flag = row.get('저상버스여부') or row.get('hasLowFloor') or row.get('LOW_FLOOR_YN')
            has_low_floor = str(raw_flag).strip().upper() in {'Y', '1', 'TRUE', '저상', 'YES'}
            rows.append((route_id.strip(), route_no.strip(), has_low_floor))

    with conn.cursor() as cur:
        execute_values(cur,
            """INSERT INTO low_floor_bus_routes (route_id, route_no, has_low_floor)
               VALUES %s
               ON CONFLICT (route_id) DO UPDATE
                 SET route_no = EXCLUDED.route_no,
                     has_low_floor = EXCLUDED.has_low_floor""",
            rows
        )
    conn.commit()
    print(f"low_floor_bus_routes: {len(rows)}건 upsert 완료")
    print(f"저상버스: {sum(1 for _, _, f in rows if f)}건 / 전체 {len(rows)}건")
```

### 3-3. BIMS API 연동 (보조)

```python
import requests

def fetch_bims_routes(service_key: str) -> list[dict]:
    """BIMS 버스 노선 목록 조회"""
    url = "http://apis.data.go.kr/6260000/BusanBIMS/getBusRouteList"
    all_routes = []
    page = 1
    while True:
        resp = requests.get(url, params={
            "serviceKey": service_key,
            "numOfRows": 500,
            "pageNo": page
        }, timeout=10)
        data = resp.json()
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if not items:
            break
        all_routes.extend(items)
        page += 1
    return all_routes
```

### 3-4. 갱신 주기

월 1회 전체 재적재 (upsert). BIMS 실시간 `lowplate1/lowplate2`는 trip 단위 override로 사용 (오케스트레이션 시 실시간 조회).

---

## 4. subway_station_elevators 적재

### 4-1. 데이터 출처

| 순위 | 출처 | 방법 |
|---|---|---|
| 1 | 한국승강기안전공단 승강기 정보 DB (국가공간정보포털) | SHP / CSV |
| 2 | 부산교통공사 역 시설 현황 공공데이터 | 수동 수집 |
| 3 | 환승역 환승 동선 엘리베이터 | 현장 확인 |

### 4-2. GeoJSON 적재 스크립트

```python
# etl/load_subway_elevators.py
import json
import psycopg2
from psycopg2.extras import execute_values

def load_from_geojson(conn, geojson_path: str):
    """
    GeoJSON Feature 구조:
    {
      "geometry": {"type": "Point", "coordinates": [lng, lat]},
      "properties": {
        "station_id": "BTC_SEOMYEON",
        "station_name": "서면",
        "line_name": "1호선",
        "entrance_no": "3",   (nullable — 환승 동선 구분용)
        "is_operating": true
      }
    }
    """
    with open(geojson_path, encoding='utf-8') as f:
        data = json.load(f)

    rows = []
    for feature in data['features']:
        props = feature['properties']
        coords = feature['geometry']['coordinates']  # [lng, lat]
        rows.append((
            props['station_id'],
            props['station_name'],
            props['line_name'],
            props.get('entrance_no'),
            f"SRID=4326;POINT({coords[0]} {coords[1]})",
            props.get('is_operating', True)
        ))

    with conn.cursor() as cur:
        execute_values(cur,
            """INSERT INTO subway_station_elevators
               (station_id, station_name, line_name, entrance_no, point, is_operating)
               VALUES %s""",
            rows
        )
    conn.commit()
    print(f"subway_station_elevators: {len(rows)}건 적재 완료")
```

### 4-3. 수집 체크리스트

부산 지하철 노선별 전역 엘리베이터 위치 수집 필요:

```
1호선: 신평 ~ 노포 (40개 역)
2호선: 장산 ~ 양산 (43개 역)
3호선: 수영 ~ 대저 (17개 역)
4호선: 안평 ~ 미남 (14개 역)
동해선: 부전 ~ 태화강 (14개 역)
```

**환승역 우선 수집 (서비스 핵심):**

| 환승역 | 호선 | 우선도 |
|---|---|---|
| 서면 | 1↔2 | 최우선 |
| 연산 | 1↔3 | 최우선 |
| 수영 | 2↔3 | 최우선 |
| 사상 | 2↔부산김해경전철 | 최우선 |
| 대저 | 2↔부산김해경전철 | 최우선 |

환승 동선 엘리베이터는 `entrance_no`로 구분:
- `entrance_no = '1호선_승강장'`, `'환승_통로'` 등으로 기록

---

## 5. Spring Boot Entity 클래스

```java
// backend/src/main/java/com/ieumgil/transit/domain/LowFloorBusRoute.java
@Entity
@Table(name = "low_floor_bus_routes")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class LowFloorBusRoute {

    @Id
    @Column(name = "route_id")
    private String routeId;

    @Column(name = "route_no", nullable = false)
    private String routeNo;

    @Column(name = "has_low_floor", nullable = false)
    private boolean hasLowFloor;

    public LowFloorBusRoute(String routeId, String routeNo, boolean hasLowFloor) {
        this.routeId = routeId;
        this.routeNo = routeNo;
        this.hasLowFloor = hasLowFloor;
    }
}
```

```java
// backend/src/main/java/com/ieumgil/transit/domain/SubwayStationElevator.java
@Entity
@Table(name = "subway_station_elevators")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class SubwayStationElevator {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "elevator_id")
    private Long elevatorId;

    @Column(name = "station_id", nullable = false)
    private String stationId;

    @Column(name = "station_name", nullable = false)
    private String stationName;

    @Column(name = "line_name", nullable = false)
    private String lineName;

    @Column(name = "entrance_no")
    private String entranceNo;

    @Column(name = "point", columnDefinition = "GEOMETRY(POINT, 4326)", nullable = false)
    private Point point;   // org.locationtech.jts.geom.Point (Hibernate Spatial)

    @Column(name = "is_operating", nullable = false)
    private boolean isOperating = true;

    public GeoPoint toGeoPoint() {
        return new GeoPoint(point.getY(), point.getX());  // lat = Y, lng = X
    }
}
```

**Hibernate Spatial 의존성 (build.gradle에 추가):**
```groovy
implementation 'org.hibernate.orm:hibernate-spatial'
```

---

## 6. 실행 명령

```bash
# svc_plan_00 venv 활성화 (svc_plan_01 이후 언제든 실행 가능)
source etl/.venv/bin/activate

# 1. 저상버스 노선 적재 (CSV)
python etl/load_low_floor_routes.py \
  --csv etl/data/public/low_floor_routes.csv

# 2. 지하철 엘리베이터 적재 (GeoJSON)
python etl/load_subway_elevators.py \
  --geojson etl/data/public/subway_elevators.geojson

# 실행 확인
psql -h localhost -U ieumgil -d ieumgil -c "
SELECT COUNT(*) AS routes, SUM(has_low_floor::int) AS low_floor
FROM low_floor_bus_routes;
"
psql -h localhost -U ieumgil -d ieumgil -c "
SELECT COUNT(*) AS elevators, COUNT(DISTINCT station_id) AS stations
FROM subway_station_elevators WHERE is_operating = true;
"
```

> **실행 타이밍:** svc_plan_01 완료 후 바로 실행 가능. svc_plan_02, svc_plan_03과 병렬 진행 가능.

---

## 7. 검증 쿼리

```sql
-- low_floor_bus_routes 적재 확인
SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN has_low_floor THEN 1 ELSE 0 END) AS low_floor_cnt,
    ROUND(100.0 * SUM(CASE WHEN has_low_floor THEN 1 ELSE 0 END) / COUNT(*), 1) AS low_floor_pct
FROM low_floor_bus_routes;
-- 기대: 부산 저상버스 비율 60~80%

-- 역별 엘리베이터 수 확인
SELECT station_id, station_name, line_name, COUNT(*) AS elev_cnt
FROM subway_station_elevators
WHERE is_operating = true
GROUP BY station_id, station_name, line_name
ORDER BY line_name, station_name;

-- 엘리베이터 없는 역 (운영 중) 확인 — 이 역은 MOBILITY 경로에서 탈락
SELECT DISTINCT s.station_id, s.station_name, s.line_name
FROM subway_station_elevators s
WHERE NOT EXISTS (
    SELECT 1 FROM subway_station_elevators e
    WHERE e.station_id = s.station_id AND e.is_operating = true
);

-- 좌표 유효성
SELECT COUNT(*) FROM subway_station_elevators WHERE NOT ST_IsValid(point);
-- 기대: 0
```

---

## 6. Spring Boot Repository (오케스트레이션 참조용)

```java
// svc_plan_06에서 사용
@Repository
public interface LowFloorBusRouteRepository extends JpaRepository<LowFloorBusRoute, String> {
    Optional<LowFloorBusRoute> findByRouteId(String routeId);
}

@Repository
public interface SubwayStationElevatorRepository extends JpaRepository<SubwayStationElevator, Long> {

    boolean existsByStationIdAndIsOperatingTrue(String stationId);

    // 역 좌표 기준 가장 가까운 엘리베이터 조회 (오케스트레이션에서 walk leg endpoint 대체)
    @Query("""
        SELECT e FROM SubwayStationElevator e
        WHERE e.stationId = :stationId AND e.isOperating = true
        ORDER BY ST_Distance(e.point, ST_SetSRID(ST_Point(:lng, :lat), 4326))
        LIMIT 1
        """,
        nativeQuery = true)
    Optional<SubwayStationElevator> findNearestOperating(
        @Param("stationId") String stationId,
        @Param("lat") double lat,
        @Param("lng") double lng
    );
}
```

---

## 7. 완료 기준

- [ ] `low_floor_bus_routes`: 부산 전 노선 적재 (저상버스 비율 50% 이상)
- [ ] `subway_station_elevators`: 주요 환승역 포함 전역 엘리베이터 위치 적재
- [ ] 좌표 유효성 통과
- [ ] 엘리베이터 없는 역 목록 파악 (MOBILITY 경로 탈락 기준)
- [ ] Repository 쿼리 동작 확인 (findNearestOperating)
