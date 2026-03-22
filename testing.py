# flake8: noqa

from parser import MapParser
from routing.router import Router
from simulation.engine import SimulationEngine


def test_map(path: str) -> None:
    parser = MapParser()
    router = Router()

    try:
        world = parser.parse_file(path)
        graph = router.build_graph(world)
        path_found = router.find_path(world)
        result = SimulationEngine(world).run()

        print(f"[OK] {path}")
        print("World:")
        print(
            f"  nb_drones={world.nb_drones} "
            f"start={world.start_hub_name} end={world.end_hub_name}"
        )
        print(
            f"  total_hubs={len(world.hubs)} "
            f"total_connections={len(world.connections)}"
        )
        print()

        print("Hubs:")
        for hub_name, hub in world.hubs.items():
            print(
                f"  {hub_name}: x={hub.x} y={hub.y} "
                f"zone={hub.zone} color={hub.color} "
                f"max_drones={hub.max_drones} "
                f"start={hub.start} end={hub.end}"
            )
        print()

        print("Connections:")
        for connection in world.connections:
            print(
                f"  {connection.source} <-> {connection.target} "
                f"max_link_capacity={connection.max_link_capacity}"
            )
        print()

        print("Graph:")
        print(f"  {graph}")
        print()

        print("Path:")
        print(f"  {path_found}")
        print()

        print("Simulation:")
        print(f"  turns={result.turns}")
        for line in result.lines:
            print(f"  {line}")
        print()

    except Exception as exc:
        print(f"[ERROR] {path}: {exc}")


def test_group(title: str, paths: list[str]) -> None:
    print(title)
    for path in paths:
        test_map(path)
    print()


def main() -> None:
    focused_maps = [
        "maps/test_blocked.txt",
        "maps/test_restricted.txt",
        "maps/test_priority.txt"
    ]

    test_group("=== FOCUSED MAPS ===", focused_maps)


if __name__ == "__main__":
    main()
