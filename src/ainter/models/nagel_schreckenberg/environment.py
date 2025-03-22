from dataclasses import dataclass
from typing import Self

import networkx as nx
from networkx.classes import MultiDiGraph

from ainter.models.nagel_schreckenberg.intersection import Intersection
from ainter.models.nagel_schreckenberg.road import Road


@dataclass(slots=True)
class Environment:
    road_graph: MultiDiGraph
    roads: dict[tuple[int, int], Road]
    intersections: dict[int, Intersection]

    @classmethod
    def from_directed_graph(cls, graph: MultiDiGraph) -> Self:
        # TODO: Assert graph not empty
        t = nx.bfs_tree(graph, tuple(graph.nodes)[0])

        roads = dict()
        for start_id, end_id in t.edges():
            edge_data = graph.adj[start_id][end_id][0]

            # TODO: handle lanes:backward lanes:forward
            new_road = Road.from_length(length=edge_data['length'],
                                        # TODO: Fix missing lanes data
                                        lanes_forward=int(edge_data.get('lanes', 2)) // 2,
                                        lanes_backward=int(edge_data.get('lanes', 2)) // 2)
            roads.update({(start_id, end_id): new_road})

        intersections = dict()
        for node_id in t.nodes():
            intersections.update({node_id: Intersection.from_grid()})

        return cls(road_graph=graph, roads=roads, intersections=intersections)
