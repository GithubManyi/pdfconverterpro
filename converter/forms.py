from django import forms
from django.core.validators import FileExtensionValidator

# Custom widget for multiple file uploads
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        default_attrs = {'multiple': 'multiple'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        value = files.get(name)
        if isinstance(value, list):
            return value
        return [value] if value else []

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result
    
class BaseFileUploadForm(forms.Form):
    """Base form for single file uploads."""
    file = forms.FileField(
        label='Choose File',
        widget=forms.ClearableFileInput(attrs={
            'class': 'hidden',
            'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.bmp,.tiff'
        }),
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 
                              'jpg', 'jpeg', 'png', 'bmp', 'tiff']
        )]
    )

class MultipleFileUploadForm(forms.Form):
    """Form for multiple file uploads (e.g., merge PDF, image to PDF)."""
    files = forms.FileField(
        label='Choose Files',
        widget=MultipleFileInput(attrs={  # Use our custom widget
            'class': 'hidden',
            'accept': '.pdf,.jpg,.jpeg,.png,.bmp,.tiff'
        }),
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff']
        )]
    )

# converter/forms.py - Enhanced PDFToWordForm
class PDFToWordForm(BaseFileUploadForm):
    """Form for PDF to Word conversion with formatting options."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['accept'] = '.pdf'
        self.fields['file'].validators = [
            FileExtensionValidator(allowed_extensions=['pdf'])
        ]
    
    # Add formatting options
    preserve_layout = forms.BooleanField(
        label='Preserve original layout',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 rounded'
        }),
        help_text='Keep the exact page layout (recommended for forms, reports)'
    )
    
    extract_text_only = forms.BooleanField(
        label='Extract text only',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 rounded'
        }),
        help_text='Remove images and tables for clean text extraction'
    )
    
    use_ocr = forms.BooleanField(
        label='Use OCR for scanned PDFs',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 rounded'
        }),
        help_text='Enable optical character recognition for scanned documents'
    )
    
    output_format = forms.ChoiceField(
        label='Output format',
        choices=[
            ('docx', 'Microsoft Word (.docx) - Recommended'),
            ('doc', 'Microsoft Word 97-2003 (.doc)'),
            ('rtf', 'Rich Text Format (.rtf)'),
            ('txt', 'Plain Text (.txt)'),
        ],
        initial='docx',
        widget=forms.RadioSelect(attrs={
            'class': 'space-y-2'
        }),
        help_text='Choose the output format that works best for you'
    )

class WordToPDFForm(BaseFileUploadForm):
    """Form for Word to PDF conversion."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['accept'] = '.doc,.docx'
        self.fields['file'].validators = [
            FileExtensionValidator(allowed_extensions=['doc', 'docx'])
        ]

class MergePDFForm(forms.Form):
    """Form for merging PDF files."""
    files = MultipleFileField(
        label='Choose Files',
        widget=MultipleFileInput(attrs={
            'class': 'hidden',
            'accept': '.pdf'
        }),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Select multiple PDF files to merge'
    )

    def clean_files(self):
        files = self.cleaned_data.get('files')
        if not files:
            raise forms.ValidationError('Please select at least one PDF file.')
        
        if len(files) > 10:
            raise forms.ValidationError('Maximum 10 files allowed.')
        
        for file in files:
            if file.size > 50 * 1024 * 1024:  # 50MB
                raise forms.ValidationError(f'{file.name} is too large. Maximum size is 50MB.')
            
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError(f'{file.name} is not a PDF file.')
        
        return files

