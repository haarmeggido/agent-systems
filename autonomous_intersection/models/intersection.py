from mesa import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from models.intersection_manager import IntersectionManager
from models.vehicle import VehicleAgent
import random

class IntersectionModel(Model):
    def __init__(self, width=10, height=10, num_vehicles=4):
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = SimultaneousActivation(self)

        # Define intersection (4 middle squares)
        self.intersection_center = (5, 5)
        self.intersection_area = {(5, 5), (5, 6), (6, 5), (6, 6)}

        # Entry points for vehicles (fixed locations for clarity)
        self.entry_points = {
            "N": (5, 0),
            "S": (6, 9),
            "E": (9, 5),
            "W": (0, 6),
        }
        self.next_agent_id = 4

        # Create Intersection Manager
        self.intersection_manager = IntersectionManager(99, self)
        self.schedule.add(self.intersection_manager)

        # Spawn vehicles at correct starting positions
        for i, (direction, pos) in enumerate(self.entry_points.items()):
            agent = VehicleAgent(i, self, direction)
            self.grid.place_agent(agent, pos)
            self.schedule.add(agent)

    def spawn_vehicles(self):
        """Spawn new vehicles at entry points with a 1/4 probability if space is free."""
        for direction, pos in self.entry_points.items():
            if random.random() < 0.05:  # 5% chance
                if not self.grid.is_cell_empty(pos):
                    continue  # Don't spawn if space is occupied

                new_vehicle = VehicleAgent(self.next_agent_id, self, direction)
                self.grid.place_agent(new_vehicle, pos)
                self.schedule.add(new_vehicle)
                self.next_agent_id += 1  # Ensure unique ID

    def step(self):
        self.schedule.step()
        self.spawn_vehicles()
