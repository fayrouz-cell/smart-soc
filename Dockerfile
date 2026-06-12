FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tshark \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 idsuser && \
    mkdir -p /app/data/logs /app/data/pcap_samples /app/data/datasets && \
    chown -R idsuser:idsuser /app

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set permissions
RUN chown -R idsuser:idsuser /app

# Switch to non-root user
USER idsuser

# Default to replay mode
ENV IDS_MODE=replay

# Run IDS
CMD ["python", "main.py", "--start", "--mode", "replay"]


