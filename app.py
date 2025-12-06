import os
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC

app = Flask(__name__)
MUSIC_DIR = os.path.expanduser("~/Music")
DB_PATH = "music.db"

def init_db():
    """Initialize the database schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            artist TEXT,
            album TEXT,
            filepath TEXT UNIQUE,
            filename TEXT,
            duration INTEGER,
            directory TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS listening_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration_played INTEGER,
            song_duration INTEGER,
            percentage_played REAL,
            completed BOOLEAN,
            FOREIGN KEY (song_id) REFERENCES songs(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_metadata(filepath):
    """Extract metadata from audio file."""
    try:
        audio = MutagenFile(filepath, easy=True)
        if audio is None:
            return None

        title = audio.get('title', [os.path.splitext(os.path.basename(filepath))[0]])[0]
        artist = audio.get('artist', ['Unknown Artist'])[0]
        album = audio.get('album', ['Unknown Album'])[0]

        # Get duration
        duration = 0
        if hasattr(audio.info, 'length'):
            duration = int(audio.info.length)

        return {
            'title': title,
            'artist': artist,
            'album': album,
            'duration': duration
        }
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def scan_music():
    """Scan music directory and populate database."""
    print(f"Scanning {MUSIC_DIR} for music files...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    count = 0
    extensions = {'.mp3', '.m4a', '.flac', '.wav', '.ogg'}

    for root, dirs, files in os.walk(MUSIC_DIR):
        for file in files:
            if Path(file).suffix.lower() in extensions:
                filepath = os.path.join(root, file)

                # Extract directory name (immediate parent folder)
                directory = os.path.basename(os.path.dirname(filepath))
                # If it's directly in Music folder, use the file's parent dir
                rel_path = os.path.relpath(os.path.dirname(filepath), MUSIC_DIR)
                # Get the top-level directory name
                top_dir = rel_path.split(os.sep)[0] if rel_path != '.' else 'Music'

                # Check if already in database
                c.execute('SELECT id FROM songs WHERE filepath = ?', (filepath,))
                if c.fetchone():
                    continue

                metadata = get_metadata(filepath)
                if metadata:
                    c.execute('''
                        INSERT INTO songs (title, artist, album, filepath, filename, duration, directory)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        metadata['title'],
                        metadata['artist'],
                        metadata['album'],
                        filepath,
                        file,
                        metadata['duration'],
                        top_dir
                    ))
                    count += 1
                    if count % 100 == 0:
                        print(f"Indexed {count} songs...")

    conn.commit()
    conn.close()
    print(f"Scan complete! Indexed {count} new songs.")

@app.route('/')
def index():
    """Main page with browse and search."""
    return render_template('index.html')

@app.route('/api/artists')
def get_artists():
    """Get list of all artists."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT DISTINCT artist FROM songs ORDER BY artist')
    artists = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(artists)

@app.route('/api/albums')
def get_albums():
    """Get albums for a specific artist."""
    artist = request.args.get('artist')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if artist:
        c.execute('SELECT DISTINCT album FROM songs WHERE artist = ? ORDER BY album', (artist,))
    else:
        c.execute('SELECT DISTINCT artist, album FROM songs ORDER BY artist, album')

    if artist:
        albums = [row[0] for row in c.fetchall()]
    else:
        albums = [{'artist': row[0], 'album': row[1]} for row in c.fetchall()]

    conn.close()
    return jsonify(albums)

