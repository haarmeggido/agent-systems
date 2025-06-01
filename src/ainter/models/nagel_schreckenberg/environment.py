from dataclasses import dataclass
from typing import Self

from networkx.classes import MultiDiGraph, DiGraph

from ainter.models.nagel_schreckenberg.intersection import Intersection
from ainter.models.nagel_schreckenberg.road import Road


def create_roads_from_graph(graph: MultiDiGraph, graph_di: DiGraph) -> dict[tuple[int, int], Road]:
    roads = dict()
    for start_id, end_id in graph_di.edges:
        start_data = graph.nodes[start_id]
        end_data = graph.nodes[end_id]
        edge_data = graph_di.edges[start_id, end_id]

        new_road = Road.from_graph_data(start_node_info=start_data,
                                        end_node_info=end_data,
                                        edge_info=edge_data)
        roads.update({(start_id, end_id): new_road})
    return roads

def create_intersections_from_graph(graph_di: DiGraph) -> dict[int, Intersection]:
    intersections = dict()
    for node_id in graph_di.nodes:
        node_data = graph_di.nodes[node_id]
        edges_data = {edge: graph_di.edges[edge]
                      for edge in set(graph_di.in_edges(node_id)) | set(graph_di.out_edges(node_id))}
        new_intersection = Intersection.from_graph_data(osm_id=node_id,
                                                        in_edges_info=edges_data,
                                                        node_info=node_data)
        intersections.update({node_id: new_intersection})
    return intersections


@dataclass(slots=True)
class Environment:
    road_graph: DiGraph
    roads: dict[tuple[int, int], Road]
    intersections: dict[int, Intersection]

    @classmethod
    def from_directed_graph(cls, graph: MultiDiGraph) -> Self:
        assert all(map(lambda x: x[2] == 0, graph.edges)), 'The convertion to DiGraph would result in information loss'

        graph_di = DiGraph(graph)

        roads = create_roads_from_graph(graph, graph_di)
        intersections = create_intersections_from_graph(graph_di)

        return cls(road_graph=graph_di,
                   roads=roads,
                   intersections=intersections)
