*This project has been created as part of the 42 curriculum by nstreet-.*

# fly-in

## Description

`fly-in` is a Python project that parses a custom map format, validates the
input world, computes a route between a start hub and an end hub, simulates the
movement of multiple drones on that route, and optionally renders the result in
a Pygame visualization.

The main goal of the project is to model constrained movement in a graph-based
world. Each hub may define metadata such as zone type, color, and capacity,
while each connection may restrict how many drones can use it per turn. The
project combines:

- parsing and validation of structured map files
- graph routing from start hub to end hub
- turn-based simulation with occupancy and link-capacity constraints
- an interactive visual representation of the resulting execution

This makes the project useful both as a small algorithmic exercise and as a
clear visual demonstration of how multiple agents move through a constrained
network.

## Features

- Custom parser for map files with explicit validation and readable errors
- Support for hub zones such as `normal`, `priority`, `restricted`, and
  `blocked`
- Route computation through the world graph
- Multi-drone simulation with turn-by-turn output
- Capacity-aware movement on hubs and connections
- Interactive visualization with:
  - background image support
  - custom drone sprite support
  - pause, reset, and manual step controls
  - legend and zone markers

## Instructions

### Requirements

- Python 3.12 recommended
- `pip` available in the environment

### Installation

You can install dependencies directly:

```bash
make install
```

Or manually:

```bash
python3 -m pip install -r requirements.txt
```

### Run the project

The default `Makefile` target uses `maps/easy/01_linear_path.txt`:

```bash
make run
```

To run with a different map:

```bash
make run MAP=maps/test_blocked.txt
```

To launch the visual renderer, run the main script manually with `--run-viz`:

```bash
python3 main.py maps/test_restricted2.txt --run-viz
```

### Debug mode

Run the project with Python's built-in debugger:

```bash
make debug
```

### Linting and type checking

```bash
make lint
```

Optional stricter checks:

```bash
make lint-strict
```

### Clean temporary files

```bash
make clean
```

## Usage

### Standard execution

Without visualization, the program parses the world, runs the simulation, and
prints one line per turn describing drone movements.

Example:

```bash
python3 main.py maps/easy/01_linear_path.txt
```

### Visual execution

With `--run-viz`, the same parsed world and simulation result are rendered in a
Pygame window.

Controls:

- `Space`: pause or resume the animation
- `R`: reset the animation
- `Left`: move one snapshot backward
- `Right`: move one snapshot forward

## Algorithm And Implementation Strategy

The project is structured as a pipeline with four main stages.

### 1. Parsing and validation

`parser.py` reads the map file line by line and converts it into a validated
`World` object. The parser:

- ignores comments and empty lines
- validates the global drone count
- validates hub definitions and metadata
- validates connection syntax and references
- checks consistency rules after the full file is parsed

This approach keeps input validation close to the parsing logic and ensures
that the simulation only runs on a fully coherent world state.

### 2. Routing

Once the map is valid, the routing layer computes a path from the start hub to
the end hub. The route is then shared by all drones. This is a simple and clear
strategy for this project because it separates pathfinding from scheduling and
makes the simulation easier to reason about and visualize.

### 3. Simulation

The simulation engine runs turn by turn. At each turn, it:

- resolves drones already in transit
- checks whether waiting drones can start moving
- enforces hub occupancy limits
- enforces per-turn connection capacity limits
- handles `restricted` hubs as a delayed arrival, which takes an extra turn

The implementation uses snapshots of the drone list after each turn. This is an
important design choice because the textual output and the visualization both
depend on the same simulation history.

### 4. Visualization

The renderer does not recompute any movement logic. Instead, it consumes the
snapshots produced by the simulation engine and interpolates drone positions
between consecutive states. This keeps the engine as the source of truth and
lets the visual layer stay focused on presentation.

## Visual Representation

The visual representation is designed to make the simulation easier to
understand at a glance.

### Map layout

- The world is automatically scaled to fit the window.
- The map is centered using screen offsets computed from the world bounds.
- A background image can be displayed to make the scene more readable and less
  abstract.

### Hub rendering

- Hubs are drawn as circles using their declared colors.
- `rainbow` hubs are drawn with concentric colored rings.
- Zone markers are displayed as small badges:
  - `P` for priority
  - `R` for restricted
  - `B` for blocked

These markers improve readability because zone meaning remains visible even when
hub colors are similar or when the background is visually rich.

### Drone rendering

- Drones use a dedicated sprite from `assets/drone.png`
- The legend reuses the same drone visual language
- Positions are interpolated between snapshots to make movement smoother

Using a sprite instead of a plain circle makes drones immediately stand out from
hubs and connections, which improves usability during playback.

### Interaction

The visualization supports pausing, resetting, and stepping frame by frame. This
is especially helpful when several drones compete for the same hubs or links,
because it lets the user inspect why a turn produced a specific result.

## Project Structure

```text
.
├── main.py
├── parser.py
├── simulation/
├── routing/
├── visualization/
├── models/
├── maps/
├── assets/
├── requirements.txt
├── mypy.ini
└── Makefile
```

## Resources

### Topic references

- Python documentation: https://docs.python.org/3/
- `argparse` documentation:
  https://docs.python.org/3/library/argparse.html
- `pathlib` documentation:
  https://docs.python.org/3/library/pathlib.html
- Pygame documentation: https://www.pygame.org/docs/
- `dataclasses` documentation:
  https://docs.python.org/3/library/dataclasses.html

### AI usage

AI was used as a development assistant, mainly for:

- reviewing code structure and readability
- suggesting refactors for rendering and event handling
- improving comments and documentation

AI was not used as a substitute for understanding the project logic.
