"""Tests for converter app."""
from django.test import TestCase
from django.urls import reverse

class ConverterViewsTests(TestCase):
    def test_pdf_to_word_page(self):
        response = self.client.get(reverse('pdf_to_word'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'converter/pdf_to_word.html')
    
    def test_word_to_pdf_page(self):
        response = self.client.get(reverse('word_to_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'converter/word_to_pdf.html')
    
    def test_merge_pdf_page(self):
        response = self.client.get(reverse('merge_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'converter/merge_pdf.html')