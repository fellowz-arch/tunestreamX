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
    
    const categoryTabs = document.getElementById('categoryTabs');
    const movieTabs = document.getElementById('movieTabs');
    const wrestlingTabs = document.getElementById('wrestlingTabs');
    
    categoryTabs.style.display = 'none';
    movieTabs.style.display = 'none';
    wrestlingTabs.style.display = 'none';
    
    if (tab === 'football') {
        categoryTabs.style.display = 'flex';
    } else if (tab === 'movies') {
        movieTabs.style.display = 'flex';
    } else if (tab === 'wrestling') {
        wrestlingTabs.style.display = 'flex';
    }
    
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<div style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:1000;"><div style="width:40px;height:40px;border:4px solid #f3f3f3;border-top:4px solid #667eea;border-radius:50%;animation:spin 1s linear infinite;"></div></div><style>@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}</style>';
    
    if (window.innerWidth <= 768) {
        const sb = document.getElementById('sidebar');
        if (sb) sb.classList.remove('active');
    }
    
    try {
        const response = await fetch(`/${tab}`);
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const videos = await response.json();
        
        if (!videos || videos.length === 0) {
            resultsDiv.innerHTML = '<p class="loading">No content available. Try again later.</p>';
        } else {
            displayResults(videos);
        }
    } catch (error) {
        console.error('Error loading tab:', error);
        resultsDiv.innerHTML = '<p class="loading">Failed to load content. Please refresh the page.</p>';
    }
}

async function loadCategory(query) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<p class="loading">🔄 Loading content... Please wait.</p>';
    
    document.querySelectorAll('.category-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query})
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const videos = await response.json();
        
        if (!videos || videos.length === 0) {
            resultsDiv.innerHTML = '<p class="loading">No content found for this category. Try another one.</p>';
        } else {
            displayResults(videos);
        }
    } catch (error) {
        console.error('Category error:', error);
        resultsDiv.innerHTML = '<p class="loading">Failed to load category. Please try again.</p>';
    }
}

async function search() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value.trim();
    const resultsDiv = document.getElementById('results');
    
    if (!query) return;
    
    resultsDiv.innerHTML = '<p class="loading">🔄 Searching... Please wait.</p>';
    
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query})
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const videos = await response.json();
        
        if (!videos || videos.length === 0) {
            resultsDiv.innerHTML = '<p class="loading">No results found. Try different keywords.</p>';
        } else {
            displayResults(videos);
        }
    } catch (error) {
        console.error('Search error:', error);
        resultsDiv.innerHTML = '<p class="loading">Search failed. Please try again.</p>';
    }
}

function displayResults(videos) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    
    if (!videos || videos.length === 0) {
        resultsDiv.innerHTML = '<p class="loading">No content available at the moment.</p>';
        return;
    }
    
    videos.forEach(v => {
        const item = document.createElement('div');
        item.className = 'result-item';

        if (v.isLive) {
            item.onclick = () => playLiveStream(v);
        } else if (v.source === 'certifytv' && v.url) {
            item.onclick = () => window.open(v.url, '_blank');
        } else {
            item.onclick = () => playAudio(v.id, v.title, v.thumbnail);
        }
        
        const img = document.createElement('img');
        img.src = v.thumbnail;
        img.alt = v.title;
        img.onerror = function() { this.src = 'https://placehold.co/200x200/1a1a2e/ffffff?text=No+Image'; };
        
        const info = document.createElement('div');
        info.className = 'result-info';
        const liveBadge = v.isLive ? '<span style="background:#e63946;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;margin-right:6px;font-weight:bold;">&#128308; LIVE</span>' : '';
        const sourceBadge = v.channel ? `<span style="background:#333;color:#aaa;padding:2px 6px;border-radius:4px;font-size:10px;">${v.channel}</span>` : '';
        info.innerHTML = `
            <h3>${liveBadge}${v.title}</h3>
            <div class="artist">${sourceBadge}</div>
        `;
        
        item.appendChild(img);
        item.appendChild(info);
        resultsDiv.appendChild(item);
    });
}

