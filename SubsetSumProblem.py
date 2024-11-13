import random
import tkinter as tk
from tkinter import Menu, Canvas, FALSE
import threading
import time

# Number of items in the set
num_items = 20
# Minimum value of an item
min_value = 1
# Maximum value of an item
max_value = 50
# Target sum to reach
target_value = random.randint(50, 200)


# Backtracking function to find the subset sum
def subset_sum(items, target, partial=[], partial_sum=0, ui=None):
    # Update the UI to reflect the current state
    if ui:
        ui.update_partial(partial, partial_sum)
        time.sleep(0.5)  # Pause to allow visualization

    # Check if the partial sum is equal to the target
    if partial_sum == target:
        return partial

    # If partial_sum exceeds target, return None
    if partial_sum > target:
        return None

    for i in range(len(items)):
        remaining = items[i + 1:]
        result = subset_sum(remaining, target, partial + [items[i]], partial_sum + items[i], ui)
        if result is not None:
            return result

    return None


# Main UI Class
class SubsetSumUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Subset Sum Problem")
        self.option_add("*tearOff", FALSE)
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.width}x{self.height}+0+0")
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)

        # Menu bar setup
        menu_bar = Menu(self)
        self['menu'] = menu_bar
        menu_SS = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_SS, label='Subset Sum', underline=0)

        menu_SS.add_command(label="Generate Set", command=self.generate_set, underline=0)
        menu_SS.add_command(label="Solve", command=self.start_solver, underline=0)

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
            text = self.canvas.create_text(x_start + 50, y_start + i * 30 + 15, text=str(value), font=('Arial', 14))
            self.partial_visuals.append((rect, text))

    def draw_target(self):
        self.canvas.create_text(150, 100, text=f'Target: {self.target}', font=('Arial', 18),
                                fill='darkorange')

    def start_solver(self):
        if not self.items_list:
            self.generate_set()

        # Run the solver in a separate thread to keep the UI responsive
        threading.Thread(target=self.run_solver).start()

    def run_solver(self):
        self.solution = subset_sum(self.items_list, self.target, ui=self)
        self.draw_solution()

    def update_partial(self, partial, partial_sum):
        # Highlight the items currently in the partial solution
        self.clear_partial_highlights()
        for value in partial:
            for i, item_value in enumerate(self.items_list):
                if item_value == value:
                    rect, text = self.partial_visuals[i]
                    self.canvas.itemconfig(rect, fill='yellow')
                    break

        # Update the running sum of the partial solution
        self.canvas.create_text(400, 50, text=f'Current Partial Sum: {partial_sum}', font=('Arial', 16),
                                fill='yellow', tag='partial_sum')

    def clear_partial_highlights(self):
        # Clear previous partial highlights and the partial sum text
        for rect, text in self.partial_visuals:
            self.canvas.itemconfig(rect, fill='lightblue')
        self.canvas.delete('partial_sum')

    def draw_solution(self):
        if self.solution is None:
            self.canvas.create_text(400, 100, text='No Solution Found', font=('Arial', 18), fill='red')
        else:
            x_start = 250
            y_start = 150
            solution_sum = sum(self.solution)
            self.canvas.create_text(300, 100, text=f'Solution Found: {solution_sum}', font=('Arial', 18, 'bold'), fill='green')
            for i, value in enumerate(self.solution):
                self.canvas.create_rectangle(x_start, y_start + i * 30, x_start + 100, y_start + (i + 1) * 30,
                                             fill='lightgreen')
                self.canvas.create_text(x_start + 50, y_start + i * 30 + 15, text=str(value), font=('Arial', 14, 'bold'))


# Run the application
if __name__ == '__main__':
    ui = SubsetSumUI()
    ui.mainloop()
