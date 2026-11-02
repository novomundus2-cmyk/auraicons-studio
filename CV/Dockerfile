# ==============================================================================
# NovusMundus Quant Platform & Interactive Visualizer
# Production Docker Container with Zero-Vulnerability Base
# ==============================================================================
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8765

# Install curl for container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy complete project code into container
COPY . .

# Ensure data persistence folders exist
RUN mkdir -p /app/07_trading_bot/data

EXPOSE 8765

# Healthcheck monitoring the live trading status API
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8765/api/trading/status || exit 1

# Launch the NetGUI server with LAN mode enabled
CMD ["python", "05_archify_visualizer/netgui_server.py", "--lan", "--no-browser", "--port", "8765"]
