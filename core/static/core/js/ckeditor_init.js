/**
 * CKEditor initialization script
 * This script ensures that CKEditor is properly initialized on the page
 */

document.addEventListener('DOMContentLoaded', function () {
    // Find all CKEditor instances
    const ckeditorElements = document.querySelectorAll('.django_ckeditor_5 textarea');

    if (ckeditorElements.length > 0) {
        console.log('Found CKEditor elements:', ckeditorElements.length);

        // Check if CKEditor is loaded
        if (typeof ClassicEditor !== 'undefined') {
            console.log('CKEditor is loaded');
            initializeEditors();
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
            // Check if this element has been processed
            if (element.getAttribute('data-processed') === '0') {
                element.setAttribute('data-processed', '1');

                try {
                    // Full-featured toolbar configuration
                    const editorConfig = {
                        toolbar: [
                            'heading', '|',
                            'bold', 'italic', 'strikethrough', 'underline', 'removeFormat', '|',
                            'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',
                            'bulletedList', 'numberedList', 'todoList', '|',
                            'outdent', 'indent', '|',
                            'blockQuote', 'insertTable', 'mediaEmbed', 'link', 'imageUpload', '|',
                            'alignment', '|',
                            'undo', 'redo'
                        ],
                        language: {
                            ui: 'en',
                            content: 'ka'
                        },
                        ckfinder: {
                            uploadUrl: '/ckeditor5/upload/'
                        },
                        image: {
                            toolbar: [
                                'imageStyle:inline',
                                'imageStyle:block',
                                'imageStyle:side',
                                '|',
                                'toggleImageCaption',
                                'imageTextAlternative'
                            ]
                        },
                        table: {
                            contentToolbar: [
                                'tableColumn',
                                'tableRow',
                                'mergeTableCells',
                                'tableCellProperties',
                                'tableProperties'
                            ]
                        },
                    };

                    ClassicEditor
                        .create(element, editorConfig)
                        .then(editor => {
                            console.log(`CKEditor ${index} initialized successfully`);

                            // Make sure the editor is visible
                            const editorElement = editor.ui.getEditableElement();
                            if (editorElement) {
                                editorElement.style.minHeight = '400px';
                            }

                            // Make sure toolbar is visible
                            const toolbar = document.querySelector('.ck-toolbar');
                            if (toolbar) {
                                toolbar.style.visibility = 'visible';
                                toolbar.style.opacity = '1';
                                toolbar.style.display = 'flex';
                            }
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