FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY statcan_transit_mcp/ /app/statcan_transit_mcp/
COPY pyproject.toml /app/

RUN pip install --no-cache-dir -e .

RUN mkdir -p /app/data /app/cache

EXPOSE 3000


CMD ["python", "-m", "statcan_transit_mcp.http_server"]

