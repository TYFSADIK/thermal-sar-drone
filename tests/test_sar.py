import unittest

from sar.georef import Pose, pixel_to_ground
from sar.pipeline import DetectionMap, process_frame
from sar.thermal import find_hotspots, synthetic_frame


class TestSAR(unittest.TestCase):
    def test_finds_people_not_snow(self):
        self.assertEqual(len(find_hotspots(synthetic_frame(people=((40, 30), (120, 90))))), 2)
        self.assertEqual(find_hotspots(synthetic_frame(people=())), [])

    def test_centre_pixel_is_under_drone(self):
        lat, lon, _ = pixel_to_ground(80, 60, Pose(45.0, -75.0, 60, 0))
        self.assertAlmostEqual(lat, 45.0, places=6)
        self.assertAlmostEqual(lon, -75.0, places=6)

    def test_top_of_image_is_forward(self):
        lat, _, _ = pixel_to_ground(80, 0, Pose(45.0, -75.0, 60, 0))
        self.assertGreater(lat, 45.0)

    def test_repeat_sightings_merge(self):
        m, pose = DetectionMap(), Pose(45.0, -75.0, 60, 0)
        for i in range(3):
            process_frame(synthetic_frame(people=((80, 60),)), pose, m, t=i)
        self.assertEqual(len(m.items), 1)
        self.assertEqual(m.items[0]["hits"], 3)


if __name__ == "__main__":
    unittest.main()
