from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import time
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

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
                    if v and v.get('duration', 0) > 60:
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
        videos = fetch_videos('music 2024', 100)
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
    top_terms = ['top songs 2024', 'best music']
    all_videos = []
    seen = set()
    
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(fetch_videos, term, 100) for term in top_terms]
            for future in as_completed(futures, timeout=25):
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
    genres = ['pop music', 'hip hop']
    all_videos = []
    seen = set()
    
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(fetch_videos, genre, 100) for genre in genres]
            for future in as_completed(futures, timeout=25):
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

# placeholder endpoints for desktop sidebar links that may not have real data yet
@app.route('/shorts')
def shorts():
    # shorts/short-form content not implemented
    return jsonify([])

@app.route('/library')
def library():
    # user library not implemented
    return jsonify([])

@app.route('/profile')
def profile():
    # profile information not implemented
    return jsonify([])

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)