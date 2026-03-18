from models.world import World


class Router:
    def build_graph(self, world: World) -> dict[str, list[str]]:
        d = {}
        for hub in world.hubs:
            d[hub]


    def find_path(self, world: World) -> list[str]:
        ...
