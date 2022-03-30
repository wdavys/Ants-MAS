import random
import mesa
import argparse
import mesa.space
from mesa.batchrunner import BatchRunner
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer

from environnement import Ground
from canvas import ContinuousCanvas


def run_single_server():
    n_colonies = 2
    n_ants = [10, 7] # List of shape (n_colonies,)
    n_warriors = [3, 4] # List of shape (n_colonies,)
    epsilons = [.5, .3] # List of shape (n_colonies,)
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
