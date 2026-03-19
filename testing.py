# flake8: noqa

from parser import MapParser
from routing.router import Router


def test_map(path: str) -> None:
    parser = MapParser()
    router = Router()

    try:
        world = parser.parse_file(path)
        print(f"[OK] {path}")
        graph = router.build_graph(world)
        path_found = router.find_path(world)

        print(f"Graph: {graph}")
        print(f"Path: {path_found}")

    except Exception as exc:
        print(f"[ERROR] {path}: {exc}")


def main() -> None:
    test_map("maps/easy/01_linear_path.txt")
    print()


if __name__ == "__main__":
    main()
