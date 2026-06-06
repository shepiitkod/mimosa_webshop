document.addEventListener('DOMContentLoaded', function () {
    forceMimosaLightAdminTheme();
    initMimosaAdminGradient();
    document.documentElement.classList.add('mimosa-admin-ready');
    initProductFramingEditor();
    enhanceMimosaAdminUi();
    ensureMimosaCopilotOnAdmin();
});

function ensureMimosaCopilotOnAdmin() {
    if (document.getElementById('mimosa-copilot-tab')) {
        return;
    }

    var path = window.location.pathname || '';
    if (path.indexOf('/admin') !== 0) {
        return;
    }

    if (!document.querySelector('link[href*="admin_copilot.css"]')) {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/static/admin_copilot.css?v=20260607-photo-cards';
        document.head.appendChild(link);
    }

    if (!document.querySelector('script[src*="admin_copilot.js"]')) {
        var script = document.createElement('script');
        script.src = '/static/admin_copilot.js?v=20260607-photo-cards';
        script.defer = true;
        document.head.appendChild(script);
    }
}

function forceMimosaLightAdminTheme() {
    localStorage.setItem('theme', 'light');
    document.documentElement.setAttribute('data-theme', 'light');
    document.documentElement.classList.remove('theme-dark');
    document.documentElement.classList.add('theme-light');
}

function initMimosaAdminGradient() {
    const root = document.documentElement;
    let pointerX = 18;
    let pointerY = 12;
    let glow = 0.58;
    let warmth = 0;
    let rafId = 0;

    function scheduleUpdate() {
        if (rafId) return;
        rafId = window.requestAnimationFrame(function () {
            rafId = 0;
            const scrollRange = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
            const scrollProgress = window.scrollY / scrollRange;
            const angle = 118 + scrollProgress * 34 + warmth * 10;

            root.style.setProperty('--mimosa-flow-x', pointerX.toFixed(1) + '%');
            root.style.setProperty('--mimosa-flow-y', pointerY.toFixed(1) + '%');
            root.style.setProperty('--mimosa-flow-angle', angle.toFixed(1) + 'deg');
            root.style.setProperty('--mimosa-flow-glow', glow.toFixed(2));
            root.style.setProperty('--mimosa-flow-warmth', warmth.toFixed(2));
        });
    }

    function pulse(actionClass, nextGlow, nextWarmth) {
        root.classList.add(actionClass);
        glow = nextGlow;
        warmth = nextWarmth;
        scheduleUpdate();

        window.setTimeout(function () {
            root.classList.remove(actionClass);
            glow = 0.58;
            warmth = 0;
            scheduleUpdate();
        }, 900);
    }

    window.addEventListener('pointermove', function (event) {
        pointerX = Math.max(0, Math.min(100, (event.clientX / window.innerWidth) * 100));
        pointerY = Math.max(0, Math.min(100, (event.clientY / window.innerHeight) * 100));
        scheduleUpdate();
    }, { passive: true });

    window.addEventListener('scroll', scheduleUpdate, { passive: true });

    document.addEventListener('pointerdown', function () {
        pulse('mimosa-admin-action-click', 0.78, 0.42);
    });

    document.addEventListener('focusin', function (event) {
        if (!event.target.closest('input, textarea, select, .vTextField, .mimosa-framing-frame')) return;
        pulse('mimosa-admin-action-focus', 0.72, 0.22);
    });

    document.addEventListener('submit', function () {
        pulse('mimosa-admin-action-save', 0.9, 0.62);
    });

    scheduleUpdate();
}

