from dataclasses import dataclass, field
from enum import auto, IntEnum
from random import choices, random, choice

from networkx import DiGraph, descendants

from ainter.models.data.osmnx import bfs_shortest_path
from ainter.models.nagel_schreckenberg.units import discretize_length, discretize_speed, discretize_acceleration, \
    DiscreteLength, DiscreteSpeed, DiscreteAcceleration, DiscreteTime, TimeDensity


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
    speed: DiscreteSpeed = field(init=False)
    start_time: DiscreteTime
    from_node: int = field(init=False)
    to_node: int = field(init=False)
    path: list[int]

    def __post_init__(self) -> None:
        self.speed = discretize_speed(0.)
        self.from_node = self.path[0]
        self.to_node = self.path[-1]


def generate_vehicles(graph: DiGraph,
                      start_time: DiscreteTime,
                      end_time: DiscreteTime,
                      probability: TimeDensity) -> list[Vehicle]:
    vehicles = []
    types = list(VehicleType)
    idx = 0

    for time_step in range(start_time, end_time):
        if random() < probability.get_probability(time_step):
            while True:
                start_node = choice(list(graph.nodes))
                end_node_possibilities = list(descendants(graph, start_node))
                if len(end_node_possibilities) > 0:
                    break

            end_node = choice(end_node_possibilities)

            path = bfs_shortest_path(graph, start_node, end_node)

            # Randomly select a vehicle type
            vehicle_type, = choices(types, weights=list(map(lambda x: x.get_pdf(), types)),k=1)
            vehicles.append(Vehicle(
                id=idx,
                type=vehicle_type,
                start_time=time_step,
                path=path,
            ))
            idx += 1

    return vehicles
