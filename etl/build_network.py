from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import osmium  # type: ignore
except ModuleNotFoundError:
    osmium = None


INCLUDE_HIGHWAY = frozenset({
    "footway",
    "path",
    "pedestrian",
    "living_street",
    "residential",
    "service",
    "unclassified",
    "crossing",
    "steps",
    "elevator",
})
EXCLUDE_HIGHWAY = frozenset({"motorway", "trunk"})
ANCHOR_NODE_TAGS = frozenset({"crossing", "barrier"})
DEFAULT_BATCH_SIZE = 5_000


@dataclass(frozen=True)
class SegmentReference:
    way_id: int
    from_osm_node_id: int
    to_osm_node_id: int
    ordinal: int
    node_ids: tuple[int, ...]


@dataclass(frozen=True)
class Coordinate:
    lon: float
    lat: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build road_nodes and road_segments from Busan OSM PBF.")
    parser.add_argument("--pbf", default="etl/data/raw/busan.osm.pbf", help="Path to the Busan OSM PBF file.")
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate road network tables before loading. Use for full rebuilds.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Bulk insert page size.",
    )
    return parser.parse_args()


def is_walkable(tags: dict[str, str]) -> bool:
    if tags.get("foot") == "no" or tags.get("access") == "private":
        return False
    if tags.get("highway") in EXCLUDE_HIGHWAY:
        return False
    return (
        tags.get("highway") in INCLUDE_HIGHWAY
        or tags.get("foot") in {"yes", "designated"}
        or tags.get("sidewalk") in {"left", "right", "both", "yes"}
    )


def is_anchor_node(tags: dict[str, str]) -> bool:
    return any(tag in tags for tag in ANCHOR_NODE_TAGS)


def identify_anchors(walkable_ways: dict[int, list[int]], node_way_count: dict[int, int], tagged_nodes: set[int]) -> set[int]:
    anchors = set(tagged_nodes)
    for nodes in walkable_ways.values():
        if not nodes:
            continue
        anchors.add(nodes[0])
        anchors.add(nodes[-1])
    anchors.update(node_id for node_id, count in node_way_count.items() if count >= 2)
    return anchors


def split_way_to_segments(way_id: int, nodes: list[int], anchors: set[int]) -> list[SegmentReference]:
    if len(nodes) < 2:
        return []

    segments: list[SegmentReference] = []
    start_index = 0
    ordinal = 0
    for index in range(1, len(nodes)):
        if nodes[index] not in anchors:
            continue
        if nodes[start_index] == nodes[index]:
            start_index = index
            continue
        segment_node_ids = tuple(nodes[start_index:index + 1])
        if len(segment_node_ids) >= 2:
            segments.append(
                SegmentReference(
                    way_id=way_id,
                    from_osm_node_id=segment_node_ids[0],
                    to_osm_node_id=segment_node_ids[-1],
                    ordinal=ordinal,
                    node_ids=segment_node_ids,
                )
            )
            ordinal += 1
        start_index = index
    return segments


def build_linestring_wkt(coords: Iterable[Coordinate]) -> str:
    serialized = ", ".join(f"{coord.lon:.7f} {coord.lat:.7f}" for coord in coords)
    return f"LINESTRING({serialized})"


def measure_length_meters(coords: list[Coordinate]) -> float:
    if len(coords) < 2:
        return 0.0

    total = 0.0
    for start, end in zip(coords, coords[1:]):
        total += haversine_meters(start, end)
    return round(total, 2)


def haversine_meters(start: Coordinate, end: Coordinate) -> float:
    radius_m = 6_371_000.0
    lat1 = math.radians(start.lat)
    lat2 = math.radians(end.lat)
    delta_lat = math.radians(end.lat - start.lat)
    delta_lon = math.radians(end.lon - start.lon)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_m * c


def require_osmium():
    if osmium is None:
        raise SystemExit(
            "osmium is required to parse OSM PBF files. Install ETL dependencies first: "
            "`cd etl && python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`."
        )


