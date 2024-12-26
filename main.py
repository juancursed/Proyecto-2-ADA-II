import tkinter as tk
from tkinter import filedialog, messagebox
from minizinc import Instance, Model, Solver
import traceback

def cargar_archivo():
    """Permite al usuario seleccionar un archivo y procesarlo."""
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo de entrada",
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
    )
    if archivo:
        try:
            with open(archivo, 'r') as f:
                datos = f.readlines()
            procesar_datos(datos)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

def procesar_datos(datos):
    """Procesa el contenido del archivo y genera el archivo .dzn."""
    try:
        # Extracción de datos del archivo
        n = int(datos[0].strip())
        coordenadas = [list(map(int, linea.split())) for linea in datos[1:n+1]]
        tamano_matriz = int(datos[n+1].strip())
        matriz_pob = [list(map(int, datos[i].split())) for i in range(n+2, n+2+tamano_matriz)]
        matriz_emp = [list(map(int, datos[i].split())) for i in range(n+2+tamano_matriz, n+2+2*tamano_matriz)]
        max_sedes = int(datos[-1].strip())


        preseleccionadas = [[0] * tamano_matriz for _ in range(tamano_matriz)]
        for i in range(tamano_matriz):
            for j in range(tamano_matriz):
                if [i, j] in coordenadas:
                    preseleccionadas[i][j] = 1
                

        archivo_dzn = "datos.dzn"
        generar_archivo_dzn(archivo_dzn, tamano_matriz, matriz_pob, matriz_emp, preseleccionadas, max_sedes)
        resultado = ejecutar_minizinc_con_dzn(archivo_dzn, "./sedes.mzn")

        # Mostrar el resultado
        mostrar_resultado(resultado)
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar los datos: {e}")
        print(traceback.format_exc())
        messagebox.showerror("Error", f"Error al procesar los datos: {e}")

def generar_archivo_dzn(nombre_archivo, n, matriz_pob, matriz_emp, preseleccionados, max_sedes):
    """Genera un archivo .dzn con el formato correcto para MiniZinc."""
    def convertir_a_matriz_dzn(matriz):
        filas = [f"|{', '.join(map(str, fila))}, " for fila in matriz[:-1]]  
        filas.append(f"|{', '.join(map(str, matriz[-1]))}|") 
        return f"{''.join(filas)}"

    with open(nombre_archivo, "w") as archivo:
        archivo.write(f"n = {n};\n")
        archivo.write(f"max_selecciones = {max_sedes};\n")
        archivo.write("matriz1 = [")
        archivo.write(convertir_a_matriz_dzn(matriz_pob))
        archivo.write("];\n")
        archivo.write("matriz2 = [")
        archivo.write(convertir_a_matriz_dzn(matriz_emp))
        archivo.write("];\n")
        archivo.write("preseleccionadas = [")
        archivo.write(convertir_a_matriz_dzn(preseleccionados))
        archivo.write("];\n")

def ejecutar_minizinc_con_dzn(archivo_dzn, modelo_mzn):
    """Ejecuta MiniZinc utilizando un archivo .dzn como entrada."""
    sedes = Model(modelo_mzn)
    solver = Solver.lookup("chuffed")
    instance = Instance(solver, sedes)

    instance.add_file(archivo_dzn)
    result = instance.solve()
    sol_matriz = result["seleccion"]
    sol_objetive = result["objective"]
    return sol_matriz, sol_objetive

def mostrar_resultado(resultado):
    """Muestra el resultado en la interfaz."""
    ventana_resultado = tk.Toplevel()
    ventana_resultado.title("Resultado")

    label = tk.Label(ventana_resultado, text="Resultado:")
    label.pack()

    texto = tk.Text(ventana_resultado, wrap=tk.WORD, height=10, width=50)
    texto.insert(tk.END, str(resultado))
    texto.pack()

    boton_cerrar = tk.Button(ventana_resultado, text="Cerrar", command=ventana_resultado.destroy)
    boton_cerrar.pack()

# Configuración de la interfaz principal
ventana = tk.Tk()
ventana.title("MiniZinc Interfaz")

label = tk.Label(ventana, text="Cargue un archivo de entrada para procesar el modelo.")
label.pack(pady=10)

boton_cargar = tk.Button(ventana, text="Cargar archivo", command=cargar_archivo)
boton_cargar.pack(pady=10)

boton_salir = tk.Button(ventana, text="Salir", command=ventana.quit)
boton_salir.pack(pady=10)

ventana.mainloop()
