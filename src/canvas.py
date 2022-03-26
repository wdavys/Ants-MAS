from collections import defaultdict
from mesa.visualization.ModularVisualization import VisualizationElement


class ContinuousCanvas(VisualizationElement):
    local_includes = [
        "./js/simple_continuous_canvas.js",
    ]

    def __init__(self, canvas_height=500, canvas_width=500, instantiate=True):
        VisualizationElement.__init__(self)
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.identifier = "space-canvas"
        if instantiate:
            new_element = "new Simple_Continuous_Module({}, {},'{}')".format(
                self.canvas_width, self.canvas_height, self.identifier
            )
            self.js_code = "elements.push(" + new_element + ");"

    def portrayal_method(self, obj):
        return obj.portrayal_method()

    def render(self, model):
        representation = defaultdict(list)
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = (obj.x - model.space.x_min) / (
                    model.space.x_max - model.space.x_min
                )
                portrayal["y"] = (obj.y - model.space.y_min) / (
                    model.space.y_max - model.space.y_min
                )
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.foods:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = (obj.x - model.space.x_min) / (
                    model.space.x_max - model.space.x_min
                )
                portrayal["y"] = (obj.y - model.space.y_min) / (
                    model.space.y_max - model.space.y_min
                )
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.markers:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = (obj.x - model.space.x_min) / (
                    model.space.x_max - model.space.x_min
                )
                portrayal["y"] = (obj.y - model.space.y_min) / (
                    model.space.y_max - model.space.y_min
                )
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.obstacles:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = (obj.x - model.space.x_min) / (
                    model.space.x_max - model.space.x_min
                )
                portrayal["y"] = (obj.y - model.space.y_min) / (
                    model.space.y_max - model.space.y_min
                )
            representation[portrayal["Layer"]].append(portrayal)

        return representation
