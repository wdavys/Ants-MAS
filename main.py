import enum
import math
import random
import uuid
from enum import Enum
import matplotlib.pyplot as plt
import argparse
from mesa.batchrunner import BatchRunner

import mesa
import numpy as np
from collections import defaultdict

import mesa.space
from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import VisualizationElement, ModularServer
from mesa.visualization.modules import ChartModule

MAX_ITERATION = 100
PROBA_CHGT_ANGLE = 0.03

def move(x, y, speed, angle):
    return x + speed * math.cos(angle), y + speed * math.sin(angle)

def euclidean(p1, p2):
    return np.linalg.norm(p1.x-p2.x, p1.y-p2.y)

class MarkerPurpose(Enum):
    DANGER = enum.auto(),
    FOOD = enum.auto()


class ContinuousCanvas(VisualizationElement):
    local_includes = [
        "./js/simple_continuous_canvas.js",
    ]

    def __init__(self, canvas_height=500,
                 canvas_width=500, instantiate=True):
        VisualizationElement.__init__(self)
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.identifier = "space-canvas"
        if (instantiate):
            new_element = ("new Simple_Continuous_Module({}, {},'{}')".
                           format(self.canvas_width, self.canvas_height, self.identifier))
            self.js_code = "elements.push(" + new_element + ");"

    def portrayal_method(self, obj):
        return obj.portrayal_method()

    def render(self, model):
        representation = defaultdict(list)
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.foods:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.markers:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.obstacles:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)

        return representation


class Obstacle:  # Environnement: obstacle infranchissable
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "black",
                     "r": self.r}
        return portrayal


class Food:
    def __init__(self, x, y, r, weight):
        self.x = x
        self.y = y
        self.r = r
        self.n = weight

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "olive",
                     "r": self.r*self.weight}
        return portrayal

    def get_one_piece(self):
        self.weight -= 1


class Marker:  # La classe pour les balises
    def __init__(self, x, y, purpose, directions):
        self.x = x
        self.y = y
        self.purpose = purpose
        if purpose == MarkerPurpose.FOOD:
            self.directions = directions

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 2,
                     "Color": "red" if self.purpose == MarkerPurpose.DANGER else "green",
                     "r": 2}
        return portrayal


class Colony:
    def __init__(self, x, y, r, ants):
        self.x = x
        self.y = y
        self.r = r
        self.ants = ants


class Ant(Agent):
    def __init__(self, unique_id: int, model: Model, x, y, speed, angle,
                    sight_distance)
        super().__init__(unique_id, model)
        self.x = x
        self.y = y
        self.speed = speed
        self.sight_distance = sight_distance
        self.angle = angle
        self.is_carrying = False
        self.is_on_food_marker = False

    def next_pos(self):
        next_x = self.x + self.speed * math.cos(self.angle)
        next_y = self.y + self.speed * math.sin(self.angle)
        return next_x, next_y

    def go_to(self, destination):
        x = self.x
        y = self.y
        speed = self.speed
        dist_to_destination = euclidean(self, destination)

        if dist_to_destination < speed:
            return (dest_x, dest_y), 2 * math.pi * random.random()
        else:
            angle = math.acos((dest_x - x)/dist_to_destination)
            if dest_y < y:
                angle = - angle
            return self.next_pos(), angle


    def step(self):

        foods = [food for food in self.model.foods if euclidean(food, self)<self.sight_distance]
        food_markers = [marker for marker in self.model.markers if marker.purpose == MarkerPurpose.FOOD]
        if foods:
            nearest_food = food[np.argmin([euclidean(self, food) for food in foods])]
            next_x, next_y, angle = self.go_to(nearest_food)
        elif food_markers:
            nearest_food_marker = food_markers[np.argmin([euclidean(self, marker) for marker in food_markers])]
            next_x, next_y = nearest_food_marker.x, nearest_food_marker.y
            self.is_on_food_marker = True


        self.x, self.y = next_x, next_y

        self.x, self.y = self.next_pos()

        if random.random() < PROBA_CHGT_ANGLE:
            self.angle = random.random()*2*np.pi


    def portrayal_method(self):
        portrayal = {"Shape": "arrowHead", "s": 1, "Filled": "true", "Color": "Red", "Layer": 3, 'x': self.x,
                     'y': self.y, "angle": self.angle}
        return portrayal



