*This project has been created as part of the 42 curriculum by nstreet-.*

# fly-in

## Description

`fly-in` is a Python project that parses a custom map format, validates the
input world, computes a route between a start hub and an end hub, simulates the
movement of multiple drones on that route, and optionally renders the result in
a Pygame visualization.

The project models constrained movement in a graph-based world. Each hub may
define metadata such as zone type, color, and capacity, while each connection
may restrict how many drones can use it per turn.

The full pipeline includes:

- parsing and validation of structured map files
- Dijkstra-based routing from start hub to end hub
- turn-based simulation with hub and connection constraints
- an interactive visualization built from simulation snapshots

## Features

- Custom parser for map files with explicit validation and readable errors
- Support for hub zones such as `normal`, `priority`, `restricted`, and
  `blocked`
- Dijkstra-based route computation with custom hub costs
- Multi-drone simulation with turn-by-turn output
- Capacity-aware movement on hubs and connections
- Interactive visualization with:
  - background image support
  - custom drone sprite support
  - pause, reset, and manual step controls
  - legend, status text, and zone markers
- Automated test coverage for benchmark maps and invalid error maps

## Requirements

- Python 3.12 recommended
- `pip` available in the environment

## Installation

Install dependencies with:

```bash
make install
```

Or manually:

```bash
python3 -m pip install -r requirements.txt
```

## Running The Project

The default `Makefile` target uses `maps/easy/01_linear_path.txt`:

```bash
make run
```

To run with a different map:

```bash
make run MAP=maps/challenger/01_the_impossible_dream.txt
```

To launch the visual renderer:

```bash
make viz MAP=maps/medium/02_circular_loop.txt
```

Or directly:

```bash
python3 main.py maps/test/testing_restricted.txt --run-viz
```

## Development Commands

Run with Python's built-in debugger:

```bash
make debug
```

Run the benchmark-style suite:

```bash
make test
```

Lint and type-check:

```bash
make lint
```

Optional stricter checks:

```bash
make lint-strict
```

Clean temporary files:

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
- supports inline comments after valid content
- validates the global drone count
- validates hub definitions and metadata
- validates connection syntax and references
- checks consistency rules after the full file is parsed

This keeps input validation close to the parsing logic and ensures that the
simulation only runs on a coherent world state.

### 2. Routing

Once the map is valid, the routing layer computes a path from the start hub to
the end hub. The route is then shared by all drones.

The router uses a Dijkstra-style search with custom hub costs:

- `restricted` hubs are more expensive to enter
- `priority` hubs are preferred as tie-breakers
- `blocked` hubs are excluded from the graph

### 3. Simulation

The simulation engine runs turn by turn. At each turn, it:

- resolves drones already in transit
- checks whether idle drones can start moving
- enforces hub occupancy limits
- enforces per-turn connection capacity limits
- handles `restricted` hubs as delayed arrivals that complete on the next turn

The engine stores snapshots of drone state after each turn. It also tracks
per-turn arrivals and departures so the renderer can animate turns in two
distinct phases.

### 4. Visualization

The renderer does not recompute movement logic. Instead, it consumes the
snapshots and turn-tracking information produced by the engine and interpolates
drone positions between consecutive states.

This keeps the simulation engine as the source of truth while the renderer
stays focused on presentation.

## Visual Representation

### Map layout

- The world is automatically scaled to fit the window
- The map is centered using screen offsets computed from world bounds
- A background image may be displayed to make the scene more readable

### Hub rendering

- Hubs are drawn as circles using their declared colors
- `rainbow` hubs are drawn with concentric colored rings
- Zone markers are displayed as small badges:
  - `P` for priority
  - `R` for restricted
  - `B` for blocked

### Drone rendering

- Drones use a dedicated sprite from `assets/drone.png`
- The legend reuses the same drone visual language
- Positions are interpolated between snapshots to make movement smoother
- Turns are animated in two phases so restricted arrivals and new departures
  remain visually readable

### Interaction

The visualization supports pausing, resetting, and stepping frame by frame.
This is especially useful when several drones compete for the same hubs or
links, because it lets the user inspect why a turn produced a specific result.

## Maps And Tests

The repository includes:

- benchmark maps in `maps/easy`, `maps/medium`, `maps/hard`, and
  `maps/challenger`
- parser and simulation failure cases in `maps/error`
- a focused restricted-zone map in `maps/test/testing_restricted.txt`

The benchmark runner in `tests/run_map_suite.py` compares simulation results
against reference targets and checks that every map in `maps/error` fails
somewhere in the pipeline.

## Project Structure

```text
.
├── main.py
├── parser.py
├── tests/
├── simulation/
├── routing/
├── visualization/
├── models/
├── maps/
├── assets/
├── docs/
├── requirements.txt
├── mypy.ini
└── Makefile
```

## Resources

### Topic references

- Python documentation: https://docs.python.org/3/
- `argparse` documentation:
  https://docs.python.org/3/library/argparse.html
- `heapq` documentation:
  https://docs.python.org/3/library/heapq.html
- `typing` documentation:
  https://docs.python.org/3/library/typing.html
- `pathlib` documentation:
  https://docs.python.org/3/library/pathlib.html
- Pygame documentation:
  https://www.pygame.org/docs/
- Graph theory overview:
  https://en.wikipedia.org/wiki/Graph_theory
- Dijkstra's algorithm overview:
  https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

### Community and peer resources

- 42 Slack `world_pedagogy` channel, used for project discussion and clarifying
  parts of the subject
- Discussions with peers who were also working on `fly-in`
- Informal code reviews and feedback from friends who had already completed
  the project

### AI usage

AI was used as a development assistant, mainly for:

- reviewing code structure and readability
- suggesting refactors for rendering and event handling
- improving comments and documentation & preparing and structuring this file
- helping design validation and test coverage around the provided map suite

AI was not used as a substitute for understanding the project logic.
