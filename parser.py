import sys
from typing import Any
from models.world import World


def parse_file() -> dict[str, Any] | None:
    """Parse and validate the map files.

    Returns:
        Validated configuration dictionary, or 'None' when parsing fails.
    """

    with open(sys.argv[1]) as file:

        world = World()

        # Ler linha a linha
        for line_number, line in enumerate(file, start=1):
            stripped_line = line.strip()

            if not stripped_line or stripped_line.startswith('#'):
                continue

            prefix, _, rest = stripped_line.partition(":")

            if prefix == "nb_drones":
                parse_drones(rest.strip(), line_number, world)

            elif prefix in ("hub", "start_hub", "end_hub"):
                parse_hub(rest.strip(), prefix, line_number, world)

            elif prefix == "connection":
                parse_connection(rest.strip(), line_number, world)

            else:
                return ValueError(
                    f"Unknown line type at line {line_number}"
                    )

    return None  # temporary


def parse_drones(rest: str, line_number: int, world):
    try:
        nb = int(rest.strip())
    except ValueError:
        raise ValueError(f"Invalid number of drones at line {line_number}")

    if nb <= 0:
        raise ValueError(f"# of drones must be positive (line {line_number})")

    if world.nb_drones is not None:
        raise ValueError(f"Duplicate nb_drones def. at line {line_number}")

    world.nb_drones = nb