# class Robot(Agent):  # La classe des agents
#     def __init__(self, unique_id: int, model: Model, x, y, speed, sight_distance,
#                         allow_smart_angle_chgt, allow_danger_markers, allow_info_markers,
#                         angle=0.0, chgt_angle_step=0.01, maxiter_chgt_angle=2000, knn=2):
#         super().__init__(unique_id, model)
#         self.x = x
#         self.y = y
#         self.speed = speed
#         self.quicksand_speed = speed/2
#         self.sight_distance = sight_distance
#         self.angle = angle
#         self.counter = 0
#         self.chgt_angle_step = chgt_angle_step
#         self.maxiter_chgt_angle=maxiter_chgt_angle
#         self.knn = knn
#         self.allow_smart_angle_chgt = allow_smart_angle_chgt
#         self.allow_danger_markers = allow_danger_markers
#         self.allow_info_markers = allow_info_markers
#
#     def next_pos(self):
#         next_x = self.x + self.speed * math.cos(self.angle)
#         next_y = self.y + self.speed * math.sin(self.angle)
#         return next_x, next_y
#
#     def go_to(self, dest_x, dest_y):
#         x = self.x
#         y = self.y
#         speed = self.speed
#
#         if np.linalg.norm((x - dest_x, y - dest_y)) < speed:
#             return (dest_x, dest_y), 2 * math.pi * random.random()
#         else:
#             angle = math.acos((dest_x - x)/np.linalg.norm((x - dest_x, y - dest_y)))
#             if dest_y < y:
#                 angle = - angle
#             return move(x, y, speed, angle), angle
#
#     def will_crash_with(self, object):
#         '''
#             Check if the agent will crash with the object.
#             object can be either an obstacle or another robot.
#         '''
#         x_0, y_0 = self.x, self.y
#         x_f, y_f = move(x_0, y_0, self.speed, self.angle)
#         x_c, y_c = object.x, object.y
#         p0 = np.array([x_0, y_0])
#         pf = np.array([x_f, y_f])
#         pc = np.array([x_c, y_c])
#         p0pf = pf - p0
#         p0pc = pc - p0
#         norm_p0pf = euclidean(p0, pf)
#         norm_p0pc = euclidean(p0, pc)
#         prod = p0pf.dot(p0pc)
#         norm_p0ph = abs(prod/norm_p0pf)
#         radius = object.speed if object.__class__.__name__=='Robot' else object.r
#
#         if norm_p0ph>norm_p0pf:
#             dist = euclidean(pf, pc)
#         elif prod<0 :
#             dist=np.inf
#         #     dist = euclidean(p0, pc)
#         else:
#             dist = np.sqrt(norm_p0pc**2 - norm_p0ph**2)
#
#         return dist<=radius
#
#
#
#     def will_crash_at_least_once(self, objects):
#         '''
#             Check if the agent will have a crash with an object in objects
#         '''
#
#         for obj in objects:
#             at_least_1_crash = self.will_crash_with(obj)
#             if at_least_1_crash:
#                 return True
#         return False
#
#
#     def step(self):
#         self.counter+=1
#
#         ########################################
#         ############## Priorité 0 ##############
#         ########################################
#
#         # --- Changement aléatoire d'angle --- #
#         if np.random.random()<PROBA_CHGT_ANGLE:
#             if self.allow_smart_angle_chgt:
#                 # Utilisation du changement d'angle intelligent (question bonus)
#                 # Récupération des k plus proches voisins (kppv)
#                 all_robots = [robot for robot in self.model.schedule.agents if robot!=self]
#                 distances = [euclidean((robot.x, robot.y), (self.x, self.y)) for robot in all_robots]
#                 idx_knn = np.argpartition(distances, self.knn)[:self.knn]
#                 knn = [all_robots[idx] for idx in idx_knn]
#
#                 # Calcul de la direction moyenne aux kppv
#                 directions_to_knn = np.array([[robot.x - self.x, robot.y - self.y] for robot in knn])
#                 norm_to_knn = np.sqrt(np.sum(directions_to_knn**2, axis=1))[:, np.newaxis]
#                 normalized_directions_to_knn = directions_to_knn/norm_to_knn
#                 mean_direction_to_knn = np.mean(normalized_directions_to_knn, axis=0)
#
#                 # Direction opposée à la direction moyenne aux kppv
#                 opposite_direction = -1 * mean_direction_to_knn
#
#                 if opposite_direction.any():
#                     # Si la direction moyenne est non nulle
#                     # on va dans la direction opposée à la direction moyenne
#                     self.angle = math.atan2(opposite_direction[1], opposite_direction[0])
#                 else:
#                     # Sinon, les ppv sont également répartis autour du robot
#                     # on va dans la direction au milieu de deux des kppvs.
#                     direction_to_first_knn = normalized_directions_to_knn[0]
#                     angle_first_knn = math.atan2(direction_to_first_knn[1], direction_to_first_knn[0])
#                     pm = np.random.randint(2)*2-1
#                     self.angle = angle_first_knn + pm * np.pi/self.knn
#
#             else :
#                 # Si pas d'utilisation du changement d'angle intelligent
#                 # changement d'angle aléatoire
#                 self.angle = np.random.random()*2*np.pi
#
#
#         # --- Gestion des sables mouvants --- #
#         in_quicksand = [euclidean((self.x, self.y), (sand.x, sand.y))<sand.r
#                                 for sand in self.model.quicksands]
#
#         # Ralentissement et pose de balises
#         initial_speed = self.speed
#         self.speed = self.quicksand_speed if sum(in_quicksand) else self.quicksand_speed*2
#         if self.speed>initial_speed and self.allow_danger_markers:
#             self.model.markers.append(Marker(self.x, self.y, MarkerPurpose.DANGER))
#             self.counter = 0
#
#         # Détection des balises danger
#         danger_markers = [marker for marker in self.model.markers
#             if euclidean((marker.x, marker.y), (self.x, self.y))<self.sight_distance
#             and marker.purpose==MarkerPurpose.DANGER]
#         if len(danger_markers) and self.counter>self.speed/2 and self.speed!=self.quicksand_speed:
#             self.angle -= np.pi
#             self.counter = 0
#             # Remise à 0 du compteur ici pour éviter qu'un agent ne reste bloqué
#             # par une balise qui vient d'être posée par un autre agent à proximité
#             # Mais implique une diminution du temps de réaction des agents
#
#
#         # --- Gestion des balises d'information --- #
#         indic_markers = [marker for marker in self.model.markers
#             if euclidean((marker.x, marker.y), (self.x, self.y))<self.sight_distance
#             and marker.purpose==MarkerPurpose.FOOD]
#
#         # Priorité inférieure aux balises sable mouvants, on n'entre pas dans
#         # cette boucle si une balise sable mouvant vient d'être détectéé
#         if len(indic_markers) and self.counter>self.speed/2 and self.speed!=self.quicksand_speed:
#             first_marker = indic_markers[0] # => CONSIDERER LE MARKER LE PLUS PROCHE PLUTOT ?
#             pm = np.random.randint(2)*2-1 # signe aléatoire
#             self.angle = first_marker.direction + pm*np.pi/2
#             self.counter = 0
#
#
#         ############################################################
#         ############## Priorité 1 : Gestion des mines ##############
#         ############################################################
#
#         mines = [mine for mine in self.model.mines
#                         if euclidean((mine.x, mine.y), (self.x, self.y))<self.sight_distance]
#
#         # Détection et direction vers les mines
#         if len(mines):
#             first_mine = mines[0] ## => CONSIDERER LA MINE LA PLUS PROCHE PLUTOT ?
#             _, angle = self.go_to(first_mine.x, first_mine.y)
#             self.angle=angle
#
#         # Désamorçage, pose de balise information
#         for mine in mines:
#             if euclidean((mine.x, mine.y), (self.x, self.y))<mine.r:
#                 mines.remove(mine)
#                 self.model.mines.remove(mine)
#                 if self.allow_info_markers:
#                     self.model.markers.append(Marker(self.x, self.y,
#                                                         MarkerPurpose.FOOD, self.angle))
#                     self.counter = 0
#
#
#         #################################################################
#         ############## Priorité 2 : Gestion de l'évitement ##############
#         #################################################################
#
#         robots = [robot for robot in self.model.schedule.agents if self!=robot
#                             and euclidean((robot.x, robot.y), (self.x, self.y))<self.sight_distance]
#         obstacles = [obstacle for obstacle in self.model.obstacles
#                         if euclidean((obstacle.x, obstacle.y), (self.x, self.y))<self.sight_distance]
#
#
#         next_x, next_y = self.next_pos()
#         crash_at_least_once = self.model.space.out_of_bounds((next_x, next_y))
#         if not crash_at_least_once:
#             crash_at_least_once = self.will_crash_at_least_once(robots)
#         if not crash_at_least_once:
#             crash_at_least_once = self.will_crash_at_least_once(obstacles)
#
#         iter = 0
#         max_iter = self.maxiter_chgt_angle
#         initial_angle = self.angle
#         while crash_at_least_once and iter<max_iter:
#             # ---- Priorité 2.1 ----
#             # On essaie de trouver un angle qui permette d'éviter le crash contre
#             # un autre agent et contre un obstacle
#             if iter%2:
#                 self.angle = initial_angle + (iter//2+1)*self.chgt_angle_step
#             else:
#                 self.angle = initial_angle - (iter//2+1)*self.chgt_angle_step
#             next_x, next_y = self.next_pos()
#             crash_at_least_once = self.model.space.out_of_bounds((next_x, next_y))
#             if not crash_at_least_once:
#                 crash_at_least_once = self.will_crash_at_least_once(robots)
#             if not crash_at_least_once:
#                 crash_at_least_once = self.will_crash_at_least_once(obstacles)
#             iter += 1
#
#
#         if crash_at_least_once :
#             # Aucun angle ne permettant d'éviter le crash contre un autre agent
#             # et contre un obstacle a été trouvé
#             iter = 0
#             while crash_at_least_once and iter<max_iter:
#                 # ---- Priorité 2.2 ----
#                 # On essaie au moins de trouver un angle qui permette d'éviter
#                 # le crash contre un autre agent (tant pis pour le crash avec un obstacle)
#                 if iter%2:
#                     self.angle = initial_angle + (iter//2+1)*self.chgt_angle_step
#                 else:
#                     self.angle = initial_angle - (iter//2+1)*self.chgt_angle_step
#
#                 crash_at_least_once = self.will_crash_at_least_once(robots)
#                 iter += 1
#
#
#         if crash_at_least_once :
#             # Aucun angle ne permettant d'éviter un crash n'a été trouvé,
#             # on maintient l'angle initial et on espère qu'il n'y aura pas de crash
#
#             # => Destruction des robots en cas de crash ?
#             self.angle = initial_angle
#
#         self.x, self.y = self.next_pos()
#
#         pass
#
#     def portrayal_method(self):
#         portrayal = {"Shape": "arrowHead", "s": 1, "Filled": "true", "Color": "Red", "Layer": 3, 'x': self.x,
#                      'y': self.y, "angle": self.angle}
#         return portrayal


