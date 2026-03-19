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

        if start == goal:
            return []
        queue = deque([start])
        visited: set = {start}
        previous: set = {}

        while queue:
    

        return path