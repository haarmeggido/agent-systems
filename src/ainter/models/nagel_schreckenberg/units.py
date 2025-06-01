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

DELTA_TIME: Final[float] = np.float64(1.)

CELL_SIZE: Final[PhysicalLength] = np.float64(2.)
LINE_WIDTH: Final[PhysicalLength] = np.float32(3.)

SPEED_MAX: Final[PhysicalSpeed] = np.float64(50)
SPEED_MIN: Final[PhysicalSpeed] = np.float64(-10)
DEFAULT_ROAD_MAX_SPEED: Final[PhysicalSpeed] = SPEED_MAX

ACCELERATION_MAX: Final[PhysicalAcceleration] = np.float64(2.5)
ACCELERATION_MIN: Final[PhysicalAcceleration] = np.float64(-1.5)

ROAD_COLOR: Final[np.uint8] = np.uint8(64)

MIN_JUMP_PATH_NODES_LENGTH: Final = 4


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

def convert_km_h_to_m_s(speed_kmh: float) -> PhysicalSpeed:
    """Converts speed from km/h to m/s"""
    return np.float64(speed_kmh * 1000 / 3600)


class TimeDensity(ABC):

    @abstractmethod
    def __call__(self, t: DiscreteTime) -> float:
        pass


class NormalTimeDensity(TimeDensity):

    def __call__(self, t: DiscreteTime) -> float:
        peak1_mu_seconds: float = 8 * 3600  # 8:00
        peak2_mu_seconds: float = 16 * 3600 # 16:00

        sigma_seconds: float = 1.5 * 3600
        amplitude: float = 0.3

        def gaussian_component(current_time: float, peak_mu: float, sigma: float, A: float) -> float:
            return A * np.exp(-np.square(current_time - peak_mu) / (2 * np.square(sigma)))

        time_float = float(t)
        prob_peak1 = gaussian_component(time_float, peak1_mu_seconds, sigma_seconds, amplitude)
        prob_peak2 = gaussian_component(time_float, peak2_mu_seconds, sigma_seconds, amplitude)

        return prob_peak1 + prob_peak2


class UniformTimeDensity(TimeDensity):

    def __call__(self, t: DiscreteTime) -> float:
        return 0.2


def get_time_density_strategy(code: str) -> TimeDensity:
    match code:
        case "normal_dist":
            return NormalTimeDensity()

        case "uniform_dist":
            return UniformTimeDensity()

        case _:
            raise ValueError("Unknown strategy code provided")
