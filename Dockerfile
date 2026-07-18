FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py scrip_mapping.csv ./
COPY upstox_mcp/ ./upstox_mcp/

ENV MCP_TRANSPORT=http \
    MCP_SERVER_HOST=0.0.0.0 \
    MCP_SERVER_PORT=8080

EXPOSE 8080

CMD ["python", "server.py"]
