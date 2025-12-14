#!/bin/bash

# Azure Web App Startup Script for Streamlit
echo "Starting Streamlit Movie Recommendation System..."
echo "Neo4j URI: $NEO4J_URI"
echo "Neo4j Username: $NEO4J_USERNAME"

# Set default port if not provided
PORT="${PORT:-8000}"
echo "Running on port: $PORT"

# Run Streamlit
python -m streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
