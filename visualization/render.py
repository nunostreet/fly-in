import pygame as pg
from parser import MapParser


class RenderApp:
    """Open a Pygame window and render the parsed world map."""

    def __init__(self):
        """Initialize Pygame, load the map, and store render settings."""
        # 1. Initialize the game
        pg.init()

        # 2. Create window
        self.screen = pg.display.set_mode([1200, 600])
        pg.display.set_caption("Fly-in Map Viewer")

        # 3. Create clock to control FPS
        self.clock = pg.time.Clock()

        # 4. Load map
        self.world = MapParser().parse_file(
            "maps/hard/02_capacity_hell.txt"
            )

        # 5. Save configs
        self.scale = 80
        self.offset_x = 100
        self.offset_y = 300

        # 6. Drones
        self.drone = DroneView(1, "start", "goal")

        # 7. App status
        self.running = True

        # 8. Creating font for labels
        self.font = pg.font.Font(None, 12)

    def map_to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Convert map coordinates into screen coordinates."""
        screen_x = self.offset_x + x * self.scale
        screen_y = self.offset_y - y * self.scale
        return screen_x, screen_y

    def handle_events(self):
        """Process window events and stop the app when it is closed."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

    def update(self):
        self.drone.progress += 0.01

        if self.drone.progress >= 1.0:
            self.drone.progress = 0.0

    def draw_hubs(self):
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
        }
        return color_map.get(color_name.lower(), (0, 255, 0))

    def draw_connections(self):
        """Draw every connection between hubs as a line."""
        for connection in self.world.connections:
            source_hub = self.world.hubs[connection.source]
            target_hub = self.world.hubs[connection.target]

            x1, y1 = self.map_to_screen(source_hub.x, source_hub.y)
            x2, y2 = self.map_to_screen(target_hub.x, target_hub.y)

            pg.draw.line(self.screen, (120, 120, 120), (x1, y1), (x2, y2), 3)

    def draw_drones(self):
        start_hub = self.world.hubs[self.drone.start_hub_name]
        end_hub = self.world.hubs[self.drone.end_hub_name]

        start_x = start_hub.x
        start_y = start_hub.y
        end_x = end_hub.x
        end_y = end_hub.y

        x = start_x + (end_x - start_x) * self.drone.progress
        y = start_y + (end_y - start_y) * self.drone.progress

        sx, sy = self.map_to_screen(x, y)

        pg.draw.circle(self.screen, (200, 80, 120), (int(sx), int(sy)), 10)

    def draw_hub_labels(self):
        """Draw the name of each hub next to its circle."""
        for hub in self.world.hubs.values():
            sx, sy = self.map_to_screen(hub.x, hub.y)
            label = self.font.render(hub.name, True, (0, 0, 0))
            self.screen.blit(label, (sx - 25, sy - 35))

    def draw(self):
        """Render one full frame of the map."""
        self.screen.fill((240, 240, 240))

        self.draw_connections()
        self.draw_hubs()
        self.draw_drones()
        self.draw_hub_labels()

        # To update the entire screen
        pg.display.flip()

    def run(self):
        """Run the main application loop until the window is closed."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pg.quit()


class DroneView:
    """Represent the visual state of one drone moving b/n two hubs."""

    def __init__(self, drone_id, start_hub_name, end_hub_name):
        """Store the drone identity and the segment being animated."""
        self.drone_id = drone_id
        self.start_hub_name = start_hub_name
        self.end_hub_name = end_hub_name
        self.progress = 0.0


def main():
    """Create the render application and start it."""
    app = RenderApp()
    app.run()


if __name__ == "__main__":
    main()
