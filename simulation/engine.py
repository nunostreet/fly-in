from dataclasses import dataclass
from models.world import World
from models.drone import Drone
from routing.router import Router
from typing import List


@dataclass
class SimulationResult:
    """Store the simulation output in turn-by-turn text form."""

    turns: int
    lines: list[str]


class SimulationEngine:
    """Run a simple multi-drone simulation over a routed path."""

    def __init__(self, world: World) -> None:
        """Initialize the engine with a parsed world."""

        self._world = world
        self._router = Router()

    def run(self) -> SimulationResult:
        """Simulate drone movement until every drone reaches the goal.

        Returns:
            A ``SimulationResult`` containing the number of turns and the
            formatted movement lines for each turn.
        """

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
        """Create one drone instance per configured drone in the world."""

        nb_drones = self._world.nb_drones or 0
        return [Drone(id=i) for i in range(1, nb_drones + 1)]

    def _run_turn(self, drones: list[Drone], path: list[str]) -> List[str]:
        """Advance each unfinished drone by one step along the path.

        Each drone can move at most one hub per turn. The returned strings
        are later joined into the output line for that turn.
        """

        moves: list[str] = []

        for drone in drones:
            if drone.finished:
                continue

            move = self._move_drone(drone, path)
            if move is not None:
                moves.append(move)

        return moves

    def _move_drone(self, drone: Drone, path: list[str]) -> str | None:
        """Move a single drone to the next hub in the path.

        The ``path_index`` points to the drone's current position in the
        shared path. Advancing by one means moving from the current hub to the
        next hub for this turn only.

        Returns:
            A formatted move like ``D1-junction`` when the drone advances, or
            ``None`` when no movement is possible.
        """

        if drone.path_index >= len(path) - 1:
            drone.finished = True
            return None

        drone.path_index += 1
        next_hub = path[drone.path_index]

        if drone.path_index == len(path) - 1:
            drone.finished = True

        return f"D{drone.id}-{next_hub}"

    def _all_finished(self, drones: list[Drone]) -> bool:
        """Return ``True`` when every drone has reached the final hub."""

        return all(drone.finished for drone in drones)
