FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY config.yaml .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0","--port", "8001","--reload"]