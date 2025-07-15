document.addEventListener('DOMContentLoaded', function() {
    const videoPlayer = document.getElementById('videoPlayer');
    if (!videoPlayer) return;
    const playPauseBtn = document.getElementById('playPauseBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressHandle = document.getElementById('progressHandle');
    const currentTimeEl = document.getElementById('currentTime');
    const durationEl = document.getElementById('duration');
    const volumeBtn = document.getElementById('volumeBtn');
    const volumeSlider = document.getElementById('volumeSlider');
    const volumeLevel = document.getElementById('volumeLevel');
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    const qualityBtn = document.getElementById('qualityBtn');
    const qualityOptions = document.getElementById('qualityOptions');
    const errorMsg = document.getElementById('videoErrorMsg');

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        seconds = Math.floor(seconds % 60);
        return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }
    const sourceEl = videoPlayer.querySelector('source');
    if (!sourceEl || !sourceEl.getAttribute('src')) {
        document.querySelector('.player-controls').style.display = 'none';
        errorMsg.style.display = 'block';
        return;
    }
    videoPlayer.addEventListener('error', () => {
        document.querySelector('.player-controls').style.display = 'none';
        errorMsg.style.display = 'block';
    });
    videoPlayer.addEventListener('loadedmetadata', () => {
        durationEl.textContent = formatTime(videoPlayer.duration);
    });
    videoPlayer.addEventListener('timeupdate', () => {
        const percent = (videoPlayer.currentTime / videoPlayer.duration) * 100;
        progressBar.style.width = `${percent}%`;
        progressHandle.style.left = `${percent}%`;
        currentTimeEl.textContent = formatTime(videoPlayer.currentTime);
    });

    // Seek
    let seeking = false;
    progressContainer.addEventListener('mousedown', (e) => {
        seeking = true; seek(e);
    });
    document.addEventListener('mousemove', (e) => { if (seeking) seek(e); });
    document.addEventListener('mouseup', () => seeking = false);
    function seek(e) {
        const rect = progressContainer.getBoundingClientRect();
        let pos = (e.clientX - rect.left) / rect.width;
        pos = Math.max(0, Math.min(1, pos));
        videoPlayer.currentTime = pos * videoPlayer.duration;
    }

    // Play/Pause
    playPauseBtn.addEventListener('click', () => {
        if (videoPlayer.paused) {
            videoPlayer.play();
            playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
            videoPlayer.pause();
            playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
        }
    });

    // Volume
    let adjustingVolume = false;
    volumeSlider.addEventListener('mousedown', (e) => {
        adjustingVolume = true;
        changeVolume(e);
    });
    document.addEventListener('mousemove', (e) => { if (adjustingVolume) changeVolume(e); });
    document.addEventListener('mouseup', () => adjustingVolume = false);
    function changeVolume(e) {
        const rect = volumeSlider.getBoundingClientRect();
        let pos = (e.clientX - rect.left) / rect.width;
        pos = Math.max(0, Math.min(1, pos));
        videoPlayer.volume = pos;
        volumeLevel.style.width = `${pos * 100}%`;
        if (pos === 0) volumeBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
        else if (pos < 0.5) volumeBtn.innerHTML = '<i class="fas fa-volume-down"></i>';
        else volumeBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
    }
    volumeBtn.addEventListener('click', () => {
        if (videoPlayer.volume === 0) changeVolume({ clientX: volumeSlider.getBoundingClientRect().left + volumeSlider.offsetWidth * 0.8 });
        else changeVolume({ clientX: volumeSlider.getBoundingClientRect().left });
    });

    // Fullscreen
    fullscreenBtn.addEventListener('click', () => {
        const player = document.querySelector('.player');
        if (!document.fullscreenElement) {
            player.requestFullscreen?.();
            fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
        } else {
            document.exitFullscreen?.();
            fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
        }
    });

    // Quality options
    qualityBtn.addEventListener('click', () => qualityOptions.classList.toggle('active'));
    document.querySelectorAll('.quality-option').forEach(option => {
        option.addEventListener('click', () => {
            document.querySelector('.quality-option.active').classList.remove('active');
            option.classList.add('active');
            qualityBtn.innerHTML = `<i class="fas fa-hd"></i> ${option.textContent.trim()}`;
            qualityOptions.classList.remove('active');
            document.querySelector('.player').style.backgroundColor = '#000';
            setTimeout(() => document.querySelector('.player').style.backgroundColor = 'transparent', 300);
        });
    });
    document.addEventListener('click', (e) => {
        if (!qualityBtn.contains(e.target)) {
            qualityOptions.classList.remove('active');
        }
    });
});