function playLiveStream(v) {
    const fullPlayer = document.getElementById('fullPlayer');
    const fullPlayerFrame = document.getElementById('fullPlayerFrame');
    const fullPlayerImg = document.getElementById('fullPlayerImg');
    const fullPlayerTitle = document.getElementById('fullPlayerTitle');
    const fullPlayerArtist = document.getElementById('fullPlayerArtist');

    fullPlayerImg.src = v.thumbnail;
    fullPlayerTitle.innerHTML = '<span style="background:#e63946;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;margin-right:8px;">&#128308; LIVE</span>' + v.title;
    fullPlayerArtist.textContent = v.channel || 'Live Stream';
    fullPlayer.classList.add('active');
    fullPlayerFrame.style.display = 'none';

    // Remove any existing video element
    const existingVideo = document.getElementById('liveVideoPlayer');
    if (existingVideo) existingVideo.remove();

    if (v.streamType === 'm3u8' && v.streamUrl) {
        playM3U8(v.streamUrl);
    } else if (v.streamType === 'iframe' && v.streamUrl) {
        fullPlayerFrame.style.display = 'block';
        fullPlayerFrame.src = v.streamUrl;
    } else {
        // Try proxy to extract stream on the fly
        fetch(`/proxy-stream?url=${encodeURIComponent(v.pageUrl)}`)
            .then(r => r.json())
            .then(data => {
                if (data.type === 'm3u8' && data.url) {
                    playM3U8(data.url);
                } else if (data.type === 'iframe' && data.url) {
                    fullPlayerFrame.style.display = 'block';
                    fullPlayerFrame.src = data.url;
                } else {
                    fullPlayerFrame.style.display = 'block';
                    fullPlayerFrame.src = v.pageUrl;
                }
            })
            .catch(() => {
                fullPlayerFrame.style.display = 'block';
                fullPlayerFrame.src = v.pageUrl;
            });
    }
}

function playM3U8(url) {
    const fullPlayerFrame = document.getElementById('fullPlayerFrame');
    const container = fullPlayerFrame.parentElement;

    const video = document.createElement('video');
    video.id = 'liveVideoPlayer';
    video.style.cssText = 'width:100%;height:100%;background:#000;';
    video.controls = true;
    video.autoplay = true;
    container.insertBefore(video, fullPlayerFrame);

    if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = url;
    } else if (window.Hls && Hls.isSupported()) {
        const hls = new Hls();
        hls.loadSource(url);
        hls.attachMedia(video);
    } else {
        // Fallback: load HLS.js dynamically
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/hls.js@latest';
        script.onload = () => {
            if (Hls.isSupported()) {
                const hls = new Hls();
                hls.loadSource(url);
                hls.attachMedia(video);
            }
        };
        document.head.appendChild(script);
    }
}

let currentVideoId = '';
let currentTitle = '';
let currentArtist = '';
let currentThumbnail = '';
let isPlaying = false;
let relatedVideos = [];
let currentVideoIndex = 0;
let navBtnTimeout;

function playAudio(videoId, title, thumbnail) {
    currentVideoId = videoId;
    currentTitle = title;
    currentThumbnail = thumbnail;
    currentArtist = 'Unknown Artist';
    isPlaying = true;
    
    // Track view with category
    const category = getCurrentCategory();
    trackView(category);
    
    const fullPlayer = document.getElementById('fullPlayer');
    const fullPlayerImg = document.getElementById('fullPlayerImg');
    const fullPlayerTitle = document.getElementById('fullPlayerTitle');
    const fullPlayerArtist = document.getElementById('fullPlayerArtist');
    const fullPlayerFrame = document.getElementById('fullPlayerFrame');
    
    fullPlayerImg.src = thumbnail;
    fullPlayerTitle.textContent = title;
    fullPlayerArtist.textContent = currentArtist;
    fullPlayer.classList.add('active');
    
    generateComments();
    loadRelatedVideos(title);
    
    showAdBeforeVideo(videoId);
    setupNavButtonAutoHide();
}

function setupNavButtonAutoHide() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const videoContainer = document.querySelector('.video-player').parentElement;
    
    if (!prevBtn || !nextBtn || !videoContainer) return;
    
    const showButtons = () => {
        prevBtn.classList.remove('hidden');
        nextBtn.classList.remove('hidden');
        clearTimeout(navBtnTimeout);
        navBtnTimeout = setTimeout(() => {
            prevBtn.classList.add('hidden');
            nextBtn.classList.add('hidden');
        }, 3000);
    };
    
    videoContainer.addEventListener('click', showButtons);
    videoContainer.addEventListener('touchstart', showButtons);
    videoContainer.addEventListener('mousemove', showButtons);
    
    navBtnTimeout = setTimeout(() => {
        prevBtn.classList.add('hidden');
        nextBtn.classList.add('hidden');
    }, 3000);
}

