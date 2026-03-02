# TuneStreamX 🎵

A modern music and video streaming platform with YouTube-style interface, featuring music, sports, movies, and more.

## Features

### 🎵 Content Streaming
- Music streaming with trending, top hits, and personalized recommendations
- Football highlights and live matches
- Wrestling events (WWE, WrestleMania, SmackDown)
- Movie trailers and full HD content

### 🎨 User Interface
- YouTube-style layout with dark/light theme toggle
- Responsive design for mobile and desktop
- Auto-hiding video navigation controls
- Search with intelligent suggestions
- Related videos sidebar
- Auto-scrolling comments section

### 📺 Video Player
- HD video playback
- Previous/Next navigation buttons
- Auto-hide controls (3-second timeout)
- Related videos recommendations
- AI-generated comments with auto-scroll

### 💰 Ads System
- Pre-roll video ads (5-second skip timer)
- HD video ad playback
- Clickable "Learn More" buttons with custom URLs
- Ad view tracking
- Admin panel for ad management

### 👤 Authentication
- Email/Password signup and login
- Google OAuth integration
- Apple ID integration
- GitHub OAuth integration
- Automated welcome emails

### 🛡️ Admin Panel
- User management (view, ban, delete)
- Content moderation
- Ad management (upload, delete, track views)
- Reports and analytics
- Revenue tracking
- System statistics dashboard

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TuneStreamX.git
cd TuneStreamX
```

2. Install dependencies:
```bash
pip install flask yt-dlp
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Admin Panel Access

Access the admin panel at:
```
http://localhost:5000/admin
```

## Project Structure

```
TuneStreamX/
├── app.py                 # Main Flask application
├── templates/
│   ├── index.html        # Main app interface
│   ├── admin.html        # Admin panel
│   └── creator.html      # Creator dashboard
├── static/
│   ├── script.js         # Main JavaScript
│   ├── yt-layout.css     # Styles
│   ├── ads/              # Uploaded ad videos
│   └── logo files        # App logos
└── README.md
```

## Technologies Used

- **Backend**: Flask (Python)
- **Video Extraction**: yt-dlp
- **Frontend**: HTML5, CSS3, JavaScript
- **Email**: SMTP (Gmail)
- **Storage**: File system (ads)

## Features in Detail

### Video Categories
- **For You**: Personalized mix of pop, hip hop, rock, and EDM
- **Trending**: Latest trending music
- **Top Music**: Best and viral songs
- **Football**: Live matches, highlights, league content
- **Wrestling**: WWE events and highlights
- **Movies**: Trailers, DJ Afro, animations, full HD movies

### Ad Management
- Upload video files (MP4/WebM)
- Add clickable URLs for ads
- Track ad impressions
- 5-second countdown before skip
- HD video quality

### Mobile Optimization
- Responsive layout
- Touch-friendly controls
- Bottom navigation bar
- Optimized video player
- Hidden comments on mobile

## Configuration

### Email Setup
Update the email credentials in `app.py`:
```python
sender_email = 'your-email@gmail.com'
sender_password = 'your-app-password'
```

### Secret Key
Change the secret key in production:
```python
app.secret_key = 'your-secret-key-change-this-in-production'
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For support, contact via WhatsApp: +254103024172

## Author

Created with ❤️ by FELLOWZ_JNR TECH

---

**Stream It. Feel It. Enjoy It.** 🎵
