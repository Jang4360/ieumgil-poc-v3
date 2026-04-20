CREATE EXTENSION IF NOT EXISTS postgis;

DO $$
BEGIN
    CREATE TYPE accessibility_state AS ENUM ('YES', 'NO', 'UNKNOWN');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE width_state_t AS ENUM ('ADEQUATE_150', 'ADEQUATE_120', 'NARROW', 'UNKNOWN');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE surface_state_t AS ENUM ('PAVED', 'GRAVEL', 'UNPAVED', 'OTHER', 'UNKNOWN');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE crossing_state_t AS ENUM ('TRAFFIC_SIGNALS', 'UNCONTROLLED', 'UNMARKED', 'NO', 'UNKNOWN');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE disability_type_t AS ENUM ('VISUAL', 'MOBILITY');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE route_option_t AS ENUM ('SAFE_WALK', 'FAST_WALK', 'ACCESSIBLE_TRANSIT');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS road_nodes (
    vertex_id BIGSERIAL PRIMARY KEY,
    osm_node_id BIGINT NOT NULL UNIQUE,
    point GEOMETRY(POINT, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_road_nodes_point ON road_nodes USING GIST(point);

CREATE TABLE IF NOT EXISTS road_segments (
    edge_id BIGSERIAL PRIMARY KEY,
    from_node_id BIGINT NOT NULL REFERENCES road_nodes(vertex_id),
    to_node_id BIGINT NOT NULL REFERENCES road_nodes(vertex_id),
    geom GEOMETRY(LINESTRING, 4326) NOT NULL,
    length_meter NUMERIC(10,2) NOT NULL,
    source_way_id BIGINT NOT NULL,
    source_osm_from_node_id BIGINT NOT NULL,
    source_osm_to_node_id BIGINT NOT NULL,
    segment_ordinal INT NOT NULL DEFAULT 0,
    walk_access VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN',
    avg_slope_percent NUMERIC(6,2),
    width_meter NUMERIC(6,2),
    braille_block_state accessibility_state NOT NULL DEFAULT 'UNKNOWN',
    audio_signal_state accessibility_state NOT NULL DEFAULT 'UNKNOWN',
    curb_ramp_state accessibility_state NOT NULL DEFAULT 'UNKNOWN',
    width_state width_state_t NOT NULL DEFAULT 'UNKNOWN',
    surface_state surface_state_t NOT NULL DEFAULT 'UNKNOWN',
    stairs_state accessibility_state NOT NULL DEFAULT 'UNKNOWN',
    elevator_state accessibility_state NOT NULL DEFAULT 'UNKNOWN',
    crossing_state crossing_state_t NOT NULL DEFAULT 'UNKNOWN',
    UNIQUE (source_way_id, source_osm_from_node_id, source_osm_to_node_id)
);

CREATE INDEX IF NOT EXISTS idx_road_segments_geom ON road_segments USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_road_segments_way ON road_segments(source_way_id);
CREATE INDEX IF NOT EXISTS idx_road_segments_nodes ON road_segments(from_node_id, to_node_id);

CREATE TABLE IF NOT EXISTS segment_attribute_match_result (
    id BIGSERIAL PRIMARY KEY,
    edge_id BIGINT NOT NULL REFERENCES road_segments(edge_id),
    attribute VARCHAR(50) NOT NULL,
    matched BOOLEAN NOT NULL,
    confidence VARCHAR(10),
    distance_meter NUMERIC(8,2),
    source_dataset VARCHAR(100),
    matched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_match_result_edge ON segment_attribute_match_result(edge_id);

CREATE TABLE IF NOT EXISTS low_floor_bus_routes (
    route_id VARCHAR(20) PRIMARY KEY,
    route_no VARCHAR(20) NOT NULL,
    has_low_floor BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS subway_station_elevators (
    elevator_id BIGSERIAL PRIMARY KEY,
    station_id VARCHAR(20) NOT NULL,
    station_name VARCHAR(100) NOT NULL,
    line_name VARCHAR(50) NOT NULL,
    entrance_no VARCHAR(10),
    point GEOMETRY(POINT, 4326) NOT NULL,
    is_operating BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_subway_elev_station ON subway_station_elevators(station_id);
CREATE INDEX IF NOT EXISTS idx_subway_elev_point ON subway_station_elevators USING GIST(point);
