# Music Player Web App - Project Context

## Overview
This is a Flask-based web application for browsing and playing local music files from ~/Music directory. The app provides a modern web interface with search, filtering, and playback controls.

## Project Architecture

### Backend (app.py)
- **Framework**: Flask 3.0.0
- **Database**: SQLite (music.db)
- **Metadata Extraction**: mutagen library
- **Music Directory**: ~/Music (configurable via MUSIC_DIR variable)
- **Port**: 5001 (changed from 5000 due to macOS AirPlay conflict)

### Frontend (templates/index.html)
- Single-page application with vanilla JavaScript
- Modern CSS with gradient styling
- HTML5 audio player for streaming

### Database Schema
```sql
CREATE TABLE songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    artist TEXT,
    album TEXT,
    filepath TEXT UNIQUE,
    filename TEXT,
    duration INTEGER,
    directory TEXT  -- Top-level directory name from ~/Music
)
```

## Key Features Implemented

1. **Directory Filtering** (added per user request)
   - Extracts top-level directory name from file path
   - Allows browsing by folder (e.g., "Club Music", artist folders)
   - Mutually exclusive with artist/album filters

2. **Shuffle Mode** (added per user request)
   - Toggle button in UI (green=OFF, red=ON)
   - Allows repeats when enabled
   - Works with filtered playlists

3. **Previous/Next Navigation** (added per user request)
   - Circular playback (wraps around at ends)
   - Respects shuffle mode
   - Round buttons below audio player

## Important Implementation Details

### Music Scanning
- Runs automatically on first launch (when database is empty)
- Supports: MP3, M4A, FLAC, WAV, OGG
- Extracts metadata using mutagen
- Some files may fail to read (corrupted metadata) - errors are logged but don't stop the scan
- Scans ~3,650 songs in a few minutes

### API Endpoints
- `/api/directories` - Returns list of unique top-level directories
- `/api/songs?directory=X&artist=Y&album=Z&search=Q` - Flexible filtering
- `/api/stream/<song_id>` - Streams audio file with partial content support (HTTP 206)

### Frontend State Management
- `allSongs[]` - Current filtered song list
- `currentSongId` - Currently playing song
- `shuffleMode` - Boolean for shuffle state
- `currentDirectory`, `currentArtist`, `currentAlbum` - Active filters

### Filter Behavior
- Selecting directory clears artist/album filters
- Selecting artist clears directory filter
- Search operates independently
- "Clear" button resets all filters

## Known Issues & Limitations

1. **Corrupted Files**: Some FLAC and MP3 files have metadata errors and are skipped during scanning
2. **Port Conflict**: Default port 5000 conflicts with macOS AirPlay Receiver, changed to 5001
3. **Large Libraries**: Initial scan can take time; progress logged every 100 songs
4. **No Authentication**: App is accessible to anyone on the local network

## File Structure
```
/Users/nathanspeidel/git-repos/music/
├── app.py                    # Flask backend
├── templates/
│   └── index.html           # Frontend SPA
├── requirements.txt         # Flask==3.0.0, mutagen==1.47.0
├── music.db                 # SQLite database (auto-generated)
├── README.md                # User documentation
└── PROJECT_CONTEXT.md       # This file (for AI agents)
```

## Development Notes

### Running the App
```bash
python3 app.py
```
- Debug mode is enabled
- Auto-reloads on template changes
- Accessible at http://localhost:5001

### Rescanning Music
- Visit http://localhost:5001/api/rescan
- Or delete music.db and restart

### Adding New Features
- Backend routes go in app.py
- Frontend logic in templates/index.html <script> section
- Database migrations: Delete music.db to recreate with new schema

## User Preferences Observed
- Prefers random playback WITH repeats (not typical shuffle behavior)
- Wanted directory-based browsing (not just artist/album)
- Likes simple, functional UI without over-engineering

## Testing
- User has ~3,650 songs indexed
- Successfully tested with Club Music directory
- Multiple concurrent song streams working correctly

## For Future AI Agents

When working on this project:
1. The user's music is in ~/Music with various subdirectories
2. Port 5001 is intentional - don't change it back to 5000
3. Shuffle mode allows repeats by design (user preference)
4. Directory filter shows top-level folders only
5. The app is meant to be simple - avoid adding complexity unless requested
6. Database is auto-generated - delete music.db to force rescan
7. Some metadata extraction errors are normal for corrupted files
