% Parámetros
int: n; 
int: max_selecciones; 
array[1..n, 1..n] of int: matriz1 ;
array[1..n, 1..n] of int: matriz2 ;
array[1..n, 1..n] of int: preseleccionadas ; 

% Variables
array[1..n, 1..n] of var 0..1: seleccion; 

% Solo contar nuevas selecciones (excluyendo preseleccionadas)
var int: nuevas_selecciones = sum([seleccion[i, j] | i, j in 1..n where preseleccionadas[i, j] = 0]);

% Función para calcular la suma de adyacentes en una matriz
function var int: suma_adyacentes(array[1..n, 1..n] of int: matriz, int: i, int: j) =
    sum([matriz[x, y] | x, y in 1..n where abs(x - i) <= 1 /\ abs(y - j) <= 1 /\ (x != i \/ y != j)]);

% Restricciones
% 1. Incorporar las casillas preseleccionadas
constraint forall(i in 1..n, j in 1..n) (
    preseleccionadas[i, j] = 1 -> seleccion[i, j] = 1
);

% 2. Limitar la cantidad de nuevas selecciones
constraint nuevas_selecciones <= max_selecciones;


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
