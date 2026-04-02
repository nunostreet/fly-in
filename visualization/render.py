from pathlib import Path

import pygame as pg
from models.drone import Drone
from models.zone import ZoneType
from parser import MapParser
from simulation.engine import SimulationEngine


class RenderApp:
    """Open a Pygame window and render the parsed world map."""

    def __init__(self, map_path: str) -> None:
        """Initialize Pygame, load the map, and store render settings."""
        # 1. Initialize the game
        pg.init()

        # 2. Create window
        self.screen = pg.display.set_mode([1500, 600])
        pg.display.set_caption("Fly-in Map Viewer")

        # 3. Create clock to control FPS
        self.clock = pg.time.Clock()

        # 4. Load map
        self.world = MapParser().parse_file(map_path)

        # 5. Save configs
        self.fit_world_to_screen()

        # 6. Drones
        self.engine = SimulationEngine(self.world)
        self.result = self.engine.run()
        self.snapshots = self.result.snapshots
        self.path = self.result.path
        self.turn_tracker = self.result.turn_tracker

        self.is_paused = False
        self.current_turn = 0
        self.turn_progress = 0.0
        self.turn_speed = 0.012

        # 7. App status
        self.running = True

        # 8. Creating font for labels
        self.label_font = pg.font.Font(None, 12)
        self.legend_font = pg.font.Font(None, 12)
        self.marker_font = pg.font.Font(None, 12)

        # 9. Background image
        self.background = self.load_background()
        self.drone_sprite = self.load_drone_sprite()

    def load_background(self) -> pg.Surface | None:
        """Load and scale the background image to the window size."""
        background_path = Path(__file__).resolve().parent.parent.joinpath(
            "assets",
            "terrain.jpeg",
        )

        # If background doesn't exist
        if not background_path.exists():
            return None

        background = pg.image.load(str(background_path)).convert()
        return pg.transform.scale(background, self.screen.get_size())

    def load_drone_sprite(self) -> pg.Surface | None:
        """Load and scale the drone image used on the map."""
        drone_path = Path(__file__).resolve().parent.parent.joinpath(
            "assets",
            "drone.png",
        )

        # If drone sprite doesn't exist
        if not drone_path.exists():
            return None

        # Creates a new copy of the surface with the desired pixel format
        # The new surface will be in a format suited for quick blitting to
        # the given format with per pixel alpha.
        drone_image = pg.image.load(str(drone_path)).convert_alpha()
        return pg.transform.smoothscale(drone_image, (30, 30))

    def fit_world_to_screen(self) -> None:
        """Calculate scale and offsets so the full map fits the window."""
        hubs = list(self.world.hubs.values())

        if not hubs:
            self.scale = 1.0
            self.offset_x = 0.0
            self.offset_y = 0.0
            return

        # Create list of x and y values for map dimensions
        x_values = [hub.x for hub in hubs]
        y_values = [hub.y for hub in hubs]

        # Get min/max x and y values
        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)

        # Checking size for world width / height
        world_width = max_x - min_x
        world_height = max_y - min_y

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Extra space for borders
        padding = 80

        usable_width = screen_width - 2 * padding
        usable_height = screen_height - 2 * padding

        # Horizontal scale
        scale_x: float
        if world_width == 0:
            scale_x = float(usable_width)
        else:
            scale_x = usable_width / world_width

        # Vertical scale
        scale_y: float
        if world_height == 0:
            scale_y = float(usable_height)
        else:
            scale_y = usable_height / world_height

        self.scale = min(scale_x, scale_y)

        # Calculate the center of the map
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

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.toggle_pause()
                elif event.key == pg.K_r:
                    self.reset_animation()
                elif event.key == pg.K_RIGHT:
                    self.step_forward()
                elif event.key == pg.K_LEFT:
                    self.step_backward()

    def toggle_pause(self) -> None:
        self.is_paused = not self.is_paused

    def reset_animation(self) -> None:
        self.current_turn = 0
        self.turn_progress = 0.0
        self.is_paused = False

    def step_forward(self) -> None:
        self.is_paused = True
        if self.current_turn < len(self.snapshots) - 1:
            self.current_turn += 1
            self.turn_progress = 0.0

    def step_backward(self) -> None:
        self.is_paused = True
        if self.current_turn > 0:
            self.current_turn -= 1
            self.turn_progress = 0.0

    def update(self) -> None:
        """Advance the visual animation between simulation snapshots."""
        if self.is_paused:
            return

        if self.current_turn >= len(self.snapshots) - 1:
            return

        self.turn_progress += self.turn_speed

        if self.turn_progress >= 1.0:
            self.turn_progress = 0.0
            self.current_turn += 1

    def get_rgb_color(self, color_name: str) -> tuple[int, int, int]:
        """Translate a color name from the map file into an RGB tuple."""
        color_map = {
            "red": (255, 80, 80),
            "green": (80, 220, 120),
            "blue": (90, 150, 255),
            "cyan": (70, 210, 210),
            "yellow": (255, 210, 70),
            "white": (255, 255, 255),
            "purple": (180, 100, 255),
            "black": (200, 200, 210),
            "brown": (200, 130, 70),
            "orange": (255, 140, 50),
            "maroon": (180, 60, 90),
            "gold": (255, 200, 50),
            "darkred": (200, 50, 50),
            "violet": (200, 100, 220),
            "crimson": (240, 60, 80),
        }
        return color_map.get(color_name.lower(), (0, 255, 0))

    def draw_marker(
            self,
            center: tuple[float, float],
            text: str,
            background_color: tuple[int, int, int],
            text_color: tuple[int, int, int],
            radius: int = 8
            ) -> None:
        """Draw a small circular marker with centered text."""
        cx, cy = int(center[0]), int(center[1])
        pg.draw.circle(self.screen, background_color, (cx, cy), radius)

        label = self.marker_font.render(text, True, text_color)
        label_rect = label.get_rect(center=(cx, cy))
        self.screen.blit(label, label_rect)

    def draw_rainbow_hub(
            self,
            center: tuple[float, float],
            radius: int
            ) -> None:
        """Draw a circular hub with concentric rainbow-colored rings."""
        rainbow_colors = [
            (255, 0, 0),
            (255, 127, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 0, 255),
            (75, 0, 130),
            (148, 0, 211),
        ]

        cx, cy = int(center[0]), int(center[1])
        total_colors = len(rainbow_colors)

        for index, color in enumerate(rainbow_colors):
            current_radius = radius - (index * radius) // total_colors
            pg.draw.circle(self.screen, color, (cx, cy), current_radius)

    def draw_drone(self, center: tuple[float, float], size: int = 30) -> None:
        """Draw a drone sprite centered on the given map position."""
        cx, cy = int(center[0]), int(center[1])

        if self.drone_sprite is not None:
            if self.drone_sprite.get_size() == (size, size):
                sprite = self.drone_sprite
            else:
                # Re-scale only when the legend or another caller needs
                # a different size than the default in-map sprite
                sprite = pg.transform.smoothscale(
                    self.drone_sprite,
                    (size, size),
                )

            sprite_rect = sprite.get_rect(center=(cx, cy))
            self.screen.blit(sprite, sprite_rect)
            return

        pg.draw.circle(self.screen, (255, 255, 255), (cx, cy), size // 2)
        pg.draw.circle(self.screen, (200, 80, 120), (cx, cy), size // 3)

    def get_drone_position(
            self,
            current_drone: Drone,
            next_drone: Drone,
            arrivals: set[int],
            departures: set[int],
            ) -> tuple[float, float]:
        """Return the interpolated map position for one drone.

        The engine is the source of truth for movement. This method only
        converts two consecutive drone states into a drawable position.
        """
        if self.turn_progress < 0.5:
            phase_progress = self.turn_progress * 2.0
            if (
                current_drone.id in arrivals
                and current_drone.in_transit
                and current_drone.next_hub is not None
            ):
                origin_name = current_drone.transit_origin
                if origin_name is None:
                    origin_name = self.path[current_drone.path_index]
                return self._interpolate_between_hubs(
                    origin_name,
                    current_drone.next_hub,
                    0.5 + phase_progress * 0.5,
                )

            if current_drone.current_hub is not None:
                return self._hub_position(current_drone.current_hub)

            if current_drone.next_hub is not None:
                return self._hub_position(current_drone.next_hub)

            return 0.0, 0.0

        phase_progress = (self.turn_progress - 0.5) * 2.0
        if (
            current_drone.id in departures
            and current_drone.current_hub is not None
        ):
            if next_drone.in_transit and next_drone.next_hub is not None:
                return self._interpolate_between_hubs(
                    current_drone.current_hub,
                    next_drone.next_hub,
                    phase_progress * 0.5,
                )

            departure_target = next_drone.current_hub
            if departure_target is not None and departure_target != current_drone.current_hub:
                return self._interpolate_between_hubs(
                    current_drone.current_hub,
                    departure_target,
                    phase_progress,
                )

        if (
            current_drone.current_hub is not None
            and next_drone.current_hub is not None
            and next_drone.current_hub == current_drone.current_hub
            and current_drone.current_hub is not None
        ):
            return self._hub_position(current_drone.current_hub)

        if current_drone.current_hub is not None:
            start_x, start_y = self._hub_position(current_drone.current_hub)
        elif current_drone.next_hub is not None:
            return self._hub_position(current_drone.next_hub)
        else:
            return 0.0, 0.0

        # No visible hub change between these two snapshots: drone is waiting
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

    def draw_connections(self) -> None:
        """Draw every connection between hubs as a line."""
        for connection in self.world.connections:
            source_hub = self.world.hubs[connection.source]
            target_hub = self.world.hubs[connection.target]

            x1, y1 = self.map_to_screen(source_hub.x, source_hub.y)
            x2, y2 = self.map_to_screen(target_hub.x, target_hub.y)

            pg.draw.line(self.screen, (120, 120, 120), (x1, y1), (x2, y2), 3)

    def draw_hubs(self) -> None:
        """Draw every hub from the parsed world onto the screen."""
        for hub in self.world.hubs.values():
            center = self.map_to_screen(hub.x, hub.y)

            if hub.color.lower() == "rainbow":
                self.draw_rainbow_hub(center, 20)
                continue

            pg.draw.circle(
                self.screen,
                self.get_rgb_color(hub.color),
                center,
                20,
            )

    def draw_zone_markers(self) -> None:
        """Draw markers for priority, restricted and blocked hubs."""
        for hub in self.world.hubs.values():
            sx, sy = self.map_to_screen(hub.x, hub.y)
            # Offset the badge so it stays readable without covering the hub
            marker_center = (sx + 15, sy - 15)

            if hub.zone == ZoneType.PRIORITY:
                self.draw_marker(
                    marker_center,
                    "P",
                    self.get_rgb_color("white"),
                    self.get_rgb_color("cyan"),
                )
            elif hub.zone == ZoneType.RESTRICTED:
                self.draw_marker(
                    marker_center,
                    "R",
                    self.get_rgb_color("black"),
                    self.get_rgb_color("red"),
                )
            elif hub.zone == ZoneType.BLOCKED:
                self.draw_marker(
                    marker_center,
                    "B",
                    (60, 60, 60),
                    (255, 255, 255),
                )

    def draw_drones(self) -> None:
        """Draw every drone using the current engine snapshots."""
        if not self.snapshots:
            return

        if self.current_turn >= len(self.snapshots) - 1:
            final_snapshot = self.snapshots[-1]

            for drone in final_snapshot:
                hub_name = drone.current_hub or drone.next_hub
                if hub_name is None:
                    continue

                hub = self.world.hubs[hub_name]
                sx, sy = self.map_to_screen(hub.x, hub.y)
                self.draw_drone((sx, sy))
            return

        current_snapshot = self.snapshots[self.current_turn]
        next_snapshot = self.snapshots[self.current_turn + 1]
        turn_event = self.turn_tracker[self.current_turn]
        arrivals = set(turn_event.arrivals)
        departures = set(turn_event.departures)

        for current_drone, next_drone in zip(current_snapshot, next_snapshot):
            # Blend between consecutive snapshots for smoother animation
            x, y = self.get_drone_position(
                current_drone,
                next_drone,
                arrivals,
                departures,
            )
            sx, sy = self.map_to_screen(x, y)
            self.draw_drone((sx, sy))

    def _interpolate_between_hubs(
            self,
            origin_name: str,
            target_name: str,
            progress: float,
            ) -> tuple[float, float]:
        """Return a position between two hubs."""
        progress = max(0.0, min(1.0, progress))
        origin_hub = self.world.hubs[origin_name]
        target_hub = self.world.hubs[target_name]
        x = origin_hub.x + (target_hub.x - origin_hub.x) * progress
        y = origin_hub.y + (target_hub.y - origin_hub.y) * progress
        return float(x), float(y)

    def _hub_position(self, hub_name: str) -> tuple[float, float]:
        """Return the map coordinates of a hub as floats."""
        hub = self.world.hubs[hub_name]
        return float(hub.x), float(hub.y)

    def draw_hub_labels(self) -> None:
        """Draw the name of each hub next to its circle."""
        for hub in self.world.hubs.values():
            sx, sy = self.map_to_screen(hub.x, hub.y)
            label = self.label_font.render(hub.name, True, (0, 0, 0))
            self.screen.blit(label, (sx - 25, sy - 35))

    def draw_legend(self) -> None:
        """Draw a small legend box explaining colors used in the map."""
        rect = self.get_legend_rect()
        legend_x = rect.x
        legend_y = rect.y
        legend_width = 190
        legend_height = 220

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
            # Reuse the same visual language as the map markers
            (
                "Priority",
                ("P", self.get_rgb_color("white"), self.get_rgb_color("cyan")),
            ),
            (
                "Restricted",
                ("R", self.get_rgb_color("black"), self.get_rgb_color("red")),
            ),
            ("Blocked", ("B", (60, 60, 60), (255, 255, 255))),
        ]

        title = self.legend_font.render("Legend", True, (0, 0, 0))
        self.screen.blit(title, (legend_x + 10, legend_y + 10))

        y = legend_y + 35
        for text, value in entries:
            marker_text, bg_color, text_color = value
            self.draw_marker(
                (legend_x + 15, y + 6),
                marker_text,
                bg_color,
                text_color,
                radius=8,
            )

            label = self.legend_font.render(text, True, (0, 0, 0))
            self.screen.blit(label, (legend_x + 30, y))
            y += 22

        self.draw_drone((legend_x + 15, y + 6), size=18)
        label = self.legend_font.render("Drone", True, (0, 0, 0))
        self.screen.blit(label, (legend_x + 30, y))
        y += 22

        y += 8

        turn_label = self.legend_font.render(
            f"Turn: {self.current_turn}/{self.result.turns}",
            True,
            (0, 0, 0),
        )
        self.screen.blit(turn_label, (legend_x + 10, y + 5))

        status = "Paused" if self.is_paused else "Playing"
        status_label = self.legend_font.render(
            f"Status: {status}",
            True,
            (0, 0, 0),
        )
        self.screen.blit(status_label, (legend_x + 10, y + 25))

        controls_label = self.legend_font.render(
            "Space: pause | R: reset",
            True,
            (0, 0, 0),
        )
        self.screen.blit(controls_label, (legend_x + 10, y + 45))

        step_label = self.legend_font.render(
            "Left arrow (previous) / Right arrow (next)",
            True,
            (0, 0, 0),
        )
        self.screen.blit(step_label, (legend_x + 10, y + 65))

    def legend_overlaps_hubs(self, rect: pg.Rect) -> bool:
        """Return whether the legend box overlaps any hub marker."""
        for hub in self.world.hubs.values():
            sx, sy = self.map_to_screen(hub.x, hub.y)

            hub_rect = pg.Rect(sx - 25, sy - 25, 50, 50)
            # Test if two triangles overlap
            if rect.colliderect(hub_rect):
                return True

        return False

    def get_legend_rect(self) -> pg.Rect:
        """Choose a legend position that avoids overlapping hub markers."""
        width = 190
        height = 220
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

        # Fall back to the first corner if every candidate overlaps
        return candidates[0]

    def draw(self) -> None:
        """Render one full frame of the map."""
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((240, 240, 240))

        self.draw_connections()
        self.draw_hubs()
        self.draw_zone_markers()
        self.draw_drones()
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
