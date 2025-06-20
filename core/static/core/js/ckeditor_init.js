/**
 * CKEditor initialization script
 * This script ensures that CKEditor is properly initialized on the page
 */

document.addEventListener('DOMContentLoaded', function () {
    // Find all CKEditor instances
    const ckeditorElements = document.querySelectorAll('.django_ckeditor_5');

    if (ckeditorElements.length > 0) {
        console.log('Found CKEditor elements:', ckeditorElements.length);

        // Check if CKEditor is loaded
        if (typeof ClassicEditor !== 'undefined') {
            console.log('CKEditor is loaded');
        } else {
            console.error('CKEditor is not loaded!');

            // Try to load CKEditor manually if it's not loaded
            const script = document.createElement('script');
            script.src = '/static/django_ckeditor_5/dist/bundle.js';
            script.onload = function () {
                console.log('CKEditor loaded manually');
                initializeEditors();
            };
            document.head.appendChild(script);
        }
    }

    function initializeEditors() {
        ckeditorElements.forEach(function (element, index) {
            // Check if this element already has a CKEditor instance
            if (!element.classList.contains('ck-editor__editable')) {
                try {
                    ClassicEditor
                        .create(element, {
                            toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote'],
                            language: {
                                ui: 'en',
                                content: 'ka'
                            }
                        })
                        .then(editor => {
                            console.log(`CKEditor ${index} initialized`);
                        })
                        .catch(error => {
                            console.error(`CKEditor ${index} initialization failed:`, error);
                        });
                } catch (e) {
                    console.error('Error initializing CKEditor:', e);
                }
            }
        });
    }
}); 