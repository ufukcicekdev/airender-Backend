FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x scripts/railway-start.sh scripts/railway-web.sh scripts/railway-celery.sh \
    && mkdir -p media/uploads media/previews media/renders staticfiles

EXPOSE 8000

# Railway sets $PORT; railway.toml startCommand overrides this when deployed there.
CMD ["sh", "scripts/railway-start.sh"]
