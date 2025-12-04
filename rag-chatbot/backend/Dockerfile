FROM python:3.11-slim

# Update system packages to reduce vulnerabilities
RUN apt-get update && \
    apt-get install -y sqlite3 libsqlite3-dev && \
    sqlite3 --version

WORKDIR /app
COPY ./ /app

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
