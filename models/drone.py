from dataclasses import dataclass


@dataclass
class Drone():
    """Represent a drone moving along the shared routed path.

    Attributes:
        id: Sequential drone identifier used in the output.
        current_hub: Name of the hub where the drone is currently located.
        path_index: Current index in the chosen path. A value of ``0`` means
            the drone is still at the start hub.
        next_hub: Name of the hub the drone is currently traveling toward, if
            any.
        waiting: Whether the drone is blocked in the current turn because the
            destination hub or connecting edge is full.
        in_transit: Whether the drone is currently between hubs because a
            restricted destination requires an extra turn to complete.
        finished: Whether the drone has already reached the final hub.
    """

    id: int = 1
    current_hub: str | None = None
    next_hub: str | None = None
    path_index: int = 0
    waiting: bool = False
    in_transit: bool = False
    finished: bool = False
