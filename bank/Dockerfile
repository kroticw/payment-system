FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .

# Устанавливаем права на выполнение
RUN chmod +x main.py

EXPOSE 8080

# Используем main.py как точку входа
CMD ["python", "main.py"] 