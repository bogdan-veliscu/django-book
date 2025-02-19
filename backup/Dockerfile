FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    cron \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    boto3 \
    python-dateutil

WORKDIR /app

COPY scripts/ /app/

RUN chmod +x /app/*.sh && \
    echo "0 3 * * * /app/backup.sh >> /var/log/cron.log 2>&1" | crontab -

CMD ["cron", "-f"] 