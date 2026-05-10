# Proyecto climatologia-aviacion

Descubre como sera tu vuelo antes de despegar.
Convierte la incertidumbre en informacion: conoce las condiciones de tu vuelo y destino antes de embarcar.

## Integrantes

Neide Ochocho Penet;
Guillermo Diaz Barrero;
Mateo Molina Garibo;
Rodrigo Gutman Nieto Peret;

## Estructura

- src: codigo fuente (descarga, limpieza, scoring de vuelos, integraciones con APIs)
- web: aplicacion Streamlit (app.py)
- data: ficheros crudos y trabajados (CSV y JSON)
- notebooks: ficheros de prueba y analisis exploratorio


## Instrucciones

- Virtual env: python -m venv .venv
- Activarlo: .venv\Scripts\activate / source .venv/bin/activate
- Librerias: pip install -r requirements.txt
- Arrancar la app: streamlit run web/app.py


## Arquitectura Docker

La aplicacion se divide en dos contenedores que se ejecutan en orden:

```
APIs externas --> [data-pipeline] --> volumen /data (CSV/JSON) --> [streamlit-app] --> Usuario
```

**Contenedor 1 — data-pipeline**

Ejecuta download.py y clean.py. Descarga los datos de las APIs de vuelos y tiempo, los limpia y los guarda en el volumen compartido. Cuando termina su trabajo, se apaga.

**Contenedor 2 — streamlit-app**

Arranca despues del primero (depends_on: data-pipeline). Lee los datos ya procesados del volumen y sirve la aplicacion web en el puerto 8505.

**Volumen compartido — data-volume**

Es una carpeta gestionada por Docker que montan los dos contenedores. Permite que el pipeline escriba los ficheros y que la app los lea sin que ninguno dependa directamente del otro.

Para arrancar todo junto:

```bash
docker compose up --build
# La app queda disponible en http://localhost:8505
```

## Conceptos Docker

- Imagen: plantilla con el sistema operativo, Python y las librerias instaladas. Se construye a partir del Dockerfile.
- Contenedor: una instancia en ejecucion de una imagen. Es como un mini-ordenador aislado.
- Dockerfile: archivo con las instrucciones para construir una imagen (que instalar, que copiar, como arrancar).
- Docker Compose: herramienta para definir y arrancar varios contenedores a la vez, en orden, con un solo comando.
- Volumen: carpeta persistente fuera de los contenedores. Si un contenedor se apaga, los datos no se pierden.

