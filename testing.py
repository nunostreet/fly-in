# flake8: noqa

from parser import MapParser

def test_map(path: str) -> None:
    parser = MapParser()

    try:
        world = parser.parse_file(path)
        print(f"[OK] {path}")
        print(world)
    except Exception as exc:
        print(f"[ERROR] {path}: {exc}")

def main() -> None:
    test_map("maps/easy/01_linear_path.txt")
    print()
    test_map("maps/easy/02_simple_fork.txt")
    print()
    test_map("maps/easy/03_basic_capacity.txt")
    print()


if __name__ == "__main__":
    main()
