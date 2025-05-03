from typing import Final

import numpy as np


type PhysicalTime = np.float64 | float          # In seconds
type PhysicalLength = np.float64 | float        # In meters
type PhysicalSpeed = np.float64 | float         # In meters per seconds
type PhysicalAcceleration = np.float64 | float  # In meters per second squared

type DiscreteTime = np.uint32 | int             # In time step
type DiscreteLength = np.uint16                 # In the number of grid cells
type DiscreteSpeed = np.int8                    # In grid cells per time steps
type DiscreteAcceleration = np.int8             # In grid cells per time step squared

DELTA_TIME: Final[PhysicalTime] = np.float64(0.5)

CELL_SIZE: Final[PhysicalLength] = np.float64(0.25)

SPEED_MAX: Final[PhysicalSpeed] = np.float64(20)
SPEED_MIN: Final[PhysicalSpeed] = np.float64(-10)

ACCELERATION_MAX: Final[PhysicalAcceleration] = np.float64(2.5)
ACCELERATION_MIN: Final[PhysicalAcceleration] = np.float64(-1.5)


def discretize_length(length: PhysicalLength) -> DiscreteLength:
    """Converts the physical length measure into discrete length value"""
    return np.uint16(np.round(length / CELL_SIZE))

def discretize_speed(speed: PhysicalSpeed) -> DiscreteSpeed:
    """Converts the physical speed measure into discrete speed value"""
    return np.int8(np.round(speed * DELTA_TIME / CELL_SIZE))

def discretize_acceleration(acceleration: PhysicalAcceleration) -> DiscreteAcceleration:
    """Converts the physical length measure into discrete Length value"""
    return np.int8(np.round(acceleration * DELTA_TIME * DELTA_TIME / CELL_SIZE))

def reconstruct_length(length: DiscreteLength) -> PhysicalLength:
    return np.float64(length * CELL_SIZE)
