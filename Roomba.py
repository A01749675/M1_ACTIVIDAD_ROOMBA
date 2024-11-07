import mesa
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.colors as mcolors

class RoombaModel(mesa.Model):
    def __init__(self, N, width, height, dirty_cells, max_time):
        super().__init__()
        self.num_agents = N
        self.width = width
        self.height = height
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.dirty_cells = int((width * height) * dirty_cells)
        
        self.build_grid()
        self.dirty_grid()
        self.add_agents()
        
        self.cleaners = {f"Roomba {i}": 0 for i in range(N)}
        
        self.keep_cleaning = True
        self.time = max_time
        self.datacollector = mesa.DataCollector(
            model_reporters={"Steps": lambda m: m.schedule.steps,
                             "Cleaned": lambda m: m.count_cleaned_cells(),
                             "Movements": lambda m: m.total_movements()},
            
            agent_reporters={"Steps": "pos", "Cleaned": "cleaned", "Movements": "movements"},
        )
        
        
    def build_grid(self):
        for i in range(self.grid.width):
            for j in range(self.grid.height):
                a = Cell((i, j), self)
                self.grid.place_agent(a, (i, j))
                
    def total_movements(self):
        total_movements = 0
        for agent in self.schedule.agents:
            if "Roomba" in agent.who_am_i:
                total_movements += agent.movements
        return total_movements
    
    def dirty_grid(self):
        dirty_count = self.dirty_cells
        while dirty_count > 0:
            x = self.random.randrange(2, self.grid.width)
            y = self.random.randrange(2, self.grid.height)
            for agent in self.grid[x][y]:
                if agent.who_am_i == "Cell" and not agent.dirty:
                    dirty_count -= 1
                    agent.dirty = True

    def add_agents(self):
        for i in range(self.num_agents):
            a = RoombaAgent(i, self)
            self.schedule.add(a)
            self.grid.place_agent(a, (1, 1))
        
    def step(self):
        if self.time > 0 and self.keep_cleaning:
            self.schedule.step()
            self.count_cleaned_cells()

            self.datacollector.collect(self)
            self.time -= 1
        if self.dirty_cells == 0:
            self.keep_cleaning = False

    def count_cleaned_cells(self):
        return ((self.width * self.height) - self.dirty_cells)/(self.width * self.height)*100

class Cell(mesa.Agent):
    def __init__(self, unique_id, model, dirty=False):
        super().__init__(unique_id, model)
        self.who_am_i = "Cell"
        self.dirty = dirty

class RoombaAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.who_am_i = "Roomba " + str(unique_id)
        self.cleaned = 0
        self.movements = 0
        
    def move(self):
       possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
       new_position = self.random.choice(possible_steps)
       self.movements += 1
       self.model.grid.move_agent(self, new_position)
    
    def clean(self):
        current_cell = self.model.grid.get_cell_list_contents([self.pos])
        for agent in current_cell:
            if agent.who_am_i == "Cell" and agent.dirty:
                agent.dirty = False
                self.cleaned += 1
                self.model.dirty_cells -= 1
                return True
        return False

    def step(self):
        self.clean()
        self.move()

def update(frame, model, ax):
    model.step()
    ax.clear()
    
    if model.keep_cleaning:
    
    # Initialize a grid to store cell statuses for coloring
        agent_counts = np.zeros((model.grid.width, model.grid.height))
        
        for cell_content, (x, y) in model.grid.coord_iter():
            is_dirty = any(agent.who_am_i == "Cell" and agent.dirty for agent in cell_content)
            has_roomba = any("Roomba" in agent.who_am_i for agent in cell_content)
            
            if has_roomba:
                agent_counts[x][y] = 1  # Set 1 for Roomba
            elif is_dirty:
                agent_counts[x][y] = 0.5  # Set 0.5 for dirty cell
            else:
                agent_counts[x][y] = 0  # Set 0 for clean cell

        # Custom colormap: clean cells (0) as light yellow, dirty cells (0.5) as brown, Roomba cells (1) as blue
        cmap = mcolors.ListedColormap(["lightyellow", "brown", "blue"])
        bounds = [0, 0.25, 0.75, 1]  # Define boundaries for the custom color categories
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        # Plot the grid
        sns.heatmap(agent_counts, cmap=cmap, norm=norm, cbar=False, square=True, ax=ax, annot=False)
        ax.set_title("Grid Status: Yellow = Clean, Brown = Dirty, Blue = Roomba")

# In the main section, FuncAnimation remains the same
if __name__ == "__main__":
    model = RoombaModel(10, 20, 20, 0.3,1000)
    fig, ax = plt.subplots(figsize=(4, 4))
    
    anim = FuncAnimation(fig, update, fargs=(model, ax), frames=200, interval=200)
    plt.show()