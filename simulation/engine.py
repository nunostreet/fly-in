from dataclasses import dataclass
from models.world import World
from models.drone import Drone
from typing import List


@dataclass
class SimulationResult:
    turns: int
    lines: list[str]


class SimulationEngine:
    def __init__(
        self, world: World,
        start: str,
        goal: str,
        nb_drones: int,
        scheduler: None
    ) -> None:
        self._world = world
        self._start = start
        self._goal = goal
        self._nb_drones = nb_drones
        self._scheduler = scheduler

    def _init_drones(self) -> List[Drone]:
        return [Drone(id=i, path_index=World.start_hub_name)
                for i in range(1, self._nb_drones + 1)]
