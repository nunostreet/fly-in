from dataclasses import dataclass, replace
from models.world import World
from models.drone import Drone
from models.zone import ZoneType
from routing.router import Router
from typing import List


@dataclass
class TurnTracker:
    """Keeping track of arrivals/departures for rendering purposes."""
    arrivals: list[int]
    departures: list[int]


@dataclass
class SimulationResult:
    """Store the simulation output."""
    turns: int
    lines: list[str]
    snapshots: list[list[Drone]]
    path: list[str]
    turn_tracker: list[TurnTracker]


class SimulationEngine:
    """Run a simple multi-drone simulation over a routed path.

    This is a single-path solution which takes into account hub occupancy,
    link capacity and zone restrictions.
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
            SimulationResult, containing the number of turns and the
            formatted movement lines for each turn.
        """

        # Solution path with each hub from start to goal
        path = self._router.find_path(self._world)
        if not path:
            raise RuntimeError("No solution found")

        drones = self._init_drones()
        snapshots: list[list[Drone]] = []
        lines: list[str] = []
        turns = 0
        turn_track: list[TurnTracker] = []

        snapshots.append(self._snapshot_drones(drones))
        while not self._all_finished(drones):
            turn_moves, made_progress, turn_arr_or_dep = self._run_turn(
                drones, path
            )
            snapshots.append(self._snapshot_drones(drones))
            turn_track.append(turn_arr_or_dep)

            if turn_moves:
                lines.append(" ".join(turn_moves))
            elif not made_progress:
                raise RuntimeError(
                    f"No drone could move this turn (turn: {turns})"
                )

            turns += 1

        return SimulationResult(
            turns=turns,
            lines=lines,
            snapshots=snapshots,
            path=path,
            turn_tracker=turn_track,
        )

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

        return drones

    def _run_turn(
            self, drones: list[Drone], path: list[str]
            ) -> tuple[List[str], bool, TurnTracker]:
        """Advance the simulation by one turn.

        Drones that were already traveling to a restricted hub are resolved
        first. After that, drones that are idle may attempt to start a new
        movement. The returned strings are joined into the output line for the
        current turn.
        """

        moves: list[str] = []
        arrivals: list[int] = []
        departures: list[int] = []
        made_progress = False

        # Track how many drones have already used each connection this turn.
        link_usage: dict[tuple[str, str], int] = {}

        # Drones that already arrived from restricted transit do not move again
        # in the same turn.
        processed_ids: set[int] = set()

        # 1. We prioritise drones that were already in transit
        for drone in drones:
            if not drone.in_transit or drone.next_hub is None:
                continue

            next_hub_name = drone.next_hub
            drone.current_hub = next_hub_name
            drone.next_hub = None
            drone.transit_origin = None
            drone.in_transit = False
            drone.path_index += 1
            drone.waiting = False
            if self._world.hubs[next_hub_name].zone != ZoneType.RESTRICTED:
                self._hub_occupancy[next_hub_name] += 1

            made_progress = True

            if drone.path_index == len(path) - 1:
                drone.finished = True

            arrivals.append(drone.id)
            moves.append(f"D{drone.id}-{next_hub_name}")
            processed_ids.add(drone.id)

        for drone in drones:
            if drone.id in processed_ids or drone.finished or drone.in_transit:
                continue

            move, progressed = self._move_drone(drone, path, link_usage)
            made_progress = made_progress or progressed
            if move is not None:
                departures.append(drone.id)
                moves.append(move)

        return moves, made_progress, TurnTracker(
            arrivals=arrivals,
            departures=departures,
        )

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
        next_capacity = self._hub_capacity(next_hub_name)
        if self._hub_occupancy[next_hub_name] >= next_capacity:
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

        if self._world.hubs[current_hub_name].zone != ZoneType.RESTRICTED:
            self._hub_occupancy[current_hub_name] -= 1
        link_usage[link_key] = used_this_turn + 1

        if next_hub.zone == ZoneType.RESTRICTED:
            drone.current_hub = None
            drone.next_hub = next_hub_name
            drone.transit_origin = current_hub_name
            drone.in_transit = True
            drone.waiting = False
            connection_name = self._connection_name(
                current_hub_name, next_hub_name
                )

            return f"D{drone.id}-{connection_name}", True
        else:
            self._hub_occupancy[next_hub_name] += 1
            drone.current_hub = next_hub_name
            drone.path_index += 1
            drone.waiting = False

            if drone.path_index == len(path) - 1:
                drone.finished = True

            return f"D{drone.id}-{next_hub_name}", True

    @staticmethod
    def _connection_key(origin: str, destiny: str) -> tuple[str, str]:
        """Return a normalized key for undirected connection comparison.
        """
        first, second = sorted((origin, destiny))
        return first, second

    def _connection_name(self, origin: str, destiny: str) -> str:
        return f"{origin}-{destiny}"

    def _hub_capacity(self, hub_name: str) -> int:
        """Return the capacity for a hub during simulation."""
        if (
            hub_name == self._world.start_hub_name
            or hub_name == self._world.end_hub_name
        ):
            return self._world.nb_drones or 0

        return self._world.hubs[hub_name].max_drones

    def _all_finished(self, drones: list[Drone]) -> bool:
        return all(drone.finished for drone in drones)

    def _snapshot_drones(self, drones: list[Drone]) -> list[Drone]:
        """Return a detached copy of the current drone states."""
        return [replace(drone) for drone in drones]
