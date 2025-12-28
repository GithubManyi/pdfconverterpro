# PDF Converter Pro

A complete online file conversion platform for PDF, Word, Excel, and Images.

## Features
- PDF to Word conversion
- Word to PDF conversion
- PDF merge, split, compress
- Excel to PDF conversion
- Image to PDF conversion
- Secure file handling
- Mobile responsive design
- AdSense ready

## Setup Instructions

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Copy environment file: `cp .env.example .env`
6. Update `.env` with your settings
7. Run migrations: `python manage.py migrate`
8. Create superuser: `python manage.py createsuperuser`
9. Run server: `python manage.py runserver`

## Project Structure
- `core/` - Django project settings
- `home/` - Home page and static pages
- `converter/` - All conversion tools
- `static/` - CSS, JS, images
- `media/` - Uploaded files (auto-created)
- `scripts/` - Utility scripts

## Deployment
See `render.yaml` for Render deployment or use any Django-compatible hosting.