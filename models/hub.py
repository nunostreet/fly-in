from dataclasses import dataclass


@dataclass
class Hub:
    name: str
    x: int
    y: int
    metadata: dict
