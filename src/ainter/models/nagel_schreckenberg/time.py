from abc import ABC, abstractmethod

from ainter.models.nagel_schreckenberg.units import DiscreteTime


class TimeDensity(ABC):

    @abstractmethod
    def get_probability(self, time: DiscreteTime) -> float:
        pass


class NormalTimeDensity(TimeDensity):

    def get_probability(self, time: DiscreteTime) -> float:
        raise NotImplemented


class UniformTimeDensity(TimeDensity):

    def get_probability(self, time: DiscreteTime) -> float:
        return 0.1


def get_time_density_strategy(code: str) -> TimeDensity:
    match code:
        case "normal_dist":
            return NormalTimeDensity()

        case "uniform_dist":
            return UniformTimeDensity()

        case _:
            raise ValueError("Unknown strategy code provided")
