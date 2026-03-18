from dataclasses import dataclass, field
from .hub import Hub
from .connection import Connection


@dataclass
class World:
    """Represent the full parsed map state.

    Attributes:
        nb_drones: Total number of drones available in the simulation.
        hubs: Mapping of hub names to their parsed hub definitions.
        connections: List of parsed connections between hubs.
        start_hub_name: Name of the starting hub, when defined.
        end_hub_name: Name of the ending hub, when defined.
    """

    nb_drones: int | None = None
    hubs: dict[str, Hub] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)
    start_hub_name: str | None = None
    end_hub_name: str | None = None
