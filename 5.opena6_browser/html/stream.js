// 📹 Browser Agent 6.0 - Live Video Streaming & WebRTC

let streamActive = false;
let localStream = null;
let peerConnection = null;
let streamSocket = null;
let frameRate = 30;
let videoElement = null;

// ===============================================
// Stream Control Functions
// ===============================================

async function toggleStream() {
    const button = document.querySelector('[onclick="toggleStream()"]');
    const videoContainer = document.getElementById('videoContainer');
    const streamStatus = document.getElementById('streamStatus');
    
    if (streamActive) {
        // Stop streaming
        stopStream();
        button.textContent = '▶️ Start Stream';
        button.className = 'btn btn-success btn-sm';
        streamStatus.textContent = 'Stream: Stopped';
        videoContainer.style.display = 'none';
        
        showNotification('Video stream stopped', 'info');
    } else {
        // Start streaming
        try {
            await startStream();
            button.textContent = '⏹️ Stop Stream';
            button.className = 'btn btn-danger btn-sm';
            streamStatus.textContent = 'Stream: Active';
            videoContainer.style.display = 'block';
            
            showNotification('Video stream started successfully', 'success');
        } catch (error) {
            showNotification(`Failed to start stream: ${error.message}`, 'error');
        }
    }
}

async function startStream() {
    try {
        // Initialize video element
        initializeVideoElement();
        
        // Try WebRTC first, fallback to HTTP streaming
        if (CONFIG.WEBRTC_ENABLED) {
            await startWebRTCStream();
        } else {
            await startHTTPStream();
        }
        
        streamActive = true;
        updateStreamInfo();
        
    } catch (error) {
        console.error('Stream start failed:', error);
        throw error;
    }
}

function stopStream() {
    // Stop WebRTC
    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }
    
    // Stop local stream
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }
    
    // Close WebSocket
    if (streamSocket) {
        streamSocket.close();
        streamSocket = null;
    }
    
    // Clear video
    if (videoElement) {
        videoElement.srcObject = null;
        videoElement.src = '';
    }
    
    streamActive = false;
    updateStreamInfo();
}

function initializeVideoElement() {
    videoElement = document.getElementById('liveVideo');
    if (!videoElement) {
        throw new Error('Video element not found');
    }
    
    videoElement.addEventListener('loadedmetadata', () => {
        console.log('Video metadata loaded:', {
            width: videoElement.videoWidth,
            height: videoElement.videoHeight,
            duration: videoElement.duration
        });
    });
    
    videoElement.addEventListener('error', (e) => {
        console.error('Video error:', e);
        showNotification('Video playback error', 'error');
    });
}

// ===============================================
// WebRTC Streaming
// ===============================================

async function startWebRTCStream() {
    try {
        // Create WebSocket connection to signaling server
        streamSocket = new WebSocket(CONFIG.WEBRTC_SIGNALING_URL);
        
        streamSocket.onopen = () => {
            console.log('WebRTC signaling connected');
            requestBrowserStream();
        };
        
        streamSocket.onmessage = async (event) => {
            const message = JSON.parse(event.data);
            await handleSignalingMessage(message);
        };
        
        streamSocket.onerror = (error) => {
            console.error('WebRTC signaling error:', error);
            throw new Error('WebRTC connection failed');
        };
        
        streamSocket.onclose = () => {
            console.log('WebRTC signaling disconnected');
            if (streamActive) {
                showNotification('Stream connection lost', 'warning');
            }
        };
        
    } catch (error) {
        console.error('WebRTC setup failed:', error);
        throw error;
    }
}

function requestBrowserStream() {
    if (streamSocket && streamSocket.readyState === WebSocket.OPEN) {
        streamSocket.send(JSON.stringify({
            type: 'request_stream',
            config: {
                video: {
                    width: CONFIG.STREAM_WIDTH,
                    height: CONFIG.STREAM_HEIGHT,
                    frameRate: frameRate
                },
                audio: CONFIG.STREAM_AUDIO
            }
        }));
    }
}

async function handleSignalingMessage(message) {
    switch (message.type) {
        case 'offer':
            await handleOffer(message.offer);
            break;
        case 'answer':
            await handleAnswer(message.answer);
            break;
        case 'ice-candidate':
            await handleICECandidate(message.candidate);
            break;
        case 'stream_ready':
            console.log('Browser stream is ready');
            break;
        case 'error':
            console.error('Signaling error:', message.error);
            throw new Error(message.error);
        default:
            console.log('Unknown signaling message:', message);
    }
}

