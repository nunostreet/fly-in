from pathlib import Path
from models.world import World
from models.hub import Hub
from models.connection import Connection
from models.zone import ZoneType


class MapParser:
    """Parse Fly-in map files into validated world objects.

    The parser reads a map definition line by line, validates its structure,
    and builds a ``World`` instance containing hubs, connections, and global
    map settings.
    """

    def parse_file(self, filepath: str) -> World:
        """Parse a map file and return the validated ``World`` state.

        Args:
            filepath: Path to the map file that should be parsed.

        Returns:
            A validated ``World`` instance populated with the parsed data.

        Raises:
            FileNotFoundError: If the map file does not exist.
            ValueError: If the file cannot be read or contains invalid data.
        """

        world = World()
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Map file not found {filepath}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except IOError as exc:
            raise ValueError(f"Failed to read file: {exc}") from exc

        # Read line by line
        for line_number, line in enumerate(lines, start=1):

            # Ignore empty lines and comments
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith('#'):
                continue

            # Split the line into prefix and rest
            prefix, _, rest = stripped_line.partition(":")

            if prefix == "nb_drones":
                self.parse_drones(rest.strip(), line_number, world)

            elif prefix in ("hub", "start_hub", "end_hub"):
                self.parse_hub(rest.strip(), prefix, line_number, world)

            elif prefix == "connection":
                self.parse_connection(rest.strip(), line_number, world)

            else:
                raise ValueError(
                    f"Unknown line type at line {line_number}"
                    )

        self.check_world(world)

        return world

    @staticmethod
    def parse_drones(rest: str, line_number: int, world: World) -> None:
        """Parse the drone count line and store it in the ``World``.

        Args:
            rest: Raw value that follows the "nb_drones:" prefix.
            line_number: Line number being parsed.
            world: ``World`` instance being populated.

        Raises:
            ValueError: If the drone count is invalid or duplicated.
        """

        try:
            nb = int(rest.strip())
        except ValueError:
            raise ValueError(f"Invalid number of drones at line {line_number}")

        if nb <= 0:
            raise ValueError(
                f"# of drones must be positive (line {line_number})"
                )

        if nb > 1000:
            raise ValueError(
                f"# of drones must be less than 1000 (line {line_number})"
                )

        if world.nb_drones is not None:
            raise ValueError(f"Duplicate nb_drones def. at line {line_number}")

        world.nb_drones = nb

    def parse_hub(
            self, rest: str, prefix: str, line_number: int, world: World
            ) -> None:
        """Parse a hub definition and register it in the ``World``.

        Args:
            rest: Raw hub definition after the line prefix.
            prefix: Hub line prefix.
            line_number: Line number being parsed.
            world: ``World`` instance being populated.

        Raises:
            ValueError: If the hub data is incomplete, invalid, or duplicated.
        """

        parts = rest.split(maxsplit=3)
        if len(parts) < 3:
            raise ValueError(f"Insufficient hub data in line {line_number}")

        name, x, y, *r_parts = parts

        try:
            x_int = int(x)
            y_int = int(y)
        except ValueError as exc:
            raise ValueError(
                f"Invalid hub coordinates at line {line_number}") from exc

        # Hub names must be unique across the whole map.
        if name in world.hubs:
            raise ValueError(f"Duplicate hub at line {line_number}")

        if "-" in name:
            raise ValueError(f"Hub names can't have '-' (line {line_number})")

        # The map must define at most one start hub and one end hub.
        if prefix == "start_hub" and world.start_hub_name is not None:
            raise ValueError(f"Duplicate start_hub at line {line_number}")
        elif prefix == "start_hub":
            world.start_hub_name = name
        if prefix == "end_hub" and world.end_hub_name is not None:
            raise ValueError(f"Duplicate end_hub at line {line_number}")
        elif prefix == "end_hub":
            world.end_hub_name = name

        # Parse the optional hub metadata block when present.
        if r_parts:
            if r_parts[0].startswith("[") and r_parts[0].endswith("]"):
                metadata = self._process_metadata(r_parts[0])
            else:
                raise ValueError(f"Invalid metadata at line {line_number}")
        else:
            metadata = {}

        allowed_metadata = {"zone", "color", "max_drones"}

        for key in metadata:
            if key not in allowed_metadata:
                raise ValueError(
                    f"Unknown hub metadata '{key}' at line {line_number}"
                )

        try:
            max_drones = int(metadata.get("max_drones", 1))
        except ValueError as exc:
            raise ValueError(
                f"Invalid max_drones value at line {line_number}"
            ) from exc

        if max_drones <= 0:
            raise ValueError(
                f"max_drones must be positive at line {line_number}"
            )

        try:
            zone = ZoneType(metadata.get("zone", "normal"))
        except ValueError as exc:
            raise ValueError(
                f"Invalid zone value at line {line_number}"
            ) from exc

        # Store the fully validated hub in the parsed world.
        world.hubs[name] = Hub(
            name=name,
            x=x_int,
            y=y_int,
            zone=zone,
            color=metadata.get("color", "none"),
            max_drones=max_drones,
            start=(prefix == "start_hub"),
            end=(prefix == "end_hub")
        )

    def parse_connection(
            self, rest: str, line_number: int, world: World
            ) -> None:
        """Parse a connection definition and add it to the ``World``.

        Args:
            rest: Raw connection definition after the line prefix.
            line_number: Line number being parsed.
            world: ``World`` instance being populated.

        Raises:
            ValueError: If the connection is invalid, duplicated, or references
                unknown hubs.
        """

        if not rest.strip():
            raise ValueError(
                f"Empty connection definition at line {line_number}"
                )

        parts = rest.split(maxsplit=1)
        metadata: dict[str, str] = {}

        # Parse optional connection metadata after the ``origin-destiny`` part.
        if parts[0].count("-") != 1:
            raise ValueError(
                    "Connection should be in origin-destiny format. "
                    f"Line: {line_number}"
                    )

        origin, destiny = parts[0].split("-")

        if not origin or not destiny:
            raise ValueError("Connection origin and destination can't"
                             f"be empty (line {line_number})")

        if len(parts) > 1:
            metadata = self._process_metadata(parts[1])

        if origin == destiny:
            raise ValueError(f"Self loops not allowed. Line: {line_number}")

        # Connections may only reference hubs that were already defined.
        if origin not in world.hubs and destiny not in world.hubs:
            raise ValueError(
                f"Invalid connection at line {line_number}. "
                f"Both hubs '{origin}' and '{destiny}' do not exist."
            )
        if origin not in world.hubs:
            raise ValueError(
                f"Invalid connection at line {line_number}. "
                f"Origin hub '{origin}' does not exist."
            )
        if destiny not in world.hubs:
            raise ValueError(
                f"Invalid connection at line {line_number}. "
                f"Destination hub '{destiny}' does not exist."
            )

        allowed_metadata = {"max_link_capacity"}

        for key in metadata:
            if key not in allowed_metadata:
                raise ValueError(
                    f"Unknown connection metadata '{key}'"
                    f" at line {line_number}"
                )

        try:
            max_link_capacity = int(metadata.get("max_link_capacity", 1))
        except ValueError as exc:
            raise ValueError(
                f"Invalid max_link_capacity value at line {line_number}"
            ) from exc

        if max_link_capacity <= 0:
            raise ValueError(
                f"max_link_capacity must be positive at line {line_number}"
            )

        new_connection_key = self._connection_key(origin, destiny)
        existing_connection_keys = {
            self._connection_key(connection.source, connection.target)
            for connection in world.connections
        }
        if new_connection_key in existing_connection_keys:
            raise ValueError(f"Duplicate connection at line {line_number}.")

        # Store the fully validated connection in the parsed world.
        world.connections.append(Connection(
            source=origin,
            target=destiny,
            max_link_capacity=max_link_capacity
            )
        )

    @staticmethod
    def _process_metadata(metadata: str) -> dict[str, str]:
        """Convert a metadata block into a dictionary.

        Args:
            metadata: Metadata text such as ``[color=green max_drones=4]``.

        Returns:
            A dictionary containing the parsed metadata key-value pairs.

        Raises:
            ValueError: If the metadata format is invalid.
        """

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

    @staticmethod
    def _connection_key(origin: str, destiny: str) -> tuple[str, str]:
        """Return a normalized key for undirected connection comparison.

        Args:
            origin: Name of the source hub.
            destiny: Name of the destination hub.

        Returns:
            A sorted tuple that treats ``A-B`` and ``B-A`` as the same
            connection.
        """

        first, second = sorted((origin, destiny))
        return first, second

    def check_world(self, world: World) -> None:
        """Validate that the parsed world contains the required sections.

        Args:
            world: Parsed world to validate.

        Raises:
            ValueError: If required sections are missing from the world.
        """

        if world.nb_drones is None:
            raise ValueError("No valid number of drones found")
        if world.start_hub_name is None:
            raise ValueError("No starting point found")
        if world.end_hub_name is None:
            raise ValueError("No ending point found")
        if world.start_hub_name == world.end_hub_name:
            raise ValueError("Start and end can't be in the same hub.")
        if not world.connections:
            raise ValueError("No connection between hubs found")
