import contextlib
from dataclasses import dataclass
from enum import auto, IntEnum
from typing import Final

import numpy as np
from mesa import Agent, Model

from ainter.models.nagel_schreckenberg.units import discretize_length, discretize_speed, discretize_acceleration, \
    DiscreteLength, DiscreteAcceleration, DiscreteSpeed, SPEED_MAX, get_breaking_distance, convert_km_h_to_m_s

type VehicleId = int
type IntersectionPosition = int
type RoadPosition = tuple[int, int]
type Position = IntersectionPosition | RoadPosition

NULL_VEHICLE_ID: Final[VehicleId] = 0

def is_intersection_position(pos: Position) -> bool:
    return isinstance(pos, int)

def is_road_position(pos: Position) -> bool:
    return isinstance(pos, tuple) and len(pos) == 2 and isinstance(pos[0], int) and isinstance(pos[1], int)


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
        """Method that returns VehicleCharacteristic associated with a VehicleType.
        :returns: VehicleCharacteristic object associated with a given VehicleType.
        """
        # TODO: Fix so that the acc is zero when CELL_SIZE=2m AND DELTA_TIME=1s
        match self:
            case VehicleType.CAR:
                return VehicleCharacteristic(length=discretize_length(4.5),
                                             acc_forward=discretize_acceleration(2.),
                                             acc_backward=discretize_acceleration(2))

            case VehicleType.BUS:
                return VehicleCharacteristic(length=discretize_length(12.),
                                             acc_forward=discretize_acceleration(2.),
                                             acc_backward=discretize_acceleration(2.))

            case VehicleType.TRUCK:
                return VehicleCharacteristic(length=discretize_length(14.),
                                             acc_forward=discretize_acceleration(2.),
                                             acc_backward=discretize_acceleration(2.))

            case VehicleType.MOTORCYCLE:
                return VehicleCharacteristic(length=discretize_length(2.5),
                                             acc_forward=discretize_acceleration(2.5),
                                             acc_backward=discretize_acceleration(2))

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
                 vehicle_type: VehicleType,
                 path: list[int]) -> None:
        assert len(path) > 1, "Cannot construct a valid graph path from one node"

        super().__init__(model=model)
        self.type = vehicle_type
        self.speed = discretize_speed(0.)
        self.path = path
        self.from_node = self.path[0]
        self.to_node = self.path[-1]
        self.pos = self.from_node
        self.color = np.array([self.random.randint(64, 181) for _ in range(3)], dtype=np.uint8)
        _ = self.model.add_agent_to_environment(position=self.pos, agent_id=self.unique_id)


    def step(self) -> None:
        if self.finished():
            raise ValueError("Agent should be removed")

        distance = int(self.model.get_obstacle_distance(self.pos, self.unique_id))
        self.speed = self.model.move_agent(position=self.pos,
                                           agent_id=self.unique_id,
                                           speed=self.decide_speed(distance))

        if self.model.is_agent_leaving(position=self.pos,
                                       agent_id=self.unique_id,
                                       speed=self.speed):
            new_pos = self.calc_new_pos()

            if not self.model.can_accept_agent(position=new_pos,
                                               agent_id=self.unique_id,
                                               length=self.type.get_characteristic().length):
                return

            self.model.remove_agent_from_environment(position=self.pos,
                                                     agent_id=self.unique_id)
            if self.is_on_intersection():
                self.pos = new_pos
                _ = self.model.add_agent_to_environment(position=self.pos,
                                                        agent_id=self.unique_id,
                                                        color=self.color,
                                                        length=self.type.get_characteristic().length)

            elif self.is_on_road():
                self.pos = new_pos
                _ = self.model.add_agent_to_environment(position=self.pos,
                                                        agent_id=self.unique_id)

            else:
                raise ValueError("The position of an agent cannot be determined")

    def finished(self) -> bool:
        """Check if the agent has reached its destination"""
        return self.pos == self.to_node

    def remove(self) -> None:
        with contextlib.suppress(KeyError):
            self.model.remove_agent_from_environment(position=self.pos,
                                                     agent_id=self.unique_id)

            self.model.deregister_agent(self)

    def decide_speed(self, distance: DiscreteLength) -> DiscreteSpeed:
        nbd = get_breaking_distance(self.speed, self.type.get_characteristic().acc_backward) + self.random.randint(1, 2)

        if distance <= nbd:
            if self.speed < self.type.get_characteristic().acc_backward:
                self.speed = 0
            else:
                self.speed -= self.type.get_characteristic().acc_backward
        else:
            self.speed += self.type.get_characteristic().acc_forward
            if self.speed > discretize_speed(convert_km_h_to_m_s(SPEED_MAX)):
                self.speed = discretize_speed(convert_km_h_to_m_s(SPEED_MAX))

        return self.speed

    def is_on_intersection(self) -> bool:
        return is_intersection_position(self.pos)

    def is_on_road(self) -> bool:
        return is_road_position(self.pos)

    def calc_new_pos(self) -> Position:
        if self.is_on_intersection():
            current_journey_index = self.path.index(self.pos)
            return self.path[current_journey_index], self.path[current_journey_index + 1]
        elif self.is_on_road():
            current_journey_index = self.path.index(self.pos[1])
            return self.path[current_journey_index]

        raise ValueError("Unknown possition value")

