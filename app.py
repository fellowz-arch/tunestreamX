from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import yt_dlp
import os
import time
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Security decorator for admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In production, implement proper authentication
        # For demo purposes, we'll use a simple session check
        if not session.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Security decorator for creator routes
def creator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In production, implement proper authentication
        if not session.get('is_creator') and not session.get('is_admin'):
            return jsonify({'error': 'Creator access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Demo login routes (replace with proper auth in production)
@app.route('/admin/login')
def admin_login():
    session['is_admin'] = True  # Demo only
    return redirect('/admin')

@app.route('/creator/login')
def creator_login():
    session['is_creator'] = True  # Demo only
    return redirect('/creator')

@app.route('/test')
def test():
    return jsonify({
        'status': 'ok',
        'message': 'API is working',
        'test_songs': [
            {
                'id': 'dQw4w9WgXcQ',
                'title': 'Test Song 1',
                'duration': 213,
                'thumbnail': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg',
                'channel': 'Test Artist',
                'views': 1000000,
                'likes': 50000
            },
            {
                'id': 'kJQP7kiw5Fk',
                'title': 'Test Song 2',
                'duration': 180,
                'thumbnail': 'https://i.ytimg.com/vi/kJQP7kiw5Fk/hqdefault.jpg',
                'channel': 'Test Artist 2',
                'views': 2000000,
                'likes': 100000
            }
        ]
    })

@app.route('/')
def index():
    return render_template('index.html')

def fetch_videos(term, max_results=100):
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True, 'socket_timeout': 10}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f'ytsearch{max_results}:{term}', download=False)
            videos = []
            if result and 'entries' in result:
                for v in result['entries']:
                    if v and v.get('duration'):
                        videos.append({
                            'id': v['id'],
                            'title': v['title'],
                            'duration': v.get('duration', 0),
                            'thumbnail': f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg",
                            'channel': v.get('channel', 'Unknown'),
                            'views': random.randint(100000, 50000000),
                            'likes': random.randint(1000, 500000)
                        })
            return videos
    except Exception as e:
        print(f"Error fetching {term}: {e}")
        return []

@app.route('/trending')
def trending():
    print("Trending endpoint called")
    try:
        videos = fetch_videos('music 2024', 50)
        print(f"Fetched {len(videos)} videos")
        return jsonify(videos)
    except Exception as e:
        print(f"Error in trending: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])

@app.route('/top')
def top():
    import random
    top_terms = ['top songs 2024', 'best music', 'viral songs']
    all_videos = []
    seen = set()
    
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(fetch_videos, term, 50) for term in top_terms]
            for future in as_completed(futures, timeout=15):
                try:
                    videos = future.result()
                    for v in videos:
                        if v['id'] not in seen:
                            all_videos.append(v)
                            seen.add(v['id'])
                except Exception as e:
                    print(f"Error processing future: {e}")
                    continue
    except Exception as e:
        print(f"Error in top: {e}")
    
    if all_videos:
        random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/foryou')
def foryou():
    import random
    genres = ['pop music', 'hip hop', 'rock music', 'edm music']
    all_videos = []
    seen = set()
    
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(fetch_videos, genre, 50) for genre in genres]
            for future in as_completed(futures, timeout=15):
                try:
                    videos = future.result()
                    for v in videos:
                        if v['id'] not in seen:
                            all_videos.append(v)
                            seen.add(v['id'])
                except Exception as e:
                    print(f"Error processing future: {e}")
                    continue
    except Exception as e:
        print(f"Error in foryou: {e}")
    
    if all_videos:
        random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True, 'socket_timeout': 10}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(f"ytsearch100:{query}", download=False)
            videos = []
            
            for v in result['entries']:
                if v and v.get('duration'):
                    videos.append({
                        'id': v['id'],
                        'title': v['title'],
                        'duration': v.get('duration', 0),
                        'thumbnail': f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg",
                        'channel': v.get('channel', 'Unknown'),
                        'views': random.randint(100000, 50000000),
                        'likes': random.randint(1000, 500000)
                    })
            
            return jsonify(videos)
        except Exception as e:
            print(f"Search error: {e}")
            return jsonify([])

@app.route('/suggestions')
def suggestions():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    try:
        import urllib.request
        import json
        url = f'https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={urllib.parse.quote(query)}'
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
            return jsonify(data[1] if len(data) > 1 else [])
    except Exception as e:
        print(f"Suggestions error: {e}")
        return jsonify([])

@app.route('/football')
def football():
    import random
    terms = ['football live', 'football highlights today', 'premier league highlights', 'la liga highlights', 'champions league', 'football matches']
    all_videos = []
    seen = set()
    
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(fetch_videos, term, 20) for term in terms]
            for future in as_completed(futures, timeout=30):
                try:
                    videos = future.result()
                    for v in videos:
                        if v['id'] not in seen:
                            all_videos.append(v)
                            seen.add(v['id'])
                except Exception as e:
                    print(f"Error processing future: {e}")
                    continue
    except Exception as e:
        print(f"Error in football: {e}")
    
    if all_videos:
        random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/wrestling')
