from mesa import Model
from mesa.time import SimultaneousActivation

from ainter.configs.env_creation import EnvConfig
from ainter.models.data.osmnx import get_data_from_bbox
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.nagel_schreckenberg.units import discretize_time
from ainter.models.vehicles.vehicle import Vehicle, generate_vehicles
from ainter.models.vehicles.vehicle_mesa import VehicleAgent
from ainter.models.nagel_schreckenberg.road_network_space import RoadNetworkSpace

class NaSchUrbanModel(Model):
    def __init__(self, config: EnvConfig):
        super().__init__()
        self.schedule = SimultaneousActivation(self)
        graph = get_data_from_bbox(config.map_box)
        env = Environment.from_directed_graph(graph)
        self.space = RoadNetworkSpace(env)

        self.vehicle_agents = []
        vehicles = generate_vehicles(env.road_graph,
                                     discretize_time(config.physics.start_time),
                                     discretize_time(config.physics.end_time),
                                     config.vehicles.time_density_strategy)
        for v in vehicles:
            agent = VehicleAgent(v.id, self, v)
            self.vehicle_agents.append(agent)
            self.schedule.add(agent)
            self.space.place_agent(agent, v.from_node)

    def step(self):
        self.schedule.step()
