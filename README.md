# 🎵 TuneStreamX

**Stream It. Feel It. Enjoy It.**

A modern, Spotify-like music streaming web application built with Flask and yt-dlp. Discover, stream, and enjoy 1800+ songs across trending hits, top charts, and personalized recommendations.

## ✨ Features

- 🎧 **Stream Music** - Instant playback with YouTube embed player
- 🔥 **Trending** - 600 viral songs and chart toppers
- 🏆 **Top Charts** - 600 songs from Billboard, Spotify, Apple Music
- 💖 **For You** - 600 personalized songs across 12 genres
- 🔍 **Smart Search** - Find any song with autocomplete suggestions
- 🎭 **Theater Mode** - Full-screen streaming experience
- 🌓 **Dark/Light Theme** - Toggle between themes
- 👁️ **View Counts** - See song popularity
- ❤️ **Like System** - Save your favorite tracks
- 📱 **Responsive Design** - Works on all devices
- 💬 **WhatsApp Support** - Direct support contact

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/fellowz-arch/tunestreamX.git
cd tunestreamX
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and visit:
```
http://localhost:5000
```

## 📦 Dependencies

- Flask - Web framework
- yt-dlp - YouTube data extraction
- concurrent.futures - Parallel processing

## 🎨 Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **API**: YouTube Data via yt-dlp
- **Styling**: Custom CSS with dark/light themes
- **Performance**: ThreadPoolExecutor for parallel API calls

## 🌟 Key Features Explained

### Music Discovery
- **1800+ Songs** loaded across all tabs
- **10-12 parallel API calls** for fast loading
- **Smart deduplication** ensures unique tracks
- **Genre diversity** from Pop to Jazz

### Streaming Experience
- **Instant playback** with YouTube embed
- **Theater mode** for immersive viewing
- **Bottom player bar** for continuous listening
- **Expand/minimize controls**

### User Interface
- **7-column grid** on large screens
- **Responsive layout** adapts to all devices
- **Smooth animations** and hover effects
- **Loading indicators** for better UX

## 📱 Deployment

### Render
1. Push code to GitHub
2. Connect repository to Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`

### Railway
1. Connect GitHub repository
2. Auto-deploys on push
3. No configuration needed

### Vercel
1. Import GitHub repository
2. Uses `vercel.json` configuration
3. Automatic deployment

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Developer

Created by **fellowz-arch**

## 📞 Support

For support, contact via WhatsApp: +233103024172

## 🎯 Roadmap

- [ ] User authentication
- [ ] Playlist creation
- [ ] Download functionality (local only)
- [ ] Social sharing
- [ ] Advanced search filters
- [ ] Recently played history

## ⚡ Performance

- **Lightning fast**: 1800 songs load in under 10 seconds
- **Optimized API calls**: 1-second timeout per request
- **Parallel processing**: Up to 12 concurrent workers
- **Smart caching**: Prevents duplicate API calls

## 🎵 Music Categories

### Trending (600 songs)
- Viral songs 2024
- Chart toppers
- Popular music
- Hot songs

### Top (600 songs)
- Billboard Hot 100
- Spotify Top 50
- Apple Music Charts
- YouTube Trending

### For You (600 songs)
- Pop, Hip Hop, Rock
- Electronic, R&B, Country
- Indie, Latin, Jazz
- Reggae, Folk, Blues

---

**Made with ❤️ by fellowz-arch**
