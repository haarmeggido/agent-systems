from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Self

from ainter.models.autonomous_intersection.lane_directions import LaneDirections


class IntersectionEntranceDirection(IntEnum):
    NORTH = 0
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

    def get_left_of(self) -> Self:
        return IntersectionEntranceDirection((self - 1) % len(list(IntersectionEntranceDirection)))

    def get_right_of(self) -> Self:
        return IntersectionEntranceDirection((self + 1) % len(list(IntersectionEntranceDirection)))

    def get_straight(self) -> Self:
        return self.get_left_of().get_left_of()

    def get_direction(self, other) -> LaneDirections:
        diff_direction = (self.value - other.value) % len(list(IntersectionEntranceDirection))

        if diff_direction == 0:
            return LaneDirections.STRAIGHT
        if diff_direction == 1:
            return LaneDirections.RIGHT
        if diff_direction == 2:
            return LaneDirections.STRAIGHT
        return LaneDirections.LEFT

@dataclass(slots=True)
class IntersectionDirection:
    direction: IntersectionEntranceDirection
    name: str
    action_slice: tuple[slice, slice] | None
    lanes: int
