#!/bin/bash

# Azure Web App Startup Script for Streamlit
echo "=========================================="
echo "Starting Streamlit Movie Recommendation System..."
echo "=========================================="

# Set default port if not provided (Azure sets PORT automatically)
export PORT="${PORT:-8000}"
echo "Running on port: $PORT"

# Log environment variables (without sensitive data)
echo "Neo4j URI configured: ${NEO4J_URI:+Yes}"
echo "Neo4j Username: ${NEO4J_USERNAME:-Not set}"
echo "Python version: $(python --version)"
echo "Streamlit version: $(python -m streamlit --version)"

# Ensure streamlit config directory exists
mkdir -p ~/.streamlit

# Create streamlit config for Azure
cat > ~/.streamlit/config.toml << EOF
[server]
headless = true
port = $PORT
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"
serverPort = $PORT

[theme]
base = "dark"
EOF

echo "Streamlit configuration created"
echo "=========================================="
echo "Starting application..."
echo "=========================================="

# Run Streamlit with explicit configuration
python -m streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
