# Python Parser

Este proyecto es un parser simple que analiza un archivo de entrada en Python y verifica su sintaxis. Utiliza expresiones regulares para tokenizar el código y una clase `AnalizadorSintactico` para validar la estructura del código Python en el archivo de entrada.

## Requisitos

- Python 3.x
- Clonar o descargar este repositorio
- Ejecutar el programa desde la línea de comandos

## Archivos en el proyecto

- `parser.py`: El archivo principal que contiene el código del parser.
- `entrada.py`: Un archivo de ejemplo con código Python para ser analizado por el parser.
- `salida.txt`: Archivo de salida que contiene el resultado del análisis sintáctico.

## Uso

1. Coloca el archivo de código Python que deseas analizar en el mismo directorio y asegúrate de que tenga una extensión `.py`.
2. Abre una terminal y navega al directorio del proyecto.
3. Ejecuta el siguiente comando para analizar el archivo:


      ```bash
      python3 parser.py Entrada0.py
      ```

4. El resultado del análisis se guardará en `salida.txt`. Si el archivo es sintácticamente correcto, verás el mensaje:

    ```plaintext
    El analisis sintactico ha finalizado exitosamente.
    ```

    Si hay errores, verás un mensaje de error con la ubicación y descripción del error, por ejemplo:

    ```plaintext
    <linea,columna> Error sintactico: se encontro: "<token_encontrado>"; se esperaba: "<tokens_esperados>"
    ```


