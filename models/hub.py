from dataclasses import dataclass, field


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
    metadata: dict[str, str] = field(default_factory=dict)
    start: bool = False
    end: bool = False