def load_osm_structure(pbf_path: Path) -> tuple[dict[int, list[int]], set[int], dict[int, Coordinate]]:
    require_osmium()

    class Phase1Collector(osmium.SimpleHandler):  # type: ignore[misc]
        def __init__(self) -> None:
            super().__init__()
            self.walkable_ways: dict[int, list[int]] = {}
            self.node_way_count: dict[int, int] = {}
            self.tagged_anchor_nodes: set[int] = set()

        def node(self, node) -> None:
            tags = {tag.k: tag.v for tag in node.tags}
            if is_anchor_node(tags):
                self.tagged_anchor_nodes.add(node.id)

        def way(self, way) -> None:
            tags = {tag.k: tag.v for tag in way.tags}
            if not is_walkable(tags):
                return
            node_ids = [node.ref for node in way.nodes]
            if len(node_ids) < 2:
                return
            self.walkable_ways[way.id] = node_ids
            for node_id in node_ids:
                self.node_way_count[node_id] = self.node_way_count.get(node_id, 0) + 1

    collector = Phase1Collector()
    collector.apply_file(str(pbf_path), locations=False)
    anchors = identify_anchors(collector.walkable_ways, collector.node_way_count, collector.tagged_anchor_nodes)
    referenced_node_ids = {node_id for node_ids in collector.walkable_ways.values() for node_id in node_ids}

    class NodeLocationCollector(osmium.SimpleHandler):  # type: ignore[misc]
        def __init__(self, target_node_ids: set[int]) -> None:
            super().__init__()
            self.target_node_ids = target_node_ids
            self.node_locations: dict[int, Coordinate] = {}

        def node(self, node) -> None:
            if node.id not in self.target_node_ids:
                return
            if not node.location.valid():
                return
            self.node_locations[node.id] = Coordinate(lon=node.location.lon, lat=node.location.lat)

    location_collector = NodeLocationCollector(referenced_node_ids)
    location_collector.apply_file(str(pbf_path), locations=True)
    return collector.walkable_ways, anchors, location_collector.node_locations


def build_segment_references(walkable_ways: dict[int, list[int]], anchors: set[int]) -> list[SegmentReference]:
    segment_refs: list[SegmentReference] = []
    for way_id, node_ids in walkable_ways.items():
        segment_refs.extend(split_way_to_segments(way_id, node_ids, anchors))
    return segment_refs


def missing_locations(segment_references: Iterable[SegmentReference], node_locations: dict[int, Coordinate]) -> set[int]:
    missing: set[int] = set()
    for segment in segment_references:
        for node_id in segment.node_ids:
            if node_id not in node_locations:
                missing.add(node_id)
    return missing


def insert_road_nodes(cur, anchor_node_ids: Iterable[int], node_locations: dict[int, Coordinate], batch_size: int) -> None:
    from psycopg2.extras import execute_values

    values = []
    for node_id in anchor_node_ids:
        coord = node_locations.get(node_id)
        if coord is None:
            continue
        values.append((node_id, f"SRID=4326;POINT({coord.lon:.7f} {coord.lat:.7f})"))
    if not values:
        return
    execute_values(
        cur,
        """
        INSERT INTO road_nodes (osm_node_id, point)
        VALUES %s
        ON CONFLICT (osm_node_id) DO NOTHING
        """,
        values,
        page_size=batch_size,
    )


def fetch_vertex_ids(cur, anchor_node_ids: Iterable[int]) -> dict[int, int]:
    osm_node_ids = list(anchor_node_ids)
    if not osm_node_ids:
        return {}
    cur.execute(
        """
        SELECT osm_node_id, vertex_id
        FROM road_nodes
        WHERE osm_node_id = ANY(%s)
        """,
        (osm_node_ids,),
    )
    return {osm_node_id: vertex_id for osm_node_id, vertex_id in cur.fetchall()}


