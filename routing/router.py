from models.world import World
from collections import deque


class Router:
    def build_graph(self, world: World) -> dict[str, list[str]]:
        graph: dict[str, list[str]] = {}

        for hub_name in world.hubs:
            graph[hub_name] = []

        for conn in world.connections:
            graph[conn.source].append(conn.target)
            graph[conn.target].append(conn.source)

        return graph

    def find_path(self, world: World) -> list[str]:
        graph = self.build_graph(world)
        start = world.start_hub_name
        goal = world.end_hub_name

        if start is None or goal is None:
            return []

        if start == goal:
            return [start]

        queue: deque[str] = deque([start])
        visited: set[str] = {start}
        previous: dict[str, str] = {}

        while queue:
            hub = queue.popleft()

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
                if neighbor not in visited:
                    visited.add(neighbor)
                    previous[neighbor] = hub
                    queue.append(neighbor)

        return []
