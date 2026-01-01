# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Keep for compatibility
    path('', views.index, name='home'),   # Add alias for templates
    
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('cookies/', views.cookies, name='cookies'),
    path('quick-start/', views.quick_start, name='quick_start'),
    path('faq/', views.faq, name='faq'),
    path('tools/', views.tools, name='tools'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
]