# Este archivo contiene ejemplos de código que el parser debería analizar correctamente.

# Definición de una función con parámetros y anotaciones de tipo
def sumar(a: int, b: int) -> int:
    resultado = a + b
    return resultado

# Uso de estructuras condicionales
if 5 > 3:
    print("Cinco es mayor que tres")
else:
    print("Esto nunca se imprimirá")

# Ejemplo de un bucle for
for i in range(5):
    print("Número:", i)

# Ejemplo de un bucle while
contador = 0
while contador < 3:
    print("Contador:", contador)
    contador  = contador + 1

# Llamada a la función definida anteriormente
print("La suma es:", sumar(10, 20))

# Ejemplo de listas y acceso a elementos
mi_lista = [1, 2, 3, 4]


# Ejemplo de un bucle for con una lista
for elemento in mi_lista:
    print("Elemento:", elemento)
