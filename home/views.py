"""Views for home app."""
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import ContactMessage
from django.http import HttpResponse
from django.views.decorators.http import require_GET

def index(request):
    """Home page view."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'Free PDF Converter - Convert, Merge, Split PDF Files Online',
        'description': 'Free online PDF tools to convert, merge, split, and compress PDF files. No registration required.',
    }
    return render(request, 'home/index.html', context)

def tools(request):
    """Display all available PDF tools."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'All PDF Tools - Free Online PDF Converter',
        'description': 'Browse all our free PDF tools: PDF to Word, Word to PDF, Merge PDF, Split PDF, Compress PDF, Excel to PDF, Image to PDF.',
    }
    return render(request, 'home/tools.html', context)

def about(request):
    """About page view."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'About Us - PDF Converter Pro',
        'description': 'Learn about our free online file conversion tools and our mission to provide easy PDF solutions.',
    }
    return render(request, 'home/about.html', context)

def contact(request):
    """Contact page view."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Save to database
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )
        
        # Send email notification
        try:
            send_mail(
                f'New Contact Message from {name}',
                f'Email: {email}\n\nMessage:\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Thank you! Your message has been sent.')
        except:
            messages.success(request, 'Thank you! Your message has been saved.')
        
        return render(request, 'home/contact.html')
    
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'Contact Us - PDF Converter Pro',
        'description': 'Get in touch with our support team for any questions or feedback about our PDF tools.',
    }
    return render(request, 'home/contact.html', context)

def privacy(request):
    """Privacy policy page."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'Privacy Policy - PDF Converter Pro',
        'description': 'Our privacy policy regarding file conversion and data handling. Your files are secure with us.',
    }
    return render(request, 'home/privacy.html', context)

def terms(request):
    """Terms of Service page."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'Terms of Service - PDF Converter Pro',
        'description': 'Terms and conditions for using our free PDF conversion tools.',
    }
    return render(request, 'home/terms.html', context)

def cookies(request):
    """Cookie Policy page."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'Cookie Policy - PDF Converter Pro',
        'description': 'Learn how we use cookies on our PDF converter website.',
    }
    return render(request, 'home/cookies.html', context)

def quick_start(request):
    """Quick Start Guide page."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'Quick Start Guide - PDF Converter Pro',
        'description': 'Get started quickly with our PDF conversion tools. Easy step-by-step guide.',
    }
    return render(request, 'home/quick_start.html', context)

def faq(request):
    """Frequently Asked Questions page."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'FAQ - Frequently Asked Questions - PDF Converter Pro',
        'description': 'Find answers to common questions about our PDF conversion tools and services.',
    }
    return render(request, 'home/faq.html', context)

def handler_404(request, exception):
    """Custom 404 error handler."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'Page Not Found - 404 Error',
        'description': 'The page you are looking for could not be found.',
    }
    return render(request, 'errors/404.html', context, status=404)

def handler_500(request):
    """Custom 500 error handler."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'Server Error - 500 Error',
        'description': 'An internal server error has occurred.',
    }
    return render(request, 'errors/500.html', context, status=500)
# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.decorators.http import require_GET

# Health check view
@require_GET
def health_check(request):
    return HttpResponse("OK", status=200, content_type="text/plain")

urlpatterns = [
    # Health check endpoint - Render uses /healthz (no trailing slash)
    path('healthz', health_check),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Home app
    path('', include('home.urls')),
    
    # Converter app
    path('', include('converter.urls')),
]