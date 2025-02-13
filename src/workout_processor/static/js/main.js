let videoId = null;

// Handle file upload
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('video-file');
    formData.append('file', fileInput.files[0]);
    
    try {
        // Create XMLHttpRequest to track progress
        const xhr = new XMLHttpRequest();
        
        // Track upload progress
        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
                const percentComplete = (event.loaded / event.total) * 100;
                updateProgress('upload-progress', percentComplete);
            }
        };
        
        // Create promise to handle response
        const response = await new Promise((resolve, reject) => {
            xhr.onload = () => resolve(JSON.parse(xhr.response));
            xhr.onerror = () => reject(xhr.statusText);
            xhr.open('POST', '/api/upload');
            xhr.send(formData);
        });
        
        videoId = response.video_id;
        
        // Show movements section
        document.getElementById('movements-section').style.display = 'block';
    } catch (error) {
        console.error('Upload failed:', error);
    }
});

function updateProgress(elementId, percent) {
    const progressBar = document.getElementById(elementId);
    if (progressBar) {
        progressBar.style.width = `${percent}%`;
    }
}

// Handle movement inputs
document.getElementById('add-movement').addEventListener('click', () => {
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'movement-input';
    input.placeholder = 'Enter movement';
    document.getElementById('movements-list').insertBefore(input, document.getElementById('add-movement'));
});

// Process video
document.getElementById('process-video').addEventListener('click', async () => {
    const movements = Array.from(document.getElementsByClassName('movement-input'))
        .map(input => input.value)
        .filter(value => value.trim() !== '');
    
    // Show processing status
    const processingSection = document.getElementById('processing-status');
    processingSection.style.display = 'block';
    
    try {
        // Send process request
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_id: videoId,
                movements: movements
            })
        });
        
        const result = await response.json();
        displayGifPreviews(result.movements);
        
        // Hide processing status after completion
        processingSection.style.display = 'none';
    } catch (error) {
        console.error('Processing failed:', error);
        alert('Processing failed. Please try again.');
    }
});

// Move this function outside of displayGifPreviews (at the top level of the file)
function replaceGifWithFirstFrame(img) {
    // Create a canvas to capture the first frame
    const canvas = document.createElement('canvas');
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    canvas.style.width = '100%';
    canvas.style.height = 'auto';
    canvas.style.backgroundColor = '#fff';  // Add white background
    
    // Draw the current frame
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#fff';  // Set white background
    ctx.fillRect(0, 0, canvas.width, canvas.height);  // Fill background
    ctx.drawImage(img, 0, 0);
    
    return canvas;
}

