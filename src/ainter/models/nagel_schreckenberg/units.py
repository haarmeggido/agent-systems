from abc import ABC, abstractmethod
from datetime import time
from typing import Final

import numpy as np


type PhysicalTime = time                        # In seconds
type PhysicalLength = np.float64 | float        # In meters
type PhysicalSpeed = np.float64 | float         # In meters per seconds
type PhysicalAcceleration = np.float64 | float  # In meters per second squared

type DiscreteTime = np.uint32 | int             # In time step
type DiscreteLength = np.uint16                 # In the number of grid cells
type DiscreteSpeed = np.int8                    # In grid cells per time steps
type DiscreteAcceleration = np.int8             # In grid cells per time step squared

DELTA_TIME: Final[float] = np.float64(0.5)

CELL_SIZE: Final[PhysicalLength] = np.float64(0.25)
LINE_WIDTH: Final[PhysicalLength] = np.float32(3.)

SPEED_MAX: Final[PhysicalSpeed] = np.float64(50)
SPEED_MIN: Final[PhysicalSpeed] = np.float64(-10)
DEFAULT_ROAD_MAX_SPEED: Final[PhysicalSpeed] = SPEED_MAX

ACCELERATION_MAX: Final[PhysicalAcceleration] = np.float64(2.5)
ACCELERATION_MIN: Final[PhysicalAcceleration] = np.float64(-1.5)


def discretize_time(time_obj: time) -> DiscreteTime:
    return np.uint32(np.round((time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second) / DELTA_TIME))

def discretize_length(length: PhysicalLength) -> DiscreteLength:
    """Converts the physical length measure into discrete length value"""
    return np.uint16(np.round(length / CELL_SIZE))

def discretize_speed(speed: PhysicalSpeed) -> DiscreteSpeed:
    """Converts the physical speed measure into discrete speed value"""
    return np.int8(np.round(speed * DELTA_TIME / CELL_SIZE))

def discretize_acceleration(acceleration: PhysicalAcceleration) -> DiscreteAcceleration:
    """Converts the physical length measure into discrete Length value"""
    return np.int8(np.round(acceleration * DELTA_TIME * DELTA_TIME / CELL_SIZE))


class TimeDensity(ABC):

    @abstractmethod
    def get_probability(self, t: DiscreteTime) -> float:
        pass


class NormalTimeDensity(TimeDensity):

    def get_probability(self, t: DiscreteTime) -> float:
        raise NotImplemented


class UniformTimeDensity(TimeDensity):

    def get_probability(self, t: DiscreteTime) -> float:
        return 0.1


def get_time_density_strategy(code: str) -> TimeDensity:
    match code:
        case "normal_dist":
            return NormalTimeDensity()

        case "uniform_dist":
            return UniformTimeDensity()

        case _:
            raise ValueError("Unknown strategy code provided")