def wrestling():
    videos = fetch_videos('wwe wrestling highlights', 30)
    return jsonify(videos)

@app.route('/movies')
def movies():
    videos = fetch_videos('movie trailers', 30)
    return jsonify(videos)

@app.route('/library')
def library_page():
    return jsonify([])

@app.route('/settings')
def settings():
    return jsonify([])

@app.route('/shorts')
def shorts():
    return jsonify([])

@app.route('/profile')
def profile():
    return jsonify([])

# Super Admin Panel (Secure)
@app.route('/admin')
# @admin_required  # Uncomment in production
def admin():
    return render_template('admin.html')

@app.route('/admin/stats')
# @admin_required  # Uncomment in production
def admin_stats():
    return jsonify({
        'totalUsers': 1247,
        'activeSessions': 89,
        'totalVideos': 15420,
        'totalViews': 2847392,
        'totalRevenue': 12450.75,
        'reportedContent': 23,
        'bannedUsers': 5
    })

@app.route('/admin/users')
def admin_users():
    return jsonify([
        {'email': 'user1@example.com', 'joined': '2024-01-15', 'status': 'Active', 'videos': 12, 'views': 45000},
        {'email': 'creator@example.com', 'joined': '2024-02-01', 'status': 'Creator', 'videos': 89, 'views': 250000},
        {'email': 'banned@example.com', 'joined': '2024-01-20', 'status': 'Banned', 'videos': 0, 'views': 0}
    ])

@app.route('/admin/content')
def admin_content():
    return jsonify([
        {'id': 'dQw4w9WgXcQ', 'title': 'Popular Song', 'category': 'Music', 'views': 1000000, 'status': 'Active', 'reports': 0},
        {'id': 'kJQP7kiw5Fk', 'title': 'Trending Video', 'category': 'Entertainment', 'views': 500000, 'status': 'Active', 'reports': 2},
        {'id': 'xyz123abc', 'title': 'Reported Content', 'category': 'Music', 'views': 10000, 'status': 'Under Review', 'reports': 15}
    ])

@app.route('/admin/reports')
def admin_reports():
    return jsonify([
        {'id': 1, 'contentId': 'xyz123abc', 'reason': 'Copyright violation', 'reporter': 'user@example.com', 'date': '2024-01-20', 'status': 'Pending'},
        {'id': 2, 'contentId': 'abc456def', 'reason': 'Inappropriate content', 'reporter': 'another@example.com', 'date': '2024-01-19', 'status': 'Resolved'}
    ])

@app.route('/admin/delete-user', methods=['POST'])
def delete_user():
    data = request.json
    email = data.get('email')
    return jsonify({'success': True, 'message': f'User {email} deleted'})

@app.route('/admin/ban-user', methods=['POST'])
def ban_user():
    data = request.json
    email = data.get('email')
    return jsonify({'success': True, 'message': f'User {email} banned'})

@app.route('/admin/delete-content', methods=['POST'])
def delete_content():
    data = request.json
    content_id = data.get('contentId')
    return jsonify({'success': True, 'message': f'Content {content_id} deleted'})

# Ads storage (in production, use a database)
ads_storage = []
ad_views = {}

ADS_FOLDER = Path('static/ads')
ADS_FOLDER.mkdir(exist_ok=True)

@app.route('/admin/ads')
def admin_ads():
    return jsonify([{
        'id': ad['id'],
        'title': ad['title'],
        'videoFile': ad.get('videoFile'),
        'clickUrl': ad.get('clickUrl'),
        'views': ad_views.get(ad['id'], 0),
        'uploaded': ad['uploaded']
    } for ad in ads_storage])

@app.route('/admin/upload-ad', methods=['POST'])
def upload_ad():
    try:
        if 'videoFile' in request.files:
            file = request.files['videoFile']
            title = request.form.get('title')
            click_url = request.form.get('clickUrl')
            
            if file and title:
                ad_id = str(int(time.time()))
                filename = f"ad_{ad_id}.mp4"
                filepath = ADS_FOLDER / filename
                file.save(filepath)
                
                ad = {
                    'id': ad_id,
                    'title': title,
                    'videoFile': f'/static/ads/{filename}',
                    'clickUrl': click_url,
                    'uploaded': time.strftime('%Y-%m-%d')
                }
                ads_storage.append(ad)
                ad_views[ad_id] = 0
                return jsonify({'success': True, 'ad': ad})
        
        return jsonify({'success': False, 'error': 'No video file provided'}), 400
    except Exception as e:
        print(f'Upload ad error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/delete-ad', methods=['POST'])
def delete_ad():
    data = request.json
    ad_id = data.get('adId')
    global ads_storage
    ads_storage = [ad for ad in ads_storage if ad['id'] != ad_id]
    return jsonify({'success': True})

