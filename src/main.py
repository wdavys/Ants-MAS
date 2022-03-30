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
        "epsilons": epsilons,
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
    series = []
    model_reporters={}
    for i in range(2):
        series.append({"Label": "Ants " + str(i), "Color": "black"})
        series.append({"Label": "Food picked " + str(i), "Color": "black"})
        
        model_reporters["Food picked " +str(i)]=eval("lambda model: model.colonies["+str(i)+"].food_picked")
        model_reporters["Ants " + str(i)]=eval("lambda model: len(model.colonies["+str(i)+"].ants)") 
    
    batchrunner = BatchRunner(
        model_cls = Ground,
        variable_parameters={
            "n_colonies": (2,),
            "n_ants": ((10,10),),
            "n_warriors": tuple((i,0) for i in range(10)),
            "n_foods": (3,),
            "n_obstacles": (5,),
            "color_food": ("#EAEA08",),
            "epsilons": ((.5, .5),),
            "speed": (20,),
            "allow_danger_markers": (True,),
            "allow_info_markers": (True,)
        },
        model_reporters=model_reporters
    )
    batchrunner.run_all()
    df = batchrunner.get_model_vars_dataframe()
    return df


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-rb",
        "--run_batch",
        default=0,
        type=int,
        help="if 0 runs notebook in singular server mode, else runs notebook in batch mode (default: 0)",
    )
    parser.add_argument(
        "-n",
        "--name",
        default="exp.csv",
        type=str,
        help="name of the result dataframe"
    )
    args = parser.parse_args()

    if args.run_batch:
        df = run_batch()
        df.to_csv(args.name)
    else:
        run_single_server()
