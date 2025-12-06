# Music Player Web App

A Flask-based web application to browse, search, and play your local music collection with a modern, user-friendly interface.

## Features

### Browsing & Organization
- **Directory Filter**: Browse music by top-level folder (e.g., "Club Music", "Jazz", artist folders)
- **Artist Filter**: Filter songs by artist with dynamic album dropdown
- **Album Filter**: View songs from specific albums
- **Search**: Full-text search across song titles, artists, and albums

### Playback Controls
- **Web-based Player**: Play music directly in your browser using HTML5 audio
- **Next/Previous Buttons**: Navigate through your playlist with circular looping
- **Shuffle Mode**: Random playback with repeats (works with any filtered list)
- **Auto-play**: Automatically plays the next song when current finishes

### Technical Details
- Supports MP3, M4A, FLAC, WAV, and OGG formats
- Extracts metadata from audio files (title, artist, album, duration)
- SQLite database for fast searching and filtering
- Clean, gradient-styled UI with responsive design
- Network accessible - works on any device on your local network

## Installation

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python3 app.py
```

2. Open your browser to: **http://localhost:5001**

3. The app will automatically scan your `~/Music` directory on first run (this may take a few minutes depending on library size)

## How to Use

1. **Browse by Directory**: Use the first dropdown to select a top-level folder from your Music directory
2. **Browse by Artist/Album**: Use the artist and album dropdowns to filter your collection
3. **Search**: Type keywords to find songs, artists, or albums
4. **Shuffle**: Click the "Shuffle" button to enable random playback
5. **Navigate**: Use Previous (◄) and Next (►) buttons to skip through songs
6. **Play**: Click any song in the list to start playing

## How It Works

- The app scans `~/Music` directory and extracts metadata from audio files
- Metadata is stored in a SQLite database (`music.db`) for fast searching
- Songs are streamed directly from your file system
- No files are copied or modified
- Directory names are extracted from the top-level folders in ~/Music

## Rescanning Your Library

If you add new music, visit: **http://localhost:5001/api/rescan**

Or delete `music.db` and restart the app to perform a complete rescan.

## Project Structure

```
music/
├── app.py                 # Flask application and API routes
├── templates/
│   └── index.html        # Web interface with player controls
├── requirements.txt      # Python dependencies
├── music.db             # SQLite database (auto-generated)
└── README.md            # This file
```

## API Endpoints

- `GET /` - Main web interface
- `GET /api/artists` - List all artists
- `GET /api/albums?artist=<name>` - List albums for an artist
- `GET /api/directories` - List all top-level directories
- `GET /api/songs?directory=<name>&artist=<name>&album=<name>&search=<term>` - Get filtered songs
- `GET /api/stream/<song_id>` - Stream audio file
- `GET /api/rescan` - Rescan music directory

## Notes

- The app runs on `http://0.0.0.0:5001`, making it accessible from other devices on your network
- Your music files are never modified, only read
- The database file (`music.db`) will be created in the project directory
- Successfully tested with 3,650+ songs

## Features Summary

✅ Browse by directory, artist, or album
✅ Full-text search
✅ Shuffle mode with repeats
✅ Previous/Next navigation
✅ Auto-play next song
✅ Clean, modern UI
✅ Network accessible
✅ No music file modifications
