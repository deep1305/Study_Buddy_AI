## Parent image
FROM python:3.12-slim

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USE_OLLAMA=false

## Work directory inside the docker container
WORKDIR /app

## Installing system dependancies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements first for better caching
COPY requirements.txt .

## Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

## Copy project files
COPY . .

## Install project (editable)
RUN pip install --no-cache-dir -e .

# Used PORTS
EXPOSE 8501

# Run the app 
CMD ["streamlit", "run", "application.py", "--server.port=8501", "--server.address=0.0.0.0","--server.headless=true"]