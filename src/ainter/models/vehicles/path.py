import itertools
from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Any, Self

import networkx as nx
from networkx import descendants

from ainter.models.data.osmnx import bfs_shortest_path
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.nagel_schreckenberg.units import discretize_length
from ainter.models.vehicles.vehicle import VehicleType


class ActionType(IntEnum):
    GO_TO_INTERSECTION = 0
    GO_TO_ROAD = auto()
    CHANGE_LANE = auto()


@dataclass(slots=True)
class Action:
    action_type: ActionType
    additional_data: dict[str, Any]


@dataclass(slots=True)
class Path:
    high_level_path: list[int]
    detailed_path: list[Action]

    @classmethod
    def from_graph(cls, random, agent_type: VehicleType, env: Environment, min_path_length: int) -> Self:
        graph = env.road_graph
        vehicle_minimum_road_length = agent_type.get_characteristic().length + discretize_length(2.)
        possible_starting_nodes = set(filter(lambda x: len(list(descendants(graph, x))) != 0, graph.nodes))

        # TODO: Assert if the path cannot ever be chosen, bc of constraints
        while True:
            starting_node = random.choice(possible_starting_nodes)
            possible_ending_node = random.choice(descendants(graph, starting_node))

            path = bfs_shortest_path(graph, starting_node, possible_ending_node)
            if len(path) < min_path_length:
                continue

            if any(map(lambda x: discretize_length(graph.adj[x[0]][x[1]]['length']) < vehicle_minimum_road_length,
                       itertools.pairwise(path))):
                continue

        assert path is not None, "Path cannot be None"

        return cls(high_level_path=path, detailed_path=enrich_path(random, graph, path))


def enrich_path(rng, env: Environment, path: list[int]) -> list[Action]:
    full_path = list()

    for start, end in itertools.pairwise(path):
        full_path.append(Action(ActionType.GO_TO_INTERSECTION, {'to': start}))
        full_path.append(Action())

    full_path.append(Action(ActionType.GO_TO_INTERSECTION, {'to': path[-1]}))

    return full_path
