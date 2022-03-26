import uuid
import math
import random
import numpy as np
from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from marker import MarkerPurpose
from ant import Ant


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
    def __init__(self, x, y, r, stock):
        self.x = x
        self.y = y
        self.r = r
        self.stock = stock

    def portrayal_method(self):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "Color": "olive",
            "r": self.r * self.stock,
        }
        return portrayal

    def get_one_piece(self):
        self.stock -= 1


class Colony:
    def __init__(self, x, y, r, ants):
        self.x = x
        self.y = y
        self.r = r
        self.ants = ants
        self.food_picked = 0


class Ground(Model):
    collector = DataCollector(
        model_reporters={
            "Foods": lambda model: len(model.foods),
            "Danger markers": lambda model: len(
                [m for m in model.markers if m.purpose == MarkerPurpose.DANGER]
            ),
            "Food markers": lambda model: len(
                [m for m in model.markers if m.purpose == MarkerPurpose.FOOD]
            ),
        },
        agent_reporters={},
    )

    def __init__(
        self,
        n_colony,
        n_ants_per_colony,
        color_ants,
        color_colonies,
        n_obstacles,
        n_food,
        speed,
        allow_info_markers=True,
        allow_danger_markers=True,
        sight_distance=30,
    ):
        Model.__init__(self)
        self.space = ContinuousSpace(600, 600, False)
        self.schedule = RandomActivation(self)
        self.markers = (
            []
        )  # Access list of markers from robot through self.model.markers (both read and write)
        self.obstacles = (
            []
        )  # Access list of obstacles from robot through self.model.obstacles
        self.colonies = []
        self.foods = []
        self.color_ants = color_ants

        for _ in range(n_obstacles):
            self.obstacles.append(
                Obstacle(
                    random.random() * 500,
                    random.random() * 500,
                    10 + 20 * random.random(),
                )
            )

        for _ in range(n_food):
            x, y = random.random() * 500, random.random() * 500
            while [
                o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r
            ]:
                x, y = random.random() * 500, random.random() * 500
            self.foods.append(Food(x=x, y=y, r=random.randint(100, 300), stock=30))

        for idx_colony in range(n_colony):
            colony = Colony(x, y, [], color_colonies[idx_colony])
            x, y = random.random() * 500, random.random() * 500
            while [
                o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r
            ] or [f for f in self.foods if np.linalg.norm((f.x - x, f.y - y)) < f.r]:
                x, y = random.random() * 500, random.random() * 500

            ants = [
                Ant(
                    unique_id=int(uuid.uuid1()),
                    model=self,
                    x=x + random.random() * 20,
                    y=y + random.random() * 20,
                    speed=speed,
                    colony=colony,
                    angle=random.random() * 2 * np.pi,
                    sight_distance=sight_distance,
                    color=color_ants[idx_colony],
                )
                for _ in range(n_ants_per_colony[idx_colony])
            ]
            colony.ants = ants
            self.colonies.append(colony)
            for ant in ants:
                self.schedule.add(ant)

        self.datacollector = self.collector

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        if not self.foods:
            self.running = False