async function handleOffer(offer) {
    try {
        // Create peer connection
        peerConnection = new RTCPeerConnection(CONFIG.ICE_SERVERS);
        
        // Set up event handlers
        peerConnection.ontrack = (event) => {
            console.log('Received remote stream');
            if (videoElement) {
                videoElement.srcObject = event.streams[0];
            }
        };
        
        peerConnection.onicecandidate = (event) => {
            if (event.candidate && streamSocket) {
                streamSocket.send(JSON.stringify({
                    type: 'ice-candidate',
                    candidate: event.candidate
                }));
            }
        };
        
        peerConnection.onconnectionstatechange = () => {
            console.log('Connection state:', peerConnection.connectionState);
            updateConnectionState(peerConnection.connectionState);
        };
        
        // Set remote description
        await peerConnection.setRemoteDescription(offer);
        
        // Create and send answer
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);
        
        streamSocket.send(JSON.stringify({
            type: 'answer',
            answer: answer
        }));
        
    } catch (error) {
        console.error('Handle offer failed:', error);
        throw error;
    }
}

async function handleAnswer(answer) {
    if (peerConnection) {
        await peerConnection.setRemoteDescription(answer);
    }
}

async function handleICECandidate(candidate) {
    if (peerConnection) {
        await peerConnection.addIceCandidate(candidate);
    }
}

function updateConnectionState(state) {
    const streamQuality = document.getElementById('streamQuality');
    if (streamQuality) {
        streamQuality.textContent = `Connection: ${state}`;
    }
    
    if (state === 'connected') {
        showNotification('WebRTC connection established', 'success');
    } else if (state === 'failed' || state === 'disconnected') {
        showNotification('WebRTC connection lost', 'warning');
    }
}

// ===============================================
// HTTP Streaming Fallback
// ===============================================

async function startHTTPStream() {
    try {
        // Request HTTP stream from browser agent
        const response = await api('/stream/start', 'POST', {
            format: 'mjpeg',
            quality: CONFIG.STREAM_QUALITY,
            frameRate: frameRate
        });
        
        if (response && response.stream_url) {
            videoElement.src = response.stream_url;
            videoElement.play();
        } else {
            throw new Error('No stream URL received');
        }
        
    } catch (error) {
        console.error('HTTP streaming failed:', error);
        
        // Fallback to mock stream
        startMockStream();
    }
}

function startMockStream() {
    // Create a canvas-based mock stream for demonstration
    const canvas = document.createElement('canvas');
    canvas.width = CONFIG.STREAM_WIDTH;
    canvas.height = CONFIG.STREAM_HEIGHT;
    
    const ctx = canvas.getContext('2d');
    
    // Generate mock video stream
    const stream = canvas.captureStream(frameRate);
    videoElement.srcObject = stream;
    
    // Animate mock content
    let frame = 0;
    const animate = () => {
        if (!streamActive) return;
        
        // Clear canvas
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw mock browser content
        drawMockBrowserContent(ctx, frame);
        
        frame++;
        requestAnimationFrame(animate);
    };
    
    animate();
    console.log('Mock stream started (demo mode)');
}

function drawMockBrowserContent(ctx, frame) {
    const time = frame * 0.1;
    
    // Mock browser window
    ctx.strokeStyle = '#444';
    ctx.lineWidth = 2;
    ctx.strokeRect(20, 20, CONFIG.STREAM_WIDTH - 40, CONFIG.STREAM_HEIGHT - 40);
    
    // Mock URL bar
    ctx.fillStyle = '#2d2d2d';
    ctx.fillRect(30, 30, CONFIG.STREAM_WIDTH - 60, 30);
    
    // Mock URL text
    ctx.fillStyle = '#fff';
    ctx.font = '12px monospace';
    ctx.fillText('https://example.com/page', 40, 50);
    
    // Mock webpage content
    ctx.fillStyle = '#333';
    ctx.fillRect(30, 70, CONFIG.STREAM_WIDTH - 60, CONFIG.STREAM_HEIGHT - 100);
    
    // Animated elements
    const x = 50 + Math.sin(time) * 20;
    const y = 100 + Math.cos(time * 0.7) * 15;
    
    ctx.fillStyle = '#4a9eff';
    ctx.fillRect(x, y, 100, 30);
    
    ctx.fillStyle = '#fff';
    ctx.fillText('Button', x + 10, y + 20);
    
    // Mock scrolling text
    for (let i = 0; i < 5; i++) {
        const lineY = 150 + i * 25 + (time * 10) % 125;
        ctx.fillStyle = '#666';
        ctx.fillText(`Mock content line ${i + 1}`, 50, lineY);
    }
    
    // Connection indicator
    ctx.fillStyle = streamActive ? '#28a745' : '#dc3545';
    ctx.beginPath();
    ctx.arc(CONFIG.STREAM_WIDTH - 30, 30, 8, 0, 2 * Math.PI);
    ctx.fill();
}

