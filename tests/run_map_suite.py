from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
MAPS_DIR = ROOT_DIR / "maps"
sys.path.insert(0, str(ROOT_DIR))

from parser import MapParser
from simulation.engine import SimulationEngine


@dataclass(frozen=True)
class Benchmark:
    label: str
    target_turns: int | None
    optional: bool = False


BENCHMARKS: dict[str, Benchmark] = {
    "maps/easy/01_linear_path.txt": Benchmark("Easy / Linear path", 6),
    "maps/easy/02_simple_fork.txt": Benchmark("Easy / Simple fork", 6),
    "maps/easy/03_basic_capacity.txt": Benchmark("Easy / Basic capacity", 8),
    "maps/medium/01_dead_end_trap.txt": Benchmark("Medium / Dead end trap", 15),
    "maps/medium/02_circular_loop.txt": Benchmark("Medium / Circular loop", 20),
    "maps/medium/03_priority_puzzle.txt": Benchmark("Medium / Priority puzzle", 12),
    "maps/hard/01_maze_nightmare.txt": Benchmark("Hard / Maze nightmare", 45),
    "maps/hard/02_capacity_hell.txt": Benchmark("Hard / Capacity hell", 60),
    "maps/hard/03_ultimate_challenge.txt": Benchmark("Hard / Ultimate challenge", 35),
    "maps/challenger/01_the_impossible_dream.txt": Benchmark(
        "Challenger / The Impossible Dream", 45, optional=True
    ),
}


def rel_path(path: Path) -> str:
    return str(path.relative_to(ROOT_DIR))


def status_icon(ok: bool) -> str:
    return "OK" if ok else "FAIL"


def run_valid_maps() -> tuple[list[str], list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    lines: list[str] = []

    header = (
        f"{'Status':<6}  {'Map':<34} {'Turns':>7}  {'Target':>7}  {'Delta':>7}"
    )
    lines.append(header)
    lines.append("-" * len(header))

    valid_maps = sorted(
        path for path in MAPS_DIR.rglob("*.txt") if "error" not in path.parts
    )

    for map_path in valid_maps:
        map_key = rel_path(map_path)
        benchmark = BENCHMARKS.get(map_key)

        try:
            world = MapParser().parse_file(str(map_path))
            result = SimulationEngine(world).run()
            turns = result.turns
        except Exception as exc:
            failures.append(f"{map_key}: {type(exc).__name__}: {exc}")
            lines.append(
                f"{status_icon(False):<6}  {map_path.stem:<34} {'ERR':>7}  {'-':>7}  {'-':>7}"
            )
            continue

        if benchmark is None or benchmark.target_turns is None:
            lines.append(
                f"{status_icon(True):<6}  {map_path.stem:<34} {turns:>7}  {'-':>7}  {'-':>7}"
            )
            continue

        delta = turns - benchmark.target_turns
        delta_text = f"{delta:+d}"
        passed_target = turns <= benchmark.target_turns
        lines.append(
            f"{status_icon(passed_target):<6}  {map_path.stem:<34} {turns:>7}  "
            f"{benchmark.target_turns:>7}  {delta_text:>7}"
        )

        if not passed_target:
            message = (
                f"{map_key}: {turns} turns vs target {benchmark.target_turns}"
            )
            if benchmark.optional:
                warnings.append(message)
            else:
                failures.append(message)

    return lines, failures, warnings


def run_error_maps() -> tuple[list[str], list[str]]:
    expected_failures: list[str] = []
    unexpected_passes: list[str] = []

    for map_path in sorted(path for path in MAPS_DIR.rglob("*.txt") if "error" in path.parts):
        try:
            world = MapParser().parse_file(str(map_path))
            SimulationEngine(world).run()
        except Exception:
            expected_failures.append(rel_path(map_path))
        else:
            unexpected_passes.append(rel_path(map_path))

    lines = [
        f"Expected failures: {len(expected_failures)}",
        f"Unexpected passes: {len(unexpected_passes)}",
    ]

    if unexpected_passes:
        preview = ", ".join(unexpected_passes[:5])
        if len(unexpected_passes) > 5:
            preview += ", ..."
        lines.append(f"Unexpected pass list: {preview}")

    return lines, unexpected_passes


def main() -> int:
    valid_lines, valid_failures, warnings = run_valid_maps()
    error_lines, unexpected_error_passes = run_error_maps()

    print("== Map Benchmark Report ==")
    for line in valid_lines:
        print(line)

    print("\n== Error Map Summary ==")
    for line in error_lines:
        print(line)

    if warnings:
        print("\n== Optional Benchmark Warnings ==")
        for warning in warnings:
            print(f"- {warning}")

    if valid_failures:
        print("\n== Failures ==")
        for failure in valid_failures:
            print(f"- {failure}")

    if unexpected_error_passes:
        return 1

    if valid_failures:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