@app.route('/api/directories')
def get_directories():
    """Get list of all directories."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT DISTINCT directory FROM songs WHERE directory IS NOT NULL ORDER BY directory')
    directories = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(directories)

@app.route('/api/songs')
def get_songs():
    """Get songs with optional filters."""
    artist = request.args.get('artist')
    album = request.args.get('album')
    directory = request.args.get('directory')
    search = request.args.get('search')
    limit = request.args.get('limit', 'true').lower() == 'true'  # Default to limiting

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if search:
        query = '''
            SELECT id, title, artist, album, filepath, duration
            FROM songs
            WHERE title LIKE ? OR artist LIKE ? OR album LIKE ?
            ORDER BY artist, album, title
        '''
        search_term = f'%{search}%'
        c.execute(query, (search_term, search_term, search_term))
    elif directory:
        c.execute('''
            SELECT id, title, artist, album, filepath, duration
            FROM songs
            WHERE directory = ?
            ORDER BY artist, album, title
        ''', (directory,))
    elif artist and album:
        c.execute('''
            SELECT id, title, artist, album, filepath, duration
            FROM songs
            WHERE artist = ? AND album = ?
            ORDER BY title
        ''', (artist, album))
    elif artist:
        c.execute('''
            SELECT id, title, artist, album, filepath, duration
            FROM songs
            WHERE artist = ?
            ORDER BY album, title
        ''', (artist,))
    else:
        query = '''
            SELECT id, title, artist, album, filepath, duration
            FROM songs
            ORDER BY artist, album, title
        '''
        if limit:
            query += ' LIMIT 100'
        c.execute(query)

    songs = []
    for row in c.fetchall():
        songs.append({
            'id': row[0],
            'title': row[1],
            'artist': row[2],
            'album': row[3],
            'filepath': row[4],
            'duration': row[5]
        })

    conn.close()
    return jsonify(songs)

@app.route('/api/stream/<int:song_id>')
def stream_song(song_id):
    """Stream a song file."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT filepath FROM songs WHERE id = ?', (song_id,))
    result = c.fetchone()
    conn.close()

    if result:
        return send_file(result[0])
    return "File not found", 404

@app.route('/api/track-play', methods=['POST'])
def track_play():
    """Track a song play with listening stats."""
    data = request.get_json()
    song_id = data.get('song_id')
    duration_played = data.get('duration_played', 0)
    song_duration = data.get('song_duration', 0)

    if not song_id:
        return jsonify({'error': 'song_id required'}), 400

    # Calculate percentage and completion
    percentage_played = (duration_played / song_duration * 100) if song_duration > 0 else 0
    completed = percentage_played >= 90  # Consider 90%+ as completed

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO listening_history
        (song_id, duration_played, song_duration, percentage_played, completed)
        VALUES (?, ?, ?, ?, ?)
    ''', (song_id, duration_played, song_duration, percentage_played, completed))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})

@app.route('/api/stats')
def get_stats():
    """Get listening statistics."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Top songs by play count
    c.execute('''
        SELECT
            s.id,
            s.title,
            s.artist,
            s.album,
            COUNT(h.id) as play_count,
            SUM(CASE WHEN h.completed = 1 THEN 1 ELSE 0 END) as completed_count,
            SUM(CASE WHEN h.completed = 0 THEN 1 ELSE 0 END) as skipped_count,
            AVG(h.percentage_played) as avg_percentage
        FROM songs s
        JOIN listening_history h ON s.id = h.song_id
        GROUP BY s.id
        ORDER BY play_count DESC
        LIMIT 50
    ''')
    top_songs = [dict(row) for row in c.fetchall()]

    # Overall stats
    c.execute('''
        SELECT
            COUNT(*) as total_plays,
            SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as total_completed,
            SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END) as total_skipped,
            AVG(percentage_played) as avg_percentage
        FROM listening_history
    ''')
    overall = dict(c.fetchone())

    # Top artists
    c.execute('''
        SELECT
            s.artist,
            COUNT(h.id) as play_count,
            SUM(CASE WHEN h.completed = 1 THEN 1 ELSE 0 END) as completed_count
        FROM songs s
        JOIN listening_history h ON s.id = h.song_id
        GROUP BY s.artist
        ORDER BY play_count DESC
        LIMIT 20
    ''')
    top_artists = [dict(row) for row in c.fetchall()]

    conn.close()

    return jsonify({
        'top_songs': top_songs,
        'overall': overall,
        'top_artists': top_artists
    })

@app.route('/api/rescan')
def rescan():
    """Rescan music directory."""
    scan_music()
    return jsonify({'status': 'complete'})

if __name__ == '__main__':
    init_db()

    # Check if database is empty and scan if needed
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM songs')
    count = c.fetchone()[0]
    conn.close()

    if count == 0:
        print("Database is empty. Scanning music directory...")
        scan_music()
    else:
        print(f"Found {count} songs in database.")

    print("\nStarting music player on http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