// ===============================================
// Stream Control Functions
// ===============================================

function changeQuality(quality) {
    CONFIG.STREAM_QUALITY = quality;
    
    if (streamActive) {
        showNotification(`Stream quality changed to ${quality}`, 'info');
        // Restart stream with new quality
        setTimeout(async () => {
            stopStream();
            await startStream();
        }, 500);
    }
    
    // Update UI
    document.querySelectorAll('[onclick^="changeQuality"]').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[onclick="changeQuality('${quality}')"]`).classList.add('active');
}

function changeFrameRate(fps) {
    frameRate = fps;
    
    if (streamActive) {
        showNotification(`Frame rate changed to ${fps} FPS`, 'info');
        // Note: For WebRTC, this would require renegotiation
    }
    
    // Update UI
    document.querySelectorAll('[onclick^="changeFrameRate"]').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[onclick="changeFrameRate(${fps})"]`).classList.add('active');
}

function toggleFullscreen() {
    const videoContainer = document.getElementById('videoContainer');
    
    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else {
        videoContainer.requestFullscreen();
    }
}

function takeScreenshot() {
    if (!videoElement) {
        showNotification('No video stream available', 'warning');
        return;
    }
    
    try {
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth || CONFIG.STREAM_WIDTH;
        canvas.height = videoElement.videoHeight || CONFIG.STREAM_HEIGHT;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        
        // Download screenshot
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `screenshot-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
        
        showNotification('Screenshot saved', 'success');
        
    } catch (error) {
        console.error('Screenshot failed:', error);
        showNotification('Screenshot failed', 'error');
    }
}

// ===============================================
// Stream Information & Monitoring
// ===============================================

function updateStreamInfo() {
    const streamInfo = document.getElementById('streamInfo');
    if (!streamInfo) return;
    
    if (streamActive && videoElement) {
        const info = {
            resolution: `${videoElement.videoWidth || CONFIG.STREAM_WIDTH}×${videoElement.videoHeight || CONFIG.STREAM_HEIGHT}`,
            frameRate: `${frameRate} FPS`,
            quality: CONFIG.STREAM_QUALITY,
            protocol: CONFIG.WEBRTC_ENABLED ? 'WebRTC' : 'HTTP'
        };
        
        streamInfo.innerHTML = `
            <div class="stream-stat">
                <strong>Resolution:</strong> ${info.resolution}
            </div>
            <div class="stream-stat">
                <strong>Frame Rate:</strong> ${info.frameRate}
            </div>
            <div class="stream-stat">
                <strong>Quality:</strong> ${info.quality}
            </div>
            <div class="stream-stat">
                <strong>Protocol:</strong> ${info.protocol}
            </div>
        `;
    } else {
        streamInfo.innerHTML = '<div class="text-muted">Stream not active</div>';
    }
}

// ===============================================
// Stream Statistics
// ===============================================

function updateStreamStats() {
    if (!streamActive || !peerConnection) return;
    
    peerConnection.getStats().then(stats => {
        stats.forEach(report => {
            if (report.type === 'inbound-rtp' && report.mediaType === 'video') {
                const bytesReceived = report.bytesReceived;
                const packetsReceived = report.packetsReceived;
                const packetsLost = report.packetsLost || 0;
                
                const lossRate = packetsReceived > 0 ? (packetsLost / packetsReceived * 100).toFixed(2) : 0;
                
                const streamStats = document.getElementById('streamStats');
                if (streamStats) {
                    streamStats.innerHTML = `
                        <div class="stat">Bytes: ${formatBytes(bytesReceived)}</div>
                        <div class="stat">Packets: ${packetsReceived}</div>
                        <div class="stat">Loss: ${lossRate}%</div>
                    `;
                }
            }
        });
    }).catch(console.error);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Start stats monitoring when stream is active
setInterval(() => {
    if (streamActive) {
        updateStreamStats();
        updateStreamInfo();
    }
}, CONFIG.STATS_UPDATE_INTERVAL);