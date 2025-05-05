from mesa.space import NetworkGrid
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.nagel_schreckenberg.road import Road
from ainter.models.nagel_schreckenberg.intersection import Intersection


class RoadNetworkSpace(NetworkGrid):
    def __init__(self, environment: Environment):
        # Initialize base NetworkGrid with road graph
        print(type(environment))
        super().__init__(environment.road_graph)

        # Store roads and intersections for easy access
        self.roads: dict[tuple[int, int], Road] = environment.roads
        self.intersections: dict[int, Intersection] = environment.intersections

    def get_road(self, start: int, end: int) -> Road | None:
        """Return road object between two nodes."""
        return self.roads.get((start, end), None)

    def get_intersection(self, node_id: int) -> Intersection | None:
        """Return intersection object for a node."""
        return self.intersections.get(node_id, None)

    def get_agents_on_road(self, start: int, end: int) -> list:
        """Get all agents currently on the road (approximate by nodes for now)."""
        # Optionally: implement finer segment tracking if needed
        return [agent for agent in self.get_all_cell_contents(start)
                if getattr(agent, "to_node", None) == end]

    def place_vehicle_at_node(self, agent, node_id: int):
        """Place agent at intersection node."""
        self.place_agent(agent, node_id)

    def move_vehicle_to_node(self, agent, node_id: int):
        """Move vehicle to another node (intersection)."""
        self.move_agent(agent, node_id)
