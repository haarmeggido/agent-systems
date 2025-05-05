from mesa import Agent

from ainter.models.vehicle import Vehicle

class VehicleAgent(Agent):
    def __init__(self, unique_id, model, vehicle: Vehicle):
        super().__init__(unique_id, model)
        self.vehicle = vehicle
        self.speed = vehicle.speed
        self.path = vehicle.path
        self.current_node_index = 0

    def step(self):
        # Stub for now
        if self.current_node_index + 1 < len(self.path):
            self.current_node_index += 1
            self.pos = self.path[self.current_node_index]