def insert_road_segments(cur, segment_references: Iterable[SegmentReference], vertex_ids: dict[int, int],
                         node_locations: dict[int, Coordinate], batch_size: int) -> int:
    from psycopg2.extras import execute_values

    rows = []
    inserted_candidates = 0
    for segment in segment_references:
        from_vertex = vertex_ids.get(segment.from_osm_node_id)
        to_vertex = vertex_ids.get(segment.to_osm_node_id)
        if from_vertex is None or to_vertex is None:
            continue

        coords = [node_locations[node_id] for node_id in segment.node_ids]
        rows.append((
            from_vertex,
            to_vertex,
            build_linestring_wkt(coords),
            measure_length_meters(coords),
            segment.way_id,
            segment.from_osm_node_id,
            segment.to_osm_node_id,
            segment.ordinal,
        ))
        inserted_candidates += 1

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO road_segments
            (from_node_id, to_node_id, geom, length_meter,
             source_way_id, source_osm_from_node_id, source_osm_to_node_id, segment_ordinal)
            VALUES %s
            ON CONFLICT (source_way_id, source_osm_from_node_id, source_osm_to_node_id) DO NOTHING
            """,
            rows,
            page_size=batch_size,
            template="(%s, %s, ST_GeomFromText(%s, 4326), %s, %s, %s, %s, %s)",
        )
    return inserted_candidates


def truncate_network_tables(cur) -> None:
    cur.execute(
        """
        TRUNCATE TABLE
            segment_attribute_match_result,
            road_segments,
            road_nodes
        RESTART IDENTITY CASCADE
        """
    )


def fetch_validation_summary(cur) -> dict[str, int]:
    cur.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM road_nodes) AS road_nodes_count,
            (SELECT COUNT(*) FROM road_segments) AS road_segments_count,
            (SELECT COUNT(*) FROM road_segments WHERE ST_IsEmpty(geom) OR geom IS NULL) AS invalid_geom_count,
            (SELECT COUNT(*) FROM (
                SELECT source_way_id, source_osm_from_node_id, source_osm_to_node_id, COUNT(*)
                FROM road_segments
                GROUP BY 1, 2, 3
                HAVING COUNT(*) > 1
            ) duplicates) AS duplicate_segment_key_count
        """
    )
    row = cur.fetchone()
    return {
        "road_nodes_count": row[0],
        "road_segments_count": row[1],
        "invalid_geom_count": row[2],
        "duplicate_segment_key_count": row[3],
    }


def run_pipeline(pbf_path: Path, truncate: bool, batch_size: int) -> dict[str, int]:
    if not pbf_path.exists():
        raise SystemExit(f"PBF file not found: {pbf_path}")
    if batch_size <= 0:
        raise SystemExit("--batch-size must be a positive integer")

    walkable_ways, anchors, node_locations = load_osm_structure(pbf_path)
    segment_references = build_segment_references(walkable_ways, anchors)

    missing = missing_locations(segment_references, node_locations)
    if missing:
        sample = ", ".join(str(node_id) for node_id in sorted(missing)[:10])
        raise SystemExit(f"Missing coordinates for {len(missing)} OSM nodes. Sample: {sample}")

    try:
        from etl.db import get_conn
    except ModuleNotFoundError:
        from db import get_conn  # type: ignore

    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                if truncate:
                    truncate_network_tables(cur)

                insert_road_nodes(cur, anchors, node_locations, batch_size)
                vertex_ids = fetch_vertex_ids(cur, anchors)
                if len(vertex_ids) != len(anchors):
                    raise SystemExit(
                        f"Inserted vertex count mismatch. expected={len(anchors)} actual={len(vertex_ids)}"
                    )
                insert_road_segments(cur, segment_references, vertex_ids, node_locations, batch_size)

                summary = fetch_validation_summary(cur)
    finally:
        conn.close()

    summary["walkable_way_count"] = len(walkable_ways)
    summary["anchor_count"] = len(anchors)
    summary["segment_reference_count"] = len(segment_references)
    return summary


def main() -> int:
    args = parse_args()
    summary = run_pipeline(Path(args.pbf), truncate=args.truncate, batch_size=args.batch_size)
    print("build-network summary")
    for key, value in summary.items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
