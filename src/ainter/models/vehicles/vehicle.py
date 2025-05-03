from dataclasses import dataclass, field
from enum import auto, IntEnum
from random import choices, random, choice
from typing import Self

import networkx as nx

from ainter.models.data.osmnx import bfs_shortest_path
from ainter.models.nagel_schreckenberg.time import TimeDensity
from ainter.models.nagel_schreckenberg.units import discretize_length, discretize_speed, discretize_acceleration, \
    DiscreteLength, DiscreteSpeed, DiscreteAcceleration, DiscreteTime


@dataclass(slots=True, frozen=True)
class VehicleCharacteristic:
    length: DiscreteLength
    acc_forward: DiscreteAcceleration
    acc_backward: DiscreteAcceleration


class VehicleType(IntEnum):
    """Vehicle Type with its associated spawn rate"""
    CAR = auto()
    BUS = auto()
    TRUCK = auto()
    MOTORCYCLE = auto()

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

        raise ValueError("Unknown Vehicle Type provided")

    def get_pdf(self) -> float:
        """Get the probability of spawning a particular type of vehicle"""
        match self:
            case VehicleType.CAR:
                return 0.45

            case VehicleType.BUS:
                return 0.175

            case VehicleType.TRUCK:
                return 0.125

            case VehicleType.MOTORCYCLE:
                return 0.25

        raise ValueError("Unknown Vehicle Type provided")


@dataclass(slots=True)
class Vehicle:
    id: int
    type: VehicleType
    # TODO: consider only storing a characteristic id and not an characteristic object for every vehicle
    characteristic: VehicleCharacteristic = field(init=False)
    speed: DiscreteSpeed = field(init=False)
    start_time: DiscreteTime
    from_node: int
    to_node: int
    path: list[int]

    def __post_init__(self) -> None:
        self.characteristic = self.type.get_characteristic()
        self.speed = discretize_speed(0.)


def generate_vehicles(graph: nx.MultiDiGraph,
                      start_time: DiscreteTime,
                      end_time: DiscreteTime,
                      probability: TimeDensity) -> list[Vehicle]:
    vehicles = []
    types = list(VehicleType)
    idx = 0

    for time_step in range(start_time, end_time):
        if random() < probability.get_probability(time_step):
            start_node = choice(list(graph.nodes))
            # TODO: Check if a node does not have any descendants
            end_node = choice(list(nx.descendants(graph, start_node)))

            path = bfs_shortest_path(graph, start_node, end_node)

            # Randomly select a vehicle type
            vehicle_type, = choices(types, weights=list(map(lambda x: x.get_pdf(), types)),k=1)
            vehicles.append(Vehicle(
                id=idx,
                type=vehicle_type,
                start_time=time_step,
                from_node=start_node,
                to_node=end_node,
                path=path,
            ))
            idx += 1

    return vehicles
