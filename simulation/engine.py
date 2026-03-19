from dataclasses import dataclass
from models.world import World
from models.drone import Drone
from routing.router import Router
from typing import List


@dataclass
class SimulationResult:
    turns: int
    lines: list[str]


class SimulationEngine:
    def __init__(self, world: World) -> None:
        self._world = world
        self._router = Router()

    def run(self) -> SimulationResult:
        path = self._router.find_path(self._world)
        if not path:
            return SimulationResult(turns=0, lines=[])

        drones = self._init_drones()
        lines: list[str] = []
        turns = 0

        while not self._all_finished(drones):
            turn_moves = self._run_turn(drones, path)

            if turn_moves:
                lines.append(" ".join(turn_moves))

            turns += 1

        return SimulationResult(turns=turns, lines=lines)

    def _init_drones(self) -> List[Drone]:
        nb_drones = self._world.nb_drones or 0
        return [Drone(id=i) for i in range(1, nb_drones + 1)]

    def _run_turn(self, drones: list[Drone], path: list[str]) -> List[str]:
        moves: list[str] = []

        for drone in drones:
            if drone.finished:
                continue

            move = self._move_drone(drone, path)
            if move is not None:
                moves.append(move)

        return moves

    def _move_drone(self, drone: Drone, path: list[str]) -> str | None:

      
        return None

    def _all_finished(self, drones: list[Drone]) -> bool:
        return all(drone.finished for drone in drones)
