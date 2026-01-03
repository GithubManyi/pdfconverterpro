"""
Secure views for converter app.
"""
import os
import uuid
import logging
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.http import FileResponse, HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ValidationError, SuspiciousOperation
from ipware import get_client_ip

from .models import UploadedFile, ConversionTask
from .forms import (
    PDFToWordForm, WordToPDFForm, MergePDFForm, 
    SplitPDFForm, CompressPDFForm, ExcelToPDFForm, 
    ImageToPDFForm
)
from .utils import (
    handle_file_upload, convert_pdf_to_word, convert_word_to_pdf, merge_pdfs,
    split_pdf, compress_pdf as compress_pdf_util,
    convert_excel_to_pdf, convert_images_to_pdf,
    split_pdf_by_range, split_pdf_custom, split_pdf_every_page, split_pdf_by_count
)
from .security import SecureFileValidator, AntiAbuseSystem, FilePathSecurity, create_secure_temp_file, cleanup_secure_temp

logger = logging.getLogger(__name__)

def rate_limit_check(request, operation_type: str):
    """
    Check rate limiting for operations
    """
    client_ip, _ = get_client_ip(request)
    
    if not client_ip:
        return True  # Can't track, but proceed
    
    # Different limits for different operations
    limits = {
        'upload': 10,  # 10 uploads per minute
        'conversion': 5,  # 5 conversions per minute
        'download': 20,  # 20 downloads per minute
    }
    
    limit = limits.get(operation_type, 5)
    cache_key = f"rate_limit:{client_ip}:{operation_type}"
    requests = cache.get(cache_key, 0)
    
    if requests >= limit:
        logger.warning(f"Rate limit exceeded for IP {client_ip}, operation: {operation_type}")
        return False
    
    cache.set(cache_key, requests + 1, 60)  # 1 minute window
    return True


def validate_and_secure_file(file, request):
    """
    Validate file security and return validation result
    """
    validator = SecureFileValidator()
    validation_result = validator.validate_file(file)
    
    if not validation_result['is_valid']:
        for error in validation_result['errors']:
            logger.warning(f"File validation failed for IP {get_client_ip(request)[0]}: {error}")
            messages.error(request, f"File validation failed: {error}")
        
        # Clean up the file
        if hasattr(file, 'temporary_file_path'):
            try:
                os.unlink(file.temporary_file_path())
            except:
                pass
        
        return None
    
    return validation_result


def secure_file_upload(file, request):
    """
    Secure wrapper around handle_file_upload with validation
    """
    # Rate limiting check
    if not rate_limit_check(request, 'upload'):
        messages.error(request, 'Upload rate limit exceeded. Please try again in a minute.')
        return None
    
    # Validate file
    validation_result = validate_and_secure_file(file, request)
    if not validation_result:
        return None
    
    # Use the existing handle_file_upload
    uploaded = handle_file_upload(file, request)
    
    # Log successful upload
    logger.info(f"Secure file upload: {file.name}, size: {file.size}, "
                f"type: {validation_result['mime_type']}, IP: {get_client_ip(request)[0]}")
    
    return uploaded


