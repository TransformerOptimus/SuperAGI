FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY config.yaml .
COPY ./entrypoint* /app/

RUN chmod +x /app/entrypoint*

ENTRYPOINT [ "entrypoint.sh" ]