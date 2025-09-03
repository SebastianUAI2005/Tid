import matplotlib.pyplot as plt

def plot_explosiones(filename="explosiones.txt"):
    colors = plt.cm.tab10.colors  # Paleta de colores
    with open(filename, "r") as f:
        for idx, line in enumerate(f):
            celdas = []
            energia = []
            datos = line.strip().split(" ")
            for dato in datos:
                parts = dato.split(",")
                if len(parts) == 2:
                    celdas.append(int(parts[0]))
                    energia.append(int(parts[1]))
            x = range(1, len(celdas) + 1)
            color = colors[idx % len(colors)]
            plt.plot(x, celdas, label=f"Celdas afectadas línea {idx+1}", marker="o", color=color)
            plt.plot(x, energia, label=f"Energía total línea {idx+1}", marker="s", linestyle="--", color=color)

    plt.xlabel("Número de explosión")
    plt.ylabel("Valor")
    plt.title("Evolución de las explosiones en el autómata")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    plot_explosiones()