def pdf_to_word(request):
    """
    Secure PDF to Word conversion
    """
    if request.method == 'POST':
        # Rate limiting check
        if not rate_limit_check(request, 'conversion'):
            messages.error(request, 'Conversion rate limit exceeded. Please try again later.')
            return render(request, 'converter/pdf_to_word.html', {'form': PDFToWordForm()})
        
        form = PDFToWordForm(request.POST, request.FILES)
        if form.is_valid():
            # Secure file upload
            uploaded = secure_file_upload(request.FILES['file'], request)
            if not uploaded:
                return render(request, 'converter/pdf_to_word.html', {'form': form})
            
            try:
                # Create task
                task = ConversionTask.objects.create(
                    input_file=uploaded,
                    conversion_type='pdf_to_word',
                    status='processing',
                    extra_data={
                        'output_format': request.POST.get('output_format', 'docx'),
                        'preserve_layout': request.POST.get('preserve_layout') == 'on',
                        'enhanced_ocr': request.POST.get('enhanced_ocr') == 'on',
                        'extract_text_only': request.POST.get('extract_text_only') == 'on',
                        'client_ip': get_client_ip(request)[0],
                        'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                    }
                )
                
                # Process conversion
                result = convert_pdf_to_word(
                    uploaded.file.path,
                    output_format=task.extra_data['output_format'],
                    preserve_layout=task.extra_data['preserve_layout'],
                    use_ocr=task.extra_data['enhanced_ocr'],
                    extract_text_only=task.extra_data['extract_text_only']
                )
                
                # Save output
                ext = '.docx' if task.extra_data['output_format'] == 'docx' else '.doc'
                output_filename = f"{os.path.splitext(uploaded.original_filename)[0]}_converted{ext}"
                
                task.output_file.save(output_filename, ContentFile(result.read()))
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.save()
                
                logger.info(f"PDF to Word conversion completed: {uploaded.original_filename}")
                
                return render(request, 'converter/result.html', {
                    'task': task,
                    'filename': output_filename,
                    'format_options': task.extra_data
                })
                
            except Exception as e:
                logger.error(f"PDF to Word conversion failed: {str(e)}", exc_info=True)
                if 'task' in locals():
                    task.status = 'failed'
                    task.completed_at = timezone.now()
                    task.save()
                messages.error(request, 'Conversion failed. Please try again or contact support.')
    
    else:
        form = PDFToWordForm()
    
    return render(request, 'converter/pdf_to_word.html', {'form': form})


def word_to_pdf(request):
    """
    Secure Word to PDF conversion
    """
    if request.method == 'POST':
        # Rate limiting check
        if not rate_limit_check(request, 'conversion'):
            messages.error(request, 'Conversion rate limit exceeded. Please try again later.')
            return render(request, 'converter/word_to_pdf.html', {'form': WordToPDFForm()})
        
        form = WordToPDFForm(request.POST, request.FILES)
        if form.is_valid():
            # Secure file upload
            uploaded = secure_file_upload(request.FILES['file'], request)
            if not uploaded:
                return render(request, 'converter/word_to_pdf.html', {'form': form})
            
            try:
                task = ConversionTask.objects.create(
                    input_file=uploaded,
                    conversion_type='word_to_pdf',
                    status='processing',
                    extra_data={
                        'client_ip': get_client_ip(request)[0],
                        'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                    }
                )
                
                result = convert_word_to_pdf(uploaded.file.path)
                output_filename = f"{os.path.splitext(uploaded.original_filename)[0]}_converted.pdf"
                
                task.output_file.save(output_filename, ContentFile(result.read()))
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.save()
                
                logger.info(f"Word to PDF conversion completed: {uploaded.original_filename}")
                
                return render(request, 'converter/result.html', {
                    'task': task,
                    'filename': output_filename
                })
                
            except Exception as e:
                logger.error(f"Word to PDF conversion failed: {str(e)}", exc_info=True)
                if 'task' in locals():
                    task.status = 'failed'
                    task.completed_at = timezone.now()
                    task.save()
                messages.error(request, 'Conversion failed. Please try again or contact support.')
    
    else:
        form = WordToPDFForm()
    
    return render(request, 'converter/word_to_pdf.html', {'form': form})


def merge_pdf(request):
    """
    Secure PDF merging
    """
    if request.method == 'POST':
        # Rate limiting check
        if not rate_limit_check(request, 'conversion'):
            messages.error(request, 'Conversion rate limit exceeded. Please try again later.')
            return render(request, 'converter/merge_pdf.html', {'form': MergePDFForm()})
        
        form = MergePDFForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data['files']
            
            # Validate minimum files
            if len(files) < 2:
                messages.error(request, 'Please select at least 2 PDF files to merge.')
                return render(request, 'converter/merge_pdf.html', {'form': form})
            
            # Validate maximum files
            if len(files) > 10:
                messages.error(request, 'Maximum 10 files allowed for merging.')
                return render(request, 'converter/merge_pdf.html', {'form': form})
            
            uploaded_files = []
            
            # Secure upload all files
            for file in files:
                uploaded = secure_file_upload(file, request)
                if not uploaded:
                    # Clean up already uploaded files
                    for uf in uploaded_files:
                        uf.delete()
                    return render(request, 'converter/merge_pdf.html', {'form': form})
                uploaded_files.append(uploaded)
            
            try:
                # Get file paths - ensure they exist
                file_paths = []
                for uf in uploaded_files:
                    file_path = uf.file.path
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"Uploaded file missing: {file_path}")
                    file_paths.append(file_path)
                
                # Debug logging
                logger.info(f"Merging {len(file_paths)} PDFs: {[os.path.basename(p) for p in file_paths]}")
                
                # Merge PDFs
                result = merge_pdfs(file_paths)
                
                output_filename = f"merged_{uuid.uuid4().hex[:8]}.pdf"
                
                # Create task
                task = ConversionTask.objects.create(
                    input_file=uploaded_files[0],
                    conversion_type='merge_pdf',
                    status='processing',
                    extra_data={
                        'file_count': len(files),
                        'remove_blank_pages': request.POST.get('remove_blank_pages') == 'on',
                        'optimize_size': request.POST.get('optimize_size') == 'on',
                        'quality': request.POST.get('quality', 'medium'),
                        'client_ip': get_client_ip(request)[0],
                        'merged_files': [uf.id for uf in uploaded_files[1:]],
                    }
                )
                
                # Save output
                task.output_file.save(output_filename, ContentFile(result.read()))
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.save()
                
                logger.info(f"PDF merge completed: {len(files)} files merged, size: {task.output_file.size} bytes")
                
                return render(request, 'converter/result.html', {
                    'task': task,
                    'filename': output_filename,
                    'format_options': task.extra_data
                })
                
            except Exception as e:
                logger.error(f"PDF merge failed: {str(e)}", exc_info=True)
                if 'task' in locals():
                    task.status = 'failed'
                    task.completed_at = timezone.now()
                    task.save()
                messages.error(request, 'Merge failed. Please try again or contact support.')
        
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    else:
        form = MergePDFForm()
    
    return render(request, 'converter/merge_pdf.html', {'form': form})


def split_pdf(request):
    """
    Secure PDF splitting
    """
    if request.method == 'POST':
        # Rate limiting check
        if not rate_limit_check(request, 'conversion'):
            messages.error(request, 'Conversion rate limit exceeded. Please try again later.')
            return render(request, 'converter/split_pdf.html', {'form': SplitPDFForm()})
        
        form = SplitPDFForm(request.POST, request.FILES)
        if form.is_valid():
            # Secure file upload
            uploaded = secure_file_upload(request.FILES['file'], request)
            if not uploaded:
                return render(request, 'converter/split_pdf.html', {'form': form})
            
            split_type = form.cleaned_data['split_type']
            
            try:
                task = ConversionTask.objects.create(
                    input_file=uploaded,
                    conversion_type='split_pdf',
                    status='processing',
                    extra_data={
                        'split_type': split_type,
                        'client_ip': get_client_ip(request)[0],
                    }
                )
                
                # Process based on split type
                if split_type == 'range':
                    pages = form.cleaned_data['pages']
                    # Validate page range
                    if not pages or not all(c.isdigit() or c in ',- ' for c in pages):
                        raise ValidationError("Invalid page range format")
                    result = split_pdf_by_range(uploaded.file.path, pages)
                    task.extra_data['pages'] = pages
                    
                elif split_type == 'every':
                    split_every = form.cleaned_data['split_every']
                    if split_every < 1:
                        raise ValidationError("Split every must be at least 1")
                    result = split_pdf_every_page(uploaded.file.path, split_every)
                    task.extra_data['split_every'] = split_every
                    
                elif split_type == 'count':
                    page_count = form.cleaned_data['page_count']
                    if page_count < 1:
                        raise ValidationError("Page count must be at least 1")
                    result = split_pdf_by_count(uploaded.file.path, page_count)
                    task.extra_data['page_count'] = page_count
                    
                elif split_type == 'custom':
                    custom_split = form.cleaned_data['custom_split']
                    # Validate custom split format
                    if not all(c.isdigit() or c in ',' for c in custom_split):
                        raise ValidationError("Invalid custom split format")
                    result = split_pdf_custom(uploaded.file.path, custom_split)
                    task.extra_data['custom_split'] = custom_split
                
                else:
                    # Default to range splitting
                    pages = form.cleaned_data.get('pages', '1')
                    result = split_pdf_by_range(uploaded.file.path, pages)
                    task.extra_data['pages'] = pages
                
                # Save output
                output_filename = f"split_{uuid.uuid4().hex[:8]}.zip"
                task.output_file.save(output_filename, ContentFile(result.read()))
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.save()
                
                logger.info(f"PDF split completed: {uploaded.original_filename}, type: {split_type}")
                
                return render(request, 'converter/result.html', {
                    'task': task,
                    'filename': output_filename,
                    'format_options': task.extra_data
                })
                
            except Exception as e:
                logger.error(f"PDF split failed: {str(e)}", exc_info=True)
                if 'task' in locals():
                    task.status = 'failed'
                    task.completed_at = timezone.now()
                    task.save()
                messages.error(request, f'Split failed: {str(e)}')
        
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    else:
        form = SplitPDFForm()
    
    return render(request, 'converter/split_pdf.html', {'form': form})


def compress_pdf_view(request):
    """
    Secure PDF compression
    """
    if request.method == 'POST':
        # Rate limiting check
        if not rate_limit_check(request, 'conversion'):
            messages.error(request, 'Conversion rate limit exceeded. Please try again later.')
            return render(request, 'converter/compress_pdf.html', {'form': CompressPDFForm()})
        
        form = CompressPDFForm(request.POST, request.FILES)
        if form.is_valid():
            # Secure file upload
            uploaded = secure_file_upload(request.FILES['file'], request)
            if not uploaded:
                return render(request, 'converter/compress_pdf.html', {'form': form})
            
            # Create secure temporary directory
            temp_dir, temp_path = create_secure_temp_file()
            
            try:
                # Write to temp file
                with open(temp_path, 'wb') as f:
                    for chunk in request.FILES['file'].chunks():
                        f.write(chunk)
                
                # Get form data
                compression_level = form.cleaned_data['compression_level']
                optimize_options = form.cleaned_data.get('optimize_options', '')
                quality_preservation = form.cleaned_data.get('quality_preservation', 'balanced')
                
                # Parse optimize options
                optimize_images = 'images' in optimize_options
                remove_metadata = 'metadata' in optimize_options
                optimize_fonts = 'fonts' in optimize_options
                remove_unused = 'unused' in optimize_options
                
                # Create task
                task = ConversionTask.objects.create(
                    input_file=uploaded,
                    conversion_type='compress_pdf',
                    status='processing',
                    extra_data={
                        'compression_level': compression_level,
                        'optimize_images': optimize_images,
                        'remove_metadata': remove_metadata,
                        'optimize_fonts': optimize_fonts,
                        'remove_unused': remove_unused,
                        'quality_preservation': quality_preservation,
                        'client_ip': get_client_ip(request)[0],
                    }
                )
                
                # Try different compression methods
                try:
                    from .utils import compress_pdf_with_pikepdf, compress_pdf_with_pypdf2
                    compressed_pdf = compress_pdf_with_pikepdf(
                        temp_path,
                        compression_level=compression_level,
                        optimize_images=optimize_images,
                        optimize_fonts=optimize_fonts,
                        remove_metadata=remove_metadata
                    )
                except ImportError:
                    try:
                        compressed_pdf = compress_pdf_with_pypdf2(
                            temp_path,
                            compression_level=compression_level,
                            optimize_images=optimize_images,
                            optimize_fonts=optimize_fonts,
                            remove_metadata=remove_metadata
                        )
                    except ImportError:
                        compressed_pdf = compress_pdf_util(
                            temp_path,
                            compression_level=compression_level,
                            optimize_images=optimize_images,
                            optimize_fonts=optimize_fonts,
                            remove_metadata=remove_metadata
                        )
                
                # Save output
                name, ext = os.path.splitext(uploaded.original_filename)
                output_filename = f"compressed_{name}.pdf"
                task.output_file.save(output_filename, ContentFile(compressed_pdf.read()))
                
                # Calculate stats
                original_size = uploaded.file.size
                compressed_size = task.output_file.size
                reduction_percent = 0
                if original_size > 0:
                    reduction_percent = ((original_size - compressed_size) / original_size) * 100
                
                # Update task
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.extra_data.update({
                    'reduction_percent': round(reduction_percent, 1),
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'savings': original_size - compressed_size
                })
                task.save()
                
                logger.info(f"PDF compression completed: {uploaded.original_filename}, "
                           f"reduction: {reduction_percent:.1f}%")
                
                # Clean up temp directory
                cleanup_secure_temp(temp_dir)
                
                return render(request, 'converter/result.html', {
                    'task': task,
                    'filename': output_filename,
                    'format_options': task.extra_data,
                })
                
            except Exception as e:
                # Clean up temp directory on error
                if temp_dir and os.path.exists(temp_dir):
                    cleanup_secure_temp(temp_dir)
                
                logger.error(f"PDF compression failed: {str(e)}", exc_info=True)
                if 'task' in locals():
                    task.status = 'failed'
                    task.completed_at = timezone.now()
                    task.save()
                messages.error(request, f"Error compressing PDF: {str(e)}")
                return render(request, 'converter/compress_pdf.html', {'form': form})
    
    else:
        form = CompressPDFForm()
    
    return render(request, 'converter/compress_pdf.html', {'form': form})


def excel_to_pdf(request):
    """
    Secure Excel to PDF conversion
    """
    if request.method == 'POST':
        # Rate limiting check
        if not rate_limit_check(request, 'conversion'):
            messages.error(request, 'Conversion rate limit exceeded. Please try again later.')
            return render(request, 'converter/excel_to_pdf.html', {'form': ExcelToPDFForm()})
        
        form = ExcelToPDFForm(request.POST, request.FILES)
        if form.is_valid():
            # Secure file upload
            uploaded = secure_file_upload(request.FILES['file'], request)
            if not uploaded:
                return render(request, 'converter/excel_to_pdf.html', {'form': form})
            
            try:
                # Get options
                include_gridlines = 'gridlines' in request.POST.getlist('options[]')
                fit_to_page = 'fit' in request.POST.getlist('options[]')
                include_headers = 'headers' in request.POST.getlist('options[]')
                worksheet_option = request.POST.get('worksheet', 'first')
                
                task = ConversionTask.objects.create(
                    input_file=uploaded,
                    conversion_type='excel_to_pdf',
                    status='processing',
                    extra_data={
                        'include_gridlines': include_gridlines,
                        'fit_to_page': fit_to_page,
                        'include_headers': include_headers,
                        'worksheet_option': worksheet_option,
                        'client_ip': get_client_ip(request)[0],
                    }
                )
                
                # Convert Excel to PDF
                result = convert_excel_to_pdf(uploaded.file.path, include_gridlines)
                output_filename = f"{os.path.splitext(uploaded.original_filename)[0]}_converted.pdf"
                
                task.output_file.save(output_filename, ContentFile(result.read()))
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.save()
                
                logger.info(f"Excel to PDF conversion completed: {uploaded.original_filename}")
                
                return render(request, 'converter/result.html', {
                    'task': task,
                    'filename': output_filename,
                    'format_options': task.extra_data
                })
                
            except Exception as e:
                logger.error(f"Excel to PDF conversion failed: {str(e)}", exc_info=True)
                if 'task' in locals():
                    task.status = 'failed'
                    task.completed_at = timezone.now()
                    task.save()
                messages.error(request, 'Conversion failed. Please try again or contact support.')
    
    else:
        form = ExcelToPDFForm()
    
    return render(request, 'converter/excel_to_pdf.html', {'form': form})


def image_to_pdf(request):
    """
    Secure Image to PDF conversion
    """
    if request.method == 'POST':
        # Rate limiting check
        if not rate_limit_check(request, 'conversion'):
            messages.error(request, 'Conversion rate limit exceeded. Please try again later.')
            return render(request, 'converter/image_to_pdf.html', {'form': ImageToPDFForm()})
        
        # Manual form handling with security
        files = request.FILES.getlist('files')
        page_size = request.POST.get('page_size')
        orientation = request.POST.get('orientation')
        placement = request.POST.get('placement', 'fit')
        add_page_numbers = request.POST.get('add_page_numbers') == 'true'
        
        # Basic validation
        if not files:
            messages.error(request, 'Please select at least one image file.')
            return render(request, 'converter/image_to_pdf.html', {'form': ImageToPDFForm()})
        
        # Limit number of images
        if len(files) > 20:
            messages.error(request, 'Maximum 20 images allowed per conversion.')
            return render(request, 'converter/image_to_pdf.html', {'form': ImageToPDFForm()})
        
        try:
            uploaded_files = []
            uploaded_file_instances = []
            
            # Secure upload all images
            for file in files:
                uploaded = secure_file_upload(file, request)
                if not uploaded:
                    # Clean up already uploaded files
                    for uf in uploaded_file_instances:
                        uf.delete()
                    return render(request, 'converter/image_to_pdf.html', {'form': ImageToPDFForm()})
                
                uploaded_files.append(uploaded.file.path)
                uploaded_file_instances.append(uploaded)
            
            image_count = len(uploaded_files)
            
            # Convert images to PDF
            result = convert_images_to_pdf(
                uploaded_files, 
                page_size, 
                orientation,
                placement,
                add_page_numbers
            )
            
            # Generate filename
            if image_count == 1:
                output_filename = f"{os.path.splitext(files[0].name)[0]}.pdf"
            else:
                output_filename = f"images_collection_{uuid.uuid4().hex[:8]}.pdf"
            
            # Create task
            task = ConversionTask.objects.create(
                input_file=uploaded_file_instances[0],
                conversion_type='image_to_pdf',
                status='processing',
                extra_data={
                    'page_size': page_size,
                    'orientation': orientation,
                    'placement': placement,
                    'add_page_numbers': add_page_numbers,
                    'image_count': image_count,
                    'client_ip': get_client_ip(request)[0],
                    'file_names': [f.name for f in files],
                    'additional_files': [str(uf.id) for uf in uploaded_file_instances[1:]]
                }
            )
            
            # Save output
            task.output_file.save(output_filename, ContentFile(result.read()))
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.save()
            
            logger.info(f"Image to PDF conversion completed: {image_count} images")
            
            return render(request, 'converter/result.html', {
                'task': task,
                'filename': output_filename,
                'format_options': task.extra_data
            })
            
        except Exception as e:
            logger.error(f"Image to PDF conversion failed: {str(e)}", exc_info=True)
            # Clean up uploaded files on error
            for uploaded in uploaded_file_instances:
                if os.path.exists(uploaded.file.path):
                    try:
                        os.remove(uploaded.file.path)
                    except:
                        pass
            messages.error(request, f'Conversion failed: {str(e)}')
    
    else:
        form = ImageToPDFForm()
    
    return render(request, 'converter/image_to_pdf.html', {'form': form})


def download_file(request, task_id):
    """
    Secure file download with rate limiting
    """
    # Rate limiting check
    if not rate_limit_check(request, 'download'):
        messages.error(request, 'Download rate limit exceeded. Please try again in a minute.')
        return redirect('index')
    
    try:
        task = ConversionTask.objects.get(id=task_id)
        
        # Additional security check: verify IP matches (optional)
        client_ip = get_client_ip(request)[0]
        if task.extra_data and task.extra_data.get('client_ip') != client_ip:
            logger.warning(f"Download IP mismatch: task IP {task.extra_data.get('client_ip')}, "
                         f"request IP {client_ip}")
            # You might still allow download, but log it
        
        if task.output_file:
            # Set secure headers
            response = FileResponse(
                task.output_file.open(), 
                as_attachment=True, 
                filename=os.path.basename(task.output_file.name)
            )
            
            # Security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['Content-Security-Policy'] = "default-src 'self'"
            
            logger.info(f"File downloaded: {task.output_file.name}, IP: {client_ip}")
            
            return response
        else:
            messages.error(request, 'No output file found for this task')
            
    except ConversionTask.DoesNotExist:
        logger.warning(f"Download attempt for non-existent task: {task_id}")
        messages.error(request, 'Conversion task not found')
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}", exc_info=True)
        messages.error(request, 'Error downloading file')
    
    return redirect('index')


def conversion_result(request, task_id):
    """
    View conversion result with security
    """
    try:
        task = ConversionTask.objects.get(id=task_id)
        
        # Optional: Verify user/IP matches
        client_ip = get_client_ip(request)[0]
        if task.extra_data and task.extra_data.get('client_ip') != client_ip:
            logger.warning(f"Result view IP mismatch: task IP {task.extra_data.get('client_ip')}, "
                         f"request IP {client_ip}")
        
        return render(request, 'converter/result.html', {'task': task})
    except ConversionTask.DoesNotExist:
        messages.error(request, 'Conversion task not found')
        return redirect('index')