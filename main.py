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
    """Procesa el contenido del archivo de acuerdo con el formato especificado."""
    try:
        # Paso 1: Leer el número de posiciones existentes (n)
        n = int(datos[0].strip())  # Primera línea
        if len(datos) < n + 3:
            raise ValueError("El archivo no contiene suficientes líneas para las coordenadas y el tamaño de la matriz.")

        # Paso 2: Leer las coordenadas de las posiciones existentes
        coordenadas = []
        for i in range(1, n + 1):  # Siguientes n líneas
            coordenadas.append(list(map(int, datos[i].split())))
        
        # Paso 3: Leer el tamaño de las matrices
        tamano_matriz = int(datos[n + 1].strip())  # Línea después de las coordenadas
        
        # Validar que el archivo tenga suficientes líneas para las matrices y max_sedes
        if len(datos) < n + 2 + 2 * tamano_matriz + 1:
            raise ValueError("El archivo no contiene suficientes líneas para las matrices de población y entorno empresarial.")

        # Paso 4: Leer la matriz de población
        matriz_pob = []
        inicio_pob = n + 2  # Inicio de la matriz de población
        for i in range(inicio_pob, inicio_pob + tamano_matriz):
            matriz_pob.append(list(map(int, datos[i].split())))

        # Paso 5: Leer la matriz de entorno empresarial
        matriz_emp = []
        inicio_emp = inicio_pob + tamano_matriz  # Inicio de la matriz de entorno empresarial
        for i in range(inicio_emp, inicio_emp + tamano_matriz):
            matriz_emp.append(list(map(int, datos[i].split())))

        # Paso 6: Leer el número de programas a ubicar (max_sedes)
        max_sedes = int(datos[-1].strip())  # Última línea

        # Validaciones adicionales
        if len(matriz_pob) != tamano_matriz or any(len(fila) != tamano_matriz for fila in matriz_pob):
            raise ValueError("La matriz de población no tiene el tamaño especificado.")
        if len(matriz_emp) != tamano_matriz or any(len(fila) != tamano_matriz for fila in matriz_emp):
            raise ValueError("La matriz de entorno empresarial no tiene el tamaño especificado.")
        for x, y in coordenadas:
            if not (0 <= x < tamano_matriz and 0 <= y < tamano_matriz):
                raise ValueError(f"Coordenada fuera de rango: ({x}, {y}).")

        # Crear la matriz preseleccionada
        preseleccionadas = [[0] * tamano_matriz for _ in range(tamano_matriz)]
        for x, y in coordenadas:
            preseleccionadas[x][y] = 1

        # Continuar con el procesamiento
        archivo_dzn = "datos.dzn"
        generar_archivo_dzn(archivo_dzn, tamano_matriz, matriz_pob, matriz_emp, preseleccionadas, max_sedes)
        resultado = ejecutar_minizinc_con_dzn(archivo_dzn, "./sedes.mzn")

        # Mostrar el resultado
        mostrar_resultado(resultado)

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
