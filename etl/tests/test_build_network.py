import unittest

from etl.build_network import Coordinate
from etl.build_network import build_linestring_wkt
from etl.build_network import identify_anchors
from etl.build_network import is_walkable
from etl.build_network import measure_length_meters
from etl.build_network import split_way_to_segments


class BuildNetworkLogicTest(unittest.TestCase):

    def test_is_walkable_respects_include_rules(self):
        self.assertTrue(is_walkable({"highway": "footway"}))
        self.assertTrue(is_walkable({"foot": "designated"}))
        self.assertTrue(is_walkable({"sidewalk": "both"}))

    def test_is_walkable_respects_exclude_rules(self):
        self.assertFalse(is_walkable({"highway": "motorway"}))
        self.assertFalse(is_walkable({"highway": "footway", "access": "private"}))
        self.assertFalse(is_walkable({"highway": "service", "foot": "no"}))

    def test_identify_anchors_combines_endpoints_intersections_and_tagged_nodes(self):
        walkable_ways = {
            1: [10, 20, 30],
            2: [30, 40, 50],
        }
        node_way_count = {
            10: 1,
            20: 1,
            30: 2,
            40: 1,
            50: 1,
            99: 1,
        }
        anchors = identify_anchors(walkable_ways, node_way_count, {99})
        self.assertEqual({10, 30, 50, 99}, anchors)

    def test_split_way_to_segments_breaks_only_on_anchor_nodes(self):
        anchors = {1, 3, 5}
        segments = split_way_to_segments(42, [1, 2, 3, 4, 5], anchors)
        self.assertEqual(2, len(segments))
        self.assertEqual((1, 2, 3), segments[0].node_ids)
        self.assertEqual((3, 4, 5), segments[1].node_ids)
        self.assertEqual(0, segments[0].ordinal)
        self.assertEqual(1, segments[1].ordinal)

    def test_build_linestring_wkt_preserves_lon_lat_order(self):
        wkt = build_linestring_wkt([
            Coordinate(lon=129.0, lat=35.0),
            Coordinate(lon=129.1, lat=35.1),
        ])
        self.assertEqual("LINESTRING(129.0000000 35.0000000, 129.1000000 35.1000000)", wkt)

    def test_measure_length_meters_returns_positive_distance(self):
        distance = measure_length_meters([
            Coordinate(lon=129.0756, lat=35.1796),
            Coordinate(lon=129.0760, lat=35.1800),
        ])
        self.assertGreater(distance, 0.0)


if __name__ == "__main__":
    unittest.main()
