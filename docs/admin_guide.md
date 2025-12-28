# PDF Converter Pro - Admin Guide

## System Administration

### 1. Server Setup
```bash
# Clone repository
git clone [repository-url]
cd pdfconverterpro

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py migrate
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver