#!/bin/bash

# Setup Script for Movie Recommendation System
# This script automates the initial setup process

echo "=========================================="
echo "🎬 Movie Recommendation System Setup"
echo "=========================================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Create virtual environment (recommended)
echo ""
echo "📌 Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "⚠️  Failed to create virtual environment. Continuing anyway..."
else
    echo "✅ Virtual environment created"
    echo ""
    echo "📌 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies
echo ""
echo "📌 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies."
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Setup .env file
echo ""
echo "📌 Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file with your Neo4j credentials:"
    echo "   nano .env"
    echo "   or"
    echo "   code .env"
else
    echo "ℹ️  .env file already exists, skipping..."
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Neo4j credentials"
echo "2. Run: python data_seeder.py"
echo "3. Run: streamlit run app.py"
echo ""
echo "If you created a virtual environment, activate it with:"
echo "   source venv/bin/activate"
echo ""
