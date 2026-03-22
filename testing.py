# flake8: noqa

from parser import MapParser
from routing.router import Router
from simulation.engine import SimulationEngine


def test_map(path: str) -> None:
    parser = MapParser()
    router = Router()

    try:
        world = parser.parse_file(path)
        print(f"[OK] {path}")
        graph = router.build_graph(world)
        path_found = router.find_path(world)
        result = SimulationEngine(world).run()

        print(f"Graph: {graph}")
        print(f"Path: {path_found}")
        print(f"Simulation turns: {result.turns}")
        print("Simulation lines:")
        for line in result.lines:
            print(line)

    except Exception as exc:
        print(f"[ERROR] {path}: {exc}")


def main() -> None:
    test_map("maps/easy/02_simple_fork.txt")
    print()


if __name__ == "__main__":
    main()
