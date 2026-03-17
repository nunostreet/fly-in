from dataclasses import dataclass


@dataclass
class Connection:
    """Represent a connection between two hubs.

    Attributes:
        source: Name of the source hub.
        target: Name of the target hub.
        metadata: Optional connection configuration from the map file.
    """

    source: str
    target: str
    metadata: dict[str, str]
