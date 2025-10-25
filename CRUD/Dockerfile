# Usamos una imagen base oficial de Python
FROM python:3.9-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de dependencias
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install -r requirements.txt

# Copiamos el resto del código de la aplicación
COPY . .

# Exponemos el puerto 5000 (en el que corre Flask)
EXPOSE 5000

# El comando para correr la aplicación cuando inicie el contenedor
CMD ["python", "app.py"]