function togglePlayPause() {
    const fullPlayerFrame = document.getElementById('fullPlayerFrame');
    
    if (isPlaying) {
        const currentSrc = fullPlayerFrame.src;
        if (currentSrc.includes('autoplay=1')) {
            fullPlayerFrame.src = currentSrc.replace('autoplay=1', 'autoplay=0');
        }
        isPlaying = false;
    } else {
        const currentSrc = fullPlayerFrame.src;
        if (currentSrc.includes('autoplay=0')) {
            fullPlayerFrame.src = currentSrc.replace('autoplay=0', 'autoplay=1');
        } else if (!currentSrc.includes('autoplay')) {
            fullPlayerFrame.src = currentSrc + '&autoplay=1';
        }
        isPlaying = true;
    }
}

function nextSong() {
    if (relatedVideos.length > 0 && currentVideoIndex < relatedVideos.length - 1) {
        currentVideoIndex++;
        const next = relatedVideos[currentVideoIndex];
        playAudio(next.id, next.title, next.thumbnail);
    }
}

function previousSong() {
    if (currentVideoIndex > 0) {
        currentVideoIndex--;
        const prev = relatedVideos[currentVideoIndex];
        playAudio(prev.id, prev.title, prev.thumbnail);
    }
}

async function loadRelatedVideos(query) {
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query})
        });
        
        relatedVideos = await response.json();
        currentVideoIndex = 0;
        displayRelatedVideos();
    } catch (error) {
        console.error('Error loading related videos:', error);
    }
}

function displayRelatedVideos() {
    const recommendedList = document.getElementById('recommendedList');
    if (!recommendedList) return;
    
    if (!relatedVideos.length) {
        recommendedList.innerHTML = '<p style="color: var(--text-secondary); padding: 20px;">Loading suggestions...</p>';
        return;
    }
    
    recommendedList.innerHTML = relatedVideos.map(v => `
        <div class="recommended-item" onclick="playAudio('${v.id}', '${v.title.replace(/'/g, "\\'").replace(/"/g, '&quot;')}', '${v.thumbnail}')">
            <img src="${v.thumbnail}" alt="${v.title}">
            <div class="recommended-info">
                <h4>${v.title}</h4>
                <p>${v.channel}</p>
            </div>
        </div>
    `).join('');
}

