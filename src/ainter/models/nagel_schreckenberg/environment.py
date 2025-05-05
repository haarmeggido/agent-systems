from dataclasses import dataclass
from typing import Self

import networkx as nx
from networkx.classes import MultiDiGraph, DiGraph

from ainter.models.nagel_schreckenberg.intersection import Intersection
from ainter.models.nagel_schreckenberg.road import Road
from ainter.models.vehicles.vehicle import Vehicle


@dataclass(slots=True)
class Environment:
    road_graph: DiGraph
    roads: dict[tuple[int, int], Road]
    intersections: dict[int, Intersection]

    @classmethod
    def from_directed_graph(cls, graph: MultiDiGraph) -> Self:
        # TODO: Assert that a MultiDiGraph can be converted to DiGraph without loosing generality
        graph_di = DiGraph(graph)

        roads = dict()
        for start_id, end_id in graph_di.edges:
            start_data = graph.nodes[start_id]
            end_data = graph.nodes[end_id]
            edge_data = graph_di.edges[start_id, end_id]

            new_road = Road.from_graph_data(start_node_info=start_data,
                                            end_node_info=end_data,
                                            edge_info=edge_data)
            roads.update({(start_id, end_id): new_road})

        intersections = dict()
        for node_id in graph_di.nodes:
            node_data = graph_di.nodes[node_id]
            new_intersection = Intersection.from_graph_data(osm_id=node_id,
                                                            node_info=node_data)
            intersections.update({node_id: new_intersection})

        return cls(road_graph=graph_di,
                   roads=roads,
                   intersections=intersections)
