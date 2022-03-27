import uuid
import random
import numpy as np
from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from ant import Ant
from marker import MarkerPurpose

RADIUS_COLONY = 2

class Obstacle:
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
    def __init__(self, x, y, stock, color_food):
        self.x = x
        self.y = y
        self.stock = stock
        self.r = stock
        self.color_food = color_food

    def portrayal_method(self):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "Color": self.color_food,
            "r": self.stock,
        }
        return portrayal

    def get_one_piece(self):
        self.stock -= 1


class Colony:
    def __init__(self, x, y, r, ants, color_colony, id_colony, markers_colors):
        self.x = x
        self.y = y
        self.r = r
        self.ants = ants
        self.food_picked = 0
        self.color_colony = color_colony
        self.id_colony = id_colony
        self.markers_colors = markers_colors
    
    def portrayal_method(self):
        portrayal = {
            "Shape": "circle",
            "Filled": "false",
            "Layer": 1,
            "Color": self.color_colony,
            "r": self.r,
        }
        return portrayal


class Ground(Model):
    def __init__(
        self,
        n_colonies,
        n_ants_per_colony,
        color_ants,
        color_colonies,
        color_food,
        n_obstacles,
        n_foods,
        markers_colors,
        speed,
        allow_info_markers=True,
        allow_danger_markers=True,
        sight_distance=50,
    ):
        Model.__init__(self)
        self.space = ContinuousSpace(500, 500, False)
        self.schedule = RandomActivation(self)

        self.markers_dict = {str(id): [] for id in range(n_colonies)}
            # Access list of markers from robot through self.model.markers (both read and write)
        self.obstacles = (
            []
        )  # Access list of obstacles from robot through self.model.obstacles
        self.colonies = []
        self.foods = []
        self.color_ants = color_ants
        self.color_colonies = color_colonies
        self.color_food = color_food

        for _ in range(n_obstacles):
            self.obstacles.append(
                Obstacle(
                    random.random() * 500,
                    random.random() * 500,
                    10 + 20 * random.random(),
                )
            )

        for _ in range(n_foods):
            x, y = random.random() * 500, random.random() * 500
            stock = random.randint(10, 100)
            while [o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) <= o.r + stock]:
                x, y = random.random() * 500, random.random() * 500
                stock = random.randint(10, 100)
            food = Food(x, y, stock, color_food=self.color_food)
            self.foods.append(food)

        for id_colony in range(n_colonies):
            x, y  = random.random() * 500, random.random() * 500
            r = RADIUS_COLONY * n_ants_per_colony[id_colony]
            while [o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) <= o.r + r] \
            or [f for f in self.foods if np.linalg.norm((f.x - x, f.y - y)) <= f.stock + r] \
            or [c for c in self.colonies if np.linalg.norm((c.x - x, c.y - y)) <= c.r + r]:
                x, y = random.random() * 500, random.random() * 500
            colony = Colony(x, y, r, [], color_colony=self.color_colonies[id_colony], id_colony=id_colony, markers_colors=markers_colors)

            for _ in range(n_ants_per_colony[id_colony]):
                ant = Ant(
                    unique_id=int(uuid.uuid1()),
                    model=self,
                    x=x + np.cos(random.random()*2*np.pi) * colony.r,
                    y=y + np.sin(random.random()*2*np.pi) * colony.r,
                    speed=speed,
                    colony=colony,
                    angle=random.random() * 2 * np.pi,
                    sight_distance=sight_distance,
                    color=self.color_ants[id_colony],
                )
                self.schedule.add(ant)
                colony.ants.append(ant)
      
            self.colonies.append(colony)
        
        model_reporters={}
        #     "Foods Picked": lambda model: model.colonies[0].food_picked,
        #     "Ants": lambda model: model.
        #     "Foods Picked": lambda model: len(model.foods),
        #     "Danger markers 0": lambda model: len(
        #         [m for m in model.markers_dict['0'] if m.purpose == MarkerPurpose.DANGER]
        #     ),
        #     "Food markers 0": lambda model: len(
        #         [m for m in model.markers_dict['0'] if m.purpose == MarkerPurpose.FOOD]
        #     ),
        # },
        
        model_reporters["Food picked 0"]=lambda model: model.colonies[0].food_picked
        model_reporters["Food picked 1"]=lambda model: model.colonies[1].food_picked
        
        # Automatisation j'arrive pas, en effet quand je décommande, les deux graphes affichent la même valeur.... (Davy)
        # Si quelqu'un a une idée je suis preneur
        #for i in range(n_colonies):
        #    model_reporters["Food picked " + str(i)]=lambda model: model.colonies[i].food_picked
        #    model_reporters["Ants " + str(_)]=lambda model: len(model.colonies[_].ants) 
        
        self.datacollector = DataCollector(
            model_reporters=model_reporters,
            agent_reporters={},
        )

    def step(self):
        self.schedule.step()
        for keys in self.markers_dict.keys():
            for mk in self.markers_dict[keys]:
                if mk.lifetime == 0:
                    self.markers_dict[keys].remove(mk)
                else :
                    mk.lifetime -= 1
        self.datacollector.collect(self)
        
        if not self.foods: #self.schedule.steps >= 100:
            self.running = False
