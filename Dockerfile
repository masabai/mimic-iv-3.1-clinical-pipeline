FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    gcc \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install DuckDB CLI
RUN curl -L https://github.com/duckdb/duckdb/releases/download/v1.2.2/duckdb_cli-linux-amd64.zip -o duckdb.zip \
    && unzip duckdb.zip -d /usr/local/bin \
    && rm duckdb.zip

COPY requiremments.txt .
RUN pip install --no-cache-dir -r requiremments.txt

COPY . .

CMD ["python", "flow/mimic_flow.py"]
