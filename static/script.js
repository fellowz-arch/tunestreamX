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
    const profileBtn = document.querySelector('.icon-btn[onclick="openLoginModal()"]');
    if (profileBtn) {
        profileBtn.innerHTML = '✓';
        profileBtn.title = email;
    }
}

document.addEventListener('click', (e) => {
    const modal = document.getElementById('loginModal');
    if (e.target === modal) {
        closeLoginModal();
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
    
    // Track session
    trackSession();
    
    // Track install if first time
    if (!localStorage.getItem('appInstalled')) {
        trackInstall();
        localStorage.setItem('appInstalled', 'true');
    }
    
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
    adVideo.muted = true; // Add muted for autoplay to work
    adVideo.controls = false;
    
    // Add error handling
    adVideo.onerror = () => {
        console.error('Ad video failed to load:', adVideoFile);
        adOverlay.remove();
        playMainVideo(mainVideoId);
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
    });
    
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