// Display GIF previews
function displayGifPreviews(movements) {
    const previewSection = document.getElementById('preview-section');
    const previewsContainer = document.getElementById('gif-previews');
    previewsContainer.innerHTML = '';
    
    for (const [movement, segments] of Object.entries(movements)) {
        const movementDiv = document.createElement('div');
        movementDiv.className = 'movement-preview';
        movementDiv.innerHTML = `<h3>${movement}</h3><div class="segments-container"></div>`;
        const segmentsContainer = movementDiv.querySelector('.segments-container');
        
        segments.forEach((segment, index) => {
            const gifContainer = document.createElement('div');
            gifContainer.className = 'gif-container';
            
            // Create filename without extension
            const fileName = `${movement.replace(' ', '_')}_${(index + 1).toString().padStart(2, '0')}`;
            
            // Create GIF preview with trim controls and checkbox
            gifContainer.innerHTML = `
                <div class="gif-header">
                    <div class="gif-info">
                        <div class="segment-name">${fileName}</div>
                        <div class="time-display">
                            <div class="original-time">Original: ${segment.start_time.toFixed(1)}s - ${segment.end_time.toFixed(1)}s</div>
                            <div class="trim-time">Selected: <span class="trim-values">Full GIF</span></div>
                        </div>
                    </div>
                    <label class="checkbox-container">
                        <input type="checkbox" class="gif-selector">
                        <span class="checkmark"></span>
                    </label>
                </div>
                <div class="gif-preview">
                    <img src="/api/download/${segment.gif_path}" alt="${fileName}">
                    <video style="display: none;" 
                           loop 
                           muted 
                           playsinline 
                           autoplay
                           class="preview-video"></video>
                    <div class="loading-overlay" style="display: none;">
                        <div class="spinner"></div>
                        <div>Generating preview...</div>
                    </div>
                </div>
                <div class="trim-controls">
                    <div class="slider-container">
                        <div class="slider-labels">
                            <span>Start</span>
                            <span>End</span>
                        </div>
                        <div class="slider-track">
                            <input type="range" class="trim-start" min="0" max="1" step="0.1" value="0" disabled>
                            <input type="range" class="trim-end" min="0" max="1" step="0.1" value="1" disabled>
                        </div>
                    </div>
                </div>
            `;
            
            // Add trim control event listeners
            const startSlider = gifContainer.querySelector('.trim-start');
            const endSlider = gifContainer.querySelector('.trim-end');
            const img = gifContainer.querySelector('img');
            const trimValues = gifContainer.querySelector('.trim-values');

            // Store original gif URL
            const originalGifUrl = img.src;
            let currentDuration = 0;

            // Initialize sliders once we know the GIF duration
            img.onload = async () => {
                try {
                    const response = await fetch(`/api/gif-info/${segment.gif_path}`);
                    if (!response.ok) throw new Error('Failed to get GIF info');
                    const gifInfo = await response.json();
                    currentDuration = gifInfo.duration;
                    
                    // Update slider ranges with actual duration
                    startSlider.min = 0;
                    startSlider.max = currentDuration;
                    startSlider.value = 0;
                    startSlider.disabled = false;
                    
                    endSlider.min = 0;
                    endSlider.max = currentDuration;
                    endSlider.value = currentDuration;
                    endSlider.disabled = false;
                } catch (error) {
                    console.error('Failed to get GIF duration:', error);
                }
            };

            // Handle slider changes
            let updateTimeout = null;
            function updateTrim() {
                const start = parseFloat(startSlider.value);
                const end = parseFloat(endSlider.value);
                const loadingOverlay = gifContainer.querySelector('.loading-overlay');
                const video = gifContainer.querySelector('video');
                
                // Update time display in both cases
                if (start === 0 && end === currentDuration) {
                    trimValues.textContent = 'Full GIF';
                    img.style.display = 'block';
                    video.style.display = 'none';
                    video.pause();
                    video.src = '';  // Clear the video source
                    loadingOverlay.style.display = 'none';
                } else {
                    // Update trim values display immediately
                    trimValues.textContent = `${start.toFixed(1)}s - ${end.toFixed(1)}s`;
                    
                    if (updateTimeout) {
                        clearTimeout(updateTimeout);
                    }
                    
                    updateTimeout = setTimeout(() => {
                        loadingOverlay.style.display = 'flex';
                        const trimmedUrl = `${originalGifUrl}?start=${start}&end=${end}&t=${Date.now()}&preview=true`;
                        
                        video.src = trimmedUrl;
                        video.onloadeddata = () => {
                            loadingOverlay.style.display = 'none';
                            img.style.display = 'none';
                            video.style.display = 'block';
                            
                            // Ensure video plays properly
                            const playVideo = async () => {
                                try {
                                    await video.play();
                                } catch (err) {
                                    console.log('Playback failed, retrying...', err);
                                    // Retry playback after a short delay
                                    setTimeout(playVideo, 100);
                                }
                            };
                            playVideo();
                        };
                        
                        video.onerror = () => {
                            console.error('Video failed to load:', video.error);
                            loadingOverlay.style.display = 'none';
                            img.style.display = 'block';
                            video.style.display = 'none';
                        };
                    }, 500);
                }
            }

            // Ensure end slider can't go below start slider
            startSlider.addEventListener('input', () => {
                const startVal = parseFloat(startSlider.value);
                const endVal = parseFloat(endSlider.value);
                if (startVal > endVal) {
                    endSlider.value = startVal;
                }
                updateTrim();
            });

            // Ensure start slider can't go above end slider
            endSlider.addEventListener('input', () => {
                const startVal = parseFloat(startSlider.value);
                const endVal = parseFloat(endSlider.value);
                if (endVal < startVal) {
                    startSlider.value = endVal;
                }
                updateTrim();
            });
            
            // Store gif data for download
            const checkbox = gifContainer.querySelector('.gif-selector');
            checkbox.addEventListener('change', updateDownloadButton);
            
            segmentsContainer.appendChild(gifContainer);
        });
        
        previewsContainer.appendChild(movementDiv);
    }
    
    previewSection.style.display = 'block';
}

// Handle download button state
function updateDownloadButton() {
    const downloadButton = document.getElementById('download-selected');
    const selectedCount = document.querySelectorAll('.gif-selector:checked').length;
    downloadButton.disabled = selectedCount === 0;
}

// Handle downloads
document.getElementById('download-selected').addEventListener('click', async () => {
    console.log('Download button clicked');
    
    const selectedGifs = Array.from(document.querySelectorAll('.gif-selector:checked')).map(checkbox => {
        const container = checkbox.closest('.gif-container');
        const img = container.querySelector('img');
        const startSlider = container.querySelector('.trim-start');
        const endSlider = container.querySelector('.trim-end');
        
        // Get the original URL without any existing trim parameters
        const originalUrl = img.src.split('?')[0];
        
        console.log('Selected GIF:', {
            url: originalUrl,
            start: parseFloat(startSlider.value),
            end: parseFloat(endSlider.value)
        });
        
        return {
            url: originalUrl,
            start: parseFloat(startSlider.value),
            end: parseFloat(endSlider.value)
        };
    });

    console.log('Total selected GIFs:', selectedGifs.length);
    if (selectedGifs.length === 0) return;

    // Show download message
    const downloadMessage = document.getElementById('download-message');
    downloadMessage.style.display = 'block';

    try {
        console.log('Sending download request...');
        // Create zip file of selected GIFs
        const response = await fetch('/api/download-selected', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(selectedGifs)
        });

        console.log('Response status:', response.status);

        if (!response.ok) throw new Error('Download failed');

        // Trigger download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'selected_gifs.zip';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        // Hide download message after a short delay
        setTimeout(() => {
            downloadMessage.style.display = 'none';
        }, 1000);
    } catch (error) {
        console.error('Download failed:', error);
        alert('Failed to download GIFs. Please try again.');
        downloadMessage.style.display = 'none';
    }
}); 