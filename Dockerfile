FROM python:3.11.4
WORKDIR /app
COPY requirements.txt .

#RUN apt-get update && apt-get install --no-install-recommends -y git wget libpq-dev gcc python3-dev && pip install psycopg2
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
<<<<<<< HEAD

COPY . .
COPY config.yaml ./config.yaml
COPY entrypoint.sh ./entrypoint.sh
COPY wait-for-it.sh ./wait-for-it.sh
RUN chmod +x ./entrypoint.sh ./wait-for-it.sh
=======
RUN playwright install --with-deps chromium
COPY . .
COPY config.yaml ./config.yaml
COPY entrypoint.sh /entrypoint.sh
COPY wait-for-it.sh /wait-for-it.sh
COPY install_tool_dependencies.sh /install_tool_dependencies.sh
RUN chmod +x /entrypoint.sh /wait-for-it.sh /install_tool_dependencies.sh

# RUN chmod +x /entrypoint.sh /wait-for-it.sh /install_tool_dependencies.sh \
#     && chmod +x install_tool_dependencies.sh
>>>>>>> tool-input-arch

CMD ["./wait-for-it.sh", "super__postgres:5432","-t","60","--","./entrypoint.sh"]
