from dataclasses import dataclass
from .world import World


@dataclass
class Drone():
    id: int = 1
    path_index: str | None = World.start_hub_name
    finished: bool = False
