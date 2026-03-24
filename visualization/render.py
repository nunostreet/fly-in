import pygame as pg
from parser import MapParser
from models.zone import ZoneType


pg.init()

# Set up the drawing window
# Everything is viewed on a single user-created display
# Display is created using .set_mode()
screen = pg.display.set_mode([1200, 600])

clock = pg.time.Clock()

world = MapParser().parse_file("maps/hard/03_ultimate_challenge.txt")
SCALE = 80
OFFSET_X = 100
OFFSET_Y = 300


def map_to_screen(x: int, y: int) -> tuple[int, int]:
    screen_x = OFFSET_X + x * SCALE
    screen_y = OFFSET_Y - y * SCALE
    return screen_x, screen_y


running = True
while running:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill((240, 240, 240))

    for connection in world.connections:
        source_hub = world.hubs[connection.source]
        target_hub = world.hubs[connection.target]

        x1, y1 = map_to_screen(source_hub.x, source_hub.y)
        x2, y2 = map_to_screen(target_hub.x, target_hub.y)

        pg.draw.line(screen, (120, 120, 120), (x1, y1), (x2, y2), 3)

    for hub in world.hubs.values():
        sx, sy = map_to_screen(hub.x, hub.y)
        if hub.start is True:
            pg.draw.circle(screen, (0, 0, 255), (sx, sy), 20)
        elif hub.end is True:
            pg.draw.circle(screen, (0, 0, 255), (sx, sy), 20)
        elif hub.zone == ZoneType.PRIORITY:
            pg.draw.circle(screen, (255, 0, 0), (sx, sy), 20)
        elif hub.zone == ZoneType.RESTRICTED:
            pg.draw.circle(screen, (255, 250, 50), (sx, sy), 20)
        else:
            pg.draw.circle(screen, (0, 255, 0), (sx, sy), 20)

    # Flip the display
    pg.display.flip()
    clock.tick(60)

pg.quit()
