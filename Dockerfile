FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

COPY . /app

COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh

RUN chmod +x /app/scripts/entrypoint.sh

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y redis-server && apt-get clean

EXPOSE 8000

CMD ["/app/scripts/entrypoint.sh"]