function initProductFramingEditor() {
    var imageFields = [
        { name: 'image',   label: 'Фото 1', x: 'image_focal_x',   y: 'image_focal_y'   },
        { name: 'image_2', label: 'Фото 2', x: 'image_2_focal_x', y: 'image_2_focal_y' },
        { name: 'image_3', label: 'Фото 3', x: 'image_3_focal_x', y: 'image_3_focal_y' },
    ];

    imageFields.forEach(function(field) {
        var fileInput = document.getElementById('id_' + field.name);
        if (!fileInput) return;

        var xInput = document.getElementById('id_' + field.x);
        var yInput = document.getElementById('id_' + field.y);

        var row = fileInput.closest('.form-row') || fileInput.parentElement;
        if (!row || row.dataset.mimosaCard) return;
        row.dataset.mimosaCard = '1';

        if (xInput) xInput.value = normalizePercent(xInput.value || 50);
        if (yInput) yInput.value = normalizePercent(yInput.value || 50);

        // Get existing image URL from Django's "Currently:" link
        var currentLink = Array.from(row.querySelectorAll('a[href]')).find(function(a) {
            return /\.(jpg|jpeg|png|gif|webp|avif)(\?|$)/i.test(a.getAttribute('href') || '');
        }) || row.querySelector('a[href*="/media/"]');
        var currentUrl = currentLink ? currentLink.href : '';

        // Get Django clear checkbox
        var clearCheckbox = row.querySelector('input[type="checkbox"]');

        // Move file input + clear checkbox out of the Django widget (keep in form)
        fileInput.style.cssText = 'position:absolute;opacity:0;width:1px;height:1px;overflow:hidden;pointer-events:none;';
        row.appendChild(fileInput);
        if (clearCheckbox) {
            clearCheckbox.style.display = 'none';
            row.appendChild(clearCheckbox);
        }

        // Hide the original Django widget container
        var innerDiv = row.querySelector(':scope > div');
        if (innerDiv) innerDiv.style.display = 'none';

        // ── Build clean photo card ───────────────────────────────
        var card = document.createElement('div');
        card.className = 'mimosa-photo-card';

        // Preview area
        var preview = document.createElement('div');
        preview.className = 'mimosa-photo-preview' + (currentUrl ? ' has-image' : '');

        if (currentUrl) {
            var img = document.createElement('img');
            img.src = currentUrl;
            img.alt = field.label;
            preview.appendChild(img);
        } else {
            preview.innerHTML = '<div class="mimosa-photo-empty"><span>📷</span><span>' + field.label + '</span></div>';
        }

        // Actions
        var actions = document.createElement('div');
        actions.className = 'mimosa-photo-actions';

        // Label for field
        var fieldLabel = document.createElement('div');
        fieldLabel.className = 'mimosa-photo-field-label';
        fieldLabel.textContent = field.label;

        // Choose / Replace button (label → triggers file input)
        var chooseBtn = document.createElement('label');
        chooseBtn.className = 'mimosa-btn mimosa-btn-choose';
        chooseBtn.htmlFor = 'id_' + field.name;
        chooseBtn.innerHTML = '<span>📁</span> ' + (currentUrl ? 'Заменить' : 'Выбрать фото');

        // Crop button
        var cropBtn = document.createElement('button');
        cropBtn.type = 'button';
        cropBtn.className = 'mimosa-btn mimosa-btn-crop';
        cropBtn.innerHTML = '<span>✂️</span> Обрезать';
        cropBtn.disabled = !currentUrl;

        // Focus/frame button
        var focusBtn = null;
        if (xInput && yInput) {
            focusBtn = document.createElement('button');
            focusBtn.type = 'button';
            focusBtn.className = 'mimosa-btn mimosa-btn-focus';
            focusBtn.innerHTML = '<span>🎯</span> Фокус';
            focusBtn.disabled = !currentUrl;
        }

        // Remove button
        var removeBtn = null;
        if (clearCheckbox) {
            removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'mimosa-btn mimosa-btn-remove';
            removeBtn.innerHTML = '<span>🗑</span> Удалить';
            removeBtn.disabled = !currentUrl;
        }

        actions.appendChild(fieldLabel);
        actions.appendChild(chooseBtn);
        actions.appendChild(cropBtn);
        if (focusBtn) actions.appendChild(focusBtn);
        if (removeBtn) actions.appendChild(removeBtn);

        card.appendChild(preview);
        card.appendChild(actions);
        row.appendChild(card);
        row.classList.add('mimosa-photo-row');

        // ── Helpers ──────────────────────────────────────────────
        var objectUrl = '';

        function getPreviewSrc() {
            var img = preview.querySelector('img');
            return img ? img.src : '';
        }

        function setPreview(src) {
            preview.innerHTML = '';
            var img = document.createElement('img');
            img.src = src;
            img.alt = field.label;
            preview.appendChild(img);
            preview.classList.add('has-image');
        }

        function enableButtons() {
            cropBtn.disabled = false;
            if (focusBtn) focusBtn.disabled = false;
            if (removeBtn) removeBtn.disabled = false;
        }

        // ── Events ───────────────────────────────────────────────

        // New file chosen → preview + auto crop
        fileInput.addEventListener('change', function() {
            if (!fileInput.files || !fileInput.files[0]) return;
            if (objectUrl) URL.revokeObjectURL(objectUrl);
            objectUrl = URL.createObjectURL(fileInput.files[0]);
            setPreview(objectUrl);
            enableButtons();
            chooseBtn.innerHTML = '<span>📁</span> Заменить';

            // Auto-open crop
            openCropModal({
                field: field,
                imageUrl: objectUrl,
                imageFile: fileInput.files[0],
                imageField: fileInput,
            });
        });

        // Crop → works for new AND existing images
        cropBtn.addEventListener('click', function() {
            var src = getPreviewSrc();
            if (!src) { alert('Сначала выберите фото.'); return; }

            // If new file is selected — use it directly
            if (objectUrl && fileInput.files && fileInput.files[0]) {
                openCropModal({
                    field: field, imageUrl: objectUrl,
                    imageFile: fileInput.files[0], imageField: fileInput,
                });
                return;
            }

            // Existing image — fetch as blob then crop
            cropBtn.disabled = true;
            cropBtn.innerHTML = '<span>⏳</span> Загружаю…';
            fetch(src)
                .then(function(r) { return r.blob(); })
                .then(function(blob) {
                    var file = new File([blob], 'photo.jpg', { type: blob.type || 'image/jpeg' });
                    var blobUrl = URL.createObjectURL(blob);
                    openCropModal({
                        field: field, imageUrl: blobUrl,
                        imageFile: file, imageField: fileInput,
                    });
                    cropBtn.disabled = false;
                    cropBtn.innerHTML = '<span>✂️</span> Обрезать';
                })
                .catch(function() {
                    cropBtn.disabled = false;
                    cropBtn.innerHTML = '<span>✂️</span> Обрезать';
                    alert('Не удалось загрузить фото для обрезки.');
                });
        });

        // Focus / focal point
        if (focusBtn) {
            focusBtn.addEventListener('click', function() {
                var src = getPreviewSrc();
                if (!src) return;
                openFramingModal({ field: field, imageUrl: src, xInput: xInput, yInput: yInput, trigger: focusBtn });
            });
        }

        // Remove
        if (removeBtn && clearCheckbox) {
            removeBtn.addEventListener('click', function() {
                if (!confirm('Удалить фото «' + field.label + '»?')) return;
                clearCheckbox.checked = true;
                preview.innerHTML = '<div class="mimosa-photo-empty"><span>🗑</span><span>Удалится при сохранении</span></div>';
                preview.classList.remove('has-image');
                cropBtn.disabled = true;
                if (focusBtn) focusBtn.disabled = true;
                removeBtn.disabled = true;
                chooseBtn.innerHTML = '<span>📁</span> Выбрать фото';
            });
        }
    });

    document.body.classList.add('mimosa-framing-ready');
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
