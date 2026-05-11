# Dockerfile - proyecto-legion
# Este es el primer contenedor del flujo, el que arranca la app de Streamlit

# Usamos la imagen oficial de Python 3.12 
FROM python:3.12-slim

# Esto evita que Python cree archivos .pyc y que los logs salgan en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Aqui le decimos al contenedor que trabaje dentro de la carpeta /app
WORKDIR /app

# Instalamos dependencias del sistema que algunas librerias de Python necesitan
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el requirements.txt e instalamos las librerias
# Lo hacemos antes de copiar el codigo para que Docker use la cache
# si el requirements.txt no ha cambiado, no reinstala todo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el codigo de la app al contenedor
COPY src/    ./src/
COPY web/    ./web/
COPY data/   ./data/

# El puerto donde corre Streamlit
EXPOSE 8505

# Comando para arrancar la app
CMD ["streamlit", "run", "web/app.py", \
     "--server.port=8505", \
     "--server.address=0.0.0.0"]