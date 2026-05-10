[READ ME.md](https://github.com/user-attachments/files/25681143/READ.ME.md)
## Proyecto climatología-aviación

Descubre cómo será tu vuelo antes de despegar
Convierte la incertidumbre en información: conoce las condiciones de tu vuelo y destino antes de embarcar.

### Estructura

- src: código
- data: ficheros crudos y trabajados
- notebooks: ficheros de prueba

### Instrucciones

- Virtual env: python -m venv .venv
- Activarlo: .venv\Scripts\activate. /// source .venv/bin/activate
- Librerías: pip install -r requirements .txt

### Integrantes
Neide Ochocho Pénet;
Guillermo Díaz Barrero;
Mateo Molina Garibo;
Rodrigo Gutmán Nieto Péret;

# Proyecto Legión - Documentación Docker

## Conceptos Fundamentales
- Imagen: Paquete ejecutable que incluye el código, el tiempo de ejecución, las herramientas del sistema y las librerías.
- Contenedor: Instancia de ejecución de una imagen.
- Dockerfile: Archivo de texto que contiene los comandos para construir una imagen.
- Docker Compose: Herramienta para definir y ejecutar aplicaciones Docker de varios contenedores.
- Volumen: Mecanismo para persistir datos generados y utilizados por contenedores Docker.

## Arquitectura de la Aplicación
Se ha implementado una arquitectura de contenedor único basada en Python 3.11-slim. El diseño separa la lógica de procesamiento situada en la carpeta src de la interfaz de usuario ubicada en la carpeta web. El manejo de datos en la carpeta data se ha proyectado para su uso con volúmenes, garantizando la persistencia de los archivos CSV y JSON.

## Guía de Ejecución
1. Construcción de la imagen:
docker build -t proyecto-legion .

2. Ejecución del contenedor:
docker run -p 5000:5000 proyecto-legion

## Notas Técnicas
La configuración del Docker Engine incluye el uso de DNS externos (8.8.8.8) para mitigar restricciones de conectividad durante la descarga de imágenes base desde el registro oficial.