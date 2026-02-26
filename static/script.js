let currentTab = 'trending';
<<<<<<< HEAD
let suggestTimeout;
=======
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781

async function loadTab(tab, element) {
    currentTab = tab;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    if (element) element.classList.add('active');
    
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<p class="loading">Loading...</p>';
    
<<<<<<< HEAD
    try {
        const response = await fetch(`/${tab}`);
        const videos = await response.json();
        displayResults(videos);
    } catch (error) {
        console.error('Error loading tab:', error);
        resultsDiv.innerHTML = '<p class="loading">Error loading songs. Please try again.</p>';
    }
=======
    const response = await fetch(`/${tab}`);
    const videos = await response.json();
    displayResults(videos);
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781
}

async function search() {
    const query = document.getElementById('searchInput').value;
    const resultsDiv = document.getElementById('results');
    
    if (!query) return;
    
    resultsDiv.innerHTML = '<p class="loading">Searching...</p>';
    
<<<<<<< HEAD
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query})
        });
        
        const videos = await response.json();
        displayResults(videos);
    } catch (error) {
        console.error('Search error:', error);
        resultsDiv.innerHTML = '<p class="loading">Search failed. Please try again.</p>';
    }
=======
    const response = await fetch('/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query})
    });
    
    const videos = await response.json();
    displayResults(videos);
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781
}

function displayResults(videos) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    
<<<<<<< HEAD
    if (!videos || videos.length === 0) {
        resultsDiv.innerHTML = '<p class="loading">No songs found.</p>';
        return;
    }
    
=======
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781
    videos.forEach(v => {
        const item = document.createElement('div');
        item.className = 'result-item';
        
        const img = document.createElement('img');
        img.src = v.thumbnail;
        img.alt = v.title;
        img.onerror = function() { this.src = 'https://via.placeholder.com/200x200?text=No+Image'; };
        
        const info = document.createElement('div');
        info.className = 'result-info';
        info.innerHTML = `
            <h3>${v.title}</h3>
            <div class="artist">${v.channel || 'Unknown Artist'}</div>
<<<<<<< HEAD
            <div class="stats">
                <span class="views">👁 ${formatViews(v.views || 0)}</span>
                <span class="likes">❤ ${formatLikes(v.likes || 0)}</span>
            </div>
=======
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781
            <p>${Math.floor(v.duration / 60)}:${(v.duration % 60).toString().padStart(2, '0')}</p>
        `;
        
        const playBtn = document.createElement('button');
        playBtn.className = 'play-btn';
<<<<<<< HEAD
        playBtn.textContent = '▶ Play Now';
        playBtn.onclick = () => playAudio(v.id, v.title, v.thumbnail);
        
        const likeBtn = document.createElement('button');
        likeBtn.className = 'like-btn';
        likeBtn.innerHTML = '❤ Like';
        likeBtn.onclick = (e) => {
            e.stopPropagation();
            toggleLike(likeBtn, v.id);
        };
=======
        playBtn.textContent = '▶ Play';
        playBtn.onclick = () => playAudio(v.id, v.title, v.thumbnail);
        
        const downloadBtns = document.createElement('div');
        downloadBtns.className = 'download-buttons';
        
        const mp3Btn = document.createElement('button');
        mp3Btn.textContent = '⬇ MP3';
        mp3Btn.onclick = () => download(v.id, 'mp3');
        
        const mp4Btn = document.createElement('button');
        mp4Btn.textContent = '⬇ MP4';
        mp4Btn.onclick = () => download(v.id, 'mp4');
        
        downloadBtns.appendChild(mp3Btn);
        downloadBtns.appendChild(mp4Btn);
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781
        
        item.appendChild(img);
        item.appendChild(info);
        item.appendChild(playBtn);
<<<<<<< HEAD
        item.appendChild(likeBtn);
=======
        item.appendChild(downloadBtns);
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781
        resultsDiv.appendChild(item);
    });
}

<<<<<<< HEAD
function formatViews(views) {
    if (views >= 1000000) return (views / 1000000).toFixed(1) + 'M';
    if (views >= 1000) return (views / 1000).toFixed(1) + 'K';
    return views.toString();
}

function formatLikes(likes) {
    if (likes >= 1000000) return (likes / 1000000).toFixed(1) + 'M';
    if (likes >= 1000) return (likes / 1000).toFixed(1) + 'K';
    return likes.toString();
}

function toggleLike(button, videoId) {
    const isLiked = button.classList.contains('liked');
    if (isLiked) {
        button.classList.remove('liked');
        button.innerHTML = '❤ Like';
    } else {
        button.classList.add('liked');
        button.innerHTML = '❤ Liked';
    }
}

=======
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781
let currentVideoId = '';
let currentTitle = '';
let currentThumbnail = '';

function playAudio(videoId, title, thumbnail) {
    currentVideoId = videoId;
    currentTitle = title;
    currentThumbnail = thumbnail;
    
    const player = document.getElementById('player');
    const playerTitle = document.getElementById('playerTitle');
    const playerImg = document.getElementById('playerImg');
    const playerFrame = document.getElementById('playerFrame');
    
    playerTitle.textContent = title;
    playerImg.src = thumbnail;
    playerFrame.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
    player.classList.add('active');
}

