# Usa una imagen base de Python
FROM python:3.11-slim

# Configura el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos necesarios
COPY requirements.txt .
COPY app /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto que usa la API
EXPOSE 8000

# Comando para iniciar la API
CMD ["uvicorn", "whatsapp_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
