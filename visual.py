# Roomba Cleaning Simulation. 

#Este código es la representacón gráfica del modelo simulado en la lase Rooomba.py
#Despliega la simulación en una interfaz gráfica para una mejor visualización de la simulación, ésta corre en un servidor local,
#muestra un grid con celdas sucias y limpias, y agentes Roomba que se mueven y limpian las celdas sucias.
#Además, muestra gráficas en tiempo real de los datos importantes como el porcentaje de celdas limpias, el tiempo de ejecución,
# y los pasos requeridos para completar la simulación

# Autor: Carlos Iker Fuentes Reyes A01749675 && Santiago Chevez Trejo A01749887
# Fecha de creación: 7/11/2024


from mesa.visualization.modules import ChartModule,BarChartModule
from Roomba import *
import mesa
import random


def agentPortrayal(agent):
    """
    Instancia un agente Roomba y lo representa en la interfaz gráfica.

    Args:
        agent (Agent): un agente que puede ser de tipo RoombaAgent o Cell.

    Returns:
        dict: diccionario con las propiedades del agente.
    """
    portrayal = {"Shape": "",
                    "Filled": "true",
                    "Layer": 0,
                    "w": 1.0,
                    "h": 1.0}
    
    if isinstance(agent, RoombaAgent):
        portrayal["Shape"] = "roomba.jpg"
        portrayal["Color"] = "red"
    if isinstance(agent, Cell):
        if agent.dirty:
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "brown"
        else:
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "green"
    return portrayal

def generateRandomGridSize():
    """
    Genera un tamaño aleatorio para el grid.

    Returns:
        tuple: regresa una tupla con dos valores enteros 
                aleatorios para el ancho y alto del grid.
    """
    return (random.randint(3, 12),random.randint(3, 12))

def generateRandomAgents():
    """
    Genera un número aleatorio de agentes Roomba.

    Returns:
        int: número entero aleatorio de agentes Roomba.
    """
    return random.randint(1, 20)

width , height = generateRandomGridSize()


grid = mesa.visualization.CanvasGrid(agentPortrayal, width, height, 500, 500)

stepsSimuated = ChartModule([{ "Label": "Steps", "Color": "Black" }], data_collector_name = 'dataCollector')
cleanedPercentage = ChartModule([{ "Label": "CleanedPercentage", "Color": "Black" }], data_collector_name = 'dataCollector')
movementsByAllAgents = ChartModule([{ "Label": "TotalMovements", "Color": "Black" }], data_collector_name = 'dataCollector')
timeTaken = ChartModule([{ "Label": "TimeTaken", "Color": "Black" }], data_collector_name = 'dataCollector')



server = mesa.visualization.ModularServer(
    RoombaModel,
    [grid, stepsSimuated,cleanedPercentage,movementsByAllAgents,timeTaken],
    "Roombas, by Carlos Iker Fuentes Reyes|Santiago Chevez Trejo",
    {"numAgents": random.randint(1, 20),
     "width": width,
     "height": height,
     "dirtyCellsRatio": random.uniform(0.1, 0.5),
     "maxTime": 100000}
)

server.port = 8080
server.launch()