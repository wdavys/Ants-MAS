import uuid
import math
import random
import numpy as np
from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from .marker import MarkerPurpose


class Obstacle:  # Environnement: obstacle infranchissable
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def portrayal_method(self):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "Color": "black",
            "r": self.r,
        }
        return portrayal


class Food:
    def __init__(self, x, y, r, weight):
        self.x = x
        self.y = y
        self.r = r
        self.n = weight

    def portrayal_method(self):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "Color": "olive",
            "r": self.r * self.weight,
        }
        return portrayal

    def get_one_piece(self):
        self.weight -= 1


class Colony:
    def __init__(self, x, y, r, ants):
        self.x = x
        self.y = y
        self.r = r
        self.ants = ants


class MinedZone(Model):
    collector = DataCollector(
        model_reporters={
            "Mines": lambda model: len(model.mines),
            "Danger markers": lambda model: len(
                [m for m in model.markers if m.purpose == MarkerPurpose.DANGER]
            ),
            "FOOD markers": lambda model: len(
                [m for m in model.markers if m.purpose == MarkerPurpose.FOOD]
            ),
            "Steps in quicksand": lambda model: model.step_in_quicksands,
        },
        agent_reporters={},
    )

    def __init__(
        self,
        n_robots,
        n_obstacles,
        n_quicksand,
        n_mines,
        speed,
        allow_info_markers=True,
        allow_danger_markers=True,
        allow_smart_angle_chgt=True,
    ):
        Model.__init__(self)
        self.space = ContinuousSpace(600, 600, False)
        self.schedule = RandomActivation(self)
        self.mines = []  # Access list of mines from robot through self.model.mines
        self.markers = (
            []
        )  # Access list of markers from robot through self.model.markers (both read and write)
        self.obstacles = (
            []
        )  # Access list of obstacles from robot through self.model.obstacles
        self.quicksands = (
            []
        )  # Access list of quicksands from robot through self.model.quicksands
        for _ in range(n_obstacles):
            self.obstacles.append(
                Obstacle(
                    random.random() * 500,
                    random.random() * 500,
                    10 + 20 * random.random(),
                )
            )
        for _ in range(n_robots):
            x, y = random.random() * 500, random.random() * 500
            while [
                o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r
            ] or [
                o for o in self.quicksands if np.linalg.norm((o.x - x, o.y - y)) < o.r
            ]:
                x, y = random.random() * 500, random.random() * 500
            self.schedule.add(
                Robot(
                    int(uuid.uuid1()),
                    self,
                    x,
                    y,
                    speed,
                    2 * speed,
                    allow_smart_angle_chgt,
                    allow_danger_markers,
                    allow_info_markers,
                    random.random() * 2 * math.pi,
                )
            )
        for _ in range(n_mines):
            x, y = random.random() * 500, random.random() * 500
            while [
                o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r
            ] or [
                o for o in self.quicksands if np.linalg.norm((o.x - x, o.y - y)) < o.r
            ]:
                x, y = random.random() * 500, random.random() * 500
            self.mines.append(Mine(x, y))
        self.datacollector = self.collector
        # self.t = 0
        self.step_in_quicksands = 0

    def step(self):
        # self.t += 1
        self.datacollector.collect(self)
        self.schedule.step()
        if not self.mines:
            self.running = False

        self.step_in_quicksands += len(
            [
                robot
                for robot in self.schedule.agents
                if robot.speed == robot.quicksand_speed
            ]
        )
