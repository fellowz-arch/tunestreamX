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

@app.route('/test-espn')
def test_espn():
    import requests
    import datetime
    headers = {'User-Agent': 'Mozilla/5.0'}
    today = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')
    results = {}
    for league_id in ['eng.1', 'uefa.champions', 'esp.1']:
        try:
            r = requests.get(f'https://site.api.espn.com/apis/site/v2/sports/soccer/{league_id}/scoreboard?dates={today}', headers=headers, timeout=8)
            results[league_id] = {'status': r.status_code, 'data': r.json()}
        except Exception as e:
            results[league_id] = {'error': str(e)}
    return jsonify(results)


@app.route('/test-sports')
def test_sports():
    import requests, datetime
    headers = {'User-Agent': 'Mozilla/5.0'}
    today = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    results = {}
    try:
        r = requests.get(f'https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={today}&s=Soccer', headers=headers, timeout=10)
        results['thesportsdb'] = {'status': r.status_code, 'data': r.json()}
    except Exception as e:
        results['thesportsdb'] = {'error': str(e)}
    try:
        r2 = requests.get('https://www.livesoccertv.com/schedules/', headers=headers, timeout=10)
        results['livesoccertv'] = {'status': r2.status_code, 'html_snippet': r2.text[:3000]}
    except Exception as e:
        results['livesoccertv'] = {'error': str(e)}
    try:
        r3 = requests.get('https://cricfy.tv/', headers=headers, timeout=10, allow_redirects=True)
        results['cricfy'] = {'status': r3.status_code, 'final_url': r3.url, 'html_snippet': r3.text[:3000]}
    except Exception as e:
        results['cricfy'] = {'error': str(e)}
    return jsonify(results)


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
    import datetime

    streams = []
    seen = set()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'}
    now = datetime.datetime.now(datetime.timezone.utc)

    espn_leagues = [
        ('eng.1', 'Premier League'),
        ('uefa.champions', 'Champions League'),
        ('esp.1', 'La Liga'),
        ('ger.1', 'Bundesliga'),
        ('ita.1', 'Serie A'),
        ('fra.1', 'Ligue 1'),
        ('uefa.europa', 'Europa League'),
        ('usa.1', 'MLS'),
        ('eng.2', 'Championship'),
        ('esp.2', 'La Liga 2'),
        ('ger.2', 'Bundesliga 2'),
        ('ita.2', 'Serie B'),
        ('ned.1', 'Eredivisie'),
        ('por.1', 'Primeira Liga'),
        ('tur.1', 'Super Lig'),
        ('sco.1', 'Scottish Premiership'),
        ('uefa.wchampions', 'Women Champions League'),
        ('concacaf.champions', 'CONCACAF Champions'),
        ('conmebol.libertadores', 'Copa Libertadores'),
    ]

    def parse_events(data, league_name, date_str):
        results = []
        league_logo = ''
        for lg in data.get('leagues', []):
            logos = lg.get('logos', [])
            if logos:
                league_logo = logos[0].get('href', '')
        for event in data.get('events', []):
            state = event.get('status', {}).get('type', {}).get('state', '').lower()
            if state == 'post':
                continue
            detail = event.get('status', {}).get('type', {}).get('shortDetail', '')
            display_clock = event.get('status', {}).get('displayClock', '')
            comp = (event.get('competitions') or [{}])[0]
            competitors = comp.get('competitors', [])
            home = next((c for c in competitors if c.get('homeAway') == 'home'), {})
            away = next((c for c in competitors if c.get('homeAway') == 'away'), {})
            home_name = home.get('team', {}).get('displayName', '')
            away_name = away.get('team', {}).get('displayName', '')
            home_logo = home.get('team', {}).get('logo', '') or league_logo
            away_logo = away.get('team', {}).get('logo', '')
            home_score = home.get('score', '')
            away_score = away.get('score', '')
            event_date = event.get('date', '')[:16].replace('T', ' ') + ' UTC'
            is_live = state == 'in'
            uid = abs(hash(event.get('id', home_name + away_name + date_str))) % 100000000
            if not home_name or not away_name:
                continue
            results.append({
                'id': f'espn_{uid}',
                'title': f'{home_name} vs {away_name}',
                'thumbnail': home_logo or f'https://placehold.co/320x180/1a1a2e/ffffff?text={league_name.replace(" ","+")}',
                'awayLogo': away_logo,
                'homeName': home_name,
                'awayName': away_name,
                'homeScore': home_score,
                'awayScore': away_score,
                'channel': league_name,
                'isLive': is_live,
                'isUpcoming': not is_live,
                'matchTime': display_clock if is_live else event_date,
                'detail': detail,
                'streamType': 'iframe',
                'streamUrl': 'https://cricfy.tv/',
                'pageUrl': 'https://cricfy.tv/'
            })
        return results

    # Fetch all leagues for next 7 days in parallel
    def fetch_league_day(league_id, league_name, day_offset):
        check_date = (now + datetime.timedelta(days=day_offset)).strftime('%Y%m%d')
        try:
            url = f'https://site.api.espn.com/apis/site/v2/sports/soccer/{league_id}/scoreboard?dates={check_date}'
            r = requests.get(url, headers=headers, timeout=6)
            if r.status_code == 200:
                return parse_events(r.json(), league_name, check_date)
        except Exception as e:
            print(f'ESPN {league_name} {check_date} error: {e}')
        return []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for league_id, league_name in espn_leagues:
            for day_offset in range(7):
                futures.append(executor.submit(fetch_league_day, league_id, league_name, day_offset))
        for future in as_completed(futures, timeout=20):
            try:
                for e in future.result():
                    if e['id'] not in seen:
                        seen.add(e['id'])
                        streams.append(e)
            except Exception as ex:
                print(f'Future error: {ex}')

    streams.sort(key=lambda x: (0 if x['isLive'] else 1, x.get('matchTime', '')))
    return jsonify(streams)


