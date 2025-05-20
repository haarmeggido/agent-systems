from dataclasses import dataclass
from enum import auto, IntEnum
from random import randint
from typing import Optional

import numpy as np
from mesa import Agent, Model

from ainter.models.nagel_schreckenberg.units import discretize_length, discretize_speed, discretize_acceleration, \
    DiscreteLength, DiscreteAcceleration, DiscreteSpeed

type VehicleId = int
type RoadPosition = tuple[int, slice]
type IntersectionPosition = tuple[slice, slice]


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
        # TODO: FIx so that the acc is zero when CELL_SIZE=2m AND DELTA_TIME=1s
        match self:
            case VehicleType.CAR:
                return VehicleCharacteristic(length=discretize_length(4.5),
                                             acc_forward=discretize_acceleration(2.),
                                             acc_backward=discretize_acceleration(-2))

            case VehicleType.BUS:
                return VehicleCharacteristic(length=discretize_length(12.),
                                             acc_forward=discretize_acceleration(2.),
                                             acc_backward=discretize_acceleration(-2.))

            case VehicleType.TRUCK:
                return VehicleCharacteristic(length=discretize_length(14.),
                                             acc_forward=discretize_acceleration(2.),
                                             acc_backward=discretize_acceleration(-2.))

            case VehicleType.MOTORCYCLE:
                return VehicleCharacteristic(length=discretize_length(2.5),
                                             acc_forward=discretize_acceleration(2.5),
                                             acc_backward=discretize_acceleration(-2))

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


class Vehicle(Agent):

    def __init__(self, model: Model,
                 type: VehicleType,
                 path: list[int],
                 ) -> None:
        super().__init__(model=model)

        self.type = type
        self.speed = discretize_speed(0.)
        self.path = path
        self.from_node = self.path[0]
        self.to_node = self.path[-1]
        self.pos = None                 # type: Optional[int | tuple[int, int]]
        self.inner_position = None
        # TODO use a proper self.rng
        # TODO: generate dark vehicles
        self.color = np.random.randint(128, 182, size=3, dtype=np.uint8)

        print("Vehicle", self.unique_id, "added", self.from_node)
        self.pos = self.from_node
        self.model.grid.intersections[self.pos].add_agent(agent_id=self.unique_id)


    def step(self) -> None:
        if self.is_on_intersection():
            intersection = self.model.grid.intersections[self.pos]

            if intersection.is_agent_leaving(agent_id=self.unique_id,
                                             speed=self.speed):
                print(self.unique_id, "Leaving intersection", self.pos)
                current_journey_index = self.path.index(self.pos)
                if current_journey_index == len(self.path) - 1:
                    print(self.unique_id, "Arrived at destination", self.to_node)
                    self.model.grid.intersections[self.pos].remove_agent(agent_id=self.unique_id)
                    self.remove()
                    return

                self.pos = (self.path[current_journey_index], self.path[current_journey_index + 1])
                road = self.model.grid.roads[self.pos]
                road.add_agent(agent_id=self.unique_id,
                               color=self.color,
                               lane=randint(0, road.lanes - 1),
                               length=self.type.get_characteristic().length)

        elif self.is_on_road():  # Immediately teleport agent to the next road segment
            road = self.model.grid.roads[self.pos]

            if road.is_agent_leaving(agent_id=self.unique_id,
                                     speed=self.speed):
                print(self.unique_id, "Leaving road", self.pos)
                current_journey_index = self.path.index(self.pos[1])
                self.pos = self.path[current_journey_index]
                intersection = self.model.grid.intersections[self.pos]
                intersection.add_agent(agent_id=self.unique_id)

            # Agents Obey the speed limit of the road
            # TODO: Check if an agent would collide
            self.speed = self.decide_speed(road)
            print("Agent", self.unique_id, "speed", self.speed)
            road.move_agent(agent_id=self.unique_id,
                            speed=self.speed)

    def decide_speed(self, road) -> DiscreteSpeed:
        # TODO: Make function to convert from km/h to m/s
        distance_to_obstacle = road.get_length_to_obstacle(agent_id=self.unique_id)

        if distance_to_obstacle < self.get_breaking_distance():
            return max(self.speed + self.type.get_characteristic().acc_backward, 2)

        return min(self.speed + self.type.get_characteristic().acc_forward, discretize_speed(road.max_speed / 3.6))

    def get_breaking_distance(self) -> DiscreteLength:
        return self.speed ** 2 / (2 * self.type.get_characteristic().acc_backward)

    def is_on_intersection(self) -> bool:
        return isinstance(self.pos, int)

    def is_on_road(self) -> bool:
        return isinstance(self.pos, tuple)