function closePlayer() {
    const fullPlayer = document.getElementById('fullPlayer');
    const fullPlayerFrame = document.getElementById('fullPlayerFrame');
    
    fullPlayer.classList.remove('active');
    fullPlayerFrame.src = '';
    
    const liveVideo = document.getElementById('liveVideoPlayer');
    if (liveVideo) liveVideo.remove();
    
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
                const response = await fetch(`/suggestions?q=${encodeURIComponent(query)}`);
                const suggestions = await response.json();
                
                if (suggestions && suggestions.length > 0) {
                    suggestionsDiv.innerHTML = suggestions.slice(0, 10).map(s => 
                        `<div class="suggestion-item" onclick="selectSuggestion('${s.replace(/'/g, "\\'").replace(/"/g, '&quot;')}')">${s}</div>`
                    ).join('');
                    suggestionsDiv.classList.add('active');
                } else {
                    suggestionsDiv.classList.remove('active');
                }
            } catch (error) {
                console.error('Suggestions error:', error);
                suggestionsDiv.classList.remove('active');
            }
        }, 200);
    });
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            suggestionsDiv.classList.remove('active');
            search();
        }
    });
    
    searchInput.addEventListener('focus', (e) => {
        if (e.target.value.trim().length >= 2 && suggestionsDiv.innerHTML) {
            suggestionsDiv.classList.add('active');
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


function generateComments() {
    const commentsList = document.getElementById('commentsList');
    if (!commentsList) return;
    
    const names = ['Alex', 'Sarah', 'Mike', 'Emma', 'Chris', 'Lisa', 'David', 'Maria', 'John', 'Anna', 'Tom', 'Kate', 'Ryan', 'Sophia', 'James', 'Olivia', 'Daniel', 'Mia', 'Lucas', 'Ava'];
    const emojis = ['😍', '🔥', '❤️', '👏', '🎵', '🎶', '💯', '✨', '🙌', '👍', '😊', '🎉', '💪', '🌟', '😎'];
    const times = ['1 minute ago', '5 minutes ago', '10 minutes ago', '30 minutes ago', '1 hour ago', '2 hours ago', '5 hours ago', '1 day ago', '2 days ago', '1 week ago'];
    
    const commentTemplates = [
        'This is absolutely amazing! {emoji}',
        'Can\'t stop listening to this! {emoji}',
        'This song is fire! {emoji}{emoji}',
        'Best song I\'ve heard all year!',
        'This deserves more views! {emoji}',
        'Who else is listening in 2024? {emoji}',
        'This brings back so many memories {emoji}',
        'The beat is incredible! {emoji}',
        'This is on repeat all day! {emoji}',
        'Masterpiece! {emoji}{emoji}{emoji}',
        'Why is this so addictive? {emoji}',
        'This hits different at night {emoji}',
        'Goosebumps every time! {emoji}',
        'This is pure art {emoji}',
        'Can\'t get enough of this! {emoji}',
        'This is what real music sounds like {emoji}',
        'Legendary! {emoji}',
        'This never gets old {emoji}',
        'Playing this on repeat! {emoji}',
        'This is my new favorite! {emoji}'
    ];
    
    let commentsHTML = '';
    
    for (let i = 0; i < 100; i++) {
        const name = names[Math.floor(Math.random() * names.length)];
        const emoji = emojis[Math.floor(Math.random() * emojis.length)];
        const time = times[Math.floor(Math.random() * times.length)];
        const template = commentTemplates[Math.floor(Math.random() * commentTemplates.length)];
        const text = template.replace(/{emoji}/g, emoji);
        const likes = Math.floor(Math.random() * 1000) + 1;
        const avatarEmoji = emojis[Math.floor(Math.random() * emojis.length)];
        
        commentsHTML += `
            <div class="comment-item">
                <div class="comment-avatar">${avatarEmoji}</div>
                <div class="comment-content">
                    <div class="comment-author">
                        ${name}
                        <span class="comment-time">${time}</span>
                    </div>
                    <div class="comment-text">${text}</div>
                    <div class="comment-actions">
                        <div class="comment-action">👍 ${likes}</div>
                        <div class="comment-action">👎</div>
                        <div class="comment-action">Reply</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    commentsList.innerHTML = commentsHTML + commentsHTML;
}


function openLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.classList.add('active');
        showLogin();
    }
}

function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function showLogin() {
    document.getElementById('modalTitle').textContent = 'Sign In';
    document.getElementById('authBtn').textContent = 'Sign In';
    document.getElementById('authConfirmPassword').style.display = 'none';
    document.getElementById('modalFooter').innerHTML = 'Don\'t have an account? <a href="#" onclick="showSignup()">Sign Up</a>';
}

function showSignup() {
    document.getElementById('modalTitle').textContent = 'Sign Up';
    document.getElementById('authBtn').textContent = 'Sign Up';
    document.getElementById('authConfirmPassword').style.display = 'block';
    document.getElementById('authConfirmPassword').required = true;
    document.getElementById('modalFooter').innerHTML = 'Already have an account? <a href="#" onclick="showLogin()">Sign In</a>';
}

async function handleAuth(event) {
    event.preventDefault();
    const email = document.getElementById('authEmail').value;
    const password = document.getElementById('authPassword').value;
    const confirmPassword = document.getElementById('authConfirmPassword').value;
    const isSignup = document.getElementById('authBtn').textContent === 'Sign Up';
    
    if (isSignup && password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }
    
    try {
        const endpoint = isSignup ? '/auth/signup' : '/auth/login';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        const result = await response.json();
        
        if (result.success) {
            localStorage.setItem('userEmail', email);
            localStorage.setItem('isLoggedIn', 'true');
            
            closeLoginModal();
            updateProfileButton(email);
            
            if (isSignup) {
                sendWelcomeEmail(email);
                showWelcomeModal();
            } else {
                alert('Login successful!');
            }
        } else {
            alert(result.error);
        }
    } catch (error) {
        alert('Authentication failed. Please try again.');
    }
}

async function sendWelcomeEmail(email) {
    try {
        await fetch('/send-welcome-email', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email})
        });
    } catch (error) {
        console.error('Failed to send welcome email:', error);
    }
}

function showWelcomeModal() {
    const welcomeModal = document.getElementById('welcomeModal');
    if (welcomeModal) {
        welcomeModal.classList.add('active');
    }
}

function closeWelcomeModal() {
    const welcomeModal = document.getElementById('welcomeModal');
    if (welcomeModal) {
        welcomeModal.classList.remove('active');
    }
}

function loginWithGoogle() {
    window.location.href = 'https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=' + encodeURIComponent(window.location.origin + '/auth/google/callback') + '&response_type=code&scope=email%20profile';
}

function loginWithApple() {
    window.location.href = 'https://appleid.apple.com/auth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=' + encodeURIComponent(window.location.origin + '/auth/apple/callback') + '&response_type=code&scope=email%20name';
}

function loginWithGithub() {
    window.location.href = 'https://github.com/login/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=' + encodeURIComponent(window.location.origin + '/auth/github/callback') + '&scope=user:email';
}

function updateProfileButton(email) {
    const profileBtn = document.getElementById('profileBtn');
    const mobileProfileIcon = document.getElementById('mobileProfileIcon');
    const userEmailDiv = document.getElementById('userEmail');
    const loggedInMenu = document.getElementById('loggedInMenu');
    const loggedOutMenu = document.getElementById('loggedOutMenu');
    
    if (profileBtn) {
        profileBtn.innerHTML = '✓';
        profileBtn.title = email;
    }
    if (mobileProfileIcon) {
        mobileProfileIcon.textContent = '✓';
    }
    if (userEmailDiv) {
        userEmailDiv.textContent = email;
    }
    if (loggedInMenu) {
        loggedInMenu.style.display = 'block';
    }
    if (loggedOutMenu) {
        loggedOutMenu.style.display = 'none';
    }
}

function toggleProfileMenu() {
    const menu = document.getElementById('profileMenu');
    if (menu) {
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    }
}

function logout() {
    localStorage.removeItem('userEmail');
    localStorage.removeItem('isLoggedIn');
    
    const profileBtn = document.getElementById('profileBtn');
    const mobileProfileIcon = document.getElementById('mobileProfileIcon');
    const loggedInMenu = document.getElementById('loggedInMenu');
    const loggedOutMenu = document.getElementById('loggedOutMenu');
    
    if (profileBtn) {
        profileBtn.innerHTML = '👤';
        profileBtn.title = 'Profile';
    }
    if (mobileProfileIcon) {
        mobileProfileIcon.textContent = '👤';
    }
    if (loggedInMenu) {
        loggedInMenu.style.display = 'none';
    }
    if (loggedOutMenu) {
        loggedOutMenu.style.display = 'block';
    }
    
    alert('Logged out successfully!');
}

document.addEventListener('click', (e) => {
    const menu = document.getElementById('profileMenu');
    const profileBtn = document.getElementById('profileBtn');
    if (menu && profileBtn && !profileBtn.contains(e.target) && !menu.contains(e.target)) {
        menu.style.display = 'none';
    }
});

document.addEventListener('click', (e) => {
    const modal = document.getElementById('loginModal');
    if (e.target === modal) {
        closeLoginModal();
    }
    
    const suggestionsDiv = document.getElementById('suggestions');
    if (suggestionsDiv && !e.target.closest('.search-box')) {
        suggestionsDiv.classList.remove('active');
    }
});

window.onload = () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light');
        const themeToggle = document.querySelector('[onclick="toggleTheme()"]');
        if (themeToggle) themeToggle.textContent = '🌙';
    }
    
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const userEmail = localStorage.getItem('userEmail');
    if (isLoggedIn === 'true' && userEmail) {
        updateProfileButton(userEmail);
    }
    
    trackSession();
    
    initializeSearch();
    loadTab('foryou');
    
    setTimeout(() => {
        const splashScreen = document.getElementById('splashScreen');
        const mainApp = document.getElementById('mainApp');
        if (splashScreen) splashScreen.style.display = 'none';
        if (mainApp) mainApp.style.display = 'block';
    }, 5000);
};

async function trackSession() {
    try {
        await fetch('/track/session', { method: 'POST' });
    } catch (e) {
        console.log('Session tracking failed');
    }
}

async function trackInstall() {
    try {
        await fetch('/track/install', { method: 'POST' });
    } catch (e) {
        console.log('Install tracking failed');
    }
}

async function trackView(category) {
    try {
        await fetch('/track/view', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({category})
        });
    } catch (e) {
        console.log('View tracking failed');
    }
}

function getCurrentCategory() {
    switch(currentTab) {
        case 'football': return 'sports';
        case 'movies': return 'movies';
        case 'wrestling': return 'sports';
        case 'foryou':
        case 'trending':
        case 'top':
        default: return 'music';
    }
}


async function showAdBeforeVideo(videoId) {
    try {
        const response = await fetch('/get-ad');
        const ad = await response.json();
        
        if (ad && ad.videoFile) {
            showAdPlayer(ad.videoFile, ad.clickUrl, ad.id, videoId);
            return;
        }
    } catch (error) {
        console.error('Failed to load ad:', error);
    }
    
    playMainVideo(videoId);
}

function extractYouTubeId(url) {
    const match = url.match(/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/);
    return match ? match[1] : null;
}

function showAdPlayer(adVideoFile, adClickUrl, adId, mainVideoId) {
    const fullPlayerFrame = document.getElementById('fullPlayerFrame');
    
    const adOverlay = document.createElement('div');
    adOverlay.id = 'adOverlay';
    adOverlay.className = 'video-player';
    adOverlay.style.cssText = 'position: relative; background: #000; display: flex; flex-direction: column; align-items: center; justify-content: center;';
    
    const adVideo = document.createElement('video');
    adVideo.style.cssText = 'width: 100%; height: 100%; object-fit: contain;';
    adVideo.src = adVideoFile;
    adVideo.autoplay = true;
    adVideo.muted = false;
    adVideo.controls = false;
    adVideo.preload = 'auto';
    
    adVideo.onerror = () => {
        console.error('Ad video failed to load:', adVideoFile);
        adOverlay.remove();
        playMainVideo(mainVideoId);
    };
    
    // Force play after load
    adVideo.onloadeddata = () => {
        adVideo.play().catch(e => console.error('Autoplay failed:', e));
    };
    
    const adLabel = document.createElement('div');
    adLabel.style.cssText = 'position: absolute; top: 20px; left: 20px; background: #f59e0b; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold; font-size: 14px; z-index: 11;';
    adLabel.textContent = 'Advertisement';
    
    const skipBtn = document.createElement('button');
    skipBtn.style.cssText = 'position: absolute; bottom: 20px; right: 20px; background: rgba(255,255,255,0.9); color: #000; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; display: none; z-index: 11;';
    skipBtn.textContent = 'Skip Ad';
    skipBtn.onclick = () => {
        adOverlay.remove();
        playMainVideo(mainVideoId);
    };
    
    if (adClickUrl && adClickUrl.trim() !== '') {
        const learnMoreBtn = document.createElement('button');
        learnMoreBtn.style.cssText = 'position: absolute; bottom: 20px; left: 20px; background: #3b82f6; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; z-index: 11; transition: background 0.3s;';
        learnMoreBtn.textContent = 'Learn More';
        learnMoreBtn.onmouseover = () => learnMoreBtn.style.background = '#2563eb';
        learnMoreBtn.onmouseout = () => learnMoreBtn.style.background = '#3b82f6';
        learnMoreBtn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            const url = adClickUrl.startsWith('http') ? adClickUrl : 'https://' + adClickUrl;
            window.open(url, '_blank', 'noopener,noreferrer');
        };
        adOverlay.appendChild(learnMoreBtn);
    }
    
    const countdown = document.createElement('div');
    countdown.style.cssText = 'position: absolute; bottom: 20px; right: 20px; background: rgba(0,0,0,0.8); color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold; z-index: 11;';
    countdown.textContent = 'Ad will be skippable in 5s';
    
    adOverlay.appendChild(adVideo);
    adOverlay.appendChild(adLabel);
    adOverlay.appendChild(countdown);
    adOverlay.appendChild(skipBtn);
    
    fullPlayerFrame.parentElement.insertBefore(adOverlay, fullPlayerFrame);
    fullPlayerFrame.style.display = 'none';
    
    fetch('/track-ad-view', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({adId})
    }).then(response => response.json())
      .then(data => console.log('Ad view tracked:', data))
      .catch(error => console.error('Failed to track ad view:', error));
    
    let timeLeft = 5;
    const countdownInterval = setInterval(() => {
        timeLeft--;
        if (timeLeft > 0) {
            countdown.textContent = `Ad will be skippable in ${timeLeft}s`;
        } else {
            countdown.style.display = 'none';
            skipBtn.style.display = 'block';
            clearInterval(countdownInterval);
        }
    }, 1000);
    
    adVideo.onended = () => {
        adOverlay.remove();
        playMainVideo(mainVideoId);
    };
}

function playMainVideo(videoId) {
    const fullPlayerFrame = document.getElementById('fullPlayerFrame');
    fullPlayerFrame.style.display = 'block';
    fullPlayerFrame.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1`;
}

// Live Sports
let allLiveMatches = [];

async function openLiveSports() {
    document.getElementById('liveSportsPage').style.display = 'block';
    document.body.style.overflow = 'hidden';
    await loadLiveMatches();
}

async function loadLiveMatches() {
    const grid = document.getElementById('liveMatchesGrid');
    grid.innerHTML = '<div style="color:#aaa;text-align:center;grid-column:1/-1;padding:40px;">&#128308; Loading live matches from all sources...</div>';
    try {
        const res = await fetch('/live-football');
        allLiveMatches = await res.json();
        renderLiveMatches(allLiveMatches);
    } catch(e) {
        grid.innerHTML = '<div style="color:#e63946;text-align:center;grid-column:1/-1;padding:40px;">Failed to load matches. Please try again.</div>';
    }
}

function renderLiveMatches(matches) {
    const grid = document.getElementById('liveMatchesGrid');
    if (!matches || matches.length === 0) {
        grid.innerHTML = '<div style="color:#aaa;text-align:center;grid-column:1/-1;padding:60px 20px;"><div style="font-size:48px;">⚽</div><div style="margin-top:12px;font-size:16px;">No matches right now. Check back soon.</div></div>';
        return;
    }

    // Separate live and upcoming
    const live = matches.filter(m => m.isLive);
    const upcoming = matches.filter(m => !m.isLive);

    let html = '';

    if (live.length > 0) {
        html += `<div style="grid-column:1/-1;display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <span style="background:#e63946;color:#fff;padding:4px 12px;border-radius:4px;font-weight:bold;font-size:13px;">&#128308; LIVE NOW</span>
            <span style="color:#aaa;font-size:13px;">${live.length} match${live.length > 1 ? 'es' : ''} live</span>
        </div>`;
        html += live.map(m => matchCard(m)).join('');
    }

    if (upcoming.length > 0) {
        html += `<div style="grid-column:1/-1;display:flex;align-items:center;gap:10px;margin:16px 0 4px;">
            <span style="background:#f39c12;color:#fff;padding:4px 12px;border-radius:4px;font-weight:bold;font-size:13px;">&#128336; UPCOMING</span>
            <span style="color:#aaa;font-size:13px;">${upcoming.length} match${upcoming.length > 1 ? 'es' : ''} today</span>
        </div>`;
        html += upcoming.map(m => matchCard(m)).join('');
    }

    grid.innerHTML = html;
}

function matchCard(m) {
    const home = m.homeName || m.title.split(' vs ')[0] || 'Home';
    const away = m.awayName || m.title.split(' vs ')[1] || 'Away';
    const homeInitial = home.substring(0, 3).toUpperCase();
    const awayInitial = away.substring(0, 3).toUpperCase();
    const isLive = m.isLive;
    const hasScore = m.homeScore !== '' && m.awayScore !== '' && m.homeScore !== undefined;
    const league = m.channel || '';
    const matchTime = m.matchTime || '';
    const homeLogo = m.thumbnail && m.thumbnail.includes('espn') ? m.thumbnail : '';
    const awayLogo = m.awayLogo || '';

    return `
    <div onclick="openStream('${(m.streamUrl||m.pageUrl).replace(/'/g,"\\'").replace(/"/g,'&quot;')}','${(home+' vs '+away).replace(/'/g,"\\'")}')"
         style="background:#1a1a2e;border-radius:10px;overflow:hidden;cursor:pointer;border:1px solid #2a2a4a;transition:all 0.2s;"
         onmouseover="this.style.borderColor='#e63946';this.style.background='#1e1e3a'"
         onmouseout="this.style.borderColor='#2a2a4a';this.style.background='#1a1a2e'">
        <div style="background:#12122a;padding:8px 14px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #2a2a4a;">
            <span style="color:#aaa;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:70%;">${league}</span>
            ${isLive
                ? '<span style="background:#e63946;color:#fff;padding:2px 8px;border-radius:3px;font-size:10px;font-weight:bold;animation:pulse 1.5s infinite;">&#9679; LIVE</span>'
                : `<span style="color:#f39c12;font-size:11px;">&#128336; ${matchTime}</span>`
            }
        </div>
        <div style="padding:16px 14px;display:flex;align-items:center;justify-content:space-between;gap:8px;">
            <div style="flex:1;text-align:center;">
                ${homeLogo
                    ? `<img src="${homeLogo}" style="width:44px;height:44px;object-fit:contain;margin:0 auto 8px;display:block;" onerror="this.style.display='none'">`
                    : `<div style="width:44px;height:44px;background:#2a2a4a;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;font-weight:bold;color:#fff;font-size:12px;">${homeInitial}</div>`
                }
                <div style="color:#fff;font-size:12px;font-weight:600;line-height:1.3;">${home}</div>
            </div>
            <div style="text-align:center;flex-shrink:0;min-width:50px;">
                ${hasScore && isLive
                    ? `<div style="color:#fff;font-weight:bold;font-size:22px;">${m.homeScore} - ${m.awayScore}</div><div style="color:#e63946;font-size:10px;margin-top:2px;">LIVE</div>`
                    : isLive
                        ? '<div style="color:#e63946;font-weight:bold;font-size:14px;">LIVE</div>'
                        : '<div style="color:#aaa;font-weight:bold;font-size:16px;">VS</div>'
                }
            </div>
            <div style="flex:1;text-align:center;">
                ${awayLogo
                    ? `<img src="${awayLogo}" style="width:44px;height:44px;object-fit:contain;margin:0 auto 8px;display:block;" onerror="this.style.display='none'">`
                    : `<div style="width:44px;height:44px;background:#2a2a4a;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;font-weight:bold;color:#fff;font-size:12px;">${awayInitial}</div>`
                }
                <div style="color:#fff;font-size:12px;font-weight:600;line-height:1.3;">${away}</div>
            </div>
        </div>
        <div style="padding:0 14px 14px;">
            <button style="width:100%;background:${isLive ? '#e63946' : '#2a2a4a'};color:#fff;border:none;padding:9px;border-radius:6px;font-weight:bold;font-size:13px;cursor:pointer;"
                onmouseover="this.style.background='${isLive ? '#c0392b' : '#3a3a6a'}'"
                onmouseout="this.style.background='${isLive ? '#e63946' : '#2a2a4a'}'"
            >${isLive ? '&#128308; Watch Live' : '&#128336; Watch on CricFy'}</button>
        </div>
    </div>`;
}

function filterLive(source) {
    document.querySelectorAll('[id^="filter_"]').forEach(b => b.style.background = '#2a2a4a');
    const activeBtn = document.getElementById('filter_' + source.replace(/ /g,'_').toLowerCase());
    if (activeBtn) activeBtn.style.background = '#e63946';
    if (source === 'all') {
        renderLiveMatches(allLiveMatches);
    } else if (source === 'live') {
        renderLiveMatches(allLiveMatches.filter(m => m.isLive));
    } else if (source === 'upcoming') {
        renderLiveMatches(allLiveMatches.filter(m => !m.isLive));
    } else {
        renderLiveMatches(allLiveMatches.filter(m => m.channel === source));
    }
}

function closeLiveSports() {
    document.getElementById('liveSportsPage').style.display = 'none';
    document.body.style.overflow = '';
    closeLiveStreamFrame();
}

function openStream(url, title) {
    const frameDiv = document.getElementById('liveStreamFrame');
    const iframe = document.getElementById('liveStreamIframe');
    const titleEl = document.getElementById('liveStreamTitle');
    titleEl.textContent = title;
    iframe.src = url;
    frameDiv.style.display = 'block';
    frameDiv.scrollIntoView({ behavior: 'smooth' });
}

function closeLiveStreamFrame() {
    const frameDiv = document.getElementById('liveStreamFrame');
    const iframe = document.getElementById('liveStreamIframe');
    if (iframe) iframe.src = '';
    if (frameDiv) frameDiv.style.display = 'none';
}

// Music Radio
function openMusicRadio() {
    document.getElementById('musicRadioPage').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeMusicRadio() {
    stopRadio();
    document.getElementById('musicRadioPage').style.display = 'none';
    document.body.style.overflow = '';
}

function playRadio(url, title) {
    const playerDiv = document.getElementById('radioPlayerDiv');
    const iframe = document.getElementById('radioIframe');
    const titleEl = document.getElementById('radioTitle');
    titleEl.textContent = '🎵 Now Playing: ' + title;
    iframe.src = url;
    playerDiv.style.display = 'block';
    playerDiv.scrollIntoView({ behavior: 'smooth' });
}

function stopRadio() {
    const iframe = document.getElementById('radioIframe');
    const playerDiv = document.getElementById('radioPlayerDiv');
    iframe.src = '';
    playerDiv.style.display = 'none';
}
