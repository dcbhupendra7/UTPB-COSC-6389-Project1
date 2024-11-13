import math
import random
import tkinter as tk
from tkinter import Menu, FALSE, Canvas

# Configuration parameters
num_cities = 25  # Number of cities to visit in the Traveling Salesman Problem
city_scale = 5  # Scale for drawing city nodes
road_width = 2  # Width of roads (edges) in the UI
padding = 50  # Padding for the canvas

class Node:
    def __init__(self, x, y, index):
        self.x = x
        self.y = y
        self.index = index  # Unique identifier for the city

    def draw(self, canvas, color='yellow'):
        # Draw the city node as a circle on the canvas
        canvas.create_oval(
            self.x - city_scale * 2, self.y - city_scale * 2,
            self.x + city_scale * 2, self.y + city_scale * 2,
            fill=color, outline='black'
        )
        # Draw the city index number next to the city node
        canvas.create_text(
            self.x, self.y - city_scale * 3,
            text=str(self.index),
            font=('Arial', 12),
            fill='blue'
        )


class Edge:
    def __init__(self, a, b):
        self.city_a = a  # Starting city of the edge
        self.city_b = b  # Ending city of the edge
        # Calculate the Euclidean distance between the two cities
        self.length = math.hypot(a.x - b.x, a.y - b.y)

    def draw(self, canvas, color='grey', style=None):
        # Draw the edge (road) connecting two cities on the canvas
        kwargs = {'fill': color, 'width': road_width}
        if style:
            kwargs['dash'] = style
        canvas.create_line(
            self.city_a.x, self.city_a.y,
            self.city_b.x, self.city_b.y,
            **kwargs
        )

class TSP_Solver:
    def __init__(self, cities):
        self.cities = cities
        self.num_cities = len(cities)
        # Precompute the distances between every pair of cities
        self.distance_matrix = self.calculate_distance_matrix()
        # Generate an initial solution using the greedy approach
        self.current_solution = self.greedy_initial_solution()
        self.best_solution = self.current_solution[:]
        # Calculate the distance of the initial solution
        self.best_distance = self.calculate_total_distance(self.best_solution)
        self.temperature = 10000  # Initial temperature for simulated annealing
        self.cooling_rate = 0.999  # Cooling rate to control the annealing process
        self.original_distance = self.best_distance  # Store the original distance of the initial solution

    def calculate_distance_matrix(self):
        # Create a matrix to store distances between each pair of cities
        matrix = [[0]*self.num_cities for _ in range(self.num_cities)]
        for i in range(self.num_cities):
            for j in range(i+1, self.num_cities):
                dist = math.hypot(
                    self.cities[i].x - self.cities[j].x,
                    self.cities[i].y - self.cities[j].y
                )
                matrix[i][j] = dist
                matrix[j][i] = dist
        return matrix

    def calculate_total_distance(self, solution):
        # Calculate the total distance of the given solution (route)
        distance = 0
        for i in range(len(solution)):
            a = solution[i]
            b = solution[(i + 1) % len(solution)]  # Wrap around to the starting city
            distance += self.distance_matrix[a][b]
        return distance

    def swap_cities(self, solution):
        # Swap two cities in the solution to create a new solution
        new_solution = solution[:]
        i, j = random.sample(range(self.num_cities), 2)
        new_solution[i], new_solution[j] = new_solution[j], new_solution[i]
        return new_solution

    def anneal(self):
        # Perform one iteration of the simulated annealing process
        new_solution = self.swap_cities(self.current_solution)
        current_distance = self.calculate_total_distance(self.current_solution)
        new_distance = self.calculate_total_distance(new_solution)
        # Calculate the probability of accepting the new solution
        acceptance_prob = self.acceptance_probability(current_distance, new_distance, self.temperature)
        if acceptance_prob > random.random():
            # Accept the new solution
            self.current_solution = new_solution
            current_distance = new_distance
            # Update the best solution if the new solution is better
            if current_distance < self.best_distance:
                self.best_distance = current_distance
                self.best_solution = self.current_solution[:]
        # Decrease the temperature (cooling step)
        self.temperature *= self.cooling_rate

    def acceptance_probability(self, current_distance, new_distance, temperature):
        # Calculate the acceptance probability for the new solution
        if new_distance < current_distance:
            return 1.0  # Always accept if the new solution is better
        else:
            # Accept with a probability that decreases as temperature decreases
            return math.exp((current_distance - new_distance) / temperature)

    def greedy_initial_solution(self):
        # Generate a greedy initial solution using the nearest neighbor heuristic
        unvisited = list(range(self.num_cities))
        solution = [unvisited.pop(0)]  # Start from the first city
        while unvisited:
            last = solution[-1]
            # Select the nearest unvisited city
            next_city = min(unvisited, key=lambda city: self.distance_matrix[last][city])
            solution.append(next_city)
            unvisited.remove(next_city)
        return solution

