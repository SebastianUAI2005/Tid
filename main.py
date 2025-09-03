import numpy as np
import random
import tkinter as tk
import atexit  # para guardar log al salir

class SandpileAutomaton:
    def __init__(self, size=4):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.root = tk.Tk()
        self.root.title("Sandpile Automaton (Toroidal)")

        # Configurar canvas
        self.cell_size = 20
        self.canvas = tk.Canvas(self.root, 
                               width=size * self.cell_size, 
                               height=size * self.cell_size)
        self.canvas.pack()

        # Botones de control
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.start_button = tk.Button(control_frame, text="Iniciar", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(control_frame, text="Detener", command=self.stop_simulation)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.step_button = tk.Button(control_frame, text="Un Paso", command=self.single_step)
        self.step_button.pack(side=tk.LEFT, padx=5)

        # Etiqueta de energía total
        self.energy_label = tk.Label(self.root, text="Energía del sistema: 0")
        self.energy_label.pack(pady=5)

        # Etiqueta de información
        self.info_label = tk.Label(self.root, text="Modo: Pausa - Haz clic en las celdas para añadir granos")
        self.info_label.pack(pady=5)

        self.running = False
        self.update_interval = 100  # ms

        # Registro de explosiones (lista de tuplas: (celdas_afectadas, energia_sistema))
        self.explosion_log = []

        # Vincular evento de clic del mouse
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Guardar explosiones al salir
        atexit.register(self.save_explosions_to_file)

    def get_toroidal_neighbors(self, i, j):
        neighbors = []
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni = (i + di) % self.size
            nj = (j + dj) % self.size
            neighbors.append((ni, nj))
        return neighbors

    def add_grain(self, i, j):
        self.grid[i, j] += 1
        if self.grid[i, j] >= 4:
            self.collapse_cell(i, j, set())

    def collapse_cell(self, i, j, affected_cells):
        """Colapsa una celda y registra explosión"""
        self.grid[i, j] = 0
        affected_cells.add((i, j))
        neighbors = self.get_toroidal_neighbors(i, j)
        for ni, nj in neighbors:
            self.grid[ni, nj] += 1
        for ni, nj in neighbors:    
            if self.grid[ni, nj] >= 4:
                self.collapse_cell(ni, nj, affected_cells)

        # Al final de la propagación registrar
        energia_total = np.sum(self.grid)
        if affected_cells:  
            self.explosion_log.append((len(affected_cells), int(energia_total)))

    def random_step(self):
        i = random.randint(0, self.size - 1)
        j = random.randint(0, self.size - 1)
        self.add_grain(i, j)

    def on_canvas_click(self, event):
        if not self.running:  
            j = event.x // self.cell_size
            i = event.y // self.cell_size
            if 0 <= i < self.size and 0 <= j < self.size:
                self.add_grain(i, j)
                self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.size):
            for j in range(self.size):
                value = self.grid[i, j]
                if value == 0:
                    color = "white"
                elif value == 1:
                    color = "lightblue"
                elif value == 2:
                    color = "blue"
                elif value == 3:
                    color = "darkblue"
                else:
                    color = "red"
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                        text=str(value), fill="black" if value < 2 else "white")

        # actualizar energía total
        energia_total = np.sum(self.grid)
        self.energy_label.config(text=f"Energía del sistema: {energia_total}")

    def update_info_label(self):
        if self.running:
            self.info_label.config(text="Modo: Ejecutando - La simulación está en curso")
        else:
            self.info_label.config(text="Modo: Pausa - Haz clic en las celdas para añadir granos")

    def update(self):
        if self.running:
            self.random_step()
            self.draw_grid()
            self.root.after(self.update_interval, self.update)

    def start_simulation(self):
        self.running = True
        self.update_info_label()
        self.update()

    def stop_simulation(self):
        self.running = False
        self.update_info_label()

    def single_step(self):
        self.random_step()
        self.draw_grid()

    def run(self):
        self.draw_grid()
        self.update_info_label()
        self.root.mainloop()

    def save_explosions_to_file(self):
        """Guardar explosion_log en un txt al terminar el programa"""
        with open("explosiones.txt", "a") as f:
            for affected, energia in self.explosion_log:
                f.write(f"{affected},{energia} ")
            f.write("\n")


if __name__ == "__main__":
    automaton = SandpileAutomaton(10)
    automaton.run()
