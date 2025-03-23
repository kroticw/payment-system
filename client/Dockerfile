FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY server.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD ["python", "server.py"] 