class UI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Traveling Salesman Problem")
        self.option_add("*tearOff", FALSE)
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.geometry(f"{self.width}x{self.height}+0+0")
        self.state("zoomed")

        # Create a canvas for drawing cities and roads
        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)
        self.w = self.width - padding * 2
        self.h = self.height - padding * 2

        self.cities_list = []
        self.tsp_solver = None
        self.is_running = False

        # Menu bar setup
        menu_bar = Menu(self)
        self.config(menu=menu_bar)
        menu_TS = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_TS, label='Salesman', underline=0)

        # Add menu options to generate cities and run the solver
        menu_TS.add_command(label="Generate", command=self.generate, underline=0)
        menu_TS.add_command(label="Run", command=self.start_solver, underline=0)

    def generate(self):
        # Generate random cities and draw them on the canvas
        self.clear_canvas()
        self.cities_list.clear()
        for i in range(num_cities):
            self.add_city(i)
        self.draw_cities()

    def add_city(self, index):
        # Add a new city at a random position within the canvas bounds
        x = random.randint(padding, self.w)
        y = random.randint(padding, self.h)
        node = Node(x, y, index)
        self.cities_list.append(node)

    def draw_cities(self):
        # Draw all cities on the canvas
        for city in self.cities_list:
            city.draw(self.canvas)

    def clear_canvas(self):
        # Clear the canvas
        self.canvas.delete("all")

    def start_solver(self):
        # Start the TSP solver
        if not self.cities_list:
            self.generate()  # Generate cities if not already generated
        self.tsp_solver = TSP_Solver(self.cities_list)
        self.is_running = True
        self.run_solver()

    def run_solver(self):
        # Run the solver iteratively using simulated annealing
        if self.is_running and self.tsp_solver.temperature > 1:
            self.tsp_solver.anneal()
            # Clear and redraw the current solution to visualize progress
            self.clear_canvas()
            self.draw_solution(self.tsp_solver.current_solution)
            self.display_current_distance()
            self.canvas.update()
            # Schedule the next iteration
            self.after(1, self.run_solver)
        else:
            # Stop the solver and display the best solution found
            self.is_running = False
            print(f"Best distance found: {self.tsp_solver.best_distance}")
            self.clear_canvas()
            self.draw_solution(self.tsp_solver.best_solution)
            self.display_best_distance()

    def display_best_distance(self):
        # Add a message to display the best distance found
        self.canvas.create_text(
            padding, padding,
            text=f"Best Distance Found: {int(self.tsp_solver.best_distance)}",
            font=('Arial', 20, 'bold'),
            fill='green',
            anchor='nw'
        )
        print(f"Best Distance Found: {int(self.tsp_solver.best_distance)}")

    def display_current_distance(self):
        # Display the current distance of the solution
        current_distance = self.tsp_solver.calculate_total_distance(self.tsp_solver.current_solution)
        self.canvas.create_text(
            padding, padding + 50,
            text=f"Current Distance: {int(current_distance)}",
            font=('Arial', 20, 'bold'),
            fill='orange',
            anchor='nw'
        )

    def draw_solution(self, solution):
        # Draw the path
        for i in range(len(solution)):
            city_a = self.cities_list[solution[i]]
            city_b = self.cities_list[solution[(i + 1) % len(solution)]]
            edge = Edge(city_a, city_b)
            edge.draw(self.canvas, color='red')  # Solid lines for the solution path
        # Draw the cities
        for city in self.cities_list:
            city.draw(self.canvas, color='blue')

if __name__ == '__main__':
    ui = UI()
    ui.mainloop()
