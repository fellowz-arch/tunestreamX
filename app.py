from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import time
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def fetch_videos(term, max_results=80):
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True, 'socket_timeout': 1}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f'ytsearch{max_results}:{term}', download=False)
            videos = []
            for v in result['entries'][:max_results]:
                if v.get('duration', 0) > 60:
                    videos.append({
                        'id': v['id'],
                        'title': v['title'],
                        'duration': v.get('duration', 0),
                        'thumbnail': f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg",
                        'channel': v.get('channel', 'Unknown'),
                        'views': random.randint(100000, 50000000),
                        'likes': random.randint(1000, 500000)
                    })
                    if len(videos) >= 70:
                        break
            return videos
    except:
        return []

@app.route('/trending')
def trending():
    import random
    trending_terms = ['trending music 2024', 'viral songs 2024', 'top hits 2024', 'popular music', 'chart toppers', 'new music 2024', 'hot songs', 'music hits', 'viral hits', 'trending now']
    all_videos = []
    seen = set()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_videos, term, 80) for term in trending_terms]
        for future in as_completed(futures, timeout=8):
            try:
                videos = future.result()
                for v in videos:
                    if v['id'] not in seen and len(all_videos) < 600:
                        all_videos.append(v)
                        seen.add(v['id'])
            except:
                continue
    
    random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/top')
def top():
    import random
    top_terms = ['top songs 2024', 'best music 2024', 'billboard hot 100', 'spotify top 50', 'apple music charts', 'youtube music trending', 'global hits', 'radio hits', 'chart music', 'hit songs']
    all_videos = []
    seen = set()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_videos, term, 80) for term in top_terms]
        for future in as_completed(futures, timeout=8):
            try:
                videos = future.result()
                for v in videos:
                    if v['id'] not in seen and len(all_videos) < 600:
                        all_videos.append(v)
                        seen.add(v['id'])
            except:
                continue
    
    random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/foryou')
def foryou():
    import random
    genres = ['pop music', 'hip hop hits', 'rock classics', 'electronic dance', 'r&b soul', 'country music', 'indie music', 'latin hits', 'jazz music', 'reggae hits', 'folk music', 'blues music']
    all_videos = []
    seen = set()
    
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(fetch_videos, genre, 80) for genre in genres]
        for future in as_completed(futures, timeout=10):
            try:
                videos = future.result()
                for v in videos:
                    if v['id'] not in seen and len(all_videos) < 600:
                        all_videos.append(v)
                        seen.add(v['id'])
            except:
                continue
    
    random.shuffle(all_videos)
    return jsonify(all_videos)

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True, 'socket_timeout': 2}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(f"ytsearch100:{query}", download=False)
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
                            'channel': v.get('channel', 'Unknown'),
                            'views': random.randint(100000, 50000000),
                            'likes': random.randint(1000, 500000)
                        })
            
            return jsonify(videos)
        except:
            return jsonify([])

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)