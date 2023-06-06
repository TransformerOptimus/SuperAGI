FROM mcr.microsoft.com/playwright/python:v1.34.0-jammy
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chrome chromium
COPY . .
COPY config.yaml ./config.yaml
COPY entrypoint.sh /entrypoint.sh
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /entrypoint.sh /wait-for-it.sh

CMD ["/wait-for-it.sh", "super__postgres:5432","-t","60","--","/entrypoint.sh"]