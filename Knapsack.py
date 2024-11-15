import math
import random
import tkinter as tk
from tkinter import *

# Problem parameters
num_items = 100
frac_target = 0.7
min_value = 128
max_value = 2048

# UI parameters
screen_padding = 25
item_padding = 5
stroke_width = 5

# Genetic Algorithm parameters
num_generations = 1000
pop_size = 50
elitism_count = 2
mutation_rate = 0.05  # Adjusted mutation rate

sleep_time = 100  # in milliseconds

# Helper function to generate a random RGB color
def random_rgb_color():
    red = random.randint(0x10, 0xff)
    green = random.randint(0x10, 0xff)
    blue = random.randint(0x10, 0xff)
    hex_color = '#{:02x}{:02x}{:02x}'.format(red, green, blue)
    return hex_color

# Class to represent an item with value and color
class Item:
    def __init__(self):
        self.value = random.randint(min_value, max_value)
        self.color = random_rgb_color()
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    def place(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self, canvas, active=False):
        gap = 14
        # Draw the rectangle representing the item
        if active:
            canvas.create_rectangle(self.x,
                                    self.y,
                                    self.x + self.w,
                                    self.y + self.h,
                                    fill=self.color,
                                    outline=self.color,
                                    width=stroke_width)
        else:
            canvas.create_rectangle(self.x,
                                    self.y,
                                    self.x + self.w,
                                    self.y + self.h,
                                    fill='',
                                    outline=self.color,
                                    width=stroke_width)

        # Draw the value text with more spacing
        canvas.create_text(self.x + self.w + gap, self.y + self.h / 2, text=f'{self.value}', anchor='w', font=('Arial', 12), fill='white')

