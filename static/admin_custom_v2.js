document.addEventListener('DOMContentLoaded', function () {
    document.documentElement.classList.add('mimosa-admin-ready');
    initProductFramingEditor();
    enhanceMimosaAdminUi();
});

function initProductFramingEditor() {
    const imageFields = [
        { name: 'image', label: 'Photo 1', x: 'image_focal_x', y: 'image_focal_y' },
        { name: 'image_2', label: 'Photo 2', x: 'image_2_focal_x', y: 'image_2_focal_y' },
        { name: 'image_3', label: 'Photo 3', x: 'image_3_focal_x', y: 'image_3_focal_y' },
        { name: 'image_4', label: 'Photo 4', x: 'image_4_focal_x', y: 'image_4_focal_y' },
    ];

    let mountedEditors = 0;

    imageFields.forEach(function (field) {
        const fileInput = document.getElementById('id_' + field.name);
        const xInput = document.getElementById('id_' + field.x);
        const yInput = document.getElementById('id_' + field.y);
        if (!fileInput || !xInput || !yInput) return;

        const row = fileInput.closest('.form-row') || fileInput.parentElement;
        if (!row) return;
        if (row.querySelector('.mimosa-framing-actions')) return;

        xInput.value = normalizePercent(xInput.value || 50);
        yInput.value = normalizePercent(yInput.value || 50);
        row.classList.add('mimosa-gallery-row');

        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'mimosa-framing-button';
        button.textContent = buttonLabel(field.label, xInput.value, yInput.value);

        const cropButton = document.createElement('button');
        cropButton.type = 'button';
        cropButton.className = 'mimosa-framing-button mimosa-crop-button-trigger';
        cropButton.textContent = 'Crop Image';
        cropButton.style.backgroundColor = '#417505';
        cropButton.style.color = 'white';

        const hint = document.createElement('span');
        hint.className = 'mimosa-framing-hint';
        hint.textContent = '4:5 site crop';

        const actions = document.createElement('div');
        actions.className = 'mimosa-framing-actions';
        actions.append(button, cropButton, hint);
        const uploadBlock = fileInput.closest('.file-upload') || fileInput.parentElement || row;
        uploadBlock.insertAdjacentElement('afterend', actions);

        let objectUrl = '';

        function currentSource() {
            if (objectUrl) return objectUrl;
            const currentLink = Array.from(row.querySelectorAll('a[href]')).find(function (link) {
                return /\.(jpg|jpeg|png|gif|webp|avif|ico)(\?|#|$)/i.test(link.getAttribute('href') || link.href);
            });
            return currentLink ? currentLink.href : '';
        }

        function updateButtonState() {
            button.disabled = !currentSource();
            button.textContent = currentSource()
                ? buttonLabel(field.label, xInput.value, yInput.value)
                : field.label + ': choose image first';
            
            cropButton.disabled = !currentSource() && !fileInput.files?.length;
        }

        fileInput.addEventListener('change', function () {
            if (objectUrl) URL.revokeObjectURL(objectUrl);
            objectUrl = '';

            if (fileInput.files && fileInput.files[0]) {
                objectUrl = URL.createObjectURL(fileInput.files[0]);
                updateButtonState();
                openFramingModal({
                    field: field,
                    imageUrl: objectUrl,
                    xInput: xInput,
                    yInput: yInput,
                    trigger: button,
                });
            } else {
                updateButtonState();
            }
        });

        button.addEventListener('click', function () {
            const source = currentSource();
            if (!source) return;

            openFramingModal({
                field: field,
                imageUrl: source,
                xInput: xInput,
                yInput: yInput,
                trigger: button,
            });
        });

        cropButton.addEventListener('click', function () {
            if (!fileInput.files || !fileInput.files[0]) {
                alert('Please upload an image first');
                return;
            }
            
            openCropModal({
                field: field,
                imageUrl: objectUrl || currentSource(),
                imageFile: fileInput.files[0],
                imageField: fileInput,
            });
        });

        updateButtonState();
        mountedEditors += 1;
    });

    if (mountedEditors > 0) {
        document.body.classList.add('mimosa-framing-ready');
    }
}

function openFramingModal(options) {
    const existing = document.querySelector('.mimosa-framing-modal');
    if (existing) existing.remove();

    const initialX = normalizePercent(options.xInput.value || 50);
    const initialY = normalizePercent(options.yInput.value || 50);
    const modal = document.createElement('div');
    modal.className = 'mimosa-framing-modal';
    modal.innerHTML = [
        '<div class="mimosa-framing-dialog" role="dialog" aria-modal="true" aria-labelledby="mimosa-framing-title">',
        '  <div class="mimosa-framing-header">',
        '    <div>',
        '      <h2 id="mimosa-framing-title">Photo framing</h2>',
        '      <p>' + escapeHtml(options.field.label) + '</p>',
        '    </div>',
        '    <button type="button" class="mimosa-framing-close" data-action="close" aria-label="Close">Close</button>',
        '  </div>',
        '  <div class="mimosa-framing-frame" tabindex="0">',
        '    <img src="' + escapeAttribute(options.imageUrl) + '" alt="">',
        '    <span class="mimosa-framing-target" aria-hidden="true"></span>',
        '  </div>',
        '  <div class="mimosa-framing-controls">',
        '    <label>Horizontal <input type="range" min="0" max="100" value="' + initialX + '" data-axis="x"></label>',
        '    <label>Vertical <input type="range" min="0" max="100" value="' + initialY + '" data-axis="y"></label>',
        '  </div>',
        '  <div class="mimosa-framing-presets" aria-label="Framing presets">',
        '    <button type="button" data-preset-x="50" data-preset-y="0">Top</button>',
        '    <button type="button" data-preset-x="50" data-preset-y="50">Center</button>',
        '    <button type="button" data-preset-x="50" data-preset-y="100">Bottom</button>',
        '    <button type="button" data-preset-x="0" data-preset-y="50">Left</button>',
        '    <button type="button" data-preset-x="100" data-preset-y="50">Right</button>',
        '  </div>',
        '  <div class="mimosa-framing-footer">',
        '    <output class="mimosa-framing-output"></output>',
        '    <button type="button" class="mimosa-framing-save" data-action="save">Save framing</button>',
        '  </div>',
        '</div>',
    ].join('');

    document.body.appendChild(modal);

    const frame = modal.querySelector('.mimosa-framing-frame');
    const image = modal.querySelector('img');
    const xRange = modal.querySelector('[data-axis="x"]');
    const yRange = modal.querySelector('[data-axis="y"]');
    const output = modal.querySelector('.mimosa-framing-output');
    const saveButton = modal.querySelector('[data-action="save"]');
    const closeButton = modal.querySelector('[data-action="close"]');
    let isDragging = false;

    function updatePreview() {
        const x = normalizePercent(xRange.value);
        const y = normalizePercent(yRange.value);
        const position = x + '% ' + y + '%';

        image.style.objectPosition = position;
        frame.style.setProperty('--mimosa-frame-x', x + '%');
        frame.style.setProperty('--mimosa-frame-y', y + '%');
        output.value = position;
    }

    function setFromPointer(event) {
        const point = event.touches ? event.touches[0] : event;
        const rect = frame.getBoundingClientRect();
        const x = ((point.clientX - rect.left) / rect.width) * 100;
        const y = ((point.clientY - rect.top) / rect.height) * 100;

        xRange.value = normalizePercent(x);
        yRange.value = normalizePercent(y);
        updatePreview();
    }

    function closeModal() {
        modal.remove();
        document.removeEventListener('keydown', onKeydown);
        if (options.trigger) options.trigger.focus();
    }

    function onKeydown(event) {
        if (event.key === 'Escape') closeModal();
    }

    xRange.addEventListener('input', updatePreview);
    yRange.addEventListener('input', updatePreview);

    frame.addEventListener('pointerdown', function (event) {
        isDragging = true;
        frame.setPointerCapture(event.pointerId);
        setFromPointer(event);
    });

    frame.addEventListener('pointermove', function (event) {
        if (!isDragging) return;
        setFromPointer(event);
    });

    frame.addEventListener('pointerup', function (event) {
        isDragging = false;
        frame.releasePointerCapture(event.pointerId);
    });

    modal.querySelectorAll('[data-preset-x]').forEach(function (presetButton) {
        presetButton.addEventListener('click', function () {
            xRange.value = presetButton.dataset.presetX;
            yRange.value = presetButton.dataset.presetY;
            updatePreview();
        });
    });

    saveButton.addEventListener('click', function () {
        const x = normalizePercent(xRange.value);
        const y = normalizePercent(yRange.value);

        options.xInput.value = x;
        options.yInput.value = y;
        if (options.trigger) options.trigger.textContent = buttonLabel(options.field.label, x, y);
        closeModal();
    });

    closeButton.addEventListener('click', closeModal);
    modal.addEventListener('click', function (event) {
        if (event.target === modal) closeModal();
    });
    document.addEventListener('keydown', onKeydown);

    updatePreview();
    frame.focus();
}

function normalizePercent(value) {
    const number = Number.parseInt(value, 10);
    if (Number.isNaN(number)) return 50;
    return Math.max(0, Math.min(100, number));
}

function buttonLabel(label, x, y) {
    return label + ': edit framing (' + normalizePercent(x) + '% ' + normalizePercent(y) + '%)';
}

function escapeAttribute(value) {
    return String(value).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
}

function escapeHtml(value) {
    return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function enhanceMimosaAdminUi() {
    const content = document.getElementById('content');
    if (!content || document.querySelector('.mimosa-admin-hero')) return;

    const title = content.querySelector('h1');
    if (!title) return;

    const hero = document.createElement('div');
    hero.className = 'mimosa-admin-hero';
    hero.innerHTML = [
        '<div>',
        '  <p class="mimosa-admin-kicker">Mimosa Atelier</p>',
        '  <h1>' + escapeHtml(title.textContent.trim()) + '</h1>',
        '</div>',
        '<div class="mimosa-admin-badge">Admin Studio</div>',
    ].join('');

    title.replaceWith(hero);

    const fieldsets = document.querySelectorAll('.change-form fieldset.module');
    fieldsets.forEach(function (fieldset, index) {
        fieldset.style.setProperty('--mimosa-panel-delay', String(index * 45) + 'ms');
    });
}

/**
 * Open image crop modal with visual cropper
 */
function openCropModal(options) {
    if (typeof ImageCropper === 'undefined') {
        alert('ImageCropper component is not loaded');
        return;
    }
    
    const existing = document.querySelector('.mimosa-crop-modal');
    if (existing) existing.remove();
    
    const modal = document.createElement('div');
    modal.className = 'mimosa-crop-modal';
    modal.innerHTML = [
        '<div class="mimosa-crop-dialog" role="dialog" aria-modal="true" aria-labelledby="mimosa-crop-title">',
        '  <div class="mimosa-crop-header">',
        '    <div>',
        '      <h2 id="mimosa-crop-title">Crop Image</h2>',
        '      <p>' + escapeHtml(options.field.label) + '</p>',
        '    </div>',
        '    <button type="button" class="mimosa-crop-close" data-action="close" aria-label="Close">×</button>',
        '  </div>',
        '  <div style="position: relative;">',
        '    <div class="mimosa-crop-canvas-container">',
        '      <canvas class="mimosa-crop-canvas"></canvas>',
        '      <div class="mimosa-crop-loading"><div class="mimosa-crop-spinner"></div><span>Loading...</span></div>',
        '    </div>',
        '  </div>',
        '  <div class="mimosa-crop-info">',
        '    <div class="mimosa-crop-info-row">',
        '      <div class="mimosa-crop-info-item">',
        '        <span class="mimosa-crop-info-label">X</span>',
        '        <span class="mimosa-crop-info-value" data-crop-x>0</span>',
        '      </div>',
        '      <div class="mimosa-crop-info-item">',
        '        <span class="mimosa-crop-info-label">Y</span>',
        '        <span class="mimosa-crop-info-value" data-crop-y>0</span>',
        '      </div>',
        '      <div class="mimosa-crop-info-item">',
        '        <span class="mimosa-crop-info-label">Width</span>',
        '        <span class="mimosa-crop-info-value" data-crop-w>0</span>',
        '      </div>',
        '      <div class="mimosa-crop-info-item">',
        '        <span class="mimosa-crop-info-label">Height</span>',
        '        <span class="mimosa-crop-info-value" data-crop-h>0</span>',
        '      </div>',
        '    </div>',
        '  </div>',
        '  <div class="mimosa-crop-presets">',
        '    <button type="button" class="mimosa-crop-preset" data-preset="square">Square</button>',
        '    <button type="button" class="mimosa-crop-preset" data-preset="3-4">3:4 (Portrait)</button>',
        '    <button type="button" class="mimosa-crop-preset" data-preset="4-3">4:3 (Landscape)</button>',
        '    <button type="button" class="mimosa-crop-preset" data-preset="16-9">16:9</button>',
        '  </div>',
        '  <div class="mimosa-crop-footer">',
        '    <button type="button" class="mimosa-crop-button mimosa-crop-button-cancel" data-action="cancel">Cancel</button>',
        '    <button type="button" class="mimosa-crop-button mimosa-crop-button-save" data-action="save">Save Crop</button>',
        '  </div>',
        '</div>',
    ].join('');
    
    document.body.appendChild(modal);
    
    const canvas = modal.querySelector('.mimosa-crop-canvas');
    const closeBtn = modal.querySelector('[data-action="close"]');
    const cancelBtn = modal.querySelector('[data-action="cancel"]');
    const saveBtn = modal.querySelector('[data-action="save"]');
    const loading = modal.querySelector('.mimosa-crop-loading');
    const infoX = modal.querySelector('[data-crop-x]');
    const infoY = modal.querySelector('[data-crop-y]');
    const infoW = modal.querySelector('[data-crop-w]');
    const infoH = modal.querySelector('[data-crop-h]');
    
    function closeModal() {
        modal.remove();
        if (cropper) {
            if (cropper.canvas) {
                cropper.canvas.removeEventListener('mousedown', cropper.onMouseDown);
            }
        }
    }
    
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', function(e) {
        if (e.target === modal) closeModal();
    });
    
    // Initialize cropper
    const cropper = new ImageCropper({
        minWidth: 50,
        minHeight: 50,
        onCropChange: function(coords) {
            infoX.textContent = coords.x;
            infoY.textContent = coords.y;
            infoW.textContent = coords.width;
            infoH.textContent = coords.height;
        }
    });
    
    loading.classList.add('show');
    
    cropper.initialize(canvas, options.imageUrl).then(function() {
        loading.classList.remove('show');
        cropper.bindEvents();
        cropper.draw();
        cropper.onCropChangeCallback();
        
        // Preset buttons
        modal.querySelectorAll('[data-preset]').forEach(function(btn) {
            btn.addEventListener('click', function() {
                const preset = btn.dataset.preset;
                const aspect = {
                    'square': 1,
                    '3-4': 3/4,
                    '4-3': 4/3,
                    '16-9': 16/9
                }[preset];
                
                if (aspect) {
                    cropper.options.aspectRatio = aspect;
                    cropper.constrainToAspectRatio();
                    cropper.constrainToBounds();
                    cropper.draw();
                    cropper.onCropChangeCallback();
                    
                    modal.querySelectorAll('[data-preset]').forEach(function(b) {
                        b.classList.remove('active');
                    });
                    btn.classList.add('active');
                }
            });
        });
        
        // Save button
        saveBtn.addEventListener('click', function() {
            saveBtn.disabled = true;
            const loadingSpinner = modal.querySelector('.mimosa-crop-loading');
            loadingSpinner.classList.add('show');
            
            // Get cropped image as blob (client-side)
            cropper.getCroppedImageBlob('image/jpeg', 0.95).then(function(blob) {
                // Create File object from Blob
                const originalFileName = options.imageFile.name;
                const fileNameParts = originalFileName.split('.');
                const fileExt = fileNameParts[fileNameParts.length - 1];
                const croppedFileName = 'cropped_' + Date.now() + '.' + fileExt;
                
                const file = new File([blob], croppedFileName, { type: 'image/jpeg' });
                
                // Use DataTransfer API to update the file input
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                options.imageField.files = dataTransfer.files;
                
                // Trigger change event so Django admin detects the file change
                const changeEvent = new Event('change', { bubbles: true });
                options.imageField.dispatchEvent(changeEvent);
                
                // Close modal
                closeModal();
                loadingSpinner.classList.remove('show');
            }).catch(function(error) {
                alert('Error cropping image: ' + error.message);
                saveBtn.disabled = false;
                loadingSpinner.classList.remove('show');
            });
        });
        
    }).catch(function(error) {
        loading.classList.remove('show');
        alert('Error loading image: ' + error.message);
        closeModal();
    });
}
