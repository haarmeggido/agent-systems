from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Self


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


@dataclass(slots=True)
class IntersectionDirection:
    direction: IntersectionEntranceDirection
    lanes: int
