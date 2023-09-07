# Stage 1: Compile image
FROM python:3.10-slim-bullseye AS compile-image
WORKDIR /app

RUN apt-get update && \
    apt-get install --no-install-recommends -y wget libpq-dev gcc g++ python3-dev curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN curl -sL https://deb.nodesource.com/setup_16.x -o /root/nodesource_setup.sh


COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader averaged_perceptron_tagger punkt

COPY . .

RUN chmod +x ./entrypoint.sh ./wait-for-it.sh ./install_tool_dependencies.sh ./entrypoint_celery.sh

# Stage 2: Build image
FROM python:3.10-slim-bullseye AS build-image
WORKDIR /app


COPY --from=compile-image /root/nodesource_setup.sh /tmp/nodesource_setup.sh
RUN bash /tmp/nodesource_setup.sh
RUN apt install nodejs

RUN apt-get update && \
    apt-get install --no-install-recommends -y libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN npm install flexsearch node-html-parser

COPY --from=compile-image /opt/venv /opt/venv
COPY --from=compile-image /app /app
COPY --from=compile-image /root/nltk_data /root/nltk_data

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8001