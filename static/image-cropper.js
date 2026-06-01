/**
 * Image Cropper Component
 * Provides visual cropping interface for product images in the admin panel
 */

class ImageCropper {
  constructor(options = {}) {
    this.canvas = null;
    this.ctx = null;
    this.image = null;
    this.imageUrl = null;
    this.isDragging = false;
    this.dragOffset = { x: 0, y: 0 };
    this.scale = 1; // Canvas to image coordinates scale
    
    // Crop box state
    this.cropBox = {
      x: 0,
      y: 0,
      width: 100,
      height: 100,
      minWidth: 20,
      minHeight: 20,
    };
    
    // Drag handles state
    this.dragHandle = null; // 'move', 'nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w'
    
    // Options
    this.options = {
      aspectRatio: null, // null = free aspect, or number like 4/3
      minWidth: options.minWidth || 20,
      minHeight: options.minHeight || 20,
      ...options,
    };
    
    this.onCropChange = options.onCropChange || null;
  }
  
  /**
   * Initialize cropper with canvas and image URL
   */
  async initialize(canvasElement, imageUrl) {
    this.canvas = canvasElement;
    this.ctx = this.canvas.getContext('2d');
    this.imageUrl = imageUrl;
    
    // Load image
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        this.image = img;
        this.fitCanvasToImage();
        this.initializeCropBox();
        this.draw();
        resolve();
      };
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = imageUrl;
    });
  }
  
  /**
   * Fit canvas to image dimensions
   */
  fitCanvasToImage() {
    if (!this.image) return;
    
    // Get parent container dimensions
    const parent = this.canvas.parentElement;
    const maxWidth = parent?.clientWidth || 500;
    const maxHeight = parent?.clientHeight || 500;
    
    // Calculate scale to fit image in container
    const imageAspect = this.image.width / this.image.height;
    let width = Math.min(this.image.width, maxWidth);
    let height = width / imageAspect;
    
    if (height > maxHeight) {
      height = maxHeight;
      width = height * imageAspect;
    }
    
    this.canvas.width = width;
    this.canvas.height = height;
    this.scale = this.image.width / width; // Scale factor for converting canvas coords to image coords
  }
  
  /**
   * Initialize crop box to fit the image
   */
  initializeCropBox() {
    if (!this.image) return;
    
    // Start with full image, then apply aspect ratio if set
    this.cropBox.x = 0;
    this.cropBox.y = 0;
    this.cropBox.width = this.canvas.width;
    this.cropBox.height = this.canvas.height;
    
    if (this.options.aspectRatio) {
      this.constrainToAspectRatio();
    }
  }
  
  /**
   * Constrain crop box to aspect ratio
   */
  constrainToAspectRatio() {
    if (!this.options.aspectRatio) return;
    
    const aspect = this.options.aspectRatio;
    const { x, y, width, height } = this.cropBox;
    
    // Adjust height based on width and aspect ratio
    let newHeight = width / aspect;
    
    if (newHeight > height) {
      newHeight = height;
      this.cropBox.width = newHeight * aspect;
    }
    
    this.cropBox.height = newHeight;
    
    // Keep crop box within canvas bounds
    if (this.cropBox.x + this.cropBox.width > this.canvas.width) {
      this.cropBox.x = Math.max(0, this.canvas.width - this.cropBox.width);
    }
    if (this.cropBox.y + this.cropBox.height > this.canvas.height) {
      this.cropBox.y = Math.max(0, this.canvas.height - this.cropBox.height);
    }
  }
  
  /**
   * Get coordinates in image space (not canvas space)
   */
  getImageCoordinates() {
    return {
      x: Math.round(this.cropBox.x * this.scale),
      y: Math.round(this.cropBox.y * this.scale),
      width: Math.round(this.cropBox.width * this.scale),
      height: Math.round(this.cropBox.height * this.scale),
    };
  }
  
  /**
   * Draw canvas with image and crop overlay
   */
  draw() {
    if (!this.ctx || !this.image) return;
    
    // Draw full image
    this.ctx.drawImage(this.image, 0, 0, this.canvas.width, this.canvas.height);
    
    // Draw darkened area outside crop box
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    
    // Top
    this.ctx.fillRect(0, 0, this.canvas.width, this.cropBox.y);
    
    // Bottom
    this.ctx.fillRect(0, this.cropBox.y + this.cropBox.height, 
                      this.canvas.width, 
                      this.canvas.height - this.cropBox.y - this.cropBox.height);
    
    // Left
    this.ctx.fillRect(0, this.cropBox.y, this.cropBox.x, this.cropBox.height);
    
    // Right
    this.ctx.fillRect(this.cropBox.x + this.cropBox.width, this.cropBox.y,
                      this.canvas.width - this.cropBox.x - this.cropBox.width,
                      this.cropBox.height);
    
    // Draw crop box border
    this.ctx.strokeStyle = '#fff';
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(this.cropBox.x, this.cropBox.y, 
                        this.cropBox.width, this.cropBox.height);
    
    // Draw grid lines
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    this.ctx.lineWidth = 1;
    
    const gridX1 = this.cropBox.x + this.cropBox.width / 3;
    const gridX2 = this.cropBox.x + (this.cropBox.width * 2) / 3;
    const gridY1 = this.cropBox.y + this.cropBox.height / 3;
    const gridY2 = this.cropBox.y + (this.cropBox.height * 2) / 3;
    
    this.ctx.beginPath();
    this.ctx.moveTo(gridX1, this.cropBox.y);
    this.ctx.lineTo(gridX1, this.cropBox.y + this.cropBox.height);
    this.ctx.moveTo(gridX2, this.cropBox.y);
    this.ctx.lineTo(gridX2, this.cropBox.y + this.cropBox.height);
    this.ctx.moveTo(this.cropBox.x, gridY1);
    this.ctx.lineTo(this.cropBox.x + this.cropBox.width, gridY1);
    this.ctx.moveTo(this.cropBox.x, gridY2);
    this.ctx.lineTo(this.cropBox.x + this.cropBox.width, gridY2);
    this.ctx.stroke();
    
    // Draw resize handles
    this.drawHandles();
  }
  
  /**
   * Draw resize handles at crop box corners and edges
   */
  drawHandles() {
    const handleSize = 8;
    const corners = [
      { pos: 'nw', x: this.cropBox.x, y: this.cropBox.y },
      { pos: 'ne', x: this.cropBox.x + this.cropBox.width, y: this.cropBox.y },
      { pos: 'sw', x: this.cropBox.x, y: this.cropBox.y + this.cropBox.height },
      { pos: 'se', x: this.cropBox.x + this.cropBox.width, y: this.cropBox.y + this.cropBox.height },
      { pos: 'n', x: this.cropBox.x + this.cropBox.width / 2, y: this.cropBox.y },
      { pos: 's', x: this.cropBox.x + this.cropBox.width / 2, y: this.cropBox.y + this.cropBox.height },
      { pos: 'w', x: this.cropBox.x, y: this.cropBox.y + this.cropBox.height / 2 },
      { pos: 'e', x: this.cropBox.x + this.cropBox.width, y: this.cropBox.y + this.cropBox.height / 2 },
    ];
    
    this.ctx.fillStyle = '#fff';
    this.ctx.strokeStyle = '#333';
    this.ctx.lineWidth = 1;
    
    corners.forEach(corner => {
      this.ctx.fillRect(corner.x - handleSize / 2, corner.y - handleSize / 2, handleSize, handleSize);
      this.ctx.strokeRect(corner.x - handleSize / 2, corner.y - handleSize / 2, handleSize, handleSize);
    });
  }
  
  /**
   * Get which handle is at the given canvas coordinates
   */
  getHandleAtPoint(x, y) {
    const handleSize = 12;
    
    const checks = [
      { pos: 'nw', x: this.cropBox.x, y: this.cropBox.y },
      { pos: 'ne', x: this.cropBox.x + this.cropBox.width, y: this.cropBox.y },
      { pos: 'sw', x: this.cropBox.x, y: this.cropBox.y + this.cropBox.height },
      { pos: 'se', x: this.cropBox.x + this.cropBox.width, y: this.cropBox.y + this.cropBox.height },
      { pos: 'n', x: this.cropBox.x + this.cropBox.width / 2, y: this.cropBox.y },
      { pos: 's', x: this.cropBox.x + this.cropBox.width / 2, y: this.cropBox.y + this.cropBox.height },
      { pos: 'w', x: this.cropBox.x, y: this.cropBox.y + this.cropBox.height / 2 },
      { pos: 'e', x: this.cropBox.x + this.cropBox.width, y: this.cropBox.y + this.cropBox.height / 2 },
    ];
    
    for (let check of checks) {
      if (Math.abs(x - check.x) < handleSize && Math.abs(y - check.y) < handleSize) {
        return check.pos;
      }
    }
    
    // Check if inside crop box (for moving)
    if (x > this.cropBox.x && x < this.cropBox.x + this.cropBox.width &&
        y > this.cropBox.y && y < this.cropBox.y + this.cropBox.height) {
      return 'move';
    }
    
    return null;
  }
  
  /**
   * Update cursor based on drag handle
   */
  updateCursor(handle) {
    const cursorMap = {
      'move': 'grab',
      'nw': 'nwse-resize',
      'ne': 'nesw-resize',
      'sw': 'nesw-resize',
      'se': 'nwse-resize',
      'n': 'ns-resize',
      's': 'ns-resize',
      'e': 'ew-resize',
      'w': 'ew-resize',
    };
    this.canvas.style.cursor = cursorMap[handle] || 'default';
  }
  
  /**
   * Handle mouse down on canvas
   */
  onMouseDown(event) {
    const rect = this.canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    this.dragHandle = this.getHandleAtPoint(x, y);
    if (!this.dragHandle) return;
    
    this.isDragging = true;
    this.dragOffset = { x, y };
    this.updateCursor(this.dragHandle);
  }
  
  /**
   * Handle mouse move on canvas
   */
  onMouseMove(event) {
    const rect = this.canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    if (!this.isDragging) {
      const handle = this.getHandleAtPoint(x, y);
      this.updateCursor(handle);
      return;
    }
    
    const deltaX = x - this.dragOffset.x;
    const deltaY = y - this.dragOffset.y;
    
    this.resizeCropBox(this.dragHandle, deltaX, deltaY);
    
    this.dragOffset = { x, y };
    this.draw();
    this.onCropChangeCallback();
  }
  
  /**
   * Handle mouse up
   */
  onMouseUp() {
    this.isDragging = false;
    this.dragHandle = null;
    this.updateCursor(null);
  }
  
  /**
   * Resize crop box based on drag handle
   */
  resizeCropBox(handle, deltaX, deltaY) {
    const minW = this.options.minWidth;
    const minH = this.options.minHeight;
    
    switch (handle) {
      case 'move':
        // Move entire crop box
        this.cropBox.x = Math.max(0, Math.min(this.canvas.width - this.cropBox.width, this.cropBox.x + deltaX));
        this.cropBox.y = Math.max(0, Math.min(this.canvas.height - this.cropBox.height, this.cropBox.y + deltaY));
        break;
        
      case 'nw':
        this.cropBox.x += deltaX;
        this.cropBox.y += deltaY;
        this.cropBox.width -= deltaX;
        this.cropBox.height -= deltaY;
        break;
        
      case 'ne':
        this.cropBox.y += deltaY;
        this.cropBox.width += deltaX;
        this.cropBox.height -= deltaY;
        break;
        
      case 'sw':
        this.cropBox.x += deltaX;
        this.cropBox.width -= deltaX;
        this.cropBox.height += deltaY;
        break;
        
      case 'se':
        this.cropBox.width += deltaX;
        this.cropBox.height += deltaY;
        break;
        
      case 'n':
        this.cropBox.y += deltaY;
        this.cropBox.height -= deltaY;
        break;
        
      case 's':
        this.cropBox.height += deltaY;
        break;
        
      case 'w':
        this.cropBox.x += deltaX;
        this.cropBox.width -= deltaX;
        break;
        
      case 'e':
        this.cropBox.width += deltaX;
        break;
    }
    
    // Constrain to bounds
    this.constrainToBounds();
    
    // Apply aspect ratio if set
    if (this.options.aspectRatio) {
      this.constrainToAspectRatio();
    }
  }
  
  /**
   * Constrain crop box to canvas bounds
   */
  constrainToBounds() {
    const minW = this.options.minWidth;
    const minH = this.options.minHeight;
    
    // Minimum size
    if (this.cropBox.width < minW) this.cropBox.width = minW;
    if (this.cropBox.height < minH) this.cropBox.height = minH;
    
    // Maximum bounds
    if (this.cropBox.x < 0) this.cropBox.x = 0;
    if (this.cropBox.y < 0) this.cropBox.y = 0;
    if (this.cropBox.x + this.cropBox.width > this.canvas.width) {
      this.cropBox.x = this.canvas.width - this.cropBox.width;
    }
    if (this.cropBox.y + this.cropBox.height > this.canvas.height) {
      this.cropBox.y = this.canvas.height - this.cropBox.height;
    }
  }
  
  /**
   * Call onCropChange callback if provided
   */
  onCropChangeCallback() {
    if (this.onCropChange) {
      const coords = this.getImageCoordinates();
      this.onCropChange(coords);
    }
  }
  
  /**
   * Setup event listeners
   */
  bindEvents() {
    this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
    document.addEventListener('mousemove', (e) => this.onMouseMove(e));
    document.addEventListener('mouseup', () => this.onMouseUp());
    
    // Touch support
    this.canvas.addEventListener('touchstart', (e) => {
      const touch = e.touches[0];
      this.onMouseDown(touch);
    });
    document.addEventListener('touchmove', (e) => {
      const touch = e.touches[0];
      this.onMouseMove(touch);
    });
    document.addEventListener('touchend', () => this.onMouseUp());
  }
  
  /**
   * Get current crop data
   */
  getCropData() {
    return this.getImageCoordinates();
  }
  
  /**
   * Generate a Blob of the cropped image (client-side)
   * @returns {Promise<Blob>} Promise that resolves with the cropped image blob
   */
  /**
   * Generate a Blob of the cropped image at full original resolution (client-side)
   * Crops using original image dimensions, not the scaled canvas size
   * @returns {Promise<Blob>} Promise that resolves with the cropped image blob at original quality
   */
  getCroppedImageBlob(format = 'image/jpeg', quality = 0.95) {
    return new Promise((resolve, reject) => {
      if (!this.image || !this.canvas || !this.ctx) {
        reject(new Error('Image cropper not properly initialized'));
        return;
      }
      
      // Get crop dimensions in CANVAS space (displayed size)
      const canvasX = this.cropBox.x;
      const canvasY = this.cropBox.y;
      const canvasWidth = this.cropBox.width;
      const canvasHeight = this.cropBox.height;
      
      // Calculate scale factor between canvas display size and original image size
      // this.scale stores: original_image.width / canvas.width
      const scaleX = this.image.naturalWidth / this.canvas.width;
      const scaleY = this.image.naturalHeight / this.canvas.height;
      
      // Convert canvas coordinates to ORIGINAL IMAGE coordinates
      const origX = canvasX * scaleX;
      const origY = canvasY * scaleY;
      const origWidth = canvasWidth * scaleX;
      const origHeight = canvasHeight * scaleY;
      
      // Ensure we don't exceed original image bounds
      const finalX = Math.max(0, Math.min(origX, this.image.naturalWidth - 1));
      const finalY = Math.max(0, Math.min(origY, this.image.naturalHeight - 1));
      const finalWidth = Math.min(origWidth, this.image.naturalWidth - finalX);
      const finalHeight = Math.min(origHeight, this.image.naturalHeight - finalY);
      
      // Create a new canvas with ORIGINAL resolution of the cropped area
      const croppedCanvas = document.createElement('canvas');
      croppedCanvas.width = Math.round(finalWidth);
      croppedCanvas.height = Math.round(finalHeight);
      
      const croppedCtx = croppedCanvas.getContext('2d');
      if (!croppedCtx) {
        reject(new Error('Failed to get canvas context'));
        return;
      }
      
      // Draw the cropped portion from the ORIGINAL image
      // Syntax: drawImage(image, sx, sy, sWidth, sHeight, dx, dy, dWidth, dHeight)
      // sx, sy, sWidth, sHeight = source rectangle on original image
      // dx, dy, dWidth, dHeight = destination rectangle on new canvas (0,0 at 1:1 scale)
      try {
        croppedCtx.drawImage(
          this.image,
          finalX, finalY, finalWidth, finalHeight,        // Source coords on original image
          0, 0, finalWidth, finalHeight                    // Destination on new canvas (1:1)
        );
      } catch (error) {
        reject(new Error('Failed to draw image: ' + error.message));
        return;
      }
      
      // Convert to blob at full resolution
      croppedCanvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Failed to create blob from canvas'));
          }
        },
        format,
        quality
      );
    });
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ImageCropper;
}
