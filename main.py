import argparse
import sys

from parser import MapParser
from simulation.engine import SimulationEngine


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("map_file")
    parser.add_argument("--run-viz", action="store_true")
    args = parser.parse_args()

    try:
        if args.run_viz:
            from visualization.render import RenderApp

            app = RenderApp(args.map_file)
            app.run()
            return

        world = MapParser().parse_file(args.map_file)
        result = SimulationEngine(world).run()

        for line in result.lines:
            print(line)

    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
