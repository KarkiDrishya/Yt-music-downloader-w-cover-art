import os
import re
import subprocess
from urllib.parse import quote_plus

# ---------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------
SOURCE_BASE_DIR = r"C:\Users\USER\Documents\College\Projects\Music_downloader"
OUTPUT_BASE_DIR = r"C:\Users\USER\Documents\College\Projects\Music_downloader\processed_music"
LOG_DIR = "logs"

# YouTube Music search filter token for "Songs" only.
# This returns the audio-only uploads with square album art, not music videos.
YTM_SONGS_FILTER = "Eg-KAQwIARAAGAAgACgAMABqChAEEAMQCRAFEAo%3D"

SKIP_FOLDERS = {"processed_music", "logs", ".git"}

os.makedirs(LOG_DIR, exist_ok=True)
error_log_path = os.path.join(LOG_DIR, "failed_downloads.txt")


def clean_song_name(filename):
    name, _ = os.path.splitext(filename)

    # 1. Remove website prefixes
    name = re.sub(r'^(yt1s\.com\s*-\s*|y2mate\.com\s*-\s*)', '', name, flags=re.IGNORECASE)

    # 2. Remove clutter words inside parentheses or brackets
    noise_patterns = [
        r'\(official music video\)',
        r'\(official video\)',
        r'\(official audio\)',
        r'\(lyrics\)',
        r'\(audio\)',
        r'\(visualizer\)',
        r'\[official music video\]',
        r'\[official video\]',
        r'\[official audio\]',
        r'\[lyrics\]',
        r'\[audio\]',
    ]
    for pattern in noise_patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)

    # 3. Clean up extra hyphens and spaces
    name = re.sub(r'\s*-\s*$', '', name)
    name = re.sub(r'\s+', ' ', name)

    return name.strip()


def build_ytm_search_url(song):
    """Build a YouTube Music 'Songs only' search URL from plain text."""
    return f"https://music.youtube.com/search?q={quote_plus(song)}&sp={YTM_SONGS_FILTER}"


def count_files(folder):
    return len(os.listdir(folder))


def download_song(song, output_folder):
    """Download the top YT Music 'Songs' result. Returns True on success."""
    search_url = build_ytm_search_url(song)

    command = [
        "yt-dlp",
        "--playlist-items", "1",            # only the top result
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0",             # best quality
        "--embed-thumbnail",
        "--add-metadata",
        "--no-overwrites",
        "-o", os.path.join(output_folder, "%(artist,uploader)s - %(track,title)s.%(ext)s"),
        "--ppa", "ThumbnailsConvertor+ffmpeg_o:-c:v mjpeg -vf crop=ih:ih",
        search_url,
    ]

    before = count_files(output_folder)
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        return False

    # yt-dlp can exit 0 even if the search returned nothing,
    # so confirm a new file really appeared.
    return count_files(output_folder) > before


def process_folders():
    if not os.path.exists(SOURCE_BASE_DIR):
        print(f"Error: Source base directory not found: {SOURCE_BASE_DIR}")
        print("Please copy your phone's music folders here and update 'SOURCE_BASE_DIR'.")
        return

    for folder_name in os.listdir(SOURCE_BASE_DIR):
        source_folder = os.path.join(SOURCE_BASE_DIR, folder_name)

        # Skip files and system/output directories to avoid recursive loops
        if not os.path.isdir(source_folder) or folder_name in SKIP_FOLDERS:
            continue

        print("\n==============================")
        print(f"Processing folder: {folder_name}")
        print("==============================")

        output_folder = os.path.join(OUTPUT_BASE_DIR, folder_name)
        os.makedirs(output_folder, exist_ok=True)

        # Build the song list from the local mp3 filenames (no URLs needed)
        songs = []
        for file in os.listdir(source_folder):
            if file.lower().endswith(".mp3"):
                cleaned = clean_song_name(file)
                if cleaned:
                    songs.append(cleaned)

        if not songs:
            print(f"No MP3 files found in {folder_name}.")
            continue

        print(f"Found {len(songs)} songs to download for '{folder_name}'.")
        failed_songs = []

        for i, song in enumerate(songs, 1):
            print(f"\n[{i}/{len(songs)}] Searching YT Music: {song}")

            if download_song(song, output_folder):
                print(f"Successfully downloaded: {song}")
            else:
                print(f"FAILED: {song}")
                failed_songs.append(f"{folder_name} -> {song}")

        if failed_songs:
            with open(error_log_path, "a", encoding="utf-8") as log_f:
                for fail in failed_songs:
                    log_f.write(fail + "\n")

    print("\nAll folders processed! Check 'processed_music' folder for results.")


if __name__ == "__main__":
    process_folders()