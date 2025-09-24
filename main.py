import numpy as np
import random
import tkinter as tk
import atexit
from collections import OrderedDict

class SandpileAutomaton:
    def __init__(self, size=4):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.root = tk.Tk()
        self.root.title("Sandpile Automaton (Toroidal) - Detección de Ciclos")

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

        # Etiqueta de ciclo
        self.cycle_label = tk.Label(self.root, text="Ciclo: No detectado")
        self.cycle_label.pack(pady=5)

        self.running = False
        self.update_interval = 250  # ms

        # Registro de explosiones
        self.explosion_log = []

        # Para detección de ciclos
        self.iteration_count = 0
        self.config_history = OrderedDict()  # Mantiene orden de inserción
        self.cycle_detected = False
        self.cycle_start_iteration = 0
        self.cycle_length = 0

        # Vincular evento de clic del mouse
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Guardar al salir
        atexit.register(self.save_explosions_to_file)

    def get_toroidal_neighbors(self, i, j):
        neighbors = []
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni = (i + di) % self.size
            nj = (j + dj) % self.size
            neighbors.append((ni, nj))
        return neighbors

    def grid_to_key(self):
        """Convierte el grid en una tupla para usar como clave en el diccionario"""
        return tuple(self.grid.flatten())

    def check_for_cycle(self):
        """Verifica si la configuración actual forma parte de un ciclo"""
        current_key = self.grid_to_key()
        
        if current_key in self.config_history:
            # ¡Ciclo detectado!
            self.cycle_start_iteration = self.config_history[current_key]
            self.cycle_length = self.iteration_count - self.cycle_start_iteration
            self.cycle_detected = True
            self.cycle_label.config(
                text=f"¡CICLO DETECTADO! Longitud: {self.cycle_length} iteraciones"
            )
            return True
        
        # Guardar configuración actual
        self.config_history[current_key] = self.iteration_count
        
        # Limitar el historial para no usar demasiada memoria
        if len(self.config_history) > 1000:
            self.config_history.popitem(last=False)
        
        return False

    def add_grain(self, i, j):
        was_running = self.running
        if self.running:
            self.stop_simulation()

        self.grid[i, j] += 1
        # ❌ ELIMINAR: self.iteration_count += 1  # Esto NO es una iteración
    
        # Verificar ciclo después de cada cambio
        if self.check_for_cycle():
            print(f"¡Ciclo detectado en iteración {self.iteration_count}!")
            print(f"Longitud del ciclo: {self.cycle_length} iteraciones")

        if self.grid[i, j] >= 4:
            cells_to_collapse = [(i, j)]
            self.collapse_cell(cells_to_collapse, set())
        else:
            self.draw_grid()
            if was_running:
                self.start_simulation()

    def collapse_cell(self, cells_to_collapse, affected_cells, original_call=True):
        """Colapsa celdas iterativamente usando una cola"""
        queue = cells_to_collapse[:]
    
        while queue:
            i, j = queue.pop(0)
        
            # Si la celda sigue siendo inestable
            if self.grid[i, j] >= 4:
                # Registrar antes del colapso
                old_value = self.grid[i, j]
            
                # Aplicar regla de colapso → ✅ ESTO SÍ es una iteración
                self.grid[i, j] -= 4
                affected_cells.add((i, j))
            
                # ✅ CORRECTO: Incrementar contador de iteraciones SOLO aquí
                self.iteration_count += 1
            
                # Aumentar vecinos
                neighbors = self.get_toroidal_neighbors(i, j)
                for ni, nj in neighbors:
                    self.grid[ni, nj] += 1
                    affected_cells.add((ni, nj))
                
                    if self.grid[ni, nj] >= 4 and (ni, nj) not in queue:
                        queue.append((ni, nj))
            
                # Verificar ciclo después de cada iteración
                if self.check_for_cycle():
                    print(f"¡Ciclo detectado durante avalancha! Iteración: {self.iteration_count}")
            
                # Actualizar visualización
                self.draw_grid(highlight_cell=(i, j), old_value=old_value)
                self.root.update()
                self.root.after(300)
    
        # Finalizar avalancha
        if original_call:
            self.explosion_log.append((len(affected_cells), np.sum(self.grid)))
            if self.running:
                self.root.after(self.update_interval, self.update)

    def on_canvas_click(self, event):
        if not self.running:  
            j = event.x // self.cell_size
            i = event.y // self.cell_size
            if 0 <= i < self.size and 0 <= j < self.size:
                self.add_grain(i, j)

    def draw_grid(self, highlight_cell=None, old_value=None):
        self.canvas.delete("all")
        for i in range(self.size):
            for j in range(self.size):
                value = self.grid[i, j]
                
                # Determinar color
                if (i, j) == highlight_cell and old_value is not None:
                    color = "orange"  # Resaltar celda en colapso
                elif value == 0:
                    color = "white"
                elif value == 1:
                    color = "lightblue"
                elif value == 2:
                    color = "blue"
                elif value == 3:
                    color = "darkblue"
                else:
                    color = "red"  # Celdas inestables
                
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                
                # Mostrar valor
                text_color = "black" if value < 2 else "white"
                if (i, j) == highlight_cell and old_value is not None:
                    text = f"{old_value}→{value}"
                    text_color = "black"
                else:
                    text = str(value)
                
                self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                        text=text, fill=text_color)
        
        # Actualizar energía total
        energia_total = np.sum(self.grid)
        self.energy_label.config(text=f"Energía del sistema: {energia_total}")
        
        # Actualizar contador de iteraciones
        self.info_label.config(text=f"Iteración: {self.iteration_count} - Modo: {'Ejecutando' if self.running else 'Pausa'}")

    def update_info_label(self):
        if self.running:
            self.info_label.config(text=f"Iteración: {self.iteration_count} - Modo: Ejecutando")
        else:
            self.info_label.config(text=f"Iteración: {self.iteration_count} - Modo: Pausa")

    def update(self):
        if self.running:
            # Elegir celda aleatoria para añadir grano
            i = random.randint(0, self.size - 1)
            j = random.randint(0, self.size - 1)
            self.add_grain(i, j)
            self.root.after(self.update_interval, self.update)

    def start_simulation(self):
        self.running = True
        self.update_info_label()
        self.update()

    def stop_simulation(self):
        self.running = False
        self.update_info_label()

    def single_step(self):
        i = random.randint(0, self.size - 1)
        j = random.randint(0, self.size - 1)
        self.add_grain(i, j)

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
    automaton = SandpileAutomaton(4)  # Empezar con 2x2 para probar ciclos
    automaton.run()