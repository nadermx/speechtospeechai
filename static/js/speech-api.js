/**
 * Speech to Speech AI - API Client
 *
 * JavaScript client for interacting with the Speech AI API endpoints.
 */

const SpeechAPI = {
    // API configuration
    baseUrl: window.API_SERVER || 'https://api.speechtospeechai.com',
    fallbackUrl: 'https://api.imageeditor.ai',

    // Get API key from user session
    getApiKey: function() {
        return window.API_KEY || localStorage.getItem('api_key') || '';
    },

    // Make API request with fallback
    async request(endpoint, options = {}) {
        const apiKey = this.getApiKey();

        if (!apiKey) {
            throw new Error('API key required. Please log in.');
        }

        const defaultHeaders = {
            'Authorization': `Bearer ${apiKey}`
        };

        // Don't set Content-Type for FormData (let browser set boundary)
        if (!(options.body instanceof FormData)) {
            defaultHeaders['Content-Type'] = 'application/json';
        }

        const fetchOptions = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        };

        try {
            // Try primary API server
            const response = await fetch(`${this.baseUrl}${endpoint}`, fetchOptions);
            return await this.handleResponse(response);
        } catch (error) {
            // Fallback to secondary server
            console.warn('Primary API failed, trying fallback:', error.message);
            try {
                const response = await fetch(`${this.fallbackUrl}${endpoint}`, fetchOptions);
                return await this.handleResponse(response);
            } catch (fallbackError) {
                throw new Error('API request failed: ' + fallbackError.message);
            }
        }
    },

    async handleResponse(response) {
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }

        return data;
    },

    /**
     * Text-to-Speech
     *
     * @param {string} text - Text to synthesize
     * @param {Object} options - TTS options
     * @param {string} options.model - TTS model (default: xtts-v2)
     * @param {string} options.voice_id - Voice identifier
     * @param {string} options.language - Language code (default: en)
     * @param {number} options.speed - Speech speed (default: 1.0)
     * @param {File} options.reference_audio - Optional voice reference
     * @returns {Promise<Object>} Job info with uuid
     */
    async textToSpeech(text, options = {}) {
        const formData = new FormData();
        formData.append('text', text);
        formData.append('model', options.model || 'xtts-v2');
        formData.append('voice_id', options.voice_id || 'default');
        formData.append('language', options.language || 'en');
        formData.append('speed', options.speed || 1.0);
        formData.append('format', options.format || 'wav');

        if (options.reference_audio) {
            formData.append('reference_audio', options.reference_audio);
        }

        return this.request('/v1/tts/', {
            method: 'POST',
            body: formData
        });
    },

    /**
     * Voice Cloning
     *
     * @param {File} referenceAudio - Reference audio file (10-30 seconds)
     * @param {string} text - Text to synthesize
     * @param {Object} options - Cloning options
     * @returns {Promise<Object>} Job info with uuid
     */
    async voiceClone(referenceAudio, text, options = {}) {
        const formData = new FormData();
        formData.append('reference_audio', referenceAudio);
        formData.append('text', text);
        formData.append('model', options.model || 'xtts-v2');
        formData.append('language', options.language || 'en');

        return this.request('/v1/voice-clone/', {
            method: 'POST',
            body: formData
        });
    },

    /**
     * Voice Conversion
     *
     * @param {File} sourceAudio - Audio to convert
     * @param {File} targetVoice - Target voice reference
     * @param {Object} options - Conversion options
     * @returns {Promise<Object>} Job info with uuid
     */
    async voiceConvert(sourceAudio, targetVoice, options = {}) {
        const formData = new FormData();
        formData.append('source_audio', sourceAudio);
        formData.append('target_voice', targetVoice);
        formData.append('model', options.model || 'openvoice');
        formData.append('preserve_pitch', options.preserve_pitch || false);

        return this.request('/v1/voice-convert/', {
            method: 'POST',
            body: formData
        });
    },

    /**
     * Speech Translation
     *
     * @param {File} audio - Audio to translate
     * @param {string} targetLanguage - Target language code
     * @param {Object} options - Translation options
     * @returns {Promise<Object>} Job info with uuid
     */
    async speechTranslate(audio, targetLanguage, options = {}) {
        const formData = new FormData();
        formData.append('audio', audio);
        formData.append('target_language', targetLanguage);
        formData.append('source_language', options.source_language || 'auto');
        formData.append('preserve_voice', options.preserve_voice !== false);

        return this.request('/v1/speech-translate/', {
            method: 'POST',
            body: formData
        });
    },

    /**
     * Audio Enhancement
     *
     * @param {File} audio - Audio to enhance
     * @param {Object} options - Enhancement options
     * @returns {Promise<Object>} Job info with uuid
     */
    async audioEnhance(audio, options = {}) {
        const formData = new FormData();
        formData.append('audio', audio);
        formData.append('denoise', options.denoise !== false);
        formData.append('dereverb', options.dereverb || false);
        formData.append('normalize', options.normalize !== false);
        formData.append('voice_enhance', options.voice_enhance !== false);

        return this.request('/v1/audio-enhance/', {
            method: 'POST',
            body: formData
        });
    },

    /**
     * Speech-to-Text (Transcription)
     *
     * @param {File} audio - Audio to transcribe
     * @param {Object} options - Transcription options
     * @returns {Promise<Object>} Job info with uuid
     */
    async speechToText(audio, options = {}) {
        const formData = new FormData();
        formData.append('audio', audio);
        formData.append('model', options.model || 'large-v3');
        formData.append('language', options.language || 'auto');

        if (options.diarize) {
            formData.append('diarize', 'true');
        }

        return this.request('/v1/transcribe/', {
            method: 'POST',
            body: formData
        });
    },

    /**
     * Check job status
     *
     * @param {string} uuid - Job UUID
     * @returns {Promise<Object>} Job status and results
     */
    async getResults(uuid) {
        return this.request(`/v1/speech/results/?uuid=${uuid}`, {
            method: 'GET'
        });
    },

    /**
     * Get transcription results
     *
     * @param {string} uuid - Job UUID
     * @returns {Promise<Object>} Transcription results
     */
    async getTranscriptionResults(uuid) {
        return this.request(`/v1/transcribe/results/?uuid=${uuid}`, {
            method: 'GET'
        });
    },

    /**
     * Poll for job completion
     *
     * @param {string} uuid - Job UUID
     * @param {Function} onProgress - Progress callback
     * @param {number} interval - Poll interval in ms (default: 2000)
     * @param {number} timeout - Timeout in ms (default: 300000)
     * @returns {Promise<Object>} Final results
     */
    async pollResults(uuid, onProgress = null, interval = 2000, timeout = 300000) {
        const startTime = Date.now();

        while (Date.now() - startTime < timeout) {
            const result = await this.getResults(uuid);

            if (onProgress) {
                onProgress(result);
            }

            if (result.status === 'completed') {
                return result;
            }

            if (result.status === 'failed') {
                throw new Error(result.error || 'Processing failed');
            }

            // Wait before next poll
            await new Promise(resolve => setTimeout(resolve, interval));
        }

        throw new Error('Processing timeout');
    },

    /**
     * Get available voices
     *
     * @param {string} model - TTS model name
     * @returns {Promise<Object>} Available voices
     */
    async getVoices(model = 'xtts-v2') {
        return this.request(`/v1/speech/voices/?model=${model}`, {
            method: 'GET'
        });
    },

    /**
     * Get supported languages
     *
     * @returns {Promise<Object>} Supported languages
     */
    async getLanguages() {
        return this.request('/v1/speech/languages/', {
            method: 'GET'
        });
    },

    /**
     * Get available models
     *
     * @returns {Promise<Object>} Available models
     */
    async getModels() {
        return this.request('/v1/speech/models/', {
            method: 'GET'
        });
    }
};

