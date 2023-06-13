FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium
COPY . .
COPY config.yaml ./config.yaml
COPY entrypoint.sh /entrypoint.sh
COPY wait-for-it.sh /wait-for-it.sh
COPY install_tool_dependencies.sh /install_tool_dependencies.sh
RUN chmod +x /entrypoint.sh /wait-for-it.sh /install_tool_dependencies.sh

# RUN chmod +x /entrypoint.sh /wait-for-it.sh /install_tool_dependencies.sh \
#     && chmod +x install_tool_dependencies.sh

CMD ["/wait-for-it.sh", "super__postgres:5432","-t","60","--","/entrypoint.sh"]