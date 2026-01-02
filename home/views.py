"""Views for home app."""
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import ContactMessage
from django.http import HttpResponse
from django.views.decorators.http import require_GET
# Add this import at the top of views.py
from django.utils.safestring import mark_safe
from django.urls import reverse
from datetime import datetime

# Sample blog data - later you can create a Blog model
BLOG_POSTS = [
    {
        'slug': 'convert-pdf-to-word-without-losing-formatting',
        'title': 'How to Convert PDF to Word Without Losing Formatting',
        'date': 'March 15, 2024',
        'excerpt': 'Learn the best practices for converting PDF files to Word documents while preserving formatting, images, and layout.',
        'content': '''
            <h2>Why Formatting Gets Lost in PDF Conversion</h2>
            <p>When converting PDF to Word, several elements can cause formatting issues:</p>
            <ul>
                <li><strong>Font embedding:</strong> PDFs use embedded fonts that may not exist on your system</li>
                <li><strong>Complex layouts:</strong> Multi-column designs, text boxes, and floating images</li>
                <li><strong>Tables and charts:</strong> These often convert as images instead of editable elements</li>
                <li><strong>Headers and footers:</strong> May appear as regular text instead of header/footer sections</li>
            </ul>
            
            <h2>Step-by-Step: Convert PDF to Word Perfectly</h2>
            <h3>Step 1: Choose the Right Tool</h3>
            <p>For best results, use our <a href="/pdf-to-word/">PDF to Word converter</a> which includes:</p>
            <ul>
                <li>Advanced OCR for scanned documents</li>
                <li>Format preservation algorithms</li>
                <li>Batch processing capability</li>
            </ul>
            
            <h3>Step 2: Prepare Your PDF</h3>
            <p>Before converting:</p>
            <ol>
                <li>Ensure text is selectable (not image-only)</li>
                <li>Remove unnecessary pages</li>
                <li>Check file size (under 10MB for best results)</li>
            </ol>
            
            <h3>Step 3: Conversion Settings</h3>
            <p>In our converter, select:</p>
            <div class="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg my-4">
                <code class="text-sm">✓ Preserve formatting<br>✓ Enable OCR (for scanned PDFs)<br>✓ Include images<br>✓ Maintain page layout</code>
            </div>
            
            <h2>Common Problems & Solutions</h2>
            <table class="min-w-full border-collapse border border-gray-300 my-6">
                <thead>
                    <tr class="bg-gray-100">
                        <th class="border p-3 text-left">Problem</th>
                        <th class="border p-3 text-left">Solution</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="border p-3">Text runs together</td>
                        <td class="border p-3">Enable "Text recognition" in advanced settings</td>
                    </tr>
                    <tr>
                        <td class="border p-3">Images missing</td>
                        <td class="border p-3">Check "Extract images" option</td>
                    </tr>
                    <tr>
                        <td class="border p-3">Wrong font</td>
                        <td class="border p-3">Convert to .docx (preserves fonts better than .doc)</td>
                    </tr>
                </tbody>
            </table>
            
            <h2>Pro Tips for Perfect Conversion</h2>
            <div class="bg-yellow-50 border-l-4 border-yellow-500 p-6 my-6">
                <strong>💡 Tip:</strong> Convert complex PDFs in sections. Convert text first, then tables, then images separately.
            </div>
            
            <h2>Conclusion</h2>
            <p>By following these steps and using our optimized conversion tool, you can achieve near-perfect PDF to Word conversions. Remember that extremely complex layouts (like magazine pages) may require some manual cleanup in Word.</p>
            
            <div class="bg-blue-50 p-6 rounded-xl mt-8">
                <h3 class="text-xl font-bold mb-2">Ready to Try?</h3>
                <p>Use our <a href="/pdf-to-word/" class="font-semibold text-blue-700">PDF to Word Converter</a> for free and experience perfect formatting preservation.</p>
            </div>
        ''',
        'read_time': '5 min read'
    },
    {
        'slug': 'compress-pdf-file-size-guide',
        'title': 'How to Compress a PDF to a Specific File Size',
        'date': 'March 14, 2024',
        'excerpt': 'Step-by-step guide to reduce PDF file size without sacrificing quality. Perfect for email attachments and online submissions.',
        'content': '''
            <h2>Why Compress PDF Files?</h2>
            <p>PDF compression is essential for:</p>
            <ul>
                <li>Email attachments (most servers limit to 25MB)</li>
                <li>Website uploads and downloads</li>
                <li>Cloud storage optimization</li>
                <li>Mobile device compatibility</li>
            </ul>
            
            <h2>Understanding PDF Compression Methods</h2>
            <h3>Lossless Compression</h3>
            <p>Preserves all original data quality:</p>
            <ul>
                <li>Best for: Text documents, legal papers</li>
                <li>Compression: 10-30% size reduction</li>
                <li>No quality loss</li>
            </ul>
            
            <h3>Lossy Compression</h3>
            <p>Reduces file size with some quality loss:</p>
            <ul>
                <li>Best for: Image-heavy PDFs, presentations</li>
                <li>Compression: 50-90% size reduction</li>
                <li>Adjustable quality settings</li>
            </ul>
            
            <h2>Step-by-Step Compression Guide</h2>
            
            <h3>Step 1: Analyze Your PDF</h3>
            <p>Before compressing, check:</p>
            <ol>
                <li>Current file size</li>
                <li>Image resolution (300 DPI is standard)</li>
                <li>Number of pages</li>
                <li>Color vs grayscale images</li>
            </ol>
            
            <h3>Step 2: Choose Compression Level</h3>
            <p>Our <a href="/compress-pdf/">PDF Compressor</a> offers three levels:</p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 my-6">
                <div class="bg-green-50 p-4 rounded-lg">
                    <h4 class="font-bold mb-2">Low Compression</h4>
                    <p>20-40% reduction</p>
                    <p>Best for: Print quality</p>
                </div>
                <div class="bg-yellow-50 p-4 rounded-lg">
                    <h4 class="font-bold mb-2">Medium Compression</h4>
                    <p>40-70% reduction</p>
                    <p>Best for: Screen viewing</p>
                </div>
                <div class="bg-red-50 p-4 rounded-lg">
                    <h4 class="font-bold mb-2">High Compression</h4>
                    <p>70-90% reduction</p>
                    <p>Best for: Email attachments</p>
                </div>
            </div>
            
            <h3>Step 3: Target Specific File Size</h3>
            <p>To hit a specific file size (e.g., under 5MB for email):</p>
            <ol>
                <li>Upload your PDF to our compressor</li>
                <li>Select "Custom Size" option</li>
                <li>Enter target size (e.g., 5MB)</li>
                <li>Adjust image quality slider</li>
                <li>Preview before downloading</li>
            </ol>
            
            <h2>Advanced Compression Techniques</h2>
            
            <h3>1. Image Optimization</h3>
            <p>Images are usually the largest component:</p>
            <ul>
                <li>Reduce resolution from 300 DPI to 150 DPI for screen viewing</li>
                <li>Convert color images to grayscale when possible</li>
                <li>Use JPEG compression for photographs</li>
            </ul>
            
            <h3>2. Font Optimization</h3>
            <p>Fonts can significantly increase file size:</p>
            <ul>
                <li>Use standard system fonts when possible</li>
                <li>Subset embedded fonts (include only used characters)</li>
                <li>Remove unused font variants</li>
            </ul>
            
            <h3>3. Object Optimization</h3>
            <p>Other elements to optimize:</p>
            <ul>
                <li>Remove hidden layers and annotations</li>
                <li>Flatten form fields</li>
                <li>Combine duplicate images</li>
            </ul>
            
            <h2>Pro Tips for Maximum Compression</h2>
            <div class="bg-blue-50 border-l-4 border-blue-500 p-6 my-6">
                <p><strong>💡 Tip 1:</strong> Compress in stages. First reduce images, then fonts, then other elements.</p>
                <p><strong>💡 Tip 2:</strong> Always preview compressed file before finalizing.</p>
                <p><strong>💡 Tip 3:</strong> Keep original file until satisfied with compression results.</p>
            </div>
            
            <h2>Common Scenarios & Solutions</h2>
            <table class="min-w-full border-collapse border border-gray-300 my-6">
                <thead>
                    <tr class="bg-gray-100">
                        <th class="border p-3 text-left">Scenario</th>
                        <th class="border p-3 text-left">Recommended Settings</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="border p-3">Email attachment (under 10MB)</td>
                        <td class="border p-3">Medium compression, 150 DPI images</td>
                    </tr>
                    <tr>
                        <td class="border p-3">Website download</td>
                        <td class="border p-3">Low compression, keep 300 DPI for print</td>
                    </tr>
                    <tr>
                        <td class="border p-3">Mobile viewing</td>
                        <td class="border p-3">High compression, 96 DPI images</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="bg-green-50 p-6 rounded-xl mt-8">
                <h3 class="text-xl font-bold mb-2">Ready to Compress Your PDFs?</h3>
                <p>Try our <a href="/compress-pdf/" class="font-semibold text-green-700">PDF Compressor</a> for free with customizable size targets.</p>
            </div>
        ''',
        'read_time': '4 min read'
    },
    {
        'slug': 'is-online-pdf-converter-safe',
        'title': 'Is It Safe to Use an Online PDF Converter?',
        'date': 'March 13, 2024',
        'excerpt': 'Security analysis of online PDF tools. Learn how to protect your sensitive documents while using conversion services.',
        'content': '''
            <h2>Understanding Online PDF Converter Security</h2>
            <p>When uploading documents to any online service, security should be your top priority. Here\'s what you need to know:</p>
            
            <h2>How Reputable PDF Converters Protect Your Files</h2>
            
            <h3>1. Encryption (SSL/TLS)</h3>
            <p>Look for HTTPS in the URL and a padlock icon:</p>
            <ul>
                <li>End-to-end encryption during upload/download</li>
                <li>Secure data transmission</li>
                <li>Protection against interception</li>
            </ul>
            
            <h3>2. Automatic File Deletion</h3>
            <p>Our converter automatically deletes files:</p>
            <ul>
                <li>Immediately after conversion (server-side)</li>
                <li>From temporary storage within 1 hour</li>
                <li>No long-term storage of your documents</li>
            </ul>
            
            <h3>3. No Human Access</h3>
            <p>Automated systems ensure:</p>
            <ul>
                <li>No manual processing of your files</li>
                <li>Automated conversion algorithms</li>
                <li>No employee access to user documents</li>
            </ul>
            
            <h2>Red Flags to Watch For</h2>
            
            <div class="bg-red-50 border-l-4 border-red-500 p-6 my-6">
                <h3 class="font-bold mb-3">⚠️ Warning Signs of Unsafe Converters:</h3>
                <ul class="space-y-2">
                    <li>❌ No HTTPS/SSL encryption</li>
                    <li>❌ Requests for personal information</li>
                    <li>❌ Hidden fees or subscriptions</li>
                    <li>❌ No privacy policy available</li>
                    <li>❌ Requires software download</li>
                </ul>
            </div>
            
            <h2>Security Checklist for Safe PDF Conversion</h2>
            
            <div class="bg-green-50 p-6 rounded-lg my-6">
                <h3 class="font-bold mb-3">✅ Safe Converter Checklist:</h3>
                <ol class="space-y-2">
                    <li><strong>Check for HTTPS:</strong> Ensure the site uses encryption</li>
                    <li><strong>Read Privacy Policy:</strong> Understand data handling practices</li>
                    <li><strong>Verify Auto-Delete:</strong> Confirm files are deleted automatically</li>
                    <li><strong>No Registration Required:</strong> Anonymous conversions are safer</li>
                    <li><strong>Reputable Provider:</strong> Choose established, trusted services</li>
                </ol>
            </div>
            
            <h2>Special Considerations for Sensitive Documents</h2>
            
            <h3>For Highly Confidential Documents:</h3>
            <ul>
                <li><strong>Use offline software</strong> for extremely sensitive files</li>
                <li><strong>Remove metadata</strong> before uploading</li>
                <li><strong>Consider local conversion</strong> for legal/medical documents</li>
                <li><strong>Use encrypted PDFs</strong> and remove password after conversion</li>
            </ul>
            
            <h2>How Our Converter Ensures Your Safety</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 my-8">
                <div class="bg-white border border-gray-200 p-6 rounded-lg">
                    <div class="text-blue-600 text-2xl mb-3">
                        🔒
                    </div>
                    <h4 class="font-bold mb-2">Automatic Deletion</h4>
                    <p>Files deleted within 1 hour of conversion</p>
                </div>
                
                <div class="bg-white border border-gray-200 p-6 rounded-lg">
                    <div class="text-green-600 text-2xl mb-3">
                        🌐
                    </div>
                    <h4 class="font-bold mb-2">SSL Encryption</h4>
                    <p>Bank-level security for all transfers</p>
                </div>
                
                <div class="bg-white border border-gray-200 p-6 rounded-lg">
                    <div class="text-purple-600 text-2xl mb-3">
                        🤖
                    </div>
                    <h4 class="font-bold mb-2">Automated Processing</h4>
                    <p>No human access to your documents</p>
                </div>
                
                <div class="bg-white border border-gray-200 p-6 rounded-lg">
                    <div class="text-red-600 text-2xl mb-3">
                        📜
                    </div>
                    <h4 class="font-bold mb-2">Transparent Policies</h4>
                    <p>Clear privacy policy and terms</p>
                </div>
            </div>
            
            <h2>Best Practices for Secure PDF Conversion</h2>
            
            <h3>Before Uploading:</h3>
            <ol>
                <li>Remove unnecessary personal information</li>
                <li>Consider redacting sensitive sections</li>
                <li>Check document for hidden metadata</li>
            </ol>
            
            <h3>During Conversion:</h3>
            <ol>
                <li>Don\'t leave browser window open</li>
                <li>Download immediately after conversion</li>
                <li>Clear browser cache after downloading</li>
            </ol>
            
            <h3>After Conversion:</h3>
            <ol>
                <li>Verify converted file is correct</li>
                <li>Delete original if no longer needed</li>
                <li>Store sensitive documents securely</li>
            </ol>
            
            <h2>Conclusion: Is Online Conversion Safe?</h2>
            <p><strong>Yes, when using reputable services</strong> like ours that prioritize security. For most documents, online conversion is safe and convenient. For highly sensitive legal or medical documents, consider offline alternatives or additional precautions.</p>
            
            <div class="bg-blue-50 p-6 rounded-xl mt-8">
                <h3 class="text-xl font-bold mb-2">Try Our Secure Converter</h3>
                <p>Experience safe, encrypted PDF conversion with automatic file deletion. <a href="/" class="font-semibold text-blue-700">Try our tools for free</a>.</p>
            </div>
        ''',
        'read_time': '6 min read'
    },
    {
        'slug': 'pdf-vs-docx-differences',
        'title': 'PDF vs DOCX: Key Differences and When to Use Each',
        'date': 'March 12, 2024',
        'excerpt': 'Complete comparison between PDF and DOCX formats. Learn which format is best for your specific needs.',
        'content': '''
            <h2>PDF vs DOCX: Understanding the Core Differences</h2>
            
            <div class="overflow-x-auto my-6">
                <table class="min-w-full border-collapse border border-gray-300">
                    <thead>
                        <tr class="bg-gray-100">
                            <th class="border p-3 text-left">Feature</th>
                            <th class="border p-3 text-left">PDF</th>
                            <th class="border p-3 text-left">DOCX</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="border p-3 font-semibold">Primary Purpose</td>
                            <td class="border p-3">Preserving layout for sharing</td>
                            <td class="border p-3">Editing and collaboration</td>
                        </tr>
                        <tr>
                            <td class="border p-3 font-semibold">Editability</td>
                            <td class="border p-3">Limited (requires special tools)</td>
                            <td class="border p-3">Easy (built for editing)</td>
                        </tr>
                        <tr>
                            <td class="border p-3 font-semibold">Cross-Platform</td>
                            <td class="border p-3">Excellent (looks same everywhere)</td>
                            <td class="border p-3">Good (may have formatting issues)</td>
                        </tr>
                        <tr>
                            <td class="border p-3 font-semibold">File Size</td>
                            <td class="border p-3">Generally larger</td>
                            <td class="border p-3">Generally smaller</td>
                        </tr>
                        <tr>
                            <td class="border p-3 font-semibold">Security</td>
                            <td class="border p-3">Built-in encryption, passwords</td>
                            <td class="border p-3">Basic protection features</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <h2>When to Use PDF Format</h2>
            
            <div class="bg-blue-50 p-6 rounded-lg my-6">
                <h3 class="font-bold mb-3">✅ Best Use Cases for PDF:</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <h4 class="font-semibold mb-2">📄 Official Documents</h4>
                        <ul class="text-sm">
                            <li>Contracts and agreements</li>
                            <li>Legal documents</li>
                            <li>Government forms</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-2">🎨 Design-Intensive Files</h4>
                        <ul class="text-sm">
                            <li>Brochures and flyers</li>
                            <li>Magazine layouts</li>
                            <li>Graphic designs</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-2">📤 Sharing & Distribution</h4>
                        <ul class="text-sm">
                            <li>Email attachments</li>
                            <li>Website downloads</li>
                            <li>Print-ready files</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-2">🔒 Secure Documents</h4>
                        <ul class="text-sm">
                            <li>Password-protected files</li>
                            <li>Digital signatures</li>
                            <li>Confidential reports</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <h2>When to Use DOCX Format</h2>
            
            <div class="bg-green-50 p-6 rounded-lg my-6">
                <h3 class="font-bold mb-3">✅ Best Use Cases for DOCX:</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <h4 class="font-semibold mb-2">✏️ Editable Documents</h4>
                        <ul class="text-sm">
                            <li>Drafts and manuscripts</li>
                            <li>Reports under revision</li>
                            <li>Templates and forms</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-2">👥 Collaboration</h4>
                        <ul class="text-sm">
                            <li>Team projects</li>
                            <li>Shared editing</li>
                            <li>Track changes</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-2">📊 Data-Rich Documents</h4>
                        <ul class="text-sm">
                            <li>Tables and charts</li>
                            <li>Dynamic content</li>
                            <li>Linked data</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-2">📝 Text-Intensive Work</h4>
                        <ul class="text-sm">
                            <li>Novels and books</li>
                            <li>Academic papers</li>
                            <li>Business documents</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <h2>Technical Comparison</h2>
            
            <h3>File Structure</h3>
            <p><strong>PDF:</strong> Fixed-layout format, preserves exact appearance</p>
            <p><strong>DOCX:</strong> Flow-based format, adapts to different displays</p>
            
            <h3>Compression</h3>
            <p><strong>PDF:</strong> Better for mixed content (text + images)</p>
            <p><strong>DOCX:</strong> Better for pure text documents</p>
            
            <h3>Accessibility</h3>
            <p><strong>PDF:</strong> Can be accessible with proper tagging</p>
            <p><strong>DOCX:</strong> Generally more accessible by default</p>
            
            <h2>Conversion Tips Between Formats</h2>
            
            <h3>Converting DOCX to PDF:</h3>
            <ol>
                <li>Use "Save as PDF" in Word for best results</li>
                <li>Check fonts are embedded</li>
                <li>Verify images remain high quality</li>
                <li>Test on different devices</li>
            </ol>
            
            <h3>Converting PDF to DOCX:</h3>
            <ol>
                <li>Use OCR for scanned documents</li>
                <li>Expect some formatting changes</li>
                <li>Check tables and images</li>
                <li>Review converted text accuracy</li>
            </ol>
            
            <h2>Making the Right Choice</h2>
            
            <div class="bg-yellow-50 p-6 rounded-lg my-6">
                <h3 class="font-bold mb-3">Quick Decision Guide:</h3>
                <div class="space-y-4">
                    <div>
                        <p class="font-semibold">Ask yourself:</p>
                        <p>"Will this document need editing?"</p>
                        <p class="text-sm mt-1">Yes → Use DOCX | No → Use PDF</p>
                    </div>
                    <div>
                        <p class="font-semibold">Ask yourself:</p>
                        <p>"Is exact formatting critical?"</p>
                        <p class="text-sm mt-1">Yes → Use PDF | No → Use DOCX</p>
                    </div>
                    <div>
                        <p class="font-semibold">Ask yourself:</p>
                        <p>"Will this be printed or shared widely?"</p>
                        <p class="text-sm mt-1">Yes → Use PDF | No → Use DOCX</p>
                    </div>
                </div>
            </div>
            
            <h2>Conclusion</h2>
            <p>Both PDF and DOCX have their strengths. <strong>PDF excels at preservation</strong> while <strong>DOCX excels at collaboration</strong>. Choose PDF for final versions and sharing, DOCX for works in progress and team editing.</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                <div class="bg-blue-50 p-6 rounded-xl">
                    <h3 class="text-xl font-bold mb-2">Convert to PDF</h3>
                    <p>Need to share a document? <a href="/word-to-pdf/" class="font-semibold text-blue-700">Convert DOCX to PDF</a> for perfect preservation.</p>
                </div>
                <div class="bg-green-50 p-6 rounded-xl">
                    <h3 class="text-xl font-bold mb-2">Convert to DOCX</h3>
                    <p>Need to edit a PDF? <a href="/pdf-to-word/" class="font-semibold text-green-700">Convert PDF to DOCX</a> for easy editing.</p>
                </div>
            </div>
        ''',
        'read_time': '7 min read'
    },
    {
        'slug': 'merge-pdfs-tutorial',
        'title': 'How to Merge PDFs: A Complete Step-by-Step Tutorial',
        'date': 'March 11, 2024',
        'excerpt': 'Learn multiple methods to combine PDF files, rearrange pages, and create professional documents.',
        'content': '''
            <h2>Why Merge PDF Files?</h2>
            <p>Merging PDFs helps you:</p>
            <ul>
                <li>Combine multiple reports into one document</li>
                <li>Create portfolios or presentations</li>
                <li>Organize scanned documents</li>
                <li>Simplify sharing multiple files</li>
                <li>Create professional proposals</li>
            </ul>
            
            <h2>Methods for Merging PDFs</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 my-8">
                <div class="bg-white border border-gray-200 p-6 rounded-lg text-center">
                    <div class="text-3xl mb-3">🌐</div>
                    <h3 class="font-bold mb-2">Online Tools</h3>
                    <p class="text-sm">Quick, no software needed</p>
                    <p class="text-xs mt-2">Best for: One-time merging</p>
                </div>
                
                <div class="bg-white border border-gray-200 p-6 rounded-lg text-center">
                    <div class="text-3xl mb-3">💻</div>
                    <h3 class="font-bold mb-2">Desktop Software</h3>
                    <p class="text-sm">Full control, offline</p>
                    <p class="text-xs mt-2">Best for: Frequent use</p>
                </div>
                
                <div class="bg-white border border-gray-200 p-6 rounded-lg text-center">
                    <div class="text-3xl mb-3">📱</div>
                    <h3 class="font-bold mb-2">Mobile Apps</h3>
                    <p class="text-sm">On-the-go merging</p>
                    <p class="text-xs mt-2">Best for: Mobile users</p>
                </div>
            </div>
            
            <h2>Step-by-Step: Merge PDFs Using Our Online Tool</h2>
            
            <h3>Step 1: Prepare Your PDFs</h3>
            <p>Before merging:</p>
            <ol>
                <li>Organize files in desired order</li>
                <li>Check file sizes (max 10MB each)</li>
                <li>Remove passwords if encrypted</li>
                <li>Name files logically (e.g., "01-Cover.pdf")</li>
            </ol>
            
            <h3>Step 2: Upload Files</h3>
            <p>Using our <a href="/merge-pdf/">PDF Merger</a>:</p>
            <div class="bg-gray-50 p-4 rounded-lg my-4">
                <code class="text-sm">1. Click "Select PDF Files"<br>2. Choose up to 10 files<br>3. Drag to reorder if needed<br>4. Click "Merge PDFs"</code>
            </div>
            
            <h3>Step 3: Arrange Pages</h3>
            <p>Our tool allows you to:</p>
            <ul>
                <li>Drag and drop to reorder files</li>
                <li>Preview each PDF before merging</li>
                <li>Remove unwanted pages</li>
                <li>Rotate pages if needed</li>
            </ul>
            
            <h3>Step 4: Merge and Download</h3>
            <ol>
                <li>Click "Merge Now" button</li>
                <li>Wait for processing (usually under 30 seconds)</li>
                <li>Download merged PDF</li>
                <li>Verify all pages are included</li>
            </ol>
            
            <h2>Advanced Merging Techniques</h2>
            
            <h3>1. Selective Page Merging</h3>
            <p>Merge specific pages instead of entire files:</p>
            <ul>
                <li>Extract only needed pages first</li>
                <li>Use page range selection</li>
                <li>Combine pages from multiple sources</li>
            </ul>
            
            <h3>2. Bookmark Preservation</h3>
            <p>Maintain navigation in merged PDF:</p>
            <ul>
                <li>Keep original bookmarks</li>
                <li>Create new table of contents</li>
                <li>Add page labels for organization</li>
            </ul>
            
            <h3>3. Metadata Management</h3>
            <p>Handle document information:</p>
            <ul>
                <li>Preserve or update author info</li>
                <li>Set new document title</li>
                <li>Add keywords for searchability</li>
            </ul>
            
            <h2>Common Merging Scenarios</h2>
            
            <div class="overflow-x-auto my-6">
                <table class="min-w-full border-collapse border border-gray-300">
                    <thead>
                        <tr class="bg-gray-100">
                            <th class="border p-3 text-left">Scenario</th>
                            <th class="border p-3 text-left">Recommended Approach</th>
                            <th class="border p-3 text-left">Tips</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="border p-3">Business Report</td>
                            <td class="border p-3">Cover + TOC + Chapters + Appendix</td>
                            <td class="border p-3">Add page numbers after merging</td>
                        </tr>
                        <tr>
                            <td class="border p-3">Academic Paper</td>
                            <td class="border p-3">Abstract + Paper + References</td>
                            <td class="border p-3">Check formatting consistency</td>
                        </tr>
                        <tr>
                            <td class="border p-3">Legal Bundle</td>
                            <td class="border p-3">All documents in chronological order</td>
                            <td class="border p-3">Add separator pages between documents</td>
                        </tr>
                        <tr>
                            <td class="border p-3">Portfolio</td>
                            <td class="border p-3">Best work samples + resume</td>
                            <td class="border p-3">Optimize images before merging</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <h2>Pro Tips for Perfect Merging</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 my-8">
                <div class="bg-blue-50 p-6 rounded-lg">
                    <h4 class="font-bold mb-3">🔧 Technical Tips:</h4>
                    <ul class="space-y-2">
                        <li>Use consistent page orientation</li>
                        <li>Check all fonts are embedded</li>
                        <li>Normalize image resolutions</li>
                        <li>Set uniform margins</li>
                    </ul>
                </div>
                
                <div class="bg-green-50 p-6 rounded-lg">
                    <h4 class="font-bold mb-3">📊 Organization Tips:</h4>
                    <ul class="space-y-2">
                        <li>Create a master outline first</li>
                        <li>Number pages after merging</li>
                        <li>Add headers/footers consistently</li>
                        <li>Include table of contents</li>
                    </ul>
                </div>
            </div>
            
            <h2>Troubleshooting Common Issues</h2>
            
            <h3>Problem: File Size Too Large</h3>
            <p><strong>Solution:</strong> Compress images before merging or use our <a href="/compress-pdf/">PDF Compressor</a> after merging.</p>
            
            <h3>Problem: Formatting Lost</h3>
            <p><strong>Solution:</strong> Ensure all PDFs use embedded fonts and check page sizes match.</p>
            
            <h3>Problem: Slow Processing</h3>
            <p><strong>Solution:</strong> Reduce file sizes, split into smaller batches, or try during off-peak hours.</p>
            
            <h2>Security Considerations</h2>
            <p>When merging sensitive documents:</p>
            <ul>
                <li>Use tools with automatic deletion</li>
                <li>Remove metadata if needed</li>
                <li>Add password protection after merging</li>
                <li>Use encrypted connections (HTTPS)</li>
            </ul>
            
            <div class="bg-purple-50 p-8 rounded-xl mt-8 text-center">
                <h3 class="text-2xl font-bold mb-4">Ready to Merge Your PDFs?</h3>
                <p class="mb-6">Combine multiple PDFs into one organized document with our free online tool.</p>
                <a href="/merge-pdf/" class="inline-flex items-center px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    Merge PDFs Now
                </a>
            </div>
        ''',
        'read_time': '5 min read'
    },
    {
        'slug': 'how-to-edit-pdf-files-online',
        'title': 'How to Edit PDF Files Online Without Adobe Acrobat',
        'date': 'March 16, 2024',
        'excerpt': 'Learn how to edit PDF files online for free. Add text, images, signatures, and more without expensive software.',
        'content': '''
            <h2>Why Edit PDFs Online?</h2>
            <p>Traditional PDF editing requires expensive software like Adobe Acrobat Pro. Online editors offer:</p>
            <ul>
                <li>No software installation needed</li>
                <li>Access from any device</li>
                <li>Free or affordable options</li>
                <li>Collaboration features</li>
            </ul>
            
            <h2>What You Can Edit in a PDF</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 my-6">
                <div class="bg-blue-50 p-4 rounded-lg">
                    <h3 class="font-bold mb-2">✓ Text Editing</h3>
                    <p>Add, delete, or modify text in PDF documents</p>
                </div>
                <div class="bg-green-50 p-4 rounded-lg">
                    <h3 class="font-bold mb-2">✓ Image Management</h3>
                    <p>Insert, resize, or replace images</p>
                </div>
                <div class="bg-yellow-50 p-4 rounded-lg">
                    <h3 class="font-bold mb-2">✓ Page Operations</h3>
                    <p>Rotate, delete, or rearrange pages</p>
                </div>
                <div class="bg-purple-50 p-4 rounded-lg">
                    <h3 class="font-bold mb-2">✓ Annotations</h3>
                    <p>Add comments, highlights, and stamps</p>
                </div>
            </div>
            
            <h2>Step-by-Step: Edit a PDF Online</h2>
            
            <h3>Step 1: Choose the Right Tool</h3>
            <p>For basic editing, look for tools that offer:</p>
            <ul>
                <li>Free usage options</li>
                <li>No registration required</li>
                <li>Secure file handling</li>
                <li>Multiple format support</li>
            </ul>
            
            <h3>Step 2: Upload Your PDF</h3>
            <p>Most online editors follow this process:</p>
            <ol>
                <li>Drag and drop your PDF</li>
                <li>Wait for file processing</li>
                <li>Access editing tools</li>
            </ol>
            
            <h3>Step 3: Make Your Edits</h3>
            <p>Common editing features:</p>
            <ul>
                <li><strong>Text Tools:</strong> Click to edit text boxes</li>
                <li><strong>Image Tools:</strong> Upload and position images</li>
                <li><strong>Drawing Tools:</strong> Add shapes and lines</li>
                <li><strong>Signature Tools:</strong> Add digital signatures</li>
            </ul>
            
            <h2>Pro Tips for Better Results</h2>
            <div class="bg-yellow-50 border-l-4 border-yellow-500 p-6 my-6">
                <p><strong>💡 Tip 1:</strong> Always work on a copy of your original PDF</p>
                <p><strong>💡 Tip 2:</strong> Save frequently during editing</p>
                <p><strong>💡 Tip 3:</strong> Check file size after adding images</p>
            </div>
            
            <h2>Security Considerations</h2>
            <p>When editing sensitive documents online:</p>
            <ul>
                <li>Use tools with automatic file deletion</li>
                <li>Check for HTTPS encryption</li>
                <li>Remove sensitive info if possible</li>
                <li>Use strong passwords for protected files</li>
            </ul>
            
            <h2>Conclusion</h2>
            <p>Online PDF editing has become easy and accessible. For most users, free online tools provide all the functionality needed for everyday PDF editing tasks.</p>
            
            <div class="bg-blue-50 p-6 rounded-xl mt-8">
                <h3 class="text-xl font-bold mb-2">Need to Edit a PDF?</h3>
                <p>Try our free online tools for basic PDF editing and conversion needs.</p>
            </div>
        ''',
        'read_time': '5 min read'
    }
]
# Tools data for the tools page
ALL_TOOLS = [
    {'name': 'PDF to Word', 'desc': 'Convert PDF files to editable Word documents', 'icon': 'file-word', 'url': 'pdf_to_word'},
    {'name': 'Word to PDF', 'desc': 'Convert Word documents to PDF format', 'icon': 'file-pdf', 'url': 'word_to_pdf'},
    {'name': 'Merge PDF', 'desc': 'Combine multiple PDF files into one', 'icon': 'copy', 'url': 'merge_pdf'},
    {'name': 'Split PDF', 'desc': 'Split PDF into multiple files', 'icon': 'cut', 'url': 'split_pdf'},
    {'name': 'Compress PDF', 'desc': 'Reduce PDF file size', 'icon': 'compress', 'url': 'compress_pdf'},
    {'name': 'Excel to PDF', 'desc': 'Convert Excel spreadsheets to PDF', 'icon': 'file-excel', 'url': 'excel_to_pdf'},
    {'name': 'Image to PDF', 'desc': 'Convert images to PDF documents', 'icon': 'file-image', 'url': 'image_to_pdf'},
]

