FROM python:3.10-slim-bullseye AS compile-image
WORKDIR /app

RUN apt-get update &&  \
    apt-get install --no-install-recommends -y wget libpq-dev gcc g++ python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY entrypoint.sh ./entrypoint.sh
COPY wait-for-it.sh ./wait-for-it.sh
RUN chmod +x ./entrypoint.sh ./wait-for-it.sh

# Downloads the tools
RUN python superagi/tool_manager.py

# Set executable permissions for install_tool_dependencies.sh
RUN chmod +x install_tool_dependencies.sh

# Install dependencies
RUN ./install_tool_dependencies.sh

FROM python:3.10-slim-bullseye AS build-image
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=compile-image /opt/venv /opt/venv
COPY --from=compile-image /app /app

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

