# Usar una imagen ligera de Python
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código y el Excel
COPY . .

# Exponer el puerto de Streamlit
EXPOSE 8501

# Comando para ejecutar la app gráfica
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]