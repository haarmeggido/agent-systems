from abc import ABC, abstractmethod

from ainter.models.nagel_schreckenberg.units import DiscreteTime


class TrafficLight(ABC):

    @abstractmethod
    def has_right_of_way(self) -> bool:
        pass

    @abstractmethod
    def step(self) -> None:
        pass


class SimpleTrafficLight(TrafficLight):

    def __init__(self,
                 global_time_ref: DiscreteTime,
                 duration: DiscreteTime,
                 cycle_duration: DiscreteTime,
                 shift: DiscreteTime) -> None:
        self.time = global_time_ref

    def has_right_of_way(self) -> bool:
        return True

    def step(self) -> None:
        pass