from dataclasses import dataclass
from .zone import ZoneType


@dataclass
class Hub:
    """Represent a hub node in the parsed map.

    Attributes:
        name: Unique hub identifier.
        x: Horizontal hub coordinate.
        y: Vertical hub coordinate.
        metadata: Optional hub configuration extracted from the map file.
        start: Whether this hub is the map starting point.
        end: Whether this hub is the map ending point.
    """

    name: str = ""
    x: int = 0
    y: int = 0
    zone: ZoneType = ZoneType.NORMAL
    color: str = "none"
    max_drones: int = 1
    start: bool = False
    end: bool = False