# In converter/forms.py, update the SplitPDFForm class:
class SplitPDFForm(BaseFileUploadForm):
    """Form for splitting PDF files."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['accept'] = '.pdf'
        self.fields['file'].validators = [
            FileExtensionValidator(allowed_extensions=['pdf'])
        ]
    
    SPLIT_CHOICES = [
        ('range', 'Split by Page Range'),
        ('every', 'Split Every Page'),
        ('count', 'Split by Page Count'),
        ('custom', 'Custom Split Points'),
    ]
    
    split_type = forms.ChoiceField(
        label='Split Method',
        choices=SPLIT_CHOICES,
        initial='range',
        widget=forms.RadioSelect(attrs={
            'class': 'split-type-radio hidden'
        })
    )
    
    pages = forms.CharField(
        label='Pages to Extract',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded-lg',
            'placeholder': 'e.g., 1-3, 5, 7-10',
            'id': 'pagesInput'
        }),
        help_text='Enter specific pages (1,3,5) or ranges (1-5)'
    )
    
    split_every = forms.IntegerField(
        label='Split every N pages',
        required=False,
        min_value=1,
        max_value=50,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border rounded-lg',
            'id': 'splitEveryInput',
            'placeholder': 'e.g., 2 for every 2 pages'
        })
    )
    
    page_count = forms.IntegerField(
        label='Pages per split',
        required=False,
        min_value=1,
        max_value=100,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border rounded-lg',
            'id': 'pageCountInput',
            'placeholder': 'e.g., 10 pages per file'
        })
    )
    
    custom_split = forms.CharField(
        label='Custom split points',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded-lg',
            'id': 'customSplitInput',
            'placeholder': 'e.g., 3,7,15 (split after these pages)'
        }),
        help_text='Enter page numbers where to split (comma separated)'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        split_type = cleaned_data.get('split_type')
        
        if split_type == 'range':
            if not cleaned_data.get('pages'):
                raise forms.ValidationError({'pages': 'Please enter page ranges for splitting.'})
        elif split_type == 'every':
            if not cleaned_data.get('split_every'):
                raise forms.ValidationError({'split_every': 'Please enter how many pages per split.'})
        elif split_type == 'count':
            if not cleaned_data.get('page_count'):
                raise forms.ValidationError({'page_count': 'Please enter pages per split file.'})
        elif split_type == 'custom':
            if not cleaned_data.get('custom_split'):
                raise forms.ValidationError({'custom_split': 'Please enter custom split points.'})
        
        return cleaned_data

# In converter/forms.py, update the CompressPDFForm class:
# In converter/forms.py - Update the CompressPDFForm class:

# In converter/forms.py - COMPLETE CompressPDFForm class:

class CompressPDFForm(BaseFileUploadForm):
    """Form for compressing PDF files."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({
            'accept': '.pdf',
            'id': 'id_file',
            'class': 'hidden'  # Hide the default file input
        })
        self.fields['file'].validators = [
            FileExtensionValidator(allowed_extensions=['pdf'])
        ]
    
    COMPRESSION_CHOICES = [
        ('low', 'Low Compression (Best Quality)'),
        ('medium', 'Medium Compression (Recommended)'),
        ('high', 'High Compression (Smallest Size)'),
    ]
    
    compression_level = forms.ChoiceField(
        label='Compression Level',
        choices=COMPRESSION_CHOICES,
        initial='medium',
        widget=forms.HiddenInput(attrs={'id': 'compression_level_input'})
    )
    
    # Use CharField instead of MultipleChoiceField for easier handling
    optimize_options = forms.CharField(
        label='Optimization Options',
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'optimize_options_input'})
    )
    
    target_size = forms.IntegerField(
        label='Target Size (KB)',
        required=False,
        min_value=10,
        max_value=10240,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border rounded-lg',
            'placeholder': 'e.g., 500 for 500KB'
        }),
        help_text='Leave empty for automatic compression'
    )
    
    quality_preservation = forms.ChoiceField(
        label='Quality Priority',
        choices=[
            ('high', 'High Quality'),
            ('balanced', 'Balanced (Recommended)'),
            ('size', 'Maximum Compression'),
        ],
        initial='balanced',
        widget=forms.HiddenInput(attrs={'id': 'quality_preservation_input'})
    )
    
    def clean_optimize_options(self):
        """Convert comma-separated string back to list."""
        data = self.cleaned_data.get('optimize_options', '')
        if data:
            return data.split(',')
        return []
    
class ExcelToPDFForm(BaseFileUploadForm):
    """Form for Excel to PDF conversion."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['accept'] = '.xls,.xlsx'
        self.fields['file'].validators = [
            FileExtensionValidator(allowed_extensions=['xls', 'xlsx'])
        ]
    
    include_gridlines = forms.BooleanField(
        label='Include Gridlines',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 rounded'
        })
    )

# converter/forms.py
class ImageToPDFForm(MultipleFileUploadForm):
    """Form for Image to PDF conversion."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for required fields
        if not self.data:  # Only set initial if not POST
            self.fields['page_size'].initial = 'A4'
            self.fields['orientation'].initial = 'portrait'
        
        self.fields['files'].widget.attrs.update({
            'accept': '.jpg,.jpeg,.png,.bmp,.tiff,.gif,.webp',
            'multiple': True,
            'id': 'id_files',  # Important: Add ID for JavaScript
        })
        self.fields['files'].validators = [
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif', 'webp'])
        ]
        self.fields['files'].help_text = 'Select multiple images (max 20)'
    
    page_size = forms.ChoiceField(
        label='Page Size',
        choices=[
            ('A4', 'A4 (210 × 297 mm)'),
            ('letter', 'Letter (8.5 × 11 in)'),
            ('A5', 'A5 (148 × 210 mm)'),
            ('legal', 'Legal (8.5 × 14 in)'),
        ],
        required=True,  # Make sure it's required
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500'
        })
    )
    
    orientation = forms.ChoiceField(
        label='Orientation',
        choices=[
            ('portrait', 'Portrait'),
            ('landscape', 'Landscape'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500'
        })
    )
    
    placement = forms.ChoiceField(
        required=False,
        choices=[
            ('fit', 'Fit to Page'),
            ('full', 'Full Page'),
            ('center', 'Centered'),
            ('multiple', 'Multiple per Page'),
        ],
        initial='fit',
        widget=forms.HiddenInput()
    )
    
    add_page_numbers = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput()
    )