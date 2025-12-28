#!/bin/bash
# Setup script for PDF Converter Pro

echo "Setting up PDF Converter Pro..."
echo "================================"

# Create virtual environment
echo "1. Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "2. Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment
echo "3. Setting up environment..."
cp .env.example .env
echo "Please edit .env file with your settings"

# Run migrations
echo "4. Running migrations..."
python manage.py migrate

# Create superuser
echo "5. Creating superuser..."
python manage.py createsuperuser

# Collect static files
echo "6. Collecting static files..."
python manage.py collectstatic --noinput

echo "Setup complete!"
echo "To run the server: python manage.py runserver"
echo "Admin URL: http://localhost:8000/admin"