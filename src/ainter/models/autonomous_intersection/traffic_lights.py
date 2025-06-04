from abc import ABC, abstractmethod
from copy import deepcopy

from ainter.models.autonomous_intersection.intersection_directions import IntersectionEntranceDirection
from ainter.models.nagel_schreckenberg.units import DiscreteTime


class TrafficLight(ABC):

    @abstractmethod
    def add_direction(self, direction: IntersectionEntranceDirection) -> None:
        pass

    @abstractmethod
    def has_right_of_way(self, direction: IntersectionEntranceDirection) -> bool:
        pass

    @abstractmethod
    def step(self) -> None:
        pass


class SimpleTrafficLight(TrafficLight):

    def __init__(self,
                 global_time_ref: DiscreteTime,
                 green_duration: DiscreteTime) -> None:
        self.time = deepcopy(global_time_ref)
        self.green_duration = green_duration
        self.directions = list()

    def add_direction(self, direction: IntersectionEntranceDirection) -> None:
        assert direction not in self.directions, "Cannot add an direction twice"
        self.directions.append(direction)

    def has_right_of_way(self, direction: IntersectionEntranceDirection) -> bool:
        assert direction in self.directions, "Cannot ask for unknow direction"

        total_phase = self.time // self.green_duration
        phase = total_phase % len(self.directions)

        return phase == self.directions.index(direction)

    def step(self) -> None:
        self.time += 1

