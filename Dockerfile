FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x ./entrypoint*

EXPOSE 8000
EXPOSE 80

ENTRYPOINT ["entrypoint.sh"]