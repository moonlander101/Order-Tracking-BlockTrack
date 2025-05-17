FROM python:3.11-slim

# Install jq and pip dependencies
RUN apt-get update && \
    apt-get install -y jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# COPY . .

WORKDIR /app/blocktrack_backend

EXPOSE 8000
