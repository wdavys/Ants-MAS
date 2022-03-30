import random
import mesa
import argparse
import mesa.space
from mesa.batchrunner import BatchRunner
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer

from environnement import Ground
from canvas import ContinuousCanvas


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



def run_single_server():
    n_colonies = 2
    n_ants = [10, 5] # List of shape (n_colonies,)
    n_warriors = [3, 1] # List of shape (n_colonies,)
    epsilons = [.5, .7] # List of shape (n_colonies,)
    colonies_colors = []
    markers_colors = []
    series = []
    for i in range(n_colonies):
        colonies_colors.append("#"+''.join(random.choices('0123456789ABCDEF', k=6)))
        markers_colors.append(["#"+''.join(random.choices('0123456789ABCDEF', k=6)),
                              "#"+''.join(random.choices('0123456789ABCDEF', k=6))]) # element 0 for purpose FOOD and element 1 for DANGER
        series.append({"Label": "Ants " + str(i), "Color": markers_colors[i][0]})
        series.append({"Label": "Food picked " + str(i), "Color": colonies_colors[i]})
              
    chart = ChartModule(
        series,
        data_collector_name="datacollector",
    )
    
    model_params = {
        "n_colonies": n_colonies,
        "n_ants": n_ants,
        "n_warriors": n_warriors,
        "n_foods": mesa.visualization.ModularVisualization.UserSettableParameter(
            "slider", "Number of foods", 3, 1, 5, 1
        ),
        "n_obstacles": mesa.visualization.ModularVisualization.UserSettableParameter(
            "slider", "Number of obstacles", 5, 2, 10, 1
        ),
        "color_food": ["#EAEA08"],
        "color_colonies": colonies_colors,
        "epsilons": epsilons,
        "markers_colors": markers_colors,
        "speed": mesa.visualization.ModularVisualization.UserSettableParameter(
            "slider", "Ant speed", 15, 5, 40, 5
        ),
        "allow_danger_markers": True,
        "allow_info_markers": True
    }

    server = ModularServer(
        Ground,
        [ContinuousCanvas(), chart],
        "Ants colonies",
        model_params
    )
    server.port = 8521
    server.launch()


def run_batch():

    # ----- Analyse allow_smart_angle_chgt -----
    # fixed_params = {"n_colony":2,
    #                 "n_obstacles":5,
    #                 "n_quicksand":5,
    #                 "speed": 15,
    #                 "n_mines":15,
    #                 "allow_danger_markers":True,
    #                 "allow_info_markers":True}
    # variable_params = {"allow_smart_angle_chgt":[False]*50 + [True]*50 }

    # ----- Analyse allow_danger_markers -----
    # fixed_params = {"n_robots":8,
    #                 "n_obstacles":5,
    #                 "n_quicksand":10,
    #                 "speed": 15,
    #                 "n_mines":15,
    #                 "allow_smart_angle_chgt":False,
    #                 "allow_info_markers":True}
    # variable_params = {"allow_danger_markers":[False]*50 + [True]*50}

    # model_reporters = {"step in quicksands": lambda model:model.step_in_quicksands,
    #                 "step in quicksands/T": lambda model:model.step_in_quicksands/model.schedule.steps,
    #                 "time step": lambda model:model.schedule.steps}
    #
    # runner = BatchRunner(MinedZone,
    #                         variable_parameters=variable_params,
    #                         fixed_parameters=fixed_params,
    #                         model_reporters=model_reporters)
    #
    # runner.run_all()
    # df = runner.get_model_vars_dataframe()
    #
    # print(df)

    return


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-rb",
        "--run_batch",
        default=0,
        type=int,
        help="if 0 runs notebook in singular server mode, else runs notebook in batch mode (default: 0)",
    )
    args = parser.parse_args()

    if args.run_batch:
        run_batch()
    else:
        run_single_server()
