from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from models.intersection import IntersectionModel

def vehicle_portrayal(agent):
    if agent is None:
        return
    
    color_map = {
        "approaching": "blue",
        "waiting": "yellow",
        "crossing": "green",
        "exited": "gray"
    }

    return {
        "Shape": "circle",
        "Color": color_map.get(agent.state, "black"),  # Default to black if unknown state
        "Filled": "true",
        "Layer": 1,
        "r": 0.5,  # Radius of circle
        "text": agent.unique_id,  # Show vehicle ID
        "text_color": "white"
    }


grid = CanvasGrid(vehicle_portrayal, 10, 10, 500, 500)

server = ModularServer(
    IntersectionModel,
    [grid],
    "Autonomous Intersection",
    {"width": 10, "height": 10, "num_vehicles": 4}
)

server.port = 8521
