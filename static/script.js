let currentTab = 'foryou';
let suggestTimeout;

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (window.innerWidth <= 1024) {
        sidebar.classList.toggle('active');
    } else {
        sidebar.classList.toggle('hidden');
        if (mainContent) {
            mainContent.classList.toggle('expanded');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const collapseBtn = document.getElementById('collapseBtn');
    if (collapseBtn) {
        collapseBtn.addEventListener('click', toggleSidebar);
    }
});

async function loadTab(tab, element) {
    currentTab = tab;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.sidebar-item').forEach(t => t.classList.remove('active'));
    if (element) element.classList.add('active');
    
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<p class="loading">Loading...</p>';
    
    if (window.innerWidth <= 768) {
        const sb = document.getElementById('sidebar');
        if (sb) sb.classList.remove('active');
    }
    
    try {
        const response = await fetch(`/${tab}`);
        const videos = await response.json();
        displayResults(videos);
    } catch (error) {
        console.error('Error loading tab:', error);
        resultsDiv.innerHTML = '<p class="loading">Error loading songs. Please try again.</p>';
    }
}

async function search() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value.trim();
    const resultsDiv = document.getElementById('results');
    
    if (!query) return;
    
    resultsDiv.innerHTML = '<p class="loading">Searching...</p>';
    
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
}

function displayResults(videos) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    
    if (!videos || videos.length === 0) {
        resultsDiv.innerHTML = '<p class="loading">No songs found.</p>';
        return;
    }
    
    videos.forEach(v => {
        const item = document.createElement('div');
        item.className = 'result-item';
        item.onclick = () => playAudio(v.id, v.title, v.thumbnail);
        
        const img = document.createElement('img');
        img.src = v.thumbnail;
        img.alt = v.title;
        img.onerror = function() { this.src = 'https://via.placeholder.com/200x200?text=No+Image'; };
        
        const info = document.createElement('div');
        info.className = 'result-info';
        info.innerHTML = `
            <h3>${v.title}</h3>
            <div class="artist">${v.channel || 'Unknown Artist'}</div>
        `;
        
        item.appendChild(img);
        item.appendChild(info);
        resultsDiv.appendChild(item);
    });
}

let currentVideoId = '';
let currentTitle = '';
let currentArtist = '';
let currentThumbnail = '';
let isPlaying = false;

function playAudio(videoId, title, thumbnail) {
    currentVideoId = videoId;
    currentTitle = title;
    currentThumbnail = thumbnail;
    currentArtist = 'Unknown Artist';
    isPlaying = true;
    
    const fullPlayer = document.getElementById('fullPlayer');
    const fullPlayerImg = document.getElementById('fullPlayerImg');
    const fullPlayerTitle = document.getElementById('fullPlayerTitle');
    const fullPlayerArtist = document.getElementById('fullPlayerArtist');
    const fullPlayerFrame = document.getElementById('fullPlayerFrame');
    const playPauseBtn = document.getElementById('playPauseBtn');
    
    fullPlayerImg.src = thumbnail;
    fullPlayerTitle.textContent = title;
    fullPlayerArtist.textContent = currentArtist;
    fullPlayerFrame.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1`;
    playPauseBtn.textContent = '⏸';
    fullPlayer.classList.add('active');
}

function togglePlayPause() {
    const fullPlayerFrame = document.getElementById('fullPlayerFrame');
    const playPauseBtn = document.getElementById('playPauseBtn');
    
    if (isPlaying) {
        // Pause the video by removing autoplay and reloading without it
        const currentSrc = fullPlayerFrame.src;
        if (currentSrc.includes('autoplay=1')) {
            fullPlayerFrame.src = currentSrc.replace('autoplay=1', 'autoplay=0');
        }
        playPauseBtn.textContent = '▶';
        isPlaying = false;
    } else {
        // Play the video by adding autoplay
        const currentSrc = fullPlayerFrame.src;
        if (currentSrc.includes('autoplay=0')) {
            fullPlayerFrame.src = currentSrc.replace('autoplay=0', 'autoplay=1');
        } else if (!currentSrc.includes('autoplay')) {
            fullPlayerFrame.src = currentSrc + '&autoplay=1';
        }
        playPauseBtn.textContent = '⏸';
        isPlaying = true;
    }
}

function nextSong() {
    console.log('Next song');
}

function previousSong() {
    console.log('Previous song');
}

function closePlayer() {
    const fullPlayer = document.getElementById('fullPlayer');
    const fullPlayerFrame = document.getElementById('fullPlayerFrame');
    
    fullPlayer.classList.remove('active');
    fullPlayerFrame.src = '';
    
    currentVideoId = '';
    currentTitle = '';
    currentArtist = '';
    currentThumbnail = '';
    isPlaying = false;
}

function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const suggestionsDiv = document.getElementById('suggestions');
    
    if (!searchInput || !suggestionsDiv) return;
    
    searchInput.addEventListener('input', (e) => {
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
                        `<div class="suggestion-item" onclick="selectSuggestion('${s.replace(/'/g, "\\\\'")}')">${s}</div>`
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
    });
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            suggestionsDiv.classList.remove('active');
            search();
        }
    });
}

function selectSuggestion(text) {
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
        suggestionsDiv.classList.remove('active');
    }
});

function toggleTheme() {
    document.body.classList.toggle('light');
    const isLight = document.body.classList.contains('light');
    const themeToggle = document.querySelector('[onclick="toggleTheme()"]');
    if (themeToggle) {
        themeToggle.textContent = isLight ? '🌙' : '☀️';
    }
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
}

window.onload = () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light');
        const themeToggle = document.querySelector('[onclick="toggleTheme()"]');
        if (themeToggle) themeToggle.textContent = '🌙';
    }
    
    setTimeout(() => {
        const splashScreen = document.getElementById('splashScreen');
        const mainApp = document.getElementById('mainApp');
        if (splashScreen) splashScreen.style.display = 'none';
        if (mainApp) mainApp.style.display = 'block';
        
        initializeSearch();
        loadTab('foryou');
    }, 3000);
};