class MinedZone(Model):
    collector = DataCollector(
        model_reporters={"Mines": lambda model: len(model.mines),
                         "Danger markers": lambda model: len([m for m in model.markers if
                                                          m.purpose == MarkerPurpose.DANGER]),
                         "FOOD markers": lambda model: len([m for m in model.markers if
                                                          m.purpose == MarkerPurpose.FOOD]),
                         "Steps in quicksand": lambda model: model.step_in_quicksands},
        agent_reporters={})

    def __init__(self, n_robots, n_obstacles, n_quicksand, n_mines, speed,
                    allow_info_markers=True, allow_danger_markers=True, allow_smart_angle_chgt=True):
        Model.__init__(self)
        self.space = mesa.space.ContinuousSpace(600, 600, False)
        self.schedule = RandomActivation(self)
        self.mines = []  # Access list of mines from robot through self.model.mines
        self.markers = []  # Access list of markers from robot through self.model.markers (both read and write)
        self.obstacles = []  # Access list of obstacles from robot through self.model.obstacles
        self.quicksands = []  # Access list of quicksands from robot through self.model.quicksands
        for _ in range(n_obstacles):
            self.obstacles.append(Obstacle(random.random() * 500, random.random() * 500, 10 + 20 * random.random()))
        for _ in range(n_robots):
            x, y = random.random() * 500, random.random() * 500
            while [o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r] or \
                    [o for o in self.quicksands if np.linalg.norm((o.x - x, o.y - y)) < o.r]:
                x, y = random.random() * 500, random.random() * 500
            self.schedule.add(
                Robot(int(uuid.uuid1()), self, x, y, speed, 2 * speed,
                        allow_smart_angle_chgt, allow_danger_markers, allow_info_markers,
                        random.random() * 2 * math.pi))
        for _ in range(n_mines):
            x, y = random.random() * 500, random.random() * 500
            while [o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r] or \
                    [o for o in self.quicksands if np.linalg.norm((o.x - x, o.y - y)) < o.r]:
                x, y = random.random() * 500, random.random() * 500
            self.mines.append(Mine(x, y))
        self.datacollector = self.collector
        # self.t = 0
        self.step_in_quicksands=0

    def step(self):
        # self.t += 1
        self.datacollector.collect(self)
        self.schedule.step()
        if not self.mines:
            self.running = False

        self.step_in_quicksands += len([robot for robot in self.schedule.agents
                                            if robot.speed == robot.quicksand_speed])



