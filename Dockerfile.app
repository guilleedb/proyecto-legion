# Dockerfile.app - proyecto-legion
# Contenedor 2: sirve la app de Streamlit

# Usamos la misma imagen base que el contenedor 1
FROM python:3.12-slim

# Esto evita que Python cree archivos .pyc y que los logs salgan en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Aqui le decimos al contenedor que trabaje dentro de la carpeta /app
WORKDIR /app

# Instalamos dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el requirements.txt e instalamos las librerias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el codigo de la app y los modulos de src
# Los datos NO se copian aqui, llegan a traves del volumen compartido
COPY src/ ./src/
COPY web/ ./web/

# El puerto donde corre Streamlit
EXPOSE 8505

# Comando para arrancar la app
CMD ["streamlit", "run", "web/app.py", \
     "--server.port=8505", \
     "--server.address=0.0.0.0"]
