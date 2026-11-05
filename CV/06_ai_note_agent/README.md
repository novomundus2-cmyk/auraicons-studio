# Entorno del agente de notas

Este laboratorio requiere Python 3.11 o posterior. El lock de uv conserva las
versiones comprobadas; instala con `uv sync --frozen`. La restricción
`pillow>=13.0.0` corrige vulnerabilidades de los decodificadores de imagen de
Pillow, dependencia transitiva de matplotlib.

Los usuarios de Python 3.10 deben actualizar el intérprete de este laboratorio.
El ejemplo PySpark del directorio `public/` mantiene su entorno independiente
con Python 3.10 y Java 17. La prueba offline comprueba el punto de entrada del
paquete y un recorrido de imagen en memoria; no envía notas a servicios externos.
