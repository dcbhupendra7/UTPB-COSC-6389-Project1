import math
import random
import tkinter as tk
from tkinter import Menu, Canvas, FALSE
import threading
import time

# Number of items in the set
num_items = 20
min_value = 1
max_value = 50
target_value = random.randint(50, 200)

# Backtracking function to find the subset sum
def subset_sum(items, target, partial=[], partial_sum=0, ui=None, iteration=[0]):
    if ui:
        iteration[0] += 1
        ui.update_backtracking(iteration[0], partial_sum, partial)  # Pass `partial` to update_backtracking
        time.sleep(0.5)

    if partial_sum == target:
        return partial
    if partial_sum > target:
        return None

    for i in range(len(items)):
        remaining = items[i + 1:]
        result = subset_sum(remaining, target, partial + [items[i]], partial_sum + items[i], ui, iteration)
        if result is not None:
            return result

    return None

# Particle Swarm Optimization for Subset Sum Problem
class Particle:
    def __init__(self, num_items):
        self.position = [random.choice([0, 1]) for _ in range(num_items)]
        self.velocity = [random.uniform(-1, 1) for _ in range(num_items)]
        self.best_position = self.position[:]
        self.best_value = float('inf')

    def update_velocity(self, global_best_position, w, c1, c2):
        for i in range(len(self.velocity)):
            r1 = random.random()
            r2 = random.random()
            cognitive = c1 * r1 * (self.best_position[i] - self.position[i])
            social = c2 * r2 * (global_best_position[i] - self.position[i])
            disturbance = random.uniform(-0.1, 0.1)
            self.velocity[i] = w * self.velocity[i] + cognitive + social + disturbance

    def update_position(self):
        for i in range(len(self.position)):
            if random.random() < 1 / (1 + math.exp(-self.velocity[i])):
                self.position[i] = 1
            else:
                self.position[i] = 0

class PSOSolver:
    def __init__(self, items, target, num_particles=30, max_iterations=100, ui=None):
        self.items = items
        self.target = target
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.particles = [Particle(len(items)) for _ in range(num_particles)]
        self.global_best_position = [0] * len(items)
        self.global_best_value = float('inf')
        self.ui = ui

    def fitness(self, position):
        subset_sum = sum(self.items[i] for i in range(len(position)) if position[i] == 1)
        if subset_sum > self.target:
            return float('inf')
        return abs(self.target - subset_sum)

    def solve(self):
        for iteration in range(self.max_iterations):
            for particle in self.particles:
                current_value = self.fitness(particle.position)
                if current_value < particle.best_value:
                    particle.best_value = current_value
                    particle.best_position = particle.position[:]
                if current_value < self.global_best_value:
                    self.global_best_value = current_value
                    self.global_best_position = particle.position[:]

            for particle in self.particles:
                particle.update_velocity(self.global_best_position, w=0.7, c1=1.8, c2=1.8)
                particle.update_position()

            if self.ui:
                self.ui.update_pso(self.global_best_position, iteration, self.global_best_value)
                self.ui.update()  # Immediately update the UI to reflect the new state
                time.sleep(0.2)  # Pause to allow visualization

            if self.global_best_value == 0:
                break

        return self.global_best_position if self.global_best_value == 0 else None

