from dataclasses import dataclass
from models.world import World
from models.drone import Drone
from models.zone import ZoneType
from routing.router import Router
from typing import List


@dataclass
class SimulationResult:
    """Store the simulation output in turn-by-turn text form."""

    turns: int
    lines: list[str]


class SimulationEngine:
    """Run a simple multi-drone simulation over a routed path.

    The engine currently makes every drone follow the same path returned by
    the router. It tracks hub occupancy across turns and link usage within a
    single turn so that hub and connection capacities can block movement.
    Moving into a restricted hub takes an extra turn, so drones may be marked
    as in transit between turns before they arrive at the destination hub.
    """

    def __init__(self, world: World) -> None:
        """Initialize the engine with a parsed world."""

        self._world = world
        self._router = Router()
        self._hub_occupancy = {hub_name: 0 for hub_name in self._world.hubs}
        self._connections = {}

        for connection in self._world.connections:
            key = self._connection_key(connection.source, connection.target)
            self._connections[key] = connection

    def run(self) -> SimulationResult:
        """Simulate drone movement until every drone reaches the goal.

        Returns:
            A ``SimulationResult`` containing the number of turns and the
            formatted movement lines for each turn.
        """

        # Solution path with each hub from start to goal
        path = self._router.find_path(self._world)
        if not path:
            raise RuntimeError("No solution found")

        drones = self._init_drones()
        lines: list[str] = []
        turns = 0

        while not self._all_finished(drones):
            turn_moves, made_progress = self._run_turn(drones, path)

            if turn_moves:
                lines.append(" ".join(turn_moves))
            elif not made_progress:
                raise RuntimeError(
                    f"No drone could move this turn (turn: {turns})"
                )

            turns += 1

        return SimulationResult(turns=turns, lines=lines)

    def _init_drones(self) -> List[Drone]:
        """Create one drone instance per configured drone in the world.

        All drones start at the world's start hub, so the initial occupancy of
        that hub is set to the total number of drones.
        """

        nb_drones = self._world.nb_drones or 0
        start_hub_name = self._world.start_hub_name
        end_hub_name = self._world.end_hub_name

        if start_hub_name is None:
            return []

        if end_hub_name is None:
            return []

        drones: list[Drone] = []

        for i in range(1, nb_drones + 1):
            drones.append(
                Drone(
                    id=i,
                    current_hub=start_hub_name,
                    path_index=0,
                    waiting=False,
                    finished=False
                )
            )

        # Record number of drones initially
        self._hub_occupancy[start_hub_name] = nb_drones

        # Update max drones for both start and end hubs,
        # which have no restrictions
        start_hub = self._world.hubs[start_hub_name]
        start_hub.max_drones = nb_drones
        end_hub = self._world.hubs[end_hub_name]
        end_hub.max_drones = nb_drones

        return drones

    def _run_turn(
            self, drones: list[Drone], path: list[str]
            ) -> tuple[List[str], bool]:
        """Advance the simulation by one turn.

        Drones that were already traveling to a restricted hub are resolved
        first. After that, drones that are idle may attempt to start a new
        movement. The returned strings are joined into the output line for the
        current turn.
        """

        moves: list[str] = []
        made_progress = False

        # Track how many drones have already used each connection this turn.
        link_usage: dict[tuple[str, str], int] = {}

        # Track which drones have been moved that were in transit
        processed_ids: set[int] = set()

        # 1. We prioritise drones that were already in transit
        for drone in drones:
            if not drone.in_transit:
                continue

            if drone.next_hub is None:
                continue

            next_hub_name = drone.next_hub
            drone.current_hub = next_hub_name
            drone.next_hub = None
            drone.in_transit = False
            drone.path_index += 1
            made_progress = True

            if drone.path_index == len(path) - 1:
                drone.finished = True

            moves.append(f"D{drone.id}-{next_hub_name}")
            processed_ids.add(drone.id)

        for drone in drones:
            if drone.id in processed_ids or drone.finished or drone.in_transit:
                continue

            move, progressed = self._move_drone(drone, path, link_usage)
            made_progress = made_progress or progressed
            if move is not None:
                moves.append(move)

        return moves, made_progress

    def _move_drone(
            self,
            drone: Drone,
            path: list[str],
            link_usage: dict[tuple[str, str], int]
            ) -> tuple[str | None, bool]:
        """Try to start moving a single drone toward the next hub in the path.

        The ``path_index`` points to the drone's current position in the
        shared path. A drone may be forced to wait if the next hub is already
        full or if the connection has no remaining capacity in the current
        turn. Entering a restricted hub begins a movement that only completes
        in the following turn.

        Returns:
            A formatted move like ``D1-junction`` when the drone arrives at a
            hub in the current turn, or ``None`` when no completed arrival is
            produced.
        """

        # 1. Check if we reached the end
        if drone.path_index >= len(path) - 1:
            drone.finished = True
            return None, False

        # 2. Find where the drone is
        current_hub_name = drone.current_hub
        if current_hub_name is None:
            return None, False

        # 3. Find where it needs to go
        next_hub_name = path[drone.path_index + 1]
        next_hub = self._world.hubs[next_hub_name]

        # The drone must wait if the destination hub is already full.
        if self._hub_occupancy[next_hub_name] >= next_hub.max_drones:
            drone.waiting = True
            return None, False

        # The drone must also wait if too many drones already used this
        # connection during the current turn.
        link_key = self._connection_key(current_hub_name, next_hub_name)
        connection = self._connections.get(link_key)

        if connection is None:
            raise ValueError(
                "No connection found between hubs "
                f"{current_hub_name} and {next_hub_name}")

        used_this_turn = link_usage.get(link_key, 0)

        if used_this_turn >= connection.max_link_capacity:
            drone.waiting = True
            return None, False

        self._hub_occupancy[current_hub_name] -= 1
        self._hub_occupancy[next_hub_name] += 1
        link_usage[link_key] = used_this_turn + 1

        if next_hub.zone == ZoneType.RESTRICTED and not drone.in_transit:
            drone.current_hub = None
            drone.next_hub = next_hub_name
            drone.in_transit = True
            drone.waiting = False

            return None, True
        else:
            drone.current_hub = next_hub_name
            drone.path_index += 1
            drone.waiting = False

            if drone.path_index == len(path) - 1:
                drone.finished = True

            return f"D{drone.id}-{next_hub_name}", True

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

    def _all_finished(self, drones: list[Drone]) -> bool:
        """Return ``True`` when every drone has reached the final hub."""

        return all(drone.finished for drone in drones)

    def get_drones_snapshot(self, drones: list[Drone]) -> list[Drone]:
        """Return a snapshot of the drones."""
        return drones
