from dataclasses import dataclass, field
from enum import Enum
from random import choices
from typing import Self

import numpy as np

from ainter.models.nagel_schreckenberg.units import discretize_length, discretize_speed, discretize_acceleration, \
    DiscreteLength, DiscreteSpeed, DiscreteAcceleration


@dataclass(slots=True, frozen=True)
class VehicleCharacteristic:
    length: DiscreteLength
    acc_forward: DiscreteAcceleration
    acc_backward: DiscreteAcceleration


class VehicleType(Enum):
    """Vehicle Type with its associated spawn rate"""
    CAR = np.float64(0.45)
    BUS = np.float64(0.175)
    TRUCK = np.float64(0.125)
    MOTORCYCLE = np.float64(0.25)

    def get_characteristic(self) -> VehicleCharacteristic:
        """Method that returns VehiclePhysicalConfiguration associated with a VehicleType.
        :returns: VehiclePhysicalConfiguration object associated with a given VehicleType.
        """
        match self:
            case VehicleType.CAR:
                return VehicleCharacteristic(length=discretize_length(4.5),
                                             acc_forward=discretize_acceleration(2.),
                                             acc_backward=discretize_acceleration(-1.5))

            case VehicleType.BUS:
                return VehicleCharacteristic(length=discretize_length(12.),
                                             acc_forward=discretize_acceleration(1.5),
                                             acc_backward=discretize_acceleration(-1.))

            case VehicleType.TRUCK:
                return VehicleCharacteristic(length=discretize_length(14.),
                                             acc_forward=discretize_acceleration(1.),
                                             acc_backward=discretize_acceleration(-1.))

            case VehicleType.MOTORCYCLE:
                return VehicleCharacteristic(length=discretize_length(2.5),
                                             acc_forward=discretize_acceleration(2.5),
                                             acc_backward=discretize_acceleration(-1.5))

            case _:
                raise ValueError("Unknown Vehicle Type provided")


@dataclass(slots=True)
class Vehicle:
    type: VehicleType
    characteristic: VehicleCharacteristic = field(init=False)
    speed: DiscreteSpeed = field(init=False)
    from_node: int
    to_node: int

    def __post_init__(self) -> None:
        self.characteristic = self.type.get_characteristic()
        self.speed = discretize_speed(0.)

    @classmethod
    def from_random(cls) -> Self:
        """Generates a vehicle with random type."""
        all_possibilities = list(VehicleType)
        probability_distribution = list(map(lambda x: x.value, all_possibilities))

        vehicle, = choices(list(VehicleType), weights=probability_distribution, k=1)
        return cls(type=vehicle, from_node=1, to_node=1)


def generate_vehicles(time_steps):
    pass