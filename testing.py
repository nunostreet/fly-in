# flake8: noqa

from parser import MapParser

def test_map(path: str) -> None:
    parser = MapParser()

    try:
        world = parser.parse_file(path)
        print(f"[OK] {path}")
        for hub in world.hubs:
            print(hub)
        for conn in world.connections:
            print(conn.source)
        graph: dict[str, list[str]] = {}

        for hub_name in world.hubs:
            graph[hub_name] = []

        for conn in world.connections:
            graph[conn.source].append(conn.target)
            graph[conn.target].append(conn.source)
        print(graph)


    except Exception as exc:
        print(f"[ERROR] {path}: {exc}")

def main() -> None:
    test_map("maps/easy/02_simple_fork.txt")

if __name__ == "__main__":
    main()