// UI Helpers
const SpeechUI = {
    // Show loading state
    showLoading(buttonEl, message = 'Processing...') {
        buttonEl.disabled = true;
        buttonEl.dataset.originalText = buttonEl.innerHTML;
        buttonEl.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${message}`;
    },

    // Hide loading state
    hideLoading(buttonEl) {
        buttonEl.disabled = false;
        buttonEl.innerHTML = buttonEl.dataset.originalText;
    },

    // Show progress
    showProgress(progressEl, status) {
        progressEl.classList.remove('d-none');
        const progressBar = progressEl.querySelector('.progress-bar');
        const statusText = progressEl.querySelector('.status-text');

        if (status === 'queued') {
            progressBar.style.width = '25%';
            statusText.textContent = 'Queued...';
        } else if (status === 'processing') {
            progressBar.style.width = '60%';
            statusText.textContent = 'Processing...';
        } else if (status === 'completed') {
            progressBar.style.width = '100%';
            statusText.textContent = 'Complete!';
        }
    },

    // Show result
    showResult(containerEl, resultUrl, type = 'audio') {
        containerEl.classList.remove('d-none');

        if (type === 'audio') {
            const audioEl = containerEl.querySelector('audio');
            audioEl.src = resultUrl;
            audioEl.load();
        }

        const downloadBtn = containerEl.querySelector('.download-btn');
        if (downloadBtn) {
            downloadBtn.href = resultUrl;
        }
    },

    // Show error
    showError(containerEl, message) {
        containerEl.classList.remove('d-none');
        containerEl.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>${message}
            </div>
        `;
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Format duration
    formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
};

// File upload handler
class FileUploader {
    constructor(dropzoneEl, options = {}) {
        this.dropzone = dropzoneEl;
        this.input = dropzoneEl.querySelector('input[type="file"]') || this.createInput();
        this.onFileSelect = options.onFileSelect || (() => {});
        this.accept = options.accept || 'audio/*';
        this.maxSize = options.maxSize || 500 * 1024 * 1024; // 500MB default

        this.init();
    }

    createInput() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = this.accept;
        input.style.display = 'none';
        this.dropzone.appendChild(input);
        return input;
    }

    init() {
        // Click to upload
        this.dropzone.addEventListener('click', () => this.input.click());

        // File input change
        this.input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFile(e.target.files[0]);
            }
        });

        // Drag and drop
        this.dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.dropzone.classList.add('drag-over');
        });

        this.dropzone.addEventListener('dragleave', () => {
            this.dropzone.classList.remove('drag-over');
        });

        this.dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.dropzone.classList.remove('drag-over');

            if (e.dataTransfer.files.length > 0) {
                this.handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    handleFile(file) {
        // Validate file size
        if (file.size > this.maxSize) {
            alert(`File too large. Maximum size is ${SpeechUI.formatFileSize(this.maxSize)}`);
            return;
        }

        // Validate file type
        if (this.accept && !file.type.match(this.accept.replace('*', '.*'))) {
            alert('Invalid file type');
            return;
        }

        this.onFileSelect(file);
        this.showFileInfo(file);
    }

    showFileInfo(file) {
        const infoEl = this.dropzone.querySelector('.file-info') || this.createInfoEl();
        infoEl.innerHTML = `
            <i class="bi bi-file-earmark-music me-2"></i>
            <span>${file.name}</span>
            <small class="text-muted ms-2">(${SpeechUI.formatFileSize(file.size)})</small>
        `;
        infoEl.classList.remove('d-none');
    }

    createInfoEl() {
        const el = document.createElement('div');
        el.className = 'file-info mt-2 d-none';
        this.dropzone.appendChild(el);
        return el;
    }

    reset() {
        this.input.value = '';
        const infoEl = this.dropzone.querySelector('.file-info');
        if (infoEl) {
            infoEl.classList.add('d-none');
        }
    }
}

// Audio recorder
class AudioRecorder {
    constructor(options = {}) {
        this.onRecordingComplete = options.onRecordingComplete || (() => {});
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
    }

    async start() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(this.stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (e) => {
                this.audioChunks.push(e.data);
            };

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                this.onRecordingComplete(audioBlob);
            };

            this.mediaRecorder.start();
            return true;
        } catch (error) {
            console.error('Recording error:', error);
            alert('Could not access microphone. Please check permissions.');
            return false;
        }
    }

    stop() {
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }

    isRecording() {
        return this.mediaRecorder && this.mediaRecorder.state === 'recording';
    }
}

// Export for use
window.SpeechAPI = SpeechAPI;
window.SpeechUI = SpeechUI;
window.FileUploader = FileUploader;
window.AudioRecorder = AudioRecorder;
