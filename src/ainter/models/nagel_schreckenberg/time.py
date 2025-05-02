from abc import ABC, abstractmethod

from ainter.models.nagel_schreckenberg.units import DiscreteTime


class TimeDensity(ABC):

    @abstractmethod
    def get_probability(self, time: DiscreteTime) -> float:
        pass


class NormalTimeDensity(TimeDensity):

    def get_probability(self, time: DiscreteTime) -> float:
        pass


def get_time_density_strategy(code: str) -> TimeDensity:
    match code:
        case "normal_dist":
            return NormalTimeDensity()

        case _:
            raise ValueError("Unknown strategy code provided")
