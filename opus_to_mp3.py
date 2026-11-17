import os
import subprocess

SOURCE_DIR = r"C:\Users\USER\Documents\College\Projects\Music_downloader\processed_music\Audio"

def convert_all_opus():
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Directory not found: {SOURCE_DIR}")
        return

    print(f"Scanning folder: {SOURCE_DIR}")
    opus_files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".opus")]

    if not opus_files:
        print("No .opus files found in the directory.")
        return

    print(f"Found {len(opus_files)} .opus files to convert.")

    for i, file in enumerate(opus_files, 1):
        input_path = os.path.join(SOURCE_DIR, file)
        base, _ = os.path.splitext(file)
        output_path = os.path.join(SOURCE_DIR, base + ".mp3")

        if os.path.exists(output_path):
            print(f"[{i}/{len(opus_files)}] Skipping (MP3 already exists): {file}")
            continue

        print(f"\n[{i}/{len(opus_files)}] Converting: {file}")

        # FFmpeg command to convert audio to MP3 and map embedded cover art
        command = [
            "ffmpeg",
            "-i", input_path,
            "-map", "0",
            "-c:a", "libmp3lame",
            "-q:a", "0",
            "-id3v2_version", "3",
            output_path
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Successfully converted: {base}.mp3")
        except subprocess.CalledProcessError:
            print(f"Failed to convert: {file}")

    print("\nAll conversions complete!")

if __name__ == "__main__":
    convert_all_opus()
    
    