@app.route('/get-ad')
def get_ad():
    if ads_storage:
        ad = random.choice(ads_storage)
        return jsonify(ad)
    return jsonify(None)

@app.route('/track-ad-view', methods=['POST'])
def track_ad_view():
    data = request.json
    ad_id = data.get('adId')
    if ad_id in ad_views:
        ad_views[ad_id] += 1
    else:
        ad_views[ad_id] = 1
    return jsonify({'success': True})

# Creator Dashboard (Like YouTube Studio)
@app.route('/creator')
# @creator_required  # Uncomment in production
def creator_dashboard():
    return render_template('creator.html')

@app.route('/creator/stats')
# @creator_required  # Uncomment in production
def creator_stats():
    return jsonify({
        'totalViews': 125000,
        'subscribers': 1250,
        'totalVideos': 45,
        'earnings': 850.25,
        'watchTime': 15420,
        'avgViewDuration': '3:45'
    })

@app.route('/creator/videos')
def creator_videos():
    return jsonify([
        {'id': 'abc123', 'title': 'My Latest Song', 'views': 25000, 'likes': 1200, 'status': 'Published', 'earnings': 125.50},
        {'id': 'def456', 'title': 'Behind the Scenes', 'views': 15000, 'likes': 800, 'status': 'Published', 'earnings': 75.25},
        {'id': 'ghi789', 'title': 'New Track Preview', 'views': 5000, 'likes': 300, 'status': 'Draft', 'earnings': 0}
    ])

@app.route('/creator/analytics')
def creator_analytics():
    return jsonify({
        'viewsData': [1200, 1500, 1800, 2200, 1900, 2500, 3000],
        'subscribersData': [10, 15, 12, 20, 18, 25, 30],
        'topVideos': [
            {'title': 'My Latest Song', 'views': 25000},
            {'title': 'Behind the Scenes', 'views': 15000},
            {'title': 'New Track Preview', 'views': 5000}
        ]
    })

@app.route('/creator/upload', methods=['POST'])
def creator_upload():
    data = request.json
    return jsonify({'success': True, 'message': 'Video uploaded successfully', 'videoId': 'new123'})

@app.route('/send-welcome-email', methods=['POST'])
def send_welcome_email():
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    data = request.json
    user_email = data.get('email')
    
    if not user_email:
        return jsonify({'success': False, 'error': 'Email required'})
    
    try:
        sender_email = 'fellowz9771@gmail.com'
        sender_password = 'oujh zclz dpnj awlf'
        
        message = MIMEMultipart('alternative')
        message['Subject'] = 'Welcome to TuneStreamX! 🎉'
        message['From'] = sender_email
        message['To'] = user_email
        
        html = f'''
        <html>
            <body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px;">
                    <h1 style="color: #6366f1; text-align: center;">🎉 Welcome to TuneStreamX!</h1>
                    <p style="font-size: 16px; color: #333;">Hi there,</p>
                    <p style="font-size: 16px; color: #333;">Thank you for joining TuneStreamX! We're excited to have you on board.</p>
                    
                    <h2 style="color: #6366f1; margin-top: 30px;">Here's what you can do:</h2>
                    
                    <div style="margin: 20px 0;">
                        <h3 style="color: #333;">🎵 Stream Music & Videos</h3>
                        <p style="color: #666;">Browse trending songs, top hits, and personalized recommendations</p>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <h3 style="color: #333;">⚽ Watch Sports</h3>
                        <p style="color: #666;">Live football, wrestling, and sports highlights from around the world</p>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <h3 style="color: #333;">🎬 Discover Movies</h3>
                        <p style="color: #666;">Latest trailers, full HD movies, and animated content</p>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <h3 style="color: #333;">🔍 Smart Search</h3>
                        <p style="color: #666;">Find anything with our intelligent search and suggestions</p>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <h3 style="color: #333;">🌙 Dark/Light Mode</h3>
                        <p style="color: #666;">Toggle between themes for comfortable viewing anytime</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 40px;">
                        <a href="http://localhost:5000" style="background: #6366f1; color: white; padding: 12px 32px; text-decoration: none; border-radius: 8px; font-weight: bold;">Start Exploring</a>
                    </div>
                    
                    <p style="margin-top: 40px; color: #999; font-size: 14px; text-align: center;">If you have any questions, feel free to reach out to us!</p>
                </div>
            </body>
        </html>
        '''
        
        part = MIMEText(html, 'html')
        message.attach(part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, message.as_string())
        
        return jsonify({'success': True})
    except Exception as e:
        print(f'Email error: {e}')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/auth/google/callback')
def google_callback():
    return render_template('index.html')

@app.route('/auth/apple/callback')
def apple_callback():
    return render_template('index.html')

@app.route('/auth/github/callback')
def github_callback():
    return render_template('index.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)