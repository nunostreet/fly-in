from dataclasses import dataclass


@dataclass
class Drone():
    """Represent a drone moving along the shared routed path.

    Attributes:
        id: Sequential drone identifier used in the output.
        path_index: Current index in the chosen path. A value of ``0`` means
            the drone is still at the start hub.
        finished: Whether the drone has already reached the final hub.
    """

    id: int = 1
    path_index: int = 0
    finished: bool = False
