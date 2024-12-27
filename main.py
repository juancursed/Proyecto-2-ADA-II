import tkinter as tk
from tkinter import filedialog, messagebox
from minizinc import Instance, Model, Solver
import traceback
import time 

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
    """Procesa el contenido del archivo de acuerdo con el formato especificado."""
    try:
        start_time = time.time() 

        # Paso 1: Leer el número de posiciones existentes (n)
        n = int(datos[0].strip())  # Primera línea
        if len(datos) < n + 3:
            raise ValueError("El archivo no contiene suficientes líneas para las coordenadas y el tamaño de la matriz.")

        # Paso 2: Leer las coordenadas de las posiciones existentes
        coordenadas = [list(map(int, datos[i].split())) for i in range(1, n + 1)]

        # Paso 3: Leer el tamaño de las matrices
        tamano_matriz = int(datos[n + 1].strip())  # Línea después de las coordenadas

        # Validar que el archivo tenga suficientes líneas para las matrices y max_sedes
        if len(datos) < n + 2 + 2 * tamano_matriz + 1:
            raise ValueError("El archivo no contiene suficientes líneas para las matrices de población y entorno empresarial.")

        # Paso 4: Leer las matrices de población y entorno empresarial
        inicio_pob = n + 2
        matriz_pob = [list(map(int, datos[i].split())) for i in range(inicio_pob, inicio_pob + tamano_matriz)]
        inicio_emp = inicio_pob + tamano_matriz
        matriz_emp = [list(map(int, datos[i].split())) for i in range(inicio_emp, inicio_emp + tamano_matriz)]

        # Paso 5: Leer el número máximo de sedes
        max_sedes = int(datos[-1].strip())

        # Paso 6: Crear la matriz preseleccionada
        preseleccionadas = [[0] * tamano_matriz for _ in range(tamano_matriz)]
        for x, y in coordenadas:
            preseleccionadas[x][y] = 1

        # Generar archivo .dzn
        archivo_dzn = "datos.dzn"
        generar_archivo_dzn(archivo_dzn, tamano_matriz, matriz_pob, matriz_emp, preseleccionadas, max_sedes)

        # Tiempo de procesamiento de datos
        data_processing_time = time.time() - start_time

        # Ejecutar MiniZinc
        resultado, execution_time = ejecutar_minizinc_con_dzn(archivo_dzn, "./sedes.mzn")

        # Mostrar resultados junto con tiempos
        mostrar_resultado(resultado, data_processing_time, execution_time)

    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar los datos: {e}")
        print(traceback.format_exc())

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
    start_time = time.time()  # Inicio del tiempo de ejecución de MiniZinc

    sedes = Model(modelo_mzn)
    solver = Solver.lookup("chuffed")
    instance = Instance(solver, sedes)
    instance.add_file(archivo_dzn)
    result = instance.solve()

    execution_time = time.time() - start_time  # Tiempo de ejecución
    sol_matriz = result["seleccion"]
    sol_objetive = result["objective"]
    return (sol_matriz, sol_objetive), execution_time

def mostrar_resultado(resultado, data_time, exec_time):
    """Muestra el resultado en la interfaz junto con métricas de rendimiento."""
    sol_matriz, sol_objetivo = resultado

    ventana_resultado = tk.Toplevel()
    ventana_resultado.title("Resultado y Benchmarking")

    label = tk.Label(ventana_resultado, text="Resultado:")
    label.pack()

    texto = tk.Text(ventana_resultado, wrap=tk.WORD, height=15, width=50)
    texto.insert(tk.END, f"Matriz de selección:\n{sol_matriz}\n\n")
    texto.insert(tk.END, f"Valor objetivo: {sol_objetivo}\n")

    texto.insert(tk.END, f"Tiempo de ejecución del modelo: {exec_time:.2f} segundos\n")
    texto.pack()

    boton_cerrar = tk.Button(ventana_resultado, text="Cerrar", command=ventana_resultado.destroy)
    boton_cerrar.pack()

# Configuración de la interfaz principal
ventana = tk.Tk()
ventana.title("MiniZinc Interfaz con Benchmarking")

label = tk.Label(ventana, text="Cargue un archivo de entrada para procesar el modelo.")
label.pack(pady=10)

boton_cargar = tk.Button(ventana, text="Cargar archivo", command=cargar_archivo)
boton_cargar.pack(pady=10)

boton_salir = tk.Button(ventana, text="Salir", command=ventana.quit)
boton_salir.pack(pady=10)

ventana.mainloop()
