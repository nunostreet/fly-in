from dataclasses import dataclass


@dataclass
class Drone():
    id: int = 1
    path_index: int = 0
    finished: bool = False