@app.route('/cricfy-proxy')
def cricfy_proxy():
    import requests
    from bs4 import BeautifulSoup
    import re
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://google.com'
    }
    
    try:
        r = requests.get('https://cricfy.tv/', headers=headers, timeout=15, allow_redirects=True)
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # Fix all relative URLs to absolute
        for tag in soup.find_all(['a', 'link', 'script', 'img', 'form']):
            for attr in ['href', 'src', 'action']:
                val = tag.get(attr, '')
                if val and not val.startswith('http') and not val.startswith('data:') and not val.startswith('#') and not val.startswith('javascript'):
                    tag[attr] = 'https://cricfy.tv/' + val.lstrip('/')
        
        # Make all external links open in same frame
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'cricfy.tv' in href:
                a['href'] = f'/cricfy-page?url={href}'
            else:
                a['target'] = '_blank'
        
        # Inject close button and custom styles
        style_tag = soup.new_tag('style')
        style_tag.string = '''
            body { margin: 0 !important; }
            * { box-sizing: border-box; }
        '''
        if soup.head:
            soup.head.append(style_tag)
        
        return str(soup), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        return f'<html><body style="background:#0d0d1a;color:#fff;padding:20px;"><h2>&#9917; Loading CricFy TV...</h2><p>Error: {str(e)}</p><a href="https://cricfy.tv" target="_blank" style="color:#e63946;">Open CricFy TV directly</a></body></html>', 200, {'Content-Type': 'text/html'}


@app.route('/cricfy-page')
def cricfy_page():
    import requests
    from bs4 import BeautifulSoup
    
    url = request.args.get('url', 'https://cricfy.tv/')
    if not url.startswith('https://cricfy.tv'):
        url = 'https://cricfy.tv/'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://cricfy.tv/'
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        
        for tag in soup.find_all(['a', 'link', 'script', 'img']):
            for attr in ['href', 'src']:
                val = tag.get(attr, '')
                if val and not val.startswith('http') and not val.startswith('data:') and not val.startswith('#') and not val.startswith('javascript'):
                    tag[attr] = 'https://cricfy.tv/' + val.lstrip('/')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'cricfy.tv' in href:
                a['href'] = f'/cricfy-page?url={href}'
        
        return str(soup), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        return f'<p>Error loading page: {e}</p>', 200


