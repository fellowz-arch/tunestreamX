from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__, template_folder='../templates', static_folder='../static')
DOWNLOAD_FOLDER = Path('downloads')
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

def fetch_videos(term, max_results=50):
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True, 'socket_timeout': 5}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f'ytsearch{max_results}:{term}', download=False)
            return [{
                'id': v['id'],
                'title': v['title'],
                'duration': v.get('duration', 0),
                'thumbnail': f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg",
                'channel': v.get('channel', 'Unknown')
            } for v in result['entries'] if v.get('duration', 0) > 60]
    except:
        return []

@app.route('/trending')
def trending():
    import random
    trending_terms = ['trending music 2024', 'viral songs 2024']
    all_videos = []
    seen = set()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(fetch_videos, term, 50) for term in trending_terms]
        for future in as_completed(futures):
            videos = future.result()
            for v in videos:
                if v['id'] not in seen and len(all_videos) < 100:
                    all_videos.append(v)
                    seen.add(v['id'])
    
    random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/top')
def top():
    import random
    top_terms = ['top songs 2024', 'best music 2024']
    all_videos = []
    seen = set()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(fetch_videos, term, 50) for term in top_terms]
        for future in as_completed(futures):
            videos = future.result()
            for v in videos:
                if v['id'] not in seen and len(all_videos) < 100:
                    all_videos.append(v)
                    seen.add(v['id'])
    
    random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/foryou')
def foryou():
    import random
    genres = ['pop music', 'hip hop hits']
    all_videos = []
    seen = set()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(fetch_videos, genre, 50) for genre in genres]
        for future in as_completed(futures):
            videos = future.result()
            for v in videos:
                if v['id'] not in seen and len(all_videos) < 100:
                    all_videos.append(v)
                    seen.add(v['id'])
    
    random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/football')
def football():
    import random
    football_terms = ['live football match today', 'football live stream', 'premier league live', 'champions league live', 'football highlights', 'live soccer match']
    all_videos = []
    seen = set()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch_videos, term, 30) for term in football_terms]
        for future in as_completed(futures):
            videos = future.result()
            for v in videos:
                if v['id'] not in seen and len(all_videos) < 100:
                    all_videos.append(v)
                    seen.add(v['id'])
    
    random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/wrestling')
def wrestling():
    import random
    wrestling_terms = ['wwe highlights', 'wrestling matches', 'aew wrestling', 'wrestling news']
    all_videos = []
    seen = set()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(fetch_videos, term, 25) for term in wrestling_terms]
        for future in as_completed(futures):
            videos = future.result()
            for v in videos:
                if v['id'] not in seen and len(all_videos) < 100:
                    all_videos.append(v)
                    seen.add(v['id'])
    
    random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/movies')
def movies():
    import random
    movie_terms = ['latest movies', 'movie trailers', 'hollywood movies', 'action movies']
    all_videos = []
    seen = set()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(fetch_videos, term, 25) for term in movie_terms]
        for future in as_completed(futures):
            videos = future.result()
            for v in videos:
                if v['id'] not in seen and len(all_videos) < 100:
                    all_videos.append(v)
                    seen.add(v['id'])
    
    random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True, 'socket_timeout': 5}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(f"ytsearch50:{query}", download=False)
            videos = []
            
            for v in result['entries']:
                if v.get('duration', 0) > 60:
                    title_lower = v['title'].lower()
                    if ('mix' not in title_lower and 
                        'playlist' not in title_lower and 
                        'compilation' not in title_lower):
                        videos.append({
                            'id': v['id'],
                            'title': v['title'],
                            'duration': v.get('duration', 0),
                            'thumbnail': f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg",
                            'channel': v.get('channel', 'Unknown')
                        })
            
            return jsonify(videos)
        except:
            return jsonify([])

@app.route('/download', methods=['POST'])
def download():
    video_id = request.json.get('video_id')
    format_type = request.json.get('format', 'mp3')
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    if format_type == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 10,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }
    else:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 10,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == 'mp3':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
        
        time.sleep(1)
        
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        else:
            return jsonify({'error': 'Download completed but file not found'}), 500
            
    except Exception as e:
        error_msg = str(e).lower()
        if 'ssl' in error_msg or 'timeout' in error_msg or 'connection' in error_msg:
            return jsonify({'error': 'Download temporarily unavailable due to network restrictions. Please try again later.'}), 503
        elif 'unavailable' in error_msg or 'private' in error_msg:
            return jsonify({'error': 'Video is unavailable or private'}), 404
        else:
            return jsonify({'error': 'Download failed. Please try again.'}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)