function toggleTheaterMode() {
    const player = document.getElementById('player');
    const theaterPlayer = document.getElementById('theaterPlayer');
    const theaterFrame = document.getElementById('theaterFrame');
    const theaterTitle = document.querySelector('.theater-title');
    
    if (theaterPlayer.classList.contains('active')) {
        theaterPlayer.classList.remove('active');
        player.classList.add('active');
        theaterFrame.src = '';
    } else {
        player.classList.remove('active');
        theaterPlayer.classList.add('active');
        theaterTitle.textContent = currentTitle;
        theaterFrame.src = `https://www.youtube.com/embed/${currentVideoId}?autoplay=1`;
    }
}

<<<<<<< HEAD

=======
async function download(videoId, format) {
    const button = event.target;
    const originalText = button.textContent;
    
    button.innerHTML = '⬇ Downloading...';
    button.disabled = true;
    button.style.opacity = '0.7';
    
    const startTime = Date.now();
    
    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({video_id: videoId, format})
        });
        
        if (!response.ok) throw new Error('Download failed');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `download.${format}`;
        a.click();
        
        button.innerHTML = '✓ Downloaded';
        button.style.background = '#4CAF50';
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            button.style.opacity = '1';
            button.style.background = '';
        }, 2000);
        
    } catch (error) {
        button.innerHTML = '✗ Failed';
        button.style.background = '#f44336';
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            button.style.opacity = '1';
            button.style.background = '';
        }, 2000);
    }
}

let suggestTimeout;
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781
let searchInput;
let suggestionsDiv;

function initializeSearch() {
<<<<<<< HEAD
    const searchInput = document.getElementById('searchInput');
    const suggestionsDiv = document.getElementById('suggestions');
=======
    searchInput = document.getElementById('searchInput');
    suggestionsDiv = document.getElementById('suggestions');
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781
    
    if (!searchInput || !suggestionsDiv) return;
    
    searchInput.addEventListener('input', (e) => {
<<<<<<< HEAD
        clearTimeout(suggestTimeout);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            suggestionsDiv.classList.remove('active');
            return;
        }
        
        suggestTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q=${encodeURIComponent(query)}`);
                const data = await response.json();
                const suggestions = data[1];
                
                if (suggestions && suggestions.length > 0) {
                    suggestionsDiv.innerHTML = suggestions.slice(0, 8).map(s => 
                        `<div class="suggestion-item" onclick="selectSuggestion('${s.replace(/'/g, "\\'")}')">${s}</div>`
                    ).join('');
                    suggestionsDiv.classList.add('active');
                } else {
                    suggestionsDiv.classList.remove('active');
                }
            } catch (error) {
                console.error('Suggestions error:', error);
                suggestionsDiv.classList.remove('active');
            }
        }, 300);
=======
    clearTimeout(suggestTimeout);
    const query = e.target.value.trim();
    
    if (query.length < 2) {
        suggestionsDiv.classList.remove('active');
        return;
    }
    
    suggestTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q=${encodeURIComponent(query)}`);
            const data = await response.json();
            const suggestions = data[1];
            
            if (suggestions.length > 0) {
                suggestionsDiv.innerHTML = suggestions.slice(0, 8).map(s => 
                    `<div class="suggestion-item" onclick="selectSuggestion('${s.replace(/'/g, "\\'")}')">${s}</div>`
                ).join('');
                suggestionsDiv.classList.add('active');
            } else {
                suggestionsDiv.classList.remove('active');
            }
        } catch (error) {
            console.error('Suggestions error:', error);
        }
    }, 300);
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781
    });
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            suggestionsDiv.classList.remove('active');
            search();
        }
    });
}

function selectSuggestion(text) {
<<<<<<< HEAD
    const searchInput = document.getElementById('searchInput');
    const suggestionsDiv = document.getElementById('suggestions');
    if (searchInput && suggestionsDiv) {
        searchInput.value = text;
        suggestionsDiv.classList.remove('active');
        search();
    }
}

document.addEventListener('click', (e) => {
    const suggestionsDiv = document.getElementById('suggestions');
    if (suggestionsDiv && !e.target.closest('.search-box')) {
=======
    searchInput.value = text;
    suggestionsDiv.classList.remove('active');
    search();
}

document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-box')) {
>>>>>>> ea52aef7016199e888802cc14e06fd488c571781
        suggestionsDiv.classList.remove('active');
    }
});



function closePlayer() {
    const player = document.getElementById('player');
    const theaterPlayer = document.getElementById('theaterPlayer');
    const playerFrame = document.getElementById('playerFrame');
    const theaterFrame = document.getElementById('theaterFrame');
    
    player.classList.remove('active');
    theaterPlayer.classList.remove('active');
    playerFrame.src = '';
    theaterFrame.src = '';
}

function toggleTheme() {
    document.body.classList.toggle('dark');
    const isDark = document.body.classList.contains('dark');
    document.querySelector('.theme-toggle').textContent = isDark ? '☀️' : '🌙';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}



window.onload = () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark');
        document.querySelector('.theme-toggle').textContent = '☀️';
    }
    
    setTimeout(() => {
        document.getElementById('splashScreen').style.display = 'none';
        document.getElementById('mainApp').style.display = 'block';
        initializeSearch();
        loadTab('trending', document.querySelector('.tab.active'));
    }, 3000);
};
