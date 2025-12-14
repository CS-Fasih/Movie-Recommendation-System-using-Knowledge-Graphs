#!/bin/bash

# Azure Web App Startup Script for Streamlit
echo "Starting Streamlit application..."

# Set default port if not provided
PORT="${PORT:-8000}"

# Run Streamlit
python -m streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
