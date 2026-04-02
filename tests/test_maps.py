import unittest
from pathlib import Path

from parser import MapParser
from simulation.engine import SimulationEngine


ROOT_DIR = Path(__file__).resolve().parent.parent
MAPS_DIR = ROOT_DIR / "maps"

VALID_MAPS = sorted(
    path for path in MAPS_DIR.rglob("*.txt") if "error" not in path.parts
)
ERROR_MAPS = sorted(
    path for path in MAPS_DIR.rglob("*.txt") if "error" in path.parts
)


class TestValidMaps(unittest.TestCase):
    def test_all_non_error_maps_parse_and_simulate(self) -> None:
        self.assertTrue(VALID_MAPS, "Expected at least one valid map")

        for map_path in VALID_MAPS:
            with self.subTest(map=map_path.relative_to(ROOT_DIR)):
                world = MapParser().parse_file(str(map_path))
                result = SimulationEngine(world).run()

                self.assertIsNotNone(world.start_hub_name)
                self.assertIsNotNone(world.end_hub_name)
                self.assertGreater(len(result.path), 0)
                self.assertEqual(result.path[0], world.start_hub_name)
                self.assertEqual(result.path[-1], world.end_hub_name)
                self.assertEqual(len(result.snapshots), result.turns + 1)


class TestErrorMaps(unittest.TestCase):
    def test_all_error_maps_fail_somewhere_in_the_pipeline(self) -> None:
        self.assertTrue(ERROR_MAPS, "Expected at least one error map")

        for map_path in ERROR_MAPS:
            with self.subTest(map=map_path.relative_to(ROOT_DIR)):
                with self.assertRaises(Exception):
                    world = MapParser().parse_file(str(map_path))
                    SimulationEngine(world).run()


if __name__ == "__main__":
    unittest.main()
