import pygame as pg
from models.drone import Drone
from models.zone import ZoneType
from parser import MapParser
from simulation.engine import SimulationEngine


class RenderApp:
    """Open a Pygame window and render the parsed world map."""

    def __init__(self) -> None:
        """Initialize Pygame, load the map, and store render settings."""
        # 1. Initialize the game
        pg.init()

        # 2. Create window
        self.screen = pg.display.set_mode([1500, 600])
        pg.display.set_caption("Fly-in Map Viewer")

        # 3. Create clock to control FPS
        self.clock = pg.time.Clock()

        # 4. Load map
        self.world = MapParser().parse_file(
            "maps/challenger/01_the_impossible_dream.txt"
            )

        # 5. Save configs
        self.fit_world_to_screen()

        # 6. Drones
        self.engine = SimulationEngine(self.world)
        self.result = self.engine.run()
        self.snapshots = self.result.snapshots
        self.path = self.result.path

        self.current_turn = 0
        self.turn_progress = 0.0
        self.turn_speed = 0.02

        # 7. App status
        self.running = True

        # 8. Creating font for labels
        self.font = pg.font.Font(None, 12)

    def fit_world_to_screen(self) -> None:
        """Calculate scale and offsets so the full map fits the window."""
        hubs = list(self.world.hubs.values())

        if not hubs:
            self.scale = 1
            self.offset_x = 0
            self.offset_y = 0
            return

        x_values = [hub.x for hub in hubs]
        y_values = [hub.y for hub in hubs]

        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)

        world_width = max_x - min_x
        world_height = max_y - min_y

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        padding = 80

        usable_width = screen_width - 2 * padding
        usable_height = screen_height - 2 * padding

        if world_width == 0:
            scale_x = usable_width
        else:
            scale_x = usable_width / world_width

        if world_height == 0:
            scale_y = usable_height
        else:
            scale_y = usable_height / world_height

        self.scale = min(scale_x, scale_y)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        self.offset_x = screen_width / 2 - center_x * self.scale
        self.offset_y = screen_height / 2 + center_y * self.scale

    def map_to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Convert map coordinates into screen coordinates."""
        screen_x = self.offset_x + x * self.scale
        screen_y = self.offset_y - y * self.scale
        return screen_x, screen_y

    def handle_events(self) -> None:
        """Process window events and stop the app when it is closed."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

    def update(self) -> None:
        """Advance the visual animation between simulation snapshots."""
        if self.current_turn >= len(self.snapshots) - 1:
            return

        self.turn_progress += self.turn_speed

        if self.turn_progress >= 1.0:
            self.turn_progress = 0.0
            self.current_turn += 1

    def draw_hubs(self) -> None:
        """Draw every hub from the parsed world onto the screen."""
        for hub in self.world.hubs.values():
            pg.draw.circle(
                self.screen,
                self.get_rgb_color(hub.color),
                self.map_to_screen(hub.x, hub.y),
                20)

    def get_rgb_color(self, color_name: str) -> tuple[int, int, int]:
        """Translate a color name from the map file into an RGB tuple."""
        color_map = {
            "none": (0, 255, 0),
            "blue": (0, 0, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "yellow": (255, 250, 50),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "orange": (255, 165, 0),
            "cyan": (0, 255, 255),
            "brown": (150, 75, 0),
            "maroon": (128, 0, 0)
        }
        return color_map.get(color_name.lower(), (0, 255, 0))

    def draw_connections(self) -> None:
        """Draw every connection between hubs as a line."""
        for connection in self.world.connections:
            source_hub = self.world.hubs[connection.source]
            target_hub = self.world.hubs[connection.target]

            x1, y1 = self.map_to_screen(source_hub.x, source_hub.y)
            x2, y2 = self.map_to_screen(target_hub.x, target_hub.y)

            pg.draw.line(self.screen, (120, 120, 120), (x1, y1), (x2, y2), 3)

    def get_drone_position(
            self,
            current_drone: Drone,
            next_drone: Drone
            ) -> tuple[float, float]:
        """Return the interpolated map position for one drone.

        The engine is the source of truth for movement. This method only
        converts two consecutive drone states into a drawable position.
        """
        if current_drone.in_transit and current_drone.next_hub is not None:
            origin_name = self.path[current_drone.path_index]
            origin_hub = self.world.hubs[origin_name]
            target_hub = self.world.hubs[current_drone.next_hub]
            x = (origin_hub.x +
                 (target_hub.x - origin_hub.x) * self.turn_progress)
            y = (origin_hub.y +
                 (target_hub.y - origin_hub.y) * self.turn_progress)
            return float(x), float(y)

        if current_drone.current_hub is not None:
            start_hub = self.world.hubs[current_drone.current_hub]
            start_x = float(start_hub.x)
            start_y = float(start_hub.y)
        elif current_drone.next_hub is not None:
            target_hub = self.world.hubs[current_drone.next_hub]
            return float(target_hub.x), float(target_hub.y)
        else:
            return 0.0, 0.0

        # No visible hub change between these two snapshots: drone is waiting.
        if (
            next_drone.current_hub is None
            or next_drone.current_hub == current_drone.current_hub
        ):
            if current_drone.in_transit and current_drone.next_hub is not None:
                target_hub = self.world.hubs[current_drone.next_hub]
                x = start_x + (target_hub.x - start_x) * self.turn_progress
                y = start_y + (target_hub.y - start_y) * self.turn_progress
                return x, y
            return start_x, start_y

        end_hub = self.world.hubs[next_drone.current_hub]
        x = start_x + (end_hub.x - start_x) * self.turn_progress
        y = start_y + (end_hub.y - start_y) * self.turn_progress
        return x, y

    def draw_drones(self) -> None:
        """Draw every drone using the current engine snapshots."""
        if not self.snapshots:
            return

        color = (200, 80, 120)

        if self.current_turn >= len(self.snapshots) - 1:
            final_snapshot = self.snapshots[-1]

            for drone in final_snapshot:
                hub_name = drone.current_hub or drone.next_hub
                if hub_name is None:
                    continue

                hub = self.world.hubs[hub_name]
                sx, sy = self.map_to_screen(hub.x, hub.y)
                pg.draw.circle(self.screen, color, (int(sx), int(sy)), 10)
            return

        current_snapshot = self.snapshots[self.current_turn]
        next_snapshot = self.snapshots[self.current_turn + 1]

        for current_drone, next_drone in zip(current_snapshot, next_snapshot):
            x, y = self.get_drone_position(current_drone, next_drone)
            sx, sy = self.map_to_screen(x, y)
            pg.draw.circle(self.screen, color, (int(sx), int(sy)), 10)

    def draw_hub_labels(self) -> None:
        """Draw the name of each hub next to its circle."""
        for hub in self.world.hubs.values():
            sx, sy = self.map_to_screen(hub.x, hub.y)
            label = self.font.render(hub.name, True, (0, 0, 0))
            self.screen.blit(label, (sx - 25, sy - 35))

    def draw_legend(self) -> None:
        """Draw a small legend box explaining colors used in the map."""
        rect = self.get_legend_rect()
        legend_x = rect.x
        legend_y = rect.y
        legend_width = 220
        legend_height = 170

        pg.draw.rect(
            self.screen,
            (255, 255, 255),
            (legend_x, legend_y, legend_width, legend_height)
            )
        pg.draw.rect(
            self.screen,
            (0, 0, 0),
            (legend_x, legend_y, legend_width, legend_height),
            2
            )

        entries = [
            ("Normal hub", (0, 255, 0)),
            ("Priority hub", (0, 255, 255)),
            ("Restricted hub", (255, 0, 0)),
            ("Drone", (200, 80, 120)),
        ]

        title = self.font.render("Legend", True, (0, 0, 0))
        self.screen.blit(title, (legend_x + 10, legend_y + 10))

        y = legend_y + 35
        for text, color in entries:
            pg.draw.circle(self.screen, color, (legend_x + 15, y + 6), 6)
            label = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(label, (legend_x + 30, y))
            y += 25

        turn_label = self.font.render(
            f"Turn: {self.current_turn}/{self.result.turns}",
            True,
            (0, 0, 0),
        )
        self.screen.blit(turn_label, (legend_x + 10, y + 5))

        # Marker for RESTRICTED hubs
        for hub in self.world.hubs.values():
            if hub.zone == ZoneType.RESTRICTED:
                sx, sy = self.map_to_screen(hub.x, hub.y)
                label = self.font.render("R", True, (255, 255, 255))
                self.screen.blit(label, (sx - 2, sy - 2))

    def legend_overlaps_hubs(self, rect: pg.Rect) -> bool:
        """Return whether the legend box overlaps any hub marker."""
        for hub in self.world.hubs.values():
            sx, sy = self.map_to_screen(hub.x, hub.y)

            hub_rect = pg.Rect(sx - 25, sy - 25, 50, 50)
            if rect.colliderect(hub_rect):
                return True

        return False

    def get_legend_rect(self) -> pg.Rect:
        """Choose a legend position that avoids overlapping hub markers."""
        width = 220
        height = 170
        margin = 20

        candidates = [
            pg.Rect(margin, margin, width, height),
            pg.Rect(
                self.screen.get_width() - width - margin,
                margin,
                width,
                height
                ),
            pg.Rect(
                margin,
                self.screen.get_height() - height - margin,
                width,
                height
                ),
            pg.Rect(
                self.screen.get_width() - width - margin,
                self.screen.get_height() - height - margin,
                width,
                height,
            ),
        ]

        for rect in candidates:
            if not self.legend_overlaps_hubs(rect):
                return rect

        return candidates[0]

    def draw(self) -> None:
        """Render one full frame of the map."""
        self.screen.fill((240, 240, 240))

        self.draw_connections()
        self.draw_hubs()
        self.draw_drones()
        self.draw_hub_labels()
        self.draw_legend()

        # To update the entire screen
        pg.display.flip()

    def run(self) -> None:
        """Run the main application loop until the window is closed."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pg.quit()


def main() -> None:
    """Create the render application and start it."""
    app = RenderApp()
    app.run()


if __name__ == "__main__":
    main()