def run_single_server():
    chart = ChartModule([{"Label": "Mines",
                          "Color": "Orange"},
                         {"Label": "Danger markers",
                          "Color": "Red"},
                         {"Label": "FOOD markers",
                          "Color": "Green"},
                          {"Label": "Steps in quicksand",
                          "Color": "Black"}
                         ],
                        data_collector_name='datacollector')
    server = ModularServer(MinedZone,
                           [ContinuousCanvas(),
                            chart],
                           "Deminer robots",
                           {"n_robots": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of robots", 7, 3,
                                                                       15, 1),
                            "n_obstacles": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of obstacles", 5, 2, 10, 1),
                            "n_quicksand": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of quicksand", 5, 2, 10, 1),
                            "speed": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Robot speed", 15, 5, 40, 5),
                            "n_mines": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of mines", 15, 5, 30, 1),
                            "allow_danger_markers": True,
                            "allow_info_markers": True,
                            "allow_smart_angle_chgt": True})
    server.port = 8521
    server.launch()


def run_batch():

    # ----- Analyse allow_smart_angle_chgt -----
    fixed_params = {"n_robots":8,
                    "n_obstacles":5,
                    "n_quicksand":5,
                    "speed": 15,
                    "n_mines":15,
                    "allow_danger_markers":True,
                    "allow_info_markers":True}
    variable_params = {"allow_smart_angle_chgt":[False]*50 + [True]*50 }


    # ----- Analyse allow_danger_markers -----
    # fixed_params = {"n_robots":8,
    #                 "n_obstacles":5,
    #                 "n_quicksand":10,
    #                 "speed": 15,
    #                 "n_mines":15,
    #                 "allow_smart_angle_chgt":False,
    #                 "allow_info_markers":True}
    # variable_params = {"allow_danger_markers":[False]*50 + [True]*50}



    model_reporters = {"step in quicksands": lambda model:model.step_in_quicksands,
                    "step in quicksands/T": lambda model:model.step_in_quicksands/model.schedule.steps,
                    "time step": lambda model:model.schedule.steps}

    runner = BatchRunner(MinedZone,
                            variable_parameters=variable_params,
                            fixed_parameters=fixed_params,
                            model_reporters=model_reporters)

    runner.run_all()
    df = runner.get_model_vars_dataframe()

    print(df)

    print(df['time step'].mean())
    print(df['time step'].std())

    # ----- Analyse allow_smart_angle_chgt -----
    mask = df['allow_smart_angle_chgt']
    time_step_with_smart_angle_chgt = df[mask]['time step']
    time_step_without_smart_angle_chgt = df[~mask]['time step']
    print(time_step_with_smart_angle_chgt.mean())
    print(time_step_without_smart_angle_chgt.mean())

    # ----- Analyse allow_danger_markers -----
    # mask = df['allow_danger_markers']
    # time_step_with_smart_angle_chgt = df[mask]['step in quicksands/T']
    # time_step_without_smart_angle_chgt = df[~mask]['step in quicksands/T']
    # print(time_step_with_smart_angle_chgt.mean())
    # print(time_step_without_smart_angle_chgt.mean())

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-rb', '--run_batch', default=0, type=int,
    help='if 0 runs notebook in singular server mode, else runs notebook in batch mode (default: 0)')
    args = parser.parse_args()

    if args.run_batch:
        run_batch()
    else:
        run_single_server()