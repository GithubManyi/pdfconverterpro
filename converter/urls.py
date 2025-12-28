# converter/urls.py
"""URL routing for converter app."""
from django.urls import path
from . import views

urlpatterns = [
    path('pdf-to-word/', views.pdf_to_word, name='pdf_to_word'),
    path('word-to-pdf/', views.word_to_pdf, name='word_to_pdf'),
    path('merge-pdf/', views.merge_pdf, name='merge_pdf'),
    path('split-pdf/', views.split_pdf, name='split_pdf'),
    path('compress-pdf/', views.compress_pdf_view, name='compress_pdf'),  # Keep this as compress_pdf
    path('excel-to-pdf/', views.excel_to_pdf, name='excel_to_pdf'),
    path('image-to-pdf/', views.image_to_pdf, name='image_to_pdf'),
    path('download/<uuid:task_id>/', views.download_file, name='download_file'),
    
]