# Genetic Algorithm Class
class GeneticAlgorithm:
    def __init__(self, items_list, target, pop_size, num_generations, mutation_rate, elitism_count):
        self.items_list = items_list
        self.target = target
        self.pop_size = pop_size
        self.num_generations = num_generations
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        self.population = []
        self.generation = 0
        self.best_genome = None

    # Calculate the sum of the values of items included in the genome
    def gene_sum(self, genome):
        return sum(item.value for idx, item in enumerate(self.items_list) if genome[idx])

    # Fitness function with penalty for exceeding target value
    def fitness(self, genome):
        total_value = self.gene_sum(genome)
        # Penalize if exceeding target, otherwise reward being close to target
        if total_value > self.target:
            return -abs(total_value - self.target) * 2
        return 1 / (1 + abs(self.target - total_value))

    # Generate the initial population randomly
    def generate_initial_population(self):
        self.population = [[random.random() < frac_target for _ in range(len(self.items_list))] for _ in range(self.pop_size)]

    # Select parents using Stochastic Universal Sampling (SUS)
    def sus_select_parents(self, population, fitnesses):
        total_fitness = sum(fitnesses)
        point_distance = total_fitness / 2  # Two parents are selected
        start_point = random.uniform(0, point_distance)

        parents = []
        current_sum = 0
        for genome, fitness in zip(population, fitnesses):
            current_sum += fitness
            if len(parents) < 2 and current_sum >= start_point:
                parents.append(genome)
                start_point += point_distance
        return parents[0], parents[1]

    # Two-point crossover to generate new offspring
    def crossover(self, parent1, parent2):
        length = len(parent1)
        point1 = random.randint(0, length // 2)
        point2 = random.randint(point1 + 1, length - 1)

        child = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
        return child

    # Multi-point mutation for better diversity
    def mutate(self, genome):
        for i in range(len(genome)):
            if random.random() < self.mutation_rate:
                genome[i] = not genome[i]
        return genome

    # Maintain diversity by using fitness sharing
    def fitness_sharing(self, population, fitnesses):
        diversity_factor = 0.1
        shared_fitnesses = []
        for i in range(len(population)):
            shared_fitness = fitnesses[i]
            for j in range(len(population)):
                if i != j and self.hamming_distance(population[i], population[j]) < len(population[i]) * diversity_factor:
                    shared_fitness *= 0.9  # Reduce fitness if similar to others
            shared_fitnesses.append(shared_fitness)
        return shared_fitnesses

    # Calculate Hamming distance between two genomes
    def hamming_distance(self, genome1, genome2):
        return sum(g1 != g2 for g1, g2 in zip(genome1, genome2))

    # Evolve the population to the next generation
    def evolve_population(self):
        fitnesses = [self.fitness(genome) for genome in self.population]
        shared_fitnesses = self.fitness_sharing(self.population, fitnesses)  # Use fitness sharing
        sorted_population = sorted(zip(self.population, shared_fitnesses), key=lambda x: x[1], reverse=True)
        new_population = [genome for genome, _ in sorted_population[:self.elitism_count]]

        while len(new_population) < self.pop_size:
            parent1, parent2 = self.sus_select_parents([p for p, _ in sorted_population], [f for _, f in sorted_population])
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            new_population.append(child)

        self.population = new_population
        self.best_genome = sorted_population[0][0]

    def run_step(self):
        if self.generation == 0:
            self.generate_initial_population()

        self.evolve_population()
        self.generation += 1

        return self.best_genome, self.generation

# The main UI class
class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Knapsack")
        self.option_add("*tearOff", FALSE)
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.width, self.height))
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)
        self.canvas.configure(bg='black')  # Set background to black
        self.items_list = []

        # Menu bar setup
        menu_bar = Menu(self)
        self['menu'] = menu_bar
        menu_K = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_K, label='Knapsack', underline=0)

        menu_K.add_command(label="Generate", command=self.generate_knapsack, underline=0)
        menu_K.add_command(label="Get Target", command=self.set_target, underline=0)
        menu_K.add_command(label="Run", command=self.start_ga, underline=0)

        self.target = 0

        # Initialize Genetic Algorithm variables
        self.ga = None

    def get_rand_item(self):
        i1 = Item()
        for i2 in self.items_list:
            if i1.value == i2.value:
                return None
        return i1

    def add_item(self):
        item = self.get_rand_item()
        while item is None:
            item = self.get_rand_item()
        self.items_list.append(item)

    def generate_knapsack(self):
        self.items_list.clear()  # Clear existing items
        for i in range(num_items):
            self.add_item()

        item_max = 0
        item_min = 9999
        for item in self.items_list:
            item_min = min(item_min, item.value)
            item_max = max(item_max, item.value)

        w = self.width - screen_padding
        h = self.height - screen_padding
        num_rows = math.ceil(num_items / 6)
        row_w = w / 8 - item_padding
        row_h = (h - 200) / num_rows

        for x in range(0, 6):
            for y in range(0, num_rows):
                if x * num_rows + y >= num_items:
                    break
                item = self.items_list[x * num_rows + y]
                item_w = row_w / 2
                item_h = max(item.value / item_max * row_h, 1)
                item.place(screen_padding + x * row_w + x * item_padding,
                           screen_padding + y * row_h + y * item_padding,
                           item_w,
                           item_h)

        self.clear_canvas()
        self.draw_items()

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_items(self):
        for item in self.items_list:
            item.draw(self.canvas)

    def draw_target(self):
        x = (self.width - screen_padding) / 8 * 7
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 2 - screen_padding
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='yellow')
        self.canvas.create_text(x + w // 2, y + h + screen_padding, text=f'Target: {int(self.target)}', font=('Arial', 18, 'bold'), fill='green')

    def draw_sum(self, item_sum, target):
        x = (self.width - screen_padding) / 8 * 6
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 2 - screen_padding
        if target != 0:
            h *= (item_sum / target)
        else:
            h = 0
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='orange')
        
        # Calculate the difference between sum and target
        difference = item_sum - target
        difference_text = f"({'+' if difference > 0 else ''}{int(difference)})" if difference != 0 else ""
        
        # Display sum with difference
        sum_text = f'Sum: {int(item_sum)}{difference_text}'
        self.canvas.create_text(x + w // 2, y + h + screen_padding, 
                              text=sum_text, 
                              font=('Arial', 18, 'bold'), 
                              fill='blue')

    def draw_genome(self, genome, gen_num):
        for idx, item in enumerate(self.items_list):
            item.draw(self.canvas, active=genome[idx])
        x = (self.width - screen_padding) / 8 * 6
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 4 * 3
        self.canvas.create_text(x + w, y + h + screen_padding * 2, text=f'Generation {gen_num}', font=('Arial', 18, 'bold'), fill='red')

    def get_item_sum(self, genome):
        return sum(item.value for idx, item in enumerate(self.items_list) if genome[idx])

    def set_target(self):
        target_set = []
        for x in range(int(num_items * frac_target)):
            item = self.items_list[random.randint(0, len(self.items_list) - 1)]
            while item in target_set:
                item = self.items_list[random.randint(0, len(self.items_list) - 1)]
            target_set.append(item)
        total = sum(item.value for item in target_set)
        self.target = total
        self.clear_canvas()
        self.draw_items()
        self.draw_target()

    def start_ga(self):
        if self.target == 0:
            self.set_target()

        self.ga = GeneticAlgorithm(self.items_list, self.target, pop_size, num_generations, mutation_rate, elitism_count)
        self.ga.running = True
        self.run_ga_step()

    def run_ga_step(self):
        if self.ga.generation == 0:
            self.ga.generate_initial_population()

        self.ga.evolve_population()
        self.ga.generation += 1

        best_genome, generation = self.ga.best_genome, self.ga.generation
        item_sum = self.get_item_sum(best_genome)

        # Draw current state
        self.clear_canvas()
        self.draw_items()
        self.draw_genome(best_genome, generation)
        self.draw_target()
        self.draw_sum(item_sum, self.target)
        self.update()

        # Print current generation info
        print(f'Generation {generation}, Sum: {item_sum}, Fitness: {self.ga.fitness(best_genome)}')

        # Check if we have met the target
        if item_sum == self.target:
            self.ga.running = False
            print('Exact solution found!')
        elif self.ga.running and self.ga.generation < self.ga.num_generations:
            # Continue to next step if target not met and we haven't reached max generations
            self.after(sleep_time, self.run_ga_step)
        else:
            self.ga.running = False
            print('Algorithm finished.')

# Instantiate and run the UI
if __name__ == '__main__':
    ui = UI()
    ui.mainloop()