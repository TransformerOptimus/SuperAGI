FROM python:3.9
WORKDIR /app
COPY requirements.txt .

#RUN apt-get update && apt-get install --no-install-recommends -y git wget libpq-dev gcc python3-dev && pip install psycopg2
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader averaged_perceptron_tagger punkt

COPY . .
RUN chmod +x ./entrypoint*

EXPOSE 8000
EXPOSE 80

ENTRYPOINT ["entrypoint.sh"]
