import numpy as np
import random
import tkinter as tk
import time

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
        
        # Etiqueta de información
        self.info_label = tk.Label(self.root, text="Modo: Pausa - Haz clic en las celdas para añadir granos")
        self.info_label.pack(pady=5)
        
        self.running = False
        self.update_interval = 100  # ms
        
        # Vincular evento de clic del mouse
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
    def get_toroidal_neighbors(self, i, j):
        """Obtiene los vecinos adyacentes con condiciones de contorno toroidales"""
        neighbors = []
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni = (i + di) % self.size
            nj = (j + dj) % self.size
            neighbors.append((ni, nj))
        return neighbors
    
    def add_grain(self, i, j):
        """Añade un grano en la posición (i,j) y propaga si es necesario"""
        self.grid[i, j] += 1
        if self.grid[i, j] >= 4:
            self.collapse_cell(i, j)
    
    def collapse_cell(self, i, j):
        """Colapsa una celda que alcanza 4 y propaga a sus vecinos"""
        self.grid[i, j] = 0
        neighbors = self.get_toroidal_neighbors(i, j)
        for ni, nj in neighbors:
            self.grid[ni, nj] += 1
            if self.grid[ni, nj] >= 4:
                self.collapse_cell(ni, nj)
    
    def random_step(self):
        """Realiza un paso aleatorio del autómata"""
        i = random.randint(0, self.size - 1)
        j = random.randint(0, self.size - 1)
        self.add_grain(i, j)
    
    def on_canvas_click(self, event):
        """Maneja el evento de clic en el canvas"""
        if not self.running:  # Solo funciona cuando está en pausa
            # Calcular coordenadas de la celda
            j = event.x // self.cell_size
            i = event.y // self.cell_size
            
            # Asegurarse de que las coordenadas están dentro de los límites
            if 0 <= i < self.size and 0 <= j < self.size:
                self.add_grain(i, j)
                self.draw_grid()
                
    
    def draw_grid(self):
        """Dibuja la matriz en el canvas"""
        self.canvas.delete("all")
        
        for i in range(self.size):
            for j in range(self.size):
                value = self.grid[i, j]
                
                # Determinar color basado en el valor
                if value == 0:
                    color = "white"
                elif value == 1:
                    color = "lightblue"
                elif value == 2:
                    color = "blue"
                elif value == 3:
                    color = "darkblue"
                else:
                    color = "red"  # Para valores > 3 (no debería ocurrir)
                
                # Dibujar celda
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                           fill=color, 
                                           outline="gray")
                
                # Mostrar el valor numérico
                self.canvas.create_text(x1 + self.cell_size//2, 
                                      y1 + self.cell_size//2, 
                                      text=str(value),
                                      fill="black" if value < 2 else "white")
    
    def update_info_label(self):
        """Actualiza la etiqueta de información"""
        if self.running:
            self.info_label.config(text="Modo: Ejecutando - La simulación está en curso")
        else:
            self.info_label.config(text="Modo: Pausa - Haz clic en las celdas para añadir granos")
    
    def update(self):
        """Actualiza la simulación"""
        if self.running:
            self.random_step()
            self.draw_grid()
            self.root.after(self.update_interval, self.update)
    
    def start_simulation(self):
        """Inicia la simulación continua"""
        self.running = True
        self.update_info_label()
        self.update()
    
    def stop_simulation(self):
        """Detiene la simulación"""
        self.running = False
        self.update_info_label()
    
    def single_step(self):
        """Ejecuta un solo paso de la simulación"""
        self.random_step()
        self.draw_grid()
    
    def run(self):
        """Ejecuta la aplicación"""
        self.draw_grid()  # Dibujar estado inicial
        self.update_info_label()
        self.root.mainloop()

# Crear y ejecutar la simulación
if __name__ == "__main__":
    automaton = SandpileAutomaton()  # Tamaño de la matriz
    automaton.run()
    print("hola")