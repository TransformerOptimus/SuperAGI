FROM python:3.9-slim-bullseye
WORKDIR /app
COPY requirements.txt .

RUN apt-get update &&  \
    apt-get install --no-install-recommends -y git wget libpq-dev gcc g++ python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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