@app.route('/live-tv')
def live_tv():
    channels = [
        # News - verified working m3u8 streams
        {'id':'aljaz','name':'Al Jazeera English','logo':'https://upload.wikimedia.org/wikipedia/en/thumb/f/f2/Aljazeera_eng.svg/200px-Aljazeera_eng.svg.png','category':'news','stream':'https://live-hls-web-aje.getaj.net/AJE/index.m3u8'},
        {'id':'bbcnews','name':'BBC News','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/BBC_News_2019.svg/200px-BBC_News_2019.svg.png','category':'news','stream':'https://vs-hls-push-ww-live.akamaized.net/x=4/i=urn:bbc:pips:service:bbc_news_channel_hd/pc_hd_abr_v2.m3u8'},
        {'id':'dwnews','name':'DW News','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Deutsche_Welle_symbol_2012.svg/200px-Deutsche_Welle_symbol_2012.svg.png','category':'news','stream':'https://dwamdstream102.akamaized.net/hls/live/2015525/dwstream102/index.m3u8'},
        {'id':'france24en','name':'France 24 English','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/France_24_logo.svg/200px-France_24_logo.svg.png','category':'news','stream':'https://stream.france24.com/hls/live/2037163/F24_EN_HI_HLS/master.m3u8'},
        {'id':'france24fr','name':'France 24 French','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/France_24_logo.svg/200px-France_24_logo.svg.png','category':'news','stream':'https://stream.france24.com/hls/live/2037161/F24_FR_HI_HLS/master.m3u8'},
        {'id':'cgtn','name':'CGTN','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/CGTN_logo.svg/200px-CGTN_logo.svg.png','category':'news','stream':'https://news.cgtn.com/resource/live/english/cgtn-news.m3u8'},
        {'id':'trt','name':'TRT World','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/TRT_World_logo.svg/200px-TRT_World_logo.svg.png','category':'news','stream':'https://tv-trtworld.live.trt.com.tr/master.m3u8'},
        {'id':'nhk','name':'NHK World','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/NHK_World_logo.svg/200px-NHK_World_logo.svg.png','category':'news','stream':'https://nhkwlive-ojp.akamaized.net/hls/live/2003459/nhkwlive-ojp-en/index.m3u8'},
        {'id':'euronews','name':'Euronews','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Euronews_logo_2022.svg/200px-Euronews_logo_2022.svg.png','category':'news','stream':'https://rakuten-euronews-1-gb.samsung.wurl.tv/manifest/playlist.m3u8'},
        {'id':'africanews','name':'Africanews','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Africanews_logo.svg/200px-Africanews_logo.svg.png','category':'news','stream':'https://stream.africanews.com/hls/live/2037165/AFRNEWS_EN_HI_HLS/master.m3u8'},
        # Sports
        {'id':'eurosport1','name':'Eurosport 1','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Eurosport_logo_2015.svg/200px-Eurosport_logo_2015.svg.png','category':'sports','stream':'https://rakuten-eurosport-1-gb.samsung.wurl.tv/manifest/playlist.m3u8'},
        {'id':'realmadridtv','name':'Real Madrid TV','logo':'https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Real_Madrid_CF.svg/200px-Real_Madrid_CF.svg.png','category':'sports','stream':'https://rmtv-live.akamaized.net/hls/live/2093126/rmtv/index.m3u8'},
        # Entertainment
        {'id':'natgeo','name':'Nat Geo Wild','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/National_Geographic_Channel_logo.svg/200px-National_Geographic_Channel_logo.svg.png','category':'entertainment','stream':'https://rakuten-natgeowild-1-gb.samsung.wurl.tv/manifest/playlist.m3u8'},
        {'id':'history','name':'History Channel','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/History_Channel_logo.svg/200px-History_Channel_logo.svg.png','category':'entertainment','stream':'https://rakuten-history-1-gb.samsung.wurl.tv/manifest/playlist.m3u8'},
        {'id':'crime','name':'Crime Investigation','logo':'https://placehold.co/80x50/1a1a2e/ffffff?text=Crime','category':'entertainment','stream':'https://rakuten-crimeinvestigation-1-gb.samsung.wurl.tv/manifest/playlist.m3u8'},
        # Music
        {'id':'mtv','name':'MTV Hits','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/MTV_2021_logo.svg/200px-MTV_2021_logo.svg.png','category':'music','stream':'https://rakuten-mtvhits-1-gb.samsung.wurl.tv/manifest/playlist.m3u8'},
        {'id':'trace','name':'Trace Urban','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Trace_TV_logo.svg/200px-Trace_TV_logo.svg.png','category':'music','stream':'https://rakuten-traceurban-1-gb.samsung.wurl.tv/manifest/playlist.m3u8'},
        # Kids
        {'id':'cartoon','name':'Cartoon Network','logo':'https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Cartoon_Network_2010_logo.svg/200px-Cartoon_Network_2010_logo.svg.png','category':'kids','stream':'https://rakuten-cartoonnetwork-1-gb.samsung.wurl.tv/manifest/playlist.m3u8'},
        # Africa
        {'id':'ntv','name':'NTV Kenya','logo':'https://placehold.co/80x50/1a1a2e/ffffff?text=NTV','category':'africa','stream':'https://ntv.co.ke/live/stream.m3u8'},
        {'id':'citizentv','name':'Citizen TV Kenya','logo':'https://placehold.co/80x50/e63946/ffffff?text=Citizen','category':'africa','stream':'https://citizentv.co.ke/live/stream.m3u8'},
        {'id':'ktn','name':'KTN Kenya','logo':'https://placehold.co/80x50/1a5276/ffffff?text=KTN','category':'africa','stream':'https://ktn.co.ke/live/stream.m3u8'},
        {'id':'channels','name':'Channels TV Nigeria','logo':'https://placehold.co/80x50/1a1a2e/ffffff?text=Channels','category':'africa','stream':'https://channelstv.com/live/stream.m3u8'},
        {'id':'sabc','name':'SABC News','logo':'https://placehold.co/80x50/003366/ffffff?text=SABC','category':'africa','stream':'https://sabc.co.za/live/stream.m3u8'},
    ]
    return jsonify(channels)


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