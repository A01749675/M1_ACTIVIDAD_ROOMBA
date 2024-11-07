from mesa.visualization.modules import ChartModule,BarChartModule
from Roomba import *
import mesa
import random


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                    "Filled": "true",
                    "Layer": 0,
                    "r": 0.5}
    if isinstance(agent, RoombaAgent):
        portrayal["Color"] = "red"
    if isinstance(agent, Cell):
        if agent.dirty:
            portrayal["Color"] = "brown"
        else:
            portrayal["Color"] = "yellow"
    return portrayal

def diceSize():
    return random.randint(3, 12)

x = diceSize()
y = diceSize()

grid = mesa.visualization.CanvasGrid(agent_portrayal, x, y, 500, 500)
steps = ChartModule([{ "Label": "Steps", "Color": "Black" }], data_collector_name = 'datacollector')
cleaned = ChartModule([{ "Label": "Cleaned", "Color": "Black" }], data_collector_name = 'datacollector')
movements = ChartModule([{ "Label": "Movements", "Color": "Black" }], data_collector_name = 'datacollector')
server = mesa.visualization.ModularServer(
    RoombaModel,
    [grid, steps,cleaned,movements],
    "Roombas",
    {"N": random.randint(1, 20),
     "width": x,
     "height": y,
     "dirty_cells": random.uniform(0.1, 0.5),
     "max_time": 100000}
)

server.port = 8080
server.launch()