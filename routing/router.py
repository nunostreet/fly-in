from models.world import World
from models.zone import ZoneType
import heapq


class Router:
    """Build navigable graphs and find routes through the world map."""

    def build_graph(self, world: World) -> dict[str, list[str]]:
        """Build an adjacency list for all hubs that are not blocked.

        Args:
            world: Parsed world containing hubs and connections.

        Returns:
            A graph where each key is a hub name and each value is the list of
            reachable neighboring hubs.
        """

        graph: dict[str, list[str]] = {}

        for hub_name in world.hubs:
            current_hub = world.hubs[hub_name]
            if current_hub.zone == ZoneType.BLOCKED:
                continue
            graph[hub_name] = []

        for conn in world.connections:
            if conn.source not in graph or conn.target not in graph:
                continue
            graph[conn.source].append(conn.target)
            graph[conn.target].append(conn.source)

        return graph

    def find_path(self, world: World) -> list[str]:
        """Find the cheapest path from the start hub to the end hub.

        The search uses Dijkstra's algorithm. Entering a restricted hub costs
        more than entering a normal or priority hub, and priority hubs are
        favored as a tie-break when two paths have the same total cost.

        Args:
            world: Parsed world containing the route definition.

        Returns:
            A list of hub names from start to goal, or an empty list when no
            valid route exists.
        """

        graph = self.build_graph(world)
        start = world.start_hub_name
        goal = world.end_hub_name

        # Guard against malformed worlds with missing endpoints
        if start is None or goal is None:
            return []

        # Blocked hubs are excluded from the graph, so no path can exist if
        # either endpoint is missing from the navigable graph
        if start not in graph or goal not in graph:
            return []

        if start == goal:
            return [start]

        # Dijkstra keeps the best known cost to each hub. When costs tie, the
        # route that uses more priority hubs is preferred
        distances: dict[str, int] = {start: 0}
        priority_counts: dict[str, int] = {start: 0}
        previous: dict[str, str] = {}
        queue: list[tuple[int, int, str]] = [(0, 0, start)]

        while queue:
            cost, neg_priority_count, hub = heapq.heappop(queue)
            priority_count = -neg_priority_count

            # Ignore entries that are inferior to new ones discovered
            known_cost = distances.get(hub, float("inf"))
            known_priority_count = priority_counts.get(hub, -1)

            if cost > known_cost:
                continue

            if cost == known_cost and priority_count < known_priority_count:
                continue

            if hub == goal:
                path: list[str] = []
                current = goal

                while current != start:
                    path.append(current)
                    current = previous[current]

                path.append(start)
                path.reverse()
                return path

            for neighbor in graph[hub]:
                # Moving into the neighbor adds its traversal cost. Priority
                # hubs do not reduce the cost, but they improve tie-breaking
                new_cost = cost + self._hub_cost(world, neighbor)
                new_priority_count = (
                    priority_count + self._priority_bonus(world, neighbor)
                    )

                # Compare the new route to the best route known so far for
                # this specific neighbor
                best_cost = distances.get(neighbor, float("inf"))
                best_priority_count = priority_counts.get(neighbor, -1)

                # Accept the new route if it is cheaper, or if it has the same
                # cost but passes through more priority hubs
                if (
                    new_cost < best_cost
                    or (
                        new_cost == best_cost
                        and new_priority_count > best_priority_count
                    )
                ):
                    distances[neighbor] = new_cost
                    priority_counts[neighbor] = new_priority_count
                    previous[neighbor] = hub
                    heapq.heappush(
                        queue, (new_cost, -new_priority_count, neighbor)
                    )

        return []

    def _hub_cost(self, world: World, hub_name: str) -> int:
        """Return the movement cost of entering a hub.

        Args:
            world: Parsed world containing the hub definitions.
            hub_name: Name of the destination hub.

        Returns:
            ``2`` for restricted hubs and ``1`` for all other traversable
            hubs.
        """

        curr_hub = world.hubs[hub_name]
        if curr_hub.zone == ZoneType.RESTRICTED:
            return 2
        return 1

    def _priority_bonus(self, world: World, hub_name: str) -> int:
        """Return the priority tie-break bonus for entering a hub.

        Args:
            world: Parsed world containing the hub definitions.
            hub_name: Name of the destination hub.

        Returns:
            ``1`` for priority hubs and ``0`` for all other hubs.
        """

        curr_hub = world.hubs[hub_name]
        if curr_hub.zone == ZoneType.PRIORITY:
            return 1
        return 0
