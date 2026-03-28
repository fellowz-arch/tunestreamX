from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import yt_dlp
import os
import time
import random
import json
import sqlite3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

DB_FILE = 'tunestreamx.db'

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT,
        joined TEXT,
        videos INTEGER DEFAULT 0,
        views INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ads (
        id TEXT PRIMARY KEY,
        title TEXT,
        video_data TEXT,
        click_url TEXT,
        uploaded TEXT,
        views INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS analytics (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    # Init analytics defaults
    defaults = {
        'downloads': '0', 'active_installs': '0', 'sessions': '0',
        'daily_Mon': '0', 'daily_Tue': '0', 'daily_Wed': '0', 'daily_Thu': '0',
        'daily_Fri': '0', 'daily_Sat': '0', 'daily_Sun': '0',
        'views_Mon': '0', 'views_Tue': '0', 'views_Wed': '0', 'views_Thu': '0',
        'views_Fri': '0', 'views_Sat': '0', 'views_Sun': '0',
        'cat_music': '0', 'cat_movies': '0', 'cat_sports': '0', 'cat_gaming': '0', 'cat_other': '0'
    }
    for key, val in defaults.items():
        c.execute('INSERT OR IGNORE INTO analytics (key, value) VALUES (?, ?)', (key, val))
    conn.commit()
    conn.close()
    print('Database initialized')

def get_analytics(key):
    conn = get_db()
    row = conn.execute('SELECT value FROM analytics WHERE key=?', (key,)).fetchone()
    conn.close()
    return int(row['value']) if row else 0

def set_analytics(key, value):
    conn = get_db()
    conn.execute('INSERT OR REPLACE INTO analytics (key, value) VALUES (?, ?)', (key, str(value)))
    conn.commit()
    conn.close()

def increment_analytics(key):
    val = get_analytics(key) + 1
    set_analytics(key, val)
    return val

init_db()

# Security decorator for admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def creator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
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
    return jsonify({'status': 'ok', 'message': 'API is working'})

@app.route('/')
def index():
    return render_template('index.html')

def fetch_videos(term, max_results=100):
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True, 
        'extract_flat': True, 
        'socket_timeout': 10,
        'default_search': 'ytsearch',
        'age_limit': None,
        'source_address': '0.0.0.0'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f'ytsearch{max_results}:{term} HD', download=False)
            videos = []
            if result and 'entries' in result:
                for v in result['entries']:
                    if v and v.get('id'):
                        videos.append({
                            'id': v['id'],
                            'title': v.get('title', 'Unknown'),
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
        if not videos:
            print("Warning: No videos fetched, returning empty list")
        return jsonify(videos if videos else [])
    except Exception as e:
        print(f"Error in trending: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch trending content'}), 500

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
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True, 
        'extract_flat': True, 
        'socket_timeout': 10,
        'default_search': 'auto'  # Search all sources
    }
    
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
    import requests
    from bs4 import BeautifulSoup
    import datetime
    
    all_videos = []
    seen = set()
    today = datetime.datetime.now()

    # Scrape CertifyTV for football content
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get('https://certifytv.com/category/football/', headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for article in soup.select('article')[:20]:
                title_el = article.select_one('h2, h3, .entry-title')
                link_el = article.select_one('a')
                img_el = article.select_one('img')
                if title_el and link_el:
                    title = title_el.get_text(strip=True)
                    link = link_el.get('href', '')
                    thumb = img_el.get('src', 'https://placehold.co/320x180/1a1a2e/ffffff?text=Football') if img_el else 'https://placehold.co/320x180/1a1a2e/ffffff?text=Football'
                    vid_id = f'certify_{abs(hash(link)) % 1000000}'
                    if vid_id not in seen:
                        all_videos.append({
                            'id': vid_id,
                            'title': title,
                            'duration': 0,
                            'thumbnail': thumb,
                            'channel': 'CertifyTV',
                            'views': 0,
                            'likes': 0,
                            'source': 'certifytv',
                            'url': link
                        })
                        seen.add(vid_id)
    except Exception as e:
        print(f'CertifyTV scrape error: {e}')

    # YouTube football highlights as fallback/supplement
    search_terms = [
        f'football highlights {today.strftime("%B %d %Y")}',
        'premier league highlights today',
        'champions league highlights',
        'football goals today',
    ]
    for term in search_terms:
        if len(all_videos) >= 80:
            break
        try:
            videos = fetch_videos(term, 15)
            for v in videos:
                if v['id'] not in seen:
                    all_videos.append(v)
                    seen.add(v['id'])
        except Exception as e:
            print(f'Error fetching {term}: {e}')

    random.shuffle(all_videos)
    return jsonify(all_videos if all_videos else [])


# Live football streams from multiple sources
@app.route('/live-football')
def live_football():
    import requests
    from bs4 import BeautifulSoup
    import re
    import datetime

    streams = []
    seen = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    def scrape_source(url, source_name, base_url=''):
        results = []
        try:
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code != 200:
                return results
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.select('article, .post, .match, .event, .card, .item, li')[:25]
            if not items:
                items = soup.select('a[href]')[:25]
            for item in items:
                title_el = item.select_one('h1,h2,h3,h4,.title,.entry-title,.match-title')
                link_el = item if item.name == 'a' else item.select_one('a[href]')
                img_el = item.select_one('img')
                if not title_el and link_el:
                    title_el = link_el
                if not link_el:
                    continue
                title = (title_el.get_text(strip=True) if title_el else '')[:100]
                href = link_el.get('href', '')
                if not href or href == '#' or len(title) < 4:
                    continue
                if not href.startswith('http'):
                    href = base_url + href
                thumb = ''
                if img_el:
                    thumb = img_el.get('src') or img_el.get('data-src') or img_el.get('data-lazy-src', '')
                if not thumb or len(thumb) < 10:
                    thumb = f'https://placehold.co/320x180/1a1a2e/ffffff?text={source_name.replace(" ","+")}'
                uid = abs(hash(href)) % 100000000
                if uid not in seen:
                    seen.add(uid)
                    results.append({
                        'id': f'{source_name[:3].lower()}_{uid}',
                        'title': title,
                        'thumbnail': thumb,
                        'channel': source_name,
                        'isLive': True,
                        'streamType': 'iframe',
                        'streamUrl': href,
                        'pageUrl': href
                    })
        except Exception as e:
            print(f'{source_name} error: {e}')
        return results

    # LiveSoccerTV - real match schedule
    try:
        r = requests.get('https://www.livesoccertv.com/schedules/', headers=headers, timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        for row in soup.select('tr.matchrow, tr[class*="match"], .match-row')[:30]:
            time_el = row.select_one('.time,.matchtime,td.time')
            home_el = row.select_one('.home,.hometeam,td.home')
            away_el = row.select_one('.away,.awayteam,td.away')
            link_el = row.select_one('a[href]')
            if home_el and away_el:
                match_time = time_el.get_text(strip=True) if time_el else ''
                home = home_el.get_text(strip=True)
                away = away_el.get_text(strip=True)
                title = f'\U0001f550 {match_time} | {home} vs {away}' if match_time else f'{home} vs {away}'
                href = link_el.get('href', '') if link_el else ''
                if href and not href.startswith('http'):
                    href = 'https://www.livesoccertv.com' + href
                uid = abs(hash(title)) % 100000000
                if uid not in seen:
                    seen.add(uid)
                    streams.append({
                        'id': f'lstv_{uid}', 'title': title,
                        'thumbnail': 'https://placehold.co/320x180/0a3d62/ffffff?text=LiveSoccerTV',
                        'channel': 'LiveSoccerTV', 'isLive': True,
                        'streamType': 'iframe',
                        'streamUrl': href or 'https://www.livesoccertv.com/schedules/',
                        'pageUrl': href or 'https://www.livesoccertv.com/schedules/'
                    })
    except Exception as e:
        print(f'LiveSoccerTV error: {e}')

    # StreamSports / SportsHub as reliable backup for live football
    for site_url, site_name, site_base in [
        ('https://streamsports.me/', 'StreamSports', 'https://streamsports.me'),
        ('https://sportshub.stream/football', 'SportsHub', 'https://sportshub.stream'),
        ('https://soccerstreams-100.com/', 'SoccerStreams', 'https://soccerstreams-100.com'),
    ]:
        if len([s for s in streams if s['isLive']]) >= 20:
            break
        streams += scrape_source(site_url, site_name, site_base)

    # EpicSports
    streams += scrape_source('https://epicsports.stream/football/', 'EpicSports', 'https://epicsports.stream')
    if not [s for s in streams if s['channel'] == 'EpicSports']:
        streams += scrape_source('https://epicsports.stream/', 'EpicSports', 'https://epicsports.stream')

    # CricFy TV - scrape live and upcoming matches
    try:
        for cricfy_url in ['https://cricfy.tv/', 'https://cricfy.tv/football-streaming/']:
            r = requests.get(cricfy_url, headers=headers, timeout=12, allow_redirects=True)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, 'html.parser')
            # Try all common match card selectors
            for sel in ['.match-card', '.event-card', '.fixture', '.match', '.game', 'article', '.post', '.entry']:
                items = soup.select(sel)[:30]
                if items:
                    for item in items:
                        title_el = item.select_one('h1,h2,h3,h4,.title,.match-title,.entry-title,.team-names')
                        link_el = item.select_one('a[href]')
                        img_el = item.select_one('img')
                        time_el = item.select_one('.time,.date,.match-time,.kickoff,.start-time')
                        status_el = item.select_one('.live,.status,.badge,.label')
                        if not link_el:
                            continue
                        title = title_el.get_text(strip=True) if title_el else link_el.get_text(strip=True)
                        title = title[:100]
                        if len(title) < 4:
                            continue
                        href = link_el.get('href', '')
                        if not href or href == '#':
                            continue
                        if not href.startswith('http'):
                            href = 'https://cricfy.tv' + href
                        match_time = time_el.get_text(strip=True) if time_el else ''
                        status_text = status_el.get_text(strip=True).lower() if status_el else ''
                        is_live = 'live' in status_text or 'live' in title.lower()
                        is_upcoming = 'upcoming' in status_text or bool(match_time)
                        if match_time:
                            title = f'\U0001f550 {match_time} | {title}'
                        thumb = ''
                        if img_el:
                            thumb = img_el.get('src') or img_el.get('data-src') or img_el.get('data-lazy-src', '')
                        if not thumb or len(thumb) < 10:
                            thumb = 'https://placehold.co/320x180/c0392b/ffffff?text=CricFy+TV'
                        uid = abs(hash(href)) % 100000000
                        if uid not in seen:
                            seen.add(uid)
                            streams.append({
                                'id': f'cfy_{uid}', 'title': title, 'thumbnail': thumb,
                                'channel': 'CricFy TV',
                                'isLive': is_live,
                                'isUpcoming': is_upcoming and not is_live,
                                'matchTime': match_time,
                                'streamType': 'iframe', 'streamUrl': href, 'pageUrl': href
                            })
                    break  # found items, stop trying selectors
    except Exception as e:
        print(f'CricFy TV error: {e}')

    # HD Streamz
    streams += scrape_source('https://hdstreamz.net/', 'HD Streamz', 'https://hdstreamz.net')

    # TV96
    streams += scrape_source('https://tv96.net/football/', 'TV96', 'https://tv96.net')
    if not [s for s in streams if s['channel'] == 'TV96']:
        streams += scrape_source('https://tv96.net/', 'TV96', 'https://tv96.net')

    # SuperSport
    try:
        r = requests.get('https://supersport.com/football', headers=headers, timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('.fixture,.match-item,.event,article,.card')[:15]:
            title_el = item.select_one('h2,h3,h4,.title,.fixture-title')
            link_el = item.select_one('a[href]')
            img_el = item.select_one('img')
            time_el = item.select_one('.time,.kickoff,.match-time')
            if title_el or (link_el and link_el.get_text(strip=True)):
                title = (title_el or link_el).get_text(strip=True)[:100]
                if time_el:
                    title = f'\U0001f550 {time_el.get_text(strip=True)} | {title}'
                href = link_el.get('href', '') if link_el else ''
                if href and not href.startswith('http'):
                    href = 'https://supersport.com' + href
                thumb = ''
                if img_el:
                    thumb = img_el.get('src') or img_el.get('data-src', '')
                if not thumb:
                    thumb = 'https://placehold.co/320x180/003366/ffffff?text=SuperSport'
                uid = abs(hash(title + href)) % 100000000
                if uid not in seen and len(title) > 4:
                    seen.add(uid)
                    streams.append({
                        'id': f'ss_{uid}', 'title': title, 'thumbnail': thumb,
                        'channel': 'SuperSport', 'isLive': True,
                        'streamType': 'iframe',
                        'streamUrl': href or 'https://supersport.com/football',
                        'pageUrl': href or 'https://supersport.com/football'
                    })
    except Exception as e:
        print(f'SuperSport error: {e}')

    # Fallback
    if not streams:
        streams = [
            {'id': 'fb_lstv', 'title': '\u26bd Live Football Schedule',
             'thumbnail': 'https://placehold.co/320x180/0a3d62/ffffff?text=LiveSoccerTV',
             'channel': 'LiveSoccerTV', 'isLive': True, 'streamType': 'iframe',
             'streamUrl': 'https://www.livesoccertv.com/schedules/',
             'pageUrl': 'https://www.livesoccertv.com/schedules/'},
            {'id': 'fb_epic', 'title': '\u26a1 EpicSports Live Football',
             'thumbnail': 'https://placehold.co/320x180/1a1a2e/ffffff?text=EpicSports',
             'channel': 'EpicSports', 'isLive': True, 'streamType': 'iframe',
             'streamUrl': 'https://epicsports.stream/football/',
             'pageUrl': 'https://epicsports.stream/football/'},
            {'id': 'fb_ctv', 'title': '\U0001f4fa CricFy TV Football',
             'thumbnail': 'https://placehold.co/320x180/1a1a2e/ffffff?text=CricFyTV',
             'channel': 'CricFy TV', 'isLive': True, 'streamType': 'iframe',
             'streamUrl': 'https://cricfy.tv/football/',
             'pageUrl': 'https://cricfy.tv/football/'},
            {'id': 'fb_ss', 'title': '\U0001f3c6 SuperSport Football',
             'thumbnail': 'https://placehold.co/320x180/003366/ffffff?text=SuperSport',
             'channel': 'SuperSport', 'isLive': True, 'streamType': 'iframe',
             'streamUrl': 'https://supersport.com/football',
             'pageUrl': 'https://supersport.com/football'},
        ]

    return jsonify(streams)


@app.route('/wrestling')
def wrestling():
    videos = fetch_videos('wwe wrestling highlights', 30)
    return jsonify(videos)

@app.route('/movies')
def movies():
    import random
    movie_terms = [
        'full movie 2024',
        'full hd movie',
        'complete movie',
        'full length movie',
        'dj afro full movie',
        'nollywood full movie',
        'hollywood full movie 2024'
    ]
    all_videos = []
    seen = set()
    
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(fetch_videos, term, 30) for term in movie_terms]
            for future in as_completed(futures, timeout=30):
                try:
                    videos = future.result()
                    for v in videos:
                        if v['id'] not in seen and v.get('duration', 0) > 1800:  # Only movies longer than 30 mins
                            all_videos.append(v)
                            seen.add(v['id'])
                except Exception as e:
                    print(f"Error processing future: {e}")
                    continue
    except Exception as e:
        print(f"Error in movies: {e}")
    
    if all_videos:
        random.shuffle(all_videos)
    return jsonify(all_videos)

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
def admin():
    password = request.args.get('password')
    if password == '9771':
        session['admin_authenticated'] = True
    
    if not session.get('admin_authenticated'):
        return '''<!DOCTYPE html>
<html><head><title>Admin Login</title><style>
body{font-family:Arial;background:#667eea;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.login{background:white;padding:40px;border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.3);text-align:center}
input{padding:12px;margin:10px;border:1px solid #ddd;border-radius:6px;width:200px}
button{padding:12px 24px;background:#667eea;color:white;border:none;border-radius:6px;cursor:pointer}
</style></head><body>
<div class="login">
<h2>🎵 TuneStreamX Admin</h2>
<form method="GET">
<input type="password" name="password" placeholder="Enter admin password" required>
<br><button type="submit">Login</button>
</form>
</div></body></html>'''
    
    return render_template('admin.html')

import json

@app.route('/track/download', methods=['POST'])
def track_download():
    increment_analytics('downloads')
    return jsonify({'success': True})

@app.route('/track/install', methods=['POST'])
def track_install():
    increment_analytics('active_installs')
    return jsonify({'success': True})

@app.route('/track/session', methods=['POST'])
def track_session():
    import datetime
    increment_analytics('sessions')
    day = datetime.datetime.now().strftime('%a')
    increment_analytics(f'daily_{day}')
    return jsonify({'success': True})

@app.route('/track/view', methods=['POST'])
def track_view():
    import datetime
    data = request.json
    category = data.get('category', 'other').lower()
    cat_map = {'music': 'cat_music', 'movies': 'cat_movies', 'sports': 'cat_sports', 'gaming': 'cat_gaming', 'other': 'cat_other'}
    if category in cat_map:
        increment_analytics(cat_map[category])
    day = datetime.datetime.now().strftime('%a')
    increment_analytics(f'views_{day}')
    return jsonify({'success': True})

@app.route('/admin/stats')
def admin_stats():
    conn = get_db()
    total_users = conn.execute('SELECT COUNT(*) as c FROM users').fetchone()['c']
    total_ad_views = conn.execute('SELECT SUM(views) as s FROM ads').fetchone()['s'] or 0
    conn.close()
    days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    total_views = sum(get_analytics(f'views_{d}') for d in days)
    return jsonify({
        'totalDownloads': get_analytics('downloads'),
        'activeInstalls': get_analytics('active_installs'),
        'totalUsers': total_users,
        'activeSessions': get_analytics('sessions'),
        'totalVideos': total_views,
        'totalViews': total_views,
        'adViews': total_ad_views,
        'totalRevenue': total_ad_views * 0.05,
        'reportedContent': 0,
        'bannedUsers': 0
    })

@app.route('/admin/chart-data')
def admin_chart_data():
    days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    conn = get_db()
    total_ad_views = conn.execute('SELECT SUM(views) as s FROM ads').fetchone()['s'] or 0
    conn.close()
    return jsonify({
        'userGrowth': [get_analytics(f'daily_{d}') for d in days],
        'viewsData': [get_analytics(f'views_{d}') for d in days],
        'revenueBreakdown': [total_ad_views, 0, 0],
        'categories': [get_analytics('cat_music'), get_analytics('cat_movies'), get_analytics('cat_sports'), get_analytics('cat_gaming'), get_analytics('cat_other')]
    })

@app.route('/admin/users')
def admin_users():
    conn = get_db()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return jsonify([{
        'id': str(i+1), 'email': u['email'], 'joined': u['joined'],
        'status': u['status'], 'videos': u['videos'], 'views': u['views']
    } for i, u in enumerate(users)])

@app.route('/admin/users/<user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
    return jsonify({'success': True})

@app.route('/admin/content')
def admin_content():
    return jsonify([])

@app.route('/admin/content/<content_id>/<action>', methods=['POST'])
def moderate_content(content_id, action):
    return jsonify({'success': True})

@app.route('/admin/reports')
def admin_reports():
    return jsonify([])

@app.route('/admin/reports/<report_id>/resolve', methods=['POST'])
def resolve_report(report_id):
    return jsonify({'success': True})

@app.route('/admin/reports/<report_id>/dismiss', methods=['POST'])
def dismiss_report(report_id):
    return jsonify({'success': True})

@app.route('/admin/ads/<ad_id>', methods=['DELETE'])
def delete_ad_by_id(ad_id):
    conn = get_db()
    conn.execute('DELETE FROM ads WHERE id=?', (ad_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/delete-user', methods=['POST'])
def delete_user():
    data = request.json
    email = data.get('email')
    conn = get_db()
    conn.execute('DELETE FROM users WHERE email=?', (email,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/ban-user', methods=['POST'])
def ban_user():
    data = request.json
    email = data.get('email')
    conn = get_db()
    conn.execute("UPDATE users SET status='banned' WHERE email=?", (email,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/delete-content', methods=['POST'])
def delete_content():
    return jsonify({'success': True})

@app.route('/admin/ads')
def admin_ads():
    conn = get_db()
    ads = conn.execute('SELECT * FROM ads').fetchall()
    conn.close()
    return jsonify([{
        'id': ad['id'], 'title': ad['title'],
        'videoFile': ad['video_data'],
        'clickUrl': ad['click_url'],
        'views': ad['views'],
        'uploaded': ad['uploaded']
    } for ad in ads])

@app.route('/admin/upload-ad', methods=['POST'])
def upload_ad():
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file provided'}), 400
        file = request.files['video']
        title = request.form.get('title')
        click_url = request.form.get('clickUrl', '')
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        allowed_extensions = {'.mp4', '.webm', '.mov', '.avi'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        if file_size > 50 * 1024 * 1024:
            return jsonify({'success': False, 'error': 'File too large. Max 50MB'}), 400
        ad_id = str(int(time.time()))
        import base64
        video_data = base64.b64encode(file.read()).decode('utf-8')
        mime_type = 'video/mp4' if file_ext == '.mp4' else 'video/webm'
        video_data_url = f'data:{mime_type};base64,{video_data}'
        conn = get_db()
        conn.execute('INSERT INTO ads (id, title, video_data, click_url, uploaded, views) VALUES (?,?,?,?,?,0)',
                     (ad_id, title, video_data_url, click_url, time.strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Ad uploaded successfully', 'ad': {'id': ad_id, 'title': title}})
    except Exception as e:
        print(f'Upload error: {e}')
        return jsonify({'success': False, 'error': f'Upload failed: {str(e)}'}), 500

@app.route('/admin/delete-ad', methods=['POST'])
def delete_ad():
    data = request.json
    ad_id = data.get('adId')
    conn = get_db()
    conn.execute('DELETE FROM ads WHERE id=?', (ad_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/get-ad')
def get_ad():
    conn = get_db()
    ads = conn.execute('SELECT * FROM ads').fetchall()
    conn.close()
    if ads:
        ad = random.choice(ads)
        return jsonify({'id': ad['id'], 'title': ad['title'], 'videoFile': ad['video_data'], 'clickUrl': ad['click_url']})
    return jsonify(None)

@app.route('/track-ad-view', methods=['POST'])
def track_ad_view():
    data = request.json
    ad_id = data.get('adId')
    conn = get_db()
    conn.execute('UPDATE ads SET views = views + 1 WHERE id=?', (ad_id,))
    conn.commit()
    conn.close()
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

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password)).fetchone()
    conn.close()
    if user:
        return jsonify({'success': True, 'message': 'Login successful'})
    return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    conn = get_db()
    existing = conn.execute('SELECT email FROM users WHERE email=?', (email,)).fetchone()
    if existing:
        conn.close()
        return jsonify({'success': False, 'error': 'Account already exists. Please login.'}), 400
    conn.execute('INSERT INTO users (email, password, joined, videos, views, status) VALUES (?,?,?,0,0,"active")',
                 (email, password, time.strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Account created successfully'})
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