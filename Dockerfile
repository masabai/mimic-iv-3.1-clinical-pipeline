FROM python:3.11-slim

WORKDIR /app

# Install git and postgres client libraries needed for compilation
RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy your pip configuration and install the full stack
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files into the container
COPY . .

# Keep the container awake or run your Prefect flow entrypoint
CMD ["python", "flow/mimic_flow.py"]
