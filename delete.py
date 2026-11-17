import os
import re

# CONFIGURATION
SOURCE_BASE_DIR = r"C:\Users\USER\Documents\College\Projects\Music_downloader"
LOG_DIR = "logs"
error_log_path = os.path.join(LOG_DIR, "failed_downloads.txt")

SKIP_FOLDERS = {"processed_music", "logs", ".git"}

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

def load_failed_songs():
    failed_set = set()
    if not os.path.exists(error_log_path):
        print("No error log found. Assuming no failed downloads exist.")
        return failed_set
    
    with open(error_log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "->" in line:
                folder, song = line.split("->", 1)
                failed_set.add((folder.strip(), song.strip()))
    return failed_set

def cleanup_original_music():
    if not os.path.exists(SOURCE_BASE_DIR):
        print(f"Error: Source base directory not found: {SOURCE_BASE_DIR}")
        return

    failed_songs = load_failed_songs()
    print(f"Loaded {len(failed_songs)} failed song entries from logs.")

    deleted_count = 0
    kept_count = 0

    for folder_name in os.listdir(SOURCE_BASE_DIR):
        source_folder = os.path.join(SOURCE_BASE_DIR, folder_name)

        if not os.path.isdir(source_folder) or folder_name in SKIP_FOLDERS:
            continue

        print(f"\nChecking folder: {folder_name}")
        for file in os.listdir(source_folder):
            if file.lower().endswith(".mp3"):
                file_path = os.path.join(source_folder, file)
                cleaned = clean_song_name(file)
                
                # Check if this song is in the failed log
                if (folder_name, cleaned) in failed_songs:
                    print(f"  [KEPT (Failed previously)]: {file}")
                    kept_count += 1
                else:
                    try:
                        os.remove(file_path)
                        print(f"  [DELETED]: {file}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"  [ERROR deleting {file}]: {e}")

    print(f"\n==============================")
    print(f"CLEANUP COMPLETE")
    print(f"==============================")
    print(f"Successfully deleted: {deleted_count} files")
    print(f"Kept (failed downloads): {kept_count} files")

if __name__ == "__main__":
    cleanup_original_music()