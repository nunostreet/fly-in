from dataclasses import dataclass


@dataclass
class Connection:
    """Represent a connection between two hubs.

    Attributes:
        source: Name of the source hub.
        target: Name of the target hub.
        max_link_capacity: Maximum number of drones that may traverse the
            connection simultaneously.
    """

    source: str
    target: str
    max_link_capacity: int = 1