# Main UI Class
class SubsetSumUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Subset Sum Problem")
        self.option_add("*tearOff", FALSE)
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.width}x{self.height}+0+0")
        self.state("zoomed")

        self.canvas = Canvas(self, bg='white')  # Set background to white
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)

        # Menu bar setup
        menu_bar = Menu(self)
        self['menu'] = menu_bar
        menu_SS = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_SS, label='Subset Sum', underline=0)

        menu_SS.add_command(label="Generate Set", command=self.generate_set, underline=0)
        menu_SS.add_command(label="Solve with Backtracking", command=self.start_backtracking_solver, underline=0)
        menu_SS.add_command(label="Solve with PSO", command=self.start_pso_solver, underline=0)

        self.items_list = []
        self.target = target_value
        self.solution = None
        self.partial_visuals = []

    def generate_set(self):
        self.items_list = [random.randint(min_value, max_value) for _ in range(num_items)]
        self.clear_canvas()
        self.draw_target()
        self.draw_items()

    def clear_canvas(self):
        self.canvas.delete("all")
        self.partial_visuals = []

    def draw_items(self):
        x_start = 100
        y_start = 150
        for i, value in enumerate(self.items_list):
            rect = self.canvas.create_rectangle(x_start, y_start + i * 30, x_start + 100, y_start + (i + 1) * 30,
                                                fill='lightblue')
            text = self.canvas.create_text(x_start + 50, y_start + i * 30 + 15, text=str(value), font=('Arial', 14, 'bold'))
            self.partial_visuals.append((rect, text))

    def draw_target(self):
        self.canvas.create_text(150, 100, text=f'Target: {self.target}', font=('Arial', 18, 'bold'), fill='red')

    def start_backtracking_solver(self):
        if not self.items_list:
            self.generate_set()

        self.clear_canvas()  # Clear previous solution
        self.draw_target()
        self.draw_items()

        threading.Thread(target=self.run_backtracking_solver).start()

    def run_backtracking_solver(self):
        iteration = [0]
        self.solution = subset_sum(self.items_list, self.target, ui=self, iteration=iteration)
        self.after(0, self.draw_solution)

    def start_pso_solver(self):
        if not self.items_list:
            self.generate_set()

        self.clear_canvas()  # Clear previous solution
        self.draw_target()
        self.draw_items()

        threading.Thread(target=self.run_pso_solver).start()

    def run_pso_solver(self):
        pso_solver = PSOSolver(self.items_list, self.target, ui=self)
        pso_solution = pso_solver.solve()
        self.solution = [self.items_list[i] for i in range(len(self.items_list)) if pso_solution and pso_solution[i] == 1]
        self.after(0, self.draw_solution)

    def update_partial(self, partial, partial_sum):
        self.clear_partial_highlights()
        for value in partial:
            for i, item_value in enumerate(self.items_list):
                if item_value == value:
                    rect, text = self.partial_visuals[i]
                    self.canvas.itemconfig(rect, fill='black')
                    break

        difference = self.target - partial_sum
        sign = '+' if difference > 0 else ''
        self.canvas.create_text(400, 50, text=f'Current Partial Sum: {partial_sum} (Difference: {sign}{difference})',
                                font=('Arial', 16, 'bold'), fill='yellow', tag='partial_sum')

    def update_backtracking(self, iteration, partial_sum, partial=[]):
        self.canvas.delete('iteration_info')
        difference = self.target - partial_sum
        sign = '+' if difference > 0 else ''

        # Highlight the selected stack
        self.clear_partial_highlights()  # Clear previous highlights
        for value in partial:
            for i, item_value in enumerate(self.items_list):
                if item_value == value:
                    rect, text = self.partial_visuals[i]
                    self.canvas.itemconfig(rect, fill='black')

        self.canvas.create_text(600, 50, text=f'Backtracking Iteration: {iteration}, Partial Sum: {partial_sum} (Difference: {sign}{difference})', font=('Arial', 16, 'bold'), fill='black', tag='iteration_info')

    def clear_partial_highlights(self):
        for rect, text in self.partial_visuals:
            self.canvas.itemconfig(rect, fill='lightblue')
        self.canvas.delete('partial_sum')

    def update_pso(self, best_position, iteration, best_value):
        self.clear_partial_highlights()
        self.canvas.delete('iteration_info')

        current_sum = sum(self.items_list[i] for i in range(len(best_position)) if best_position[i] == 1)
        difference = current_sum - self.target
        sign = '+' if difference > 0 else ''

        for i, selected in enumerate(best_position):
            if selected == 1:
                rect, text = self.partial_visuals[i]
                self.canvas.itemconfig(rect, fill='black')

        if best_value == 0:
            status_text = "Perfect Match Found!"
        else:
            status_text = f"Current Sum: {current_sum}({sign}{difference})"

        self.canvas.create_text(400, 50, text=f'Iteration: {iteration + 1}, {status_text}', font=('Arial', 16, 'bold'), fill='black', tag='iteration_info')

    def draw_solution(self):
        self.canvas.delete('solution_info')

        if not self.solution:
            self.canvas.create_text(400, 100, text='No Solution Found', font=('Arial', 18, 'bold'), fill='red', tag='solution_info')
        else:
            x_start = 250
            y_start = 150
            solution_sum = sum(self.solution)
            difference = solution_sum - self.target
            sign = '+' if difference > 0 else ''

            self.canvas.create_text(300, 100,
                                    text=f'Solution Found: {solution_sum}({sign}{difference})',
                                    font=('Arial', 18, 'bold'), fill='green', tag='solution_info')

            for i, value in enumerate(self.solution):
                self.canvas.create_rectangle(x_start, y_start + i * 30, x_start + 100, y_start + (i + 1) * 30,
                                             fill='lightgreen', tag='solution_info')
                self.canvas.create_text(x_start + 50, y_start + i * 30 + 15, text=str(value), font=('Arial', 14, 'bold'), tag='solution_info')

# Run the application
if __name__ == '__main__':
    ui = SubsetSumUI()
    ui.mainloop()