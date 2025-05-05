from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import NetworkModule
from mesa.visualization.UserParam import UserSettableParameter

from ainter.configs.env_creation import EnvConfig
from ainter.models.nagel_schreckenberg.units import discretize_time
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.nagel_schreckenberg.road_network_space import RoadNetworkSpace
from ainter.models.nagel_schreckenberg.model_mesa import NaSchUrbanModel
from ainter.models.data.osmnx import get_data_from_bbox

def vehicle_portrayal(agent):
    if agent is None or not hasattr(agent, "vehicle"):
        return

    color_map = {
        "CAR": "#0074D9",
        "BUS": "#FF851B",
        "TRUCK": "#2ECC40",
        "MOTORCYCLE": "#B10DC9"
    }

    vehicle_type = agent.vehicle.type.name
    return {
        "shape": "circle",
        "color": color_map.get(vehicle_type, "#AAAAAA"),
        "radius": 5,
        "tooltip": f"{vehicle_type} (ID: {agent.unique_id}) at node {agent.path[agent.current_node_index]}"
    }


def build_model(env_config: EnvConfig):
    return NaSchUrbanModel(env_config)


def create_network_portrayal(env: Environment):
    nodes = {}
    edges = []

    for node in env.road_graph.nodes:
        nodes[node] = (env.road_graph.nodes[node]['x'], env.road_graph.nodes[node]['y'])

    for u, v in env.road_graph.edges:
        edges.append((u, v))

    portrayal = {
        "nodes": [{"id": node_id, "x": pos[0], "y": pos[1]} for node_id, pos in nodes.items()],
        "edges": [{"source": u, "target": v} for u, v in edges]
    }
    return portrayal


# Create a test configuration
config = EnvConfig.from_json("test\resources\czarnowiejska.json") # Is it right??

test_env = Environment.from_directed_graph(
    get_data_from_bbox(config.map_box) # Finished with error here, 11:13
)

network_portrayal = create_network_portrayal(test_env)

network_module = NetworkModule(
    portrayal_method=vehicle_portrayal,
    canvas_width=800,
    canvas_height=600
)

server = ModularServer(
    NaSchUrbanModel,
    [network_module],
    "NaSch Urban Traffic Model",
    {
        "config": config
    }
)

server.port = 8521  # Default port
