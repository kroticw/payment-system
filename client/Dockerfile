FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .
COPY service.py .
COPY client.py .
COPY main.py .

# Устанавливаем права на выполнение
RUN chmod +x main.py

EXPOSE 5001

# Используем main.py как точку входа
CMD ["python", "main.py"] 