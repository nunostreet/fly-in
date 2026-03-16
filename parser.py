# flake8: noqa

import sys
from typing import Any
from pathlib import Path
from models.world import World
from models.hub import Hub
from dataclasses import dataclass


@dataclass
class MapParser:
    """
    Fly-in map parser
    
    Return: [TO BE ADDED]!!
    """
    def parse_file(self, filepath: str) -> dict[str, Any] | None:
        """Parse and validate the map files.

        Returns:
            Validated configuration dictionary, or 'None' when parsing fails.
        """

        world = World()
        hub = Hub()
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Map file not found {filepath}")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except IOError as exc:
            raise ValueError(f"Failed to read file: {exc}") from exc
        
        # Ler linha a linha
        for line_number, line in enumerate(lines, start=1):

            # Ignore empty lines and comments
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith('#'):
                continue

            # Split the line into prefix and rest
            prefix, _, rest = stripped_line.partition(":")

            if prefix == "nb_drones":
                parse_drones(rest.strip(), line_number, world)

            elif prefix in ("hub", "start_hub", "end_hub"):
                parse_hub(rest.strip(), prefix, line_number, hub)

            elif prefix == "connection":
                parse_connection(rest.strip(), line_number, world)

            else:
                raise ValueError(
                    f"Unknown line type at line {line_number}"
                    )

        return None  # temporary

    @staticmethod
    def parse_drones(rest: str, line_number: int, world: World):
        try:
            nb = int(rest.strip())
        except ValueError:
            raise ValueError(f"Invalid number of drones at line {line_number}")

        if nb <= 0:
            raise ValueError(f"# of drones must be positive (line {line_number})")

        if world.nb_drones is not None:
            raise ValueError(f"Duplicate nb_drones def. at line {line_number}")

        world.nb_drones = nb


    def parse_hub(self, rest: str, prefix: str, line_number: int, hub: Hub) -> None:  
        
        name, x, y, metadata = rest.split()

        hub.name = name
        hub.x = int(x)
        hub.y = int(y)
        hub.metadata = _process_metadata(metadata)


    # def parse_connection(rest: str, line_number: int, world: World):


    @staticmethod
    def _process_metadata(metadata: str) -> dict[str, str]:
        if not metadata:
            return {}

        text = metadata.strip()
        if not (text.startswith("[") and text.endswith("]")):
            raise ValueError("Metadata must be enclosed in brackets")

        content = text[1:-1].strip()
        if not content:
            return {}

        result: dict[str, str] = {}

        for pair in content.split():
            if "=" not in pair:
                raise ValueError(f"Invalid metadata pair: {pair}")

            key, value = pair.split("=", 1)
            if not key:
                raise ValueError("Metadata key cannot be empty")

            result[key] = value

        return result
