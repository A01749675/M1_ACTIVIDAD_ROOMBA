# Roomba Cleaning Simulation. 

#Este código simula la limpieza de un grid por parte de varios agentes Roomba, siendo instanciados dentro de
#un modelo principal. Los agentes Roomba se mueven y limpian celdas sucias, y el modelo lleva el registro de los
#datos importantes como el porcentaje de celdas limpias, el tiempo de ejecución, y los pasos requeridos para completar

# Autor: Carlos Iker Fuentes Reyes A01749675 && Santiago Chevez Trejo A01749887
# Fecha de creación: 7/11/2024

import mesa
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.colors as mcolors

class RoombaModel(mesa.Model):
    """Clase principal del modelo Roomba que controla la simulación,
    el modelo lleva el registro de los datos importantes como el porcentaje de
    celdas limpias, el tiempo de ejecución, y 
    los pasos requeridos para completar la simulación"""
    
    def __init__(self, numAgents, width, height, dirtyCellsRatio, maxTime):
        """Inicializa el modelo Roomba y asigna los parámetros iniciales.
            Args:
                numAgents (int): Número de agentes Roomba en el modelo.
                width (int): Ancho del grid del modelo.
                height (int): Alto del grid del modelo.
                dirtyCellsRatio (float): Proporción de celdas sucias al inicio de la simulación.
                maxTime (int): Número máximo de pasos a ejecutar en la simulación."""
               
        super().__init__()
        self.numAgents = numAgents
        self.width = width
        self.height = height
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.dirtyCells = int((width * height) * dirtyCellsRatio)
        
        self.buildGrid()
        self.dirtyGrid()
        self.addAgents()
        
        self.cleaners = {f"Roomba {i}": 0 for i in range(numAgents)}
        
        self.keepCleaning = True
        self.timeRemaining = maxTime
        self.limitTime = maxTime
        
        self.dataCollector = mesa.DataCollector(
            model_reporters={
                "Steps": lambda model: model.schedule.steps,
                "CleanedPercentage": lambda model: model.calculateCleanedPercentage(),
                "TotalMovements": lambda model: model.calculateTotalMovements(),
                "TimeTaken": lambda model: model.calculateTimeTaken()
            },
            agent_reporters={"Position": "pos", "Cleaned": "cleaned", "Movements": "movements"}
        )
    
    def buildGrid(self):
        """Construye el grid inicial del modelo con celdas limpias."""
        for i in range(self.grid.width):
            for j in range(self.grid.height):
                cell = Cell((i, j), self)
                self.grid.place_agent(cell, (i, j))
                
    def calculateTotalMovements(self):
        """Calcula el total de movimientos realizados por todos los agentes Roomba.
            return: 
                (int) Número total de movimientos."""
        return sum(agent.movements for agent in self.schedule.agents if "Roomba" in agent.whoAmI)
    
    def dirtyGrid(self):
        """Ensucia un porcentaje de celdas al azar al inicio de la simulación."""
        dirtyCount = self.dirtyCells
        while dirtyCount > 0:
            x = self.random.randrange(2, self.grid.width)
            y = self.random.randrange(2, self.grid.height)
            for agent in self.grid[x][y]:
                if agent.whoAmI == "Cell" and not agent.dirty:
                    dirtyCount -= 1
                    agent.dirty = True

    def addAgents(self):
        """Añade agentes Roomba al grid y al scheduler del modelo."""
        for i in range(self.numAgents):
            roomba = RoombaAgent(i, self)
            self.schedule.add(roomba)
            self.grid.place_agent(roomba, (1, 1))
        
    def step(self):
        """Ejecuta un paso del modelo, incluyendo limpieza y recolección de datos."""
        if self.timeRemaining > 0 and self.keepCleaning:
            self.schedule.step()
            self.calculateCleanedPercentage()
            self.dataCollector.collect(self)
            self.timeRemaining -= 1
        
        if self.dirtyCells == 0:
            self.keepCleaning = False

    def calculateCleanedPercentage(self):
        """Calcula el porcentaje de celdas que han sido limpiadas.
            return: 
                (int) Porcentaje de celdas limpias en un rango de 0--100"""
        return ((self.width * self.height) - self.dirtyCells) / (self.width * self.height) * 100
    def calculateTimeTaken(self):
        """Calcula el tiempo que ha tomado limpiar todas las celdas.
            return
                (int) Tiempo total en pasos de simulación."""
        return self.limitTime - self.timeRemaining

class Cell(mesa.Agent):
    """Clase que representa cada celda del grid."""
    
    def __init__(self, uniqueId, model, dirty=False):
        '''
        Inicializa una celda en el grid.
        uniqueId: valor único para la celda.
        model: referencia al modelo principal.
        dirty: indica si la celda está sucia o no, inicialmente False.'''
        
        super().__init__(uniqueId, model)
        self.whoAmI = "Cell"
        self.dirty = dirty

class RoombaAgent(mesa.Agent):
    """Clase que representa un agente Roomba, que se mueve y limpia celdas."""
    
    def __init__(self, uniqueId, model):
        """Inicializa un agente Roomba en el grid.
            uniqueId: valor único para el agente.
            model: referencia al modelo principal."""
            
        super().__init__(uniqueId, model)
        self.whoAmI = f"Roomba {uniqueId}"
        self.cleaned = 0
        self.movements = 0
        
    def move(self):
        """Realiza el movimiento del agente Roomba a una celda adyacente."""
        possibleSteps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        newPosition = self.random.choice(possibleSteps)
        self.movements += 1
        self.model.grid.move_agent(self, newPosition)
    
    def clean(self):
        """Limpia la celda actual si está sucia.
            return: True si la celda fue limpiada, False si no."""
        currentCell = self.model.grid.get_cell_list_contents([self.pos])
        for agent in currentCell:
            if agent.whoAmI == "Cell" and agent.dirty:
                agent.dirty = False
                self.cleaned += 1
                self.model.dirtyCells -= 1
                return True
        return False

    def step(self):
        """Realiza un paso de limpieza y movimiento del agente.
            Si no puede limpiar, se mueve a una celda adyacente."""
        if not self.clean():
            self.move()

def update(frame, model, ax):
    """Función de actualización para animar el modelo Roomba."""
    model.step()
    ax.clear()
    
    if model.keepCleaning:
        agentCounts = np.zeros((model.grid.width, model.grid.height))
        
        for cell_content, (x, y) in model.grid.coord_iter():
            isDirty = any(agent.whoAmI == "Cell" and agent.dirty for agent in cell_content)
            hasRoomba = any("Roomba" in agent.whoAmI for agent in cell_content)
            
            if hasRoomba:
                agentCounts[x][y] = 1  # 1 para Roomba
            elif isDirty:
                agentCounts[x][y] = 0.5  # 0.5 para celdas sucias
            else:
                agentCounts[x][y] = 0  # 0 para celdas limpias

        cmap = mcolors.ListedColormap(["lightyellow", "brown", "blue"])
        bounds = [0, 0.25, 0.75, 1]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        sns.heatmap(agentCounts, cmap=cmap, norm=norm, cbar=False, square=True, ax=ax, annot=False)
        ax.set_title("Estado del Grid: Amarillo = Limpio, Marrón = Sucio, Azul = Roomba")

if __name__ == "__main__":
    model = RoombaModel(10, 20, 20, 0.3, 1000)
    fig, ax = plt.subplots(figsize=(4, 4))
    
    anim = FuncAnimation(fig, update, fargs=(model, ax), frames=200, interval=200)
    plt.show()
