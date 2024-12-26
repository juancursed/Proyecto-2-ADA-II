% Parámetros
int: n = 6; % Tamaño de las matrices
int: max_selecciones = 3; % Máximo número de casillas seleccionables

% Matrices de entrada
array[1..n, 1..n] of int: matriz1 = array2d(1..n, 1..n, [
    3, 1, 4, 8, 6, 1,
    5, 9, 2, 7, 3, 0,
    8, 6, 3, 2, 4, 9,
    1, 4, 5, 9, 7, 1,
    6, 2, 8, 3, 1, 10,
    16, 12, 8, 13, 10,9
]);

array[1..n, 1..n] of int: matriz2 = array2d(1..n, 1..n, [
    7, 3, 2, 5, 9, 10,
    1, 8, 6, 4, 2, 0,
    9, 5, 3, 7, 6, 12,
    4, 2, 8, 1, 3, 8,
    5, 7, 6, 4, 8, 9,
    26, 12, 5, 13, 21,2
]);

% Casillas preseleccionadas (1 si está seleccionada desde el inicio, 0 en caso contrario)
array[1..n, 1..n] of int: preseleccionadas = array2d(1..n, 1..n, [
    0, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 0, 0,
    0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 1 
]);

% Variables
array[1..n, 1..n] of var 0..1: seleccion; % 1 si seleccionamos la casilla, 0 en caso contrario

% Función para calcular la suma de adyacentes en una matriz
function var int: suma_adyacentes(array[1..n, 1..n] of int: matriz, int: i, int: j) =
    sum([
        matriz[x, y] | x, y in 1..n where
        abs(x - i) <= 1 /\ abs(y - j) <= 1 /\ (x != i \/ y != j)
    ]);

% Restricciones
% 1. Incorporar las casillas preseleccionadas
constraint forall(i in 1..n, j in 1..n) (
    preseleccionadas[i, j] = 1 -> seleccion[i, j] = 1
);

% 2. Limitar el número de casillas seleccionables (nuevas y preseleccionadas)
constraint sum([seleccion[i, j] | i in 1..n, j in 1..n]) <= max_selecciones;


% 3. Prohibir que las casillas seleccionadas estén adyacentes entre sí
constraint forall(i in 1..n, j in 1..n) (
    seleccion[i, j] = 1 -> forall(x, y in 1..n where abs(x - i) <= 1 /\ abs(y - j) <= 1 /\ (x != i \/ y != j)) (
        seleccion[x, y] = 0
    )
);

% Función objetivo: Maximizar la suma de los valores adyacentes en ambas matrices
solve maximize sum([
    seleccion[i, j] * (suma_adyacentes(matriz1, i, j) + suma_adyacentes(matriz2, i, j))
    | i in 1..n, j in 1..n
]);
