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
        // Start progress event stream
        const eventSource = new EventSource(`/api/progress/${videoId}`);
        
        // Handle connection opened
        eventSource.onopen = () => {
            console.log('SSE connection opened');
        };
        
        // Handle messages
        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('Progress update:', data); // Debug log
                
                if (data.step && typeof data.progress === 'number') {
                    const progressBar = document.querySelector(`#${data.step}-progress`);
                    if (progressBar) {
                        progressBar.style.width = `${data.progress}%`;
                        
                        // Add processing class to status item
                        const statusItem = progressBar.closest('.status-item');
                        statusItem.classList.add('processing');
                        
                        if (data.progress === 100) {
                            statusItem.classList.remove('processing');
                            statusItem.classList.add('completed');
                        }
                    }
                }
            } catch (error) {
                console.error('Error parsing progress data:', error);
            }
        };
        
        // Handle errors
        eventSource.onerror = (error) => {
            console.error('SSE error:', error);
            eventSource.close();
        };
        
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
        
        // Close event stream
        eventSource.close();
        
        // Hide processing status after completion
        setTimeout(() => {
            processingSection.style.display = 'none';
        }, 2000);
    } catch (error) {
        console.error('Processing failed:', error);
        alert('Processing failed. Please try again.');
    }
});

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
                            <span>Original Segment: ${segment.start_time.toFixed(1)}s - ${segment.end_time.toFixed(1)}s</span>
                        </div>
                    </div>
                    <label class="checkbox-container">
                        <input type="checkbox" class="gif-selector">
                        <span class="checkmark"></span>
                    </label>
                </div>
                <div class="gif-preview">
                    <img src="/api/download/${segment.gif_path}" alt="${fileName}">
                </div>
                <div class="trim-controls">
                    <div class="slider-labels">
                        <span>Start</span>
                        <span>End</span>
                    </div>
                    <input type="range" class="trim-start" min="0" max="1" step="0.1" value="0" disabled>
                    <input type="range" class="trim-end" min="0" max="1" step="0.1" value="1" disabled>
                </div>
            `;
            
            // Add trim control event listeners
            const startSlider = gifContainer.querySelector('.trim-start');
            const endSlider = gifContainer.querySelector('.trim-end');
            const img = gifContainer.querySelector('img');

            // Store original gif URL
            const originalGifUrl = img.src;

            // Initialize sliders once we know the GIF duration
            img.onload = async () => {
                try {
                    // Get GIF duration from server
                    const response = await fetch(`/api/gif-info/${segment.gif_path}`);
                    if (!response.ok) throw new Error('Failed to get GIF info');
                    const gifInfo = await response.json();
                    const duration = gifInfo.duration;
                    
                    // Update slider ranges with actual duration
                    startSlider.min = 0;
                    startSlider.max = duration;
                    startSlider.value = 0;
                    startSlider.disabled = false;
                    
                    endSlider.min = 0;
                    endSlider.max = duration;
                    endSlider.value = duration;
                    endSlider.disabled = false;
                } catch (error) {
                    console.error('Failed to get GIF duration:', error);
                }
            };

            // Handle slider changes
            function updateTrim() {
                const start = parseFloat(startSlider.value);
                const end = parseFloat(endSlider.value);
                
                // Add a small delay before updating the GIF to prevent too many requests
                if (updateTrim.timeout) {
                    clearTimeout(updateTrim.timeout);
                }
                updateTrim.timeout = setTimeout(() => {
                    // Update GIF preview with trimmed version
                    const trimmedUrl = `${originalGifUrl}?start=${start}&end=${end}`;
                    img.src = trimmedUrl;
                }, 200);  // 200ms delay
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

    if (selectedGifs.length === 0) return;

    console.log('Sending download request:', selectedGifs);

    try {
        // Create zip file of selected GIFs
        const response = await fetch('/api/download-selected', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(selectedGifs)
        });

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
    } catch (error) {
        console.error('Download failed:', error);
        alert('Failed to download GIFs. Please try again.');
    }
}); 