def index(request):
    """Home page view."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'Free PDF Converter - Convert, Merge, Split PDF Files Online',
        'description': 'Free online PDF tools to convert, merge, split, and compress PDF files. No registration required.',
        'all_tools': ALL_TOOLS,
        'blog_posts': BLOG_POSTS[:3]  # Show first 3 posts on homepage
    }
    return render(request, 'home/index.html', context)

def blog_list(request):
    context = {
        'posts': BLOG_POSTS,
        'site_name': 'PDF Converter Pro',
        'title': 'Blog & Guides - PDF Conversion Tips & Tutorials',
        'description': 'Learn everything about PDF conversion, compression, editing, and security with our expert guides and tutorials. Free PDF tips.',
        'keywords': 'PDF conversion blog, PDF guides, PDF tutorials, PDF tips, PDF help, learn PDF conversion',
    }
    return render(request, 'home/blog_list.html', context)



def blog_detail(request, slug):
    post = next((p for p in BLOG_POSTS if p['slug'] == slug), None)
    if not post:
        return render(request, '404.html')
    
    # Mark the content as safe HTML
    post = post.copy()  # Create a copy to avoid modifying original
    post['content'] = mark_safe(post['content'])
    
    context = {
        'post': post,
        'site_name': 'PDF Converter Pro',
        'title': f'{post["title"]} - PDF Converter Pro Blog',
        'description': post['excerpt'],
    }
    return render(request, 'home/blog_detail.html', context)


def tools(request):
    """Display all available PDF tools."""
    context = {
        'site_name': 'PDF Converter Pro',
        'title': 'All PDF Tools - Free Online PDF Converter',
        'description': 'Browse all our free PDF tools: PDF to Word, Word to PDF, Merge PDF, Split PDF, Compress PDF, Excel to PDF, Image to PDF.',
        'all_tools': ALL_TOOLS,  # Use ALL_TOOLS, not blog_posts
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

def sitemap_view(request):
    """Generate dynamic sitemap"""
    urls = [
        {'loc': reverse('home'), 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': reverse('tools'), 'priority': '0.9', 'changefreq': 'daily'},
        {'loc': reverse('pdf_to_word'), 'priority': '0.8', 'changefreq': 'weekly'},
        {'loc': reverse('word_to_pdf'), 'priority': '0.8', 'changefreq': 'weekly'},
        {'loc': reverse('merge_pdf'), 'priority': '0.8', 'changefreq': 'weekly'},
        {'loc': reverse('split_pdf'), 'priority': '0.8', 'changefreq': 'weekly'},
        {'loc': reverse('compress_pdf'), 'priority': '0.8', 'changefreq': 'weekly'},
        {'loc': reverse('excel_to_pdf'), 'priority': '0.8', 'changefreq': 'weekly'},
        {'loc': reverse('image_to_pdf'), 'priority': '0.8', 'changefreq': 'weekly'},
        {'loc': reverse('faq'), 'priority': '0.6', 'changefreq': 'monthly'},
        {'loc': reverse('about'), 'priority': '0.5', 'changefreq': 'monthly'},
        {'loc': reverse('contact'), 'priority': '0.4', 'changefreq': 'monthly'},
        {'loc': reverse('terms'), 'priority': '0.3', 'changefreq': 'yearly'},
        {'loc': reverse('privacy'), 'priority': '0.3', 'changefreq': 'yearly'},
    ]
    
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    for url in urls:
        full_url = f"https://pdfconverterpro.onrender.com{url['loc']}"
        xml_content += f'    <url>\n'
        xml_content += f'        <loc>{full_url}</loc>\n'
        xml_content += f'        <lastmod>{today}</lastmod>\n'
        xml_content += f"        <changefreq>{url['changefreq']}</changefreq>\n"
        xml_content += f"        <priority>{url['priority']}</priority>\n"
        xml_content += '    </url>\n'
    
    xml_content += '</urlset>'
    
    return HttpResponse(xml_content, content_type='application/xml')

